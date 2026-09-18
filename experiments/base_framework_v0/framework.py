"""Smallest bounded Explorer/Map/Measure/Memory/Recovery closed loop.

The environment is injected by the caller. This module deliberately does not
import its transition table or transition helper.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable, Optional


WORLD_STATES = (0, 1, 2, 3)
ACTION_ORDER = ("ADVANCE", "HOLD", "RETREAT")
EXTERNAL_PROTECTED = "EXTERNAL_PROTECTED"
CANDIDATE_DERIVED = "CANDIDATE_DERIVED"
SHARED_ANCESTOR = "SHARED_ANCESTOR"
MEMORY_LIMIT = 8
TRACE_LIMIT = 16
EPISODE_LIMIT = 12
RECOVERY_ATTEMPT_LIMIT = 1


class AuthorityState(str, Enum):
    PROPOSED = "PROPOSED"
    OBSERVED = "OBSERVED"
    MEASURED = "MEASURED"
    QUARANTINED = "QUARANTINED"
    RECOVERING = "RECOVERING"
    AUTHORIZED = "AUTHORIZED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class ActionProposal:
    epoch: int
    transaction_id: int
    pre_state: int
    map_version: int
    action: str
    status: AuthorityState = AuthorityState.PROPOSED


@dataclass(frozen=True)
class Prediction:
    epoch: int
    transaction_id: int
    pre_state: int
    action: str
    next_state: int
    consequence: int


@dataclass(frozen=True)
class Measurement:
    epoch: int
    transaction_id: int
    observation_id: int
    matches: bool
    status: AuthorityState = AuthorityState.MEASURED


@dataclass(frozen=True)
class StateCandidate:
    epoch: int
    transaction_id: int
    observation_id: int
    source_identity: str
    value: int
    lineage: str = CANDIDATE_DERIVED
    status: AuthorityState = AuthorityState.PROPOSED


@dataclass(frozen=True)
class MemoryRecord:
    epoch: int
    transaction_id: int
    pre_state: int
    action: str
    observation_id: int
    next_state: int
    consequence: int
    measurement_matches: bool
    authorization: AuthorityState


@dataclass(frozen=True)
class TraceRecord:
    epoch: int
    transaction_id: int
    action: str
    status: AuthorityState
    detail: str
    continuation_authorized: bool


@dataclass
class MapState:
    state: int
    version: int
    epoch: int
    valid: bool = True


@dataclass(frozen=True)
class TransactionResult:
    transaction_id: int
    action: Optional[str]
    executed: bool
    committed: bool
    continued: bool
    incumbent_retained: bool
    recovery_authorized: bool
    reason: str


class Explorer:
    """Deterministic finite action policy whose scores come from Memory."""

    @staticmethod
    def scores(state: int, records: Iterable[MemoryRecord]) -> dict[str, float]:
        grouped: dict[str, list[int]] = {action: [] for action in ACTION_ORDER}
        for record in records:
            if record.pre_state == state and record.authorization == AuthorityState.AUTHORIZED:
                grouped[record.action].append(record.consequence)
        return {
            action: (sum(values) / len(values) if values else 0.0)
            for action, values in grouped.items()
        }

    def choose(self, state: int, records: Iterable[MemoryRecord]) -> str:
        scores = self.scores(state, records)
        return max(ACTION_ORDER, key=lambda action: (scores[action], -ACTION_ORDER.index(action)))

    def propose(
        self,
        map_state: MapState,
        records: Iterable[MemoryRecord],
        epoch: int,
        transaction_id: int,
        forced_action: Optional[str] = None,
    ) -> ActionProposal:
        action = forced_action if forced_action is not None else self.choose(map_state.state, records)
        return ActionProposal(
            epoch=epoch,
            transaction_id=transaction_id,
            pre_state=map_state.state,
            map_version=map_state.version,
            action=action,
        )


class MapModel:
    """Independent conditional model; it does not import environment truth."""

    def __init__(self, initial_state: int, epoch: int) -> None:
        self.current = MapState(initial_state, version=0, epoch=epoch)
        self.quarantine: list[MapState] = []

    @staticmethod
    def predict_from(state: int, action: str, epoch: int, transaction_id: int) -> Prediction:
        if action == "ADVANCE":
            next_state = (state + 1) % 4
            consequence = 1 if state in (0, 2) else -1
        elif action == "HOLD":
            next_state = state
            consequence = 1 if state == 1 else 0
        elif action == "RETREAT":
            next_state = (state - 1) % 4
            consequence = -1 if state == 0 else (0 if state == 1 else 1)
        else:
            raise ValueError("Map cannot predict unknown action")
        return Prediction(epoch, transaction_id, state, action, next_state, consequence)

    def predict(self, action: str, epoch: int, transaction_id: int) -> Prediction:
        return self.predict_from(self.current.state, action, epoch, transaction_id)

    def quarantine_incumbent(self) -> None:
        if len(self.quarantine) >= 1:
            raise RuntimeError("Map quarantine bound exceeded")
        self.quarantine.append(replace(self.current, valid=False))
        self.current.valid = False

    def commit(self, value: int, epoch: int) -> None:
        if value not in WORLD_STATES:
            raise ValueError("Map commit outside state space")
        self.current = MapState(value, self.current.version + 1, epoch, True)
        self.quarantine.clear()


class Measure:
    def evaluate(self, prediction: Prediction, receipt: Any, force_wrong: bool = False) -> Measurement:
        matches = (
            prediction.epoch == receipt.epoch
            and prediction.transaction_id == receipt.transaction_id
            and prediction.pre_state == receipt.pre_state
            and prediction.action == receipt.action
            and prediction.next_state == receipt.next_state
            and prediction.consequence == receipt.consequence
        )
        if force_wrong:
            matches = not matches
        return Measurement(receipt.epoch, receipt.transaction_id, receipt.observation_id, matches)


class EvidenceAuditor:
    """Recomputes measurement from protected receipt fields."""

    @staticmethod
    def expected(prediction: Prediction, receipt: Any) -> bool:
        return (
            receipt.lineage == EXTERNAL_PROTECTED
            and prediction.epoch == receipt.epoch
            and prediction.transaction_id == receipt.transaction_id
            and prediction.pre_state == receipt.pre_state
            and prediction.action == receipt.action
            and prediction.next_state == receipt.next_state
            and prediction.consequence == receipt.consequence
        )

    def verify(self, measurement: Measurement, prediction: Prediction, receipt: Any) -> bool:
        return (
            measurement.epoch == receipt.epoch
            and measurement.transaction_id == receipt.transaction_id
            and measurement.observation_id == receipt.observation_id
            and measurement.matches == self.expected(prediction, receipt)
        )


class ProtectedEvidenceStore:
    def __init__(self) -> None:
        self.receipts: list[Any] = []
        self.max_observed = 0

    def append(self, receipt: Any) -> None:
        if len(self.receipts) >= MEMORY_LIMIT:
            raise RuntimeError("protected receipt rotation must be paired by coordinator")
        self.receipts.append(receipt)
        self.max_observed = max(self.max_observed, len(self.receipts))

    def find(self, epoch: int, transaction_id: int, observation_id: int) -> Optional[Any]:
        for receipt in self.receipts:
            if (
                receipt.epoch == epoch
                and receipt.transaction_id == transaction_id
                and receipt.observation_id == observation_id
            ):
                return receipt
        return None


class OutcomeMemory:
    def __init__(self) -> None:
        self.records: list[MemoryRecord] = []
        self.quarantine: list[MemoryRecord] = []
        self.max_observed = 0
        self.evictions = 0

    @staticmethod
    def record_matches_receipt(record: MemoryRecord, receipt: Any) -> bool:
        return (
            receipt is not None
            and receipt.lineage == EXTERNAL_PROTECTED
            and record.epoch == receipt.epoch
            and record.transaction_id == receipt.transaction_id
            and record.observation_id == receipt.observation_id
            and record.pre_state == receipt.pre_state
            and record.action == receipt.action
            and record.next_state == receipt.next_state
            and record.consequence == receipt.consequence
            and record.measurement_matches
            and record.authorization == AuthorityState.AUTHORIZED
        )

    def audit(self, evidence: ProtectedEvidenceStore) -> tuple[list[MemoryRecord], list[MemoryRecord]]:
        valid: list[MemoryRecord] = []
        corrupt: list[MemoryRecord] = []
        for record in list(self.records):
            receipt = evidence.find(record.epoch, record.transaction_id, record.observation_id)
            if self.record_matches_receipt(record, receipt):
                valid.append(record)
            else:
                corrupt.append(record)
        if corrupt:
            if len(corrupt) > 1 or self.quarantine:
                raise RuntimeError("Memory quarantine bound exceeded")
            self.quarantine.extend(corrupt)
            self.records = valid
        return valid, corrupt

    def replace_quarantined(self, record: MemoryRecord) -> None:
        if len(self.quarantine) != 1:
            raise RuntimeError("expected one quarantined Memory record")
        self.records.append(record)
        self.records.sort(key=lambda item: (item.epoch, item.transaction_id))
        self.quarantine.clear()
        if len(self.records) > MEMORY_LIMIT:
            raise RuntimeError("Memory bound exceeded after recovery")

    def corrupt_consequence(self, transaction_id: int) -> None:
        for index, record in enumerate(self.records):
            if record.transaction_id == transaction_id:
                self.records[index] = replace(record, consequence=record.consequence + 7)
                return
        raise KeyError("record to corrupt not found")


class ActionAuthority:
    @staticmethod
    def authorize(proposal: ActionProposal, snapshot: Any, map_state: MapState) -> bool:
        return (
            proposal.action in ACTION_ORDER
            and proposal.epoch == snapshot.epoch == map_state.epoch
            and proposal.transaction_id == snapshot.transaction_id
            and proposal.pre_state == snapshot.state == map_state.state
            and proposal.map_version == map_state.version
            and map_state.valid
            and snapshot.lineage == EXTERNAL_PROTECTED
        )


class StateAuthorizer:
    def __init__(self) -> None:
        self.authorized_keys: set[tuple[int, int, int, str]] = set()

    @staticmethod
    def _matches(candidate: StateCandidate, evidence: Any, expected_value: int) -> bool:
        return (
            evidence.lineage == EXTERNAL_PROTECTED
            and candidate.epoch == evidence.epoch
            and candidate.transaction_id == evidence.transaction_id
            and candidate.observation_id == evidence.observation_id
            and candidate.source_identity == evidence.source_identity
            and candidate.value == expected_value
        )

    def authorize(self, candidate: StateCandidate, evidence: Any, expected_value: int, purpose: str) -> bool:
        if candidate.lineage not in (CANDIDATE_DERIVED, EXTERNAL_PROTECTED):
            return False
        if not self._matches(candidate, evidence, expected_value):
            return False
        key = (candidate.epoch, candidate.transaction_id, candidate.observation_id, purpose)
        if key in self.authorized_keys:
            raise RuntimeError("duplicate authorization")
        self.authorized_keys.add(key)
        return True

    @staticmethod
    def evidence_is_independent(evidence: Any) -> bool:
        return evidence.lineage == EXTERNAL_PROTECTED


class RecordAuthorizer:
    @staticmethod
    def authorize(record: MemoryRecord, receipt: Any) -> bool:
        return OutcomeMemory.record_matches_receipt(record, receipt)


class Recovery:
    def __init__(self) -> None:
        self.attempts = 0

    def _take_attempt(self) -> None:
        self.attempts += 1
        if self.attempts > RECOVERY_ATTEMPT_LIMIT:
            raise RuntimeError("recovery attempt bound exceeded")

    def state_candidate(self, evidence: Any, expected_value: int, wrong: bool = False) -> StateCandidate:
        self._take_attempt()
        return StateCandidate(
            epoch=evidence.epoch,
            transaction_id=evidence.transaction_id,
            observation_id=evidence.observation_id,
            source_identity=evidence.source_identity,
            value=(expected_value + 1) % 4 if wrong else expected_value,
            lineage=CANDIDATE_DERIVED,
            status=AuthorityState.RECOVERING,
        )

    def measurement(self, prediction: Prediction, receipt: Any) -> Measurement:
        self._take_attempt()
        # Recompute independently of Measure and EvidenceAuditor. Recovery can
        # propose a correction, but the auditor remains its authority gate.
        expected = (
            receipt.lineage == EXTERNAL_PROTECTED
            and prediction.epoch == receipt.epoch
            and prediction.transaction_id == receipt.transaction_id
            and prediction.pre_state == receipt.pre_state
            and prediction.action == receipt.action
            and prediction.next_state == receipt.next_state
            and prediction.consequence == receipt.consequence
        )
        return Measurement(receipt.epoch, receipt.transaction_id, receipt.observation_id, expected)

    def memory_record(self, receipt: Any) -> MemoryRecord:
        self._take_attempt()
        return MemoryRecord(
            epoch=receipt.epoch,
            transaction_id=receipt.transaction_id,
            pre_state=receipt.pre_state,
            action=receipt.action,
            observation_id=receipt.observation_id,
            next_state=receipt.next_state,
            consequence=receipt.consequence,
            measurement_matches=True,
            authorization=AuthorityState.AUTHORIZED,
        )


class BoundedTrace:
    def __init__(self) -> None:
        self.records: list[TraceRecord] = []
        self.max_observed = 0

    def append(self, record: TraceRecord) -> None:
        if len(self.records) == TRACE_LIMIT:
            self.records.pop(0)
        self.records.append(record)
        self.max_observed = max(self.max_observed, len(self.records))


def descendant_checker(candidate: StateCandidate, reference: StateCandidate) -> bool:
    """Deliberately invalid negative control: ignores lineage and provenance."""

    return candidate.value == reference.value


class BaseFramework:
    """Coordinator with explicit authorization boundaries and bounded state."""

    def __init__(self, environment: Any, epoch: int = 1) -> None:
        self.environment = environment
        self.epoch = epoch
        self.next_transaction_id = 1
        self.episode_steps = 0
        self.explorer = Explorer()
        self.map = MapModel(environment.state, epoch)
        self.measure = Measure()
        self.auditor = EvidenceAuditor()
        self.memory = OutcomeMemory()
        self.evidence = ProtectedEvidenceStore()
        self.state_authorizer = StateAuthorizer()
        self.record_authorizer = RecordAuthorizer()
        self.trace = BoundedTrace()
        self.continuation_authorized = True
        self.metrics = {
            "false_accepts": 0,
            "false_rejects": 0,
            "duplicate_authorizations": 0,
            "recovery_successes": 0,
            "recovery_rejections": 0,
            "provenance_rejections": 0,
            "lineage_rejections": 0,
            "descendant_false_confidence": 0,
            "memory_corruptions_detected": 0,
            "measurement_corruptions_detected": 0,
            "incumbents_retained": 0,
            "incumbents_quarantined": 0,
            "candidate_replacements": 0,
            "commits": 0,
            "safe_rejections": 0,
        }

    def start_epoch(self, epoch: int) -> None:
        if epoch == self.epoch:
            raise ValueError("epoch must change")
        self.epoch = epoch
        self.next_transaction_id = 1
        self.episode_steps = 0
        self.map = MapModel(self.environment.state, epoch)
        self.continuation_authorized = True

    def _trace(self, transaction_id: int, action: Optional[str], status: AuthorityState, detail: str, continued: bool) -> None:
        self.trace.append(TraceRecord(self.epoch, transaction_id, action or "NONE", status, detail, continued))

    def _reject(
        self,
        transaction_id: int,
        action: Optional[str],
        reason: str,
        *,
        executed: bool = False,
    ) -> TransactionResult:
        self.continuation_authorized = False
        self.metrics["safe_rejections"] += 1
        self._trace(transaction_id, action, AuthorityState.REJECTED, reason, False)
        return TransactionResult(transaction_id, action, executed, False, False, False, False, reason)

    def _paired_commit(self, receipt: Any, record: MemoryRecord) -> None:
        if len(self.memory.records) == MEMORY_LIMIT:
            oldest = self.memory.records.pop(0)
            evidence_oldest = self.evidence.receipts.pop(0)
            if (
                oldest.epoch,
                oldest.transaction_id,
                oldest.observation_id,
            ) != (
                evidence_oldest.epoch,
                evidence_oldest.transaction_id,
                evidence_oldest.observation_id,
            ):
                raise RuntimeError("paired Memory/evidence rotation lost identity")
            self.memory.evictions += 1
        self.evidence.append(receipt)
        self.memory.records.append(record)
        self.memory.max_observed = max(self.memory.max_observed, len(self.memory.records))

    def _audit_and_recover_memory(self, wrong_recovery: bool = False) -> bool:
        _, corrupt = self.memory.audit(self.evidence)
        if not corrupt:
            return True
        self.metrics["memory_corruptions_detected"] += len(corrupt)
        record = corrupt[0]
        receipt = self.evidence.find(record.epoch, record.transaction_id, record.observation_id)
        if receipt is None:
            return False
        recovery = Recovery()
        candidate = recovery.memory_record(receipt)
        if wrong_recovery:
            candidate = replace(candidate, consequence=candidate.consequence + 1)
        if not self.record_authorizer.authorize(candidate, receipt):
            self.metrics["recovery_rejections"] += 1
            return False
        self.memory.replace_quarantined(candidate)
        self.metrics["recovery_successes"] += 1
        return True

    def _recover_incumbent(self, snapshot: Any, wrong: bool = False) -> bool:
        recovery = Recovery()
        candidate = recovery.state_candidate(snapshot, snapshot.state, wrong=wrong)
        if not self.state_authorizer.authorize(candidate, snapshot, snapshot.state, "prestate-recovery"):
            self.metrics["recovery_rejections"] += 1
            return False
        self.map.commit(candidate.value, self.epoch)
        self.metrics["recovery_successes"] += 1
        return True

    def run_step(self, fault: Optional[dict[str, Any]] = None) -> TransactionResult:
        fault = fault or {}
        if not self.continuation_authorized:
            raise RuntimeError("episode continuation is not authorized")
        if self.episode_steps >= EPISODE_LIMIT:
            raise RuntimeError("episode length bound exceeded")

        transaction_id = self.next_transaction_id
        snapshot = self.environment.snapshot(self.epoch, transaction_id)

        if not self._audit_and_recover_memory(fault.get("wrong_memory_recovery", False)):
            return self._reject(transaction_id, None, "Memory recovery rejected")

        valid_records, _ = self.memory.audit(self.evidence)
        if self.map.current.state != snapshot.state or not self.map.current.valid:
            self.map.quarantine_incumbent()
            self.metrics["incumbents_quarantined"] += 1
            if not self._recover_incumbent(snapshot, fault.get("failed_recovery", False)):
                return self._reject(transaction_id, None, "invalid incumbent and recovery rejected")

        proposal = self.explorer.propose(
            self.map.current,
            valid_records,
            self.epoch,
            transaction_id,
            forced_action=fault.get("forced_action"),
        )
        if fault.get("proposal_epoch") is not None:
            proposal = replace(proposal, epoch=fault["proposal_epoch"])
        if not ActionAuthority.authorize(proposal, snapshot, self.map.current):
            self.metrics["provenance_rejections"] += 1
            return self._reject(transaction_id, proposal.action, "Explorer proposal rejected")

        prediction = self.map.predict(proposal.action, self.epoch, transaction_id)
        receipt = self.environment.step(proposal.action, self.epoch, transaction_id)

        measurement = self.measure.evaluate(prediction, receipt, fault.get("wrong_measure", False))
        if not self.auditor.verify(measurement, prediction, receipt):
            self.metrics["measurement_corruptions_detected"] += 1
            recovery = Recovery()
            corrected = recovery.measurement(prediction, receipt)
            if fault.get("wrong_measure_recovery", False):
                corrected = replace(corrected, matches=not corrected.matches)
            if not self.auditor.verify(corrected, prediction, receipt):
                self.metrics["recovery_rejections"] += 1
                return self._reject(
                    transaction_id,
                    proposal.action,
                    "Measure recovery rejected",
                    executed=True,
                )
            measurement = corrected
            self.metrics["recovery_successes"] += 1

        candidate = StateCandidate(
            epoch=self.epoch,
            transaction_id=transaction_id,
            observation_id=receipt.observation_id,
            source_identity=receipt.source_identity,
            value=prediction.next_state,
        )
        if fault.get("candidate_value") is not None:
            candidate = replace(candidate, value=fault["candidate_value"])
        if fault.get("candidate_epoch") is not None:
            candidate = replace(candidate, epoch=fault["candidate_epoch"])
        if fault.get("candidate_transaction") is not None:
            candidate = replace(candidate, transaction_id=fault["candidate_transaction"])

        if fault.get("shared_descendant", False):
            corrupt = replace(candidate, value=(receipt.next_state + 1) % 4)
            reference = replace(corrupt, lineage=SHARED_ANCESTOR)
            if descendant_checker(corrupt, reference):
                self.metrics["descendant_false_confidence"] += 1
            if not self.state_authorizer.evidence_is_independent(reference):
                self.metrics["lineage_rejections"] += 1
            return self._reject(
                transaction_id,
                proposal.action,
                "shared-descendant evidence rejected",
                executed=True,
            )

        incumbent = StateCandidate(
            epoch=self.epoch,
            transaction_id=transaction_id,
            observation_id=receipt.observation_id,
            source_identity=receipt.source_identity,
            value=self.map.current.state,
        )
        incumbent_valid = incumbent.value == receipt.next_state
        candidate_valid = self.state_authorizer._matches(candidate, receipt, receipt.next_state)

        selected: Optional[StateCandidate] = None
        selected_already_authorized = False
        incumbent_retained = False
        recovery_authorized = False

        if incumbent_valid:
            selected = incumbent
            incumbent_retained = True
            self.metrics["incumbents_retained"] += 1
        elif candidate_valid:
            selected = candidate
            self.metrics["candidate_replacements"] += 1
        else:
            self.map.quarantine_incumbent()
            self.metrics["incumbents_quarantined"] += 1
            if candidate.epoch != receipt.epoch or candidate.transaction_id != receipt.transaction_id:
                self.metrics["provenance_rejections"] += 1
            recovery = Recovery()
            recovery_candidate = recovery.state_candidate(
                receipt,
                receipt.next_state,
                wrong=fault.get("failed_recovery", False),
            )
            if self.state_authorizer.authorize(
                recovery_candidate, receipt, receipt.next_state, "state-recovery"
            ):
                selected = recovery_candidate
                selected_already_authorized = True
                recovery_authorized = True
                self.metrics["recovery_successes"] += 1
            else:
                self.metrics["recovery_rejections"] += 1
                return self._reject(
                    transaction_id,
                    proposal.action,
                    "state recovery rejected",
                    executed=True,
                )

        purpose = "incumbent" if incumbent_retained else "state-update"
        authorized = selected_already_authorized
        if not selected_already_authorized:
            try:
                authorized = self.state_authorizer.authorize(
                    selected, receipt, receipt.next_state, purpose
                )
            except RuntimeError:
                self.metrics["duplicate_authorizations"] += 1
                raise
        if not authorized:
            self.metrics["false_rejects"] += 1
            return self._reject(
                transaction_id,
                proposal.action,
                "state candidate rejected",
                executed=True,
            )

        record = MemoryRecord(
            epoch=receipt.epoch,
            transaction_id=receipt.transaction_id,
            pre_state=receipt.pre_state,
            action=receipt.action,
            observation_id=receipt.observation_id,
            next_state=receipt.next_state,
            consequence=receipt.consequence,
            measurement_matches=measurement.matches,
            authorization=AuthorityState.AUTHORIZED,
        )
        if not self.record_authorizer.authorize(record, receipt):
            self.metrics["false_rejects"] += 1
            return self._reject(
                transaction_id,
                proposal.action,
                "Memory record rejected",
                executed=True,
            )
        # Both proposed commits have now passed their separate gates. Apply
        # them together so a rejected Memory record cannot leave a Map-only
        # commit behind.
        self.map.commit(selected.value, self.epoch)
        self._paired_commit(receipt, record)

        self.metrics["commits"] += 1
        self.episode_steps += 1
        self.next_transaction_id += 1
        self.continuation_authorized = True
        self._trace(transaction_id, proposal.action, AuthorityState.AUTHORIZED, "transaction committed", True)
        return TransactionResult(
            transaction_id,
            proposal.action,
            True,
            True,
            True,
            incumbent_retained,
            recovery_authorized,
            "authorized",
        )

    def assert_bounds(self) -> None:
        if len(self.memory.records) > MEMORY_LIMIT:
            raise AssertionError("Memory bound exceeded")
        if len(self.evidence.receipts) > MEMORY_LIMIT:
            raise AssertionError("evidence bound exceeded")
        if len(self.memory.quarantine) > 1 or len(self.map.quarantine) > 1:
            raise AssertionError("quarantine bound exceeded")
        if len(self.trace.records) > TRACE_LIMIT or self.episode_steps > EPISODE_LIMIT:
            raise AssertionError("trace or episode bound exceeded")
