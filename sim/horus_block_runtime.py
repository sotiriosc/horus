# SPDX-License-Identifier: CERN-OHL-S-2.0
"""
Block-N=8 Horus runtime matching tile sideband semantics.

Modes (preregistration):
  FP_REFERENCE, HORUS_NO_KEEPER, HORUS_LOCALMAX, HORUS_RULE2,
  HORUS_RULE2_RULE5_A, HORUS_RULE2_RULE5_B,
  HORUS_RULE2_RULE5_SAT, HORUS_RULE2_RULE5_KEEP
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import numpy as np

_SIM = Path(__file__).resolve().parent
if str(_SIM) not in sys.path:
    sys.path.insert(0, str(_SIM))

from horus_nfe_bitexact import decode_array, encode_array, exponents, pack, unpack
from rule5_bitexact import detect_and_intervene
from skpr_bitexact import SkprBitExact, W_CAL

BLOCK = 8

MODE_ALIASES = {
    "R0": "FP_REFERENCE",
    "R1": "HORUS_NO_KEEPER",
    "R2": "HORUS_RULE2",
    "R3A": "HORUS_RULE2_RULE5_A",
    "R3B": "HORUS_RULE2_RULE5_B",
    "R4SAT": "HORUS_RULE2_RULE5_SAT",
    "R4KEEP": "HORUS_RULE2_RULE5_KEEP",
    "HORUS_LOCALMAX": "HORUS_NO_KEEPER",
}


@dataclass
class RuntimeStats:
    blocks: int = 0
    flags: int = 0
    false_flags: int = 0  # flag on non-faulted block (caller sets fault mask)
    nan_inf: int = 0
    keeper_rows: list = field(default_factory=list)


class HorusBlockRuntime:
    def __init__(self, mode: str, T: int, seed: int = 0):
        mode = MODE_ALIASES.get(mode, mode)
        self.mode = mode
        self.T = int(T)
        self.stats = RuntimeStats()
        self.keeper: Optional[SkprBitExact] = None
        self.oracle: Optional[SkprBitExact] = None
        if mode not in ("FP_REFERENCE", "HORUS_NO_KEEPER"):
            self.keeper = SkprBitExact()
            self.oracle = SkprBitExact()
        self._block_i = 0
        self.rng = np.random.RandomState(seed)

    def reset(self) -> None:
        self.stats = RuntimeStats()
        self._block_i = 0
        if self.keeper:
            self.keeper.reset()
        if self.oracle:
            self.oracle.reset()

    def _intervene_mode(self) -> str:
        if self.mode.endswith("_SAT"):
            return "SAT"
        if self.mode.endswith("_KEEP"):
            return "KEEP"
        return "NONE"

    def _skpr_feed(self, meta: dict) -> int:
        if self.mode in ("HORUS_RULE2", "HORUS_RULE2_RULE5_A"):
            return meta["e_max"]
        if self.mode == "HORUS_RULE2_RULE5_B":
            return meta["e_second"] if meta["flag"] else meta["e_max"]
        if self.mode in ("HORUS_RULE2_RULE5_SAT", "HORUS_RULE2_RULE5_KEEP"):
            return meta["e_max_out"]
        return meta["e_max"]

    def process_block(
        self,
        values: list[float],
        *,
        fault: bool = False,
        fault_pos: int = 0,
        fault_gap: int = 0,
        fault_positions: Optional[list[int]] = None,
        clean_for_oracle: Optional[list[float]] = None,
    ) -> list[float]:
        """Encode → optional spike → Rule5 → optional keeper → decode."""
        if self.mode == "FP_REFERENCE":
            return list(values)

        words = encode_array(values)
        clean_words = encode_array(clean_for_oracle) if clean_for_oracle is not None else list(words)

        if fault and fault_gap > 0:
            positions = list(fault_positions) if fault_positions is not None else [fault_pos]
            for p in positions:
                s, ex, ma = unpack(words[p])
                words[p] = pack(s, min(63, ex + fault_gap), ma)

        meta = detect_and_intervene(words, self.T, self._intervene_mode())
        out_words = meta["out"]

        # Elements: R3A/R3B leave unflagged path as LOCALMAX encode (no clip).
        # Quantize through NFE only (already encoded); decode out_words.
        out = decode_array(out_words)

        if self.keeper is not None:
            feed = self._skpr_feed(meta)
            kr = self.keeper.process(feed, self._block_i)
            # Oracle on clean block LOCALMAX
            o_exps = exponents(clean_words)
            o_max = max(o_exps)
            orr = self.oracle.process(o_max, self._block_i)
            self.stats.keeper_rows.append({
                "i": self._block_i,
                "flag": meta["flag"],
                "fault": int(fault),
                "feed": feed,
                "oracle_feed": o_max,
                "state": kr["state_exp"],
                "oracle_state": orr["state_exp"],
                "tag": kr["tag"],
                "oracle_tag": orr["tag"],
            })

        self.stats.blocks += 1
        self.stats.flags += int(meta["flag"])
        if meta["flag"] and not fault:
            self.stats.false_flags += 1
        if any(not np.isfinite(x) for x in out):
            self.stats.nan_inf += 1
        self._block_i += 1
        return out

    def process_tensor(self, arr: np.ndarray, fault_plan: Optional[dict] = None) -> np.ndarray:
        """Flatten → blocks of 8 → process → reshape. Tail padded with 0."""
        flat = np.asarray(arr, dtype=np.float64).reshape(-1)
        n = flat.size
        pad = (BLOCK - (n % BLOCK)) % BLOCK
        if pad:
            flat = np.concatenate([flat, np.zeros(pad)])
        out = np.empty_like(flat)
        nblocks = flat.size // BLOCK
        for b in range(nblocks):
            sl = flat[b * BLOCK:(b + 1) * BLOCK].tolist()
            fault = False
            fpos, fgap = 0, 0
            if fault_plan and b in fault_plan:
                fault, fpos, fgap = True, fault_plan[b][0], fault_plan[b][1]
            po = self.process_block(sl, fault=fault, fault_pos=fpos, fault_gap=fgap,
                                   clean_for_oracle=sl if not fault else None)
            # For oracle on faulted blocks: use pre-fault values
            if fault:
                # re-process oracle path already handled inside via clean_for_oracle
                pass
            out[b * BLOCK:(b + 1) * BLOCK] = po
        # Fix oracle clean path for faulted: process_block with clean_for_oracle=sl
        # when fault — need to pass pre-fault. Redo faulted blocks properly:
        return out[:n].reshape(arr.shape)


def build_fault_plan(
    n_blocks: int,
    regime: str,
    T: int,
    fault_seed: int,
    warmup: int = W_CAL,
) -> dict[int, tuple[int, int]]:
    """Map block_index → (pos, gap_boost)."""
    rng = np.random.RandomState(fault_seed)
    plan: dict[int, tuple[int, int]] = {}
    if regime == "clean":
        return plan
    if regime == "sparse":
        gap = T + 1
        for i in range(warmup, n_blocks, 32):
            plan[i] = (int(rng.randint(0, BLOCK)), gap)
    elif regime.startswith("burst_K"):
        K = int(regime.split("K")[1])
        gap = T + 8
        i = warmup + 8
        while i + K <= n_blocks:
            for k in range(K):
                plan[i + k] = (int(rng.randint(0, BLOCK)), gap)
            i += 48
    elif regime == "persistent":
        gap = T + 8
        start = max(warmup, n_blocks // 2)
        for k in range(16):
            if start + k < n_blocks:
                plan[start + k] = (int(rng.randint(0, BLOCK)), gap)
    elif regime == "recovery":
        gap = T + 8
        i = warmup + 8
        for k in range(4):
            if i + k < n_blocks:
                plan[i + k] = (int(rng.randint(0, BLOCK)), gap)
        # remainder clean
    else:
        raise ValueError(regime)
    return plan


def _plan_entry(entry) -> tuple[list[int], int]:
    """Normalize plan entry to (positions, gap). Legacy: (pos, gap)."""
    if isinstance(entry, dict):
        return list(entry["positions"]), int(entry["gap"])
    if isinstance(entry[0], (list, tuple)):
        return list(entry[0]), int(entry[1])
    return [int(entry[0])], int(entry[1])


def process_tensor_with_plan(
    runtime: HorusBlockRuntime,
    arr: np.ndarray,
    plan: dict,
) -> np.ndarray:
    flat = np.asarray(arr, dtype=np.float64).reshape(-1)
    n = flat.size
    pad = (BLOCK - (n % BLOCK)) % BLOCK
    if pad:
        flat = np.concatenate([flat, np.zeros(pad)])
    out = np.empty_like(flat)
    nblocks = flat.size // BLOCK
    for b in range(nblocks):
        sl = flat[b * BLOCK:(b + 1) * BLOCK].tolist()
        if b in plan:
            positions, fgap = _plan_entry(plan[b])
            po = runtime.process_block(
                sl,
                fault=True,
                fault_pos=positions[0],
                fault_gap=fgap,
                fault_positions=positions,
                clean_for_oracle=sl,
            )
        else:
            po = runtime.process_block(sl, fault=False, clean_for_oracle=sl)
        out[b * BLOCK:(b + 1) * BLOCK] = po
    return out[:n].reshape(arr.shape)
