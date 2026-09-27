"""Block floating-point helpers (from zakhor exp200 / exp105)."""

from __future__ import annotations

import math
from typing import Optional

import numpy as np

from .config import MemoryConfig


def exp_from_max(mx: float) -> float:
    return math.ceil(math.log2(mx)) if mx > 0 else 0.0


def bfp_quantize(block: np.ndarray, E: float, mbits: int) -> np.ndarray:
    lsb = 2.0 ** (E - mbits)
    q = np.clip(np.round(block / lsb), -(2**mbits - 1), 2**mbits - 1)
    return q * lsb


def localmax_quantize(v: np.ndarray, cfg: Optional[MemoryConfig] = None) -> np.ndarray:
    cfg = cfg or MemoryConfig()
    out = np.empty_like(v)
    for i in range(0, v.size, cfg.n_blk):
        b = v[i : i + cfg.n_blk]
        mx = float(np.abs(b).max())
        out[i : i + cfg.n_blk] = 0.0 if mx <= 0 else bfp_quantize(b, exp_from_max(mx), cfg.mbits)
    return out


def trimmed_quantize(v: np.ndarray, cfg: Optional[MemoryConfig] = None) -> np.ndarray:
    """Memoryless rival: exponent from 2nd-largest magnitude (exp200 TRIMMED)."""
    cfg = cfg or MemoryConfig()
    out = np.empty_like(v)
    for i in range(0, v.size, cfg.n_blk):
        b = v[i : i + cfg.n_blk]
        av = np.abs(b)
        if av.max() <= 0:
            out[i : i + cfg.n_blk] = 0.0
            continue
        second = np.partition(av, -2)[-2] if av.size >= 2 else av.max()
        ref = second if second > 0 else av.max()
        out[i : i + cfg.n_blk] = bfp_quantize(b, exp_from_max(float(ref)), cfg.mbits)
    return out


def clip_block(b: np.ndarray, av: np.ndarray, mx: float, mbits: int) -> np.ndarray:
    """exp209: clip peak channels to survivor-scale BFP."""
    top = av >= mx
    surv = av[~top]
    smx = float(surv.max()) if surv.size and surv.max() > 0 else mx
    Es = exp_from_max(smx)
    q = bfp_quantize(b, Es, mbits)
    q[top] = np.sign(b[top]) * (2**mbits - 1) * 2.0 ** (Es - mbits)
    return q
