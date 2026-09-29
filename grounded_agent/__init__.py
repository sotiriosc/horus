"""Active grounded-authority decision policy.

Historical experiment entry points remain frozen. Import ``decide`` here for
the current incumbent; ``previous_incumbent_decide`` is the rollback control.
"""

from .policy import previous_incumbent_decide, promoted_decide

# Activation changes only this selector after pre-activation verification.
decide = previous_incumbent_decide

__all__ = ("decide", "previous_incumbent_decide", "promoted_decide")
