"""Zero-inference tests for the bounded v0.14 continuation route."""
from copy import deepcopy
import hashlib,inspect,json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from .core import digest
from .one_step_value import compare_pairs,downstream_forecasts,grounded_transitions
from .problem_manager import POLICY,ProblemManager,decision_scope
from .problem_ownership_run import _plain_rows
from .routing import RoutingError

def problem(pid,state,actions,assessment,request):
    snapshot=dict(problem_id=pid,problem_type="UNRESOLVED_VALUE_TIE",state=state,
        candidate_actions=list(actions),status="REASSESSED",created_decision_sequence=1)
    evidence={a:[dict(action=a,realized_consequence=1,
        realized_next_state=(3 if a=="ADVANCE" else 1),receipt_identity=["s",1,1,1],
        receipt_is_authenticated=True)] for a in actions}
    return dict(problem_id=pid,problem_type="UNRESOLVED_VALUE_TIE",
        scope=decision_scope(state,list(actions)),owner="EVIDENCE_COVERAGE",
        lifecycle_state="REASSESSED",capability_assessment=assessment,
        requested_capability=request,created_decision_sequence=1,
        route_budgets={},route_request_count=0,probe_evidence=evidence,evidence=[],
        imported_snapshot=snapshot,imported_snapshot_sha256=digest(snapshot),
        history=[{"lifecycle_state":"REASSESSED","decision_sequence":1}],
        **{k:False for k in POLICY["manager_authority"]})

class FakeStore:
    def __init__(self): self.rows=[]; self.sequence=0
    def imported_history(self): return []
    def append(self,stream,kind,record):
        self.sequence+=1
        row={"sequence":self.sequence,"stream":stream,"kind":kind,"record":deepcopy(record)}
        self.rows.append(row); return row

class FakeClient:
    model_id="fake"; horus_model_identity={"generation":0}
    def __init__(self,value): self.value=value; self.requests=[]
    def generate(self,request):
        self.requests.append(deepcopy(request))
        return {"raw_output":json.dumps({"consequence":self.value}),
                "transport_error":None,"response_metadata":{}}

class FakeRouting:
    def __init__(self): self.lookups=[]
    def preview(self,state,action):
        self.lookups.append((state,action)); return {"selected_specialist":"G2"}

class OneStepValueTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory(); self.root=Path(self.tmp.name)
        p2=problem("PR-0002",2,("ADVANCE","RETREAT"),
            "CURRENT_OBJECTIVE_CANNOT_DISTINGUISH","LONGER_HORIZON_VALUE")
        p3=problem("PR-0003",1,("ADVANCE","HOLD"),None,None)
        self.manager=ProblemManager.create(self.root,session_id="s",attempted_decisions=85,
            authorized_executions=54,imported_problems=[p2,p3],edges=[])
    def tearDown(self): self.manager.close(); self.tmp.cleanup()

    def test_01_route_requires_objective_gap(self):
        self.manager.state["problems"]["PR-0002"]["capability_assessment"]="MORE_EVIDENCE_REQUIRED"
        with self.assertRaises(RoutingError): self.manager.authorize_one_step("PR-0002","a"*64)

    def test_02_route_requires_explicit_authorization(self):
        with self.assertRaises(RoutingError):
            self.manager.record_one_step_evaluation(problem_id="PR-0002",
                outcome="ONE_STEP_DISTINGUISHES",selected_action="ADVANCE",evaluation={})

    def test_03_primary_value_dominates_secondary(self):
        r=compare_pairs({"A":1,"B":0},{"A":-1,"B":1})
        self.assertEqual((r["selected_action"],r["secondary_consulted"]),("A",False))

    def test_04_secondary_only_consulted_on_primary_tie(self):
        r=compare_pairs({"A":1,"B":1},{"A":0,"B":1})
        self.assertEqual((r["selected_action"],r["secondary_consulted"]),("B",True))

    def test_05_authenticated_continuation_required(self):
        p=deepcopy(self.manager.state["problems"]["PR-0002"])
        p["probe_evidence"]["ADVANCE"][0]["receipt_is_authenticated"]=False
        with self.assertRaises(RoutingError): grounded_transitions(p)

    def test_06_predicted_next_state_cannot_replace_receipt(self):
        p=deepcopy(self.manager.state["problems"]["PR-0002"])
        p["probe_evidence"]["ADVANCE"]=[]; p["imported_snapshot"]["initial_forecasts"]={"ADVANCE":{"next_state":3}}
        with self.assertRaises(RoutingError): grounded_transitions(p)

    def test_07_downstream_interface_is_consequence_only(self):
        result,store,_,_=self._downstream()
        intents=[r for r in store.rows if r["kind"]=="REQUEST_INTENT"]
        self.assertEqual(len(intents),12)
        self.assertTrue(all(r["record"]["consequence_only"] and
            not r["record"]["predicted_next_state_present"] for r in intents))
        self.assertTrue(all("next_state" not in json.loads(r["record"]["request"]["prompt"])
                            for r in intents))

    def test_08_routing_lookup_is_state_and_action_local(self):
        _,_,routing,_=self._downstream()
        self.assertEqual(routing.lookups,[(s,a) for s in (3,1) for a in ("ADVANCE","HOLD","RETREAT")])

    def test_09_exactly_one_extra_horizon(self):
        result,_,_,_=self._downstream()
        self.assertEqual((result["horizon_layers"],result["calls"],
                          result["predicted_next_state_inputs"]),(1,12,0))

    def test_10_no_recursive_calls(self):
        source=inspect.getsource(downstream_forecasts)
        self.assertNotIn("downstream_forecasts(",source[source.index("def downstream_forecasts")+25:])
        self.assertEqual(self._downstream()[0]["recursive_calls"],0)

    def test_11_secondary_tie_has_no_choice(self):
        r=compare_pairs({"A":1,"B":1},{"A":0,"B":0})
        self.assertEqual((r["outcome"],r["selected_action"]),("STILL_TIED_AT_ONE_STEP",None))

    def test_12_exhaustion_requests_but_cannot_grant_deeper_horizon(self):
        self.manager.authorize_one_step("PR-0002","a"*64)
        self.manager.record_one_step_evaluation(problem_id="PR-0002",
            outcome="STILL_TIED_AT_ONE_STEP",selected_action=None,evaluation={})
        p=self.manager.state["problems"]["PR-0002"]
        self.assertEqual(p["requested_capability"],"DEEPER_HORIZON_VALUE")
        self.assertNotIn("deeper_horizon_value",p["route_budgets"])

    def test_13_problem_history_is_append_only(self):
        before=deepcopy(self.manager.state["problems"]["PR-0002"]["history"])
        self.manager.authorize_one_step("PR-0002","a"*64)
        self.assertEqual(self.manager.state["problems"]["PR-0002"]["history"][:len(before)],before)

    def test_14_pr0003_is_unaffected(self):
        before=deepcopy(self.manager.state["problems"]["PR-0003"])
        self.manager.authorize_one_step("PR-0002","a"*64)
        self.manager.record_one_step_evaluation(problem_id="PR-0002",
            outcome="ONE_STEP_DISTINGUISHES",selected_action="ADVANCE",evaluation={})
        self.assertEqual(self.manager.state["problems"]["PR-0003"],before)

    def test_15_serializer_fix_does_not_modify_v013_evidence(self):
        root=Path(__file__).resolve().parents[1]/"research/problem-ownership-v0"
        manifest=__import__("json").loads((root/"evidence-manifest.json").read_text())
        for name,expected in manifest["files"].items():
            self.assertEqual(hashlib.sha256((root/name).read_bytes()).hexdigest(),expected)
        row=dict(prediction_batch_sequence=84,state=1,status="AUTHORIZED",
            explorer={"action":"ADVANCE","reason":"x","problem_id":"PR-0003",
                      "capability_assessment":None},receipt=None,
            forecasts={"ADVANCE":{"valid":True}})
        self.assertEqual(_plain_rows([row])[0]["pre_state"],1)

    @staticmethod
    def _downstream():
        store=FakeStore(); routing=FakeRouting()
        clients={"G2":FakeClient(1),"G3":FakeClient(0)}
        return (downstream_forecasts(store,clients,routing,[3,1],"test"),
                store,routing,clients)

if __name__=="__main__": unittest.main()
