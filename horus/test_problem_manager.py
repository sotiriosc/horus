"""Zero-inference tests for Horus v0.13 canonical problem ownership."""
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from .core import digest
from .problem_manager import ProblemManager, POLICY, decision_scope


ACTIONS=("ADVANCE","HOLD","RETREAT")

def forecasts(state=1,tied=("ADVANCE","HOLD"),valid=True):
    values={a:(1 if a in tied else 0) for a in ACTIONS}
    return {a:dict(routed_consequence=values[a],valid=valid,
        G2_consequence=values[a],G3_consequence=(-1 if a in tied else 0),next_state=state)
        for a in ACTIONS}

def metadata(state=1):
    return {a:dict(authenticated_observations={"ADVANCE":4,"HOLD":12,"RETREAT":8}[a],
        observations_since_last_execution={"ADVANCE":3,"HOLD":4,"RETREAT":8}[a],
        specialists_disagree=a in ("ADVANCE","HOLD"),unresolved_recent_contradiction=None)
        for a in ACTIONS}

def ordinary(sequence,state=1,tied=("ADVANCE","HOLD"),budget=False):
    return dict(decision_sequence=sequence,mode="EXPLOIT",action=None,
        reason="EXPLOIT_TIED_MAXIMUM",abstained=True,probe_budget_available=budget,
        relation_confidence=metadata(state),coverage={})

def imported(pid,state,actions,status="OPEN"):
    snapshot=dict(problem_id=pid,problem_type="UNRESOLVED_VALUE_TIE",state=state,
        candidate_actions=list(actions),status=status,created_decision_sequence=1,
        requested_capability="MORE_RELATION_EVIDENCE",route_request_count=0,probe_count=0)
    return dict(problem_id=pid,problem_type=snapshot["problem_type"],
        scope=decision_scope(state,list(actions)),owner="EVIDENCE_COVERAGE",
        lifecycle_state=status,capability_assessment="MORE_EVIDENCE_REQUIRED",
        requested_capability="MORE_RELATION_EVIDENCE",created_decision_sequence=1,
        route_budgets={"relation_information_probe":{"limit":2,"granted":0,"executed":0}},
        route_request_count=0,probe_evidence={a:[] for a in actions},evidence=[],
        imported_snapshot=snapshot,imported_snapshot_sha256=digest(snapshot),
        history=[{"lifecycle_state":status,"decision_sequence":1}],
        **{k:False for k in POLICY["manager_authority"]})

class FakeStore:
    def __init__(self,session="session",attempts=0,events=0):
        self.checkpoint={"session_id":session,"attempted_decisions":attempts}
        self.records={"events":[{} for _ in range(events)]}


class ProblemManagerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory(); self.root=Path(self.tmp.name)
        self.manager=ProblemManager.create(self.root,session_id="session",
            attempted_decisions=0,authorized_executions=0,imported_problems=[],edges=[])
    def tearDown(self): self.manager.close(); self.tmp.cleanup()

    def replay(self,state=1,tied=("ADVANCE","HOLD"),count=2):
        for _ in range(count):
            seq=self.manager.state["attempted_decisions"]+1
            self.manager.replay_decision(pre_state=state,
                ordinary_decision=ordinary(seq,state,tied),forecasts=forecasts(state,tied))

    def test_01_two_unrelated_problems_coexist(self):
        self.replay(); self.replay(state=2,tied=("ADVANCE","RETREAT"))
        self.assertEqual(len(self.manager.state["problems"]),2)

    def test_02_identical_scope_and_type_deduplicate(self):
        self.replay(count=5); self.assertEqual(len(self.manager.state["problems"]),1)

    def test_03_different_tied_sets_create_different_problems(self):
        self.replay(); self.replay(state=1,tied=("HOLD","RETREAT"))
        self.assertEqual(len(self.manager.state["problems"]),2)

    def test_04_existing_state2_cannot_block_state1(self):
        self.manager.close(); self.tmp.cleanup(); self.tmp=TemporaryDirectory(); self.root=Path(self.tmp.name)
        p=imported("PR-0002",2,("ADVANCE","RETREAT"),"ROUTE_EXECUTED")
        self.manager=ProblemManager.create(self.root,session_id="session",attempted_decisions=0,
            authorized_executions=0,imported_problems=[p],edges=[])
        self.replay(); self.assertIsNotNone(self.manager.applicable(pre_state=1,tied_actions=["ADVANCE","HOLD"]))

    def test_05_applicable_problem_is_exact_scope(self):
        self.replay()
        self.assertIsNotNone(self.manager.applicable(pre_state=1,tied_actions=["ADVANCE","HOLD"]))
        self.assertIsNone(self.manager.applicable(pre_state=1,tied_actions=["ADVANCE","RETREAT"]))

    def test_06_problem_budgets_are_independent(self):
        self.manager.close(); self.tmp.cleanup(); self.tmp=TemporaryDirectory(); self.root=Path(self.tmp.name)
        other=imported("PR-0002",2,("ADVANCE","RETREAT"),"ROUTE_EXECUTED")
        self.manager=ProblemManager.create(self.root,session_id="session",attempted_decisions=0,
            authorized_executions=0,imported_problems=[other],edges=[])
        self.replay(); before=deepcopy(self.manager.state["problems"]["PR-0002"]["route_budgets"])
        self.manager.preregister_deadlock_route("a"*64)
        store=FakeStore(attempts=2); self.manager.prepare(store=store,
            ordinary_decision=ordinary(3),pre_state=1,forecasts=forecasts())
        state1=self.manager.applicable(pre_state=1,tied_actions=["ADVANCE","HOLD"])
        self.assertEqual(state1["route_budgets"]["deadlock_information_probe"]["granted"],1)
        self.assertEqual(self.manager.state["problems"]["PR-0002"]["route_budgets"],before)

    def test_07_successor_relationship_does_not_merge_identity(self):
        self.manager.close(); self.tmp.cleanup(); self.tmp=TemporaryDirectory(); self.root=Path(self.tmp.name)
        p1=imported("PR-0001",2,("ADVANCE","RETREAT"),"UNRESOLVED")
        p2=imported("PR-0002",2,("ADVANCE","RETREAT"),"ROUTE_EXECUTED")
        self.manager=ProblemManager.create(self.root,session_id="session",attempted_decisions=0,
            authorized_executions=0,imported_problems=[p1,p2],edges=[])
        self.manager.add_edge(from_problem="PR-0002",relation="successor_of",to_problem="PR-0001")
        self.assertEqual(len(self.manager.state["problems"]),2)

    def test_08_operational_problem_does_not_rewrite_behavioral(self):
        self.replay(); behavioral=deepcopy(self.manager.state["problems"]["PR-0001"])
        self.manager.attach_operational(decision_sequence=3,problem_type="EXTERNAL_SERVICE_PROBLEM",
            scope={"kind":"service","service_id":"ollama"},owner="MODEL_SERVICE",
            blocked_problem_id="PR-0001")
        self.assertEqual(self.manager.state["problems"]["PR-0001"],behavioral)

    def test_09_runtime_problem_does_not_rewrite_behavioral(self):
        self.replay(); behavioral=deepcopy(self.manager.state["problems"]["PR-0001"])
        self.manager.attach_operational(decision_sequence=3,problem_type="INTERNAL_ROUTE_PROBLEM",
            scope={"kind":"runtime","runtime_id":"r1"},owner="RUNTIME_CAPACITY",
            blocked_problem_id="PR-0001")
        self.assertEqual(self.manager.state["problems"]["PR-0001"],behavioral)

    def test_10_graph_replays_exactly(self):
        self.replay(); before=deepcopy(self.manager.state); self.manager.close()
        self.manager=ProblemManager(self.root); self.assertEqual(self.manager.state,before)

    def test_11_restart_preserves_consumed_deadlock_budget(self):
        self.replay(); self.manager.preregister_deadlock_route("a"*64); store=FakeStore(attempts=2)
        result=self.manager.prepare(store=store,ordinary_decision=ordinary(3),pre_state=1,forecasts=forecasts())
        self.assertEqual(result["reason"],"DEADLOCK_INFORMATION_PROBE")
        store.checkpoint["attempted_decisions"]=3; store.records["events"].append({})
        self.manager.complete(store=store,row={"prediction_batch_sequence":3,"status":"AUTHORIZED",
            "receipt":{"source_identity":"s","event_id":1,"epoch":1,"transaction_id":1,
                       "action":result["action"],"realized_consequence":1,"next_state":2},
            "source_scope":{"source_identity":"s"}})
        self.manager.close(); self.manager=ProblemManager(self.root)
        budget=self.manager.state["problems"]["PR-0001"]["route_budgets"]["deadlock_information_probe"]
        self.assertEqual((budget["granted"],budget["executed"]),(1,1))

    def test_12_corrupt_index_rebuilds_from_authoritative_log(self):
        self.replay(); expected=deepcopy(self.manager.state); self.manager.close()
        (self.root/ProblemManager.INDEX).write_text("corrupt\n")
        self.manager=ProblemManager(self.root); self.assertEqual(self.manager.state,expected)

    def test_13_manager_has_zero_behavioral_authority(self):
        self.replay(); p=next(iter(self.manager.state["problems"].values()))
        self.assertTrue(all(p[k] is False for k in POLICY["manager_authority"]))

    def test_14_deadlock_route_requires_applicable_open_problem(self):
        self.replay(); store=FakeStore(attempts=2)
        result=self.manager.prepare(store=store,
            ordinary_decision=ordinary(3),pre_state=1,forecasts=forecasts())
        self.assertEqual(result["reason"],"EXPLOIT_TIED_MAXIMUM")

    def test_15_hidden_simulator_information_absent(self):
        self.replay(count=1); record=self.manager.records[-1]["record"]
        for key in ("hidden_regime_available","simulator_law_available",
                    "future_consequence_available","counterfactual_outcomes_available"):
            self.assertIs(record[key],False)

if __name__=="__main__": unittest.main()
