"""Bounded, independently authorized operational repair for Horus v0.10."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from hashlib import sha256
from hmac import compare_digest, new as new_hmac
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import time
import urllib.request

from experiments.base_framework_v0.framework import ACTION_ORDER
from experiments.map_consequence_only_isolation_v0.protocol import parse as parse_consequence
from experiments.model_map_proposal_v0.adapter import parse as parse_joint

from .capability_gap import CapabilityGapRuntime, CapabilityGapStore
from .core import GroundedObservation, MAPPING, MapForecast, digest
from .grounded_exploration import ExplorerConfidenceStore
from .grounded_learning import atomic_json, file_hash
from .live import (CONSEQUENCE_SYSTEM, JOINT_SYSTEM, ModelClient, SessionStore,
                   _canonical, _now, _plain)
from .relation_routing import RelationEvidenceStore, relation_routed_clients
from .routing import RoutedForecastBatch, RoutingError


POLICY_PATH=Path(__file__).with_name("repair_resume_policy.json")
POLICY=json.loads(POLICY_PATH.read_text())
MANIFEST_PATH=Path.home()/".ollama/models/manifests/registry.ollama.ai/library/dolphin-mixtral/latest"
LIFECYCLE=("REQUESTED","AUTHORIZED","REPAIR_ATTEMPTED","REPAIR_SUCCEEDED",
           "REISSUE_ATTEMPTED","RESUMED","REPAIR_FAILED")


class RepairBroker:
    """Finite authority separation for behavioral, operational and design routes."""
    authority_classes={
        "MORE_RELATION_EVIDENCE":"BEHAVIORAL_ROUTE",
        "EXTERNAL_SERVICE_REPAIR":"OPERATIONAL_REPAIR_ROUTE",
        "LONGER_HORIZON_VALUE":"CAPABILITY_DESIGN_REQUEST",
    }
    def __init__(self, policy: dict|None=None): self.policy=policy or POLICY
    @staticmethod
    def retry_eligibility(*, external_action: bool, receipt_created: bool,
                          memory_published: bool, routing_evidence_added: bool,
                          unresolved: bool, exact_request_bytes: bool,
                          explicitly_authorized: bool) -> dict:
        facts=dict(external_action=external_action,receipt_created=receipt_created,
            memory_published=memory_published,routing_evidence_added=routing_evidence_added,
            unresolved=unresolved,exact_request_bytes=exact_request_bytes,
            explicitly_authorized=explicitly_authorized)
        eligible=(not external_action and not receipt_created and not memory_published and
                  not routing_evidence_added and unresolved and exact_request_bytes and
                  explicitly_authorized)
        return dict(eligible=eligible,facts=facts,
                    result="REISSUE_ALLOWED" if eligible else "FAIL_CLOSED")
    def authorize(self, requested: list[str], grant: dict) -> dict:
        if not requested or set(requested)-set(self.policy["allowed_capabilities"]):
            raise RoutingError("repair request includes an unsupported capability")
        if grant.get("explicit_authorization") is not True or \
                grant.get("request")!="EXTERNAL_SERVICE_REPAIR" or \
                grant.get("capabilities")!=requested:
            raise RoutingError("explicit bounded repair authorization is absent")
        return dict(authority_class="OPERATIONAL_REPAIR_ROUTE",
            capabilities=list(requested),authorized=True,
            can_execute_world_action=False,can_create_receipt=False,
            can_publish_memory=False,can_add_routing_evidence=False,
            can_create_training_target=False,can_train=False,
            can_change_architecture=False,can_change_objective=False)


def request_transport_bytes(request: dict) -> bytes:
    """Recreate the ModelClient HTTP body from the frozen insertion order."""
    ordered=dict(model=request["model"],system=request["system"],
                 prompt=request["prompt"],stream=request["stream"],
                 options=request["options"])
    return json.dumps(ordered).encode()


class RepairStore:
    KEY="repair-integrity.key"; STATE="repair-state.json"
    STREAM="repair-events.jsonl"; PRIVATE="repair-model-calls.private.jsonl"
    def __init__(self,root:Path):
        self.root=root.resolve(); self.policy=POLICY
        self._key=bytes.fromhex((self.root/self.KEY).read_text().strip())
        self.state=json.loads((self.root/self.STATE).read_text())["payload"]
        self.records=[json.loads(x) for x in (self.root/self.STREAM).read_text().splitlines()]
        self.private=[json.loads(x) for x in (self.root/self.PRIVATE).read_text().splitlines()]
        self._validate()
    @classmethod
    def initialize(cls,root:Path,source_session:Path,source_report:Path)->dict:
        root=root.resolve()
        if any((root/name).exists() for name in (cls.KEY,cls.STATE,cls.STREAM,cls.PRIVATE)):
            raise RoutingError("repair store already exists")
        if file_hash(source_report)!=POLICY["source_report_sha256"]:
            raise RoutingError("v0.9 public report differs from frozen failed evidence")
        with SessionStore(source_session,True) as session:
            cp=deepcopy(session.checkpoint); calls=deepcopy(session.records["calls"])
            if (cp["attempted_decisions"],len(session.records["events"]),
                    len(session.records["training"]),len(calls)) != (
                    POLICY["source_attempted_decisions"],
                    POLICY["source_authorized_executions"],
                    POLICY["source_training_records"],
                    POLICY["source_model_call_records"]):
                raise RoutingError("v0.9 private source counts differ from frozen failure")
        logical=POLICY["failed_logical_prediction_identity"]
        original=[row for row in calls if row["record"].get("call_id")==logical]
        if [row["kind"] for row in original] != ["REQUEST_INTENT","RESPONSE","PARSED"]:
            raise RoutingError("original failed call lineage is incomplete")
        intent,response,parsed=(row["record"] for row in original)
        if intent["request_sha256"]!=POLICY["failed_request_sha256"] or \
                response["response_sha256"]!=POLICY["failed_response_sha256"] or \
                response["response"].get("transport_error")!="TimeoutError" or \
                parsed.get("parsed") is not None:
            raise RoutingError("original failed call differs from frozen identity")
        raw=request_transport_bytes(intent["request"])
        key=secrets.token_bytes(32)
        fd=os.open(root/cls.KEY,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        try: os.write(fd,(key.hex()+"\n").encode()); os.fsync(fd)
        finally: os.close(fd)
        for name in (cls.STREAM,cls.PRIVATE):
            fd=os.open(root/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600); os.close(fd)
        state=dict(version=1,lifecycle_state=None,stream_count=0,stream_head_sha256=None,
            logical_prediction_identity=logical,original_request_sha256=intent["request_sha256"],
            original_transport_bytes_sha256=sha256(raw).hexdigest(),
            original_failed_response_sha256=response["response_sha256"],
            restart_count=0,reissue_count=0,resumed=False,repair_failed=False,
            source_checkpoint=cp,source_calls_head_sha256=cp["streams"]["calls"]["head_sha256"],
            created_at=_now(),updated_at=_now())
        cls._write_state(root,key,state)
        store=cls(root)
        store._append("REQUESTED",dict(requested_capability="EXTERNAL_SERVICE_REPAIR",
            allowed_capabilities=POLICY["allowed_capabilities"],
            logical_prediction_identity=logical,original_request_sha256=intent[
                "request_sha256"],original_transport_bytes_sha256=sha256(raw).hexdigest(),
            original_failure="TimeoutError",external_action_after_failure=False,
            receipt_after_failure=False,memory_after_failure=False,
            routing_evidence_after_failure=False,decision_unresolved=True,
            exact_request_bytes_retained=True))
        store._append_private("ORIGINAL_FAILED_ATTEMPT",dict(
            transport_attempt=1,logical_prediction_identity=logical,
            request=intent["request"],transport_bytes=raw.decode(),
            request_sha256=intent["request_sha256"],response=response["response"],
            response_sha256=response["response_sha256"],parsed=None,
            parse_error=parsed["parse_error"]))
        return deepcopy(store.state)
    @staticmethod
    def _write_state(root,key,state):
        state["updated_at"]=_now(); payload=deepcopy(state)
        doc={"payload":payload,"hmac_sha256":new_hmac(key,_canonical(payload).encode(),"sha256").hexdigest()}
        atomic_json(root/RepairStore.STATE,doc)
    def _mac(self,value): return new_hmac(self._key,_canonical(value).encode(),"sha256").hexdigest()
    def _append(self,state,record):
        if state not in LIFECYCLE: raise RoutingError("unknown repair lifecycle state")
        previous=None if not self.records else sha256(_canonical(self.records[-1]).encode()).hexdigest()
        signed=dict(sequence=len(self.records)+1,previous_sha256=previous,state=state,
                    record={**_plain(record),"recorded_at":_now()})
        env={**signed,"hmac_sha256":self._mac(signed)}
        with (self.root/self.STREAM).open("a") as f:
            f.write(_canonical(env)+"\n"); f.flush(); os.fsync(f.fileno())
        self.records.append(env); self.state.update(lifecycle_state=state,
            stream_count=len(self.records),stream_head_sha256=sha256(
                _canonical(env).encode()).hexdigest())
        self._write_state(self.root,self._key,self.state); return deepcopy(env)
    def _append_private(self,kind,record):
        previous=None if not self.private else sha256(_canonical(self.private[-1]).encode()).hexdigest()
        signed=dict(sequence=len(self.private)+1,previous_sha256=previous,kind=kind,
                    record={**_plain(record),"recorded_at":_now()})
        env={**signed,"hmac_sha256":self._mac(signed)}
        with (self.root/self.PRIVATE).open("a") as f:
            f.write(_canonical(env)+"\n"); f.flush(); os.fsync(f.fileno())
        self.private.append(env); return deepcopy(env)
    def _validate(self):
        doc=json.loads((self.root/self.STATE).read_text()); payload=doc["payload"]
        if not compare_digest(self._mac(payload),doc.get("hmac_sha256","")):
            raise RoutingError("repair state authentication failed")
        previous=None
        for i,row in enumerate(self.records,1):
            signed={k:row[k] for k in ("sequence","previous_sha256","state","record")}
            if row["sequence"]!=i or row["previous_sha256"]!=previous or \
                    not compare_digest(self._mac(signed),row.get("hmac_sha256","")):
                raise RoutingError("repair lifecycle chain authentication failed")
            previous=sha256(_canonical(row).encode()).hexdigest()
        if self.state["stream_count"]!=len(self.records) or (self.records and
                self.state["stream_head_sha256"]!=previous):
            raise RoutingError("repair state/stream replay mismatch")
        pprev=None
        for i,row in enumerate(self.private,1):
            signed={k:row[k] for k in ("sequence","previous_sha256","kind","record")}
            if row["sequence"]!=i or row["previous_sha256"]!=pprev or \
                    not compare_digest(self._mac(signed),row.get("hmac_sha256","")):
                raise RoutingError("private repair call chain authentication failed")
            pprev=sha256(_canonical(row).encode()).hexdigest()
    def authorize(self,grant:dict)->dict:
        if self.state["lifecycle_state"]!="REQUESTED": raise RoutingError("repair is not requested")
        authority=RepairBroker().authorize(POLICY["allowed_capabilities"],grant)
        return self._append("AUTHORIZED",dict(**authority,authorization_sha256=digest(grant)))
    def attempted(self,service_metadata:dict)->dict:
        if self.state["lifecycle_state"]!="AUTHORIZED" or self.state["restart_count"]>=1:
            raise RoutingError("service restart is not authorized")
        self.state["restart_count"]+=1
        return self._append("REPAIR_ATTEMPTED",dict(service_metadata=service_metadata,
            restart_count=self.state["restart_count"]))
    def succeeded(self,proof:dict)->dict:
        if self.state["lifecycle_state"]!="REPAIR_ATTEMPTED": raise RoutingError("repair was not attempted")
        required=(proof.get("persistent_process_alive") is True and
            proof.get("listener_alive") is True and proof.get("health_parse_valid") is True and
            proof.get("model_manifest_sha256")==POLICY["expected_model_manifest_sha256"] and
            proof.get("model")==POLICY["expected_model"])
        if not required: return self.fail("SERVICE_HEALTH_PROOF_FAILED")
        return self._append("REPAIR_SUCCEEDED",proof)
    def reissue(self,client:ModelClient,request:dict)->dict:
        if self.state["lifecycle_state"]!="REPAIR_SUCCEEDED" or self.state["reissue_count"]>=1:
            raise RoutingError("prediction reissue is not authorized")
        if digest(request)!=self.state["original_request_sha256"] or sha256(
                request_transport_bytes(request)).hexdigest()!=self.state[
                    "original_transport_bytes_sha256"]:
            raise RoutingError("reissued request bytes differ from original")
        self.state["reissue_count"]+=1
        attempt_id=self.state["logical_prediction_identity"]+":transport:2"
        self._append("REISSUE_ATTEMPTED",dict(
            logical_prediction_identity=self.state["logical_prediction_identity"],
            transport_attempt_identity=attempt_id,transport_attempt=2,
            request_sha256=digest(request),transport_bytes_sha256=sha256(
                request_transport_bytes(request)).hexdigest()))
        response=client.generate(request); parsed=None; error=response.get("transport_error")
        if error is None:
            try: parsed=parse_joint(response["raw_output"])
            except (ValueError,TypeError,json.JSONDecodeError) as exc: error=type(exc).__name__
        self._append_private("REISSUED_TRANSPORT_ATTEMPT",dict(
            transport_attempt=2,transport_attempt_identity=attempt_id,
            logical_prediction_identity=self.state["logical_prediction_identity"],
            request=request,transport_bytes=request_transport_bytes(request).decode(),
            request_sha256=digest(request),response=response,
            response_sha256=digest(response),parsed=parsed,parse_error=error))
        if parsed is None:
            self.fail(error or "INVALID_RESPONSE")
            return dict(parsed=None,error=error,response_sha256=digest(response))
        return dict(parsed=parsed,error=None,response_sha256=digest(response),
                    transport_attempt_identity=attempt_id)
    def resumed(self,binding:dict)->dict:
        if self.state["lifecycle_state"]!="REISSUE_ATTEMPTED": raise RoutingError("reissue not complete")
        self.state["resumed"]=True
        return self._append("RESUMED",binding)
    def fail(self,reason:str)->dict:
        self.state["repair_failed"]=True
        return self._append("REPAIR_FAILED",dict(reason=reason,no_recursive_repair=True))


def _original_calls(session:SessionStore)->dict:
    result={}
    for row in session.records["calls"]:
        call_id=row["record"].get("call_id","")
        if ":b57:" in call_id:
            result.setdefault(call_id,{})[row["kind"]]=row
    return result


def original_failed_request(session:SessionStore)->dict:
    calls=_original_calls(session); logical=POLICY["failed_logical_prediction_identity"]
    return deepcopy(calls[logical]["REQUEST_INTENT"]["record"]["request"])


def reconstruct_batch(session:SessionStore,capture:dict,repaired:dict)->RoutedForecastBatch:
    """Combine eight preserved b57 results with the single repaired component."""
    calls=_original_calls(session)
    if len(calls)!=9: raise RoutingError("original unresolved batch is incomplete")
    forecasts={"G2":[],"G3":[]}; evidence={}; commitments={}
    for action in ACTION_ORDER:
        payload=capture["map_inputs"][action]; prompt=_canonical(payload)
        history=tuple(GroundedObservation(**x) for x in payload[
            "VERIFIED_CHRONOLOGICAL_HISTORY"])
        context=dict(state=capture["state"],action=action,
            action_alias=payload["target_action"],epoch=capture["epoch"],
            transaction_id=capture["transaction_id"],
            authenticated_history=[asdict(x) for x in history],
            memory_sha256=capture["memory_sha256"],
            authenticated_history_reference=capture["authenticated_history_reference"])
        evidence[action]={}; commitments[action]={"specialists":{}}
        jid=f"{POLICY['failed_logical_prediction_identity'].split(':b57:')[0]}:b57:{action}:J"
        jrows=calls[jid]; expected=dict(model=POLICY["expected_model"],system=JOINT_SYSTEM,
            prompt=prompt,stream=False,options=jrows["REQUEST_INTENT"]["record"]["request"]["options"])
        if digest(expected)!=jrows["REQUEST_INTENT"]["record"]["request_sha256"]:
            raise RoutingError("fresh capture differs from original unresolved request")
        jp=repaired["parsed"] if action=="HOLD" else jrows["PARSED"]["record"]["parsed"]
        if jp is None: raise RoutingError("repaired joint batch remains invalid")
        commitments[action]["joint"]=dict(call_id=jid,
            request_sequence=jrows["REQUEST_INTENT"]["sequence"],
            response_sequence=(repaired["transport_attempt_identity"] if action=="HOLD" else
                               jrows["RESPONSE"]["sequence"]),
            parsed_sequence=("REPAIR_PRIVATE_STREAM" if action=="HOLD" else
                             jrows["PARSED"]["sequence"]),
            request_sha256=digest(expected),logical_prediction_reissued=action=="HOLD")
        for specialist in ("G2","G3"):
            cid=f"{POLICY['failed_logical_prediction_identity'].split(':b57:')[0]}:b57:{action}:{specialist}"
            rows=calls[cid]; cp=rows["PARSED"]["record"]["parsed"]
            if cp is None: raise RoutingError("preserved specialist response is invalid")
            request=rows["REQUEST_INTENT"]["record"]["request"]
            if request["prompt"]!=prompt or request["system"]!=CONSEQUENCE_SYSTEM:
                raise RoutingError("fresh capture differs from preserved specialist request")
            forecast=MapForecast(action,payload["target_action"],jp["next_state"],
                cp["consequence"],False,None,len(history),context)
            forecasts[specialist].append(forecast)
            evidence[action][specialist]=dict(response=rows["RESPONSE"]["record"]["response"],parsed=cp)
            commitments[action]["specialists"][specialist]=dict(call_id=cid,
                request_sequence=rows["REQUEST_INTENT"]["sequence"],
                response_sequence=rows["RESPONSE"]["sequence"],
                parsed_sequence=rows["PARSED"]["sequence"],
                request_sha256=rows["REQUEST_INTENT"]["record"]["request_sha256"],
                prediction=cp["consequence"])
    return RoutedForecastBatch({k:tuple(v) for k,v in forecasts.items()},evidence,commitments,True)


class RepairResumeRuntime(CapabilityGapRuntime):
    def __init__(self,*args,repaired_batch: RoutedForecastBatch|None=None,**kwargs):
        super().__init__(*args,**kwargs); self.repaired_batch=repaired_batch; self.used=False
    def _next_batch(self):
        capture=self.reader.capture()
        if not self.used:
            if self.repaired_batch is None:
                raise RoutingError("repaired batch has not been bound")
            self.used=True
            return capture,self.repaired_batch,self.store.checkpoint["attempted_decisions"]+1,(
                f"{self.store.checkpoint['session_id']}:repair-resume:d{self.store.checkpoint['attempted_decisions']+1}")
        # The preserved/repaired batch deliberately did not alter the behavioral
        # model-call stream, so decision sequence rather than request count binds
        # subsequent fresh batches.
        sequence=self.store.checkpoint["attempted_decisions"]+1
        decision_id=f"{self.store.checkpoint['session_id']}:e{capture['epoch']}:resume:d{sequence}"
        return capture,self.map.forecasts(capture,decision_id),sequence,decision_id


def service_health(client:ModelClient,process_metadata:dict)->dict:
    request=dict(model=POLICY["expected_model"],system=JOINT_SYSTEM,
        prompt=_canonical(dict(state=0,target_action="K2",VERIFIED_CHRONOLOGICAL_HISTORY=[])),
        stream=False,options=dict(num_ctx=2048,num_predict=32,repeat_penalty=1.1,
                                  temperature=0.2,top_k=40,top_p=0.9))
    response=client.generate(request); parsed=None
    if response.get("transport_error") is None:
        try: parsed=parse_joint(response["raw_output"])
        except (ValueError,TypeError,json.JSONDecodeError): pass
    return dict(model=POLICY["expected_model"],
        model_manifest_sha256=file_hash(MANIFEST_PATH),
        persistent_process_alive=process_metadata.get("persistent_process_alive") is True,
        listener_alive=process_metadata.get("listener_alive") is True,
        service_instance=process_metadata,health_request_sha256=digest(request),
        health_response_sha256=digest(response),health_transport_error=response.get("transport_error"),
        health_parse=parsed,health_parse_valid=parsed is not None,
        health_request_is_behavioral_evidence=False)


def restart_model_service(repair:RepairStore,configuration:dict)->dict:
    """Execute exactly the allowlisted service restart and check liveness sparsely."""
    executable=shutil.which("ollama")
    if executable is None or configuration.get("command")!=["ollama","serve"]:
        raise RoutingError("only the registered Ollama restart command is allowed")
    log_path=Path(configuration["log_path"]).resolve()
    repair.attempted(dict(command=[executable,"serve"],log_sha256_before=(
        file_hash(log_path) if log_path.exists() else None),persistent=True))
    log_path.parent.mkdir(parents=True,exist_ok=True)
    with log_path.open("ab",buffering=0) as log:
        process=subprocess.Popen([executable,"serve"],stdout=log,stderr=subprocess.STDOUT,
                                 start_new_session=True)
    # Service launch is short. Check once after 5 s, then once after a 20 s backoff.
    alive=False
    for wait in (5,20):
        time.sleep(wait)
        try:
            with urllib.request.urlopen("http://127.0.0.1:11434/api/tags",timeout=5) as response:
                alive=response.status==200
        except Exception: alive=False
        if alive: break
    start_ticks=None
    try: start_ticks=Path(f"/proc/{process.pid}/stat").read_text().split()[21]
    except OSError: pass
    return dict(command=[executable,"serve"],pid=process.pid,
        process_start_ticks=start_ticks,persistent_process_alive=process.poll() is None,
        listener_alive=alive,listener="127.0.0.1:11434",log_path=str(log_path),
        log_sha256_after_launch=file_hash(log_path) if log_path.exists() else None)


def run_authorized_repair_resume(session_path:Path,registry_root:Path,
                                 authorization_path:Path,
                                 process_metadata_path:Path,
                                 joint_client=None,specialist_clients=None)->dict:
    """Perform the one authorized reissue, then the minimal live continuation."""
    grant=json.loads(authorization_path.read_text())
    configuration=json.loads(process_metadata_path.read_text())
    repair=RepairStore(registry_root)
    if repair.state["lifecycle_state"]=="REQUESTED": repair.authorize(grant)
    if repair.state["lifecycle_state"]=="AUTHORIZED":
        metadata=restart_model_service(repair,configuration)
    else:
        raise RoutingError("repair route is not at the authorized restart boundary")
    client=joint_client or ModelClient()
    health=service_health(client,metadata)
    if repair.state["lifecycle_state"]=="REPAIR_ATTEMPTED": repair.succeeded(health)
    if repair.state["lifecycle_state"]=="REPAIR_FAILED":
        return dict(status="REPAIR_FAILED",health=health,new_behavioral_decisions=0,
                    new_model_calls=1,terminal_classification="REPAIR_FAILED")
    if specialist_clients is None:
        specialist_clients,relation_registry=relation_routed_clients(registry_root,device="cuda")
    else:
        from .relation_routing import load_relation_routing_registry
        relation_registry=load_relation_routing_registry(registry_root)
    before_specialists={k:specialist_clients[k].requests for k in ("G2","G3")}
    joint_before=client.requests
    with SessionStore(session_path,True) as session, \
            RelationEvidenceStore(registry_root) as routing, \
            ExplorerConfidenceStore(registry_root) as confidence, \
            CapabilityGapStore(registry_root) as gap:
        if (session.checkpoint["attempted_decisions"],len(session.records["events"])) != (
                POLICY["source_attempted_decisions"],POLICY["source_authorized_executions"]):
            raise RoutingError("repair resume source session differs from v0.9 failure")
        request=original_failed_request(session)
        repaired=repair.reissue(client,request)
        if repaired["parsed"] is None:
            return dict(status="REPAIR_FAILED",health=health,new_behavioral_decisions=0,
                        new_model_calls=client.requests-joint_before+1,
                        terminal_classification="REPAIR_FAILED")
        session.configure_regime("A",False)
        runtime=RepairResumeRuntime(session,client,specialist_clients,relation_registry,
            routing,confidence,"A",gap_store=gap)
        capture=runtime.reader.capture()
        runtime.repaired_batch=reconstruct_batch(session,capture,repaired)
        success=next(r for r in reversed(repair.records) if r["state"]=="REPAIR_SUCCEEDED")
        authorized=next(r for r in reversed(repair.records) if r["state"]=="AUTHORIZED")
        reference=dict(lifecycle_state="REPAIR_SUCCEEDED",
            repair_event_sha256=sha256(_canonical(success).encode()).hexdigest(),
            logical_prediction_identity=repair.state["logical_prediction_identity"],
            original_request_sha256=repair.state["original_request_sha256"],
            authorization_sha256=authorized["record"]["authorization_sha256"])
        gap.resume_after_authorized_repair(store=session,repair_reference=reference)
        rows=[]
        for _ in range(POLICY["maximum_new_behavioral_decisions"]):
            row=runtime.execute_autonomous()
            if len(rows)==0: row["model_calls"]=0
            rows.append(row)
            if len(rows)==1:
                repair.resumed(dict(resumed_decision_sequence=row[
                    "prediction_batch_sequence"],status=row["status"],
                    action=row.get("receipt",{}).get("action"),
                    receipt_identity=row.get("receipt",{}).get("source_identity") and [
                        row["receipt"].get(k) for k in ("source_identity","event_id","epoch",
                                                       "transaction_id")],
                    repair_event_is_world_evidence=False))
            if gap.state["terminal_classification"] is not None: break
        normal_calls=(client.requests-joint_before-1)+sum(
            specialist_clients[k].requests-before_specialists[k] for k in ("G2","G3"))
        total_calls=2+normal_calls # one health + one exact reissue + fresh normal calls
        if total_calls>POLICY["maximum_total_live_model_calls"]:
            raise RoutingError("repair continuation exceeded frozen call bound")
        return dict(status=("COMPLETE" if gap.state["terminal_classification"] else
                            "INCONCLUSIVE_AT_BOUND"),rows=rows,
            service_health=health,new_behavioral_decisions=len(rows),
            new_normal_prediction_calls=normal_calls,total_live_model_calls=total_calls,
            operational_health_calls=1,operational_reissue_calls=1,
            terminal_classification=gap.state["terminal_classification"],
            final_problem=deepcopy(gap.state["current_problem"]),
            final_checkpoint=deepcopy(session.checkpoint),
            repair_state=deepcopy(repair.state),source_history_preserved=True,
            longer_horizon_route_implemented=False)


def analyze_repair_resume(session_path:Path,registry_root:Path,run_result:dict,
                          output:Path)->dict:
    """Create a compact public report without raw requests, outputs, or keys."""
    if output.exists(): raise RoutingError("repair report output already exists")
    repair=RepairStore(registry_root)
    with SessionStore(session_path,True) as session,CapabilityGapStore(registry_root) as gap:
        gap.bind_session(session)
        problem=deepcopy(gap.state["current_problem"])
        checkpoint=deepcopy(session.checkpoint)
    lifecycle=[dict(sequence=r["sequence"],state=r["state"],
        event_sha256=sha256(_canonical(r).encode()).hexdigest()) for r in repair.records]
    result=dict(campaign_identity=POLICY["mode"],status=run_result["status"],
        original_failure=dict(logical_prediction_identity=repair.state[
            "logical_prediction_identity"],attempt_1_status="MODEL_SERVICE_FAILURE",
            request_sha256=repair.state["original_request_sha256"],
            response_sha256=repair.state["original_failed_response_sha256"],
            retained=True,overwritten=False),
        repair=dict(allowed_capabilities=POLICY["allowed_capabilities"],
            restart_count=repair.state["restart_count"],reissue_count=repair.state[
                "reissue_count"],lifecycle=lifecycle,exact_replay=True,
            separate_from_behavioral_evidence=True),
        service_restoration=run_result.get("service_health"),
        live_counts={k:run_result.get(k) for k in (
            "new_behavioral_decisions","new_normal_prediction_calls",
            "total_live_model_calls","operational_health_calls","operational_reissue_calls")},
        problem_lineage=dict(source_problem_id=problem["source_problem_id"],
            problem_id=problem["problem_id"],probe_count=problem["probe_count"],
            tied_action_evidence=problem["problem_probe_history"],
            complete_evolution=problem["evolution"]),
        final_capability_assessment=run_result.get("terminal_classification"),
        capability_request=problem.get("requested_capability"),
        localization=problem.get("where_did_resolution_stop"),
        authority_status=("REQUEST_REQUIRES_EXTERNAL_APPROVAL" if problem.get(
            "requested_capability") in ("LONGER_HORIZON_VALUE","EXTERNAL_SERVICE_REPAIR")
            else "PREAUTHORIZED_EXISTING_ROUTE"),
        final_checkpoint=dict(attempted_decisions=checkpoint["attempted_decisions"],
            completed_steps=checkpoint["completed_steps"],runtime_index=checkpoint[
                "runtime_index"],current_state=checkpoint["current_state"],
            streams=checkpoint["streams"]),
        raw_private_model_stream_included=False,repair_key_included=False,
        model_training_performed=False,architecture_changed=False,
        longer_horizon_route_implemented=False)
    atomic_json(output,result); return result
