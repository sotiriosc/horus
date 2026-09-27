"""Problem-scoped evidence authorization for the exact PR-0003 relation."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from .core import digest
from .grounded_exploration import ExplorerConfidenceStore, GroundedExplorer
from .grounded_learning import atomic_json, file_hash
from .live import ModelClient, SessionStore
from .problem_manager import (ProblemManagedExplorer, ProblemManager,
                              ProblemOwnershipRuntime)
from .relation_routing import (RelationEvidenceStore, relation_identity,
                               relation_routed_clients)
from .routing import RoutingError
from .scoped_relation_reassessment import reassess_values


POLICY_PATH=Path(__file__).with_name("scoped_relation_authorization_policy.json")
ROOT=Path(__file__).parent.parent
TARGET=relation_identity(1,"ADVANCE")
REASON="GROUND_RELATION_FOR_SPECIALIST_SELECTION"


def cadence_deadlock_proof(*, confidence_state: dict, problem: dict,
                           minimum_distance: int) -> dict:
    """Prove the abstention fixed point from authenticated counters only."""
    next_authorized=confidence_state["authorized_decisions"]+1
    last_probe=confidence_state["last_probe_authorized_decision"]
    distance=None if last_probe is None else next_authorized-last_probe
    exact_problem=(problem.get("problem_id")=="PR-0003" and
        problem.get("requested_capability")=="MORE_RELATION_EVIDENCE" and
        problem.get("scope",{}).get("pre_state")==1 and
        problem.get("scope",{}).get("tied_action_set")==["ADVANCE","HOLD"])
    blocked=exact_problem and distance is not None and distance<minimum_distance
    return dict(classification=("ROUTE_GATING_DEADLOCK" if blocked else
                                "ORDINARY_ROUTE_CAN_ADVANCE"),
        problem_id=problem.get("problem_id"),relation=TARGET,
        requested_capability=problem.get("requested_capability"),
        blocking_condition=("RELATION_PROBE_CADENCE" if blocked else None),
        authorized_decisions=confidence_state["authorized_decisions"],
        last_probe_authorized_decision=last_probe,
        next_authorized_decision=next_authorized,distance=distance,
        minimum_distance=minimum_distance,
        abstention_changes_authorized_decisions=False,
        abstention_changes_last_probe=False,
        abstentions_advance_cadence=False,
        repeated_abstention_distance=distance,
        exact_problem_scope=exact_problem)


def load_policy() -> dict:
    policy=json.loads(POLICY_PATH.read_text())
    for path,expected in policy["frozen_sha256"].items():
        if file_hash(ROOT/path)!=expected:
            raise RoutingError(f"v0.20 frozen file changed: {path}")
    if policy["maximum_scoped_probes"]!=2 or policy["maximum_ordinary_followups"]!=1 or \
            policy["maximum_behavioral_decisions"]!=3 or policy["maximum_model_calls"]!=27 or \
            policy["model_calls_per_decision"]!=9 or \
            policy["target_relation"]!={"pre_state":1,"action":"ADVANCE"} or \
            policy["frozen_reason"]!=REASON or \
            policy["global_probe_policy_changed"] is not False:
        raise RoutingError("v0.20 scope/bound changed")
    return policy


class ScopedRelationExplorer:
    def __init__(self, ordinary, manager, store):
        self.ordinary,self.manager,self.store=ordinary,manager,store

    def derive(self, **kwargs):
        ordinary=self.ordinary.derive(**kwargs)
        if ordinary.get("reason")=="INVALID_MAP_COMPONENT":
            return self.manager.prepare(store=self.store,ordinary_decision=ordinary,
                pre_state=kwargs["pre_state"],forecasts=kwargs["forecasts"])
        return self.manager.prepare_scoped_relation_probe(store=self.store,
            ordinary_decision=ordinary,pre_state=kwargs["pre_state"],
            forecasts=kwargs["forecasts"])


class ScopedRelationRuntime(ProblemOwnershipRuntime):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.confidence_store.explorer=ScopedRelationExplorer(
            GroundedExplorer(self.confidence_store.registry["policy"]),
            self.problem_manager,self.store)

    def _next_batch(self):
        capture=self.reader.capture(); sequence=self.store.checkpoint["attempted_decisions"]+1
        decision_id=(f"{self.store.checkpoint['session_id']}:e{capture['epoch']}:"
                     f"problem-scoped-relation:d{sequence}")
        return capture,self.map.forecasts(capture,decision_id),sequence,decision_id


def _request_event_sha256(manager: ProblemManager) -> str:
    rows=[row for row in manager.records if row["kind"]=="RELATION_EVIDENCE_REQUESTED" and
          row["record"].get("problem_id")=="PR-0003" and
          row["record"].get("relation")==TARGET]
    if len(rows)!=1:
        raise RoutingError("v0.20 requires exactly one retained scoped request")
    return digest(rows[0])


def _post_values(row: dict) -> dict:
    after=row["routing_evidence"]["selected_specialist_after"]
    selected=deepcopy(row["relation_selections_before"]); selected["ADVANCE"]=after
    values={action:row["forecasts"][action][f"{specialist}_consequence"]
            for action,specialist in selected.items()}
    return dict(selections=selected,**reassess_values(values))


def _score(row: dict) -> dict:
    routing=row["routing_evidence"]; scores=routing["router_score_after"]
    before=routing["selected_specialist"]
    after=routing["selected_specialist_after"]
    lead=abs(scores["G2"]["correct"]-scores["G3"]["correct"])
    return dict(G2=deepcopy(scores["G2"]),G3=deepcopy(scores["G3"]),
        selected_specialist_before=before,selected_specialist_after=after,
        lead=lead,switch_threshold_satisfied=(scores["G2"]["total"]>=3 and lead>=2),
        specialist_changed=before!=after)


def run(*, session_root: Path, registry_root: Path, output: Path,
        joint_client=None, specialists=None) -> dict:
    policy=load_policy()
    if specialists is None:
        specialists,registry=relation_routed_clients(registry_root,device="cuda")
    else:
        from .relation_routing import load_relation_routing_registry
        registry=load_relation_routing_registry(registry_root)
    joint=joint_client or ModelClient(); before_client=joint.requests
    specialist_before={key:value.requests for key,value in specialists.items()}
    with SessionStore(session_root,True) as store,RelationEvidenceStore(registry_root) as routing, \
            ExplorerConfidenceStore(registry_root) as confidence,ProblemManager(registry_root) as manager:
        expected=policy["source_endpoint"]
        if store.checkpoint["attempted_decisions"]!=expected["attempted_decisions"] or \
                len(store.records["events"])!=expected["authorized_executions"] or \
                len(store.records["calls"])!=expected["call_stream_records"] or \
                store.checkpoint["current_state"]!=1 or len(routing.records)!=expected[
                    "routing_records"] or manager.state["stream_count"]!=expected[
                    "manager_records"]:
            raise RoutingError("v0.19 source endpoint changed")
        manager.bind_session(store); routing.bind_session(store); confidence.bind_session(store)
        before_pr2=deepcopy(manager.state["problems"]["PR-0002"])
        before_pr3=deepcopy(manager.state["problems"]["PR-0003"])
        global_policy_path=Path(__file__).with_name("grounded_exploration_policy.json")
        global_policy_before=file_hash(global_policy_path)
        cadence_before={key:confidence.state[key] for key in (
            "authorized_decisions","last_probe_decision_sequence",
            "last_probe_authorized_decision")}
        minimum=confidence.registry["policy"]["probe_budget"]["minimum_decision_distance"]
        proof=cadence_deadlock_proof(confidence_state=confidence.state,
                                    problem=before_pr3,minimum_distance=minimum)
        if proof["classification"]!="ROUTE_GATING_DEADLOCK":
            result=dict(identity=policy["mode"],status="EXISTING_ROUTE_AVAILABLE",
                deadlock_proof=proof,fresh_decisions=0,model_calls=0,
                authorization_used=False,final_checkpoint=deepcopy(store.checkpoint))
            atomic_json(output,result); return result
        request_sha=_request_event_sha256(manager)
        if request_sha!=policy["request_event_sha256"]:
            raise RoutingError("retained scoped request identity changed")
        manager.record_route_gating_deadlock(problem_id="PR-0003",relation=TARGET,
                                             proof=proof)
        manager.authorize_scoped_relation_evidence(problem_id="PR-0003",relation=TARGET,
            authorization_sha256=policy["authorization_sha256"],
            request_event_sha256=request_sha)
        runtime=ScopedRelationRuntime(store,joint,specialists,registry,routing,confidence,"A",
                                      problem_manager=manager)
        boundary=dict(runtime_index=store.checkpoint["runtime_index"],
            epoch=store.checkpoint["current_epoch"],
            source_identity=store.checkpoint["current_source_identity"])
        probes=[]; stop_reason=None; post_values=None
        while len(probes)<policy["maximum_scoped_probes"]:
            if store.checkpoint["current_state"]!=1:
                stop_reason="TARGET_RELATION_NOT_CURRENT_AFTER_AUTHENTICATED_EXECUTION"; break
            current_problem=manager.state["problems"]["PR-0003"]
            current_proof=cadence_deadlock_proof(confidence_state=confidence.state,
                problem=current_problem,minimum_distance=minimum)
            if current_proof["classification"]!="ROUTE_GATING_DEADLOCK":
                stop_reason="ORDINARY_RELATION_PROBE_NOW_AVAILABLE"; break
            row=runtime.execute_autonomous()
            if row["status"]!="AUTHORIZED":
                manager.attach_operational(decision_sequence=row["prediction_batch_sequence"],
                    problem_type="EXTERNAL_SERVICE_PROBLEM",
                    scope={"kind":"service","service_id":"MODEL_SERVICE"},owner="MODEL_SERVICE",
                    blocked_problem_id="PR-0003")
                probes.append(dict(execution=row,score=None)); stop_reason="OPERATIONAL_FAILURE"; break
            score=_score(row); post_values=_post_values(row)
            probes.append(dict(execution=row,score=score,
                post_receipt_state1_reassessment=post_values))
            if score["switch_threshold_satisfied"]:
                stop_reason="LEGITIMATE_ROUTING_THRESHOLD_SATISFIED"; break
            if manager.state["problems"]["PR-0003"].get(
                    "requested_capability")!="MORE_RELATION_EVIDENCE":
                stop_reason="PROBLEM_EVIDENCE_REQUEST_RESOLVED"; break
        if stop_reason is None: stop_reason="SCOPED_PROBE_ALLOWANCE_EXHAUSTED"
        followup=None
        original_tie_disappeared=bool(post_values and not post_values["ordinary_abstained"])
        if original_tie_disappeared:
            runtime.confidence_store.explorer=ProblemManagedExplorer(
                GroundedExplorer(runtime.confidence_store.registry["policy"]),
                manager,store)
            followup=runtime.execute_autonomous()
        calls=joint.requests-before_client+sum(client.requests-specialist_before[key]
                                               for key,client in specialists.items())
        expected_calls=9*(len(probes)+(1 if followup else 0))
        if calls!=expected_calls or calls>policy["maximum_model_calls"]:
            raise RoutingError("v0.20 decision/call accounting changed")
        authorized_rows=[p for p in probes if p["execution"]["status"]=="AUTHORIZED"]
        switched=any(p["score"] and p["score"]["specialist_changed"] for p in probes)
        threshold=any(p["score"] and p["score"]["switch_threshold_satisfied"] for p in probes)
        if any(p["execution"]["status"]!="AUTHORIZED" for p in probes):
            assessment="OPERATIONAL_FAILURE"
        elif threshold and original_tie_disappeared: assessment="RELATION_ROUTING_RESOLVED"
        elif threshold: assessment="VALUE_TIE_PERSISTS"
        else: assessment="MORE_RELATION_EVIDENCE_REQUIRED"
        after_pr2=deepcopy(manager.state["problems"]["PR-0002"])
        after_pr3=deepcopy(manager.state["problems"]["PR-0003"])
        cadence_after={key:confidence.state[key] for key in cadence_before}
        result=dict(identity=policy["mode"],parent_commit=policy["parent_commit"],
            status=assessment,deadlock_proof=proof,
            authorization_sha256=policy["authorization_sha256"],
            request_event_sha256=request_sha,target_problem="PR-0003",target_relation=TARGET,
            frozen_reason=REASON,maximum_scoped_probes=2,probes_permitted=2,
            probes_used=len(probes),authorized_probe_receipts=len(authorized_rows),
            probe_stop_reason=stop_reason,model_calls=calls,maximum_model_calls=27,
            model_calls_per_decision=9,probes=probes,
            specialist_changed=switched,resulting_state1_reassessment=post_values,
            original_tie_disappeared=original_tie_disappeared,
            ordinary_follow_up=followup,ordinary_follow_up_used=followup is not None,
            before_pr3=before_pr3,after_pr3=after_pr3,
            final_pr0003_assessment=assessment,
            pr0002_unchanged=(before_pr2==after_pr2),pr0002_sha256=digest(before_pr2),
            ordinary_probe_cadence_before=cadence_before,
            ordinary_probe_cadence_after=cadence_after,
            scoped_route_updated_last_probe=(cadence_before["last_probe_authorized_decision"]!=
                                              cadence_after["last_probe_authorized_decision"]),
            global_probe_policy_sha256=file_hash(global_policy_path),
            global_probe_policy_unchanged=(global_policy_before==file_hash(global_policy_path)),
            global_probe_policy_changed=False,training_runs=0,models_changed=False,
            option_profile_used=False,horizon_changed=False,
            hidden_transition_destination_used=False,runtime_boundary=boundary,
            final_checkpoint=deepcopy(store.checkpoint),problem_graph=deepcopy(manager.state))
    atomic_json(output,result); return result
