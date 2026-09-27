"""Vectorized GPU paths for localmax / switch / compose / simulate.

Avoids per-block ``.item()`` / ``.cpu().numpy()`` syncs that made those modes
100–300s/run while keeper was ~2s.
"""

from __future__ import annotations

import math
from typing import Optional, Tuple

import torch
import torch.nn.functional as F

from .config import MemoryConfig
from .torch_keeper import _update_tracker_from_tensor_gpu
from .torch_quantize import _headroom_for_policy, _update_state_torch
from .tracker import LivingMemoryTracker


def _as_blocks(
    x: torch.Tensor, n_blk: int
) -> Tuple[torch.Tensor, Tuple, int, int]:
    work = x if x.dtype == torch.float32 else x.float()
    *lead, H = work.shape
    pad = (n_blk - (H % n_blk)) % n_blk
    if pad:
        work = F.pad(work, (0, pad))
    blocks = work.reshape(-1, work.shape[-1] // n_blk, n_blk)
    return blocks, tuple(lead), H, pad


def _from_blocks(
    blocks: torch.Tensor,
    lead: Tuple,
    H: int,
    pad: int,
    dtype: torch.dtype,
) -> torch.Tensor:
    flat_h = blocks.shape[1] * blocks.shape[2]
    out = blocks.reshape(*lead, flat_h)
    if pad:
        out = out[..., :H]
    return out.to(dtype=dtype)


@torch.no_grad()
def bfp_blocks(blocks: torch.Tensor, mbits: int) -> torch.Tensor:
    mx = blocks.abs().amax(dim=-1, keepdim=True).clamp_min(1e-12)
    E = torch.ceil(torch.log2(mx))
    lsb = torch.pow(2.0, E - float(mbits))
    return torch.clamp(
        torch.round(blocks / lsb),
        -(2**mbits - 1),
        2**mbits - 1,
    ) * lsb


@torch.no_grad()
def clip_bfp_blocks(blocks: torch.Tensor, mbits: int) -> torch.Tensor:
    """Survivor-scale BFP with peak channels saturated (switch/exp209 clip)."""
    av = blocks.abs()
    mx = av.amax(dim=-1, keepdim=True)
    # 2nd-largest ≈ survivor max when the peak is unique
    top2 = av.topk(k=min(2, av.shape[-1]), dim=-1).values
    if top2.shape[-1] == 1:
        smx = top2[..., 0:1]
    else:
        smx = top2[..., 1:2].clamp_min(1e-12)
    E = torch.ceil(torch.log2(smx.clamp_min(1e-12)))
    lsb = torch.pow(2.0, E - float(mbits))
    q = torch.clamp(
        torch.round(blocks / lsb),
        -(2**mbits - 1),
        2**mbits - 1,
    ) * lsb
    sat = (2**mbits - 1) * lsb
    top = av >= mx
    return torch.where(top, torch.sign(blocks) * sat, q)


@torch.no_grad()
def max_med_ratio_blocks(blocks: torch.Tensor) -> torch.Tensor:
    av = blocks.abs()
    mx = av.amax(dim=-1)
    med = av.median(dim=-1).values.clamp_min(1e-12)
    return mx / med


@torch.no_grad()
def localmax_activations_torch(
    x: torch.Tensor, cfg: Optional[MemoryConfig] = None
) -> torch.Tensor:
    cfg = cfg or MemoryConfig()
    n_blk, mbits = int(cfg.n_blk), int(cfg.mbits)
    blocks, lead, H, pad = _as_blocks(x, n_blk)
    q = bfp_blocks(blocks, mbits)
    zero = blocks.abs().amax(dim=-1, keepdim=True) <= 0
    q = torch.where(zero, torch.zeros_like(q), q)
    return _from_blocks(q, lead, H, pad, x.dtype)


@torch.no_grad()
def switch_activations_torch(
    x: torch.Tensor,
    threshold: float,
    cfg: Optional[MemoryConfig] = None,
) -> torch.Tensor:
    cfg = cfg or MemoryConfig()
    n_blk, mbits = int(cfg.n_blk), int(cfg.mbits)
    blocks, lead, H, pad = _as_blocks(x, n_blk)
    ratio = max_med_ratio_blocks(blocks)
    local = bfp_blocks(blocks, mbits)
    clipped = clip_bfp_blocks(blocks, mbits)
    hot = (ratio > threshold).unsqueeze(-1)
    zero = blocks.abs().amax(dim=-1, keepdim=True) <= 0
    q = torch.where(hot, clipped, local)
    q = torch.where(zero, torch.zeros_like(q), q)
    return _from_blocks(q, lead, H, pad, x.dtype)


@torch.no_grad()
def compose_quantize_activations_fast(
    tracker: LivingMemoryTracker,
    x: torch.Tensor,
    threshold: float,
    cfg: Optional[MemoryConfig] = None,
) -> torch.Tensor:
    """Anomaly → localmax; calm → keeper (vectorized, one sync for tracker)."""
    cfg = cfg or tracker.cfg
    n_blk, mbits = int(cfg.n_blk), int(cfg.mbits)
    blocks, lead, H, pad = _as_blocks(x, n_blk)
    av = blocks.abs()
    mx = av.amax(dim=-1)
    ratio = max_med_ratio_blocks(blocks)
    anomalous = ratio > threshold
    zero = mx <= 0

    local = bfp_blocks(blocks, mbits)
    local = torch.where(zero.unsqueeze(-1), torch.zeros_like(local), local)

    # Tracker: anomalous → regime nudge; calm → soft digest (one CPU sync)
    mx_list = mx.reshape(-1).tolist()
    an_list = anomalous.reshape(-1).tolist()
    z_list = zero.reshape(-1).tolist()
    tracker.stats.blocks += len(mx_list)
    for mxi, ani, zi in zip(mx_list, an_list, z_list):
        if zi or mxi <= 0:
            tracker.n += 1
            continue
        if ani:
            if tracker.s is not None:
                d = abs(math.log2(mxi) - tracker.s)
                if d > (tracker.G + 1):
                    tracker.cnt += 1
                else:
                    tracker.cnt = 0
                if tracker.cnt >= cfg.k_regime:
                    tracker.s = math.log2(mxi)
                    tracker.cnt = 0
                    tracker.settle = cfg.k_regime + cfg.settle_extra
                    tracker.stats.regime_events += 1
            else:
                tracker.s = math.log2(mxi)
            tracker.n += 1
        else:
            _update_state_torch(tracker, float(mxi), False, 0.0)
            if tracker.settle > 0:
                tracker.settle -= 1
            tracker.n += 1

    # Keeper clamp + BFP on full activation (uses updated ceiling)
    hr = _headroom_for_policy(cfg, "soft")
    c = tracker.ceiling()
    clamp_lim = c * hr if math.isfinite(c) else float("inf")
    work = x.float()
    if math.isfinite(clamp_lim):
        kept = torch.clamp(work, min=-clamp_lim, max=clamp_lim)
    else:
        kept = work
    kept_blocks, lead2, H2, pad2 = _as_blocks(kept, n_blk)
    kept_q = bfp_blocks(kept_blocks, mbits)
    keeper = _from_blocks(kept_q, lead2, H2, pad2, torch.float32)

    local_flat = _from_blocks(local, lead, H, pad, torch.float32)
    n_blocks = blocks.shape[1]
    mask_h = (
        anomalous.unsqueeze(-1)
        .expand(-1, n_blocks, n_blk)
        .reshape(*lead, n_blocks * n_blk)
    )
    if pad:
        mask_h = mask_h[..., :H]
    out = torch.where(mask_h, local_flat, keeper)
    return out.to(dtype=x.dtype)


@torch.no_grad()
def simulate_quantize_activations_fast(
    tracker: LivingMemoryTracker,
    x: torch.Tensor,
    threshold: float,
    cfg: Optional[MemoryConfig] = None,
) -> torch.Tensor:
    """Localmax → stability switch → keep pred | blend soft/hard keeper.

    Same routing idea as ``simulate_quantize_row``, but vectorized: no per-block
    tracker clones or ``.item()`` sync storms.
    """
    cfg = cfg or tracker.cfg
    n_blk, mbits = int(cfg.n_blk), int(cfg.mbits)
    st = tracker.stats
    if not hasattr(st, "stable_blocks"):
        st.stable_blocks = 0
    if not hasattr(st, "unstable_blocks"):
        st.unstable_blocks = 0
    if not hasattr(st, "confidence_sum"):
        st.confidence_sum = 0.0

    blocks, lead, H, pad = _as_blocks(x, n_blk)
    pred_b = bfp_blocks(blocks, mbits)
    zero = blocks.abs().amax(dim=-1) <= 0
    pred_b = torch.where(zero.unsqueeze(-1), torch.zeros_like(pred_b), pred_b)
    ratio = max_med_ratio_blocks(pred_b)
    stable = (ratio <= threshold) | zero

    # Soft tracker update once (continuity commit), then soft/hard clamp+BFP
    _update_tracker_from_tensor_gpu(x, tracker)
    c = tracker.ceiling()
    work = x.float()

    def _clamp_bfp(hr: float) -> torch.Tensor:
        lim = c * hr if math.isfinite(c) else float("inf")
        y = torch.clamp(work, min=-lim, max=lim) if math.isfinite(lim) else work
        yb, lead_y, Hy, pady = _as_blocks(y, n_blk)
        return _from_blocks(bfp_blocks(yb, mbits), lead_y, Hy, pady, torch.float32)

    soft = _clamp_bfp(_headroom_for_policy(cfg, "soft"))
    hard = _clamp_bfp(_headroom_for_policy(cfg, "hard"))
    pred = _from_blocks(pred_b, lead, H, pad, torch.float32)

    th = float(threshold) if threshold > 0 and math.isfinite(threshold) else 1e9
    stab_conf = 1.0 / (1.0 + (ratio / max(th, 1e-6)).clamp_min(0.0))
    scale = soft.abs().mean().clamp_min(1e-6)
    agree = 1.0 / (1.0 + (soft - hard).abs().mean() / scale)
    conf_b = 0.5 * stab_conf + 0.5 * agree  # [n_rows, n_blocks]

    n_blocks = blocks.shape[1]
    conf_flat = (
        conf_b.unsqueeze(-1)
        .expand(-1, n_blocks, n_blk)
        .reshape(*lead, n_blocks * n_blk)
    )
    stable_flat = (
        stable.unsqueeze(-1)
        .expand(-1, n_blocks, n_blk)
        .reshape(*lead, n_blocks * n_blk)
    )
    if pad:
        conf_flat = conf_flat[..., :H]
        stable_flat = stable_flat[..., :H]
    blended = conf_flat * soft + (1.0 - conf_flat) * hard
    out = torch.where(stable_flat, pred, blended)

    n_stable = int(stable.sum().item())
    n_total = int(stable.numel())
    st.stable_blocks += n_stable
    st.unstable_blocks += n_total - n_stable
    st.confidence_sum += float(stab_conf.mean().item()) * n_total
    st.blocks += n_total

    return out.to(dtype=x.dtype)
