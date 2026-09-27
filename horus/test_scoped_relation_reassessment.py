import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from experiments.base_framework_v0.framework import ACTION_ORDER

from horus.core import digest
from horus.problem_manager import ProblemManager, decision_scope
from horus.relation_routing import RelationGroundedRouter, relation_identity
from horus.routing import RoutingError
from horus.scoped_relation_reassessment import (
    REQUEST_REASON, compact_rows, latest_state_forecasts, reassess_values,
    reconstruct_routing, relation_rows, route_availability)


POLICY=dict(window_size=6,minimum_shared_scored_events=3,
            switch_lead_correct=2,cold_start_specialist="G2")


def row(sequence, g2, g3, realized, before="G2", prefix=None):
    relation=relation_identity(1,"ADVANCE"); prefix=[] if prefix is None else prefix
    router=RelationGroundedRouter(POLICY)
    value=dict(evidence_sequence=sequence,relation=relation,
        specialists={"G2":{"frozen_consequence":g2},"G3":{"frozen_consequence":g3}},
        realized_consequence=realized,correctness={"G2":g2==realized,"G3":g3==realized},
        selected_specialist=before,router_score_before=router.scores(prefix,relation),
        receipt_identity=["source",sequence,1,sequence])
    update=router.update(prefix+[value],relation,before)
    value.update(router_score_after=update["scores"],switch_occurred=update["switched"],
                 selected_specialist_after=update["selected_after"])
    return value


def imported_problem(pid,state,actions):
    return dict(problem_id=pid,problem_type="UNRESOLVED_VALUE_TIE",
        scope=decision_scope(state,actions),owner="EXPLORER_VALUE_COMPARISON",
        lifecycle_state="ROUTE_EXECUTED",capability_assessment=None,
        requested_capability=None,created_decision_sequence=65,
        route_budgets={"deadlock_information_probe":{"limit":1,"granted":1,"executed":1}},
        route_request_count=1,probe_evidence={a:[] for a in actions},evidence=[],
        imported_snapshot=None,imported_snapshot_sha256=None,
        history=[{"lifecycle_state":"ROUTE_EXECUTED","decision_sequence":84}],
        select_actions=False,execute=False,issue_receipts=False,alter_memory=False,
        alter_predictions=False,train=False,change_objective=False,create_model=False,
        self_authorize=False)


class ScopedRelationReassessmentTests(unittest.TestCase):
    def setUp(self):
        self.relation=relation_identity(1,"ADVANCE")
        self.rows=[]
        selected="G2"
        for i,(g2,g3,actual) in enumerate([(-1,1,-1),(-1,-1,-1),(-1,-1,1),
                                            (-1,-1,-1),(1,-1,-1)],1):
            value=row(i,g2,g3,actual,selected,self.rows)
            self.rows.append(value); selected=value["selected_specialist_after"]
        self.retained=dict(relation=self.relation,selected_specialist="G2",
                           evidence_count=5,last_evidence_sequence=5)

    def test_01_complete_advance_evidence_replays(self):
        result=reconstruct_routing(self.rows,self.relation,self.retained,POLICY)
        self.assertTrue(result["consistent"]); self.assertEqual(len(compact_rows(
            self.rows,self.relation)),5)

    def test_02_selection_is_derived_from_scored_receipts(self):
        result=reconstruct_routing(self.rows,self.relation,self.retained,POLICY)
        self.assertEqual(result["scores"],{"G2":{"correct":3,"total":5},
                                            "G3":{"correct":3,"total":5}})
        self.assertEqual(result["current_selected_specialist"],"G2")

    def test_03_insufficient_lead_cannot_force_switch(self):
        result=reconstruct_routing(self.rows,self.relation,self.retained,POLICY)
        self.assertFalse(result["switch_rule_satisfied"])
        self.assertEqual(result["classification"],"ROUTING_CORRECT_AS_FROZEN")

    def test_04_sufficient_challenger_lead_switches(self):
        rows=[]; selected="G2"
        for i in range(3):
            value=row(i+1,1,-1,-1,selected,rows); rows.append(value)
            selected=value["selected_specialist_after"]
        self.assertEqual(selected,"G3")

    def test_05_retained_state_inconsistency_is_detected(self):
        bad=deepcopy(self.retained); bad["selected_specialist"]="G3"
        self.assertEqual(reconstruct_routing(self.rows,self.relation,bad,POLICY)[
            "classification"],"ROUTING_EVIDENCE_INCONSISTENT")

    def _manager(self,root):
        p2=imported_problem("PR-0002",2,["ADVANCE","RETREAT"])
        p3=imported_problem("PR-0003",1,["ADVANCE","HOLD"])
        return ProblemManager.create(root,session_id="s",attempted_decisions=88,
                                     authorized_executions=55,
                                     imported_problems=[p2,p3],edges=[])

    def _request(self,manager):
        return manager.request_relation_evidence(problem_id="PR-0003",relation=self.relation,
            classification="ROUTING_CORRECT_AS_FROZEN",latest_evidence_sequence=54,
            latest_grounded_comparison={"G2_correct":False,"G3_correct":True},
            current_scores={"G2":{"correct":3,"total":5},"G3":{"correct":3,"total":5}},
            selected_specialist="G2",route_availability={"existing_route_legally_available":False})

    def test_06_pr3_requests_relation_evidence_independently(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self._manager(Path(tmp)) as manager:
                self._request(manager)
                self.assertEqual(manager.state["problems"]["PR-0003"][
                    "requested_capability"],"MORE_RELATION_EVIDENCE")

    def test_07_pr2_option_authority_cannot_affect_pr3(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self._manager(Path(tmp)) as manager:
                before=deepcopy(manager.state["problems"]["PR-0002"]); self._request(manager)
                self.assertEqual(before,manager.state["problems"]["PR-0002"])

    def test_08_probe_reason_is_frozen_in_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self._manager(Path(tmp)) as manager:
                event=self._request(manager)
                self.assertEqual(event["record"]["reason"],REQUEST_REASON)

    def test_09_hidden_destination_cannot_influence_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self._manager(Path(tmp)) as manager:
                event=self._request(manager)
                self.assertFalse(event["record"]["hidden_transition_destination_used"])
                self.assertNotIn("next_state",event["record"])

    def test_10_unscored_prediction_cannot_update_router(self):
        before=reconstruct_routing(self.rows,self.relation,self.retained,POLICY)
        unscored=deepcopy(self.rows)+[{"relation":relation_identity(1,"HOLD")}]
        after=reconstruct_routing(relation_rows(unscored,self.relation),self.relation,
                                  self.retained,POLICY)
        self.assertEqual(before["scores"],after["scores"])

    def test_11_router_change_can_remove_tie_mechanically(self):
        result=reassess_values({"ADVANCE":-1,"HOLD":1,"RETREAT":0})
        self.assertEqual(result["ordinary_action"],"HOLD")
        self.assertFalse(result["ordinary_abstained"])

    def test_12_ordinary_followup_has_no_special_override(self):
        result=reassess_values({"ADVANCE":-1,"HOLD":1,"RETREAT":0})
        self.assertEqual(result["ordinary_reason"],"UNIQUE_ROUTED_MAXIMUM")
        self.assertNotIn("problem_id",result)

    def test_13_relation_request_cannot_train(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self._manager(Path(tmp)) as manager:
                event=self._request(manager)
                self.assertFalse(event["record"]["trains_model"])
                self.assertFalse(event["record"]["controls_execution"])

    def test_route_cadence_and_consumed_budget_require_approval(self):
        availability=route_availability(dict(authorized_decisions=55,
            last_probe_authorized_decision=54),{"probe_budget":{"minimum_decision_distance":3}},
            imported_problem("PR-0003",1,["ADVANCE","HOLD"]))
        self.assertFalse(availability["existing_route_legally_available"])
        self.assertEqual(availability["authority_status"],"REQUEST_REQUIRES_EXTERNAL_APPROVAL")


if __name__=="__main__": unittest.main()
