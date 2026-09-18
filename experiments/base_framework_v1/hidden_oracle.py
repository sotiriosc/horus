"""Test-only true world. Runtime framework modules must never import this."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TrueTransition:
    epoch: int
    transaction_id: int
    pre_state: int
    action: str
    next_state: int
    consequence: int


class TrueWorldOracle:
    _ACTIONS = ("ADVANCE", "HOLD", "RETREAT")
    _NEXT = (1, 0, 3, 2, 1, 0, 3, 2, 1, 0, 3, 2)
    _CONSEQUENCE = (1, 0, -1, -1, 1, 0, 1, 0, 1, -1, 0, 1)

    def __init__(self, initial_state: int = 0) -> None:
        if initial_state not in range(4):
            raise ValueError("oracle state outside bounded world")
        self._state = initial_state
        self.execution_count = 0

    @property
    def state(self) -> int:
        return self._state

    def execute(self, epoch: int, transaction_id: int, action: str) -> TrueTransition:
        action_index = self._ACTIONS.index(action)
        index = self._state * 3 + action_index
        event = TrueTransition(
            epoch, transaction_id, self._state, action,
            self._NEXT[index], self._CONSEQUENCE[index],
        )
        self._state = event.next_state
        self.execution_count += 1
        return event
