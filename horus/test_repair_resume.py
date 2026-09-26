"""Zero-inference checks for the v0.10 bounded operational repair route."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest

from .capability_gap import CapabilityAssessor, CapabilityGapStore, initialize_capability_gap_registry
from .repair_resume import (POLICY, RepairBroker, RepairStore,
                            request_transport_bytes)
from .routing import RoutingError
from .test_capability_gap import FakeStore, SOURCE, forecasts, ordinary


class FakeClient:
    def __init__(self,response): self.response=response; self.requests=0; self.last=None
    def generate(self,request):
        self.requests+=1; self.last=deepcopy(request); return deepcopy(self.response)


def repair_store(root:Path,request:dict)->RepairStore:
    key=b"r"*32
    (root/RepairStore.KEY).write_text(key.hex()+"\n")
    (root/RepairStore.STREAM).write_text("")
    (root/RepairStore.PRIVATE).write_text("")
    state=dict(version=1,lifecycle_state=None,stream_count=0,stream_head_sha256=None,
        logical_prediction_identity="logical:1",original_request_sha256=__import__(
            "horus.core",fromlist=["digest"]).digest(request),
        original_transport_bytes_sha256=__import__("hashlib").sha256(
            request_transport_bytes(request)).hexdigest(),
        original_failed_response_sha256="failed",restart_count=0,reissue_count=0,
        resumed=False,repair_failed=False,source_checkpoint={},
        source_calls_head_sha256="source",created_at="test",updated_at="test")
    RepairStore._write_state(root,key,state)
    store=RepairStore(root)
    store._append("REQUESTED",dict(external_action_after_failure=False,
        receipt_after_failure=False,memory_after_failure=False,
        routing_evidence_after_failure=False,decision_unresolved=True,
        exact_request_bytes_retained=True))
    grant=dict(explicit_authorization=True,request="EXTERNAL_SERVICE_REPAIR",
               capabilities=POLICY["allowed_capabilities"])
    store.authorize(grant); store.attempted(dict(pid=7)); store.succeeded(dict(
        persistent_process_alive=True,listener_alive=True,health_parse_valid=True,
        model_manifest_sha256=POLICY["expected_model_manifest_sha256"],
        model=POLICY["expected_model"]))
    return store


class RepairResumeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory(); self.path=Path(self.tmp.name)
        self.request=dict(model=POLICY["expected_model"],system="s",prompt="p",
                          stream=False,options={"temperature":0.2})
    def tearDown(self): self.tmp.cleanup()

    def test_01_timeout_before_execution_can_request_repair(self):
        row=RepairBroker.retry_eligibility(external_action=False,receipt_created=False,
            memory_published=False,routing_evidence_added=False,unresolved=True,
            exact_request_bytes=True,explicitly_authorized=True)
        self.assertTrue(row["eligible"])

    def test_02_timeout_after_execution_cannot_reissue(self):
        row=RepairBroker.retry_eligibility(external_action=True,receipt_created=True,
            memory_published=True,routing_evidence_added=True,unresolved=False,
            exact_request_bytes=True,explicitly_authorized=True)
        self.assertEqual(row["result"],"FAIL_CLOSED")

    def test_03_exact_request_bytes_preserved_across_reissue(self):
        store=repair_store(self.path,self.request); client=FakeClient(dict(
            raw_output='{"next_state":2,"consequence":0}',transport_error=None,
            response_metadata={}))
        result=store.reissue(client,self.request)
        self.assertEqual(client.last,self.request); self.assertIsNotNone(result["parsed"])

    def test_04_first_failed_attempt_remains_in_history(self):
        store=repair_store(self.path,self.request)
        store._append_private("ORIGINAL_FAILED_ATTEMPT",dict(transport_attempt=1,
            status="MODEL_SERVICE_FAILURE"))
        client=FakeClient(dict(raw_output='{"next_state":2,"consequence":0}',
            transport_error=None,response_metadata={}))
        store.reissue(client,self.request)
        self.assertEqual([r["record"]["transport_attempt"] for r in store.private],[1,2])

    def test_05_only_one_repair_and_reissue_allowed(self):
        store=repair_store(self.path,self.request); client=FakeClient(dict(
            raw_output='{"next_state":2,"consequence":0}',transport_error=None,
            response_metadata={}))
        store.reissue(client,self.request)
        with self.assertRaises(RoutingError): store.reissue(client,self.request)

    def _failed_gap(self):
        root=self.path/"registry"; root.mkdir()
        shutil.copy2(SOURCE/"problem-route-registry.json",root/"problem-route-registry.json")
        initialize_capability_gap_registry(root,SOURCE/"problem-route-report.json")
        report=json.loads((SOURCE/"problem-route-report.json").read_text())
        session=FakeStore(report["final_checkpoint"]["session_id"]); gap=CapabilityGapStore(root)
        first=gap.prepare(store=session,ordinary_decision=ordinary(55),pre_state=2,
                          forecasts=forecasts())
        session.checkpoint["attempted_decisions"]+=1; session.records["events"].append({})
        gap.complete(store=session,row=dict(prediction_batch_sequence=55,status="AUTHORIZED",
            receipt=dict(source_identity="s",event_id=1,epoch=1,transaction_id=1,
                         action=first["action"],realized_consequence=1,next_state=3),
            routing_evidence=dict(evidence_sequence=51)))
        second=gap.prepare(store=session,ordinary_decision=ordinary(56,valid=False),
                           pre_state=2,forecasts=forecasts(valid=False))
        session.checkpoint["attempted_decisions"]+=1
        gap.complete(store=session,row=dict(prediction_batch_sequence=56,status="ABSTAINED"))
        return gap,session

    def _resume(self,gap,session):
        return gap.resume_after_authorized_repair(store=session,repair_reference=dict(
            lifecycle_state="REPAIR_SUCCEEDED",repair_event_sha256="r",
            logical_prediction_identity="l",original_request_sha256="q",
            authorization_sha256="a"))

    def test_06_repaired_service_can_resume_unresolved_problem(self):
        gap,session=self._failed_gap(); self._resume(gap,session)
        self.assertIsNone(gap.state["terminal_classification"]); gap.close()

    def test_07_repair_event_cannot_enter_memory(self):
        gap,session=self._failed_gap(); before=len(session.records["events"])
        row=self._resume(gap,session)
        self.assertEqual(len(session.records["events"]),before)
        self.assertFalse(row["memory_mutated"]); gap.close()

    def test_08_repair_event_cannot_become_training_target(self):
        gap,session=self._failed_gap(); row=self._resume(gap,session)
        self.assertFalse(row["training_target_created"]); gap.close()

    def test_09_duplicate_receipt_cannot_arise_from_repair(self):
        gap,session=self._failed_gap(); before=len(session.records["events"])
        self._resume(gap,session)
        self.assertEqual(len(session.records["events"]),before); gap.close()

    def test_10_problem_budget_survives_repair(self):
        gap,session=self._failed_gap(); self._resume(gap,session)
        self.assertEqual(gap.state["current_problem"]["probe_count"],1); gap.close()

    def test_11_previously_grounded_advance_is_not_repeated(self):
        gap,session=self._failed_gap(); row=self._resume(gap,session)
        self.assertFalse(row["advance_probe_repeated"]); gap.close()

    def test_12_missing_retreat_probe_can_continue(self):
        gap,session=self._failed_gap(); self._resume(gap,session)
        d=gap.prepare(store=session,ordinary_decision=ordinary(57),pre_state=2,
                      forecasts=forecasts())
        self.assertEqual(d["action"],"RETREAT"); gap.close()

    def test_13_equal_grounded_tied_outcomes_emit_objective_gap(self):
        gap,session=self._failed_gap(); self._resume(gap,session)
        d=gap.prepare(store=session,ordinary_decision=ordinary(57),pre_state=2,
                      forecasts=forecasts())
        session.checkpoint["attempted_decisions"]+=1; session.records["events"].append({})
        gap.complete(store=session,row=dict(prediction_batch_sequence=57,status="AUTHORIZED",
            receipt=dict(source_identity="s",event_id=2,epoch=2,transaction_id=2,
                         action=d["action"],realized_consequence=1,next_state=1),
            routing_evidence=dict(evidence_sequence=52)))
        terminal=gap.prepare(store=session,ordinary_decision=ordinary(58),pre_state=2,
                             forecasts=forecasts())
        self.assertEqual(terminal["capability_assessment"],
                         "CURRENT_OBJECTIVE_CANNOT_DISTINGUISH"); gap.close()

    def test_14_unequal_outcomes_emit_value_tie_resolved(self):
        gap,session=self._failed_gap(); self._resume(gap,session)
        problem=gap.state["current_problem"]
        problem["problem_probe_history"]["RETREAT"].append(dict(realized_consequence=-1))
        problem["probe_count"]=2
        decision=gap.prepare(store=session,ordinary_decision=ordinary(57,tie=False),
                             pre_state=2,forecasts=forecasts(tie=False))
        self.assertEqual(decision["capability_assessment"],"VALUE_TIE_RESOLVED"); gap.close()

    def test_15_longer_horizon_value_remains_external_only(self):
        row=CapabilityAssessor().request("LONGER_HORIZON_VALUE")
        self.assertEqual(row["authority_status"],"REQUEST_REQUIRES_EXTERNAL_APPROVAL")
        self.assertFalse(row["can_execute"])

    def test_16_failed_second_transport_produces_repair_failed(self):
        store=repair_store(self.path,self.request); result=store.reissue(FakeClient(dict(
            raw_output=None,transport_error="TimeoutError",response_metadata={})),self.request)
        self.assertIsNone(result["parsed"]); self.assertEqual(store.state[
            "lifecycle_state"],"REPAIR_FAILED")


if __name__=="__main__": unittest.main()
