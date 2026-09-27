"""GPU / on-device keeper quantize (Path 2).

Ports ``LivingMemoryTracker.quantize`` + ``_update_state`` to PyTorch so
generation no longer does GPU→CPU→numpy→GPU every token. Tracker scalars
(s, G, cnt, …) remain Python floats; only activation tensors stay on device.

Faithful to the numpy path: per 8-channel block, stranger-gated BFP, leaky
digest, K-step regime rebirth.
"""

from __future__ import annotations

import math
from typing import Optional, Tuple

import torch

from .config import MemoryConfig
from .tracker import LivingMemoryTracker


def _headroom_for_policy(cfg: MemoryConfig, policy: str) -> float:
    if policy in ("keeper", "hard"):
        return float(cfg.clamp_headroom_tight)
    if policy == "observe":
        return float("inf")
    return float(cfg.clamp_headroom_soft)


def _bfp_block(block: torch.Tensor, E: float, mbits: int) -> torch.Tensor:
    lsb = 2.0 ** (E - mbits)
    q = torch.clamp(torch.round(block / lsb), -(2**mbits - 1), 2**mbits - 1) * lsb
    return q


def _expmax(mx: float) -> float:
    return float(math.ceil(math.log2(mx))) if mx > 0 else 0.0


def _update_state_torch(
    tracker: LivingMemoryTracker,
    mx: float,
    has_stranger: bool,
    surv_max: float,
) -> None:
    """Same law as ``LivingMemoryTracker._update_state`` (scalar form)."""
    if mx <= 0:
        return
    if has_stranger and surv_max > 0:
        obs = math.log2(surv_max)
    else:
        obs = math.log2(mx)
    if tracker.s is None:
        tracker.s = obs
        return
    d = obs - tracker.s
    # innovations list is unused by train/generate logging; skip append
    # (would grow to O(blocks) per step and dominate Python time).
    if abs(d) > (tracker.G + 1):
        tracker.cnt += 1
    else:
        tracker.cnt = 0
    if tracker.cnt >= tracker.cfg.k_regime:
        tracker.s = obs
        tracker.cnt = 0
        tracker.settle = tracker.cfg.k_regime + tracker.cfg.settle_extra
        tracker.stats.regime_events += 1
    elif not has_stranger:
        tracker.s = tracker.s + tracker.cfg.alpha * d
        if tracker.n < tracker.cfg.cal_blocks:
            tracker.cal.append(max(0.0, d))
            if tracker.n == tracker.cfg.cal_blocks - 1 and tracker.cal:
                import numpy as np

                tracker.G = max(
                    float(tracker.cfg.g_floor),
                    float(np.ceil(np.percentile(tracker.cal, 99))),
                )


@torch.no_grad()
def quantize_row_torch(
    tracker: LivingMemoryTracker,
    row: torch.Tensor,
    policy: Optional[str] = None,
) -> torch.Tensor:
    """Quantize one 1-D activation row on its current device; update tracker."""
    policy = policy or tracker.policy
    cfg = tracker.cfg
    n_blk = cfg.n_blk
    mbits = cfg.mbits
    hr = _headroom_for_policy(cfg, policy)
    out = torch.empty_like(row)
    H = row.numel()

    for i in range(0, H, n_blk):
        b = row[i : i + n_blk]
        av = b.abs()
        mx_t = av.max()
        mx = float(mx_t.item())
        tracker.stats.blocks += 1
        if mx <= 0:
            out[i : i + n_blk] = 0.0
            tracker.n += 1
            continue

        c = tracker.ceiling()
        # Strangers vs living ceiling (state update uses ceiling, not clamp hr)
        if math.isfinite(c):
            stranger_mask = av > c
            has_stranger = bool(stranger_mask.any().item())
            if has_stranger:
                surv = av[~stranger_mask]
                surv_max = float(surv.max().item()) if surv.numel() else 0.0
            else:
                surv_max = 0.0
        else:
            has_stranger = False
            surv_max = 0.0
            stranger_mask = torch.zeros_like(av, dtype=torch.bool)

        _update_state_torch(tracker, mx, has_stranger, surv_max)
        if tracker.settle > 0:
            tracker.settle -= 1

        if policy == "observe":
            out[i : i + n_blk] = _bfp_block(b, _expmax(mx), mbits)
        else:
            # Clamp / BFP against ceiling * headroom (stronger when hr/scale low)
            cc = c * hr if math.isfinite(c) else float("inf")
            if not math.isfinite(cc):
                out[i : i + n_blk] = _bfp_block(b, _expmax(mx), mbits)
            else:
                clip_mask = av > cc
                if not bool(clip_mask.any().item()):
                    out[i : i + n_blk] = _bfp_block(b, _expmax(mx), mbits)
                else:
                    tracker.stats.stranger_elems += int(clip_mask.sum().item())
                    surv = av[~clip_mask]
                    smx = float(surv.max().item()) if surv.numel() and float(surv.max().item()) > 0 else mx
                    E = _expmax(smx)
                    q = _bfp_block(b, E, mbits)
                    sat = (2**mbits - 1) * (2.0 ** (E - mbits))
                    q = torch.where(clip_mask, torch.sign(b) * sat, q)
                    out[i : i + n_blk] = q
        tracker.n += 1
    return out


@torch.no_grad()
def quantize_activations_torch(
    tracker: LivingMemoryTracker,
    x: torch.Tensor,
    policy: Optional[str] = None,
) -> torch.Tensor:
    """Apply on-device keeper quantize to ``[batch, seq, hidden]`` (or 2-D)."""
    policy = policy or tracker.policy
    orig_dtype = x.dtype
    work = x.float()
    shape = work.shape
    flat = work.reshape(-1, shape[-1])
    out_flat = torch.empty_like(flat)
    for r in range(flat.size(0)):
        out_flat[r] = quantize_row_torch(tracker, flat[r], policy=policy)
    return out_flat.reshape(shape).to(dtype=orig_dtype)
