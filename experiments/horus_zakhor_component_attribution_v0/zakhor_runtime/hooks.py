"""Transformer forward hooks that apply living memory / switch quantization."""

from __future__ import annotations

from typing import List, Optional

import numpy as np
import torch

from .bfp import localmax_quantize
from .compose import compose_quantize_activations, compose_quantize_row_numpy
from .simulate import simulate_quantize_activations, simulate_quantize_row_numpy
from .config import MemoryConfig
from .layers import describe_layer_stack, get_attn_module, get_model_layers
from .switch import LayerThresholdBank, switch_quantize_row
from .torch_keeper import apply_keeper_activation
from .torch_fast import localmax_activations_torch, switch_activations_torch
from .tracker import LivingMemoryTracker


class LivingMemoryController:
    """Attach / detach per-layer attention-output hooks (architecture-agnostic).

    Supports GPT-2 (``transformer.h``), Llama/Qwen (``model.layers``), and
    NeoX/Pythia (``gpt_neox.layers``). Layer count and hidden size are taken
    from the live module stack — nothing is hardcoded to 12×768.

    Modes (compose / simulate are separate options; others unchanged):
      keeper | switch | localmax | none | compose | simulate
    """

    def __init__(
        self,
        model,
        mode: str = "keeper",
        cfg: Optional[MemoryConfig] = None,
        policy: str = "soft",
        threshold_bank: Optional[LayerThresholdBank] = None,
        training: bool = False,
        use_gpu_keeper: Optional[bool] = None,
    ):
        self.model = model
        self.mode = mode
        self.cfg = cfg or MemoryConfig()
        self.policy = policy
        self.threshold_bank = threshold_bank
        self.training = training
        self.use_gpu_keeper = (
            self.cfg.use_gpu_keeper if use_gpu_keeper is None else use_gpu_keeper
        )
        self.trackers: List[LivingMemoryTracker] = []
        self._handles = []
        self.architecture: str = "unknown"
        self.n_layers: int = 0

    def attach(self) -> "LivingMemoryController":
        self.detach()
        layers = get_model_layers(self.model)
        self.architecture, self.n_layers = describe_layer_stack(self.model)
        n = len(layers)
        self.n_layers = n
        self.trackers = [LivingMemoryTracker(self.cfg, self.policy) for _ in range(n)]
        if self.mode in ("compose", "simulate") and self.threshold_bank is None:
            self.threshold_bank = LayerThresholdBank(thresholds=[1e9] * n, cfg=self.cfg)
        if self.threshold_bank is not None and len(self.threshold_bank.thresholds) != n:
            # Resize / pad bank so indexing stays safe across architectures
            th = list(self.threshold_bank.thresholds)
            if len(th) < n:
                th = th + [1e9] * (n - len(th))
            else:
                th = th[:n]
            self.threshold_bank = LayerThresholdBank(thresholds=th, cfg=self.cfg)
        for li, blk in enumerate(layers):
            attn = get_attn_module(blk)
            self._handles.append(attn.register_forward_hook(self._make_hook(li)))
        return self

    def detach(self) -> None:
        for h in self._handles:
            h.remove()
        self._handles = []

    def reset_trackers(self) -> None:
        self.trackers = [LivingMemoryTracker(self.cfg, self.policy) for _ in self.trackers]

    def tracker_snapshots(self) -> List[dict]:
        return [t.snapshot() for t in self.trackers]

    def _make_hook(self, layer_id: int):
        mode = self.mode
        cfg = self.cfg
        trackers = self.trackers
        bank = self.threshold_bank
        training = self.training
        policy = self.policy
        use_gpu = self.use_gpu_keeper

        def hook(module, inp, out):
            if mode == "none":
                return out
            o = out[0] if isinstance(out, tuple) else out

            # Keeper (train + infer): vectorized GPU clamp/BFP — avoids per-block
            # .item() syncs that made decode feel like O(N²) even with KV cache.
            if mode == "keeper" and (training or use_gpu):
                res = apply_keeper_activation(
                    o, trackers[layer_id], cfg=cfg, policy=policy, apply_bfp=True
                )
                if isinstance(out, tuple):
                    return (res,) + out[1:]
                return res

            if mode == "compose":
                th = bank.threshold(layer_id) if bank is not None else 1e9
                if use_gpu:
                    res = compose_quantize_activations(trackers[layer_id], o, th, cfg=cfg)
                else:
                    arr = o.detach().float().cpu().numpy()
                    shape = arr.shape
                    flat = arr.reshape(-1, shape[-1])
                    for r in range(flat.shape[0]):
                        flat[r] = compose_quantize_row_numpy(
                            trackers[layer_id], flat[r], th, cfg=cfg
                        )
                    res = torch.tensor(flat.reshape(shape), dtype=o.dtype, device=o.device)
                if isinstance(out, tuple):
                    return (res,) + out[1:]
                return res

            if mode == "simulate":
                th = bank.threshold(layer_id) if bank is not None else 1e9
                if use_gpu:
                    res = simulate_quantize_activations(trackers[layer_id], o, th, cfg=cfg)
                else:
                    arr = o.detach().float().cpu().numpy()
                    shape = arr.shape
                    flat = arr.reshape(-1, shape[-1])
                    for r in range(flat.shape[0]):
                        flat[r] = simulate_quantize_row_numpy(
                            trackers[layer_id], flat[r], th, cfg=cfg
                        )
                    res = torch.tensor(flat.reshape(shape), dtype=o.dtype, device=o.device)
                if isinstance(out, tuple):
                    return (res,) + out[1:]
                return res

            if mode == "localmax" and use_gpu:
                res = localmax_activations_torch(o, cfg)
                if isinstance(out, tuple):
                    return (res,) + out[1:]
                return res

            if mode == "switch" and use_gpu:
                th = bank.threshold(layer_id) if bank is not None else 1e9
                res = switch_activations_torch(o, th, cfg)
                if isinstance(out, tuple):
                    return (res,) + out[1:]
                return res

            arr = o.detach().float().cpu().numpy()
            shape = arr.shape
            flat = arr.reshape(-1, shape[-1])
            for r in range(flat.shape[0]):
                row = flat[r]
                if mode == "localmax":
                    row = localmax_quantize(row, cfg)
                elif mode == "switch":
                    th = bank.threshold(layer_id) if bank is not None else 1e9
                    row = switch_quantize_row(row, th, cfg)
                elif mode == "keeper":
                    row = trackers[layer_id].quantize(row)
                flat[r] = row
            res = torch.tensor(flat.reshape(shape), dtype=o.dtype, device=o.device)
            if isinstance(out, tuple):
                return (res,) + out[1:]
            return res

        return hook

    def __enter__(self) -> "LivingMemoryController":
        return self.attach()

    def __exit__(self, exc_type, exc, tb) -> None:
        self.detach()
