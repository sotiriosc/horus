"""One-reissue repair and exact ordinary follow-up resume for Horus v0.18."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from hashlib import sha256
from hmac import new as new_hmac
import json
import os
from pathlib import Path
import secrets
import shutil
import signal
import subprocess
import time
import urllib.request

from experiments.base_framework_v0.framework import ACTION_ORDER

from .core import GroundedObservation, MapForecast, digest
from .grounded_exploration import ExplorerConfidenceStore, GroundedExplorationRuntime
from .grounded_learning import atomic_json, file_hash
from .live import CONSEQUENCE_SYSTEM, JOINT_SYSTEM, ModelClient, SessionStore, _canonical, _now
from .problem_manager import ProblemManager
from .relation_routing import RelationEvidenceStore, relation_routed_clients
from .repair_resume import (MANIFEST_PATH, POLICY as REPAIR_POLICY, RepairBroker,
                            RepairStore, request_transport_bytes, service_health)
from .routing import RoutedForecastBatch, RoutingError


POLICY_PATH=Path(__file__).with_name("repair_followup_suffix_policy.json")
V017_ROOT=Path(__file__).resolve().parents[1]/"research/option-profile-behavioral-integration-v0"
V015_RESULTS=Path(__file__).resolve().parents[1]/"research/deeper-horizon-route-design-v0/results.json"


def load_policy()->dict:
    policy=json.loads(POLICY_PATH.read_text())
    for name,expected in policy["frozen_sha256"].items():
        if file_hash(Path(__file__).with_name(name))!=expected:
            raise RoutingError(f"frozen v0.18 file changed: {name}")
    for path_key,hash_key in (("preregistration_path","preregistration_sha256"),
                              ("authorization_path","authorization_sha256")):
        if file_hash(Path(policy[path_key]))!=policy[hash_key]:
            raise RoutingError(f"v0.18 {path_key} changed")
    if policy["maximum_total_live_model_calls"]!=2 or policy["maximum_reissues"]!=1:
        raise RoutingError("v0.18 live bounds changed")
    return policy


def verify_v017_evidence(policy:dict)->None:
    manifest_path=V017_ROOT/"evidence-manifest.json"
    if file_hash(manifest_path)!=policy["source_manifest_sha256"]:
        raise RoutingError("v0.17 evidence manifest changed")
    manifest=json.loads(manifest_path.read_text())
    for name,expected in manifest["files"].items():
        if file_hash(V017_ROOT/name)!=expected:
            raise RoutingError(f"v0.17 evidence changed: {name}")


def _decision_calls(session:SessionStore,policy:dict)->dict:
    prefix=policy["failed_logical_prediction_identity"].rsplit(":RETREAT:J",1)[0]
    calls={}
    for row in session.records["calls"]:
        call_id=row["record"].get("call_id","")
        if call_id.startswith(prefix+":"):
            calls.setdefault(call_id,{})[row["kind"]]=row
    return calls


def repair_eligibility(session_path:Path,registry_root:Path,policy:dict)->dict:
    verify_v017_evidence(policy)
    with SessionStore(session_path,True) as session,RelationEvidenceStore(registry_root) as routing, \
            ExplorerConfidenceStore(registry_root) as confidence,ProblemManager(registry_root) as manager:
        manager.bind_session(session); routing.bind_session(session); confidence.bind_session(session)
        expected=policy["source_checkpoint"]
        actual=dict(attempted_decisions=session.checkpoint["attempted_decisions"],
            authorized_executions=len(session.records["events"]),calls=len(session.records["calls"]),
            training=len(session.records["training"]),routing=len(routing.records),
            exploration=len(confidence.records),manager=len(manager.records),
            current_state=session.checkpoint["current_state"])
        calls=_decision_calls(session,policy); failed=policy["failed_logical_prediction_identity"]
        original=calls.get(failed,{})
        kinds=sorted(original)
        request=original.get("REQUEST_INTENT",{}).get("record",{})
        response=original.get("RESPONSE",{}).get("record",{})
        parsed=original.get("PARSED",{}).get("record",{})
        siblings=[]
        for call_id,rows in sorted(calls.items()):
            if call_id==failed: continue
            valid=sorted(rows)==["PARSED","REQUEST_INTENT","RESPONSE"] and \
                rows["PARSED"]["record"].get("parsed") is not None
            siblings.append(dict(call_id=call_id,valid=valid,
                request_sha256=rows.get("REQUEST_INTENT",{}).get("record",{}).get("request_sha256"),
                response_sha256=rows.get("RESPONSE",{}).get("record",{}).get("response_sha256")))
        decision_events=[x for x in session.records["events"] if x["record"].get(
            "prediction_batch_sequence")==87]
        decision_training=[x for x in session.records["training"] if x["record"].get(
            "prediction_batch_sequence")==87]
        authorized_training=[x for x in decision_training if x["kind"]==
            "AUTHORIZED_GROUNDED_EXPLORATION_RECORD"]
        decision_routing=[x for x in routing.records if ":d87:" in json.dumps(
            x["record"].get("prediction_commitment",{}),sort_keys=True)]
        p4=manager.state["problems"].get("PR-0004")
        facts=dict(source_checkpoint_exact=actual==expected,
            original_lineage_complete=kinds==["PARSED","REQUEST_INTENT","RESPONSE"],
            original_request_hash_exact=request.get("request_sha256")==policy["failed_request_sha256"],
            original_transport_bytes_exact=(bool(request) and sha256(request_transport_bytes(
                request["request"])).hexdigest()==policy["failed_transport_bytes_sha256"]),
            original_timeout_preserved=response.get("response",{}).get(
                "transport_error")=="TimeoutError" and parsed.get("parsed") is None,
            no_external_action=len(decision_events)==0,no_receipt=len(decision_events)==0,
            no_memory_publication=len(decision_events)==0,no_training_target=len(authorized_training)==0,
            no_routing_evidence=len(decision_routing)==0,
            eight_siblings_valid=len(siblings)==8 and all(x["valid"] for x in siblings),
            failed_decision_completed_as_abstention=(len(decision_training)==1 and
                decision_training[0]["kind"]=="GROUNDED_EXPLORER_ABSTENTION"),
            pr0004_open=(p4 is not None and p4["problem_type"]=="EXTERNAL_SERVICE_PROBLEM" and
                p4["lifecycle_state"]=="OPEN" and p4["requested_capability"]=="EXTERNAL_SERVICE_REPAIR"))
        eligible=all(facts.values())
        return dict(eligible=eligible,result="REISSUE_ALLOWED" if eligible else "REPAIR_INELIGIBLE",
            facts=facts,source_checkpoint=actual,failed_logical_prediction_identity=failed,
            failed_request_sha256=request.get("request_sha256"),failed_response_sha256=response.get(
                "response_sha256"),failed_transport_bytes_sha256=(sha256(request_transport_bytes(
                    request["request"])).hexdigest() if request else None),siblings=siblings,
            pr0002_sha256=digest(manager.state["problems"]["PR-0002"]),
            pr0003_sha256=digest(manager.state["problems"]["PR-0003"]),
            pr0004=deepcopy(p4))


def initialize_repair_store(root:Path,session_path:Path,eligibility:dict,policy:dict)->RepairStore:
    if not eligibility["eligible"]: raise RoutingError("ineligible failure cannot initialize repair")
    root.mkdir(parents=True,exist_ok=False); key=secrets.token_bytes(32)
    fd=os.open(root/RepairStore.KEY,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try: os.write(fd,(key.hex()+"\n").encode()); os.fsync(fd)
    finally: os.close(fd)
    for name in (RepairStore.STREAM,RepairStore.PRIVATE):
        fd=os.open(root/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600); os.close(fd)
    with SessionStore(session_path,True) as session:
        rows=_decision_calls(session,policy)[policy["failed_logical_prediction_identity"]]
        intent,response,parsed=(rows[k]["record"] for k in ("REQUEST_INTENT","RESPONSE","PARSED"))
        state=dict(version=1,lifecycle_state=None,stream_count=0,stream_head_sha256=None,
            logical_prediction_identity=policy["failed_logical_prediction_identity"],
            original_request_sha256=intent["request_sha256"],
            original_transport_bytes_sha256=sha256(request_transport_bytes(intent["request"])).hexdigest(),
            original_failed_response_sha256=response["response_sha256"],restart_count=0,
            reissue_count=0,resumed=False,repair_failed=False,
            source_checkpoint=deepcopy(session.checkpoint),
            source_calls_head_sha256=session.checkpoint["streams"]["calls"]["head_sha256"],
            created_at=_now(),updated_at=_now())
        RepairStore._write_state(root,key,state); repair=RepairStore(root)
        repair._append("REQUESTED",dict(requested_capability="EXTERNAL_SERVICE_REPAIR",
            allowed_capabilities=policy["allowed_capabilities"],
            logical_prediction_identity=policy["failed_logical_prediction_identity"],
            original_request_sha256=intent["request_sha256"],
            original_transport_bytes_sha256=state["original_transport_bytes_sha256"],
            original_failure="TimeoutError",external_action_after_failure=False,
            receipt_after_failure=False,memory_after_failure=False,
            routing_evidence_after_failure=False,decision_unresolved=True,
            exact_request_bytes_retained=True,eight_sibling_predictions_retained=True))
        repair._append_private("ORIGINAL_FAILED_ATTEMPT",dict(transport_attempt=1,
            logical_prediction_identity=policy["failed_logical_prediction_identity"],
            request=intent["request"],transport_bytes=request_transport_bytes(intent["request"]).decode(),
            request_sha256=intent["request_sha256"],response=response["response"],
            response_sha256=response["response_sha256"],parsed=None,parse_error=parsed["parse_error"]))
        return repair


def verify_model_artifacts()->dict:
    if file_hash(MANIFEST_PATH)!=REPAIR_POLICY["expected_model_manifest_sha256"]:
        raise RoutingError("registered model manifest changed")
    manifest=json.loads(MANIFEST_PATH.read_text()); blobs=MANIFEST_PATH.parents[4]/"blobs"
    descriptors=[manifest["config"],*manifest["layers"]]; verified=[]
    for row in descriptors:
        algorithm,value=row["digest"].split(":",1)
        if algorithm!="sha256": raise RoutingError("unsupported model artifact digest")
        # This repository's registered Ollama version stores digest filenames
        # verbatim (``sha256:<hex>``), matching its manifest.
        path=blobs/f"sha256:{value}"
        if not path.is_file() or path.stat().st_size!=row["size"] or file_hash(path)!=value:
            raise RoutingError("model artifact hash or size changed")
        verified.append(dict(media_type=row["mediaType"],size=row["size"],sha256=value))
    return dict(model=REPAIR_POLICY["expected_model"],manifest_sha256=file_hash(MANIFEST_PATH),
        blobs=verified,all_artifacts_hash_verified=True)


def _service_pids()->list[int]:
    result=[]
    for path in Path("/proc").glob("[0-9]*/cmdline"):
        try: parts=[x.decode() for x in path.read_bytes().split(b"\0") if x]
        except (OSError,UnicodeDecodeError): continue
        if len(parts)>=2 and Path(parts[0]).name=="ollama" and parts[1]=="serve":
            result.append(int(path.parent.name))
    return sorted(result)


def restart_persistent_service(repair:RepairStore)->dict:
    executable=shutil.which("ollama")
    if executable is None: raise RoutingError("registered Ollama executable is unavailable")
    old=_service_pids(); repair.attempted(dict(command=[executable,"serve"],
        prior_service_pids=old,persistent=True))
    for pid in old:
        try: os.kill(pid,signal.SIGTERM)
        except ProcessLookupError: pass
    for _ in range(20):
        if not _service_pids(): break
        time.sleep(.25)
    if _service_pids(): raise RoutingError("prior Ollama service did not stop")
    log_path=Path("/tmp/horus-v018-ollama.log")
    with log_path.open("ab",buffering=0) as log:
        process=subprocess.Popen([executable,"serve"],stdout=log,stderr=subprocess.STDOUT,
                                 start_new_session=True)
    listener=False
    for wait in (5,20):
        time.sleep(wait)
        try:
            with urllib.request.urlopen("http://127.0.0.1:11434/api/tags",timeout=5) as response:
                listener=response.status==200
        except Exception: listener=False
        if listener: break
    return dict(command=[executable,"serve"],pid=process.pid,
        persistent_process_alive=process.poll() is None,listener_alive=listener,
        listener="127.0.0.1:11434",log_sha256=file_hash(log_path))


def _reconstruct_batch(session:SessionStore,capture:dict,repaired:dict,policy:dict)->RoutedForecastBatch:
    calls=_decision_calls(session,policy)
    if len(calls)!=9: raise RoutingError("interrupted prediction batch is incomplete")
    failed=policy["failed_logical_prediction_identity"]
    prefix=failed.rsplit(":RETREAT:J",1)[0]; forecasts={"G2":[],"G3":[]}
    evidence={}; commitments={}
    for action in ACTION_ORDER:
        payload=capture["map_inputs"][action]; prompt=_canonical(payload)
        history=tuple(GroundedObservation(**x) for x in payload["VERIFIED_CHRONOLOGICAL_HISTORY"])
        context=dict(state=capture["state"],action=action,action_alias=payload["target_action"],
            epoch=capture["epoch"],transaction_id=capture["transaction_id"],
            authenticated_history=[asdict(x) for x in history],memory_sha256=capture["memory_sha256"],
            authenticated_history_reference=capture["authenticated_history_reference"])
        evidence[action]={}; commitments[action]={"specialists":{}}
        jid=f"{prefix}:{action}:J"; jrows=calls[jid]; jrequest=jrows["REQUEST_INTENT"]["record"]["request"]
        if jrequest["prompt"]!=prompt or jrequest["system"]!=JOINT_SYSTEM or \
                digest(jrequest)!=jrows["REQUEST_INTENT"]["record"]["request_sha256"]:
            raise RoutingError("current authenticated context differs from interrupted request")
        joint=(repaired["parsed"] if jid==failed else jrows["PARSED"]["record"]["parsed"])
        if joint is None: raise RoutingError("reconstructed joint prediction remains invalid")
        commitments[action]["joint"]=dict(call_id=jid,
            request_sequence=jrows["REQUEST_INTENT"]["sequence"],
            response_sequence=(repaired["transport_attempt_identity"] if jid==failed else
                               jrows["RESPONSE"]["sequence"]),
            parsed_sequence=("REPAIR_PRIVATE_STREAM" if jid==failed else jrows["PARSED"]["sequence"]),
            request_sha256=jrows["REQUEST_INTENT"]["record"]["request_sha256"],
            logical_prediction_reissued=jid==failed)
        for specialist in ("G2","G3"):
            cid=f"{prefix}:{action}:{specialist}"; rows=calls[cid]
            parsed=rows["PARSED"]["record"]["parsed"]; request=rows["REQUEST_INTENT"]["record"]["request"]
            if parsed is None or request["prompt"]!=prompt or request["system"]!=CONSEQUENCE_SYSTEM:
                raise RoutingError("durable sibling prediction changed or is invalid")
            forecasts[specialist].append(MapForecast(action,payload["target_action"],
                joint["next_state"],parsed["consequence"],False,None,len(history),context))
            evidence[action][specialist]=dict(parsed=parsed,response_sha256=rows[
                "RESPONSE"]["record"]["response_sha256"])
            commitments[action]["specialists"][specialist]=dict(call_id=cid,
                request_sequence=rows["REQUEST_INTENT"]["sequence"],
                response_sequence=rows["RESPONSE"]["sequence"],
                parsed_sequence=rows["PARSED"]["sequence"],
                request_sha256=rows["REQUEST_INTENT"]["record"]["request_sha256"],
                prediction=parsed["consequence"],logical_prediction_reissued=False)
    return RoutedForecastBatch({k:tuple(v) for k,v in forecasts.items()},evidence,commitments,True)


class RepairedFollowupRuntime(GroundedExplorationRuntime):
    def __init__(self,*args,repaired:dict,policy:dict,**kwargs):
        super().__init__(*args,**kwargs); self.repaired=repaired; self.policy=policy; self.used=False
    def _next_batch(self):
        if self.used: raise RoutingError("repaired follow-up decision already consumed")
        self.used=True; capture=self.reader.capture()
        batch=_reconstruct_batch(self.store,capture,self.repaired,self.policy)
        sequence=self.store.checkpoint["attempted_decisions"]+1
        decision_id=self.policy["failed_logical_prediction_identity"]+":resumed:transport:2"
        return capture,batch,sequence,decision_id


def suffix_prefix_observation(row:dict,authenticated_identities:set[tuple],branches:list[dict])->dict:
    if row["status"]!="AUTHORIZED" or row.get("receipt") is None:
        return dict(label="OBSERVED_SUFFIX_PREFIX_CHECK",result="NOT_APPLICABLE",
            reason="RESUMED_ORDINARY_DECISION_DID_NOT_EXECUTE",global_validation_changed=False)
    receipt=row["receipt"]; identity=tuple(receipt[k] for k in (
        "source_identity","event_id","epoch","transaction_id"))
    if identity not in authenticated_identities:
        raise RoutingError("suffix observation lacks authenticated receipt")
    action=receipt["action"]; branch=next(x for x in branches if x["current_action"]=="RETREAT" and
                                          x["second_action"]==action)
    c1=branch["sequence"][1]; predicted_state=branch["predicted_second_state"]
    return dict(label="OBSERVED_SUFFIX_PREFIX_CHECK",
        result="MATCH" if c1==receipt["realized_consequence"] else "MISMATCH",action=action,
        retained_predicted_c1=c1,realized_consequence=receipt["realized_consequence"],
        c1_match=c1==receipt["realized_consequence"],
        retained_predicted_second_next_state=predicted_state,
        realized_next_state=receipt["next_state"],next_state_match=predicted_state==receipt["next_state"],
        retained_consequence_provenance="MODEL_FORECAST",
        retained_next_state_provenance="MODEL_FORECAST",
        realized_provenance="AUTHENTICATED_ORIGINAL_RECEIPT",
        full_trajectory_validated=False,global_validation_changed=False,controls_behavior=False)


def _plain_row(row:dict)->dict:
    receipt=row.get("receipt")
    return dict(decision_sequence=row["prediction_batch_sequence"],status=row["status"],
        action=row["explorer"].get("action"),reason=row["explorer"].get("reason"),
        mode=row["explorer"].get("mode"),option_profile_controlled=False,
        receipt=None if receipt is None else deepcopy(receipt),model_calls=0)


def run(session_path:Path,registry_root:Path,repair_root:Path,joint_client=None,
        specialists=None)->dict:
    policy=load_policy(); eligibility=repair_eligibility(session_path,registry_root,policy)
    if not eligibility["eligible"]:
        return dict(identity=policy["mode"],status="REPAIR_INELIGIBLE",eligibility=eligibility,
            total_live_model_calls=0,training_runs=0)
    repair=initialize_repair_store(repair_root,session_path,eligibility,policy)
    grant=json.loads(Path(policy["authorization_path"]).read_text())
    with SessionStore(session_path,True) as session,ProblemManager(registry_root) as manager:
        manager.bind_session(session); before_pr2=deepcopy(manager.state["problems"]["PR-0002"])
        before_pr3=deepcopy(manager.state["problems"]["PR-0003"])
        manager.record_operational_repair_event(problem_id="PR-0004",stage="REPAIR_REQUESTED",
            capabilities=policy["allowed_capabilities"],details=deepcopy(eligibility["facts"]))
        authorization=repair.authorize(grant)
        manager.record_operational_repair_event(problem_id="PR-0004",stage="REPAIR_AUTHORIZED",
            authorization_sha256=digest(grant),details={"authority_class":"OPERATIONAL_REPAIR_ROUTE"})
        manager.record_operational_repair_event(problem_id="PR-0004",stage="REPAIR_ATTEMPTED",
            details={"capability":"RESTART_MODEL_SERVICE"})
        service=restart_persistent_service(repair); artifacts=verify_model_artifacts()
        client=joint_client or ModelClient(); health=service_health(client,service)
        health["artifact_verification"]=artifacts
        if repair.state["lifecycle_state"]=="REPAIR_ATTEMPTED": repair.succeeded(health)
        if repair.state["lifecycle_state"]=="REPAIR_FAILED":
            manager.record_operational_repair_event(problem_id="PR-0004",stage="REPAIR_FAILED",
                details={"reason":"SERVICE_HEALTH_PROOF_FAILED"})
            return dict(identity=policy["mode"],status="REPAIR_FAILED",eligibility=eligibility,
                service_health=health,total_live_model_calls=client.requests,training_runs=0)
        manager.record_operational_repair_event(problem_id="PR-0004",stage="REPAIR_SUCCEEDED",
            details={"health_request_sha256":health["health_request_sha256"],
                     "manifest_sha256":artifacts["manifest_sha256"]})
        calls=_decision_calls(session,policy); original_request=deepcopy(calls[
            policy["failed_logical_prediction_identity"]]["REQUEST_INTENT"]["record"]["request"])
        manager.record_operational_repair_event(problem_id="PR-0004",stage="REISSUE_ATTEMPTED",
            details={"logical_prediction_identity":policy["failed_logical_prediction_identity"],
                "transport_attempt_identity":policy["failed_logical_prediction_identity"]+":transport:2",
                "request_sha256":digest(original_request)})
        repaired=repair.reissue(client,original_request)
        if repaired["parsed"] is None:
            manager.record_operational_repair_event(problem_id="PR-0004",stage="REPAIR_FAILED",
                details={"reason":repaired["error"]})
            return dict(identity=policy["mode"],status="REPAIR_FAILED",eligibility=eligibility,
                service_health=health,reissue=repaired,total_live_model_calls=client.requests,
                training_runs=0)
        if specialists is None: specialists,relation_registry=relation_routed_clients(
            registry_root,device="cuda")
        else:
            from .relation_routing import load_relation_routing_registry
            relation_registry=load_relation_routing_registry(registry_root)
        with RelationEvidenceStore(registry_root) as routing,ExplorerConfidenceStore(
                registry_root) as confidence:
            before_events=len(session.records["events"]); before_routing=len(routing.records)
            before_training=len(session.records["training"])
            runtime=RepairedFollowupRuntime(session,client,specialists,relation_registry,
                routing,confidence,"A",repaired=repaired,policy=policy)
            runtime_boundary=dict(runtime_index=session.checkpoint["runtime_index"],
                epoch=session.checkpoint["current_epoch"],
                source_identity=session.checkpoint["current_source_identity"])
            row=runtime.execute_autonomous(); row["model_calls"]=0
            status=("ORDINARY_CONTINUATION_EXECUTED" if row["status"]=="AUTHORIZED" else
                    "ORDINARY_CONTINUATION_ABSTAINS" if row["status"]=="ABSTAINED" else
                    "REPAIR_FAILED")
            manager.record_operational_repair_event(problem_id="PR-0004",stage="RESUMED",
                store=session,row=row,outcome=status,details={
                    "logical_prediction_identity":policy["failed_logical_prediction_identity"],
                    "option_profile_controlled":False})
            repair.resumed(dict(resumed_decision_sequence=row["prediction_batch_sequence"],
                status=row["status"],action=row["explorer"].get("action"),
                receipt_identity=None if row.get("receipt") is None else [row["receipt"][k] for k in (
                    "source_identity","event_id","epoch","transaction_id")],
                repair_event_is_world_evidence=False))
            identities={tuple(e["record"]["receipt_identity"]) for e in session.records["events"]}
            branches=json.loads(V015_RESULTS.read_text())["branches"]
            suffix=suffix_prefix_observation(row,identities,branches)
            if client.requests!=2: raise RoutingError("v0.18 exact two-call ceiling changed")
            if manager.state["problems"]["PR-0002"]!=before_pr2 or \
                    manager.state["problems"]["PR-0003"]!=before_pr3:
                raise RoutingError("repair rewrote an unrelated behavioral problem")
            return dict(identity=policy["mode"],status=status,eligibility=eligibility,
                repair_authorization_sha256=digest(grant),original_failure=dict(
                    logical_prediction_identity=policy["failed_logical_prediction_identity"],
                    request_sha256=policy["failed_request_sha256"],attempt_1="TimeoutError",
                    retained=True,overwritten=False),reissue=dict(
                    transport_attempt_identity=repaired["transport_attempt_identity"],
                    request_sha256=policy["failed_request_sha256"],request_bytes_identical=True,
                    response_sha256=repaired["response_sha256"],attempt=2),
                service_health=health,total_live_model_calls=client.requests,
                infrastructure_health_calls=1,repaired_transport_calls=1,other_model_calls=0,
                resumed_ordinary_decision=_plain_row(row),suffix_prefix_check=suffix,
                new_authenticated_receipts=len(session.records["events"])-before_events,
                new_routing_records=len(routing.records)-before_routing,
                training_records_added=len(session.records["training"])-before_training,
                operational_repair_records_are_training_targets=False,runtime_boundary=runtime_boundary,
                final_pr0004=deepcopy(manager.state["problems"]["PR-0004"]),
                pr0002_unchanged=True,pr0002=deepcopy(manager.state["problems"]["PR-0002"]),
                pr0003_unchanged=True,repair_state=deepcopy(repair.state),
                final_checkpoint=deepcopy(session.checkpoint),training_runs=0,
                option_profile_validity_changed=False,new_representation_added=False,
                horizon_depth_changed=False,counterfactual_advance_executed=False)
