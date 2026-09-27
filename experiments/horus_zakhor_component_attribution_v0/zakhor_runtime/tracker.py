"""Living-memory scalar tracker.

Ported from zakhor `research/exp105_neighbors.py` Tracker and
`docs/exp200_transformer_gate.py` / `exp201_policy_trial.py` Keeper.
Aligned with Horus ScaleKeeper rules: leaky digest (α), stranger/ceiling
exclusion, K-step regime rebirth.

Generation note: MemoryConfig Path 1 uses a *stronger* clamp
(lower ceiling_scale / headrooms). Path 2 runs quantize on GPU via
``torch_quantize.quantize_activations_torch`` (see hooks).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np

from .bfp import bfp_quantize, exp_from_max
from .config import MemoryConfig


@dataclass
class TrackerStats:
    blocks: int = 0
    stranger_elems: int = 0
    regime_events: int = 0
    innovations: List[float] = field(default_factory=list)
    stable_blocks: int = 0
    unstable_blocks: int = 0
    confidence_sum: float = 0.0


class LivingMemoryTracker:
    """Per-layer scalar scale memory over a token/activation stream.

    State `s` is log2 of tracked magnitude.
    Ceiling = 2^(s+G) * ceiling_scale.
    Strangers (|>clamp_threshold|) are quantized against survivors and do not
    update state. After K consecutive large |Δ|, state rebirths to obs.
    """

    def __init__(self, cfg: Optional[MemoryConfig] = None, policy: str = "soft"):
        self.cfg = cfg or MemoryConfig()
        self.policy = policy  # soft | hard | keeper | observe
        self.s: Optional[float] = None
        self.G: float = float(self.cfg.g_floor)
        self.n: int = 0
        self.cal: List[float] = []
        self.cnt: int = 0
        self.settle: int = 0
        self.stats = TrackerStats()

    def ceiling(self) -> float:
        """Per-layer activation ceiling used for stranger gating."""
        if self.s is None:
            return float("inf")
        return (2.0 ** (self.s + self.G)) * self.cfg.ceiling_scale

    def snapshot(self) -> dict:
        judged = self.stats.stable_blocks + self.stats.unstable_blocks
        mean_conf = (
            self.stats.confidence_sum / judged if judged > 0 else None
        )
        return {
            "s": self.s,
            "G": self.G,
            "n": self.n,
            "ceiling": None if self.s is None else self.ceiling(),
            "ceiling_scale": self.cfg.ceiling_scale,
            "regime_events": self.stats.regime_events,
            "stranger_elems": self.stats.stranger_elems,
            "stable_blocks": self.stats.stable_blocks,
            "unstable_blocks": self.stats.unstable_blocks,
            "mean_confidence": mean_conf,
        }

    def _local_block(self, b: np.ndarray) -> np.ndarray:
        mx = float(np.abs(b).max())
        if mx <= 0:
            return np.zeros_like(b)
        return bfp_quantize(b, exp_from_max(mx), self.cfg.mbits)

    def _update_state(self, mx: float, av: np.ndarray, c: float) -> None:
        if mx <= 0:
            return
        stranger = av > c
        if stranger.any() and (~stranger).any() and float(av[~stranger].max()) > 0:
            obs = math.log2(float(av[~stranger].max()))
        else:
            obs = math.log2(mx)
        if self.s is None:
            self.s = obs
            return
        d = obs - self.s
        self.stats.innovations.append(abs(d))
        if abs(d) > (self.G + 1):
            self.cnt += 1
        else:
            self.cnt = 0
        if self.cnt >= self.cfg.k_regime:
            self.s = obs
            self.cnt = 0
            self.settle = self.cfg.k_regime + self.cfg.settle_extra
            self.stats.regime_events += 1
        elif not stranger.any():
            self.s = self.s + self.cfg.alpha * d
            if self.n < self.cfg.cal_blocks:
                self.cal.append(max(0.0, d))
                if self.n == self.cfg.cal_blocks - 1 and self.cal:
                    self.G = max(
                        float(self.cfg.g_floor),
                        float(np.ceil(np.percentile(self.cal, 99))),
                    )

    def _guard_quantize(self, b: np.ndarray, av: np.ndarray, c: float, headroom: float) -> np.ndarray:
        cc = c * headroom
        stranger = av > cc
        if not stranger.any():
            return self._local_block(b)
        self.stats.stranger_elems += int(stranger.sum())
        surv = av[~stranger]
        smx = float(surv.max()) if surv.size and float(surv.max()) > 0 else float(av.max())
        E = exp_from_max(smx)
        q = bfp_quantize(b, E, self.cfg.mbits)
        q[stranger] = np.sign(b[stranger]) * (2**self.cfg.mbits - 1) * 2.0 ** (E - self.cfg.mbits)
        return q

    def quantize(self, v: np.ndarray) -> np.ndarray:
        """Stranger-gated BFP over N-channel blocks; updates living scalar."""
        cfg = self.cfg
        out = np.empty_like(v)
        for i in range(0, v.size, cfg.n_blk):
            b = v[i : i + cfg.n_blk]
            av = np.abs(b)
            mx = float(av.max())
            self.stats.blocks += 1
            if mx <= 0:
                out[i : i + cfg.n_blk] = 0.0
                self.n += 1
                continue
            c = self.ceiling()
            self._update_state(mx, av, c)
            if self.settle > 0:
                self.settle -= 1

            if self.policy == "observe":
                out[i : i + cfg.n_blk] = self._local_block(b)
            elif self.policy in ("keeper", "hard"):
                out[i : i + cfg.n_blk] = self._guard_quantize(
                    b, av, c, cfg.clamp_headroom_tight
                )
            else:  # soft (default generate policy)
                out[i : i + cfg.n_blk] = self._guard_quantize(
                    b, av, c, cfg.clamp_headroom_soft
                )
            self.n += 1
        return out
