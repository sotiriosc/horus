"""Tests for the one-use v0.17 PR-0002 option-profile integration."""
from copy import deepcopy
import hashlib,inspect,json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

from .core import digest
from .option_profile_integration import (
    OptionProfileIntegrationExplorer,_suffix_check,verify_v016_evidence)
from .problem_manager import POLICY,ProblemManager,decision_scope
from .routing import RoutingError


def _problem(pid="PR-0002",scope=None):
    return dict(problem_id=pid,problem_type="UNRESOLVED_VALUE_TIE",
        scope=scope or decision_scope(2,["ADVANCE","RETREAT"]),owner="EVIDENCE_COVERAGE",
        lifecycle_state="REASSESSED",capability_assessment="CURRENT_OBJECTIVE_CANNOT_DISTINGUISH",
        requested_capability="OPTION_PROFILE_BEHAVIORAL_INTEGRATION",
        created_decision_sequence=1,route_budgets={
            "option_profile_dominance":{"limit":1,"evaluated":1}},route_request_count=0,
        probe_evidence={"ADVANCE":[],"RETREAT":[]},evidence=[{"retained":True}],
        imported_snapshot={},imported_snapshot_sha256=digest({}),history=[],
        **{k:False for k in POLICY["manager_authority"]})


def _ordinary(reason="EXPLOIT_TIED_MAXIMUM",abstained=True):
    return dict(decision_sequence=86,reason=reason,abstained=abstained,action=None,
        mode="ABSTAIN",relation_confidence={})


def _forecasts(unique=False):
    values={"ADVANCE":1,"HOLD":0,"RETREAT":(-1 if unique else 1)}
    return {a:dict(valid=True,routed_consequence=v) for a,v in values.items()}


class _Store:
    checkpoint={"session_id":"s","attempted_decisions":85}
    records={"events":[{} for _ in range(54)]}


class OptionProfileIntegrationTests(unittest.TestCase):
    def _manager(self,p2=None):
        temporary=TemporaryDirectory(); root=Path(temporary.name)
        p2=p2 or _problem(); p3=_problem("PR-0003",decision_scope(1,["ADVANCE","HOLD"]))
        p3["requested_capability"]=None
        manager=ProblemManager.create(root,session_id="s",attempted_decisions=85,
            authorized_executions=54,imported_problems=[p2,p3],edges=[])
        self.addCleanup(manager.close); self.addCleanup(temporary.cleanup)
        return manager

    @staticmethod
    def _authorize(manager,profile_hash="b"*64):
        manager.authorize_option_profile_integration(problem_id="PR-0002",
            authorization_sha256="a"*64,profile_evidence_sha256=profile_hash,
            result="RETREAT_PROFILE_DOMINATES",selected_action="RETREAT")

    @staticmethod
    def _prepare(manager,profile_hash="b"*64,forecasts=None):
        return manager.prepare_option_profile_integration(store=_Store(),
            ordinary_decision=_ordinary(),pre_state=2,forecasts=forecasts or _forecasts(),
            problem_id="PR-0002",profiles={"RETREAT":[]},
            result="RETREAT_PROFILE_DOMINATES",selected_action="RETREAT",
            profile_evidence_sha256=profile_hash)

    def test_01_unavailable_without_pr0002_applicability(self):
        manager=self._manager(_problem(scope=decision_scope(3,["ADVANCE","RETREAT"])))
        with self.assertRaises(RoutingError): self._authorize(manager)

    def test_02_unavailable_for_unique_ordinary_maximum(self):
        manager=self._manager(); self._authorize(manager)
        with self.assertRaises(RoutingError): self._prepare(manager,forecasts=_forecasts(unique=True))
        self.assertIsNone(manager.state["pending_decision"])

    def test_03_unavailable_when_profile_commitment_differs(self):
        manager=self._manager(); self._authorize(manager)
        with self.assertRaises(RoutingError): self._prepare(manager,profile_hash="c"*64)

    def test_04_only_retreat_dominating_action_can_be_selected(self):
        manager=self._manager()
        with self.assertRaises(RoutingError):
            manager.authorize_option_profile_integration(problem_id="PR-0002",
                authorization_sha256="a"*64,profile_evidence_sha256="b"*64,
                result="RETREAT_PROFILE_DOMINATES",selected_action="ADVANCE")
        self._authorize(manager); final=self._prepare(manager)
        self.assertEqual(final["action"],"RETREAT")

    def test_05_selection_is_durable_before_completion(self):
        manager=self._manager(); self._authorize(manager); self._prepare(manager)
        self.assertEqual(manager.records[-1]["kind"],"OPTION_PROFILE_DECISION_FROZEN")
        self.assertEqual(manager.state["pending_decision"]["action"],"RETREAT")

    def test_06_reality_cannot_change_frozen_action(self):
        manager=self._manager(); self._authorize(manager); self._prepare(manager)
        manager._append("LIVE_DECISION_COMPLETED",dict(decision_sequence=86,status="AUTHORIZED",
            runtime_id="r",receipt=dict(receipt_identity=["s","e",1,1],action="RETREAT",
                realized_consequence=-1,realized_next_state=3,receipt_is_authenticated=True)))
        self.assertEqual(manager.state["problems"]["PR-0002"][
            "option_profile_integration_result"],"INTEGRATION_EXECUTED_CONTRADICTED")

    def test_07_advance_counterfactual_receipt_is_rejected(self):
        manager=self._manager(); self._authorize(manager); self._prepare(manager)
        record=dict(decision_sequence=86,status="AUTHORIZED",runtime_id="r",
            receipt=dict(receipt_identity=["s","e",1,1],action="ADVANCE",
                realized_consequence=1,realized_next_state=2,receipt_is_authenticated=True))
        with self.assertRaises(RoutingError):
            manager._apply(deepcopy(manager.state),"LIVE_DECISION_COMPLETED",record)

    def test_08_new_receipt_is_authenticated_ordinary_evidence(self):
        manager=self._manager(); self._authorize(manager); self._prepare(manager)
        receipt=dict(receipt_identity=["s","e",1,1],action="RETREAT",realized_consequence=1,
            realized_next_state=1,receipt_is_authenticated=True)
        manager._append("LIVE_DECISION_COMPLETED",dict(decision_sequence=86,status="AUTHORIZED",
            runtime_id="r",receipt=receipt))
        observed=manager.state["problems"]["PR-0002"]["evidence"][-1]
        self.assertTrue(observed["receipt"]["receipt_is_authenticated"])

    def test_09_contradiction_appends_without_overwriting_prior(self):
        manager=self._manager(); before=deepcopy(manager.state["problems"]["PR-0002"]["evidence"])
        self._authorize(manager); self._prepare(manager)
        manager._append("LIVE_DECISION_COMPLETED",dict(decision_sequence=86,status="AUTHORIZED",
            runtime_id="r",receipt=dict(receipt_identity=["s","e",1,1],action="RETREAT",
                realized_consequence=0,realized_next_state=2,receipt_is_authenticated=True)))
        after=manager.state["problems"]["PR-0002"]["evidence"]
        self.assertEqual(after[:len(before)],before); self.assertEqual(after[-1]["classification"],
            "INTEGRATION_EXECUTED_CONTRADICTED")

    def test_10_followup_allowance_is_exactly_one(self):
        manager=self._manager(); self._authorize(manager); self._prepare(manager)
        manager._append("LIVE_DECISION_COMPLETED",dict(decision_sequence=86,status="AUTHORIZED",
            runtime_id="r",receipt=dict(receipt_identity=["s","e",1,1],action="RETREAT",
                realized_consequence=1,realized_next_state=1,receipt_is_authenticated=True)))
        row=dict(problem_id="PR-0002",decision_sequence=87,status="ABSTAINED",
            explorer={"reason":"EXPLOIT_TIED_MAXIMUM","action":None},receipt=None,
            suffix_prefix_check=None)
        manager._append("OPTION_PROFILE_FOLLOWUP_OBSERVED",row)
        row["decision_sequence"]=88
        with self.assertRaises(RoutingError):
            manager._apply(deepcopy(manager.state),"OPTION_PROFILE_FOLLOWUP_OBSERVED",row)

    def test_11_suffix_check_is_observational_only(self):
        profiles={"RETREAT":[dict(second_action="ADVANCE",sequence=[1,1,1])]}
        row=dict(status="AUTHORIZED",explorer={"action":"ADVANCE"},
            receipt={"realized_consequence":1})
        check=_suffix_check(profiles,row)
        self.assertEqual(check["label"],"OBSERVED_SUFFIX_PREFIX_CHECK")
        self.assertFalse(check["controls_behavior"]); self.assertFalse(check["full_trajectory_validated"])

    def test_12_representation_is_not_globalized(self):
        source=inspect.getsource(OptionProfileIntegrationExplorer)
        self.assertIn('problem_id="PR-0002"',source)
        self.assertNotIn("GroundedExplorer =",source)

    def test_13_pr0003_remains_unchanged(self):
        manager=self._manager(); before=deepcopy(manager.state["problems"]["PR-0003"])
        self._authorize(manager); self._prepare(manager)
        manager._append("LIVE_DECISION_COMPLETED",dict(decision_sequence=86,status="AUTHORIZED",
            runtime_id="r",receipt=dict(receipt_identity=["s","e",1,1],action="RETREAT",
                realized_consequence=1,realized_next_state=1,receipt_is_authenticated=True)))
        self.assertEqual(manager.state["problems"]["PR-0003"],before)

    def test_14_no_training_operation_exists(self):
        import horus.option_profile_integration as module
        source=inspect.getsource(module)
        self.assertNotIn(".train(",source); self.assertNotIn("optimizer",source)

    def test_15_v016_evidence_remains_byte_identical(self):
        root=Path(__file__).resolve().parents[1]/"research/option-profile-dominance-v0"
        manifest=json.loads((root/"evidence-manifest.json").read_text())
        for name,expected in manifest["files"].items():
            self.assertEqual(hashlib.sha256((root/name).read_bytes()).hexdigest(),expected)


if __name__=="__main__": unittest.main()
