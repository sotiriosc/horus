"""External execution authority; not accessible through the candidate read port.

Object identity is a software capability in this single-threaded prototype,
not a cryptographic or hostile same-process security boundary. Only an object
in the external source's pending slot has authentic origin. Equal field values
or a frozen dataclass constructed by a candidate do not confer that origin.
"""
from dataclasses import dataclass
from typing import Callable

EXECUTION_LIMIT = 24


@dataclass(frozen=True)
class RealizedEventReceipt:
    epoch: int
    transaction_id: int
    pre_state: int
    action: str
    next_state: int
    realized_consequence: int
    event_id: int
    source_identity: str

    def binding(self):
        return (self.epoch, self.transaction_id, self.pre_state, self.action,
                self.next_state, self.realized_consequence, self.event_id,
                self.source_identity)

    def identity(self):
        return (self.source_identity, self.event_id, self.epoch, self.transaction_id)


@dataclass(frozen=True)
class ReceiptReadPort:
    """Read-only capability; no execute, mint, replace or release operation."""
    current: Callable[[], RealizedEventReceipt | None]


class ExternalExecutionBoundary:
    """Trusted lifetime-unique source identity and bounded external executor.

    The external driver owns this object. Framework components receive only
    reader(). A root that lies about execution is explicitly out of model.
    """
    def __init__(self, world, source_identity):
        if not isinstance(source_identity, str) or not source_identity:
            raise ValueError("trusted source lifetime identity required")
        self.__world = world
        self.__source_identity = source_identity
        self.__pending = None
        self.__count = 0

    def reader(self):
        return ReceiptReadPort(lambda: self.__pending)

    def _reported_event(self, actual):
        """Trusted emission boundary; overridden only by the root-failure control."""
        return actual

    def execute(self, epoch, transaction_id, action):
        if self.__pending is not None:
            raise RuntimeError("unresolved authentic event")
        if self.__count >= EXECUTION_LIMIT:
            raise RuntimeError("external execution lifetime bound")
        actual = self.__world.execute(epoch, transaction_id, action)
        # No receipt exists before the completed execution above.
        event = self._reported_event(actual)
        self.__count += 1
        self.__pending = RealizedEventReceipt(
            event.epoch, event.transaction_id, event.pre_state, event.action,
            event.next_state, event.consequence, self.__count, self.__source_identity)
        return self.__pending

    def release(self, receipt):
        """External driver retires the resolved pending slot; no history archive."""
        if receipt is not self.__pending or receipt is None:
            raise ValueError("only the current event can be retired")
        self.__pending = None
