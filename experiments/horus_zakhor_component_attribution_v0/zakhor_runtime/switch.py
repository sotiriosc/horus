"""Per-layer threshold switch (from zakhor docs/exp209_scaling.py).

Calibrate on a clean pass: collect max/median block stats per layer, freeze
TH_pl[li] at the upper Pareto percentile. At run time, blocks exceeding the
layer threshold are clip-quantized; others use localmax BFP.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence

import numpy as np

from .bfp import clip_block, localmax_quantize
from .config import MemoryConfig


def max_med_ratio(av: np.ndarray, mx: float) -> float:
    med = float(np.median(av))
    return float(mx / med) if med > 0 else 1e9


@dataclass
class LayerThresholdBank:
    thresholds: List[float] = field(default_factory=list)
    cfg: MemoryConfig = field(default_factory=MemoryConfig)

    def threshold(self, layer_id: int) -> float:
        if not self.thresholds:
            return 1e9
        if layer_id < 0 or layer_id >= len(self.thresholds):
            return 1e9
        return self.thresholds[layer_id]


def switch_quantize_row(
    v: np.ndarray,
    threshold: float,
    cfg: Optional[MemoryConfig] = None,
) -> np.ndarray:
    cfg = cfg or MemoryConfig()
    out = np.empty_like(v)
    for i in range(0, v.size, cfg.n_blk):
        b = v[i : i + cfg.n_blk]
        av = np.abs(b)
        mx = float(av.max())
        if mx <= 0:
            out[i : i + cfg.n_blk] = 0.0
            continue
        if max_med_ratio(av, mx) > threshold:
            out[i : i + cfg.n_blk] = clip_block(b, av, mx, cfg.mbits)
        else:
            out[i : i + cfg.n_blk] = localmax_quantize(b, cfg)
    return out


def thresholds_from_cal_stats(
    cal_pl: Sequence[Sequence[float]],
    pareto_pct: float = 0.25,
) -> List[float]:
    out = []
    for xs in cal_pl:
        if len(xs) > 50:
            out.append(float(np.percentile(np.asarray(xs), 100 - pareto_pct)))
        else:
            out.append(1e9)
    return out


def calibrate_layer_thresholds(
    model,
    tokenizer,
    text: str,
    cfg: Optional[MemoryConfig] = None,
    max_tokens: int = 512,
    device: Optional[str] = None,
) -> LayerThresholdBank:
    """Run a clean forward pass and freeze per-layer MAX/MED thresholds.

    Layer count comes from ``get_model_layers(model)`` (GPT-2 / Llama / Qwen /
    NeoX). Activation width is taken from each tensor's last dim — not hardcoded.

    Uses on-device block max/median ratios (one sync per layer chunk) — the old
    CPU ``.numpy()`` per-block path made chat appear stuck after weight load.
    """
    import torch

    from .layers import get_attn_module, get_model_layers
    from .torch_fast import max_med_ratio_blocks, _as_blocks

    cfg = cfg or MemoryConfig()
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    layers = get_model_layers(model)
    nlayer = len(layers)
    cal_pl: List[List[float]] = [[] for _ in range(nlayer)]
    n_blk = int(cfg.n_blk)

    def make_cal_hook(li: int):
        def hook(module, inp, out):
            o = out[0] if isinstance(out, tuple) else out
            with torch.no_grad():
                blocks, _, _, _ = _as_blocks(o.detach(), n_blk)
                ratio = max_med_ratio_blocks(blocks)
                mx = blocks.abs().amax(dim=-1)
                keep = mx > 0
                if bool(keep.any()):
                    # One sync per forward hook call (not per block)
                    cal_pl[li].extend(ratio[keep].reshape(-1).tolist())
            return out

        return hook

    ids = tokenizer(text, return_tensors="pt").input_ids[0][:max_tokens].to(device)
    handles = [
        get_attn_module(blk).register_forward_hook(make_cal_hook(li))
        for li, blk in enumerate(layers)
    ]
    try:
        with torch.inference_mode():
            step = min(int(cfg.eval_window), max_tokens)
            n_ids = min(int(ids.numel()), max_tokens)
            for start in range(0, max(0, n_ids - 1), step):
                chunk = ids[start : start + step]
                if chunk.numel() < 2:
                    break
                model(input_ids=chunk.unsqueeze(0), use_cache=False)
    finally:
        for h in handles:
            h.remove()
    return LayerThresholdBank(
        thresholds=thresholds_from_cal_stats(cal_pl, cfg.pareto_pct),
        cfg=cfg,
    )
