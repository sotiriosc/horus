"""Active grounded-authority decision policy.

Historical experiment entry points remain frozen. Import ``decide`` here for
the current incumbent; ``previous_incumbent_decide`` is the rollback control.
"""

from .policy import previous_incumbent_decide, promoted_decide

# Explicitly approved promotion of the frozen evaluated S candidate.
decide = promoted_decide

__all__ = ("decide", "previous_incumbent_decide", "promoted_decide")
