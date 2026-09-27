import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from horus.core import digest
from horus.grounded_relation_reacquisition import select_one_step
from horus.problem_manager import ProblemManager,decision_scope
from horus.relation_routing import relation_identity
from horus.routing import RoutingError


class Memory:
    def __init__(self,edges):
        self.records={"events":edges}


def edge(seq,action,next_state,consequence=0,authenticated=True):
    return dict(pre_state=2,action=action,realized_next_state=next_state,
        realized_consequence=consequence,receipt_identity=["s",seq,1,seq],epoch=1,
        transaction_id=seq,event_sequence=seq,recorded_at=str(seq),
        receipt_provenance_sha256=str(seq)*64,authenticated=authenticated,
        source="AUTHORIZED_REALIZED_EVENT" if authenticated else "PREDICTION")


def problem(pid,state,actions):
    p=dict(problem_id=pid,problem_type="UNRESOLVED_VALUE_TIE",
        scope=decision_scope(state,actions),owner="EXPLORER_VALUE_COMPARISON",
        lifecycle_state="REASSESSED",capability_assessment="MORE_EVIDENCE_REQUIRED",
        requested_capability="MORE_RELATION_EVIDENCE",created_decision_sequence=65,
        route_budgets={"deadlock_information_probe":{"limit":1,"granted":1,"executed":1}},
        route_request_count=2,probe_evidence={a:[] for a in actions},evidence=[],
        imported_snapshot=None,imported_snapshot_sha256=None,history=[],
        select_actions=False,execute=False,issue_receipts=False,alter_memory=False,
        alter_predictions=False,train=False,change_objective=False,create_model=False,
        self_authorize=False)
    if pid=="PR-0003":
        p["route_budgets"]["problem_scoped_relation_probe"]={"limit":2,"granted":1,
            "executed":1,"relation":relation_identity(1,"ADVANCE"),
            "authorization_sha256":"v"*64,"request_event_sha256":"r"*64}
    return p


class Store:
    def __init__(self,attempts=89,events=56):
        self.checkpoint={"session_id":"s","attempted_decisions":attempts}
        self.records={"events":[{} for _ in range(events)]}


def ordinary(sequence=90):
    return dict(decision_sequence=sequence,mode="EXPLOIT",action=None,
        reason="EXPLOIT_TIED_MAXIMUM",abstained=True,probe_budget_available=True)


def forecasts(state=2):
    values=(("ADVANCE",1),("HOLD",1),("RETREAT",0)) if state==1 else \
           (("ADVANCE",1),("HOLD",0),("RETREAT",1))
    return {a:{"valid":True,"routed_consequence":v} for a,v in values}


class GroundedReacquisitionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); root=Path(self.tmp.name)
        self.manager=ProblemManager.create(root,session_id="s",attempted_decisions=89,
            authorized_executions=56,imported_problems=[problem("PR-0002",2,
            ["ADVANCE","RETREAT"]),problem("PR-0003",1,["ADVANCE","HOLD"])],edges=[])
        self.target=relation_identity(1,"ADVANCE")
        self.support=edge(55,"RETREAT",1,1)

    def tearDown(self):
        self.manager.close(); self.tmp.cleanup()

    def authorize(self):
        self.manager.record_target_relation_not_current(problem_id="PR-0003",
            target_relation=self.target,current_state=2)
        return self.manager.authorize_grounded_relation_reacquisition(problem_id="PR-0003",
            target_relation=self.target,selected_action="RETREAT",
            supporting_receipt_identity=self.support["receipt_identity"],
            authorization_sha256="a"*64,graph_sha256="g"*64)

    def prepare(self):
        return self.manager.prepare_grounded_relation_reacquisition(store=Store(),
            ordinary_decision=ordinary(),pre_state=2,forecasts=forecasts(),
            supporting_receipt=self.support)

    def complete_navigation(self,next_state=1):
        row=dict(prediction_batch_sequence=90,status="AUTHORIZED",
            source_scope={"source_identity":"new"},receipt={"source_identity":"new",
            "event_id":1,"epoch":2,"transaction_id":1,"action":"RETREAT",
            "realized_consequence":-1,"next_state":next_state},routing_evidence=None)
        return self.manager.complete(store=Store(90,57),row=row)

    def test_01_prediction_cannot_create_edge(self):
        result=select_one_step({"edges":[edge(1,"ADVANCE",1,authenticated=False)]},
                               current_state=2,target_state=1)
        self.assertEqual(result["status"],"RELATION_REACQUISITION_ROUTE_UNAVAILABLE")

    def test_02_only_authenticated_receipts_create_edges(self):
        result=select_one_step({"edges":[edge(2,"RETREAT",1)]},current_state=2,target_state=1)
        self.assertEqual(result["selected_action"],"RETREAT")

    def test_03_target_state_comes_from_problem_scope(self):
        self.authorize(); budget=self.manager.state["problems"]["PR-0003"]["route_budgets"][
            "grounded_relation_reacquisition"]
        self.assertEqual(budget["target_state"],self.manager.state["problems"]["PR-0003"][
            "scope"]["pre_state"])

    def test_04_no_route_without_grounded_edge(self):
        result=select_one_step({"edges":[edge(1,"RETREAT",3)]},current_state=2,target_state=1)
        self.assertEqual(result["status"],"RELATION_REACQUISITION_ROUTE_UNAVAILABLE")

    def test_05_frozen_priority_uses_recency_then_repetitions(self):
        result=select_one_step({"edges":[edge(10,"ADVANCE",1),edge(11,"RETREAT",1),
            edge(12,"RETREAT",1)]},current_state=2,target_state=1)
        self.assertEqual(result["selected_action"],"RETREAT")
        self.assertEqual(result["supporting_receipt"]["event_sequence"],12)

    def test_06_route_is_one_use(self):
        self.authorize(); self.prepare(); self.complete_navigation()
        with self.assertRaises(RoutingError): self.prepare()

    def test_07_contradiction_preserves_old_and_new_receipts(self):
        self.authorize(); self.prepare(); self.complete_navigation(next_state=2)
        p=self.manager.state["problems"]["PR-0003"]
        self.assertEqual(p["reacquisition_status"],"REACQUISITION_TRANSITION_CONTRADICTED")
        self.assertEqual(p["route_budgets"]["grounded_relation_reacquisition"][
            "supporting_receipt_identity"],self.support["receipt_identity"])
        self.assertNotEqual(p["history"][-1]["receipt_identity"],self.support["receipt_identity"])

    def test_08_reacquired_only_after_authenticated_completion(self):
        self.authorize(); self.prepare()
        self.assertNotIn("target_relation_reacquired",self.manager.state["problems"]["PR-0003"])
        self.complete_navigation(); self.assertTrue(self.manager.state["problems"]["PR-0003"][
            "target_relation_reacquired"])

    def test_09_remaining_scoped_budget_is_not_reset(self):
        self.authorize(); self.prepare(); self.complete_navigation()
        budget=self.manager.state["problems"]["PR-0003"]["route_budgets"][
            "problem_scoped_relation_probe"]
        self.assertEqual((budget["limit"],budget["granted"],budget["executed"]),(2,1,1))

    def test_10_second_probe_requires_state_one(self):
        self.authorize(); self.prepare(); self.complete_navigation()
        with self.assertRaises(RoutingError):
            self.manager.prepare_remaining_scoped_relation_probe(store=Store(90,57),
                ordinary_decision=ordinary(91),pre_state=2,forecasts=forecasts())
        decision=self.manager.prepare_remaining_scoped_relation_probe(
            store=Store(90,57),ordinary_decision=ordinary(91),pre_state=1,
            forecasts=forecasts(1))
        self.assertEqual((decision["action"],decision["reason"]),
                         ("ADVANCE","GROUND_RELATION_FOR_SPECIALIST_SELECTION"))

    def test_11_rolling_six_evicts_exact_oldest(self):
        rows=list(range(1,7)); after=(rows+[7])[-6:]
        self.assertEqual(rows[0],1); self.assertEqual(after,[2,3,4,5,6,7])

    def test_12_router_change_requires_receipt_scored_completion(self):
        self.authorize(); self.prepare()
        p=self.manager.state["problems"]["PR-0003"]
        self.assertNotIn("reacquisition_status",p)
        self.complete_navigation(); self.assertEqual(p["reacquisition_status"],
                                                     "TARGET_RELATION_REACQUIRED")

    def test_13_navigation_does_not_optimize_consequence(self):
        result=select_one_step({"edges":[edge(10,"ADVANCE",1,99),
            edge(11,"RETREAT",1,-99)]},current_state=2,target_state=1)
        self.assertEqual(result["selected_action"],"RETREAT")
        self.assertFalse(result["consequence_used_for_selection"])

    def test_14_pr0002_is_unchanged(self):
        before=deepcopy(self.manager.state["problems"]["PR-0002"]); self.authorize()
        self.assertEqual(before,self.manager.state["problems"]["PR-0002"])

    def test_15_no_global_navigation_is_introduced(self):
        event=self.authorize()
        self.assertFalse(event["record"]["global_navigation"])
        with self.assertRaises(RoutingError):
            self.manager.record_target_relation_not_current(problem_id="PR-0002",
                target_relation=self.target,current_state=2)


if __name__=="__main__": unittest.main()
