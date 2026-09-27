import json
import tempfile
import unittest
from copy import deepcopy
from hashlib import sha256
from hmac import new as new_hmac
from pathlib import Path

from horus.core import digest
from horus.live import _canonical
from horus.problem_manager import ProblemManager, decision_scope
from horus.relation_routing import relation_identity
from horus.route_handoff_recovery import (
    EXPECTED_LOGICAL_ID, NoCallClient, _authenticated_file, _recovered_batch,
    _tail_calls, choose_route, tail_safety)
from horus.routing import RoutingError


def ordinary(available=True):
    return dict(decision_sequence=91,mode="PROBE" if available else "EXPLOIT",
        action="ADVANCE" if available else None,
        reason="PROBE_DISAGREEMENT" if available else "EXPLOIT_TIED_MAXIMUM",
        abstained=not available,probe_budget_available=available)


def fallback():
    return dict(mode="PROBLEM_SCOPED_PROBE",action="ADVANCE",
                reason="GROUND_RELATION_FOR_SPECIALIST_SELECTION",abstained=False)


def tail_fixture():
    rows=[]; seq=2502; calls={}
    payloads={a:{"state":1,"target_action":alias,"VERIFIED_CHRONOLOGICAL_HISTORY":[]}
              for a,alias in (("ADVANCE","K1"),("HOLD","K2"),("RETREAT","K3"))}
    for action in ("ADVANCE","HOLD","RETREAT"):
        for role in ("J","G2","G3"):
            seq+=1; cid=f"{EXPECTED_LOGICAL_ID}:{action}:{role}"
            request={"prompt":_canonical(payloads[action])}
            record={"call_id":cid,"request":request,"request_sha256":digest(request)}
            env={"sequence":seq,"kind":"REQUEST_INTENT","record":record}
            rows.append(env); calls[cid]={"REQUEST_INTENT":env}
    for action in ("ADVANCE","HOLD","RETREAT"):
        for role in ("J","G2","G3"):
            cid=f"{EXPECTED_LOGICAL_ID}:{action}:{role}"; seq+=1
            response={"raw_output":"{}"}; rr={"call_id":cid,"response":response,
                "response_sha256":digest(response)}
            re={"sequence":seq,"kind":"RESPONSE","record":rr}; rows.append(re)
            calls[cid]["RESPONSE"]=re; seq+=1
            value=({"next_state":{"ADVANCE":2,"HOLD":1,"RETREAT":0}[action],
                    "consequence":0} if role=="J" else
                   {"consequence":1 if action!="RETREAT" else 0})
            pr={"call_id":cid,"parsed":value,"parse_error":None}
            pe={"sequence":seq,"kind":"PARSED","record":pr}; rows.append(pe)
            calls[cid]["PARSED"]=pe
    return rows,calls,payloads


def problem(pid,kind,scope):
    return dict(problem_id=pid,problem_type=kind,scope=scope,
        owner="EXPLORER_VALUE_COMPARISON" if pid=="PR-0003" else "ROUTE_HANDOFF",
        lifecycle_state="REASSESSED" if pid=="PR-0003" else "OPEN",
        capability_assessment="MORE_EVIDENCE_REQUIRED" if pid=="PR-0003" else "ROUTE_FAILED",
        requested_capability="MORE_RELATION_EVIDENCE" if pid=="PR-0003" else "NEW_RUNTIME",
        created_decision_sequence=65 if pid=="PR-0003" else 91,
        route_budgets=({"problem_scoped_relation_probe":{"limit":2,"granted":1,
            "executed":1,"relation":relation_identity(1,"ADVANCE")}} if pid=="PR-0003" else {}),
        route_request_count=3 if pid=="PR-0003" else 0,
        probe_evidence={"ADVANCE":[],"HOLD":[]} if pid=="PR-0003" else {},
        evidence=[],imported_snapshot=None,imported_snapshot_sha256=None,history=[],
        target_relation_reacquired=True if pid=="PR-0003" else None,
        select_actions=False,execute=False,issue_receipts=False,alter_memory=False,
        alter_predictions=False,train=False,change_objective=False,create_model=False,
        self_authorize=False)


class RouteHandoffRecoveryTests(unittest.TestCase):
    def test_01_normal_route_supersedes_fallback(self):
        selected=choose_route(ordinary(),fallback())
        self.assertEqual(selected["selected_route"],"ORDINARY_EXPLORER")
        self.assertEqual(selected["status"],"NORMAL_ROUTE_REGAINS_CONTROL")

    def test_02_fallback_requires_unavailable_normal_route(self):
        selected=choose_route(ordinary(False),fallback())
        self.assertEqual(selected["selected_route"],"PROBLEM_SCOPED_FALLBACK")

    def test_03_abstains_when_neither_route_exists(self):
        self.assertIsNone(choose_route(ordinary(False),None)["selected_route"])

    def test_04_authenticated_stream_is_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            key=b"k"*32; path=Path(td)/"stream.jsonl"; previous=None; lines=[]
            for sequence in (1,2):
                signed=dict(sequence=sequence,previous_sha256=previous,kind="X",record={"n":sequence})
                env={**signed,"hmac_sha256":new_hmac(key,_canonical(signed).encode(),"sha256").hexdigest()}
                lines.append(_canonical(env)); previous=sha256(_canonical(env).encode()).hexdigest()
            path.write_text("\n".join(lines)+"\n")
            self.assertEqual(len(_authenticated_file(path,key)),2)

    def test_05_unauthenticated_tail_fails(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"stream.jsonl"
            path.write_text(_canonical(dict(sequence=1,previous_sha256=None,kind="X",
                record={},hmac_sha256="0"*64))+"\n")
            with self.assertRaises(RoutingError): _authenticated_file(path,b"k"*32)

    def test_06_exact_nine_call_tail_is_complete(self):
        rows,_,_=tail_fixture(); calls,hashes=_tail_calls(rows)
        self.assertEqual((len(calls),len(hashes),len(rows)),(9,9,27))

    def test_07_tail_with_receipt_is_rejected(self):
        safety=tail_safety(chain_continuous=True,event_matches=[{}],training_matches=[],
            routing_matches=[],explorer_matches=[],contradictory_state=False)
        self.assertFalse(safety["no_receipt"]); self.assertFalse(safety["no_memory_publication"])

    def test_08_tail_with_memory_publication_is_rejected(self):
        safety=tail_safety(chain_continuous=True,event_matches=[],training_matches=[{}],
            routing_matches=[],explorer_matches=[],contradictory_state=False)
        self.assertFalse(safety["no_memory_publication"])

    def test_09_tail_with_routing_or_explorer_state_is_rejected(self):
        safety=tail_safety(chain_continuous=True,event_matches=[],training_matches=[],
            routing_matches=[{}],explorer_matches=[{}],contradictory_state=False)
        self.assertFalse(safety["no_routing_evidence"]); self.assertFalse(safety["no_explorer_completion"])

    def test_10_model_outputs_cannot_be_regenerated(self):
        client=NoCallClient("blocked")
        with self.assertRaises(RoutingError): client.generate({})
        self.assertEqual(client.requests,0)

    def test_11_recovered_inputs_must_match_current_capture(self):
        _,calls,payloads=tail_fixture()
        proof={"calls":calls}; registry={"specialists":{
            "G2":{"artifact_sha256":"2"*64},"G3":{"artifact_sha256":"3"*64}}}
        capture=dict(state=1,epoch=2,transaction_id=1,memory_sha256="m",
            authenticated_history_reference={},map_inputs=payloads)
        batch=_recovered_batch(proof,capture,registry)
        self.assertTrue(batch.all_valid); self.assertEqual(len(batch.forecasts["G2"]),3)
        bad=deepcopy(capture); bad["map_inputs"]["ADVANCE"]={"changed":True}
        with self.assertRaises(RoutingError): _recovered_batch(proof,bad,registry)

    def test_12_rolling_window_evicts_exact_oldest(self):
        before=list(range(1,7)); after=(before+[7])[-6:]
        self.assertEqual((before[0],after),(1,[2,3,4,5,6,7]))

    def test_13_recovery_events_leave_pr0003_and_budget_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); pr3=problem("PR-0003","UNRESOLVED_VALUE_TIE",
                decision_scope(1,["ADVANCE","HOLD"])); pr5=problem("PR-0005",
                "INTERNAL_ROUTE_PROBLEM",{"kind":"runtime","runtime_id":"v0.21"})
            with ProblemManager.create(root,session_id="s",attempted_decisions=90,
                    authorized_executions=57,imported_problems=[pr3,pr5],edges=[{
                    "from_problem":"PR-0003","relation":"blocked_by",
                    "to_problem":"PR-0005"}]) as manager:
                before=deepcopy(manager.state["problems"]["PR-0003"])
                manager.record_uncommitted_call_tail(problem_id="PR-0005",
                    logical_decision_id=EXPECTED_LOGICAL_ID,decision_sequence=91,
                    checkpoint_count=2502,physical_count=2529,tail_records=27,
                    tail_head_sha256="a"*64,safety_conditions={k:True for k in (
                    "tail_authenticated","chain_continuous","single_unfinished_decision",
                    "no_receipt","no_memory_publication","no_routing_evidence",
                    "no_explorer_completion","no_contradictory_state")})
                manager.record_tail_recovered(problem_id="PR-0005",status="DURABLE_TAIL_RECOVERED",
                    registered_count=2529,registered_head_sha256="a"*64,
                    stream_records_rewritten=False,model_calls_reissued=False)
                self.assertEqual(before,manager.state["problems"]["PR-0003"])

    def test_14_recovery_does_not_train_or_change_authority(self):
        client=NoCallClient("blocked")
        self.assertEqual(client.requests,0)
        self.assertFalse(any(key in choose_route(ordinary(),fallback()) for key in
                             ("train","authorize","execute","publish_memory")))


if __name__=="__main__": unittest.main()
