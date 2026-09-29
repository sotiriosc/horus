"""Active grounded authority + bounded stagnation escape S + empirical E.

Historical study entry points remain frozen. ``promoted_decide`` is the exact
pre-E grounded-authority + S rollback selector. ``previous_incumbent_decide``
is the older grounded-authority-only control.
"""

from .policy import previous_incumbent_decide, promoted_decide
from .empirical_policy import integrated_decide

# Explicitly approved E promotion, after the zero-inference activation gate.
decide = integrated_decide

__all__ = ("decide", "previous_incumbent_decide", "promoted_decide", "integrated_decide")
