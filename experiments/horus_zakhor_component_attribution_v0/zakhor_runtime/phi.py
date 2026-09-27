"""Golden-ratio constants (from zakhor core/phi_theory.py)."""

from __future__ import annotations

import math

PHI: float = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV: float = PHI - 1.0  # == 1/φ


def shell_magnitude(hi: float, j: int) -> float:
    """φ-codebook shell j: hi · (1/φ)^j."""
    return hi * (PHI_INV ** j)


def log_phi(x: float) -> float:
    """Shell coordinate L(x) = log(x) / log(1/φ)."""
    if x <= 0:
        return float("-inf")
    return math.log(x) / math.log(PHI_INV)
