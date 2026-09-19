"""Value-only Recovery hook; historical modules and authority are unchanged.

The copied _complete_pair body has exactly one expression substitution, checked
against the historical method by the campaign. All other core methods and the
entire receipt-bound staged publication implementation are inherited.
"""
from dataclasses import dataclass, replace
from typing import Optional, Protocol

from experiments.base_framework_v1.framework import (
    CrossSourceFramework, Recovery, PairDecision, StateCandidate, StepResult,
    Measurement, CrossAuthorityState, MEMORY_LIMIT, record_from_decision,
)
from experiments.realized_event_grounding_v0.framework import (
    RealizedEventFramework, SharedReceiptPairGate,
)


@dataclass(frozen=True)
class DecisionContext:
    epoch: int
    transaction_id: int
    pair_decision_id: int
    pre_state: int
    action: str
    next_state: int
    consequence: int
    measurement_matches: bool


class StateRecoveryProposalSource(Protocol):
    def propose(self, context: DecisionContext) -> int:
        """Supply only a replacement state; this conveys no authority."""
        ...


class RecoveryOpportunity:
    """Trusted owner of one native attempt, never passed to the proposer."""
    def __init__(self):
        self._native = Recovery()

    def candidate(self, decision: PairDecision, source=None, *, wrong=False):
        # Native limit is consumed BEFORE any external callback. Repeated calls
        # on this owner fail in native code, without a second callback.
        native = self._native.state_candidate(decision, wrong=wrong)
        if source is None:
            return native
        context = DecisionContext(*(getattr(decision, field)
                                    for field in DecisionContext.__dataclass_fields__))
        try:
            value = source.propose(context)
        except Exception as exc:
            # The existing staged wrapper catches ValueError. Never fall back
            # to the receipt-derived native value after a source failure.
            raise ValueError("state recovery proposer failed") from exc
        if type(value) is not int or value not in range(4):
            raise ValueError("state recovery value must be an exact int in [0, 3]")
        return replace(native, value=value)


class RecoveryInterfaceCore(CrossSourceFramework):
    def __init__(self, initial_state=0, epoch=1, proposal_source=None):
        super().__init__(initial_state, epoch)
        self._state_recovery_source = proposal_source

    def _state_recovery_candidate(self, decision, *, wrong=False):
        opportunity = RecoveryOpportunity()
        return opportunity.candidate(decision, self._state_recovery_source, wrong=wrong)

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
        prediction = self._prediction_at_begin
        if prediction is None:
            raise RuntimeError("missing pre-outcome prediction")
        expected = self.measure_auditor.expected(prediction, decision)
        measurement = Measurement(
            decision.epoch, decision.transaction_id, decision.pair_decision_id,
            not expected if wrong_measure else expected,
        )
        if not self.measure_auditor.verify(measurement, prediction, decision):
            self.metrics["measurement_corruptions_detected"] += 1
            corrected = Recovery().measurement(prediction, decision)
            if wrong_measure_recovery:
                corrected = replace(corrected, matches=not corrected.matches)
            if not self.measure_auditor.verify(corrected, prediction, decision):
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
            selected = self._state_recovery_candidate(decision, wrong=failed_recovery)
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


class StateRecoveryFramework(RealizedEventFramework):
    """Same authentic-receipt wrapper with the separate core installed at init."""
    def __init__(self, receipt_port, initial_state=1, epoch=1001, proposal_source=None):
        super().__init__(receipt_port, initial_state, epoch)
        self.inner = RecoveryInterfaceCore(initial_state, epoch, proposal_source)
        self.inner._requires_package = True
        self.inner.pair_authorizer = SharedReceiptPairGate()
