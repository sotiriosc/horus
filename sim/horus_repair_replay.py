# SPDX-License-Identifier: CERN-OHL-S-2.0
"""Bit-exact transactional repair-and-replay model (matches horus_block_skpr_repair)."""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

_SIM = Path(__file__).resolve().parent
sys.path.insert(0, str(_SIM))

from rule5_bitexact import detect_and_intervene
from skpr_bitexact import SkprBitExact
from horus_nfe_bitexact import decode_array, encode_array, exponents


@dataclass
class ReplayStats:
    logical_blocks: int = 0
    commits: int = 0
    skpr_updates: int = 0
    flagged: int = 0
    replays: int = 0
    added_cycles: int = 0  # +1 per flagged (prereg model)
    keeper_rows: list = field(default_factory=list)


class HorusRepairReplayRuntime:
    """C5/C6 path: detect → suppress → repair → replay → commit/skpr once."""

    def __init__(self, T: int, repair_mode: str = "SAT"):
        assert repair_mode in ("SAT", "KEEP", "NONE")
        self.T = T
        self.repair_mode = repair_mode
        self.keeper = SkprBitExact()
        self.oracle = SkprBitExact()
        self.stats = ReplayStats()

    def reset(self) -> None:
        self.keeper.reset()
        self.oracle.reset()
        self.stats = ReplayStats()

    def process_block(
        self,
        values: list[float],
        *,
        fault: bool = False,
        fault_pos: int = 0,
        fault_gap: int = 0,
        fault_positions: Optional[list[int]] = None,
    ) -> list[float]:
        from horus_nfe_bitexact import pack, unpack

        words = encode_array(values)
        clean_words = list(words)
        if fault and fault_gap > 0:
            positions = list(fault_positions) if fault_positions is not None else [fault_pos]
            for p in positions:
                s, ex, ma = unpack(words[p])
                words[p] = pack(s, min(63, ex + fault_gap), ma)

        if self.repair_mode == "NONE":
            meta = detect_and_intervene(words, self.T, "NONE")
        else:
            meta = detect_and_intervene(words, self.T, self.repair_mode)

        flagged = bool(meta["flag"]) and self.repair_mode != "NONE"
        if flagged:
            out_words = meta["out"]
            self.stats.flagged += 1
            self.stats.replays += 1
            self.stats.added_cycles += 1
        else:
            out_words = list(words)

        out = decode_array(out_words)
        feed = max(exponents(out_words))
        kr = self.keeper.process(feed, self.stats.logical_blocks)
        o_max = max(exponents(clean_words))
        orr = self.oracle.process(o_max, self.stats.logical_blocks)
        self.stats.keeper_rows.append({
            "i": self.stats.logical_blocks,
            "flag": int(flagged),
            "fault": int(fault),
            "feed": feed,
            "oracle_feed": o_max,
            "state": kr["state_exp"],
            "oracle_state": orr["state_exp"],
            "tag": kr["tag"],
            "oracle_tag": orr["tag"],
        })
        self.stats.logical_blocks += 1
        self.stats.commits += 1
        self.stats.skpr_updates += 1
        return out


def process_tensor_repair(
    runtime: HorusRepairReplayRuntime,
    arr,
    plan: dict,
):
    import numpy as np
    flat = np.asarray(arr, dtype=np.float64).reshape(-1)
    n = flat.size
    pad = (8 - (n % 8)) % 8
    if pad:
        flat = np.concatenate([flat, np.zeros(pad)])
    out = np.empty_like(flat)
    from horus_block_runtime import _plan_entry

    for b in range(flat.size // 8):
        sl = flat[b * 8:(b + 1) * 8].tolist()
        if b in plan:
            positions, fgap = _plan_entry(plan[b])
            po = runtime.process_block(
                sl,
                fault=True,
                fault_pos=positions[0],
                fault_gap=fgap,
                fault_positions=positions,
            )
        else:
            po = runtime.process_block(sl, fault=False)
        out[b * 8:(b + 1) * 8] = po
    return out[:n].reshape(arr.shape)
