"""Bounded v1 framework with two registered observation channels."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Optional

from experiments.base_framework_v0.framework import (
    ACTION_ORDER,
    AuthorityState as V0Authority,
    Explorer,
    MapModel,
    Measurement,
    Prediction,
)
from experiments.base_framework_v1.types import (
    EXTERNAL_OBSERVATION,
    OBSERVATION_A,
    OBSERVATION_B,
    ObservationRequest,
    SourceReceipt,
)


MEMORY_LIMIT = 8
PAIR_LIMIT = 8
TRACE_LIMIT = 24
EPISODE_LIMIT = 12
EPOCH_LIMIT = 2
REOBSERVATION_LIMIT = 1
RECOVERY_LIMIT = 1
AUTHORIZATION_LIMIT = 24


class CrossAuthorityState(str, Enum):
    PROPOSED = "PROPOSED"
    OBSERVED_PARTIAL = "OBSERVED_PARTIAL"
    OBSERVED_PAIRED = "OBSERVED_PAIRED"
    DISAGREEMENT = "DISAGREEMENT"
    REOBSERVING = "REOBSERVING"
    MEASURED = "MEASURED"
    QUARANTINED = "QUARANTINED"
    RECOVERING = "RECOVERING"
    AUTHORIZED = "AUTHORIZED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class PairDecision:
    epoch: int
    transaction_id: int
    pair_decision_id: int
    channel_sequence: int
    pre_state: int
    action: str
    next_state: int
    consequence: int
    observation_a_id: int
    observation_b_id: int
    source_a: str
    source_b: str
    domain_a: str
    domain_b: str
    lineage_a: str
    lineage_b: str
    measurement_matches: Optional[bool] = None


@dataclass(frozen=True)
class CrossMemoryRecord:
    epoch: int
    transaction_id: int
    pre_state: int
    action: str
    pair_decision_id: int
    observation_a_id: int
    observation_b_id: int
    source_pair: tuple[str, str]
    next_state: int
    consequence: int
    measurement_matches: bool
    authorization: V0Authority


@dataclass(frozen=True)
class StateCandidate:
    epoch: int
    transaction_id: int
    pair_decision_id: int
    value: int
    status: CrossAuthorityState = CrossAuthorityState.PROPOSED


@dataclass
class PendingTransaction:
    epoch: int
    transaction_id: int
    action: str
    proposal_pre_state: int
    map_version: int
    prediction: Prediction
    channel_sequence: int = 0
    reobservations: int = 0
    receipts: dict[str, SourceReceipt] | None = None
    status: CrossAuthorityState = CrossAuthorityState.PROPOSED

    def __post_init__(self) -> None:
        if self.receipts is None:
            self.receipts = {}


@dataclass(frozen=True)
class StepResult:
    transaction_id: int
    status: CrossAuthorityState
    action: Optional[str]
    executed: bool
    committed: bool
    continued: bool
    needs_reobservation: bool
    incumbent_retained: bool
    recovery_authorized: bool
    reason: str


@dataclass(frozen=True)
class TraceRecord:
    epoch: int
    transaction_id: int
    channel_sequence: int
    status: CrossAuthorityState
    reason: str


class CrossSourceAuthorizer:
    """Validates registered ports, provenance, structure, and agreement."""

    @staticmethod
    def authorize(
        pending: PendingTransaction, receipt_a: SourceReceipt, receipt_b: SourceReceipt
    ) -> tuple[bool, str]:
        if (
            receipt_a.source_id != "SOURCE_A"
            or receipt_b.source_id != "SOURCE_B"
        ):
            return False, "source_identity"
        expected = (pending.epoch, pending.transaction_id, pending.channel_sequence, pending.action)
        if (
            (receipt_a.epoch, receipt_a.transaction_id, receipt_a.channel_sequence, receipt_a.action) != expected
            or (receipt_b.epoch, receipt_b.transaction_id, receipt_b.channel_sequence, receipt_b.action) != expected
            or receipt_a.pre_state != receipt_b.pre_state
        ):
            return False, "provenance"
        if receipt_a.observation_id == receipt_b.observation_id:
            return False, "source_identity"
        if (
            receipt_a.lineage_class != EXTERNAL_OBSERVATION
            or receipt_b.lineage_class != EXTERNAL_OBSERVATION
            or receipt_a.fault_domain != OBSERVATION_A
            or receipt_b.fault_domain != OBSERVATION_B
            or receipt_a.fault_domain == receipt_b.fault_domain
        ):
            return False, "independence"
        if (
            receipt_a.observed_next_state != receipt_b.observed_next_state
            or receipt_a.observed_consequence != receipt_b.observed_consequence
        ):
            return False, "disagreement"
        return True, "authorized_pair"


class MeasureAuditor:
    @staticmethod
    def expected(prediction: Prediction, decision: PairDecision) -> bool:
        return (
            prediction.epoch == decision.epoch
            and prediction.transaction_id == decision.transaction_id
            and prediction.pre_state == decision.pre_state
            and prediction.action == decision.action
            and prediction.next_state == decision.next_state
            and prediction.consequence == decision.consequence
        )

    def verify(self, measurement: Measurement, prediction: Prediction, decision: PairDecision) -> bool:
        return (
            measurement.epoch == decision.epoch
            and measurement.transaction_id == decision.transaction_id
            and measurement.observation_id == decision.pair_decision_id
            and measurement.matches == self.expected(prediction, decision)
        )


class CrossSourceStateAuthorizer:
    def __init__(self) -> None:
        self.authorized: set[tuple[int, int, int]] = set()

    def authorize(self, candidate: StateCandidate, decision: PairDecision) -> bool:
        if (
            candidate.epoch != decision.epoch
            or candidate.transaction_id != decision.transaction_id
            or candidate.pair_decision_id != decision.pair_decision_id
            or candidate.value != decision.next_state
        ):
            return False
        key = (candidate.epoch, candidate.transaction_id, candidate.pair_decision_id)
        if key in self.authorized:
            raise RuntimeError("duplicate authorization")
        if len(self.authorized) >= AUTHORIZATION_LIMIT:
            raise RuntimeError("authorization identity bound exceeded")
        self.authorized.add(key)
        return True


class PairStore:
    def __init__(self) -> None:
        self.decisions: list[PairDecision] = []
        self.max_observed = 0

    def find(self, epoch: int, transaction_id: int, pair_decision_id: int) -> Optional[PairDecision]:
        for decision in self.decisions:
            if (decision.epoch, decision.transaction_id, decision.pair_decision_id) == (
                epoch, transaction_id, pair_decision_id
            ):
                return decision
        return None


class CrossMemory:
    def __init__(self) -> None:
        self.records: list[CrossMemoryRecord] = []
        self.quarantine: list[CrossMemoryRecord] = []
        self.max_observed = 0
        self.evictions = 0

    @staticmethod
    def matches(record: CrossMemoryRecord, decision: Optional[PairDecision]) -> bool:
        return (
            decision is not None
            and record.epoch == decision.epoch
            and record.transaction_id == decision.transaction_id
            and record.pair_decision_id == decision.pair_decision_id
            and record.pre_state == decision.pre_state
            and record.action == decision.action
            and record.observation_a_id == decision.observation_a_id
            and record.observation_b_id == decision.observation_b_id
            and record.source_pair == (decision.source_a, decision.source_b)
            and record.next_state == decision.next_state
            and record.consequence == decision.consequence
            and record.measurement_matches == decision.measurement_matches
            and record.authorization == V0Authority.AUTHORIZED
        )

    def audit(self, store: PairStore) -> tuple[list[CrossMemoryRecord], list[CrossMemoryRecord]]:
        valid, corrupt = [], []
        for record in self.records:
            decision = store.find(record.epoch, record.transaction_id, record.pair_decision_id)
            (valid if self.matches(record, decision) else corrupt).append(record)
        if corrupt:
            if len(corrupt) > 1 or self.quarantine:
                raise RuntimeError("Memory quarantine bound exceeded")
            self.records = valid
            self.quarantine.extend(corrupt)
        return valid, corrupt

    def corrupt_consequence(self, transaction_id: int) -> None:
        for index, record in enumerate(self.records):
            if record.transaction_id == transaction_id:
                self.records[index] = replace(record, consequence=record.consequence + 5)
                return
        raise KeyError("Memory record not found")


class Recovery:
    def __init__(self) -> None:
        self.attempts = 0

    def _take(self) -> None:
        self.attempts += 1
        if self.attempts > RECOVERY_LIMIT:
            raise RuntimeError("recovery attempt bound exceeded")

    def state_candidate(self, decision: PairDecision, wrong: bool = False) -> StateCandidate:
        self._take()
        value = (decision.next_state + 1) % 4 if wrong else decision.next_state
        return StateCandidate(
            decision.epoch, decision.transaction_id, decision.pair_decision_id,
            value, CrossAuthorityState.RECOVERING,
        )

    def measurement(self, prediction: Prediction, decision: PairDecision) -> Measurement:
        self._take()
        matches = (
            prediction.epoch == decision.epoch
            and prediction.transaction_id == decision.transaction_id
            and prediction.pre_state == decision.pre_state
            and prediction.action == decision.action
            and prediction.next_state == decision.next_state
            and prediction.consequence == decision.consequence
        )
        return Measurement(decision.epoch, decision.transaction_id, decision.pair_decision_id, matches)

    def memory_record(self, decision: PairDecision) -> CrossMemoryRecord:
        self._take()
        return record_from_decision(decision)


def record_from_decision(decision: PairDecision) -> CrossMemoryRecord:
    if decision.measurement_matches is None:
        raise ValueError("pair decision lacks audited measurement")
    return CrossMemoryRecord(
        decision.epoch, decision.transaction_id, decision.pre_state, decision.action,
        decision.pair_decision_id, decision.observation_a_id, decision.observation_b_id,
        (decision.source_a, decision.source_b), decision.next_state, decision.consequence,
        decision.measurement_matches, V0Authority.AUTHORIZED,
    )


def naive_pair_agreement(a: SourceReceipt, b: SourceReceipt) -> bool:
    return (
        a.observed_next_state == b.observed_next_state
        and a.observed_consequence == b.observed_consequence
    )


class CrossSourceFramework:
    def __init__(self, initial_state: int = 0, epoch: int = 1) -> None:
        self.epoch = epoch
        self.epochs_started = 1
        self.next_transaction_id = 1
        self.episode_steps = 0
        self.explorer = Explorer()
        self.map = MapModel(initial_state, epoch)
        self.memory = CrossMemory()
        self.pairs = PairStore()
        self.pair_authorizer = CrossSourceAuthorizer()
        self.measure_auditor = MeasureAuditor()
        self.state_authorizer = CrossSourceStateAuthorizer()
        self.pending: Optional[PendingTransaction] = None
        self._requires_package = False  # enabled only by the v2 coordinator
        self._package_grant = None
        self.continuation_authorized = True
        self.trace: list[TraceRecord] = []
        self.max_trace = 0
        self.max_pending_receipts = 0
        self.metrics = {key: 0 for key in (
            "clean_authorizations", "false_accepts", "false_rejects",
            "duplicate_authorizations", "single_source_disagreements",
            "reobservations", "successful_reobservation_recoveries",
            "persistent_disagreement_rejections", "provenance_rejections",
            "source_identity_rejections", "derived_source_rejections",
            "shared_ancestor_rejections", "invalid_recovery_rejections",
            "measurement_corruptions_detected", "memory_corruptions_detected",
            "memory_behavior_changes", "common_mode_pair_false_confidence",
            "common_mode_false_accepts", "commits", "safe_rejections",
            "incumbents_retained", "incumbents_quarantined", "candidate_replacements",
        )}

    def _trace(self, status: CrossAuthorityState, reason: str) -> None:
        transaction_id = self.pending.transaction_id if self.pending else self.next_transaction_id
        sequence = self.pending.channel_sequence if self.pending else 0
        if len(self.trace) == TRACE_LIMIT:
            self.trace.pop(0)
        self.trace.append(TraceRecord(self.epoch, transaction_id, sequence, status, reason))
        self.max_trace = max(self.max_trace, len(self.trace))

    def start_epoch(self, epoch: int) -> None:
        if epoch == self.epoch:
            raise ValueError("epoch must change")
        if self.epochs_started >= EPOCH_LIMIT:
            raise RuntimeError("epoch bound exceeded")
        if self.pending is not None:
            raise RuntimeError("cannot change epoch with pending transaction")
        self.epoch = epoch
        self.epochs_started += 1
        self.next_transaction_id = 1
        self.episode_steps = 0
        self.map = MapModel(self.map.current.state, epoch)
        self.state_authorizer = CrossSourceStateAuthorizer()
        self.continuation_authorized = True

    def _reject(self, reason: str, executed: bool) -> StepResult:
        transaction_id = self.pending.transaction_id if self.pending else self.next_transaction_id
        action = self.pending.action if self.pending else None
        self.continuation_authorized = False
        self.metrics["safe_rejections"] += 1
        self._trace(CrossAuthorityState.REJECTED, reason)
        self.pending = None
        return StepResult(
            transaction_id, CrossAuthorityState.REJECTED, action, executed,
            False, False, False, False, False, reason,
        )

    def _recover_memory(self, wrong: bool = False) -> bool:
        original = list(self.memory.records)
        _, corrupt = self.memory.audit(self.pairs)
        if not corrupt:
            return True
        self.metrics["memory_corruptions_detected"] += len(corrupt)
        old = corrupt[0]
        identity = (old.epoch, old.transaction_id, old.pair_decision_id)
        slots = [i for i, record in enumerate(original)
                 if (record.epoch, record.transaction_id, record.pair_decision_id) == identity]
        if len(slots) != 1 or len(original) != len(self.pairs.decisions):
            return False
        paired = self.pairs.decisions[slots[0]]
        if (paired.epoch, paired.transaction_id, paired.pair_decision_id) != identity:
            return False
        decision = self.pairs.find(old.epoch, old.transaction_id, old.pair_decision_id)
        if decision is None:
            return False
        candidate = Recovery().memory_record(decision)
        if wrong:
            candidate = replace(candidate, consequence=candidate.consequence + 1)
        if not self.memory.matches(candidate, decision):
            self.metrics["invalid_recovery_rejections"] += 1
            return False
        original[slots[0]] = candidate
        self.memory.records = original
        self.memory.quarantine.clear()
        return True

    def begin_step(
        self, forced_action: Optional[str] = None, wrong_memory_recovery: bool = False
    ) -> PendingTransaction | StepResult:
        if not self.continuation_authorized or self.pending is not None:
            raise RuntimeError("continuation unavailable or transaction already pending")
        if self.episode_steps >= EPISODE_LIMIT:
            raise RuntimeError("episode bound exceeded")
        if not self._recover_memory(wrong_memory_recovery):
            return self._reject("Memory recovery rejected", executed=False)
        valid, _ = self.memory.audit(self.pairs)
        transaction_id = self.next_transaction_id
        action = forced_action if forced_action is not None else self.explorer.choose(self.map.current.state, valid)
        if action not in ACTION_ORDER:
            return self._reject("Explorer proposal rejected", executed=False)
        prediction = self.map.predict(action, self.epoch, transaction_id)
        self.pending = PendingTransaction(
            self.epoch, transaction_id, action, self.map.current.state,
            self.map.current.version, prediction,
        )
        self._trace(CrossAuthorityState.PROPOSED, "action authorized for execution")
        return self.pending

    def observation_request(self, true_pre_state: int) -> ObservationRequest:
        if self.pending is None:
            raise RuntimeError("no pending transaction")
        return ObservationRequest(
            self.pending.epoch, self.pending.transaction_id, true_pre_state,
            self.pending.action, self.pending.channel_sequence,
        )

    def _dispute(self, reason: str) -> StepResult:
        if self.pending is None:
            raise RuntimeError("no pending transaction")
        if reason == "provenance":
            self.metrics["provenance_rejections"] += 1
        elif reason == "source_identity":
            self.metrics["source_identity_rejections"] += 1
        elif reason == "derived_source":
            self.metrics["derived_source_rejections"] += 1
        elif reason == "shared_ancestor":
            self.metrics["shared_ancestor_rejections"] += 1
        else:
            self.metrics["single_source_disagreements"] += 1
        self._trace(CrossAuthorityState.DISAGREEMENT, reason)
        if self.pending.reobservations < REOBSERVATION_LIMIT:
            self.pending.reobservations += 1
            self.pending.channel_sequence += 1
            self.pending.receipts = {}
            self.pending.status = CrossAuthorityState.REOBSERVING
            self.metrics["reobservations"] += 1
            self._trace(CrossAuthorityState.REOBSERVING, "one bounded re-observation requested")
            return StepResult(
                self.pending.transaction_id, CrossAuthorityState.REOBSERVING,
                self.pending.action, True, False, False, True, False, False, reason,
            )
        self.metrics["persistent_disagreement_rejections"] += 1
        return self._reject(f"persistent evidence failure: {reason}", executed=True)

    def submit_receipt(
        self,
        port: str,
        receipt: SourceReceipt,
        *,
        wrong_measure: bool = False,
        wrong_measure_recovery: bool = False,
        candidate_value: Optional[int] = None,
        failed_recovery: bool = False,
        common_mode: bool = False,
    ) -> StepResult:
        if self._requires_package and not self._has_package_grant():
            return self._reject("mandatory package authorization required", executed=True)
        if self.pending is None:
            raise RuntimeError("no pending transaction")
        if port not in ("A", "B"):
            raise ValueError("unknown registered port")
        if port in self.pending.receipts:
            return self._dispute("duplicate_receipt")
        self.pending.receipts[port] = receipt
        self.max_pending_receipts = max(self.max_pending_receipts, len(self.pending.receipts))
        if len(self.pending.receipts) == 1:
            self.pending.status = CrossAuthorityState.OBSERVED_PARTIAL
            self._trace(CrossAuthorityState.OBSERVED_PARTIAL, f"receipt {port} staged; no commit")
            return StepResult(
                self.pending.transaction_id, CrossAuthorityState.OBSERVED_PARTIAL,
                self.pending.action, True, False, False, False, False, False,
                "waiting for registered second source",
            )

        a, b = self.pending.receipts["A"], self.pending.receipts["B"]
        pair_ok, reason = self.pair_authorizer.authorize(self.pending, a, b)
        if not pair_ok:
            if reason == "independence":
                if b.lineage_class == "DERIVED_SOURCE":
                    reason = "derived_source"
                else:
                    reason = "shared_ancestor"
            return self._dispute(reason)

        if common_mode:
            self.metrics["common_mode_pair_false_confidence"] += 1
        self.pending.status = CrossAuthorityState.OBSERVED_PAIRED
        pair_id = (
            (self.pending.epoch << 32)
            | (self.pending.transaction_id << 8)
            | self.pending.channel_sequence
        )
        decision = PairDecision(
            self.pending.epoch, self.pending.transaction_id, pair_id,
            self.pending.channel_sequence, a.pre_state, a.action,
            a.observed_next_state, a.observed_consequence,
            a.observation_id, b.observation_id, a.source_id, b.source_id,
            a.fault_domain, b.fault_domain, a.lineage_class, b.lineage_class,
        )
        return self._complete_pair(
            decision,
            wrong_measure=wrong_measure,
            wrong_measure_recovery=wrong_measure_recovery,
            candidate_value=candidate_value,
            failed_recovery=failed_recovery,
        )

    def _has_package_grant(self) -> bool:
        pending = self.pending
        return (
            pending is not None and self._package_grant is not None
            and self._package_grant[:3] == (
                pending.epoch, pending.transaction_id, pending.channel_sequence
            )
        )

    def _complete_pair(
        self,
        decision: PairDecision,
        *,
        wrong_measure: bool,
        wrong_measure_recovery: bool,
        candidate_value: Optional[int],
        failed_recovery: bool,
    ) -> StepResult:
        if self._requires_package:
            if not self._has_package_grant() or self._package_grant[3:] != (
                decision.observation_a_id, decision.observation_b_id
            ):
                return self._reject("mandatory package authorization required", executed=True)
        if self.pending is None:
            raise RuntimeError("no pending transaction")
        expected = self.measure_auditor.expected(self.pending.prediction, decision)
        measurement = Measurement(
            decision.epoch, decision.transaction_id, decision.pair_decision_id,
            not expected if wrong_measure else expected,
        )
        if not self.measure_auditor.verify(measurement, self.pending.prediction, decision):
            self.metrics["measurement_corruptions_detected"] += 1
            corrected = Recovery().measurement(self.pending.prediction, decision)
            if wrong_measure_recovery:
                corrected = replace(corrected, matches=not corrected.matches)
            if not self.measure_auditor.verify(corrected, self.pending.prediction, decision):
                self.metrics["invalid_recovery_rejections"] += 1
                return self._reject("Measure recovery rejected", executed=True)
            measurement = corrected

        decision = replace(decision, measurement_matches=measurement.matches)
        candidate = StateCandidate(
            decision.epoch, decision.transaction_id, decision.pair_decision_id,
            decision.next_state if candidate_value is None else candidate_value,
        )
        incumbent_valid = self.map.current.state == decision.next_state
        incumbent_retained = False
        recovery_authorized = False

        if incumbent_valid:
            selected = StateCandidate(
                decision.epoch, decision.transaction_id, decision.pair_decision_id,
                self.map.current.state,
            )
            incumbent_retained = True
            self.metrics["incumbents_retained"] += 1
        elif measurement.matches and candidate.value == decision.next_state:
            selected = candidate
            self.metrics["candidate_replacements"] += 1
        else:
            self.map.quarantine_incumbent()
            self.metrics["incumbents_quarantined"] += 1
            selected = Recovery().state_candidate(decision, wrong=failed_recovery)
            recovery_authorized = True

        try:
            state_ok = self.state_authorizer.authorize(selected, decision)
        except RuntimeError:
            self.metrics["duplicate_authorizations"] += 1
            raise
        if not state_ok:
            self.metrics["invalid_recovery_rejections"] += 1
            return self._reject("state recovery/candidate rejected", executed=True)

        record = record_from_decision(decision)
        if not self.memory.matches(record, decision):
            self.metrics["false_rejects"] += 1
            return self._reject("Memory record rejected", executed=True)

        if len(self.memory.records) == MEMORY_LIMIT:
            oldest_record = self.memory.records.pop(0)
            oldest_pair = self.pairs.decisions.pop(0)
            if (oldest_record.epoch, oldest_record.transaction_id, oldest_record.pair_decision_id) != (
                oldest_pair.epoch, oldest_pair.transaction_id, oldest_pair.pair_decision_id
            ):
                raise RuntimeError("paired evidence rotation lost identity")
            self.memory.evictions += 1
        self.map.commit(selected.value, self.epoch)
        self.memory.records.append(record)
        self.pairs.decisions.append(decision)
        self.memory.max_observed = max(self.memory.max_observed, len(self.memory.records))
        self.pairs.max_observed = max(self.pairs.max_observed, len(self.pairs.decisions))
        if self.pending.reobservations:
            self.metrics["successful_reobservation_recoveries"] += 1
        if recovery_authorized:
            self.metrics["candidate_replacements"] += 1
        self.metrics["commits"] += 1
        self.episode_steps += 1
        self.next_transaction_id += 1
        transaction_id, action = self.pending.transaction_id, self.pending.action
        self._trace(CrossAuthorityState.AUTHORIZED, "paired transaction committed")
        self.pending = None
        self.continuation_authorized = True
        return StepResult(
            transaction_id, CrossAuthorityState.AUTHORIZED, action, True, True,
            True, False, incumbent_retained, recovery_authorized, "authorized",
        )

    def assert_bounds(self) -> None:
        if len(self.memory.records) > MEMORY_LIMIT or len(self.pairs.decisions) > PAIR_LIMIT:
            raise AssertionError("Memory/pair bound exceeded")
        if len(self.memory.quarantine) > 1 or len(self.map.quarantine) > 1:
            raise AssertionError("quarantine bound exceeded")
        if self.pending and (len(self.pending.receipts) > 2 or self.pending.reobservations > 1):
            raise AssertionError("receipt/re-observation bound exceeded")
        if len(self.trace) > TRACE_LIMIT or self.episode_steps > EPISODE_LIMIT:
            raise AssertionError("trace/episode bound exceeded")
        if len(self.state_authorizer.authorized) > AUTHORIZATION_LIMIT:
            raise AssertionError("authorization bound exceeded")
        if self.epochs_started > EPOCH_LIMIT:
            raise AssertionError("epoch bound exceeded")
