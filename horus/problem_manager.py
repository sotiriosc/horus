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
from .relation_routing import relation_identity
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
        elif kind=="OPTION_PROFILE_BEHAVIORAL_INTEGRATION_AUTHORIZED":
            p=state["problems"].get(record["problem_id"]); representation=(None if not p else
                p.get("route_budgets",{}).get("option_profile_dominance"))
            if not p or p["problem_id"]!="PR-0002" or p["scope"]!=decision_scope(
                    2,["ADVANCE","RETREAT"]) or \
                    p["requested_capability"]!="OPTION_PROFILE_BEHAVIORAL_INTEGRATION" or \
                    not representation or representation.get("evaluated")!=representation.get("limit"):
                raise RoutingError("option-profile integration lacks the evaluated PR-0002 request")
            if record["result"]!="RETREAT_PROFILE_DOMINATES" or record["selected_action"]!="RETREAT":
                raise RoutingError("option-profile integration authorization changed the retained result")
            if "option_profile_behavioral_integration" in p["route_budgets"]:
                raise RoutingError("option-profile integration already authorized")
            p["route_budgets"]["option_profile_behavioral_integration"]={
                "limit":1,"granted":0,"executed":0,"follow_up_limit":1,"follow_up_observed":0,
                "authorization_sha256":record["authorization_sha256"],
                "profile_evidence_sha256":record["profile_evidence_sha256"]}
            p["history"].append(dict(lifecycle_state=p["lifecycle_state"],
                decision_sequence=state["attempted_decisions"],
                kind="OPTION_PROFILE_BEHAVIORAL_INTEGRATION_AUTHORIZED",
                representation="OPTION_PROFILE_DOMINANCE",result=record["result"],
                selected_action=record["selected_action"],
                authorization_sha256=record["authorization_sha256"],
                profile_evidence_sha256=record["profile_evidence_sha256"]))
        elif kind=="OPTION_PROFILE_DECISION_FROZEN":
            if state["pending_decision"] is not None: raise RoutingError("problem decision already pending")
            observed=cls._observe_tie(state,record); p=state["problems"].get(record["problem_id"])
            budget=(None if not p else p.get("route_budgets",{}).get(
                "option_profile_behavioral_integration"))
            if observed is None or observed["problem_id"]!=record["problem_id"] or \
                    not p or p["problem_id"]!="PR-0002" or record["pre_state"]!=2 or \
                    p["scope"]!=decision_scope(2,["ADVANCE","RETREAT"]) or \
                    not budget or budget["granted"]>=budget["limit"]:
                raise RoutingError("option-profile integration is outside its scoped allowance")
            actions,_=_tie(record["forecasts"]); ordinary=record["ordinary_decision"]
            if actions!=["ADVANCE","RETREAT"] or ordinary.get("reason")!="EXPLOIT_TIED_MAXIMUM" or \
                    ordinary.get("abstained") is not True or \
                    record["result"]!="RETREAT_PROFILE_DOMINATES" or \
                    record["selected_action"]!="RETREAT" or \
                    record["profile_evidence_sha256"]!=budget["profile_evidence_sha256"]:
                raise RoutingError("option-profile integration preconditions changed")
            final=record["final_decision"]
            if final.get("action")!="RETREAT" or final.get("abstained") is not False or \
                    final.get("reason")!="OPTION_PROFILE_DOMINANCE":
                raise RoutingError("option-profile frozen action changed")
            budget["granted"]+=1; p["route_request_count"]+=1
            p["history"].append(dict(lifecycle_state=p["lifecycle_state"],
                decision_sequence=record["decision_sequence"],kind="OPTION_PROFILE_DECISION_FROZEN",
                representation="OPTION_PROFILE_DOMINANCE",result=record["result"],
                selected_action="RETREAT",ordinary_decision_sha256=record[
                    "ordinary_decision_sha256"],current_predictions_sha256=record[
                    "current_predictions_sha256"],profiles_sha256=record["profiles_sha256"]))
            state["pending_decision"]={"decision_sequence":record["decision_sequence"],
                "problem_id":"PR-0002","selected_route":"OPTION_PROFILE_DOMINANCE",
                "action":"RETREAT","expected_consequence":1,"expected_next_state":1}
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
        elif kind in ("LIVE_DECISION_COMPLETED","SCOPED_RELATION_PROBE_EXECUTED",
                      "GROUNDED_RELATION_REACQUISITION_EXECUTED"):
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
            elif pid and pending.get("selected_route")=="OPTION_PROFILE_DOMINANCE":
                p=state["problems"][pid]; budget=p["route_budgets"][
                    "option_profile_behavioral_integration"]
                if record["status"]=="AUTHORIZED":
                    receipt=record["receipt"]
                    if receipt is None or receipt["action"]!=pending["action"]:
                        raise RoutingError("option-profile execution receipt changed the frozen action")
                    budget["executed"]+=1
                    consistent=(receipt["realized_consequence"]==pending["expected_consequence"] and
                                receipt["realized_next_state"]==pending["expected_next_state"])
                    classification=("INTEGRATION_EXECUTED_CONSISTENT" if consistent else
                                    "INTEGRATION_EXECUTED_CONTRADICTED")
                    p["evidence"].append(dict(kind="OPTION_PROFILE_REALITY_OBSERVED",
                        decision_sequence=record["decision_sequence"],action=pending["action"],
                        receipt=deepcopy(receipt),retained_expectation={"consequence":pending[
                            "expected_consequence"],"next_state":pending["expected_next_state"]},
                        classification=classification))
                    p["history"].extend([
                        dict(lifecycle_state="ROUTE_EXECUTED",decision_sequence=record[
                            "decision_sequence"],kind="ROUTE_EXECUTED",route="OPTION_PROFILE_DOMINANCE",
                            action=pending["action"],receipt_identity=receipt["receipt_identity"]),
                        dict(lifecycle_state="ROUTE_EXECUTED",decision_sequence=record[
                            "decision_sequence"],kind="REALITY_OBSERVED",classification=classification,
                            realized_consequence=receipt["realized_consequence"],
                            realized_next_state=receipt["realized_next_state"]),
                        dict(lifecycle_state="REASSESSED",decision_sequence=record[
                            "decision_sequence"],kind="REASSESSED",result=classification)])
                    p["lifecycle_state"]="REASSESSED"; p["requested_capability"]=None
                    p["option_profile_integration_result"]=classification
                else:
                    classification="INTEGRATION_FAILED_OPERATIONALLY"
                    p["lifecycle_state"]="REASSESSED"; p["option_profile_integration_result"]=classification
                    p["history"].append(dict(lifecycle_state="REASSESSED",
                        decision_sequence=record["decision_sequence"],kind="REASSESSED",
                        result=classification,status=record["status"]))
                    if record["status"]=="FRAMEWORK_REJECTED":
                        cls._create_operational(state,record["decision_sequence"],"INTERNAL_ROUTE_PROBLEM",
                            {"kind":"runtime","runtime_id":record["runtime_id"]},"RUNTIME_CAPACITY",pid)
            elif pid and pending.get("selected_route")=="GROUNDED_RELATION_REACQUISITION":
                p=state["problems"][pid]; budget=p["route_budgets"][
                    "grounded_relation_reacquisition"]
                if record["status"]=="AUTHORIZED":
                    receipt=record["receipt"]
                    if receipt is None or receipt["action"]!=pending["action"]:
                        raise RoutingError("reacquisition receipt changed the frozen action")
                    budget["executed"]+=1
                    reacquired=receipt["realized_next_state"]==budget["target_state"]
                    p["target_relation_reacquired"]=reacquired
                    p["reacquisition_status"]=("TARGET_RELATION_REACQUIRED" if reacquired else
                                                "REACQUISITION_TRANSITION_CONTRADICTED")
                    p["history"].append(dict(lifecycle_state=p["lifecycle_state"],
                        decision_sequence=record["decision_sequence"],kind=p[
                            "reacquisition_status"],route="GROUNDED_RELATION_REACQUISITION",
                        action=pending["action"],receipt_identity=receipt["receipt_identity"],
                        realized_next_state=receipt["realized_next_state"],
                        supporting_receipt_identity=deepcopy(budget[
                            "supporting_receipt_identity"])))
                elif record["status"]=="FRAMEWORK_REJECTED":
                    cls._create_operational(state,record["decision_sequence"],"INTERNAL_ROUTE_PROBLEM",
                        {"kind":"runtime","runtime_id":record["runtime_id"]},"RUNTIME_CAPACITY",pid)
            elif pid and pending.get("selected_route")=="PROBLEM_SCOPED_RELATION_PROBE":
                p=state["problems"][pid]; budget=p["route_budgets"][
                    "problem_scoped_relation_probe"]
                if record["status"]=="AUTHORIZED":
                    receipt=record["receipt"]; routing=record.get("routing_evidence")
                    if receipt is None or receipt["action"]!="ADVANCE" or not routing or \
                            routing.get("relation")!=budget["relation"]:
                        raise RoutingError("scoped relation receipt/routing binding changed")
                    budget["executed"]+=1
                    p["probe_evidence"]["ADVANCE"].append(deepcopy(receipt))
                    switched=bool(routing["switch_occurred"])
                    scores=routing["router_score_after"]
                    threshold_satisfied=(scores["G2"]["total"]>=3 and abs(
                        scores["G2"]["correct"]-scores["G3"]["correct"])>=2)
                    p["lifecycle_state"]="REASSESSED"
                    p["capability_assessment"]=("VALUE_TIE_RESOLVED" if threshold_satisfied else
                                                "MORE_EVIDENCE_REQUIRED")
                    p["requested_capability"]=(None if threshold_satisfied else
                                                "MORE_RELATION_EVIDENCE")
                    p["evidence"].append(dict(kind="PROBLEM_SCOPED_RELATION_RECEIPT",
                        decision_sequence=record["decision_sequence"],receipt=deepcopy(receipt),
                        routing_evidence=deepcopy(routing)))
                    p["history"].extend([dict(lifecycle_state="ROUTE_EXECUTED",
                        decision_sequence=record["decision_sequence"],
                        kind="SCOPED_RELATION_PROBE_EXECUTED",
                        route="PROBLEM_SCOPED_RELATION_PROBE",action="ADVANCE",
                        receipt_identity=receipt["receipt_identity"]),
                        dict(lifecycle_state="REASSESSED",decision_sequence=record[
                            "decision_sequence"],kind="REASSESSED",
                            switch_occurred=switched,selected_specialist_after=routing[
                                "selected_specialist_after"],scores=scores,
                            switch_threshold_satisfied=threshold_satisfied)])
                elif record["status"]=="FRAMEWORK_REJECTED":
                    cls._create_operational(state,record["decision_sequence"],"INTERNAL_ROUTE_PROBLEM",
                        {"kind":"runtime","runtime_id":record["runtime_id"]},"RUNTIME_CAPACITY",pid)
            state["pending_decision"]=None
        elif kind=="OPTION_PROFILE_FOLLOWUP_OBSERVED":
            if state["pending_decision"] is not None: raise RoutingError("follow-up observed while decision pending")
            p=state["problems"].get(record["problem_id"]); budget=(None if not p else
                p.get("route_budgets",{}).get("option_profile_behavioral_integration"))
            if not p or p["problem_id"]!="PR-0002" or not budget or budget["executed"]!=1 or \
                    budget["follow_up_observed"]>=budget["follow_up_limit"] or \
                    record["decision_sequence"]!=state["attempted_decisions"]+1:
                raise RoutingError("ordinary follow-up exceeds its scoped allowance")
            if record["explorer"].get("reason")=="OPTION_PROFILE_DOMINANCE":
                raise RoutingError("option-profile representation controlled the ordinary follow-up")
            if record["status"]=="AUTHORIZED":
                if record.get("receipt") is None: raise RoutingError("authorized follow-up lacks receipt")
                state["authorized_executions"]+=1
            elif record["status"] not in ("ABSTAINED","FRAMEWORK_REJECTED"):
                raise RoutingError("unknown ordinary follow-up status")
            state["attempted_decisions"]=record["decision_sequence"]
            budget["follow_up_observed"]+=1
            p["history"].append(dict(lifecycle_state=p["lifecycle_state"],
                decision_sequence=record["decision_sequence"],kind="ORDINARY_FOLLOW_UP_OBSERVED",
                status=record["status"],action=record["explorer"].get("action"),
                reason=record["explorer"].get("reason"),receipt=deepcopy(record.get("receipt")),
                suffix_prefix_check=deepcopy(record.get("suffix_prefix_check")),
                option_profile_controlled=False))
        elif kind=="OPERATIONAL_REPAIR_LIFECYCLE":
            p=state["problems"].get(record["problem_id"]); stage=record["stage"]
            if not p or p["problem_id"]!="PR-0004" or \
                    p["problem_type"]!="EXTERNAL_SERVICE_PROBLEM":
                raise RoutingError("operational repair is not bound to PR-0004")
            previous=p.get("operational_repair_state")
            required={"REPAIR_REQUESTED":None,"REPAIR_AUTHORIZED":"REPAIR_REQUESTED",
                "REPAIR_ATTEMPTED":"REPAIR_AUTHORIZED","REPAIR_SUCCEEDED":"REPAIR_ATTEMPTED",
                "REISSUE_ATTEMPTED":"REPAIR_SUCCEEDED","RESUMED":"REISSUE_ATTEMPTED"}
            if stage=="REPAIR_FAILED":
                if previous not in ("REPAIR_ATTEMPTED","REISSUE_ATTEMPTED"):
                    raise RoutingError("repair failure lacks an attempted repair or reissue")
            elif stage not in required or previous!=required[stage]:
                raise RoutingError("operational repair lifecycle order changed")
            if stage=="REPAIR_REQUESTED":
                if p.get("requested_capability")!="EXTERNAL_SERVICE_REPAIR" or \
                        record["capabilities"]!=["RESTART_MODEL_SERVICE","VERIFY_MODEL_ARTIFACT",
                            "REISSUE_UNEXECUTED_PREDICTION_REQUEST"]:
                    raise RoutingError("unsupported operational repair request")
                p["operational_repair_budget"]={"service_restarts":0,"reissues":0,
                    "maximum_service_restarts":1,"maximum_reissues":1}
            elif stage=="REPAIR_AUTHORIZED":
                if len(record.get("authorization_sha256",""))!=64:
                    raise RoutingError("operational repair authorization is not committed")
            elif stage=="REPAIR_ATTEMPTED":
                budget=p["operational_repair_budget"]
                if budget["service_restarts"]>=budget["maximum_service_restarts"]:
                    raise RoutingError("operational service-repair allowance consumed")
                budget["service_restarts"]+=1
            elif stage=="REISSUE_ATTEMPTED":
                budget=p["operational_repair_budget"]
                if budget["reissues"]>=budget["maximum_reissues"]:
                    raise RoutingError("operational transport-reissue allowance consumed")
                budget["reissues"]+=1
            elif stage=="RESUMED":
                if record["decision_sequence"]!=state["attempted_decisions"]+1 or \
                        record["status"] not in ("AUTHORIZED","ABSTAINED","FRAMEWORK_REJECTED"):
                    raise RoutingError("resumed ordinary decision does not continue the session")
                state["attempted_decisions"]=record["decision_sequence"]
                if record["status"]=="AUTHORIZED":
                    if not record.get("receipt") or record["receipt"].get(
                            "receipt_is_authenticated") is not True:
                        raise RoutingError("resumed execution lacks authenticated receipt")
                    state["authorized_executions"]+=1
                p["lifecycle_state"]="CLOSED"; p["requested_capability"]=None
                p["operational_repair_result"]=record["outcome"]
            elif stage=="REPAIR_FAILED":
                p["operational_repair_result"]="REPAIR_FAILED"
                p["requested_capability"]=None
            p["operational_repair_state"]=stage
            p["history"].append(dict(lifecycle_state=p["lifecycle_state"],
                decision_sequence=record.get("decision_sequence",state["attempted_decisions"]),
                kind=stage,details=deepcopy(record.get("details")),
                repair_is_behavioral_evidence=False,memory_mutated=False,
                training_target_created=False))
        elif kind=="OPERATIONAL_PROBLEM_ATTACHED":
            cls._create_operational(state,record["decision_sequence"],record["problem_type"],
                record["scope"],record["owner"],record.get("blocked_problem_id"))
        elif kind=="UNCOMMITTED_AUTHENTICATED_CALL_TAIL":
            p=state["problems"].get(record.get("problem_id"))
            checks=record.get("safety_conditions",{})
            required={"tail_authenticated","chain_continuous","single_unfinished_decision",
                "no_receipt","no_memory_publication","no_routing_evidence",
                "no_explorer_completion","no_contradictory_state"}
            if not p or p["problem_id"]!="PR-0005" or p[
                    "problem_type"]!="INTERNAL_ROUTE_PROBLEM" or \
                    set(checks)!=required or not all(checks.values()) or \
                    record.get("checkpoint_count")!=2502 or record.get(
                    "physical_count")!=2529 or record.get("tail_records")!=27 or \
                    record.get("decision_sequence")!=91:
                raise RoutingError("unsafe authenticated-call-tail diagnosis")
            evidence=dict(kind="UNCOMMITTED_AUTHENTICATED_CALL_TAIL",
                decision_sequence=91,checkpoint_count=2502,physical_count=2529,
                tail_records=27,logical_decision_id=record["logical_decision_id"],
                safety_conditions=deepcopy(checks),tail_head_sha256=record[
                    "tail_head_sha256"])
            p["evidence"].append(evidence)
            p["history"].append(dict(lifecycle_state=p["lifecycle_state"],
                decision_sequence=91,kind="UNCOMMITTED_AUTHENTICATED_CALL_TAIL",
                tail_records=27))
        elif kind=="DURABLE_TAIL_RECOVERED":
            p=state["problems"].get(record.get("problem_id"))
            diagnosed=bool(p and any(row.get("kind")==
                "UNCOMMITTED_AUTHENTICATED_CALL_TAIL" for row in p.get("evidence",[])))
            if not diagnosed or record.get("registered_count")!=2529 or \
                    len(record.get("registered_head_sha256",""))!=64 or record.get(
                    "stream_records_rewritten") is not False or record.get(
                    "model_calls_reissued") is not False:
                raise RoutingError("durable tail recovery lacks exact diagnosis")
            p["durable_tail_recovery"]="RECOVERED"
            p["history"].append(dict(lifecycle_state=p["lifecycle_state"],
                decision_sequence=91,kind="DURABLE_TAIL_RECOVERED",
                registered_count=2529,registered_head_sha256=record[
                    "registered_head_sha256"]))
        elif kind=="NORMAL_ROUTE_REGAINS_CONTROL":
            p5=state["problems"].get(record.get("problem_id"))
            p3=state["problems"].get(record.get("blocked_problem_id"))
            ordinary=record.get("ordinary_decision",{})
            if not p5 or p5["problem_id"]!="PR-0005" or not p3 or p3[
                    "problem_id"]!="PR-0003" or p3.get(
                    "target_relation_reacquired") is not True or \
                    p5.get("durable_tail_recovery")!="RECOVERED" or \
                    ordinary.get("mode")!="PROBE" or ordinary.get(
                    "reason")!="PROBE_DISAGREEMENT" or ordinary.get(
                    "action")!="ADVANCE" or ordinary.get("abstained") is not False or \
                    record.get("selected_route")!="ORDINARY_EXPLORER" or record.get(
                    "scoped_fallback_superseded") is not True:
                raise RoutingError("ordinary route handoff proof changed")
            p5["handoff_status"]="NORMAL_ROUTE_REGAINS_CONTROL"
            p5["history"].append(dict(lifecycle_state=p5["lifecycle_state"],
                decision_sequence=91,kind="NORMAL_ROUTE_REGAINS_CONTROL",
                route="ORDINARY_EXPLORER",action="ADVANCE"))
        elif kind=="NORMAL_ROUTE_EVIDENCE_REASSESSED":
            p=state["problems"].get(record.get("problem_id"))
            routing=record.get("routing_evidence",{}); receipt=record.get("receipt",{})
            budget=(None if not p else p.get("route_budgets",{}).get(
                "problem_scoped_relation_probe"))
            if not p or p["problem_id"]!="PR-0003" or record.get(
                    "decision_sequence")!=state["attempted_decisions"] or \
                    routing.get("relation")!=relation_identity(1,"ADVANCE") or \
                    receipt.get("receipt_is_authenticated") is not True or receipt.get(
                    "action")!="ADVANCE" or budget is None or \
                    (budget["limit"],budget["granted"],budget["executed"])!=(2,1,1):
                raise RoutingError("ordinary route reassessment is not scoped correctly")
            scores=routing["router_score_after"]
            resolved=(scores["G2"]["total"]>=3 and abs(scores["G2"]["correct"]-
                      scores["G3"]["correct"])>=2)
            if resolved!=record.get("switch_threshold_satisfied"):
                raise RoutingError("ordinary route reassessment threshold changed")
            p["lifecycle_state"]="REASSESSED"
            p["capability_assessment"]=("VALUE_TIE_RESOLVED" if resolved else
                                        "MORE_EVIDENCE_REQUIRED")
            p["requested_capability"]=(None if resolved else "MORE_RELATION_EVIDENCE")
            p["evidence"].append(dict(kind="ORDINARY_RELATION_RECEIPT",
                decision_sequence=record["decision_sequence"],receipt=deepcopy(receipt),
                routing_evidence=deepcopy(routing),scoped_budget_consumed=False))
            p["history"].append(dict(lifecycle_state="REASSESSED",
                decision_sequence=record["decision_sequence"],
                kind="NORMAL_ROUTE_EVIDENCE_REASSESSED",scores=deepcopy(scores),
                selected_specialist_after=routing["selected_specialist_after"],
                switch_occurred=routing["switch_occurred"],
                scoped_budget_consumed=False))
        elif kind=="ROUTE_HANDOFF_REPAIR_CLOSED":
            p=state["problems"].get(record.get("problem_id"))
            if not p or p["problem_id"]!="PR-0005" or p.get(
                    "durable_tail_recovery")!="RECOVERED" or p.get(
                    "handoff_status")!="NORMAL_ROUTE_REGAINS_CONTROL" or record.get(
                    "model_calls_issued")!=0 or record.get("decision_status")!="AUTHORIZED":
                raise RoutingError("route-handoff repair closure lacks completed proof")
            p["lifecycle_state"]="CLOSED"; p["capability_assessment"]=None
            p["requested_capability"]=None; p["repair_result"]="ROUTE_HANDOFF_RECOVERED"
            p["history"].append(dict(lifecycle_state="CLOSED",
                decision_sequence=state["attempted_decisions"],
                kind="ROUTE_HANDOFF_REPAIR_CLOSED",model_calls_issued=0))
        elif kind=="RELATION_EVIDENCE_REQUESTED":
            p=state["problems"].get(record.get("problem_id"))
            relation=record.get("relation",{})
            if not p or p["problem_type"]!="UNRESOLVED_VALUE_TIE" or \
                    relation.get("pre_state")!=p["scope"]["pre_state"] or \
                    relation.get("action") not in p["scope"]["tied_action_set"] or \
                    relation.get("identity_sha256")!=digest({"pre_state":relation.get(
                        "pre_state"),"action":relation.get("action")}):
                raise RoutingError("relation-evidence request is outside problem scope")
            if record.get("classification")!="ROUTING_CORRECT_AS_FROZEN" or \
                    record.get("requested_capability")!="MORE_RELATION_EVIDENCE" or \
                    record.get("requested_route")!="RELATION_PROBE" or \
                    record.get("authority_status")!="REQUEST_REQUIRES_EXTERNAL_APPROVAL" or \
                    record.get("selected_route") is not None:
                raise RoutingError("relation-evidence request invented route authority")
            scores=record.get("current_scores",{}); latest=record.get(
                "latest_grounded_comparison",{})
            if record.get("selected_specialist")!="G2" or set(scores)!={"G2","G3"} or \
                    scores["G2"].get("total")!=scores["G3"].get("total") or \
                    scores["G3"].get("correct")-scores["G2"].get("correct")>=2 or \
                    latest!={"G2_correct":False,"G3_correct":True} or \
                    record.get("route_availability",{}).get(
                        "existing_route_legally_available") is not False:
                raise RoutingError("relation evidence does not justify an external request")
            if record.get("reason")!=\
                    "RELATION_SPECIFIC_EVIDENCE_INSUFFICIENT_FOR_SPECIALIST_SELECTION" or \
                    record.get("hidden_transition_destination_used") is not False or \
                    record.get("option_profile_used") is not False:
                raise RoutingError("relation-evidence request changed its scoped reason")
            duplicate=any(row.get("kind")=="RELATION_EVIDENCE_REQUESTED" and
                row.get("relation")==relation for row in p["history"])
            if duplicate: raise RoutingError("duplicate relation-evidence request")
            p["lifecycle_state"]="ROUTE_REQUESTED"
            p["capability_assessment"]="MORE_EVIDENCE_REQUIRED"
            p["requested_capability"]="MORE_RELATION_EVIDENCE"
            p["route_request_count"]+=1
            evidence={k:deepcopy(record[k]) for k in (
                "relation","classification","latest_evidence_sequence",
                "latest_grounded_comparison","current_scores",
                "selected_specialist","route_availability")}
            evidence["kind"]="SCOPED_RELATION_REASSESSMENT"
            p["evidence"].append(evidence)
            p["history"].append(dict(lifecycle_state="ROUTE_REQUESTED",
                decision_sequence=state["attempted_decisions"],
                kind="RELATION_EVIDENCE_REQUESTED",relation=deepcopy(relation),
                requested_capability="MORE_RELATION_EVIDENCE",
                requested_route="RELATION_PROBE",
                authority_status="REQUEST_REQUIRES_EXTERNAL_APPROVAL",
                reason=record["reason"]))
        elif kind=="TARGET_RELATION_NOT_CURRENT":
            p=state["problems"].get(record.get("problem_id")); relation=record.get("target_relation",{})
            budget=(None if not p else p.get("route_budgets",{}).get(
                "problem_scoped_relation_probe"))
            if not p or p["problem_id"]!="PR-0003" or p.get(
                    "requested_capability")!="MORE_RELATION_EVIDENCE" or \
                    relation!=relation_identity(1,"ADVANCE") or record.get(
                    "current_state")!=2 or budget is None or \
                    budget["executed"]>=budget["limit"]:
                raise RoutingError("target-relation-not-current condition changed")
            if any(row.get("kind")=="TARGET_RELATION_NOT_CURRENT" for row in p["history"]):
                raise RoutingError("target-relation-not-current already recorded")
            p["history"].append(dict(lifecycle_state=p["lifecycle_state"],
                decision_sequence=state["attempted_decisions"],
                kind="TARGET_RELATION_NOT_CURRENT",current_state=2,target_state=1,
                target_relation=deepcopy(relation),remaining_scoped_probes=(
                    budget["limit"]-budget["executed"])))
        elif kind=="GROUNDED_RELATION_REACQUISITION_AUTHORIZED":
            p=state["problems"].get(record.get("problem_id")); scoped=(None if not p else
                p.get("route_budgets",{}).get("problem_scoped_relation_probe"))
            condition=any(row.get("kind")=="TARGET_RELATION_NOT_CURRENT"
                          for row in (p or {}).get("history",[]))
            if not p or p["problem_id"]!="PR-0003" or not condition or \
                    record.get("target_relation")!=relation_identity(1,"ADVANCE") or \
                    record.get("target_state")!=1 or record.get("maximum_executions")!=1 or \
                    scoped is None or scoped["limit"]-scoped["executed"]!=1 or \
                    record.get("graph_source")!="AUTHENTICATED_REALIZED_RECEIPTS" or \
                    record.get("global_navigation") is not False:
                raise RoutingError("reacquisition authorization widened scope")
            if "grounded_relation_reacquisition" in p["route_budgets"]:
                raise RoutingError("reacquisition route already authorized")
            p["route_budgets"]["grounded_relation_reacquisition"]={
                "limit":1,"granted":0,"executed":0,"target_state":1,
                "selected_action":record["selected_action"],
                "supporting_receipt_identity":deepcopy(record[
                    "supporting_receipt_identity"]),
                "authorization_sha256":record["authorization_sha256"],
                "graph_sha256":record["graph_sha256"]}
            p["history"].append(dict(lifecycle_state=p["lifecycle_state"],
                decision_sequence=state["attempted_decisions"],
                kind="GROUNDED_RELATION_REACQUISITION_AUTHORIZED",
                target_state=1,selected_action=record["selected_action"],
                supporting_receipt_identity=deepcopy(record[
                    "supporting_receipt_identity"]),maximum_executions=1))
        elif kind=="RELATION_REACQUISITION_DECISION_FROZEN":
            if state["pending_decision"] is not None:
                raise RoutingError("problem decision already pending")
            p=state["problems"].get(record.get("problem_id")); budget=(None if not p else
                p.get("route_budgets",{}).get("grounded_relation_reacquisition"))
            if record.get("decision_sequence")!=state["attempted_decisions"]+1 or \
                    not p or p["problem_id"]!="PR-0003" or budget is None or \
                    budget["granted"]>=budget["limit"] or record.get("current_state")!=2 or \
                    record.get("target_state")!=1 or record.get(
                        "target_relation")!=relation_identity(1,"ADVANCE") or \
                    record.get("selected_navigation_action")!=budget["selected_action"] or \
                    record.get("supporting_authenticated_transition_receipt",{}).get(
                        "receipt_identity")!=budget["supporting_receipt_identity"] or \
                    record.get("reason")!="REACQUIRE_TARGET_RELATION_STATE" or \
                    any(record["forecasts"][a].get("valid") is not True for a in ACTION_ORDER):
                raise RoutingError("reacquisition decision differs from grounded authorization")
            final=record["final_decision"]
            if final.get("mode")!="PROBLEM_SCOPED_NAVIGATION" or final.get(
                    "action")!=budget["selected_action"] or final.get(
                    "reason")!="REACQUIRE_TARGET_RELATION_STATE" or final.get(
                    "abstained") is not False:
                raise RoutingError("reacquisition action was not frozen")
            state["attempted_decisions"]+=1; budget["granted"]+=1
            state["pending_decision"]={"decision_sequence":record["decision_sequence"],
                "problem_id":"PR-0003","selected_route":"GROUNDED_RELATION_REACQUISITION",
                "action":budget["selected_action"]}
        elif kind in ("TARGET_RELATION_REACQUIRED","REACQUISITION_TRANSITION_CONTRADICTED"):
            p=state["problems"].get(record.get("problem_id"))
            if not p or p.get("reacquisition_status")!=kind or record.get(
                    "decision_sequence")!=state["attempted_decisions"]:
                raise RoutingError("reacquisition outcome audit changed")
        elif kind=="REMAINING_SCOPED_RELATION_PROBE_PREPARED":
            if state["pending_decision"] is not None:
                raise RoutingError("problem decision already pending")
            observed=cls._observe_tie(state,record); p=state["problems"].get(record["problem_id"])
            budget=p["route_budgets"].get("problem_scoped_relation_probe")
            final=record["final_decision"]
            if observed is not p or p["problem_id"]!="PR-0003" or p.get(
                    "target_relation_reacquired") is not True or record.get("pre_state")!=1 or \
                    budget is None or budget!={**budget,"limit":2,"granted":1,"executed":1} or \
                    record.get("relation")!=budget["relation"] or \
                    any(record["forecasts"][a].get("valid") is not True for a in ACTION_ORDER) or \
                    final.get("mode")!="PROBLEM_SCOPED_PROBE" or final.get("action")!="ADVANCE" or \
                    final.get("reason")!="GROUND_RELATION_FOR_SPECIALIST_SELECTION" or \
                    final.get("abstained") is not False:
                raise RoutingError("remaining scoped relation probe eligibility changed")
            budget["granted"]+=1; p["route_request_count"]+=1
            p["lifecycle_state"]="ROUTE_REQUESTED"
            p["history"].append(dict(lifecycle_state="ROUTE_REQUESTED",
                decision_sequence=record["decision_sequence"],
                kind="REMAINING_SCOPED_RELATION_PROBE_PREPARED",
                route="PROBLEM_SCOPED_RELATION_PROBE",relation=deepcopy(budget["relation"]),
                reason="GROUND_RELATION_FOR_SPECIALIST_SELECTION"))
            state["pending_decision"]={"decision_sequence":record["decision_sequence"],
                "problem_id":"PR-0003","selected_route":"PROBLEM_SCOPED_RELATION_PROBE",
                "action":"ADVANCE"}
        elif kind=="ROUTE_GATING_DEADLOCK_DETECTED":
            p=state["problems"].get(record.get("problem_id")); relation=record.get("relation",{})
            if not p or p["problem_id"]!="PR-0003" or p.get(
                    "requested_capability")!="MORE_RELATION_EVIDENCE" or \
                    relation.get("pre_state")!=1 or relation.get("action")!="ADVANCE" or \
                    record.get("classification")!="ROUTE_GATING_DEADLOCK" or \
                    record.get("blocking_condition")!="RELATION_PROBE_CADENCE" or \
                    record.get("abstentions_advance_cadence") is not False or \
                    record.get("distance")!=2 or record.get("minimum_distance")!=3:
                raise RoutingError("route-gating deadlock proof changed")
            if any(row.get("kind")=="ROUTE_GATING_DEADLOCK_DETECTED"
                   for row in p["history"]):
                raise RoutingError("route-gating deadlock already recorded")
            p["history"].append(dict(lifecycle_state=p["lifecycle_state"],
                decision_sequence=state["attempted_decisions"],
                kind="ROUTE_GATING_DEADLOCK_DETECTED",relation=deepcopy(relation),
                blocking_condition="RELATION_PROBE_CADENCE",
                requested_capability="MORE_RELATION_EVIDENCE",
                proof_sha256=record["proof_sha256"]))
        elif kind=="SCOPED_EVIDENCE_AUTHORIZED":
            p=state["problems"].get(record.get("problem_id")); relation=record.get("relation",{})
            requested=any(row.get("kind")=="RELATION_EVIDENCE_REQUESTED" and
                row.get("relation")==relation and
                row.get("authority_status")=="REQUEST_REQUIRES_EXTERNAL_APPROVAL"
                for row in (p or {}).get("history",[]))
            if not p or p["problem_id"]!="PR-0003" or not requested or \
                    p.get("requested_capability")!="MORE_RELATION_EVIDENCE" or \
                    p["scope"]!=decision_scope(1,["ADVANCE","HOLD"]) or \
                    relation.get("pre_state")!=1 or relation.get("action")!="ADVANCE" or \
                    relation.get("identity_sha256")!=digest({"pre_state":1,"action":"ADVANCE"}):
                raise RoutingError("scoped relation authorization lacks the exact request")
            deadlock=any(row.get("kind")=="ROUTE_GATING_DEADLOCK_DETECTED" and
                row.get("relation")==relation for row in p["history"])
            if not deadlock or record.get("maximum_executions")!=2 or record.get(
                    "global_probe_policy_changed") is not False or \
                    record.get("authoritative_scope")!="PR-0003:(1,ADVANCE)":
                raise RoutingError("scoped relation authorization widened authority")
            if "problem_scoped_relation_probe" in p["route_budgets"]:
                raise RoutingError("scoped relation evidence already authorized")
            p["route_budgets"]["problem_scoped_relation_probe"]={
                "limit":2,"granted":0,"executed":0,"relation":deepcopy(relation),
                "authorization_sha256":record["authorization_sha256"],
                "request_event_sha256":record["request_event_sha256"]}
            p["history"].append(dict(lifecycle_state=p["lifecycle_state"],
                decision_sequence=state["attempted_decisions"],
                kind="SCOPED_EVIDENCE_AUTHORIZED",relation=deepcopy(relation),
                maximum_executions=2,authorization_sha256=record["authorization_sha256"]))
        elif kind=="SCOPED_RELATION_PROBE_PREPARED":
            if state["pending_decision"] is not None:
                raise RoutingError("problem decision already pending")
            observed=cls._observe_tie(state,record); p=state["problems"].get(record["problem_id"])
            budget=(None if not p else p.get("route_budgets",{}).get(
                "problem_scoped_relation_probe"))
            relation=record.get("relation",{})
            if observed is None or observed.get("problem_id")!="PR-0003" or p is not observed or \
                    record["pre_state"]!=1 or budget is None or relation!=budget.get("relation"):
                raise RoutingError("scoped relation probe is outside PR-0003")
            ordinary=record["ordinary_decision"]
            if budget["granted"]>=budget["limit"] or \
                    ordinary.get("reason")!="EXPLOIT_TIED_MAXIMUM" or \
                    ordinary.get("abstained") is not True or \
                    ordinary.get("probe_budget_available") is not False or \
                    record.get("selected_action")!="ADVANCE" or \
                    any(record["forecasts"][a].get("valid") is not True for a in ACTION_ORDER):
                raise RoutingError("scoped relation probe preconditions changed")
            final=record["final_decision"]
            if final.get("action")!="ADVANCE" or final.get("abstained") is not False or \
                    final.get("mode")!="PROBLEM_SCOPED_PROBE" or \
                    final.get("reason")!="GROUND_RELATION_FOR_SPECIALIST_SELECTION" or \
                    final.get("problem_id")!="PR-0003":
                raise RoutingError("scoped relation probe decision changed")
            budget["granted"]+=1; p["route_request_count"]+=1
            p["lifecycle_state"]="ROUTE_REQUESTED"
            p["history"].append(dict(lifecycle_state="ROUTE_REQUESTED",
                decision_sequence=record["decision_sequence"],kind="SCOPED_RELATION_PROBE_PREPARED",
                route="PROBLEM_SCOPED_RELATION_PROBE",relation=deepcopy(relation),
                reason="GROUND_RELATION_FOR_SPECIALIST_SELECTION"))
            state["pending_decision"]={"decision_sequence":record["decision_sequence"],
                "problem_id":"PR-0003","selected_route":"PROBLEM_SCOPED_RELATION_PROBE",
                "action":"ADVANCE"}
        elif kind=="REASSESSED":
            p=state["problems"].get(record.get("problem_id"))
            if not p or p["problem_id"]!="PR-0003" or p["lifecycle_state"]!="REASSESSED" or \
                    record.get("relation")!=relation_identity(1,"ADVANCE") or \
                    record.get("decision_sequence")!=state["attempted_decisions"] or \
                    record.get("scores")!=p["history"][-1].get("scores"):
                raise RoutingError("scoped relation reassessment audit changed")
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

    def authorize_option_profile_integration(self, *, problem_id: str,
            authorization_sha256: str, profile_evidence_sha256: str,
            result: str, selected_action: str):
        if len(authorization_sha256)!=64 or len(profile_evidence_sha256)!=64:
            raise RoutingError("invalid option-profile integration commitment")
        record=dict(
            problem_id=problem_id,authorization_sha256=authorization_sha256,
            profile_evidence_sha256=profile_evidence_sha256,result=result,
            selected_action=selected_action)
        self._apply(deepcopy(self.state),"OPTION_PROFILE_BEHAVIORAL_INTEGRATION_AUTHORIZED",record)
        return self._append("OPTION_PROFILE_BEHAVIORAL_INTEGRATION_AUTHORIZED",record)

    def prepare_option_profile_integration(self, *, store, ordinary_decision: dict,
            pre_state: int, forecasts: dict, problem_id: str, profiles: dict,
            result: str, selected_action: str, profile_evidence_sha256: str) -> dict:
        self.bind_session(store); final=deepcopy(ordinary_decision)
        final.update(mode="EXPLOIT",action=selected_action,abstained=False,
            reason="OPTION_PROFILE_DOMINANCE",problem_id=problem_id,
            ordinary_decision_sha256=digest(ordinary_decision),
            route_broker={"selected_route":"OPTION_PROFILE_DOMINANCE",
                "broker_result":"EXPLICIT_V017_AUTHORIZATION","authoritative":False,
                "one_use":True,"global":False})
        record=dict(decision_sequence=ordinary_decision["decision_sequence"],pre_state=pre_state,
            ordinary_decision=deepcopy(ordinary_decision),forecasts=deepcopy(forecasts),
            ordinary_decision_sha256=digest(ordinary_decision),
            current_predictions_sha256=digest(forecasts),problem_id=problem_id,
            profiles=deepcopy(profiles),profiles_sha256=digest(profiles),result=result,
            selected_action=selected_action,profile_evidence_sha256=profile_evidence_sha256,
            final_decision=deepcopy(final),hidden_regime_available=False,
            simulator_law_available=False,future_consequence_available=False,
            counterfactual_outcomes_available=False,frozen_before_external_execution=True)
        self._apply(deepcopy(self.state),"OPTION_PROFILE_DECISION_FROZEN",record)
        self._append("OPTION_PROFILE_DECISION_FROZEN",record); return final

    def record_option_profile_followup(self, *, store, row: dict,
                                       suffix_prefix_check: dict | None):
        receipt=row.get("receipt"); compact=None
        if receipt is not None:
            compact=dict(receipt_identity=[receipt[k] for k in (
                "source_identity","event_id","epoch","transaction_id")],
                action=receipt["action"],realized_consequence=receipt["realized_consequence"],
                realized_next_state=receipt["next_state"],receipt_is_authenticated=True)
        record=dict(problem_id="PR-0002",decision_sequence=row["prediction_batch_sequence"],
            status=row["status"],explorer=deepcopy(row["explorer"]),receipt=compact,
            suffix_prefix_check=deepcopy(suffix_prefix_check))
        self._apply(deepcopy(self.state),"OPTION_PROFILE_FOLLOWUP_OBSERVED",record)
        self._append("OPTION_PROFILE_FOLLOWUP_OBSERVED",record); self.bind_session(store)
        return deepcopy(record)

    def record_operational_repair_event(self, *, problem_id: str, stage: str,
                                        store=None, row: dict | None=None, **fields):
        record=dict(problem_id=problem_id,stage=stage,**deepcopy(fields))
        if stage=="RESUMED":
            if row is None: raise RoutingError("resumed repair lacks ordinary decision")
            receipt=row.get("receipt"); compact=None
            if receipt is not None:
                compact=dict(receipt_identity=[receipt[k] for k in (
                    "source_identity","event_id","epoch","transaction_id")],
                    action=receipt["action"],realized_consequence=receipt["realized_consequence"],
                    realized_next_state=receipt["next_state"],receipt_is_authenticated=True)
            record.update(decision_sequence=row["prediction_batch_sequence"],status=row["status"],
                explorer=deepcopy(row["explorer"]),receipt=compact)
        self._apply(deepcopy(self.state),"OPERATIONAL_REPAIR_LIFECYCLE",record)
        result=self._append("OPERATIONAL_REPAIR_LIFECYCLE",record)
        if store is not None: self.bind_session(store)
        return result

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
        routing=row.get("routing_evidence")
        routing_compact=(None if routing is None else {key:deepcopy(routing[key]) for key in (
            "relation","evidence_sequence","selected_specialist","selected_specialist_after",
            "router_score_after","switch_occurred","realized_consequence","receipt_identity")})
        record=dict(decision_sequence=row["prediction_batch_sequence"],status=row["status"],receipt=compact,
                    runtime_id=row.get("source_scope",{}).get("source_identity"),
                    routing_evidence=routing_compact)
        pending=self.state.get("pending_decision") or {}
        kind=("SCOPED_RELATION_PROBE_EXECUTED" if pending.get(
            "selected_route")=="PROBLEM_SCOPED_RELATION_PROBE" else
            "GROUNDED_RELATION_REACQUISITION_EXECUTED" if pending.get(
            "selected_route")=="GROUNDED_RELATION_REACQUISITION" else
            "LIVE_DECISION_COMPLETED")
        self._append(kind,record)
        if kind=="SCOPED_RELATION_PROBE_EXECUTED" and row["status"]=="AUTHORIZED":
            routing=row["routing_evidence"]
            self._append("REASSESSED",dict(problem_id="PR-0003",
                decision_sequence=row["prediction_batch_sequence"],
                relation=deepcopy(routing["relation"]),
                scores=deepcopy(routing["router_score_after"]),
                selected_specialist_before=routing["selected_specialist"],
                selected_specialist_after=routing["selected_specialist_after"],
                switch_threshold_satisfied=(routing["router_score_after"]["G2"]["total"]>=3
                    and abs(routing["router_score_after"]["G2"]["correct"]-
                            routing["router_score_after"]["G3"]["correct"])>=2)))
        elif kind=="GROUNDED_RELATION_REACQUISITION_EXECUTED" and row[
                "status"]=="AUTHORIZED":
            receipt=row["receipt"]
            outcome=("TARGET_RELATION_REACQUIRED" if receipt["next_state"]==1 else
                     "REACQUISITION_TRANSITION_CONTRADICTED")
            self._append(outcome,dict(problem_id="PR-0003",
                decision_sequence=row["prediction_batch_sequence"],
                receipt_identity=[receipt[k] for k in (
                    "source_identity","event_id","epoch","transaction_id")],
                realized_next_state=receipt["next_state"]))
        self.bind_session(store)
        return deepcopy(record)

    def attach_operational(self, **record):
        return self._append("OPERATIONAL_PROBLEM_ATTACHED",record)

    def record_uncommitted_call_tail(self, **record):
        return self._append("UNCOMMITTED_AUTHENTICATED_CALL_TAIL",record)

    def record_tail_recovered(self, **record):
        return self._append("DURABLE_TAIL_RECOVERED",record)

    def record_normal_route_handoff(self, **record):
        return self._append("NORMAL_ROUTE_REGAINS_CONTROL",record)

    def record_normal_route_reassessment(self, **record):
        return self._append("NORMAL_ROUTE_EVIDENCE_REASSESSED",record)

    def close_route_handoff_repair(self, **record):
        return self._append("ROUTE_HANDOFF_REPAIR_CLOSED",record)

    def request_relation_evidence(self, *, problem_id: str, relation: dict,
                                  classification: str,
                                  latest_evidence_sequence: int,
                                  latest_grounded_comparison: dict,
                                  current_scores: dict,
                                  selected_specialist: str,
                                  route_availability: dict):
        """Persist a scoped request without granting or executing a route."""
        record=dict(problem_id=problem_id,relation=deepcopy(relation),
            classification=classification,
            requested_capability="MORE_RELATION_EVIDENCE",
            requested_route="RELATION_PROBE",
            authority_status="REQUEST_REQUIRES_EXTERNAL_APPROVAL",
            selected_route=None,
            reason="RELATION_SPECIFIC_EVIDENCE_INSUFFICIENT_FOR_SPECIALIST_SELECTION",
            latest_evidence_sequence=latest_evidence_sequence,
            latest_grounded_comparison=deepcopy(latest_grounded_comparison),
            current_scores=deepcopy(current_scores),
            selected_specialist=selected_specialist,
            route_availability=deepcopy(route_availability),
            hidden_transition_destination_used=False,option_profile_used=False,
            authoritative=False,controls_execution=False,alters_memory=False,
            alters_specialist_selection=False,changes_prediction=False,
            trains_model=False,changes_protected_bound=False,
            alters_simulator=False,creates_receipt=False)
        self._apply(deepcopy(self.state),"RELATION_EVIDENCE_REQUESTED",record)
        return self._append("RELATION_EVIDENCE_REQUESTED",record)

    def record_route_gating_deadlock(self, *, problem_id: str, relation: dict,
                                     proof: dict):
        if proof.get("classification")!="ROUTE_GATING_DEADLOCK":
            raise RoutingError("scoped authorization requires a route-gating deadlock")
        record=dict(problem_id=problem_id,relation=deepcopy(relation),
            requested_capability="MORE_RELATION_EVIDENCE",
            blocking_condition="RELATION_PROBE_CADENCE",
            classification="ROUTE_GATING_DEADLOCK",
            abstentions_advance_cadence=False,distance=proof["distance"],
            minimum_distance=proof["minimum_distance"],proof_sha256=digest(proof),
            proof=deepcopy(proof),authoritative=False,controls_execution=False,
            creates_receipt=False,trains_model=False)
        self._apply(deepcopy(self.state),"ROUTE_GATING_DEADLOCK_DETECTED",record)
        return self._append("ROUTE_GATING_DEADLOCK_DETECTED",record)

    def record_target_relation_not_current(self, *, problem_id: str,
                                           target_relation: dict,
                                           current_state: int):
        record=dict(problem_id=problem_id,target_relation=deepcopy(target_relation),
            current_state=current_state,condition="TARGET_RELATION_NOT_CURRENT",
            authoritative=False,controls_execution=False,creates_receipt=False,
            trains_model=False)
        self._apply(deepcopy(self.state),"TARGET_RELATION_NOT_CURRENT",record)
        return self._append("TARGET_RELATION_NOT_CURRENT",record)

    def authorize_grounded_relation_reacquisition(self, *, problem_id: str,
            target_relation: dict, selected_action: str,
            supporting_receipt_identity: list, authorization_sha256: str,
            graph_sha256: str):
        if len(authorization_sha256)!=64 or len(graph_sha256)!=64:
            raise RoutingError("invalid reacquisition authorization identity")
        record=dict(problem_id=problem_id,target_relation=deepcopy(target_relation),
            target_state=target_relation["pre_state"],selected_action=selected_action,
            supporting_receipt_identity=deepcopy(supporting_receipt_identity),
            authorization_sha256=authorization_sha256,graph_sha256=graph_sha256,
            maximum_executions=1,graph_source="AUTHENTICATED_REALIZED_RECEIPTS",
            reason="REACQUIRE_TARGET_RELATION_STATE",global_navigation=False,
            authoritative=False,controls_execution=False,creates_receipt=False,
            alters_memory=False,changes_prediction=False,trains_model=False,
            alters_simulator=False)
        self._apply(deepcopy(self.state),
                    "GROUNDED_RELATION_REACQUISITION_AUTHORIZED",record)
        return self._append("GROUNDED_RELATION_REACQUISITION_AUTHORIZED",record)

    def prepare_grounded_relation_reacquisition(self, *, store,
            ordinary_decision: dict, pre_state: int, forecasts: dict,
            supporting_receipt: dict, problem_id: str="PR-0003") -> dict:
        self.bind_session(store)
        p=self.state["problems"].get(problem_id); budget=(None if not p else
            p.get("route_budgets",{}).get("grounded_relation_reacquisition"))
        if budget is None:
            raise RoutingError("reacquisition route is not authorized")
        final=deepcopy(ordinary_decision)
        final.update(mode="PROBLEM_SCOPED_NAVIGATION",
            action=budget["selected_action"],abstained=False,
            reason="REACQUIRE_TARGET_RELATION_STATE",problem_id=problem_id,
            ordinary_decision_sha256=digest(ordinary_decision),
            route_broker={"selected_route":"GROUNDED_RELATION_REACQUISITION",
                "broker_result":"EXPLICIT_V021_PROBLEM_SCOPED_AUTHORIZATION",
                "target_state":1,"authoritative":False,"global":False})
        record=dict(decision_sequence=ordinary_decision["decision_sequence"],
            problem_id=problem_id,current_state=pre_state,target_state=1,
            target_relation=relation_identity(1,"ADVANCE"),
            selected_navigation_action=budget["selected_action"],
            supporting_authenticated_transition_receipt=deepcopy(supporting_receipt),
            reason="REACQUIRE_TARGET_RELATION_STATE",
            ordinary_decision=deepcopy(ordinary_decision),forecasts=deepcopy(forecasts),
            final_decision=deepcopy(final),hidden_regime_available=False,
            simulator_law_available=False,predicted_transition_used=False,
            consequence_value_used_for_selection=False,future_receipt_available=False,
            frozen_before_external_execution=True)
        self._apply(deepcopy(self.state),
                    "RELATION_REACQUISITION_DECISION_FROZEN",record)
        self._append("RELATION_REACQUISITION_DECISION_FROZEN",record)
        return final

    def prepare_remaining_scoped_relation_probe(self, *, store,
            ordinary_decision: dict, pre_state: int, forecasts: dict,
            problem_id: str="PR-0003") -> dict:
        self.bind_session(store); relation=relation_identity(1,"ADVANCE")
        final=deepcopy(ordinary_decision)
        final.update(mode="PROBLEM_SCOPED_PROBE",action="ADVANCE",abstained=False,
            reason="GROUND_RELATION_FOR_SPECIALIST_SELECTION",problem_id=problem_id,
            ordinary_decision_sha256=digest(ordinary_decision),
            route_broker={"selected_route":"PROBLEM_SCOPED_RELATION_PROBE",
                "broker_result":"REMAINING_V020_PROBE_AFTER_V021_REACQUISITION",
                "requested_capability":"MORE_RELATION_EVIDENCE",
                "authoritative":False,"global_probe_policy_changed":False})
        record=dict(decision_sequence=ordinary_decision["decision_sequence"],
            pre_state=pre_state,ordinary_decision=deepcopy(ordinary_decision),
            forecasts=deepcopy(forecasts),problem_id=problem_id,relation=relation,
            selected_action="ADVANCE",final_decision=deepcopy(final),
            hidden_regime_available=False,simulator_law_available=False,
            future_consequence_available=False,counterfactual_outcomes_available=False,
            hidden_transition_destination_used=False)
        self._apply(deepcopy(self.state),
                    "REMAINING_SCOPED_RELATION_PROBE_PREPARED",record)
        self._append("REMAINING_SCOPED_RELATION_PROBE_PREPARED",record)
        return final

    def authorize_scoped_relation_evidence(self, *, problem_id: str, relation: dict,
                                            authorization_sha256: str,
                                            request_event_sha256: str):
        if len(authorization_sha256)!=64 or len(request_event_sha256)!=64:
            raise RoutingError("invalid scoped relation authorization identity")
        requests=[row for row in self.records if row["kind"]=="RELATION_EVIDENCE_REQUESTED" and
                  row["record"].get("problem_id")==problem_id and
                  row["record"].get("relation")==relation]
        if len(requests)!=1 or digest(requests[0])!=request_event_sha256:
            raise RoutingError("scoped relation authorization request hash mismatch")
        record=dict(problem_id=problem_id,relation=deepcopy(relation),
            authorization_sha256=authorization_sha256,
            request_event_sha256=request_event_sha256,maximum_executions=2,
            authoritative_scope="PR-0003:(1,ADVANCE)",
            global_probe_policy_changed=False,authoritative=False,
            controls_execution=False,alters_memory=False,alters_specialist_selection=False,
            changes_prediction=False,trains_model=False,changes_protected_bound=False,
            alters_simulator=False,creates_receipt=False)
        self._apply(deepcopy(self.state),"SCOPED_EVIDENCE_AUTHORIZED",record)
        return self._append("SCOPED_EVIDENCE_AUTHORIZED",record)

    def prepare_scoped_relation_probe(self, *, store, ordinary_decision: dict,
                                      pre_state: int, forecasts: dict,
                                      problem_id: str="PR-0003") -> dict:
        self.bind_session(store); relation={"pre_state":1,"action":"ADVANCE"}
        relation["identity_sha256"]=digest(relation)
        final=deepcopy(ordinary_decision)
        final.update(mode="PROBLEM_SCOPED_PROBE",action="ADVANCE",abstained=False,
            reason="GROUND_RELATION_FOR_SPECIALIST_SELECTION",problem_id=problem_id,
            ordinary_decision_sha256=digest(ordinary_decision),
            route_broker={"selected_route":"PROBLEM_SCOPED_RELATION_PROBE",
                "broker_result":"EXPLICIT_V020_PROBLEM_SCOPED_AUTHORIZATION",
                "requested_capability":"MORE_RELATION_EVIDENCE",
                "authoritative":False,"global_probe_policy_changed":False},
            relation_evidence_reason="GROUND_RELATION_FOR_SPECIALIST_SELECTION")
        record=dict(decision_sequence=ordinary_decision["decision_sequence"],
            pre_state=pre_state,ordinary_decision=deepcopy(ordinary_decision),
            forecasts=deepcopy(forecasts),problem_id=problem_id,relation=relation,
            selected_action="ADVANCE",final_decision=deepcopy(final),
            hidden_regime_available=False,simulator_law_available=False,
            future_consequence_available=False,counterfactual_outcomes_available=False,
            hidden_transition_destination_used=False)
        self._apply(deepcopy(self.state),"SCOPED_RELATION_PROBE_PREPARED",record)
        self._append("SCOPED_RELATION_PROBE_PREPARED",record)
        return final

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
