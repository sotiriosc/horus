"""Zero-inference tests for Horus v0.9 capability-gap detection."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest

from experiments.base_framework_v0.framework import ACTION_ORDER

from .capability_gap import (CapabilityAssessor, CapabilityGapStore,
    initialize_capability_gap_registry)


SOURCE = Path(__file__).resolve().parents[1] / "research/problem-route-request-v0"


class FakeStore:
    def __init__(self, session_id):
        self.checkpoint = dict(session_id=session_id, attempted_decisions=54)
        self.records = {"events": [{} for _ in range(50)]}


def forecasts(tie=True, valid=True):
    values={"ADVANCE":1,"HOLD":0,"RETREAT":1 if tie else -1}
    return {action:dict(G2_consequence=values[action],G3_consequence=values[action],
        selected_specialist="G2",routed_consequence=values[action],next_state={
            "ADVANCE":3,"HOLD":2,"RETREAT":1}[action],action_alias=f"K{i+1}",
        history_count=3,valid=valid,selected_failure=None if valid else "TimeoutError",
        G2_failure=None if valid else "TimeoutError",G3_failure=None if valid else "TimeoutError")
        for i,action in enumerate(ACTION_ORDER)}


def metadata(state=2):
    return {action:dict(relation={"pre_state":state,"action":action},
        authenticated_observations=3,most_recent_observation_sequence=10+i,
        recent_realized_consequences=[1],recent_correctness={},
        local_scores={"G2":{"correct":2,"total":3},"G3":{"correct":2,"total":3}},
        selected_specialist="G2",specialists_disagree=False,
        clear_local_preference=False,observations_since_last_execution=2,
        unresolved_recent_contradiction=None,qualifying_probe_reasons=[])
        for i,action in enumerate(ACTION_ORDER)}


def ordinary(sequence,tie=True,valid=True):
    return dict(decision_sequence=sequence,mode="EXPLOIT",
        action=None if tie or not valid else "ADVANCE",
        reason=("INVALID_MAP_COMPONENT" if not valid else
                "EXPLOIT_TIED_MAXIMUM" if tie else "UNIQUE_ROUTED_MAXIMUM"),
        abstained=tie or not valid,probe_budget_available=True,
        relation_confidence=metadata(),coverage={})


class CapabilityGapTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory(); self.root=Path(self.tmp.name)/"registry"
        self.root.mkdir()
        shutil.copy2(SOURCE/"problem-route-registry.json",self.root/"problem-route-registry.json")
        initialize_capability_gap_registry(self.root,SOURCE/"problem-route-report.json")
        report=json.loads((SOURCE/"problem-route-report.json").read_text())
        self.store=FakeStore(report["final_checkpoint"]["session_id"])
        self.gap=CapabilityGapStore(self.root)

    def tearDown(self): self.gap.close(); self.tmp.cleanup()

    def prepare(self,tie=True,valid=True):
        seq=self.store.checkpoint["attempted_decisions"]+1
        return self.gap.prepare(store=self.store,ordinary_decision=ordinary(seq,tie,valid),
                                pre_state=2,forecasts=forecasts(tie,valid))

    def finish(self,decision,consequence=1,next_state=1,authorized=True):
        self.store.checkpoint["attempted_decisions"]+=1
        row=dict(prediction_batch_sequence=decision["decision_sequence"],
                 status="AUTHORIZED" if authorized else "ABSTAINED")
        if authorized:
            self.store.records["events"].append({})
            row.update(receipt=dict(source_identity="source",event_id=1,epoch=1,
                transaction_id=decision["decision_sequence"],action=decision["action"],
                realized_consequence=consequence,next_state=next_state),
                routing_evidence=dict(evidence_sequence=len(self.store.records["events"])))
        return self.gap.complete(store=self.store,row=row)

    def two_probes(self,second_consequence=1):
        first=self.prepare(); self.finish(first,1,3)
        second=self.prepare(); self.finish(second,second_consequence,1)
        return first,second

    def test_01_unprobed_action_prevents_repeat(self):
        first,second=self.two_probes()
        self.assertEqual((first["action"],second["action"]),("ADVANCE","RETREAT"))

    def test_02_every_tied_action_gets_problem_evidence(self):
        self.two_probes(); history=self.gap.state["current_problem"]["problem_probe_history"]
        self.assertTrue(all(len(history[action])==1 for action in ("ADVANCE","RETREAT")))

    def test_03_equal_receipts_do_not_false_resolve(self):
        self.two_probes(); problem=self.gap.state["current_problem"]
        self.assertNotEqual(problem["status"],"RESOLVED")

    def test_04_unequal_evidence_and_unique_ordinary_path_resolve(self):
        self.two_probes(second_consequence=-1)
        decision=self.prepare(tie=False)
        self.assertEqual(decision["capability_assessment"],"VALUE_TIE_RESOLVED")

    def test_05_adequate_equal_evidence_classifies_objective_gap(self):
        self.two_probes(); decision=self.prepare()
        self.assertEqual(decision["capability_assessment"],
                         "CURRENT_OBJECTIVE_CANNOT_DISTINGUISH")

    def test_06_objective_gap_requests_longer_horizon_value(self):
        self.two_probes(); decision=self.prepare()
        self.assertEqual(decision["route_design_request"]["requested_capability"],
                         "LONGER_HORIZON_VALUE")

    def test_07_incomplete_coverage_requests_more_evidence(self):
        decision=self.prepare()
        self.assertEqual((decision["capability_assessment"],decision[
            "route_broker"]["requested_capability"]),
            ("MORE_EVIDENCE_REQUIRED","MORE_RELATION_EVIDENCE"))

    def test_08_service_failure_never_becomes_representation_gap(self):
        first=self.prepare(); self.finish(first)
        decision=self.prepare(valid=False)
        problem=self.gap.state["current_problem"]
        self.assertEqual((decision["capability_assessment"],problem[
            "where_did_resolution_stop"],problem["requested_capability"]),
            ("ROUTE_FAILED","MODEL_SERVICE","EXTERNAL_SERVICE_REPAIR"))

    def test_09_runtime_exhaustion_maps_to_new_runtime(self):
        assessor=CapabilityAssessor()
        self.assertEqual(assessor.localize(runtime_exhausted=True),"RUNTIME_CAPACITY")
        self.assertEqual(assessor.request("NEW_RUNTIME")["authority_status"],
                         "REQUEST_REQUIRES_EXTERNAL_APPROVAL")

    def test_10_common_specialist_error_rule_is_frozen(self):
        assessor=CapabilityAssessor()
        no=assessor.repeated_specialist_error(shared_grounded_errors=2,
            sufficiently_observed=True,same_prediction=True)
        yes=assessor.repeated_specialist_error(shared_grounded_errors=3,
            sufficiently_observed=True,same_prediction=True)
        self.assertEqual(no["requested_capability"],"ALTERNATIVE_REPRESENTATION")
        self.assertEqual(yes["requested_capability"],"NEW_SPECIALIST")
        self.assertFalse(yes["authoritative"])

    def test_11_all_escalation_requests_have_zero_authority(self):
        assessor=CapabilityAssessor()
        for capability in assessor.policy["external_approval_only"]:
            row=assessor.request(capability)
            self.assertFalse(row["authoritative"]); self.assertFalse(row["can_execute"])

    def test_12_restart_preserves_escalation_history(self):
        self.two_probes(); decision=self.prepare(); self.finish(decision,authorized=False)
        before=deepcopy(self.gap.state)
        self.gap.close(); self.gap=CapabilityGapStore(self.root)
        self.gap.bind_session(self.store)
        self.assertEqual(self.gap.state["terminal_classification"],
                         "CURRENT_OBJECTIVE_CANNOT_DISTINGUISH")
        self.assertEqual(self.gap.state["current_problem"],before["current_problem"])

    def test_13_problem_evolution_is_append_only(self):
        prefix=(self.root/CapabilityGapStore.STREAM).read_bytes()
        decision=self.prepare(); self.finish(decision)
        after=(self.root/CapabilityGapStore.STREAM).read_bytes()
        self.assertTrue(after.startswith(prefix)); self.assertGreater(len(after),len(prefix))

    def test_14_prediction_and_receipt_are_distinct(self):
        decision=self.prepare(); self.finish(decision,consequence=1,next_state=3)
        row=self.gap.state["current_problem"]["problem_probe_history"]["ADVANCE"][0]
        self.assertTrue(row["prediction_is_descriptive_model_output"])
        self.assertTrue(row["receipt_is_authenticated"])
        self.assertIn("predicted_next_state",row); self.assertIn("realized_next_state",row)

    def test_15_hidden_answers_are_absent(self):
        self.prepare(); record=self.gap.records[-1]["record"]
        self.assertFalse(record["hidden_regime_available"])
        self.assertFalse(record["simulator_law_available"])
        self.assertFalse(record["future_consequence_available"])


if __name__=="__main__": unittest.main()
