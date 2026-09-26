"""Authenticated, event-sourced multi-problem ownership for Horus v0.13."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from hmac import compare_digest, new as new_hmac
import fcntl
import json
import os
from pathlib import Path
import secrets
from typing import Any

from experiments.base_framework_v0.framework import ACTION_ORDER

from .core import digest
from .grounded_exploration import GroundedExplorationRuntime, GroundedExplorer
from .live import _canonical, _now, _plain
from .routing import RoutingError


POLICY_PATH = Path(__file__).with_name("problem_ownership_policy.json")
POLICY = json.loads(POLICY_PATH.read_text())
ACTIVE = frozenset(POLICY["active_lifecycle_states"])


def decision_scope(pre_state: int, actions: list[str]) -> dict:
    return {"kind": "decision_state", "pre_state": pre_state,
            "tied_action_set": [a for a in ACTION_ORDER if a in actions]}


def scope_key(problem_type: str, scope: dict) -> str:
    return f"{problem_type}:{_canonical(scope)}"


def _tie(forecasts: dict) -> tuple[list[str], dict]:
    values = {a: forecasts[a]["routed_consequence"] for a in ACTION_ORDER
              if a in forecasts and forecasts[a].get("valid") is True}
    if len(values) != len(ACTION_ORDER):
        return [], values
    maximum = max(values.values())
    return [a for a in ACTION_ORDER if values[a] == maximum], values


def _authority_fields() -> dict:
    return {key: False for key in POLICY["manager_authority"]}


def _imported_problem(snapshot: dict, *, owner: str, assessment: str,
                      route_limit: int, route_executed: int,
                      canonical_state: str | None = None) -> dict:
    """Wrap an exact legacy snapshot without rewriting that source evidence."""
    actions=list(snapshot["candidate_actions"])
    evidence=deepcopy(snapshot.get("problem_probe_history",{}))
    if not evidence:
        evidence={a:[] for a in actions}
        for index,row in enumerate(snapshot.get("receipt_evidence",[])):
            evidence[actions[min(index,len(actions)-1)]].append(deepcopy(row))
    return dict(problem_id=snapshot["problem_id"],
        problem_type=snapshot["problem_type"],
        scope=decision_scope(snapshot["state"],actions),owner=owner,
        lifecycle_state=canonical_state or snapshot["status"],capability_assessment=assessment,
        requested_capability=snapshot.get("requested_capability"),
        created_decision_sequence=snapshot["created_decision_sequence"],
        route_budgets={"relation_information_probe":{
            "limit":route_limit,"granted":snapshot.get("route_request_count",0),
            "executed":route_executed}},
        route_request_count=snapshot.get("route_request_count",0),
        probe_evidence=evidence,evidence=[],
        imported_snapshot=deepcopy(snapshot),imported_snapshot_sha256=digest(snapshot),
        history=[{"lifecycle_state":snapshot["status"],
                  "decision_sequence":snapshot["created_decision_sequence"],
                  "kind":"LEGACY_SNAPSHOT_IMPORTED"}]+([] if canonical_state is None else [{
                  "lifecycle_state":canonical_state,"decision_sequence":54,
                  "kind":"SUCCESSOR_OWNERSHIP_IMPORTED"}]),**_authority_fields())


def initialize_from_v011_evidence(root: Path, evidence_root: Path) -> dict:
    """Import PR-0001/2 and replay decisions 64--83 without inference or routes."""
    evidence_root=evidence_root.resolve()
    route_report=json.loads((evidence_root/"problem-route-request-v0"/
                             "problem-route-report.json").read_text())
    coverage=evidence_root/"bounded-evidence-coverage-v0"
    capability=json.loads((coverage/"capability-gap-state.json").read_text())["payload"]
    checkpoint=json.loads((coverage/"checkpoint.json").read_text())["payload"]
    pr1_snapshot=route_report["problems"][0]
    pr2_snapshot=capability["current_problem"]
    imported=[_imported_problem(pr1_snapshot,owner="EVIDENCE_COVERAGE",
        assessment="MORE_EVIDENCE_REQUIRED",route_limit=2,
        route_executed=pr1_snapshot["probe_count"],canonical_state="SUPERSEDED"),
        _imported_problem(pr2_snapshot,owner="EVIDENCE_COVERAGE",
        assessment=pr2_snapshot["assessment"],route_limit=2,
        route_executed=pr2_snapshot["probe_count"])]
    manager=ProblemManager.create(root,session_id=checkpoint["session_id"],
        attempted_decisions=63,authorized_executions=checkpoint["completed_steps"],
        imported_problems=imported,edges=[dict(from_problem="PR-0002",
            relation="successor_of",to_problem="PR-0001")])
    decision_path=coverage/"new-exploration-decisions.jsonl"
    for line in decision_path.read_text().splitlines():
        envelope=json.loads(line)
        if envelope["kind"]!="EXPLORER_DECISION_FROZEN": continue
        row=envelope["record"]
        manager.replay_decision(pre_state=row["pre_state"],
            ordinary_decision=row["decision"],forecasts=row["forecasts"])
    result=dict(identity="HORUS_PROBLEM_OWNERSHIP_V0_RETROSPECTIVE",
        source_commit="937fc24a68e96f67e901925ecfe0e187d992a539",
        imported_snapshot_sha256={p["problem_id"]:p["imported_snapshot_sha256"] for p in imported},
        attempted_decisions=manager.state["attempted_decisions"],
        authorized_executions=manager.state["authorized_executions"],
        problem_ids=sorted(manager.state["problems"]),
        edges=deepcopy(manager.state["edges"]),
        state1_problem=deepcopy(manager.applicable(pre_state=1,tied_actions=["ADVANCE","HOLD"])),
        state2_problem=deepcopy(manager.applicable(pre_state=2,tied_actions=["ADVANCE","RETREAT"])),
        inference_calls=0,world_executions=0,training_runs=0,
        hidden_simulator_information_used=False)
    manager.close(); return result


class ProblemManager:
    """Authoritative HMAC event history plus a disposable materialized index."""
    KEY = "problem-manager-integrity.key"
    STREAM = "problem-manager-events.jsonl"
    INDEX = "problem-manager-index.json"

    @staticmethod
    def empty_state() -> dict:
        return dict(version=POLICY["version"], session_id=None,
            attempted_decisions=0, authorized_executions=0,
            next_problem_number=1, problems={}, edges=[], tie_candidates={},
            pending_decision=None,deadlock_route_enabled=False,
            deadlock_preregistration_sha256=None,stream_count=0,stream_head_sha256=None)

    @classmethod
    def create(cls, root: Path, *, session_id: str, attempted_decisions: int,
               authorized_executions: int, imported_problems: list[dict],
               edges: list[dict]) -> "ProblemManager":
        root = root.resolve()
        for name in (cls.KEY, cls.STREAM, cls.INDEX):
            if (root / name).exists():
                raise RoutingError("problem manager already exists")
        key = secrets.token_bytes(32)
        descriptor = os.open(root / cls.KEY, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            os.write(descriptor, (key.hex() + "\n").encode()); os.fsync(descriptor)
        finally:
            os.close(descriptor)
        (root / cls.STREAM).touch(mode=0o600)
        manager = cls(root)
        manager._append("MANAGER_INITIALIZED", dict(session_id=session_id,
            attempted_decisions=attempted_decisions,
            authorized_executions=authorized_executions))
        for problem in imported_problems:
            manager._append("PROBLEM_IMPORTED", {"problem": deepcopy(problem)})
        for edge in edges:
            manager.add_edge(**edge)
        return manager

    def __init__(self, root: Path):
        self.root = root.resolve()
        self._lock = (self.root / ".problem-manager.lock").open("a+")
        try:
            fcntl.flock(self._lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RoutingError("problem manager is already open") from exc
        try:
            self._key = bytes.fromhex((self.root / self.KEY).read_text().strip())
            if len(self._key) != 32: raise ValueError
            self.records = self._read_stream()
            self.state = self._replay()
            self._write_index()
        except Exception:
            self.close(); raise

    def close(self):
        if hasattr(self, "_lock") and not self._lock.closed:
            fcntl.flock(self._lock, fcntl.LOCK_UN); self._lock.close()
    def __enter__(self): return self
    def __exit__(self, *_): self.close()

    def _mac(self, value: Any) -> str:
        return new_hmac(self._key, _canonical(value).encode(), "sha256").hexdigest()

    def _read_stream(self) -> list[dict]:
        rows=[]; previous=None
        for sequence,line in enumerate((self.root/self.STREAM).read_text().splitlines(),1):
            try:
                envelope=json.loads(line)
                signed={k:envelope[k] for k in ("sequence","previous_sha256","kind","record")}
            except (ValueError,KeyError,TypeError) as exc:
                raise RoutingError("invalid problem manager record") from exc
            if sequence!=envelope["sequence"] or previous!=envelope["previous_sha256"] or \
                    not compare_digest(self._mac(signed),envelope.get("hmac_sha256","")):
                raise RoutingError("problem manager chain authentication failed")
            rows.append(envelope); previous=sha256(_canonical(envelope).encode()).hexdigest()
        return rows

    def _write_index(self):
        payload=deepcopy(self.state)
        doc={"payload":payload,"hmac_sha256":self._mac(payload)}
        temporary=self.root/(self.INDEX+".tmp")
        with temporary.open("w") as out:
            json.dump(doc,out,indent=2,sort_keys=True); out.write("\n"); out.flush(); os.fsync(out.fileno())
        os.replace(temporary,self.root/self.INDEX)

    def rebuild_index(self) -> dict:
        self.records=self._read_stream(); self.state=self._replay(); self._write_index()
        return deepcopy(self.state)

    def _append(self, kind: str, record: dict) -> dict:
        previous=None if not self.records else sha256(_canonical(self.records[-1]).encode()).hexdigest()
        signed=dict(sequence=len(self.records)+1,previous_sha256=previous,kind=kind,
                    record={**deepcopy(record),"recorded_at":record.get("recorded_at",_now())})
        envelope={**signed,"hmac_sha256":self._mac(signed)}
        with (self.root/self.STREAM).open("a") as out:
            out.write(_canonical(envelope)+"\n"); out.flush(); os.fsync(out.fileno())
        self.records.append(envelope); self._apply(self.state,kind,envelope["record"])
        self.state["stream_count"]=len(self.records)
        self.state["stream_head_sha256"]=sha256(_canonical(envelope).encode()).hexdigest()
        self._write_index(); return deepcopy(envelope)

    def _replay(self) -> dict:
        state=self.empty_state()
        for index,envelope in enumerate(self.records,1):
            self._apply(state,envelope["kind"],envelope["record"])
            state["stream_count"]=index
            state["stream_head_sha256"]=sha256(_canonical(envelope).encode()).hexdigest()
        self._validate_state(state); return state

    @staticmethod
    def _validate_problem(problem: dict):
        if problem["problem_type"] not in POLICY["problem_types"] or \
                problem["lifecycle_state"] not in POLICY["lifecycle_states"]:
            raise RoutingError("unknown canonical problem type/state")
        if problem.get("capability_assessment") is not None and \
                problem["capability_assessment"] not in POLICY["capability_assessments"]:
            raise RoutingError("unknown capability assessment")
        if any(problem.get(k) is not False for k in POLICY["manager_authority"]):
            raise RoutingError("problem manager gained behavioral authority")

    @classmethod
    def _validate_state(cls,state):
        if state["version"]!=POLICY["version"]: raise RoutingError("problem manager version mismatch")
        ids=sorted(state["problems"])
        if ids and state["next_problem_number"]<=max(int(x.split("-")[1]) for x in ids):
            raise RoutingError("problem identity counter regressed")
        for p in state["problems"].values(): cls._validate_problem(p)
        for edge in state["edges"]:
            if edge["relation"] not in POLICY["relationships"] or \
                    edge["from"] not in state["problems"] or edge["to"] not in state["problems"]:
                raise RoutingError("invalid problem relationship")

    @staticmethod
    def _find(state, problem_type: str, scope: dict, active_only=True):
        matches=[p for p in state["problems"].values()
                 if p["problem_type"]==problem_type and p["scope"]==scope and
                 (not active_only or p["lifecycle_state"] in ACTIVE)]
        if len(matches)>1: raise RoutingError("duplicate active problem scope")
        return None if not matches else matches[0]

    @staticmethod
    def _new_tie_problem(state,sequence,pre_state,actions,metadata):
        pid=f"PR-{state['next_problem_number']:04d}"; state["next_problem_number"]+=1
        problem=dict(problem_id=pid,problem_type="UNRESOLVED_VALUE_TIE",
            scope=decision_scope(pre_state,actions),owner="EXPLORER_VALUE_COMPARISON",
            lifecycle_state="OPEN",capability_assessment=None,requested_capability=None,
            created_decision_sequence=sequence,route_budgets={
                "deadlock_information_probe":{"limit":1,"granted":0,"executed":0}},
            route_request_count=0,probe_evidence={a:[] for a in actions},
            evidence=[{"kind":"PERSISTENT_IDENTICAL_TIE","decision_sequence":sequence,
                       "relation_confidence":deepcopy(metadata)}],
            imported_snapshot=None,imported_snapshot_sha256=None,history=[{
                "lifecycle_state":"DETECTED","decision_sequence":sequence},
                {"lifecycle_state":"OPEN","decision_sequence":sequence}],**_authority_fields())
        state["problems"][pid]=problem; return problem

    @classmethod
    def _observe_tie(cls,state,record):
        sequence=record["decision_sequence"]
        if sequence!=state["attempted_decisions"]+1: raise RoutingError("problem decision sequence mismatch")
        state["attempted_decisions"]=sequence
        ordinary=record["ordinary_decision"]; forecasts=record["forecasts"]
        actions,_=_tie(forecasts)
        qualifies=(ordinary.get("reason")=="EXPLOIT_TIED_MAXIMUM" and ordinary.get("abstained") is True
                   and len(actions)>1 and all(forecasts[a].get("valid") is True for a in ACTION_ORDER))
        if not qualifies: return None
        scope=decision_scope(record["pre_state"],actions); key=scope_key("UNRESOLVED_VALUE_TIE",scope)
        candidate=state["tie_candidates"].get(key)
        consecutive=(candidate is not None and candidate["last_decision_sequence"]==sequence-1 and
                     candidate["authorized_execution_count"]==state["authorized_executions"])
        state["tie_candidates"][key]=dict(count=(candidate["count"]+1 if consecutive else 1),
            last_decision_sequence=sequence,authorized_execution_count=state["authorized_executions"])
        problem=cls._find(state,"UNRESOLVED_VALUE_TIE",scope)
        if problem is None and state["tie_candidates"][key]["count"]>=POLICY["persistent_tie_attempts"]:
            problem=cls._new_tie_problem(state,sequence,record["pre_state"],actions,
                                         ordinary["relation_confidence"])
        elif problem is not None:
            problem["evidence"].append(dict(kind="TIE_REOBSERVED",decision_sequence=sequence))
        return problem

    @classmethod
    def _apply(cls,state,kind,record):
        if kind=="MANAGER_INITIALIZED":
            if state["session_id"] is not None: raise RoutingError("manager initialized twice")
            state.update(session_id=record["session_id"],attempted_decisions=record[
                "attempted_decisions"],authorized_executions=record["authorized_executions"])
        elif kind=="PROBLEM_IMPORTED":
            p=deepcopy(record["problem"]); cls._validate_problem(p)
            if p["problem_id"] in state["problems"]: raise RoutingError("duplicate imported problem")
            state["problems"][p["problem_id"]]=p
            state["next_problem_number"]=max(state["next_problem_number"],int(p["problem_id"].split("-")[1])+1)
        elif kind=="PROBLEM_RELATION_ADDED":
            edge={k:record[k] for k in ("from","relation","to")}
            if edge not in state["edges"]: state["edges"].append(edge)
        elif kind=="DEADLOCK_ROUTE_PREREGISTERED":
            if state["deadlock_route_enabled"]: raise RoutingError("deadlock route already preregistered")
            state["deadlock_route_enabled"]=True
            state["deadlock_preregistration_sha256"]=record["preregistration_sha256"]
        elif kind=="ONE_STEP_CAPABILITY_AUTHORIZED":
            p=state["problems"].get(record["problem_id"])
            if not p or p["capability_assessment"]!="CURRENT_OBJECTIVE_CANNOT_DISTINGUISH" or \
                    p["requested_capability"]!="LONGER_HORIZON_VALUE":
                raise RoutingError("one-step authorization lacks the requested capability")
            if "one_step_continuation_value" in p["route_budgets"]:
                raise RoutingError("one-step capability already authorized")
            p["route_budgets"]["one_step_continuation_value"]={"limit":1,"granted":0,"executed":0}
            p["history"].append(dict(lifecycle_state=p["lifecycle_state"],
                decision_sequence=state["attempted_decisions"],kind="CAPABILITY_AUTHORIZED",
                capability="LONGER_HORIZON_VALUE",implementation="ONE_STEP_CONTINUATION_VALUE",
                authorization_sha256=record["authorization_sha256"]))
        elif kind=="ONE_STEP_ROUTE_EVALUATED":
            p=state["problems"].get(record["problem_id"]); budget=p.get("route_budgets",{}).get(
                "one_step_continuation_value") if p else None
            if not budget or budget["granted"]>=budget["limit"]:
                raise RoutingError("one-step route is not authorized or is consumed")
            budget["granted"]+=1; budget["executed"]+=1; p["route_request_count"]+=1
            p["evidence"].append(deepcopy(record["evaluation"])); p["lifecycle_state"]="REASSESSED"
            p["requested_capability"]=(None if record["outcome"]=="ONE_STEP_DISTINGUISHES"
                                       else "DEEPER_HORIZON_VALUE")
            if record["outcome"] not in ("ONE_STEP_DISTINGUISHES","STILL_TIED_AT_ONE_STEP"):
                raise RoutingError("unknown one-step result")
            p["history"].extend([dict(lifecycle_state="ROUTE_REQUESTED",
                decision_sequence=state["attempted_decisions"],route="ONE_STEP_CONTINUATION_VALUE"),
                dict(lifecycle_state="ROUTE_EXECUTED",decision_sequence=state["attempted_decisions"],
                     route="ONE_STEP_CONTINUATION_VALUE"),
                dict(lifecycle_state="REASSESSED",decision_sequence=state["attempted_decisions"],
                     result=record["outcome"],selected_action=record.get("selected_action"))])
        elif kind=="DEPTH2_CAPABILITY_AUTHORIZED":
            p=state["problems"].get(record["problem_id"])
            if not p or p["requested_capability"]!="DEEPER_HORIZON_VALUE":
                raise RoutingError("depth-2 authorization lacks the requested capability")
            if "bounded_depth2_trajectory_value" in p["route_budgets"]:
                raise RoutingError("depth-2 capability already authorized")
            p["route_budgets"]["bounded_depth2_trajectory_value"]={"limit":1,"granted":0,"executed":0}
            p["history"].append(dict(lifecycle_state=p["lifecycle_state"],
                decision_sequence=state["attempted_decisions"],kind="DEEPER_HORIZON_VALUE_AUTHORIZED",
                implementation="BOUNDED_DEPTH2_TRAJECTORY_VALUE",
                authorization_sha256=record["authorization_sha256"]))
        elif kind=="DEPTH2_ROUTE_DESIGN_VALIDATED":
            p=state["problems"].get(record["problem_id"]); budget=(None if not p else
                p.get("route_budgets",{}).get("bounded_depth2_trajectory_value"))
            if not budget or budget["granted"]!=0:
                raise RoutingError("depth-2 design validation is not authorized")
            p["history"].append(dict(lifecycle_state=p["lifecycle_state"],
                decision_sequence=state["attempted_decisions"],kind="ROUTE_DESIGN_VALIDATED",
                route="BOUNDED_DEPTH2_TRAJECTORY_VALUE",
                analysis_sha256=record["analysis_sha256"]))
        elif kind=="DEPTH2_ROUTE_EVALUATED":
            p=state["problems"].get(record["problem_id"]); budget=(None if not p else
                p.get("route_budgets",{}).get("bounded_depth2_trajectory_value"))
            if not budget or budget["granted"]>=budget["limit"]:
                raise RoutingError("depth-2 route is not authorized or is consumed")
            if record["outcome"] not in ("DEPTH2_DISTINGUISHES","STILL_TIED_AT_DEPTH2"):
                raise RoutingError("unknown depth-2 result")
            budget["granted"]+=1; budget["executed"]+=1; p["route_request_count"]+=1
            p["evidence"].append(deepcopy(record["evaluation"])); p["lifecycle_state"]="REASSESSED"
            p["requested_capability"]=(None if record["outcome"]=="DEPTH2_DISTINGUISHES"
                else "ALTERNATIVE_VALUE_REPRESENTATION")
            p["history"].extend([dict(lifecycle_state="ROUTE_EXECUTED",
                decision_sequence=state["attempted_decisions"],route="BOUNDED_DEPTH2_TRAJECTORY_VALUE"),
                dict(lifecycle_state="REASSESSED",decision_sequence=state["attempted_decisions"],
                    result=record["outcome"],selected_action=record.get("selected_action"))])
        elif kind=="OPTION_PROFILE_AUTHORIZED":
            p=state["problems"].get(record["problem_id"])
            if not p or p["capability_assessment"]!="CURRENT_OBJECTIVE_CANNOT_DISTINGUISH" or \
                    p["requested_capability"]!="ALTERNATIVE_VALUE_REPRESENTATION":
                raise RoutingError("option-profile authorization lacks the requested capability")
            if "option_profile_dominance" in p["route_budgets"]:
                raise RoutingError("option-profile representation already authorized")
            p["route_budgets"]["option_profile_dominance"]={"limit":1,"evaluated":0}
            p["history"].append(dict(lifecycle_state=p["lifecycle_state"],
                decision_sequence=state["attempted_decisions"],
                kind="ALTERNATIVE_VALUE_REPRESENTATION_AUTHORIZED",
                representation="OPTION_PROFILE_DOMINANCE",
                authorization_sha256=record["authorization_sha256"]))
        elif kind=="OPTION_PROFILE_EVALUATED":
            p=state["problems"].get(record["problem_id"]); budget=(None if not p else
                p.get("route_budgets",{}).get("option_profile_dominance"))
            if not budget or budget["evaluated"]>=budget["limit"]:
                raise RoutingError("option-profile representation is not authorized or is consumed")
            if record["outcome"] not in ("ADVANCE_PROFILE_DOMINATES","RETREAT_PROFILE_DOMINATES",
                                         "PROFILES_EQUAL","PROFILES_INCOMPARABLE"):
                raise RoutingError("unknown option-profile result")
            budget["evaluated"]+=1; p["evidence"].append(deepcopy(record["evaluation"]))
            p["lifecycle_state"]="REASSESSED"
            p["requested_capability"]=("OPTION_PROFILE_BEHAVIORAL_INTEGRATION"
                if record["outcome"] in ("ADVANCE_PROFILE_DOMINATES","RETREAT_PROFILE_DOMINATES")
                else "ALTERNATIVE_VALUE_REPRESENTATION")
            p["history"].append(dict(lifecycle_state="REASSESSED",
                decision_sequence=state["attempted_decisions"],kind="REPRESENTATION_EVALUATED",
                representation="OPTION_PROFILE_DOMINANCE",result=record["outcome"],
                selected_action=record.get("selected_action")))
        elif kind=="ONE_STEP_EXECUTION_PREPARED":
            if state["pending_decision"] is not None: raise RoutingError("problem decision already pending")
            cls._observe_tie(state,record)
            p=state["problems"].get(record["problem_id"])
            if not p or record["selected_action"] not in p["scope"]["tied_action_set"]:
                raise RoutingError("one-step execution is not bound to its problem")
            final=record["final_decision"]
            if final.get("action")!=record["selected_action"] or final.get("reason")!="ONE_STEP_CONTINUATION_VALUE":
                raise RoutingError("one-step execution decision changed")
            state["pending_decision"]={"decision_sequence":record["decision_sequence"],
                "problem_id":p["problem_id"],"selected_route":"ONE_STEP_CONTINUATION_VALUE",
                "action":record["selected_action"]}
        elif kind=="RETROSPECTIVE_DECISION_REPLAYED":
            cls._observe_tie(state,record)
        elif kind=="LIVE_DECISION_PREPARED":
            if state["pending_decision"] is not None: raise RoutingError("problem decision already pending")
            problem=cls._observe_tie(state,record)
            expected=cls._derive_live(state,record["ordinary_decision"],record["pre_state"],record["forecasts"],problem)
            if expected!=record["final_decision"]: raise RoutingError("problem decision derivation mismatch")
            state["pending_decision"]={"decision_sequence":record["decision_sequence"],
                "problem_id":expected.get("problem_id"),"selected_route":expected.get(
                    "route_broker",{}).get("selected_route"),"action":expected.get("action")}
        elif kind=="LIVE_DECISION_COMPLETED":
            pending=state["pending_decision"]
            if pending is None or pending["decision_sequence"]!=record["decision_sequence"]:
                raise RoutingError("problem completion lacks pending decision")
            if record["status"]=="AUTHORIZED": state["authorized_executions"]+=1
            pid=pending.get("problem_id")
            if pid and pending.get("selected_route")=="DEADLOCK_INFORMATION_PROBE":
                p=state["problems"][pid]
                if record["status"]=="AUTHORIZED":
                    p["lifecycle_state"]="ROUTE_EXECUTED"
                    p["route_budgets"]["deadlock_information_probe"]["executed"]+=1
                    p["probe_evidence"][pending["action"]].append(deepcopy(record["receipt"]))
                    p["history"].append(dict(lifecycle_state="ROUTE_EXECUTED",
                        decision_sequence=record["decision_sequence"],receipt_identity=record[
                            "receipt"]["receipt_identity"]))
                elif record["status"]=="FRAMEWORK_REJECTED":
                    cls._create_operational(state,record["decision_sequence"],"INTERNAL_ROUTE_PROBLEM",
                        {"kind":"runtime","runtime_id":record["runtime_id"]},"RUNTIME_CAPACITY",pid)
            elif pid and pending.get("selected_route")=="ONE_STEP_CONTINUATION_VALUE":
                p=state["problems"][pid]
                if record["status"]=="AUTHORIZED":
                    p["history"].append(dict(lifecycle_state="REASSESSED",
                        decision_sequence=record["decision_sequence"],kind="SELECTED_ACTION_RECEIPT",
                        action=pending["action"],receipt_identity=record["receipt"]["receipt_identity"],
                        realized_consequence=record["receipt"]["realized_consequence"],
                        realized_next_state=record["receipt"]["realized_next_state"]))
                elif record["status"]=="FRAMEWORK_REJECTED":
                    cls._create_operational(state,record["decision_sequence"],"INTERNAL_ROUTE_PROBLEM",
                        {"kind":"runtime","runtime_id":record["runtime_id"]},"RUNTIME_CAPACITY",pid)
            state["pending_decision"]=None
        elif kind=="OPERATIONAL_PROBLEM_ATTACHED":
            cls._create_operational(state,record["decision_sequence"],record["problem_type"],
                record["scope"],record["owner"],record.get("blocked_problem_id"))
        else: raise RoutingError("unknown problem manager event")

    @classmethod
    def _create_operational(cls,state,sequence,problem_type,scope,owner,blocked):
        existing=cls._find(state,problem_type,scope)
        if existing: return existing
        pid=f"PR-{state['next_problem_number']:04d}"; state["next_problem_number"]+=1
        p=dict(problem_id=pid,problem_type=problem_type,scope=deepcopy(scope),owner=owner,
            lifecycle_state="OPEN",capability_assessment="ROUTE_FAILED",
            requested_capability=("EXTERNAL_SERVICE_REPAIR" if problem_type=="EXTERNAL_SERVICE_PROBLEM" else "NEW_RUNTIME"),
            created_decision_sequence=sequence,route_budgets={},route_request_count=0,
            probe_evidence={},evidence=[],imported_snapshot=None,imported_snapshot_sha256=None,
            history=[{"lifecycle_state":"OPEN","decision_sequence":sequence}],**_authority_fields())
        state["problems"][pid]=p
        if blocked: state["edges"].append({"from":blocked,"relation":"blocked_by","to":pid})
        return p

    @classmethod
    def _derive_live(cls,state,ordinary,pre_state,forecasts,observed_problem=None):
        final=deepcopy(ordinary); actions,_=_tie(forecasts)
        problem=observed_problem or cls._find(state,"UNRESOLVED_VALUE_TIE",decision_scope(pre_state,actions))
        final["problem_id"]=None; final["capability_assessment"]=None
        if problem is None: return final
        final["problem_id"]=problem["problem_id"]
        # Preserve the established v0.9 capability assessment independently per problem.
        evidence=problem.get("probe_evidence",{})
        covered=actions and all(evidence.get(a) for a in actions)
        outcomes=[evidence[a][-1]["realized_consequence"] for a in actions if evidence.get(a)]
        if covered and len(set(outcomes))==1 and sum(len(evidence[a]) for a in actions)>=2:
            problem.update(lifecycle_state="REASSESSED",
                capability_assessment="CURRENT_OBJECTIVE_CANNOT_DISTINGUISH",
                requested_capability="LONGER_HORIZON_VALUE")
            problem["history"].append(dict(lifecycle_state="REASSESSED",
                decision_sequence=ordinary["decision_sequence"],
                capability_assessment="CURRENT_OBJECTIVE_CANNOT_DISTINGUISH"))
            final["capability_assessment"]="CURRENT_OBJECTIVE_CANNOT_DISTINGUISH"
            final["route_design_request"]={"requested_capability":"LONGER_HORIZON_VALUE",
                "authority_status":"REQUEST_REQUIRES_EXTERNAL_APPROVAL",
                "authoritative":False,"can_execute":False}
            return final
        budget=problem["route_budgets"].get("deadlock_information_probe")
        eligible=(state["deadlock_route_enabled"] and
            ordinary.get("reason")=="EXPLOIT_TIED_MAXIMUM" and ordinary.get("abstained") is True
            and ordinary.get("probe_budget_available") is False and len(actions)>1
            and all(forecasts[a].get("valid") is True for a in ACTION_ORDER)
            and budget is not None and budget["granted"]<budget["limit"])
        if not eligible:
            if budget and budget["granted"]>=budget["limit"] and ordinary.get("reason")=="EXPLOIT_TIED_MAXIMUM":
                problem["lifecycle_state"]="UNRESOLVED"
                problem["history"].append(dict(lifecycle_state="UNRESOLVED",
                    decision_sequence=ordinary["decision_sequence"],reason="DEADLOCK_ROUTE_ALLOWANCE_EXHAUSTED"))
            return final
        metadata=ordinary["relation_confidence"]
        def key(action):
            row=metadata[action]; age=row["observations_since_last_execution"]
            return (bool(problem["probe_evidence"].get(action)),not row["specialists_disagree"],
                row["unresolved_recent_contradiction"] is None,row["authenticated_observations"],
                -(10**9 if age is None else age),ACTION_ORDER.index(action))
        selected=min(actions,key=key); budget["granted"]+=1; problem["route_request_count"]+=1
        problem["lifecycle_state"]="ROUTE_REQUESTED"
        problem["history"].append(dict(lifecycle_state="ROUTE_REQUESTED",
            decision_sequence=ordinary["decision_sequence"],route="DEADLOCK_INFORMATION_PROBE",action=selected))
        final.update(mode="PROBE",action=selected,reason="DEADLOCK_INFORMATION_PROBE",
            abstained=False,tied_maximum_actions=actions,
            route_broker={"selected_route":"DEADLOCK_INFORMATION_PROBE","broker_result":"ROUTE_GRANTED",
                "requested_capability":"MORE_RELATION_EVIDENCE","authoritative":False},
            deadlock_information_priority={"unprobed":not problem["probe_evidence"].get(selected),
                "specialists_disagree":metadata[selected]["specialists_disagree"],
                "unresolved_contradiction":metadata[selected]["unresolved_recent_contradiction"] is not None,
                "authenticated_observations":metadata[selected]["authenticated_observations"],
                "observations_since_last_execution":metadata[selected]["observations_since_last_execution"],
                "canonical_action_index":ACTION_ORDER.index(selected)})
        return final

    def add_edge(self, *, from_problem: str, relation: str, to_problem: str):
        if relation not in POLICY["relationships"]: raise RoutingError("unknown relationship")
        return self._append("PROBLEM_RELATION_ADDED",{"from":from_problem,"relation":relation,"to":to_problem})

    def preregister_deadlock_route(self, preregistration_sha256: str):
        if len(preregistration_sha256)!=64: raise RoutingError("invalid preregistration hash")
        return self._append("DEADLOCK_ROUTE_PREREGISTERED",{
            "preregistration_sha256":preregistration_sha256})

    def authorize_one_step(self, problem_id: str, authorization_sha256: str):
        if len(authorization_sha256)!=64:
            raise RoutingError("invalid one-step authorization hash")
        return self._append("ONE_STEP_CAPABILITY_AUTHORIZED",{
            "problem_id":problem_id,"authorization_sha256":authorization_sha256})

    def record_one_step_evaluation(self, *, problem_id: str, outcome: str,
                                   selected_action: str | None, evaluation: dict):
        return self._append("ONE_STEP_ROUTE_EVALUATED",dict(problem_id=problem_id,
            outcome=outcome,selected_action=selected_action,evaluation=deepcopy(evaluation)))

    def authorize_depth2(self, problem_id: str, authorization_sha256: str):
        if len(authorization_sha256)!=64: raise RoutingError("invalid depth-2 authorization hash")
        return self._append("DEPTH2_CAPABILITY_AUTHORIZED",{
            "problem_id":problem_id,"authorization_sha256":authorization_sha256})

    def validate_depth2_design(self, problem_id: str, analysis_sha256: str):
        if len(analysis_sha256)!=64: raise RoutingError("invalid depth-2 analysis hash")
        return self._append("DEPTH2_ROUTE_DESIGN_VALIDATED",{
            "problem_id":problem_id,"analysis_sha256":analysis_sha256})

    def record_depth2_evaluation(self, *, problem_id: str, outcome: str,
                                 selected_action: str | None, evaluation: dict):
        return self._append("DEPTH2_ROUTE_EVALUATED",dict(problem_id=problem_id,
            outcome=outcome,selected_action=selected_action,evaluation=deepcopy(evaluation)))

    def authorize_option_profile(self, problem_id: str, authorization_sha256: str):
        if len(authorization_sha256)!=64: raise RoutingError("invalid option-profile authorization hash")
        return self._append("OPTION_PROFILE_AUTHORIZED",{
            "problem_id":problem_id,"authorization_sha256":authorization_sha256})

    def record_option_profile(self, *, problem_id: str, outcome: str,
                              selected_action: str | None, evaluation: dict):
        return self._append("OPTION_PROFILE_EVALUATED",dict(problem_id=problem_id,
            outcome=outcome,selected_action=selected_action,evaluation=deepcopy(evaluation)))

    def prepare_one_step_execution(self, *, store, ordinary_decision: dict,
                                   pre_state: int, forecasts: dict,
                                   problem_id: str, selected_action: str) -> dict:
        self.bind_session(store); final=deepcopy(ordinary_decision)
        if ordinary_decision.get("reason")=="INVALID_MAP_COMPONENT":
            raise RoutingError("one-step execution integration predictions invalid")
        final.update(mode="PROBE",action=selected_action,abstained=False,
            reason="ONE_STEP_CONTINUATION_VALUE",problem_id=problem_id,
            route_broker={"selected_route":"ONE_STEP_CONTINUATION_VALUE",
                "broker_result":"EXPLICIT_V014_AUTHORIZATION","authoritative":False})
        record=dict(decision_sequence=ordinary_decision["decision_sequence"],pre_state=pre_state,
            ordinary_decision=deepcopy(ordinary_decision),forecasts=deepcopy(forecasts),
            problem_id=problem_id,selected_action=selected_action,final_decision=deepcopy(final),
            hidden_regime_available=False,simulator_law_available=False,
            future_consequence_available=False,counterfactual_outcomes_available=False)
        self._append("ONE_STEP_EXECUTION_PREPARED",record); return final

    def replay_decision(self, *, pre_state: int, ordinary_decision: dict, forecasts: dict):
        if self.state["pending_decision"] is not None: raise RoutingError("pending live decision")
        return self._append("RETROSPECTIVE_DECISION_REPLAYED",dict(
            decision_sequence=ordinary_decision["decision_sequence"],pre_state=pre_state,
            ordinary_decision=deepcopy(ordinary_decision),forecasts=deepcopy(forecasts),
            hidden_regime_available=False,simulator_law_available=False,
            future_consequence_available=False,counterfactual_outcomes_available=False))

    def applicable(self, *, pre_state: int, tied_actions: list[str]):
        return deepcopy(self._find(self.state,"UNRESOLVED_VALUE_TIE",
                                   decision_scope(pre_state,tied_actions)))

    def prepare(self, *, store, ordinary_decision: dict, pre_state: int, forecasts: dict):
        self.bind_session(store)
        record=dict(decision_sequence=ordinary_decision["decision_sequence"],pre_state=pre_state,
            ordinary_decision=deepcopy(ordinary_decision),forecasts=deepcopy(forecasts),
            hidden_regime_available=False,simulator_law_available=False,
            future_consequence_available=False,counterfactual_outcomes_available=False)
        temp=deepcopy(self.state); problem=self._observe_tie(temp,record)
        record["final_decision"]=self._derive_live(temp,record["ordinary_decision"],pre_state,forecasts,problem)
        self._append("LIVE_DECISION_PREPARED",record)
        return deepcopy(record["final_decision"])

    def complete(self, *, store, row: dict):
        receipt=row.get("receipt"); compact=None
        if receipt is not None:
            compact=dict(receipt_identity=[receipt[k] for k in ("source_identity","event_id","epoch","transaction_id")],
                action=receipt["action"],realized_consequence=receipt["realized_consequence"],
                realized_next_state=receipt["next_state"],receipt_is_authenticated=True)
        record=dict(decision_sequence=row["prediction_batch_sequence"],status=row["status"],receipt=compact,
                    runtime_id=row.get("source_scope",{}).get("source_identity"))
        self._append("LIVE_DECISION_COMPLETED",record); self.bind_session(store)
        return deepcopy(record)

    def attach_operational(self, **record):
        return self._append("OPERATIONAL_PROBLEM_ATTACHED",record)

    def bind_session(self,store):
        if self.state["session_id"]!=store.checkpoint["session_id"]:
            raise RoutingError("problem manager belongs to another session")
        pending=self.state["pending_decision"]
        expected_attempts=store.checkpoint["attempted_decisions"]+(pending is not None)
        if self.state["attempted_decisions"]!=expected_attempts or \
                self.state["authorized_executions"]!=len(store.records["events"]):
            raise RoutingError("problem manager/session history mismatch")


class ProblemManagedExplorer:
    def __init__(self,ordinary,manager,store): self.ordinary,self.manager,self.store=ordinary,manager,store
    def derive(self,**kwargs):
        ordinary=self.ordinary.derive(**kwargs)
        return self.manager.prepare(store=self.store,ordinary_decision=ordinary,
            pre_state=kwargs["pre_state"],forecasts=kwargs["forecasts"])


class ProblemOwnershipRuntime(GroundedExplorationRuntime):
    def __init__(self,*args,problem_manager: ProblemManager,**kwargs):
        super().__init__(*args,**kwargs); self.problem_manager=problem_manager
        problem_manager.bind_session(self.store)
        self.confidence_store.explorer=ProblemManagedExplorer(
            GroundedExplorer(self.confidence_store.registry["policy"]),problem_manager,self.store)
    def execute_autonomous(self):
        row=super().execute_autonomous()
        row["problem_manager_completion"]=self.problem_manager.complete(store=self.store,row=row)
        return row
