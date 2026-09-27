"""Inference-only bit-flip fault injection for activation tensors.

Attaches forward hooks on GPT-2 attention blocks and flips random bits in
activation outputs with probability ``bit_flip_rate`` per bit. After flips,
non-finite values (NaN/Inf) are detected, logged, and recovered so generation
can continue for fault-injection experiments.

Does not participate in training.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import torch


def set_determinism(seed: Optional[int]) -> None:
    """Seed Python, NumPy, and Torch RNGs when ``seed`` is not None."""
    if seed is None:
        return
    import random

    import numpy as np

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def flip_bits_float_tensor(
    tensor: torch.Tensor,
    rate: float,
    generator: torch.Generator,
) -> Tuple[torch.Tensor, int]:
    """Flip each bit of a floating tensor independently with probability ``rate``.

    Works on float16 / bfloat16 / float32 by viewing the storage as integer
    bits of matching width. Returns ``(corrupted_tensor, n_flips)``.
    """
    if rate is None or rate <= 0.0:
        return tensor, 0
    if not tensor.is_floating_point():
        return tensor, 0

    out = tensor.detach().clone().contiguous()
    dtype = out.dtype
    if dtype == torch.float32:
        ival = out.view(torch.int32)
        n_bit_width = 32
    elif dtype == torch.float16:
        ival = out.view(torch.int16)
        n_bit_width = 16
    elif dtype == torch.bfloat16:
        ival = out.view(torch.int16)
        n_bit_width = 16
    else:
        tmp, n = flip_bits_float_tensor(out.float(), rate, generator)
        return tmp.to(dtype=dtype), n

    import numpy as np

    device = ival.device
    gen_device = generator.device if hasattr(generator, "device") else torch.device("cpu")
    flips = 0
    np_signed = np.int32 if n_bit_width == 32 else np.int16
    np_unsigned = np.uint32 if n_bit_width == 32 else np.uint16
    for b in range(n_bit_width):
        rnd = torch.rand(ival.shape, generator=generator, device=gen_device)
        if device.type != "cpu":
            rnd = rnd.to(device=device)
        mask = rnd < rate
        n = int(mask.sum().item())
        if n == 0:
            continue
        flips += n
        bit_val = np_signed(np_unsigned(1) << np_unsigned(b))
        bit = torch.tensor(bit_val, dtype=ival.dtype, device=device)
        ival.bitwise_xor_(mask.to(dtype=ival.dtype) * bit)

    return out, flips


def recover_nonfinite(
    tensor: torch.Tensor,
    *,
    nan: float = 0.0,
) -> Tuple[torch.Tensor, Dict[str, Any]]:
    """Replace NaN with ``nan`` and clamp Inf to dtype finite range.

    Returns ``(recovered_tensor, info)`` where ``info`` includes counts and
    whether recovery changed any value.
    """
    if not tensor.is_floating_point():
        return tensor, {
            "nan_count": 0,
            "inf_count": 0,
            "nonfinite_count": 0,
            "recovery_applied": False,
        }

    t = tensor
    nan_mask = torch.isnan(t)
    inf_mask = torch.isinf(t)
    nan_count = int(nan_mask.sum().item())
    inf_count = int(inf_mask.sum().item())
    nonfinite = nan_count + inf_count
    if nonfinite == 0:
        return t, {
            "nan_count": 0,
            "inf_count": 0,
            "nonfinite_count": 0,
            "recovery_applied": False,
        }

    finfo = torch.finfo(t.dtype if t.dtype in (torch.float16, torch.float32, torch.bfloat16) else torch.float32)
    # bfloat16 finfo exists on recent torch; fallback to float32 limits
    try:
        posinf = float(finfo.max)
        neginf = float(finfo.min)
    except (TypeError, ValueError):
        posinf = float(torch.finfo(torch.float32).max)
        neginf = float(torch.finfo(torch.float32).min)

    recovered = torch.nan_to_num(t, nan=nan, posinf=posinf, neginf=neginf)
    return recovered, {
        "nan_count": nan_count,
        "inf_count": inf_count,
        "nonfinite_count": nonfinite,
        "recovery_applied": True,
        "nan_replaced_with": nan,
        "posinf_clamped_to": posinf,
        "neginf_clamped_to": neginf,
    }


def sanitize_logits(logits: torch.Tensor) -> Tuple[torch.Tensor, bool]:
    """Last-line defense before multinomial: no NaN/Inf/negative-mass paths."""
    if torch.isfinite(logits).all():
        return logits, False
    finfo = torch.finfo(logits.dtype if logits.dtype == torch.float32 else torch.float32)
    clean = torch.nan_to_num(
        logits.float(),
        nan=-1e4,
        posinf=float(finfo.max) if logits.dtype == torch.float32 else 1e4,
        neginf=-1e4,
    )
    return clean.to(dtype=logits.dtype), True


@dataclass
class LayerFaultRecord:
    layer_id: int
    layer_name: str
    flips: int = 0
    corrupted_values: int = 0  # elements that became non-finite after flips
    nan_count: int = 0
    inf_count: int = 0
    recovery_applied: bool = False
    hook_calls: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layer": self.layer_id,
            "layer_name": self.layer_name,
            "flips": self.flips,
            "corrupted_values": self.corrupted_values,
            "nan_count": self.nan_count,
            "inf_count": self.inf_count,
            "recovery_applied": self.recovery_applied,
            "hook_calls": self.hook_calls,
        }


@dataclass
class BitFlipStats:
    flips_applied: int = 0
    calls: int = 0
    nan_total: int = 0
    inf_total: int = 0
    corrupted_values_total: int = 0
    recovery_happened: bool = False
    by_layer: Dict[int, LayerFaultRecord] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        affected = [
            rec.to_dict()
            for _, rec in sorted(self.by_layer.items())
            if rec.flips > 0 or rec.nan_count > 0 or rec.inf_count > 0 or rec.recovery_applied
        ]
        return {
            "flips_applied": self.flips_applied,
            "hook_calls": self.calls,
            "nan_total": self.nan_total,
            "inf_total": self.inf_total,
            "corrupted_values_total": self.corrupted_values_total,
            "recovery_happened": self.recovery_happened,
            "affected_layers": affected,
        }


def layer_name_for(layer_id: int, target: str = "attn", arch: str = "gpt2") -> str:
    from .layers import layer_path

    return layer_path(arch, layer_id, attn=(target == "attn"))


class BitFlipInjector:
    """Register inference hooks that corrupt attention-block activations."""

    def __init__(
        self,
        bit_flip_rate: float = 0.0,
        seed: Optional[int] = None,
        target: str = "attn",
        recover: bool = True,
    ):
        self.bit_flip_rate = float(bit_flip_rate or 0.0)
        self.seed = seed
        self.target = target
        self.recover = recover
        self.stats = BitFlipStats()
        self._handles: List[Any] = []
        self._generator = torch.Generator(device="cpu")
        self._arch: str = "gpt2"
        if seed is not None:
            self._generator.manual_seed(int(seed) ^ 0xB17F1105)
        else:
            self._generator.manual_seed(0)

    @property
    def active(self) -> bool:
        return self.bit_flip_rate > 0.0

    def attach(self, model) -> "BitFlipInjector":
        from .layers import describe_layer_stack, get_attn_module, get_model_layers

        self.detach()
        self.stats = BitFlipStats()
        if not self.active:
            return self
        self._arch, _ = describe_layer_stack(model)
        layers = get_model_layers(model)
        for li, blk in enumerate(layers):
            module = get_attn_module(blk) if self.target == "attn" else blk
            self._handles.append(module.register_forward_hook(self._make_hook(li)))
        return self

    def detach(self) -> None:
        for h in self._handles:
            h.remove()
        self._handles = []

    def _make_hook(self, layer_id: int):
        rate = self.bit_flip_rate
        gen = self._generator
        stats = self.stats
        recover = self.recover
        lname = layer_name_for(layer_id, self.target, arch=self._arch)

        def hook(module, inp, out):
            if rate <= 0.0:
                return out
            o = out[0] if isinstance(out, tuple) else out
            corrupted, n_flips = flip_bits_float_tensor(o, rate, gen)

            # Always inspect after flips (before recovery).
            nan_count = int(torch.isnan(corrupted).sum().item())
            inf_count = int(torch.isinf(corrupted).sum().item())
            corrupted_values = nan_count + inf_count

            recovery_applied = False
            if recover and corrupted_values > 0:
                corrupted, info = recover_nonfinite(corrupted)
                recovery_applied = bool(info["recovery_applied"])
            elif corrupted_values > 0 and not recover:
                # Still must not pass NaN/Inf into sampling — force recovery
                # but mark that policy requested no-recover (we override for safety).
                corrupted, info = recover_nonfinite(corrupted)
                recovery_applied = True

            # Final guarantee: finite tensor leaves the hook.
            if not torch.isfinite(corrupted).all():
                corrupted, info = recover_nonfinite(corrupted)
                recovery_applied = True

            stats.flips_applied += n_flips
            stats.calls += 1
            stats.nan_total += nan_count
            stats.inf_total += inf_count
            stats.corrupted_values_total += corrupted_values
            if recovery_applied:
                stats.recovery_happened = True

            rec = stats.by_layer.get(layer_id)
            if rec is None:
                rec = LayerFaultRecord(layer_id=layer_id, layer_name=lname)
                stats.by_layer[layer_id] = rec
            rec.flips += n_flips
            rec.corrupted_values += corrupted_values
            rec.nan_count += nan_count
            rec.inf_count += inf_count
            rec.hook_calls += 1
            if recovery_applied:
                rec.recovery_applied = True

            out_t = corrupted.to(dtype=o.dtype)
            if isinstance(out, tuple):
                return (out_t,) + out[1:]
            return out_t

        return hook

    def __enter__(self) -> "BitFlipInjector":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.detach()
