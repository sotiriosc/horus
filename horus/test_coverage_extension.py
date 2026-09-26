"""Zero-inference checks for the v0.11 coverage-only intervention."""
from __future__ import annotations
import inspect,json
from pathlib import Path
import unittest

from experiments.base_framework_v1.framework import EPISODE_LIMIT
from .capability_gap import CapabilityGapRuntime
from .core import MapForecast,MechanicalExplorer
from .coverage_extension import (POLICY,CoverageExtensionRuntime,
    _operational_failure,classify_outcome,eligible_reassessments,
    run_coverage_extension,verify_frozen_implementation)
from .grounded_exploration import GroundedExplorer
from .routing import RoutingError


class CoverageExtensionTests(unittest.TestCase):
    def test_01_only_authority_change_is_finite_decision_bound(self):
        self.assertEqual(POLICY["maximum_fresh_behavioral_decisions"],20)
        self.assertEqual(POLICY["maximum_ordinary_prediction_calls"],180)
        self.assertEqual((POLICY["operational_health_calls"],POLICY["repair_calls"],
                          POLICY["training_runs"]),(0,0,0))

    def test_02_frozen_behavioral_files_are_byte_identical(self):
        self.assertEqual(verify_frozen_implementation(),POLICY["frozen_sha256"])

    def test_03_runtime_changes_sequence_binding_only(self):
        self.assertIs(CoverageExtensionRuntime.execute_autonomous,
                      CapabilityGapRuntime.execute_autonomous)
        own=set(CoverageExtensionRuntime.__dict__)-{"__module__","__doc__"}
        self.assertEqual(own,{"_next_batch"})

    def test_04_state_one_tie_behavior_remains_abstention(self):
        rows=tuple(MapForecast(a,f"K{i+1}",1,1,False,None,1,{})
                   for i,a in enumerate(("ADVANCE","HOLD","RETREAT")))
        result=MechanicalExplorer().choose(rows)
        self.assertTrue(result.abstained); self.assertEqual(result.reason,"TIED_MAXIMUM")

    def test_05_classifier_requirements_are_frozen(self):
        source=inspect.getsource(__import__("horus.capability_gap",fromlist=[
            "CapabilityGapStore"]).CapabilityGapStore.prepare)
        for required in ("covered","len(set(outcomes))==1","probe_count"):
            self.assertIn(required,source)

    def test_06_probe_budget_semantics_are_frozen(self):
        policy=json.loads(Path(__file__).with_name(
            "grounded_exploration_policy.json").read_text())
        self.assertEqual(policy["probe_budget"]["minimum_decision_distance"],3)
        self.assertNotIn("probe_budget",POLICY)

    def test_07_repair_authority_is_not_replenished(self):
        self.assertEqual((POLICY["repair_restart_count_required"],
                          POLICY["repair_reissue_count_required"]),(1,1))
        self.assertEqual(POLICY["repair_calls"],0)

    @staticmethod
    def record(sequence=64,state=2,reason="EXPLOIT_TIED_MAXIMUM",valid=True):
        forecasts={a:{"valid":valid} for a in ("ADVANCE","HOLD","RETREAT")}
        return {"kind":"CAPABILITY_GAP_DECISION_FROZEN","record":{
            "decision_sequence":sequence,"pre_state":state,
            "ordinary_decision":{"reason":reason},"forecasts":forecasts}}

    def test_08_synthetic_reassessment_has_no_runner_input(self):
        self.assertNotIn("reassessment",inspect.signature(run_coverage_extension).parameters)

    def test_09_old_or_invalid_evidence_cannot_masquerade_as_reassessment(self):
        rows=[self.record(sequence=63),self.record(state=1),
              self.record(reason="UNIQUE_ROUTED_MAXIMUM"),self.record(valid=False)]
        self.assertEqual(eligible_reassessments(rows),[])
        self.assertEqual(len(eligible_reassessments([self.record()])),1)

    def test_10_bound_exhaustion_is_honestly_inconclusive(self):
        self.assertEqual(classify_outcome(None,None,20),"INCONCLUSIVE_AT_BOUND")
        with self.assertRaises(RoutingError): classify_outcome(None,None,19)

    def test_11_segmentation_respects_protected_limit(self):
        self.assertEqual(POLICY["runtime_decision_schedule"],[10,10])
        self.assertEqual(sum(POLICY["runtime_decision_schedule"]),20)
        self.assertTrue(all(x<EPISODE_LIMIT for x in POLICY[
            "runtime_decision_schedule"]))
        self.assertEqual(POLICY["protected_episode_limit"],EPISODE_LIMIT)

    def test_12_operational_failure_is_not_a_capability_gap(self):
        row=dict(status="ABSTAINED",explorer={"reason":"INVALID_MAP_COMPONENT"},
            forecasts={"ADVANCE":{"selected_failure":"URLError",
                "G2_failure":None,"G3_failure":None}})
        failure=_operational_failure(row)
        self.assertEqual((failure["classification"],failure["localization"]),
                         ("OPERATIONAL_FAILURE","MODEL_SERVICE"))
        self.assertTrue(failure["repair_authority_consumed"])


if __name__=="__main__": unittest.main()
