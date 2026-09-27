"""Finite capability-gap assessment layered over completed Horus v0.8 history."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from hashlib import sha256
from hmac import compare_digest, new as new_hmac
import fcntl
import json
import os
from pathlib import Path
import secrets
from typing import Any, TypedDict

from experiments.base_framework_v0.framework import ACTION_ORDER
from experiments.base_framework_v1.framework import EPISODE_LIMIT

from .core import digest
from .grounded_exploration import (ExplorerConfidenceStore,
    GroundedExplorationRuntime, GroundedExplorer)
from .grounded_learning import atomic_json, file_hash
from .live import ModelClient, SessionStore, _canonical, _now, _plain
from .relation_routing import (RelationEvidenceStore, SPECIALISTS,
                               relation_routed_clients)
from .routing import RoutingError


POLICY_PATH = Path(__file__).with_name("capability_gap_policy.json")
CAPABILITY_GAP_VERSION = 1
SOURCE_REPORT_SHA256 = "4e73a7383c7557253602cbee690c5d0b7cdf9e126d8c97217a266b60249fb11e"


class DownstreamValueRouteInput(TypedDict):
    current_state: int
    action: str
    authenticated_immediate_consequence: int
    predicted_next_state: int
    authenticated_history_reference: dict


class DownstreamValueRouteOutput(TypedDict):
    secondary_value: int | float
    comparison_basis: str
    evidence_references: list[dict]


class CapabilityAssessor:
    """Pure finite mappings from grounded failure facts to capability requests."""
    def __init__(self, policy: dict | None = None):
        self.policy = policy or json.loads(POLICY_PATH.read_text())

    def request(self, capability: str) -> dict:
        if capability not in self.policy["capabilities"]:
            raise RoutingError("unknown capability request")
        automatic = capability in self.policy["automatic_grants"]
        return dict(requested_capability=capability,
            authority_status=("PREAUTHORIZED_EXISTING_ROUTE" if automatic else
                              "REQUEST_REQUIRES_EXTERNAL_APPROVAL"),
            authoritative=False, can_execute=False, can_make_model_calls=False,
            can_change_objective=False, can_create_architecture=False,
            can_train=False, can_inspect_hidden_law=False)

    def localize(self, *, invalid_next_state: bool = False,
                 invalid_consequence: bool = False,
                 service_failure: bool = False,
                 runtime_exhausted: bool = False,
                 tied: bool = False, coverage_complete: bool = False) -> str:
        if service_failure: value = "MODEL_SERVICE"
        elif runtime_exhausted: value = "RUNTIME_CAPACITY"
        elif invalid_next_state: value = "MAP_NEXT_STATE"
        elif invalid_consequence: value = "MAP_CONSEQUENCE"
        elif tied and not coverage_complete: value = "EVIDENCE_COVERAGE"
        elif tied: value = "REPRESENTATION"
        else: value = "EXPLORER_VALUE_COMPARISON"
        if value not in self.policy["localizations"]:
            raise RoutingError("unregistered failure localization")
        return value

    def repeated_specialist_error(self, *, shared_grounded_errors: int,
                                  sufficiently_observed: bool,
                                  same_prediction: bool) -> dict:
        qualifies = sufficiently_observed and same_prediction and \
            shared_grounded_errors >= self.policy["common_specialist_error_minimum"]
        capability = "NEW_SPECIALIST" if qualifies else "ALTERNATIVE_REPRESENTATION"
        return {**self.request(capability), "rule_satisfied": qualifies,
                "shared_grounded_errors": shared_grounded_errors,
                "minimum": self.policy["common_specialist_error_minimum"]}


def _document(payload: dict) -> dict:
    return {"payload": payload, "sha256": digest(payload)}


def _read_document(path: Path, label: str) -> dict:
    try:
        document = json.loads(path.read_text()); payload = document["payload"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise RoutingError(f"invalid {label}") from exc
    if digest(payload) != document.get("sha256"):
        raise RoutingError(f"{label} hash mismatch")
    return document


class CapabilityGapStore:
    KEY = "capability-gap-integrity.key"
    STATE = "capability-gap-state.json"
    STREAM = "capability-gap-events.jsonl"

    @staticmethod
    def initialize(root: Path, source_report: Path) -> None:
        policy = json.loads(POLICY_PATH.read_text())
        if file_hash(source_report) != SOURCE_REPORT_SHA256:
            raise RoutingError("v0.8 source report differs from frozen evidence")
        report = json.loads(source_report.read_text())
        source = next((row for row in report["problems"]
                       if row["problem_id"] == policy["source_problem_id"]), None)
        if source is None or source["status"] != "UNRESOLVED" or \
                source["problem_type"] != policy["source_problem_type"]:
            raise RoutingError("required unresolved v0.8 source problem is absent")
        root = root.resolve()
        for name in (CapabilityGapStore.KEY, CapabilityGapStore.STATE,
                     CapabilityGapStore.STREAM):
            if (root / name).exists():
                raise RoutingError("capability gap store already exists")
        key = secrets.token_bytes(32)
        fd = os.open(root / CapabilityGapStore.KEY,
                     os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try: os.write(fd, (key.hex() + "\n").encode()); os.fsync(fd)
        finally: os.close(fd)
        state = dict(version=CAPABILITY_GAP_VERSION,
            session_id=report["final_checkpoint"]["session_id"],
            source_attempted_decisions=54, attempted_decisions=54,
            source_authorized_executions=50, authorized_executions=50,
            source_problem=deepcopy(source), current_problem=None,
            terminal_classification=None, pending_decision=None,
            stream_count=0, stream_head_sha256=None, updated_at=_now())
        source_event = dict(event="SOURCE_PROBLEM_IMPORTED",
            source_problem_id=source["problem_id"], source_status=source["status"],
            source_report_sha256=SOURCE_REPORT_SHA256,
            source_problem_sha256=digest(source), imported_at=_now(),
            history_rewritten=False)
        signed = dict(sequence=1, previous_sha256=None,
                      kind="CAPABILITY_GAP_HISTORY_IMPORTED", record=source_event)
        envelope = {**signed, "hmac_sha256": new_hmac(
            key, _canonical(signed).encode(), "sha256").hexdigest()}
        (root / CapabilityGapStore.STREAM).write_text(_canonical(envelope) + "\n")
        state.update(stream_count=1,
            stream_head_sha256=sha256(_canonical(envelope).encode()).hexdigest())
        CapabilityGapStore._write_state_file(root, key, state)

    @staticmethod
    def _write_state_file(root: Path, key: bytes, state: dict) -> None:
        payload = deepcopy(state); payload["updated_at"] = _now()
        document = {"payload": payload, "hmac_sha256": new_hmac(
            key, _canonical(payload).encode(), "sha256").hexdigest()}
        temporary = root / (CapabilityGapStore.STATE + ".tmp")
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            os.write(fd, (json.dumps(document, indent=2, sort_keys=True)+"\n").encode())
            os.fsync(fd)
        finally: os.close(fd)
        os.replace(temporary, root / CapabilityGapStore.STATE)

    def __init__(self, root: Path):
        self.registry = load_capability_gap_registry(root)
        self.root, self.policy = self.registry["root"], self.registry["policy"]
        self.assessor = CapabilityAssessor(self.policy)
        self._lock = (self.root / ".capability-gap.lock").open("a+")
        try: fcntl.flock(self._lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RoutingError("capability gap store is already open") from exc
        try:
            self._key = bytes.fromhex((self.root / self.KEY).read_text().strip())
            if len(self._key) != 32: raise ValueError
            self.state = self._read_state(); self.records = self._read_stream()
            self._validate_replay()
        except Exception:
            self.close(); raise

    def close(self):
        if hasattr(self, "_lock") and not self._lock.closed:
            fcntl.flock(self._lock, fcntl.LOCK_UN); self._lock.close()
    def __enter__(self): return self
    def __exit__(self, *_): self.close()
    def _mac(self, value):
        return new_hmac(self._key, _canonical(value).encode(), "sha256").hexdigest()
    def _read_state(self):
        try:
            doc=json.loads((self.root/self.STATE).read_text()); payload=doc["payload"]
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise RoutingError("invalid capability gap state") from exc
        if not compare_digest(self._mac(payload), doc.get("hmac_sha256", "")):
            raise RoutingError("capability gap state authentication failed")
        return payload
    def _read_stream(self):
        rows=[]; previous=None
        for sequence,line in enumerate((self.root/self.STREAM).read_text().splitlines(),1):
            try:
                env=json.loads(line); signed={k:env[k] for k in
                    ("sequence","previous_sha256","kind","record")}
            except (ValueError,KeyError,TypeError) as exc:
                raise RoutingError("invalid capability gap record") from exc
            if env["sequence"]!=sequence or env["previous_sha256"]!=previous or \
                    not compare_digest(self._mac(signed),env.get("hmac_sha256","")):
                raise RoutingError("capability gap chain authentication failed")
            previous=sha256(_canonical(env).encode()).hexdigest(); rows.append(env)
        return rows
    def _append(self, kind, record):
        previous=None if not self.records else sha256(
            _canonical(self.records[-1]).encode()).hexdigest()
        record={**deepcopy(record),"recorded_at":record.get("recorded_at",_now())}
        signed=dict(sequence=len(self.records)+1,previous_sha256=previous,
                    kind=kind,record=_plain(record))
        env={**signed,"hmac_sha256":self._mac(signed)}
        with (self.root/self.STREAM).open("a") as stream:
            stream.write(_canonical(env)+"\n"); stream.flush(); os.fsync(stream.fileno())
        self.records.append(env); self.state["stream_count"]=len(self.records)
        self.state["stream_head_sha256"]=sha256(_canonical(env).encode()).hexdigest()
        return env
    def _write_state(self):
        self.state["updated_at"]=_now(); self._write_state_file(self.root,self._key,self.state)

    def _validate_replay(self):
        if not self.records or self.records[0]["kind"] != "CAPABILITY_GAP_HISTORY_IMPORTED":
            raise RoutingError("capability gap source history is absent")
        freezes=[r for r in self.records if r["kind"]=="CAPABILITY_GAP_DECISION_FROZEN"]
        completes=[r for r in self.records if r["kind"]=="CAPABILITY_GAP_DECISION_COMPLETED"]
        if len(freezes)!=len(completes)+(self.state.get("pending_decision") is not None):
            raise RoutingError("capability gap decision journal is incomplete")
        if self.state["attempted_decisions"] != 54+len(completes) or \
                self.state["stream_count"]!=len(self.records) or \
                self.state["stream_head_sha256"]!=sha256(
                    _canonical(self.records[-1]).encode()).hexdigest():
            raise RoutingError("capability gap state/stream replay mismatch")
        projections=[r for r in self.records if r["kind"] in (
            "CAPABILITY_GAP_DECISION_COMPLETED",
            "AUTHORIZED_OPERATIONAL_REPAIR_RESUME_BOUND")]
        if projections:
            projection=projections[-1]["record"]["state_projection_after"]
            actual={k:self.state[k] for k in
                ("attempted_decisions","authorized_executions",
                 "current_problem","terminal_classification")}
            if projection!=actual:
                raise RoutingError("capability gap state does not replay")

    def bind_session(self, store: SessionStore, allow_pending=False):
        if self.state["session_id"]!=store.checkpoint["session_id"] or \
                self.state["attempted_decisions"]!=store.checkpoint["attempted_decisions"] or \
                self.state["authorized_executions"]!=len(store.records["events"]):
            raise RoutingError("capability gap/session history mismatch")
        if self.state["pending_decision"] is not None and not allow_pending:
            raise RoutingError("incomplete capability gap decision")

    def resume_after_authorized_repair(self, *, store: SessionStore,
                                       repair_reference: dict) -> dict:
        """Prospectively reopen only the unresolved service-blocked route.

        The terminal v0.9 completion remains in the append-only stream.  This
        record binds an independently authorized operational repair to the
        unchanged problem budget; it does not add a decision, receipt, Memory
        record, routing observation, or training target.
        """
        self.bind_session(store)
        problem=self.state.get("current_problem")
        if self.state.get("terminal_classification")!="ROUTE_FAILED" or not problem or \
                problem.get("assessment")!="ROUTE_FAILED" or \
                problem.get("where_did_resolution_stop")!="MODEL_SERVICE" or \
                problem.get("requested_capability")!="EXTERNAL_SERVICE_REPAIR":
            raise RoutingError("no service-blocked capability route to resume")
        if problem.get("probe_count")!=1 or len(problem[
                "problem_probe_history"].get("ADVANCE",[]))!=1 or problem[
                "problem_probe_history"].get("RETREAT"):
            raise RoutingError("problem evidence differs from frozen repair scope")
        required={"repair_event_sha256","logical_prediction_identity",
                  "original_request_sha256","authorization_sha256"}
        if not required.issubset(repair_reference) or \
                repair_reference.get("lifecycle_state")!="REPAIR_SUCCEEDED":
            raise RoutingError("authorized successful repair proof is absent")
        problem.update(assessment="MORE_EVIDENCE_REQUIRED",status="OPEN",
            where_did_resolution_stop="EVIDENCE_COVERAGE",
            requested_capability="MORE_RELATION_EVIDENCE")
        problem["evolution"].append(dict(
            decision_sequence=self.state["attempted_decisions"],
            events=["AUTHORIZED_OPERATIONAL_REPAIR_BOUND",
                    "UNRESOLVED_PROBLEM_RESUMED"],
            repair_reference=deepcopy(repair_reference),
            recorded_before_execution=True))
        self.state["terminal_classification"]=None
        projection={k:deepcopy(self.state[k]) for k in
            ("attempted_decisions","authorized_executions","current_problem",
             "terminal_classification")}
        record=dict(repair_reference=deepcopy(repair_reference),
            problem_id=problem["problem_id"],probe_count_preserved=problem["probe_count"],
            advance_probe_repeated=False,retreat_probe_still_missing=True,
            behavioral_evidence_created=False,memory_mutated=False,
            routing_evidence_created=False,training_target_created=False,
            state_projection_after=projection)
        env=self._append("AUTHORIZED_OPERATIONAL_REPAIR_RESUME_BOUND",record)
        self._write_state()
        self.bind_session(store)
        return deepcopy(env["record"])

    @staticmethod
    def _tied_actions(forecasts):
        if not all(row["valid"] for row in forecasts.values()): return []
        maximum=max(row["routed_consequence"] for row in forecasts.values())
        return [a for a in ACTION_ORDER if forecasts[a]["routed_consequence"]==maximum]

    def _new_problem(self, sequence, state, actions, forecasts):
        source=self.state["source_problem"]
        return dict(problem_id=self.policy["successor_problem_id"],
            source_problem_id=source["problem_id"], problem_type="UNRESOLVED_VALUE_TIE",
            created_decision_sequence=sequence, state=state,
            candidate_actions=actions, initial_forecasts=deepcopy(forecasts),
            problem_probe_history={a:[] for a in actions},
            assessment="MORE_EVIDENCE_REQUIRED", where_did_resolution_stop="EVIDENCE_COVERAGE",
            requested_capability="MORE_RELATION_EVIDENCE", status="OPEN",
            route_request_count=0, probe_count=0, evolution=[],
            authoritative=False, can_execute=False, can_make_model_calls=False,
            can_change_objective=False, can_create_architecture=False,
            can_train=False, can_inspect_hidden_law=False)

    def _probe_action(self, problem, metadata):
        actions=problem["candidate_actions"]
        def key(action):
            row=metadata[action]; unprobed=not problem["problem_probe_history"][action]
            age=row["observations_since_last_execution"]
            return (not unprobed, not row["specialists_disagree"],
                row["unresolved_recent_contradiction"] is None,
                row["authenticated_observations"],-(10**9 if age is None else age),
                ACTION_ORDER.index(action))
        selected=min(actions,key=key)
        return selected,dict(unprobed_for_problem=not problem[
            "problem_probe_history"][selected],specialists_disagree=metadata[selected][
            "specialists_disagree"],unresolved_contradiction=metadata[selected][
            "unresolved_recent_contradiction"] is not None,
            authenticated_observations=metadata[selected]["authenticated_observations"],
            observations_since_last_execution=metadata[selected][
                "observations_since_last_execution"],canonical_action_index=ACTION_ORDER.index(selected),
            priority_order=self.policy["tie_probe_priority"])

    def prepare(self, *, store, ordinary_decision, pre_state, forecasts):
        self.bind_session(store); sequence=ordinary_decision["decision_sequence"]
        if sequence!=self.state["attempted_decisions"]+1:
            raise RoutingError("capability gap sequence mismatch")
        final=deepcopy(ordinary_decision); final["ordinary_decision_sha256"]=digest(ordinary_decision)
        final.update(problem_id=None,capability_assessment=None,route_design_request=None)
        actions=self._tied_actions(forecasts)
        tied=ordinary_decision["reason"]=="EXPLOIT_TIED_MAXIMUM" and len(actions)>1
        problem=self.state["current_problem"]; evolution=[]
        if tied and problem is None and pre_state==self.state["source_problem"]["state"] and \
                actions==self.state["source_problem"]["candidate_actions"]:
            problem=self._new_problem(sequence,pre_state,actions,forecasts)
            self.state["current_problem"]=problem
            evolution.append("SUCCESSOR_PROBLEM_OPENED_FROM_UNRESOLVED_V0_8_HISTORY")
        if problem is not None and pre_state==problem["state"]:
            final["problem_id"]=problem["problem_id"]
            if not all(row["valid"] for row in forecasts.values()):
                problem.update(assessment="ROUTE_FAILED",status="UNRESOLVED",
                    where_did_resolution_stop="MODEL_SERVICE",
                    requested_capability="EXTERNAL_SERVICE_REPAIR")
                request=self.assessor.request("EXTERNAL_SERVICE_REPAIR")
                final.update(capability_assessment="ROUTE_FAILED",route_design_request=request)
                evolution.append("ROUTE_FAILED")
            elif not tied:
                problem.update(assessment="VALUE_TIE_RESOLVED",status="RESOLVED",
                    where_did_resolution_stop="EXPLORER_VALUE_COMPARISON",
                    requested_capability=None)
                final["capability_assessment"]="VALUE_TIE_RESOLVED"
                evolution.append("VALUE_TIE_RESOLVED")
            else:
                covered=all(problem["problem_probe_history"][a] for a in actions)
                outcomes=[problem["problem_probe_history"][a][-1]["realized_consequence"]
                          for a in actions if problem["problem_probe_history"][a]]
                if covered and len(set(outcomes))==1 and problem["probe_count"]>=2:
                    request=self.assessor.request("LONGER_HORIZON_VALUE")
                    design=dict(kind="ROUTE_DESIGN_REQUEST",problem_id=problem["problem_id"],
                        source_problem=problem["problem_type"],
                        observed_limitation="IMMEDIATE_CONSEQUENCE_DOES_NOT_DISTINGUISH_TIED_ACTIONS",
                        tied_actions=actions,
                        grounded_immediate_outcomes={a:problem["problem_probe_history"][a][-1][
                            "realized_consequence"] for a in actions},
                        authenticated_realized_next_states={a:problem[
                            "problem_probe_history"][a][-1]["realized_next_state"] for a in actions},
                        predicted_next_states={a:forecasts[a]["next_state"] for a in actions},
                        requested_capability="LONGER_HORIZON_VALUE",
                        authority_status=request["authority_status"],
                        predictions_are_authenticated_receipts=False,
                        outcomes_are_authenticated_receipts=True,**{k:v for k,v in request.items()
                            if k not in ("requested_capability","authority_status")})
                    problem.update(assessment="CURRENT_OBJECTIVE_CANNOT_DISTINGUISH",
                        status="UNRESOLVED",where_did_resolution_stop="REPRESENTATION",
                        requested_capability="LONGER_HORIZON_VALUE")
                    final.update(capability_assessment="CURRENT_OBJECTIVE_CANNOT_DISTINGUISH",
                                 route_design_request=design)
                    evolution.append("CAPABILITY_ESCALATION_REQUESTED")
                    self.state["terminal_classification"]="CURRENT_OBJECTIVE_CANNOT_DISTINGUISH"
                elif problem["probe_count"]<self.policy["maximum_tie_information_probes"]:
                    action,priority=self._probe_action(problem,ordinary_decision["relation_confidence"])
                    request=self.assessor.request("MORE_RELATION_EVIDENCE")
                    problem.update(assessment="MORE_EVIDENCE_REQUIRED",status="ROUTE_REQUESTED",
                        where_did_resolution_stop="EVIDENCE_COVERAGE",
                        requested_capability="MORE_RELATION_EVIDENCE",
                        route_request_count=problem["route_request_count"]+1)
                    final.update(mode="PROBE",action=action,reason="PROBE_TIED_MAXIMUM",
                        abstained=False,capability_assessment="MORE_EVIDENCE_REQUIRED",
                        tied_maximum_actions=actions,tie_information_priority=priority,
                        route_broker={**request,"selected_route":"TIE_INFORMATION_PROBE"})
                    evolution.append("PROBLEM_SPECIFIC_PROBE_REQUESTED")
                else:
                    problem.update(assessment="MORE_EVIDENCE_REQUIRED",status="UNRESOLVED")
                    final["capability_assessment"]="MORE_EVIDENCE_REQUIRED"
                    evolution.append("PROBE_COVERAGE_INCOMPLETE_AT_BOUND")
        if problem is not None:
            problem["evolution"].append(dict(decision_sequence=sequence,events=evolution,
                                              recorded_before_execution=True))
        record=dict(decision_sequence=sequence,pre_state=pre_state,
            ordinary_decision=deepcopy(ordinary_decision),forecasts=deepcopy(forecasts),
            final_decision=deepcopy(final),evolution_events=evolution,
            hidden_regime_available=False,simulator_law_available=False,
            future_consequence_available=False,counterfactual_outcomes_available=False)
        env=self._append("CAPABILITY_GAP_DECISION_FROZEN",record)
        self.state["pending_decision"]=dict(decision_sequence=sequence,
                                            frozen_record_sha256=digest(env["record"]))
        self._write_state(); return deepcopy(final)

    def complete(self, *, store, row):
        frozen=next(r["record"] for r in reversed(self.records)
                    if r["kind"]=="CAPABILITY_GAP_DECISION_FROZEN")
        final=frozen["final_decision"]; sequence=frozen["decision_sequence"]
        if row["prediction_batch_sequence"]!=sequence: raise RoutingError("completion mismatch")
        problem=self.state["current_problem"]; receipt=None
        if row["status"]=="AUTHORIZED":
            self.state["authorized_executions"]+=1
            if problem and final.get("problem_id")==problem["problem_id"] and \
                    final.get("reason")=="PROBE_TIED_MAXIMUM":
                action=final["action"]; receipt=dict(action=action,
                    attempted_decision_sequence=sequence,
                    predicted_next_state=frozen["forecasts"][action]["next_state"],
                    prediction_is_descriptive_model_output=True,
                    receipt_identity=list(row["receipt"].get(k) for k in
                        ("source_identity","event_id","epoch","transaction_id")),
                    realized_consequence=row["receipt"]["realized_consequence"],
                    realized_next_state=row["receipt"]["next_state"],
                    receipt_is_authenticated=True,
                    routing_evidence_sequence=row["routing_evidence"]["evidence_sequence"])
                problem["problem_probe_history"][action].append(receipt)
                problem["probe_count"]+=1; problem["status"]="ROUTE_EXECUTED"
                problem["evolution"].append(dict(decision_sequence=sequence,
                    events=["AUTHENTICATED_PROBLEM_PROBE_EVIDENCE_ACQUIRED"],
                    receipt_reference=receipt["receipt_identity"]))
        elif row["status"]=="FRAMEWORK_REJECTED":
            if problem:
                problem.update(assessment="ROUTE_FAILED",status="UNRESOLVED",
                    where_did_resolution_stop="RUNTIME_CAPACITY",
                    requested_capability="NEW_RUNTIME")
                self.state["terminal_classification"]="ROUTE_FAILED"
        elif row["status"]!="ABSTAINED": raise RoutingError("unknown completion status")
        if final.get("capability_assessment") in (
                "VALUE_TIE_RESOLVED","ROUTE_FAILED"):
            self.state["terminal_classification"]=final["capability_assessment"]
        self.state["attempted_decisions"]+=1; self.state["pending_decision"]=None
        projection={k:deepcopy(self.state[k]) for k in
            ("attempted_decisions","authorized_executions","current_problem",
             "terminal_classification")}
        record=dict(decision_sequence=sequence,status=row["status"],
            action=final.get("action"),problem_id=final.get("problem_id"),
            assessment=final.get("capability_assessment"),receipt=receipt,
            state_projection_after=projection)
        self._append("CAPABILITY_GAP_DECISION_COMPLETED",record); self._write_state()
        self.bind_session(store); return deepcopy(record)


def initialize_capability_gap_registry(root: Path, source_report: Path) -> dict:
    root=root.resolve(); policy=json.loads(POLICY_PATH.read_text())
    if not (root/"problem-route-registry.json").is_file():
        raise RoutingError("v0.8 registry history is absent")
    source_registry=_read_document(root/"problem-route-registry.json","v0.8 registry")
    payload=dict(version=CAPABILITY_GAP_VERSION,mode=policy["mode"],created_at=_now(),
        policy_sha256=file_hash(POLICY_PATH),source_report_sha256=SOURCE_REPORT_SHA256,
        source_problem_route_registry_sha256=source_registry["sha256"],
        source_problem_preserved=True,weights_modified=False,
        longer_horizon_route_implemented=False,hidden_regime_available=False,
        protected_episode_limit=EPISODE_LIMIT)
    atomic_json(root/"capability-gap-registry.json",_document(payload))
    CapabilityGapStore.initialize(root,source_report)
    return dict(root=str(root),registry_sha256=digest(payload))


def load_capability_gap_registry(root: Path) -> dict:
    root=root.resolve(); policy=json.loads(POLICY_PATH.read_text())
    doc=_read_document(root/"capability-gap-registry.json","capability gap registry")
    payload=doc["payload"]
    if payload.get("version")!=CAPABILITY_GAP_VERSION or payload.get("mode")!=policy["mode"] or \
            payload.get("policy_sha256")!=file_hash(POLICY_PATH) or \
            payload.get("source_report_sha256")!=SOURCE_REPORT_SHA256 or \
            payload.get("source_problem_preserved") is not True or \
            payload.get("weights_modified") is not False or \
            payload.get("longer_horizon_route_implemented") is not False or \
            payload.get("hidden_regime_available") is not False or \
            payload.get("protected_episode_limit")!=EPISODE_LIMIT:
        raise RoutingError("capability gap registry violates frozen policy")
    return dict(root=root,document=doc,payload=payload,policy=policy)


class GapAwareExplorer:
    def __init__(self, ordinary, gap, store): self.ordinary,self.gap,self.store=ordinary,gap,store
    def derive(self, **kwargs):
        ordinary=self.ordinary.derive(**kwargs)
        return self.gap.prepare(store=self.store,ordinary_decision=ordinary,
            pre_state=kwargs["pre_state"],forecasts=kwargs["forecasts"])


class CapabilityGapRuntime(GroundedExplorationRuntime):
    def __init__(self,*args,gap_store,**kwargs):
        super().__init__(*args,**kwargs); self.gap_store=gap_store
        gap_store.bind_session(self.store)
        self.confidence_store.explorer=GapAwareExplorer(
            GroundedExplorer(self.confidence_store.registry["policy"]),gap_store,self.store)
    def execute_autonomous(self):
        row=super().execute_autonomous()
        row["capability_gap_completion"]=self.gap_store.complete(store=self.store,row=row)
        return row


def run_capability_gap_campaign(session: Path, registry_root: Path,
                                joint_client=None, specialist_clients=None) -> dict:
    registry=load_capability_gap_registry(registry_root)
    if specialist_clients is None:
        specialist_clients,relation_registry=relation_routed_clients(registry_root,device="cuda")
    else:
        from .relation_routing import load_relation_routing_registry
        relation_registry=load_relation_routing_registry(registry_root)
    joint=joint_client or ModelClient(); before={k:specialist_clients[k].requests for k in SPECIALISTS}
    joint_before=joint.requests
    with SessionStore(session,True) as store,RelationEvidenceStore(registry_root) as routing,\
            ExplorerConfidenceStore(registry_root) as confidence,CapabilityGapStore(registry_root) as gap:
        if store.checkpoint["attempted_decisions"]!=54 or len(store.records["events"])!=50:
            raise RoutingError("v0.9 source session differs from completed v0.8")
        store.configure_regime("A",False)
        runtime=CapabilityGapRuntime(store,joint,specialist_clients,relation_registry,
            routing,confidence,"A",gap_store=gap)
        rows=[]
        for _ in range(registry["policy"]["maximum_live_decisions"]):
            rows.append(runtime.execute_autonomous())
            if gap.state["terminal_classification"] is not None: break
        calls=joint.requests-joint_before+sum(specialist_clients[k].requests-before[k]
                                               for k in SPECIALISTS)
        return dict(identity=registry["policy"]["mode"],rows=rows,
            new_decisions=len(rows),new_model_calls=calls,
            terminal_classification=gap.state["terminal_classification"],
            final_problem=deepcopy(gap.state["current_problem"]),
            final_checkpoint=deepcopy(store.checkpoint),
            final_gap_state=deepcopy(gap.state),
            source_history_preserved=True,hidden_regime_available=False,
            calibration_executions=0)


def analyze_capability_gap_campaign(session: Path,registry_root: Path,output: Path) -> dict:
    if output.exists(): raise RoutingError("capability gap report output already exists")
    with SessionStore(session,True) as store,RelationEvidenceStore(registry_root) as routing,\
            ExplorerConfidenceStore(registry_root) as confidence,CapabilityGapStore(registry_root) as gap:
        gap.bind_session(store); records=deepcopy(gap.records); state=deepcopy(gap.state)
        calls=deepcopy(store.records["calls"]); events=deepcopy(store.records["events"])
        checkpoint=deepcopy(store.checkpoint)
    new_requests=[r for r in calls if r["kind"]=="REQUEST_INTENT"][486:]
    new_events=events[50:]
    if len(new_requests)%9 or len(new_requests)>108:
        raise RoutingError("v0.9 call bound violated")
    for row in new_requests:
        text=json.dumps(row["record"]["request"],sort_keys=True).lower()
        if any(token in text for token in ("regime","simulator_law","capability_gap",
                                           "route_design_request","future_consequence")):
            raise RoutingError("hidden capability state entered model prompt")
    decisions=[r["record"] for r in records if r["kind"]=="CAPABILITY_GAP_DECISION_FROZEN"]
    problem=state["current_problem"]
    result=dict(identity="HORUS_CAPABILITY_GAP_DETECTION_V0",
        source_problem_id="PR-0001",source_problem_status="UNRESOLVED",
        new_model_calls=len(new_requests),new_decisions=len(decisions),
        new_authorized_executions=len(new_events),
        new_abstentions=len(decisions)-len(new_events),
        problem=problem,complete_problem_evolution=problem["evolution"],
        distinct_tied_action_receipts={a:problem["problem_probe_history"][a]
                                       for a in problem["candidate_actions"]},
        immediate_evidence_resolved_tie=problem["assessment"]=="VALUE_TIE_RESOLVED",
        capability_request=problem["requested_capability"],
        authority_status=(None if problem["requested_capability"] is None else
            CapabilityAssessor().request(problem["requested_capability"])["authority_status"]),
        terminal_classification=state["terminal_classification"],
        hidden_input_checks=len(new_requests),calibration_executions=0,
        restart_replay=dict(source_attempts=54,source_receipts=50,
            runtime_index=checkpoint["runtime_index"],capability_gap_exact_replay=True,
            source_problem_history_rewritten=False,probe_budget_preserved=True,
            protected_episode_limit=EPISODE_LIMIT),
        final_checkpoint=checkpoint,final_gap_state=state)
    atomic_json(output,result); return result
