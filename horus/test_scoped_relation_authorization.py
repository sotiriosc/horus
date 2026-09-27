import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from horus.core import digest
from horus.grounded_exploration import ExplorerConfidenceStore
from horus.grounded_learning import file_hash
from horus.problem_manager import ProblemManager, decision_scope
from horus.relation_routing import relation_identity
from horus.routing import RoutingError
from horus.scoped_relation_authorization import cadence_deadlock_proof


def problem(pid,state,actions):
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


class Store:
    def __init__(self,attempts=88,events=55):
        self.checkpoint={"session_id":"s","attempted_decisions":attempts}
        self.records={"events":[{} for _ in range(events)]}


def ordinary(sequence=89,budget=False):
    return dict(decision_sequence=sequence,mode="EXPLOIT",action=None,
        reason="EXPLOIT_TIED_MAXIMUM",abstained=True,probe_budget_available=budget)


def forecasts():
    return {action:{"valid":True,"routed_consequence":value}
            for action,value in (("ADVANCE",1),("HOLD",1),("RETREAT",0))}


def proof(authorized=55,last=54):
    p=problem("PR-0003",1,["ADVANCE","HOLD"])
    p.update(requested_capability="MORE_RELATION_EVIDENCE",
             capability_assessment="MORE_EVIDENCE_REQUIRED")
    return cadence_deadlock_proof(confidence_state={"authorized_decisions":authorized,
        "last_probe_authorized_decision":last},problem=p,minimum_distance=3)


class ScopedRelationAuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); root=Path(self.tmp.name)
        self.manager=ProblemManager.create(root,session_id="s",attempted_decisions=88,
            authorized_executions=55,imported_problems=[problem("PR-0002",2,
            ["ADVANCE","RETREAT"]),problem("PR-0003",1,["ADVANCE","HOLD"])],edges=[])
        self.relation=relation_identity(1,"ADVANCE")
        self.request=self.manager.request_relation_evidence(problem_id="PR-0003",
            relation=self.relation,classification="ROUTING_CORRECT_AS_FROZEN",
            latest_evidence_sequence=54,
            latest_grounded_comparison={"G2_correct":False,"G3_correct":True},
            current_scores={"G2":{"correct":3,"total":5},"G3":{"correct":3,"total":5}},
            selected_specialist="G2",
            route_availability={"existing_route_legally_available":False})

    def tearDown(self):
        self.manager.close(); self.tmp.cleanup()

    def detect(self):
        return self.manager.record_route_gating_deadlock(problem_id="PR-0003",
            relation=self.relation,proof=proof())

    def authorize(self):
        self.detect()
        return self.manager.authorize_scoped_relation_evidence(problem_id="PR-0003",
            relation=self.relation,authorization_sha256="a"*64,
            request_event_sha256=digest(self.request))

    def completion(self,sequence=89,events=56,g2=3,g3=4,after="G2",switched=False,
                   receipt=True):
        row=dict(prediction_batch_sequence=sequence,status="AUTHORIZED",
            source_scope={"source_identity":"source"},receipt=(None if not receipt else {
            "source_identity":"source","event_id":sequence,"epoch":1,
            "transaction_id":sequence,"action":"ADVANCE","realized_consequence":-1,
            "next_state":2}),routing_evidence={"relation":self.relation,
            "evidence_sequence":events,"selected_specialist":"G2",
            "selected_specialist_after":after,"router_score_after":{
                "G2":{"correct":g2,"total":6},"G3":{"correct":g3,"total":6}},
            "switch_occurred":switched,"realized_consequence":-1,
            "receipt_identity":["source",sequence,1,sequence]})
        return self.manager.complete(store=Store(sequence,events),row=row)

    def test_01_cadence_deadlock_is_mechanical(self):
        result=proof(); self.assertEqual(result["classification"],"ROUTE_GATING_DEADLOCK")
        self.assertEqual(result["distance"],2); self.assertFalse(result["abstentions_advance_cadence"])

    def test_02_no_scoped_route_if_ordinary_cadence_can_advance(self):
        self.assertEqual(proof(55,53)["classification"],"ORDINARY_ROUTE_CAN_ADVANCE")
        with self.assertRaises(RoutingError):
            self.manager.authorize_scoped_relation_evidence(problem_id="PR-0003",
                relation=self.relation,authorization_sha256="a"*64,
                request_event_sha256=digest(self.request))

    def test_03_global_cadence_file_remains_unchanged(self):
        path=Path(__file__).with_name("grounded_exploration_policy.json"); before=file_hash(path)
        self.authorize(); self.assertEqual(file_hash(path),before)

    def test_04_exact_authorization_is_required(self):
        self.detect()
        with self.assertRaises(RoutingError):
            self.manager.authorize_scoped_relation_evidence(problem_id="PR-0003",
                relation=self.relation,authorization_sha256="a"*64,
                request_event_sha256="b"*64)

    def test_05_route_cannot_target_another_relation(self):
        self.detect()
        with self.assertRaises(RoutingError):
            self.manager.authorize_scoped_relation_evidence(problem_id="PR-0003",
                relation=relation_identity(1,"HOLD"),authorization_sha256="a"*64,
                request_event_sha256=digest(self.request))

    def test_06_hidden_destination_cannot_influence_route(self):
        self.authorize(); decision=self.manager.prepare_scoped_relation_probe(store=Store(),
            ordinary_decision=ordinary(),pre_state=1,forecasts=forecasts())
        self.assertNotIn("next_state",decision)
        self.assertEqual(decision["reason"],"GROUND_RELATION_FOR_SPECIALIST_SELECTION")

    def test_07_maximum_two_scoped_probes(self):
        self.authorize()
        self.manager.prepare_scoped_relation_probe(store=Store(),ordinary_decision=ordinary(),
            pre_state=1,forecasts=forecasts()); self.completion()
        self.manager.prepare_scoped_relation_probe(store=Store(89,56),
            ordinary_decision=ordinary(90),pre_state=1,forecasts=forecasts())
        self.completion(90,57)
        with self.assertRaises(RoutingError):
            self.manager.prepare_scoped_relation_probe(store=Store(90,57),
                ordinary_decision=ordinary(91),pre_state=1,forecasts=forecasts())

    def test_08_stop_state_on_legitimate_resolution(self):
        self.authorize(); self.manager.prepare_scoped_relation_probe(store=Store(),
            ordinary_decision=ordinary(),pre_state=1,forecasts=forecasts())
        self.completion(g2=2,g3=4,after="G3",switched=True)
        p=self.manager.state["problems"]["PR-0003"]
        self.assertEqual(p["capability_assessment"],"VALUE_TIE_RESOLVED")
        self.assertIsNone(p["requested_capability"])

    def test_09_probe_requires_receipt(self):
        self.authorize(); self.manager.prepare_scoped_relation_probe(store=Store(),
            ordinary_decision=ordinary(),pre_state=1,forecasts=forecasts())
        with self.assertRaises((RoutingError,TypeError)):
            self.completion(receipt=False)

    def test_10_scores_update_only_after_authorized_completion(self):
        self.authorize()
        self.manager.prepare_scoped_relation_probe(store=Store(),ordinary_decision=ordinary(),
            pre_state=1,forecasts=forecasts())
        evidence=self.manager.state["problems"]["PR-0003"]["evidence"]
        self.assertFalse(any(row.get("kind")=="PROBLEM_SCOPED_RELATION_RECEIPT"
                             for row in evidence))
        self.completion(); evidence=self.manager.state["problems"]["PR-0003"]["evidence"]
        self.assertTrue(any(row.get("kind")=="PROBLEM_SCOPED_RELATION_RECEIPT"
                            for row in evidence))

    def test_11_g2_may_remain_selected(self):
        self.authorize(); self.manager.prepare_scoped_relation_probe(store=Store(),
            ordinary_decision=ordinary(),pre_state=1,forecasts=forecasts())
        self.completion(); self.assertEqual(self.manager.state["problems"]["PR-0003"][
            "history"][-1]["selected_specialist_after"],"G2")

    def test_12_g3_may_legitimately_become_selected(self):
        self.authorize(); self.manager.prepare_scoped_relation_probe(store=Store(),
            ordinary_decision=ordinary(),pre_state=1,forecasts=forecasts())
        self.completion(g2=2,g3=4,after="G3",switched=True)
        self.assertEqual(self.manager.state["problems"]["PR-0003"]["history"][-1][
            "selected_specialist_after"],"G3")

    def test_13_scoped_mode_does_not_reset_ordinary_probe_cadence(self):
        replay=dict(attempted_decisions=88,authorized_decisions=55,
            last_probe_decision_sequence=84,last_probe_authorized_decision=54,
            last_execution_by_relation={},unresolved_contradictions={},outcomes={})
        freeze={"decision_sequence":89,"decision":{"mode":"PROBLEM_SCOPED_PROBE"}}
        complete={"decision_sequence":89,"status":"AUTHORIZED","relation":self.relation,
            "contradiction_baseline_required":3,"realized_consequence":-1,
            "contradiction_started":False,"routing_evidence_sequence":56,
            "router_score_after":{"G2":{"correct":3,"total":6},"G3":{"correct":4,"total":6}},
            "clear_preference_minimum_observations":3,"clear_preference_lead_correct":2,
            "contradiction_resolved":False}
        ExplorerConfidenceStore._apply_completion(replay,freeze,complete)
        self.assertEqual(replay["last_probe_authorized_decision"],54)
        self.assertEqual(replay["authorized_decisions"],56)

    def test_14_pr0002_is_unchanged(self):
        before=deepcopy(self.manager.state["problems"]["PR-0002"]); self.authorize()
        self.assertEqual(before,self.manager.state["problems"]["PR-0002"])

    def test_15_ordinary_followup_has_no_scoped_override(self):
        self.authorize(); decision=self.manager.prepare_scoped_relation_probe(store=Store(),
            ordinary_decision=ordinary(),pre_state=1,forecasts=forecasts())
        self.assertEqual(decision["mode"],"PROBLEM_SCOPED_PROBE")
        plain=ordinary(); self.assertNotIn("route_broker",plain)
        self.assertNotEqual(plain["reason"],decision["reason"])


if __name__=="__main__": unittest.main()
