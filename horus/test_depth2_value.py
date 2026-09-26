"""Zero-inference tests for the finite v0.15 depth-2 route."""
from copy import deepcopy
import inspect,json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from .core import digest
from .depth2_value import analyze_max_compression,compare_trajectories,evaluate_depth2
from .one_step_value import grounded_transitions
from .problem_manager import POLICY,ProblemManager,decision_scope
from .routing import RoutingError

class Store:
    def __init__(self): self.rows=[]; self.sequence=0
    def imported_history(self): return []
    def append(self,stream,kind,record):
        self.sequence+=1; row={"sequence":self.sequence,"kind":kind,"record":deepcopy(record)}
        self.rows.append(row); return row

class Joint:
    model_id="joint"
    def generate(self,request):
        state=json.loads(request["prompt"])["state"]
        return {"raw_output":json.dumps({"next_state":state,"consequence":0}),
                "transport_error":None,"response_metadata":{}}

class Consequence:
    def __init__(self,name,value):
        self.model_id=name; self.value=value; self.horus_model_identity={"specialist_id":name}
    def generate(self,request):
        return {"raw_output":json.dumps({"consequence":self.value}),
                "transport_error":None,"response_metadata":{}}

class Routing:
    def preview(self,state,action): return {"selected_specialist":"G2"}

def imported_problem(pid,request):
    scope=decision_scope(2,["ADVANCE","RETREAT"])
    return dict(problem_id=pid,problem_type="UNRESOLVED_VALUE_TIE",scope=scope,
        owner="EVIDENCE_COVERAGE",lifecycle_state="REASSESSED",
        capability_assessment="CURRENT_OBJECTIVE_CANNOT_DISTINGUISH",requested_capability=request,
        created_decision_sequence=1,route_budgets={},route_request_count=0,
        probe_evidence={"ADVANCE":[dict(realized_consequence=1,realized_next_state=3,
            receipt_identity=["s",1,1,1],receipt_is_authenticated=True)],
            "RETREAT":[dict(realized_consequence=1,realized_next_state=1,
            receipt_identity=["s",1,2,1],receipt_is_authenticated=True)]},
        evidence=[],imported_snapshot={},imported_snapshot_sha256=digest({}),
        history=[],**{k:False for k in POLICY["manager_authority"]})

class Depth2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v14=json.loads((Path(__file__).resolve().parents[1]/
            "research/bounded-longer-horizon-v0/results.json").read_text())
    def evaluate(self):
        store=Store(); transitions=self.v14["grounded_transitions"]
        result=evaluate_depth2(store,Joint(),{"G2":Consequence("G2",1),
            "G3":Consequence("G3",0)},Routing(),transitions,"test")
        return result,store
    def test_01_v014_result_unchanged(self):
        self.assertEqual(self.v14["pairs"],{"ADVANCE":[1,1],"RETREAT":[1,1]})
    def test_02_all_second_actions_examined(self):
        result,_=self.evaluate()
        self.assertEqual({k:len(v) for k,v in result["candidates"].items()},
                         {"ADVANCE":3,"RETREAT":3})
    def test_03_immediate_consequence_is_primary(self):
        r=compare_trajectories({"A":[{"second_action":"x","sequence":[1,-1,-1]}],
            "B":[{"second_action":"x","sequence":[0,1,1]}]})
        self.assertEqual(r["selected_action"],"A")
    def test_04_second_consequence_dominates_third(self):
        r=compare_trajectories({"A":[{"second_action":"x","sequence":[1,1,-1]}],
            "B":[{"second_action":"x","sequence":[1,0,1]}]})
        self.assertEqual(r["selected_action"],"A")
    def test_05_no_sum_or_discount(self):
        source=inspect.getsource(compare_trajectories)
        self.assertNotIn("sum(",source); self.assertNotIn("discount",source)
    def test_06_authenticated_first_continuation_required(self):
        p=imported_problem("PR-0002","DEEPER_HORIZON_VALUE")
        p["probe_evidence"]["ADVANCE"][0]["receipt_is_authenticated"]=False
        with self.assertRaises(RoutingError): grounded_transitions(p)
    def test_07_predicted_second_state_labeled_predicted(self):
        result,_=self.evaluate()
        self.assertTrue(all(r["next_state_provenance"]=="MODEL_FORECAST"
                            for r in result["second_branches"]))
    def test_08_consequence_request_has_no_predicted_next_state_field(self):
        _,store=self.evaluate(); intents=[r for r in store.rows if r["kind"]=="REQUEST_INTENT"
            and "consequence" in r["record"]["role"]]
        self.assertTrue(all("predicted_next_state" not in r["record"]["request"]["prompt"]
                            for r in intents))
    def test_09_exactly_depth_two(self):
        self.assertEqual(self.evaluate()[0]["horizon_depth"],2)
    def test_10_no_recursion_beyond_registered_depth(self):
        result,_=self.evaluate(); self.assertEqual(result["recursive_calls"],0)
        source=inspect.getsource(evaluate_depth2)
        self.assertNotIn("evaluate_depth2(",source[source.index("def evaluate_depth2")+20:])
    def test_11_exact_identical_requests_deduplicate(self):
        result,_=self.evaluate()
        self.assertEqual((result["calls"],len(result["deduplicated_requests"])),(18,12))
        self.assertTrue(all("exact_request_sha256" in r for r in result["deduplicated_requests"]))
    def test_12_tie_makes_no_arbitrary_choice(self):
        row={"second_action":"x","sequence":[1,1,1]}
        r=compare_trajectories({"A":[row],"B":[row]})
        self.assertEqual((r["outcome"],r["selected_action"]),("STILL_TIED_AT_DEPTH2",None))
    def test_13_pr0003_unchanged(self):
        with TemporaryDirectory() as d:
            p2=imported_problem("PR-0002","DEEPER_HORIZON_VALUE")
            p3=imported_problem("PR-0003",None); p3["scope"]=decision_scope(1,["ADVANCE","HOLD"])
            with ProblemManager.create(Path(d),session_id="s",attempted_decisions=85,
                    authorized_executions=54,imported_problems=[p2,p3],edges=[]) as manager:
                before=deepcopy(manager.state["problems"]["PR-0003"])
                manager.authorize_depth2("PR-0002","a"*64)
                manager.validate_depth2_design("PR-0002","b"*64)
                manager.record_depth2_evaluation(problem_id="PR-0002",outcome="STILL_TIED_AT_DEPTH2",
                    selected_action=None,evaluation={})
                self.assertEqual(manager.state["problems"]["PR-0003"],before)
    def test_14_no_hidden_simulator_law(self):
        result,store=self.evaluate(); self.assertFalse(result["hidden_simulator_law_present"])
        self.assertTrue(all(r["record"].get("hidden_simulator_law_present") is False
            for r in store.rows if r["kind"]=="REQUEST_INTENT" and r["record"]["role"]=="depth2-next-state"))
    def test_15_route_has_zero_behavioral_authority(self):
        result,_=self.evaluate(); self.assertFalse(result["behavioral_authority"])
        source=inspect.getsource(evaluate_depth2)
        self.assertNotIn("execute_autonomous",source)
        self.assertNotIn("ProblemOwnershipRuntime",source)

if __name__=="__main__": unittest.main()
