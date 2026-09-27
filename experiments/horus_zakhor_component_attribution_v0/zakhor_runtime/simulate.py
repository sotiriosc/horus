"""Simulate mode — separate option (do not average with compose).

Pipeline per activation block:

    Input
      |
      v
   Localmax                 ← hypothesis / prediction
      |
      v
  "Is this prediction stable?"  ← Switch (max/med vs calibrated TH)
      |
      +---- yes → normal continuation (keep Localmax prediction)
      |
      +---- no  → Keeper simulation
                    |
                    possible states (soft / hard / pred-under-keeper)
                    |
                 confidence-weighted output
"""

from __future__ import annotations

import math
from typing import Optional, Tuple

import numpy as np
import torch

from .config import MemoryConfig
from .switch import max_med_ratio
from .torch_quantize import quantize_row_torch, _bfp_block, _expmax
from .tracker import LivingMemoryTracker


def _snapshot_tracker(tr: LivingMemoryTracker) -> dict:
    return {
        "s": tr.s,
        "G": tr.G,
        "n": tr.n,
        "cnt": tr.cnt,
        "settle": tr.settle,
        "cal": list(tr.cal),
        "policy": tr.policy,
    }


def _restore_tracker(tr: LivingMemoryTracker, snap: dict) -> None:
    tr.s = snap["s"]
    tr.G = snap["G"]
    tr.n = snap["n"]
    tr.cnt = snap["cnt"]
    tr.settle = snap["settle"]
    tr.cal = list(snap["cal"])
    tr.policy = snap["policy"]


def _clone_tracker(tr: LivingMemoryTracker) -> LivingMemoryTracker:
    c = LivingMemoryTracker(tr.cfg, tr.policy)
    _restore_tracker(c, _snapshot_tracker(tr))
    # fresh stats for the branch
    return c


def _agreement_confidence(states: Tuple[torch.Tensor, ...]) -> float:
    """1 when simulated keeper states agree; falls as they diverge."""
    if len(states) < 2:
        return 1.0
    ref = states[0]
    scale = float(ref.abs().mean().item()) + 1e-6
    total = 0.0
    n = 0
    for s in states[1:]:
        total += float((ref - s).abs().mean().item())
        n += 1
    mean_l1 = total / max(n, 1)
    return float(1.0 / (1.0 + mean_l1 / scale))


def _stability_confidence(ratio: float, threshold: float) -> float:
    """How clearly below the switch threshold the prediction sits."""
    if threshold <= 0 or not math.isfinite(threshold):
        return 1.0
    # ratio << threshold → ~1; at threshold → 0.5; far above → ~0
    return float(1.0 / (1.0 + max(0.0, ratio) / threshold))


@torch.no_grad()
def simulate_quantize_row(
    tracker: LivingMemoryTracker,
    row: torch.Tensor,
    threshold: float,
    cfg: Optional[MemoryConfig] = None,
) -> torch.Tensor:
    """Localmax → stability switch → continue | keeper-sim + confidence."""
    cfg = cfg or tracker.cfg
    n_blk = cfg.n_blk
    out = torch.empty_like(row)
    H = row.numel()

    # Ensure stats fields exist (older trackers may lack them)
    st = tracker.stats
    if not hasattr(st, "stable_blocks"):
        st.stable_blocks = 0  # type: ignore[attr-defined]
    if not hasattr(st, "unstable_blocks"):
        st.unstable_blocks = 0  # type: ignore[attr-defined]
    if not hasattr(st, "confidence_sum"):
        st.confidence_sum = 0.0  # type: ignore[attr-defined]

    for i in range(0, H, n_blk):
        b = row[i : i + n_blk]
        av = b.abs()
        mx = float(av.max().item())
        tracker.stats.blocks += 1
        if mx <= 0:
            out[i : i + n_blk] = 0.0
            tracker.n += 1
            continue

        # 1) Localmax — hypothesis / prediction
        pred = _bfp_block(b, _expmax(mx), cfg.mbits)
        pav = pred.abs()
        pmx = float(pav.max().item())
        if pmx <= 0:
            out[i : i + n_blk] = 0.0
            tracker.n += 1
            continue

        # 2) Switch — "Is this prediction stable?"
        ratio = max_med_ratio(pav.detach().cpu().numpy(), pmx)
        stable = ratio <= threshold
        conf = _stability_confidence(ratio, threshold)

        if stable:
            # 3a) Normal continuation — keep Localmax prediction
            out[i : i + n_blk] = pred
            st.stable_blocks += 1  # type: ignore[attr-defined]
            st.confidence_sum += conf  # type: ignore[attr-defined]
            # Digest scale gently from the continued prediction (soft keeper update
            # on pred would double-quantize; update scalars only via a soft pass
            # on a clone, then copy scalars — keeps living memory alive).
            dig = _clone_tracker(tracker)
            dig.policy = "soft"
            _ = quantize_row_torch(dig, pred.clone(), policy="soft")
            tracker.s, tracker.G = dig.s, dig.G
            tracker.cnt, tracker.settle = dig.cnt, dig.settle
            tracker.cal = list(dig.cal)
            tracker.n += 1
        else:
            # 3b) Keeper simulation — possible states → confidence
            soft_tr = _clone_tracker(tracker)
            soft_tr.policy = "soft"
            state_soft = quantize_row_torch(soft_tr, b.clone(), policy="soft")

            hard_tr = _clone_tracker(tracker)
            hard_tr.policy = "hard"
            state_hard = quantize_row_torch(hard_tr, b.clone(), policy="hard")

            pred_tr = _clone_tracker(tracker)
            pred_tr.policy = "soft"
            state_pred = quantize_row_torch(pred_tr, pred.clone(), policy="soft")

            agree = _agreement_confidence((state_soft, state_hard, state_pred))
            # Unstable branch: blend stability signal with state agreement
            conf = 0.5 * conf + 0.5 * agree

            # Low confidence → lean conservative (hard); high → soft continuity
            blended = conf * state_soft + (1.0 - conf) * state_hard
            out[i : i + n_blk] = blended

            st.unstable_blocks += 1  # type: ignore[attr-defined]
            st.confidence_sum += conf  # type: ignore[attr-defined]

            # Commit living state from the soft simulation (continuity branch)
            tracker.s, tracker.G = soft_tr.s, soft_tr.G
            tracker.cnt, tracker.settle = soft_tr.cnt, soft_tr.settle
            tracker.cal = list(soft_tr.cal)
            tracker.n = soft_tr.n
            tracker.stats.stranger_elems += soft_tr.stats.stranger_elems
            tracker.stats.regime_events += soft_tr.stats.regime_events

    return out


@torch.no_grad()
def simulate_quantize_activations(
    tracker: LivingMemoryTracker,
    x: torch.Tensor,
    threshold: float,
    cfg: Optional[MemoryConfig] = None,
) -> torch.Tensor:
    from .torch_fast import simulate_quantize_activations_fast

    return simulate_quantize_activations_fast(tracker, x, threshold, cfg=cfg)


def simulate_quantize_row_numpy(
    tracker: LivingMemoryTracker,
    row: np.ndarray,
    threshold: float,
    cfg: Optional[MemoryConfig] = None,
) -> np.ndarray:
    t = torch.from_numpy(np.asarray(row, dtype=np.float32))
    return simulate_quantize_row(tracker, t, threshold, cfg=cfg).numpy()
