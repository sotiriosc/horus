"""Compose mode — complementary routing (separate option).

Do not average modes. Switch acts as controller between localmax (explore)
and keeper (preserve). Run `--mode none` separately as reality-check baseline.
"""

from __future__ import annotations

import math
from typing import Optional

import numpy as np
import torch

from .config import MemoryConfig
from .switch import max_med_ratio
from .torch_quantize import quantize_row_torch, _bfp_block, _expmax
from .tracker import LivingMemoryTracker


@torch.no_grad()
def compose_quantize_row(
    tracker: LivingMemoryTracker,
    row: torch.Tensor,
    threshold: float,
    cfg: Optional[MemoryConfig] = None,
) -> torch.Tensor:
    """Route one activation row: anomaly → localmax; calm → keeper."""
    cfg = cfg or tracker.cfg
    n_blk = cfg.n_blk
    out = torch.empty_like(row)
    H = row.numel()

    for i in range(0, H, n_blk):
        b = row[i : i + n_blk]
        av = b.abs()
        mx = float(av.max().item())
        tracker.stats.blocks += 1
        if mx <= 0:
            out[i : i + n_blk] = 0.0
            tracker.n += 1
            continue

        ratio = max_med_ratio(av.detach().cpu().numpy(), mx)
        anomalous = ratio > threshold

        if anomalous:
            # Switch → explore / conservative: Localmax; push regime toward reset
            if tracker.s is not None:
                d = abs(math.log2(mx) - tracker.s)
                if d > (tracker.G + 1):
                    tracker.cnt += 1
                else:
                    tracker.cnt = 0
                if tracker.cnt >= cfg.k_regime:
                    tracker.s = math.log2(mx)
                    tracker.cnt = 0
                    tracker.settle = cfg.k_regime + cfg.settle_extra
                    tracker.stats.regime_events += 1
            elif mx > 0:
                tracker.s = math.log2(mx)
            out[i : i + n_blk] = _bfp_block(b, _expmax(mx), cfg.mbits)
            tracker.n += 1
        else:
            # Switch → preserve: Keeper continuity
            out[i : i + n_blk] = quantize_row_torch(tracker, b.clone(), policy="soft")
    return out


@torch.no_grad()
def compose_quantize_activations(
    tracker: LivingMemoryTracker,
    x: torch.Tensor,
    threshold: float,
    cfg: Optional[MemoryConfig] = None,
) -> torch.Tensor:
    from .torch_fast import compose_quantize_activations_fast

    return compose_quantize_activations_fast(tracker, x, threshold, cfg=cfg)


def compose_quantize_row_numpy(
    tracker: LivingMemoryTracker,
    row: np.ndarray,
    threshold: float,
    cfg: Optional[MemoryConfig] = None,
) -> np.ndarray:
    t = torch.from_numpy(np.asarray(row, dtype=np.float32))
    return compose_quantize_row(tracker, t, threshold, cfg=cfg).numpy()
