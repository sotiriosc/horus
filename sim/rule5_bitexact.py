# SPDX-License-Identifier: CERN-OHL-S-2.0
"""Rule 5 detect / optional SAT|KEEP — wraps skpr_golden (RTL-matched golden)."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_SIM = Path(__file__).resolve().parent
if str(_SIM) not in sys.path:
    sys.path.insert(0, str(_SIM))

from skpr_golden import calibrate_T, detect_and_clip  # noqa: E402


def detect(block: list[int], T: int) -> dict[str, Any]:
    """Detect-only (no element rewrite)."""
    d = detect_and_clip(block, T, "SAT")
    return {
        "flag": d["flag"],
        "e_max": d["e_max"],
        "e_second": d["e_second"],
        "gap": d["gap"],
        "argmax": d["argmax"],
        "block_scale": d["e_second"] if d["flag"] else d["e_max"],
    }


def detect_and_intervene(block: list[int], T: int, mode: str) -> dict[str, Any]:
    """mode: 'NONE' | 'SAT' | 'KEEP'."""
    if mode in (None, "NONE", "none"):
        meta = detect(block, T)
        meta["out"] = list(block)
        meta["e_max_out"] = meta["e_max"]
        return meta
    d = detect_and_clip(block, T, mode.upper())
    return {
        "out": d["out"],
        "flag": d["flag"],
        "e_max": d["e_max"],
        "e_second": d["e_second"],
        "gap": d["gap"],
        "argmax": d["argmax"],
        "e_max_out": d["e_max_out"],
        "block_scale": d["e_max_out"] if d["flag"] else d["e_max"],
    }


def calibrate_threshold(gaps: list[int], target_rate: float = 0.0025):
    return calibrate_T(gaps, target_rate)
