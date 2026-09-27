"""Independent four-state ground environment for base framework v0.

This module imports no framework policy, prediction, measurement, memory, or
recovery helper. Its immutable transition table is the external ground used by
the experiment.
"""

from __future__ import annotations

from dataclasses import dataclass


WORLD_STATES = (0, 1, 2, 3)
WORLD_ACTIONS = ("ADVANCE", "HOLD", "RETREAT")
EXTERNAL_LINEAGE = "EXTERNAL_PROTECTED"
SOURCE_IDENTITY = "bounded-world-v0"


_TRANSITIONS = {
    0: {"ADVANCE": (1, 1), "HOLD": (0, 0), "RETREAT": (3, -1)},
    1: {"ADVANCE": (2, -1), "HOLD": (1, 1), "RETREAT": (0, 0)},
    2: {"ADVANCE": (3, 1), "HOLD": (2, 0), "RETREAT": (1, 1)},
    3: {"ADVANCE": (0, -1), "HOLD": (3, 0), "RETREAT": (2, 1)},
}


@dataclass(frozen=True)
class StateReceipt:
    epoch: int
    transaction_id: int
    observation_id: int
    state: int
    source_identity: str = SOURCE_IDENTITY
    lineage: str = EXTERNAL_LINEAGE


@dataclass(frozen=True)
class ConsequenceReceipt:
    epoch: int
    transaction_id: int
    observation_id: int
    pre_state: int
    action: str
    next_state: int
    consequence: int
    source_identity: str = SOURCE_IDENTITY
    lineage: str = EXTERNAL_LINEAGE


class BoundedWorld:
    """Deterministic environment with an explicit bounded state space."""

    def __init__(self, initial_state: int = 0) -> None:
        if initial_state not in WORLD_STATES:
            raise ValueError("initial state outside bounded world")
        self._state = initial_state
        self.execution_count = 0

    @property
    def state(self) -> int:
        return self._state

    @staticmethod
    def _observation_id(epoch: int, transaction_id: int, phase: int) -> int:
        return (epoch << 20) | (transaction_id << 1) | phase

    def snapshot(self, epoch: int, transaction_id: int) -> StateReceipt:
        return StateReceipt(
            epoch=epoch,
            transaction_id=transaction_id,
            observation_id=self._observation_id(epoch, transaction_id, 0),
            state=self._state,
        )

    def step(self, action: str, epoch: int, transaction_id: int) -> ConsequenceReceipt:
        if action not in WORLD_ACTIONS:
            raise ValueError("environment received invalid action")
        pre_state = self._state
        next_state, consequence = _TRANSITIONS[pre_state][action]
        self._state = next_state
        self.execution_count += 1
        return ConsequenceReceipt(
            epoch=epoch,
            transaction_id=transaction_id,
            observation_id=self._observation_id(epoch, transaction_id, 1),
            pre_state=pre_state,
            action=action,
            next_state=next_state,
            consequence=consequence,
        )

