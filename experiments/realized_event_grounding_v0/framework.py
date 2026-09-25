"""Receipt-bound atomic layer around the unchanged five-component loop.

A/B are shared-root compatibility adapters, NOT independent truth observations.
The old stationary witness C is replaced by exact receipt-origin/identity
checking. Neither agreement nor the old process registry confers authority.
"""
from copy import deepcopy
from dataclasses import dataclass

from experiments.base_framework_v1.framework import CrossSourceFramework, StepResult
from experiments.base_framework_v1.types import SourceReceipt
from .receipt import RealizedEventReceipt

PACKAGE_LIMIT = 8
SHARED_ROOT = "SHARED_REALIZED_EVENT_ROOT"


@dataclass(frozen=True)
class EvidencePackage:
    receipt: RealizedEventReceipt
    a: tuple
    b: tuple
    c: tuple


def evidence(receipt):
    """Untrusted construction: even A+B+C agreement cannot mint receipt origin."""
    return EvidencePackage(receipt, receipt.binding(), receipt.binding(), receipt.identity())


@dataclass(frozen=True)
class AuthorizedEvent:
    package_id: tuple
    pair_decision_id: int
    receipt: RealizedEventReceipt
    prediction: object


class SharedReceiptPairGate:
    """Legacy pair syntax only; grounding was checked against the root first."""
    @staticmethod
    def authorize(pending, a, b):
        for item, port in ((a, "A"), (b, "B")):
            if (item.epoch, item.transaction_id, item.channel_sequence, item.pre_state, item.action) != (
                pending.epoch, pending.transaction_id, pending.channel_sequence,
                pending.proposal_pre_state, pending.action):
                return False, "receipt_identity"
            if (item.source_id, item.lineage_class, item.fault_domain) != (
                    "SOURCE_" + port, SHARED_ROOT, SHARED_ROOT):
                return False, "shared_root_adapter_identity"
        return (a.observation_id != b.observation_id and
                (a.observed_next_state, a.observed_consequence) ==
                (b.observed_next_state, b.observed_consequence)), "shared_receipt_binding"


def _event_tuple(record):
    return (record.epoch, record.transaction_id, record.pre_state, record.action,
            record.next_state, record.consequence)


class RealizedEventFramework:
    def __init__(self, receipt_port, initial_state=1, epoch=1001):
        self.__receipt_port = receipt_port
        self.inner = CrossSourceFramework(initial_state, epoch)
        self.inner._requires_package = True
        self.inner.pair_authorizer = SharedReceiptPairGate()
        self.packages = []

    def _audit(self, core, packages, memory=True):
        if not len(packages) == len(core.pairs.decisions) == len(core.memory.records):
            raise ValueError("receipt/pair/Memory ring length")
        for package, pair, record in zip(packages, core.pairs.decisions, core.memory.records):
            receipt = package.receipt
            if (package.package_id != receipt.identity() or
                    package.pair_decision_id != pair.pair_decision_id or
                    _event_tuple(pair) != receipt.binding()[:6] or
                    pair.measurement_matches != core.measure_auditor.expected(package.prediction, pair)):
                raise ValueError("retained receipt/pair binding")
            if memory and not core.memory.matches(record, pair):
                raise ValueError("retained receipt/Memory binding")
        core.assert_bounds()
        if len(packages) > PACKAGE_LIMIT:
            raise ValueError("receipt package bound")

    def begin_step(self, **kwargs):
        if self.__receipt_port.current() is not None:
            raise RuntimeError("external driver must resolve the previous event")
        try:
            # Permit the existing bounded Memory repair only from receipt-bound pairs.
            self._audit(self.inner, self.packages, memory=False)
            staged = deepcopy(self.inner)
            result = staged.begin_step(**kwargs)
            self._audit(staged, self.packages)
        except (ValueError, RuntimeError):
            return self.inner._reject("begin validation failed", executed=False)
        if isinstance(result, StepResult):
            return self.inner._reject(result.reason, executed=False)
        staged.continuation_authorized = False
        self.inner = staged
        return deepcopy(result)

    def start_epoch(self, epoch):
        if self.__receipt_port.current() is not None:
            raise RuntimeError("pending external event")
        self._audit(self.inner, self.packages)
        self.inner.start_epoch(epoch)

    def _check(self, package):
        root = self.__receipt_port.current()
        if root is None or not isinstance(package, EvidencePackage) or package.receipt is not root:
            raise ValueError("inauthentic_or_substituted_receipt")
        pending = self.inner.pending
        if pending is None:
            raise ValueError("no_pending_proposal")
        if (root.epoch, root.transaction_id, root.pre_state, root.action) != (
                pending.epoch, pending.transaction_id, pending.proposal_pre_state, pending.action):
            raise ValueError("execution_identity")
        if (any(type(x) is not int for x in (root.epoch, root.transaction_id,
                root.pre_state, root.next_state, root.realized_consequence, root.event_id)) or
                root.pre_state not in range(4) or root.next_state not in range(4) or
                root.realized_consequence not in (-1, 0, 1) or root.event_id not in range(1, 25)):
            raise ValueError("receipt_domain")
        # Type-sensitive tuple equality avoids bool/int aliases in candidate data.
        for supplied, expected in ((package.a, root.binding()), (package.b, root.binding()),
                                   (package.c, root.identity())):
            if (type(supplied) is not tuple or len(supplied) != len(expected) or
                    any(type(x) is not type(y) or x != y for x, y in zip(supplied, expected))):
                raise ValueError("receipt_content_or_identity_binding")
        return root

    def submit_package(self, package, **faults):
        try:
            root = self._check(package)
            self._audit(self.inner, self.packages)
            staged = deepcopy(self.inner)
            pending = staged.pending
            prediction = staged._prediction_at_begin
            seq = pending.channel_sequence
            base = (root.epoch << 24) | (root.transaction_id << 8)
            adapters = [SourceReceipt(root.epoch, root.transaction_id, base | offset,
                "SOURCE_" + port, seq, root.pre_state, root.action, root.next_state,
                root.realized_consequence, SHARED_ROOT, SHARED_ROOT)
                for port, offset in (("A", 1), ("B", 2))]
            staged._package_grant = (root.epoch, root.transaction_id, seq,
                                    adapters[0].observation_id, adapters[1].observation_id)
            partial = staged.submit_receipt("A", adapters[0])
            if partial.committed:
                raise ValueError("partial publication")
            result = staged.submit_receipt("B", adapters[1], **faults)
            if not result.committed:
                return self.inner._reject(result.reason, executed=True)
            authorized = AuthorizedEvent(root.identity(), staged.pairs.decisions[-1].pair_decision_id,
                                         root, prediction)
            packages = (self.packages + [authorized])[-PACKAGE_LIMIT:]
            self._audit(staged, packages)
            if (staged._prediction_at_begin != self.inner._prediction_at_begin or
                    package.receipt is not self.__receipt_port.current()):
                raise ValueError("prediction_or_root_changed")
            staged._package_grant = None
            # No checks/callbacks between publication assignments. Single threaded.
            self.inner, self.packages = staged, packages
            return result
        except (ValueError, RuntimeError, TypeError, AttributeError) as exc:
            return self.inner._reject(str(exc), executed=self.__receipt_port.current() is not None)

    def submit_receipt(self, *args, **kwargs):
        return self.inner._reject("mandatory realized-event package", executed=True)

    def assert_bounds(self):
        self._audit(self.inner, self.packages)
