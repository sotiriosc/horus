"""Experiment-side truth overlay; never supplies evidence or authorization."""

from dataclasses import replace
from experiments.base_framework_v1.hidden_oracle import TrueWorldOracle


def changed_consequence(event, new_regime):
    if new_regime and event.pre_state == 1:
        if event.action == "HOLD":
            return replace(event, consequence=-1)
        if event.action == "ADVANCE":
            return replace(event, consequence=1)
    return event


class ConsequenceOverlay:
    def __init__(self, arm, initial_state=1):
        if arm not in ("CONTROL", "SHIFT"):
            raise ValueError("unknown world arm")
        self._arm = arm
        self._world = TrueWorldOracle(initial_state)
        self.events = []

    @property
    def state(self):
        return self._world.state

    def execute(self, epoch, transaction_id, action):
        original = self._world.execute(epoch, transaction_id, action)
        new_regime = self._arm == "SHIFT" and self._world.execution_count > 3
        actual = changed_consequence(original, new_regime)
        self.events.append((original, actual, "NEW" if new_regime else "OLD"))
        return actual
