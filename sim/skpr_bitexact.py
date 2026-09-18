# SPDX-License-Identifier: CERN-OHL-S-2.0
"""SKPR Rules 1–4 — thin wrapper over scale_keeper_golden (RTL-matched)."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_SIM = Path(__file__).resolve().parent
if str(_SIM) not in sys.path:
    sys.path.insert(0, str(_SIM))

from scale_keeper_golden import (  # noqa: E402
    FRAC_BITS, K, N_SETTLE, TAG_OK, TAG_OUTLIER, TAG_RESEEDED, TAG_SETTLING,
    W_CAL, ScaleKeeper,
)

PERSIST_Q_DEFAULT = 256
GUARD_Q_DEFAULT = 512


class SkprBitExact:
    def __init__(self, persist_bound_q: int = PERSIST_Q_DEFAULT,
                 guard_margin_q: int = GUARD_Q_DEFAULT):
        self._k = ScaleKeeper(persist_bound_q, guard_margin_q)

    def reset(self) -> None:
        self._k._reset()

    def process(self, e_max_in: int, block_idx: int | None = None) -> dict[str, Any]:
        state, ceil, tag, ev, evd = self._k.process_block(int(e_max_in), block_idx)
        return {
            "state_exp": state,
            "ceiling_exp": ceil,
            "tag": tag,
            "event_valid": bool(ev),
            "event_dir": evd,
            "state_q": self._k.state_q,
        }


__all__ = [
    "SkprBitExact", "PERSIST_Q_DEFAULT", "GUARD_Q_DEFAULT",
    "FRAC_BITS", "K", "N_SETTLE", "W_CAL",
    "TAG_OK", "TAG_OUTLIER", "TAG_SETTLING", "TAG_RESEEDED",
]
