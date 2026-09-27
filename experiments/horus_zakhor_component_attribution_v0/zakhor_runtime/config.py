from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryConfig:
    """Living-memory / keeper defaults.

    Path 1 (stronger clamp): ceiling_scale and headrooms are set *below* the
    earlier relaxed generation defaults so stranger gating bites harder.

    Path 2 (GPU): ``use_gpu_keeper=True`` runs quantize on-device (see
    ``torch_quantize.py``) instead of the CPU numpy round-trip.
    """

    n_blk: int = 8
    mbits: int = 6
    alpha: float = 1.0 / 16.0
    k_regime: int = 3
    cal_blocks: int = 128
    settle_extra: int = 4

    # --- Path 1: stronger ceiling pressure (lower = tighter clamp) ---
    # Prior relaxed values were g_floor=1.25, ceiling_scale=1.25,
    # soft=5.0, tight=1.25. Tightened for stronger stranger gating.
    g_floor: float = 0.85
    ceiling_scale: float = 0.85
    clamp_headroom_soft: float = 2.5
    clamp_headroom_tight: float = 0.85

    # --- Path 2: on-device keeper for generation ---
    use_gpu_keeper: bool = True

    # exp209 switch calibration
    pareto_pct: float = 0.25
    # model
    default_model: str = "gpt2-medium"
    eval_window: int = 512
