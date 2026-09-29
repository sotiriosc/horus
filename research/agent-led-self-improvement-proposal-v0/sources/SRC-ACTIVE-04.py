"""Thin selectors over the frozen, evaluated controlled-pairing implementation.

These functions choose an action. Protected execution, signed receipts,
Measure, authorization, and Memory publication remain in their existing code.
"""

from experiments.grounded_stagnation_escape_promotion_controlled_v0 import worker as frozen


def previous_incumbent_decide(store, memory, client, index):
    """The exact canonical grounded-authority I decision path."""
    context = frozen.context(store, memory, index)
    return frozen.canonical_action_decision(store, client, index, context)


def promoted_decide(store, memory, client, index):
    """The evaluated S path: incumbent plus bounded stagnation escape."""
    context = frozen.context(store, memory, index)
    return frozen.frozen_decide(store, memory, client, "ACTIVE", "S", index, context)
