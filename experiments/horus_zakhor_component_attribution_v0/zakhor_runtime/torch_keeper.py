"""Differentiable keeper clamp for training (forward + backward).

Hot path notes
--------------
Tracker updates used to call ``.item()`` inside nested Python loops over every
activation block — tens of thousands of CPU↔GPU syncs per layer per step.
We now compute all block statistics with vectorized GPU ops, sync **once**
per layer hook, then run the sequential scalar tracker on CPU.
"""

from __future__ import annotations

import math
from typing import Optional

import torch
import torch.nn.functional as F
from torch.autograd import Function

from .config import MemoryConfig
from .torch_quantize import _update_state_torch, _headroom_for_policy
from .tracker import LivingMemoryTracker


class STEClamp(Function):
    """Clamp in forward; identity STE gradient in backward."""

    @staticmethod
    def forward(ctx, input_tensor: torch.Tensor, min_val: float, max_val: float):
        return torch.clamp(input_tensor, min=min_val, max=max_val)

    @staticmethod
    def backward(ctx, grad_output):
        return grad_output, None, None


class STEBlockBFP(Function):
    """Block floating-point quantize in forward; identity STE in backward."""

    @staticmethod
    def forward(ctx, input_tensor: torch.Tensor, n_blk: int, mbits: int):
        *lead, H = input_tensor.shape
        pad = (n_blk - (H % n_blk)) % n_blk
        x_pad = F.pad(input_tensor, (0, pad)) if pad else input_tensor
        flat = x_pad.reshape(-1, x_pad.shape[-1] // n_blk, n_blk)
        mx = flat.abs().amax(dim=-1, keepdim=True).clamp_min(1e-12)
        E = torch.ceil(torch.log2(mx))
        lsb = torch.pow(2.0, E - float(mbits))
        q = torch.clamp(
            torch.round(flat / lsb),
            -(2**mbits - 1),
            2**mbits - 1,
        ) * lsb
        out = q.reshape(*lead, x_pad.shape[-1])
        return out[..., :H] if pad else out

    @staticmethod
    def backward(ctx, grad_output):
        return grad_output, None, None


def apply_keeper_activation(
    x: torch.Tensor,
    tracker: LivingMemoryTracker,
    cfg: Optional[MemoryConfig] = None,
    policy: str = "soft",
    apply_bfp: bool = True,
) -> torch.Tensor:
    """Ceiling clamp (+ optional BFP STE) with on-device tracker updates."""
    cfg = cfg or tracker.cfg
    hr = _headroom_for_policy(cfg, policy)

    with torch.no_grad():
        _update_tracker_from_tensor_gpu(x, tracker)
        c = tracker.ceiling()
        clamp_lim = c * hr if math.isfinite(c) else float("inf")

    if policy == "observe":
        return x

    if math.isfinite(clamp_lim):
        y = STEClamp.apply(x, -clamp_lim, clamp_lim)
    else:
        y = x

    if apply_bfp:
        y = STEBlockBFP.apply(y, int(cfg.n_blk), int(cfg.mbits))
    return y


@torch.no_grad()
def _update_tracker_from_tensor_gpu(x: torch.Tensor, tracker: LivingMemoryTracker) -> None:
    """Advance tracker from block maxima with a single GPU→CPU sync.

    Block abs-max (and stranger stats vs the *start-of-call* ceiling) are
    computed fully on GPU, then transferred once. The sequential living-memory
    state machine still runs in Python over those scalars — no per-block
    ``.item()`` syncs.
    """
    cfg = tracker.cfg
    n_blk = int(cfg.n_blk)
    work = x.detach()
    if work.dtype != torch.float32:
        work = work.float()

    *_, H = work.shape
    pad = (n_blk - (H % n_blk)) % n_blk
    if pad:
        work = F.pad(work, (0, pad))
    # [n_rows, n_blocks, n_blk]
    blocks = work.reshape(-1, work.shape[-1] // n_blk, n_blk)
    av = blocks.abs()
    mx = av.amax(dim=-1)  # [n_rows, n_blocks]

    # Stranger gating uses ceiling at the start of this activation update.
    # Within-hook ceiling evolution is approximated (avoids per-block syncs).
    c = tracker.ceiling()
    if math.isfinite(c):
        stranger = av > c
        has_stranger = stranger.any(dim=-1)
        surv_max = av.masked_fill(stranger, 0.0).amax(dim=-1)
    else:
        has_stranger = torch.zeros_like(mx, dtype=torch.bool)
        surv_max = torch.zeros_like(mx)

    # ONE sync for all block stats (not one sync per block).
    mx_list = mx.reshape(-1).tolist()
    hs_list = has_stranger.reshape(-1).tolist()
    sm_list = surv_max.reshape(-1).tolist()

    n_blocks = len(mx_list)
    tracker.stats.blocks += n_blocks

    for mxi, hsi, smi in zip(mx_list, hs_list, sm_list):
        if mxi <= 0:
            tracker.n += 1
            continue
        _update_state_torch(tracker, float(mxi), bool(hsi), float(smi))
        if tracker.settle > 0:
            tracker.settle -= 1
        tracker.n += 1
