"""Zero-inference tests for the bounded v0.18 operational repair."""
from copy import deepcopy
import hashlib,inspect,json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from .core import digest
from .problem_manager import POLICY as MANAGER_POLICY,ProblemManager,decision_scope
from .repair_followup_suffix import (V015_RESULTS,V017_ROOT,_reconstruct_batch,
    suffix_prefix_observation,verify_v017_evidence)
from .repair_resume import POLICY as REPAIR_POLICY,RepairBroker,RepairStore,request_transport_bytes
from .routing import RoutingError


class FakeClient:
    def __init__(self,response): self.response=response; self.requests=0; self.last=None
    def generate(self,request):
        self.requests+=1; self.last=deepcopy(request); return deepcopy(self.response)


def _repair_store(root:Path,request:dict)->RepairStore:
    key=b"v"*32
    (root/RepairStore.KEY).write_text(key.hex()+"\n")
    (root/RepairStore.STREAM).write_text(""); (root/RepairStore.PRIVATE).write_text("")
    state=dict(version=1,lifecycle_state=None,stream_count=0,stream_head_sha256=None,
        logical_prediction_identity="logical:followup",original_request_sha256=digest(request),
        original_transport_bytes_sha256=hashlib.sha256(request_transport_bytes(request)).hexdigest(),
        original_failed_response_sha256="failed",restart_count=0,reissue_count=0,resumed=False,
        repair_failed=False,source_checkpoint={},source_calls_head_sha256="source",
        created_at="test",updated_at="test")
    RepairStore._write_state(root,key,state); store=RepairStore(root)
    store._append("REQUESTED",dict(original_failure="TimeoutError"))
    grant=dict(explicit_authorization=True,request="EXTERNAL_SERVICE_REPAIR",
        capabilities=REPAIR_POLICY["allowed_capabilities"])
    store.authorize(grant); store.attempted(dict(pid=1)); store.succeeded(dict(
        persistent_process_alive=True,listener_alive=True,health_parse_valid=True,
        model_manifest_sha256=REPAIR_POLICY["expected_model_manifest_sha256"],
        model=REPAIR_POLICY["expected_model"]))
    return store


def _problem(pid,kind="UNRESOLVED_VALUE_TIE"):
    scope=(decision_scope(2,["ADVANCE","RETREAT"]) if kind=="UNRESOLVED_VALUE_TIE" else
           {"kind":"service","service_id":"MODEL_SERVICE"})
    return dict(problem_id=pid,problem_type=kind,scope=scope,owner="MODEL_SERVICE",
        lifecycle_state="OPEN",capability_assessment=("ROUTE_FAILED" if kind==
            "EXTERNAL_SERVICE_PROBLEM" else "CURRENT_OBJECTIVE_CANNOT_DISTINGUISH"),
        requested_capability=("EXTERNAL_SERVICE_REPAIR" if kind=="EXTERNAL_SERVICE_PROBLEM" else None),
        created_decision_sequence=87,route_budgets={},route_request_count=0,probe_evidence={},
        evidence=[],imported_snapshot={},imported_snapshot_sha256=digest({}),history=[],
        **{k:False for k in MANAGER_POLICY["manager_authority"]})


class RepairFollowupSuffixTests(unittest.TestCase):
    def setUp(self): self.tmp=TemporaryDirectory(); self.path=Path(self.tmp.name)
    def tearDown(self): self.tmp.cleanup()

    def test_01_v017_evidence_is_byte_identical(self):
        manifest=json.loads((V017_ROOT/"evidence-manifest.json").read_text())
        for name,expected in manifest["files"].items():
            self.assertEqual(hashlib.sha256((V017_ROOT/name).read_bytes()).hexdigest(),expected)

    def test_02_timeout_preceded_execution_receipt_and_routing(self):
        result=json.loads((V017_ROOT/"results.json").read_text())
        self.assertEqual(result["ordinary_follow_up"]["reason"],"INVALID_MAP_COMPONENT")
        self.assertIsNone(result["ordinary_follow_up"]["receipt_identity"])
        calls=json.loads((V017_ROOT/"call-summary.json").read_text())
        invalid=[x for x in calls["calls"] if not x["valid"]]
        self.assertEqual([(x["role"],x["parse_error"]) for x in invalid],
                         [("joint-next-state","TimeoutError")])
        routes=[json.loads(x) for x in (V017_ROOT/"new-routing-records.jsonl").read_text().splitlines()]
        self.assertFalse(any(":d87:" in json.dumps(x) for x in routes))

    def test_03_reissue_forbidden_if_receipt_exists(self):
        result=RepairBroker.retry_eligibility(external_action=True,receipt_created=True,
            memory_published=True,routing_evidence_added=True,unresolved=False,
            exact_request_bytes=True,explicitly_authorized=True)
        self.assertEqual(result["result"],"FAIL_CLOSED")

    def test_04_reissue_preserves_exact_request_bytes(self):
        request=dict(model=REPAIR_POLICY["expected_model"],system="s",prompt="p",stream=False,
            options={"temperature":.2}); store=_repair_store(self.path,request)
        client=FakeClient(dict(raw_output='{"next_state":1,"consequence":1}',
            transport_error=None,response_metadata={}))
        store.reissue(client,request); self.assertEqual(client.last,request)
        self.assertEqual(hashlib.sha256(request_transport_bytes(client.last)).hexdigest(),
                         store.state["original_transport_bytes_sha256"])

    def test_05_failed_attempt_remains_in_private_history(self):
        request=dict(model=REPAIR_POLICY["expected_model"],system="s",prompt="p",stream=False,options={})
        store=_repair_store(self.path,request)
        store._append_private("ORIGINAL_FAILED_ATTEMPT",dict(transport_attempt=1))
        store.reissue(FakeClient(dict(raw_output='{"next_state":1,"consequence":1}',
            transport_error=None,response_metadata={})),request)
        self.assertEqual([x["record"]["transport_attempt"] for x in store.private],[1,2])

    def test_06_only_one_transport_reissue(self):
        request=dict(model=REPAIR_POLICY["expected_model"],system="s",prompt="p",stream=False,options={})
        store=_repair_store(self.path,request); client=FakeClient(dict(
            raw_output='{"next_state":1,"consequence":1}',transport_error=None,response_metadata={}))
        store.reissue(client,request)
        with self.assertRaises(RoutingError): store.reissue(client,request)

    def test_07_durable_siblings_are_not_regenerated(self):
        source=inspect.getsource(_reconstruct_batch)
        self.assertNotIn(".generate(",source); self.assertIn("logical_prediction_reissued",source)

    def test_08_ordinary_explorer_alone_controls_resume(self):
        from .repair_followup_suffix import RepairedFollowupRuntime
        source=inspect.getsource(RepairedFollowupRuntime)
        self.assertNotIn("explorer=",source); self.assertNotIn("selected_action",source)

    def test_09_option_profile_override_cannot_control_followup(self):
        import horus.repair_followup_suffix as module
        source=inspect.getsource(module)
        self.assertNotIn("OptionProfileIntegrationExplorer",source)
        self.assertIn("option_profile_controlled=False",source)

    def test_10_suffix_comparison_requires_authenticated_receipt(self):
        branches=json.loads(V015_RESULTS.read_text())["branches"]
        receipt=dict(source_identity="s",event_id=1,epoch=1,transaction_id=1,action="HOLD",
            realized_consequence=1,next_state=1)
        row=dict(status="AUTHORIZED",receipt=receipt)
        with self.assertRaises(RoutingError): suffix_prefix_observation(row,set(),branches)
        check=suffix_prefix_observation(row,{("s",1,1,1)},branches)
        self.assertEqual(check["result"],"MATCH")

    def test_11_retained_consequence_stays_labeled_prediction(self):
        branches=json.loads(V015_RESULTS.read_text())["branches"]
        row=dict(status="AUTHORIZED",receipt=dict(source_identity="s",event_id=1,epoch=1,
            transaction_id=1,action="ADVANCE",realized_consequence=1,next_state=2))
        check=suffix_prefix_observation(row,{("s",1,1,1)},branches)
        self.assertEqual(check["retained_consequence_provenance"],"MODEL_FORECAST")

    def test_12_retained_next_state_stays_labeled_prediction(self):
        branches=json.loads(V015_RESULTS.read_text())["branches"]
        row=dict(status="AUTHORIZED",receipt=dict(source_identity="s",event_id=1,epoch=1,
            transaction_id=1,action="RETREAT",realized_consequence=0,next_state=0))
        check=suffix_prefix_observation(row,{("s",1,1,1)},branches)
        self.assertEqual(check["retained_next_state_provenance"],"MODEL_FORECAST")

    def test_13_one_prefix_does_not_validate_profile_globally(self):
        branches=json.loads(V015_RESULTS.read_text())["branches"]
        row=dict(status="AUTHORIZED",receipt=dict(source_identity="s",event_id=1,epoch=1,
            transaction_id=1,action="HOLD",realized_consequence=1,next_state=1))
        check=suffix_prefix_observation(row,{("s",1,1,1)},branches)
        self.assertFalse(check["global_validation_changed"]); self.assertFalse(
            check["full_trajectory_validated"])

    def _manager(self):
        p2=_problem("PR-0002"); p3=_problem("PR-0003"); p3["scope"]=decision_scope(1,["ADVANCE","HOLD"])
        p4=_problem("PR-0004","EXTERNAL_SERVICE_PROBLEM")
        manager=ProblemManager.create(self.path,session_id="s",attempted_decisions=87,
            authorized_executions=55,imported_problems=[p2,p3,p4],edges=[])
        self.addCleanup(manager.close); return manager

    def _request_repair(self,manager):
        caps=["RESTART_MODEL_SERVICE","VERIFY_MODEL_ARTIFACT",
              "REISSUE_UNEXECUTED_PREDICTION_REQUEST"]
        manager.record_operational_repair_event(problem_id="PR-0004",stage="REPAIR_REQUESTED",
            capabilities=caps,details={})
        manager.record_operational_repair_event(problem_id="PR-0004",stage="REPAIR_AUTHORIZED",
            authorization_sha256="a"*64,details={})

    def test_14_pr0004_repair_does_not_rewrite_pr0002(self):
        manager=self._manager(); before=deepcopy(manager.state["problems"]["PR-0002"])
        self._request_repair(manager)
        manager.record_operational_repair_event(problem_id="PR-0004",stage="REPAIR_ATTEMPTED",details={})
        self.assertEqual(manager.state["problems"]["PR-0002"],before)

    def test_15_repair_records_never_enter_memory_or_training(self):
        manager=self._manager(); self._request_repair(manager)
        history=manager.state["problems"]["PR-0004"]["history"][-2:]
        self.assertTrue(all(not x["memory_mutated"] and not x["training_target_created"] and
                            not x["repair_is_behavioral_evidence"] for x in history))


if __name__=="__main__": unittest.main()
