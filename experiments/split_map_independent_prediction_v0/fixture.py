"""Exact retained histories, detached split prediction, and grounded execution."""
from copy import deepcopy
from dataclasses import asdict
from unittest.mock import patch

from experiments.cross_episode_initialization_boundary_v1.boundary import EpisodeController, EpisodePlan
from experiments.cross_episode_stale_memory_feasibility_v0.campaign import execute, audit, snap, plain
from experiments.cross_episode_initialization_boundary_v1.campaign import boundary_observer
from experiments.map_guided_explorer_interface_v0.interface import AuthenticatedReader
from experiments.realized_event_grounding_v0.framework import evidence
from experiments.base_framework_v0.framework import MapModel
from .protocol import CAMPAIGN, WORLDS, ROLES, control, body, request_hash, matched


GUARD = "experiments.base_framework_v1.hidden_oracle.TrueWorldOracle.execute"


class Context:
    def __init__(self, descriptor):
        self.d = deepcopy(descriptor)
        self.w = WORLDS[descriptor["world"]]
        self.control = control(descriptor)
        self.c = EpisodeController(f'{CAMPAIGN}:c{descriptor["index"]:02d}',
            EpisodePlan(initial_state=self.w["state"]))
        self.authentic = {}
        self.executions = {}
        self.initial = snap(self.c)
        assert self.initial["world_state"] == self.w["state"]
        assert self.initial["epoch"] == 1001 and not self.initial["protected"]["memory"]
        self.setup = [execute(self.c, action, self.authentic, self.executions)
                      for action in descriptor["setup_actions"]]
        self.reader = AuthenticatedReader(self.c, self.authentic, self.executions)
        self.capture = self.reader.capture(descriptor["mapping"])
        self.payload = self.capture["map_inputs"][descriptor["target_action"]]
        # All request bodies are completed before any response can exist.
        self.requests = {role: body(role, descriptor, self.payload) for role in ROLES}
        self.before = snap(self.c)
        self.audit_before()
        matched(self.requests, descriptor)

    def audit_before(self):
        c = self.c
        descriptor = self.d
        state = snap(c)
        assert state == self.before
        assert state["world_state"] == state["protected"]["map"]["state"] == self.w["state"]
        assert state["epoch"] == 1001
        assert state["world_executions"] == state["source_event_count"] == len(state["protected"]["memory"]) == 5
        assert state["next_transaction_id"] == 6 and state["root_receipt"] is None and state["pending"] is None
        assert self.reader.capture(descriptor["mapping"]) == self.capture
        assert type(c._active.framework.inner.map) is MapModel
        assert self.payload["state"] == descriptor["state"]
        assert self.payload["target_action"] == descriptor["target_alias"]
        assert self.payload["VERIFIED_CHRONOLOGICAL_HISTORY"] == descriptor["authenticated_target_history"]
        assert request_hash(self.requests["J"]) == descriptor["historical_request_sha256"]
        assert len(self.authentic) == 5
        return audit(c, self.authentic, self.executions)

    def record(self):
        return plain(dict(descriptor=self.d, initial=self.initial, setup=self.setup,
            before=self.before, capture=self.capture,
            request_sha256={role: request_hash(request) for role, request in self.requests.items()},
            provenance=self.audit_before()))

    def grounded_step(self, journal=None):
        """No probe or reconciled value enters this method or the framework."""
        self.audit_before()
        c = self.c
        def log(status, value):
            if journal is not None:
                journal.append(status, plain(value))
        with patch(GUARD, side_effect=AssertionError("future event must not execute before control latch")):
            pending = c.begin_step(self.w["action"])
        prediction = asdict(pending.prediction)
        latched = snap(c)
        assert prediction == latched["prediction_at_begin"]
        assert {key: prediction[key] for key in self.control} == self.control
        assert latched["world_executions"] == 5 and latched["root_receipt"] is None
        assert latched["protected"] == self.before["protected"]
        log("CONTROL_PREDICTION_LATCHED", dict(prediction=prediction, non_model=True, snapshot=latched))
        log("EXECUTION_INTENT_RECORDED", dict(epoch=pending.epoch,
            transaction_id=pending.transaction_id, action=pending.action))
        receipt = c.execute_pending()
        original = asdict(receipt)
        actual = asdict(c._active.world.last_actual)
        assert c._source.reader().current() is receipt and receipt.identity() not in self.authentic
        assert receipt.transaction_id == receipt.event_id == 6
        assert receipt.binding()[:6] == tuple(actual[key] for key in
            ("epoch", "transaction_id", "pre_state", "action", "next_state", "consequence"))
        self.authentic[receipt.identity()] = receipt
        self.executions[receipt.identity()] = actual
        log("AUTHENTIC_EXECUTION_RECEIPT", dict(actual=actual, receipt=original,
            original_receipt_object=True))
        with boundary_observer() as effects:
            result = c.submit_package(evidence(receipt))
        assert result.committed and result.continued
        assert effects["measure"] == 1 and effects["package_admission"] == 1
        framework = c._active.framework
        assert framework.packages[-1].receipt is receipt and type(framework.inner.map) is MapModel
        assert asdict(receipt) == original and snap(c)["prediction_at_begin"] == prediction
        control_match = (self.control["next_state"], self.control["consequence"]) == (
            receipt.next_state, receipt.realized_consequence)
        assert framework.inner.memory.records[-1].measurement_matches == control_match
        proof = audit(c, self.authentic, self.executions)
        assert snap(c)["protected"]["memory"][:-1] == self.before["protected"]["memory"]
        log("MEASURE_AUTHORIZATION_PUBLICATION", dict(authorization=asdict(result),
            effects=effects, control_measurement_matches=control_match, provenance=proof))
        c.release(receipt)
        after = snap(c)
        assert after["world_executions"] == after["source_event_count"] == 6
        assert after["root_receipt"] is None
        return plain(dict(control_prediction=prediction, latch=latched, actual=actual,
            receipt=original, authorization=asdict(result), effects=effects,
            provenance=proof, control_measurement_matches=control_match,
            before=self.before, after=after))

    def finish(self, calls, journal=None):
        assert set(calls) == set(ROLES)
        predictions = {role: deepcopy(calls[role]["parsed"]) for role in ROLES}
        next_prediction = predictions["N"]
        consequence_prediction = predictions["C"]
        reconciled = None
        if next_prediction is not None and consequence_prediction is not None:
            reconciled = dict(next_state=next_prediction["next_state"],
                              consequence=consequence_prediction["consequence"])
        reconciliation = dict(
            mechanical=True, model_inference=False, correction=False, retry=False,
            voting=False, hidden_law_lookup=False,
            next_state_call_id=calls["N"]["call_id"],
            consequence_call_id=calls["C"]["call_id"],
            both_component_outputs_durable_and_parsed=True,
            invalid_component_abstains=(reconciled is None), result=deepcopy(reconciled))
        if journal is not None:
            assert all(journal.calls.get(calls[role]["call_id"]) == "PARSED" for role in ROLES)
            journal.append("SPLIT_RECONCILIATION_FROZEN", reconciliation)
        grounded = self.grounded_step(journal)
        receipt = grounded["receipt"]
        scores = {
            "J": dict(next_state=(predictions["J"]["next_state"] == receipt["next_state"]
                                  if predictions["J"] else None),
                      consequence=(predictions["J"]["consequence"] == receipt["realized_consequence"]
                                   if predictions["J"] else None)),
            "N": dict(next_state=(next_prediction["next_state"] == receipt["next_state"]
                                  if next_prediction else None)),
            "C": dict(consequence=(consequence_prediction["consequence"] == receipt["realized_consequence"]
                                   if consequence_prediction else None)),
        }
        scores["J"]["exact"] = (scores["J"]["next_state"] and scores["J"]["consequence"]
                                  if predictions["J"] else None)
        scores["split"] = dict(
            next_state=scores["N"]["next_state"] if reconciled else None,
            consequence=scores["C"]["consequence"] if reconciled else None,
            exact=(scores["N"]["next_state"] and scores["C"]["consequence"]
                   if reconciled else None))
        assert predictions == {role: calls[role]["parsed"] for role in ROLES}
        return dict(descriptor=self.d, predictions=predictions,
            reconciled_prediction=reconciled, reconciliation=reconciliation, scores=scores,
            authentic_post_response_score=True, authentic_history=True,
            probe_detached=True, probe_publication=False, **grounded)
