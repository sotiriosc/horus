"""One-edge Memory-grounded reacquisition for PR-0003."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import json
from pathlib import Path

from experiments.base_framework_v0.framework import ACTION_ORDER

from .core import digest
from .grounded_exploration import ExplorerConfidenceStore, GroundedExplorer
from .grounded_learning import atomic_json, file_hash
from .live import ModelClient, SessionStore
from .problem_manager import (ProblemManagedExplorer, ProblemManager,
                              ProblemOwnershipRuntime)
from .relation_routing import (RelationEvidenceStore, relation_identity,
                               relation_key, relation_routed_clients)
from .routing import RoutingError
from .scoped_relation_authorization import _post_values

POLICY_PATH=Path(__file__).with_name("grounded_relation_reacquisition_policy.json")
ROOT=Path(__file__).parent.parent
TARGET=relation_identity(1,"ADVANCE")


def authenticated_transition_graph(store: SessionStore) -> dict:
    edges=[]
    for envelope in store.records["events"]:
        record=envelope["record"]; receipt=record["receipt"]
        edges.append(dict(pre_state=receipt["pre_state"],action=receipt["action"],
            realized_next_state=receipt["next_state"],
            realized_consequence=receipt["realized_consequence"],
            receipt_identity=deepcopy(record["receipt_identity"]),epoch=receipt["epoch"],
            transaction_id=receipt["transaction_id"],event_sequence=envelope["sequence"],
            recorded_at=record["recorded_at"],receipt_provenance_sha256=record[
                "receipt_provenance_sha256"],authenticated=True,
            source="AUTHORIZED_REALIZED_EVENT"))
    return dict(identity="AUTHENTICATED_REALIZED_TRANSITION_GRAPH",edges=edges,
        edge_count=len(edges),predicted_edges=0,simulator_edges=0,
        inferred_edges=0,counterfactual_edges=0)


def select_one_step(graph: dict, *, current_state: int, target_state: int) -> dict:
    candidates=[row for row in graph["edges"] if row["pre_state"]==current_state and
                row["realized_next_state"]==target_state and row.get("authenticated") is True]
    if not candidates:
        return dict(status="RELATION_REACQUISITION_ROUTE_UNAVAILABLE",
                    current_state=current_state,target_state=target_state,candidates=[])
    counts=Counter(row["action"] for row in candidates)
    by_action={action:max((row for row in candidates if row["action"]==action),
                          key=lambda row:row["event_sequence"])
               for action in counts}
    selected_action=min(by_action,key=lambda action:(
        -by_action[action]["event_sequence"],-counts[action],ACTION_ORDER.index(action)))
    return dict(status="RELATION_REACQUISITION_ROUTE_AVAILABLE",
        current_state=current_state,target_state=target_state,
        selected_action=selected_action,reason="REACQUIRE_TARGET_RELATION_STATE",
        supporting_receipt=deepcopy(by_action[selected_action]),
        exact_transition_repetitions=counts[selected_action],
        selection_priority=["MOST_RECENT_AUTHENTICATED_RECEIPT",
                            "EXACT_TRANSITION_REPETITIONS","CANONICAL_ACTION_ORDER"],
        candidates=deepcopy(candidates),consequence_used_for_selection=False,
        predicted_next_state_used=False)


def load_policy() -> dict:
    policy=json.loads(POLICY_PATH.read_text())
    for path,expected in policy["frozen_sha256"].items():
        if file_hash(ROOT/path)!=expected:
            raise RoutingError(f"v0.21 frozen file changed: {path}")
    if policy["maximum_navigation_executions"]!=1 or \
            policy["maximum_remaining_scoped_probes"]!=1 or \
            policy["maximum_ordinary_followups"]!=1 or \
            policy["maximum_behavioral_decisions"]!=3 or \
            policy["model_calls_per_decision"]!=9 or policy["maximum_model_calls"]!=27 or \
            policy["target_relation"]!={"pre_state":1,"action":"ADVANCE"} or \
            policy["global_navigation"] is not False:
        raise RoutingError("v0.21 scope/bound changed")
    return policy


class ReacquisitionExplorer:
    def __init__(self, ordinary, manager, store, supporting_receipt):
        self.ordinary,self.manager,self.store=ordinary,manager,store
        self.supporting_receipt=deepcopy(supporting_receipt)
    def derive(self,**kwargs):
        ordinary=self.ordinary.derive(**kwargs)
        return self.manager.prepare_grounded_relation_reacquisition(store=self.store,
            ordinary_decision=ordinary,pre_state=kwargs["pre_state"],
            forecasts=kwargs["forecasts"],supporting_receipt=self.supporting_receipt)


class RemainingScopedExplorer:
    def __init__(self,ordinary,manager,store):
        self.ordinary,self.manager,self.store=ordinary,manager,store
    def derive(self,**kwargs):
        ordinary=self.ordinary.derive(**kwargs)
        return self.manager.prepare_remaining_scoped_relation_probe(store=self.store,
            ordinary_decision=ordinary,pre_state=kwargs["pre_state"],
            forecasts=kwargs["forecasts"])


class ReacquisitionRuntime(ProblemOwnershipRuntime):
    def __init__(self,*args,supporting_receipt: dict,**kwargs):
        super().__init__(*args,**kwargs)
        self.confidence_store.explorer=ReacquisitionExplorer(
            GroundedExplorer(self.confidence_store.registry["policy"]),
            self.problem_manager,self.store,supporting_receipt)
    def _next_batch(self):
        capture=self.reader.capture(); sequence=self.store.checkpoint["attempted_decisions"]+1
        decision_id=(f"{self.store.checkpoint['session_id']}:e{capture['epoch']}:"
                     f"relation-reacquisition:d{sequence}")
        return capture,self.map.forecasts(capture,decision_id),sequence,decision_id


def _window_row(row: dict) -> dict:
    return {key:deepcopy(row[key]) for key in ("evidence_sequence","relation",
        "receipt_identity","realized_consequence","specialist_predictions","correctness")}


def run(*, session_root: Path, registry_root: Path, output: Path,
        joint_client=None,specialists=None) -> dict:
    policy=load_policy()
    if specialists is None:
        specialists,registry=relation_routed_clients(registry_root,device="cuda")
    else:
        from .relation_routing import load_relation_routing_registry
        registry=load_relation_routing_registry(registry_root)
    joint=joint_client or ModelClient(); joint_before=joint.requests
    specialist_before={key:value.requests for key,value in specialists.items()}
    with SessionStore(session_root,True) as store, RelationEvidenceStore(registry_root) as routing, \
            ExplorerConfidenceStore(registry_root) as confidence, ProblemManager(registry_root) as manager:
        expected=policy["source_endpoint"]
        actual=dict(attempted_decisions=store.checkpoint["attempted_decisions"],
            authorized_executions=len(store.records["events"]),
            call_stream_records=len(store.records["calls"]),
            training_records=len(store.records["training"]),
            routing_records=len(routing.records),confidence_records=len(confidence.records),
            manager_records=len(manager.records),current_state=store.checkpoint["current_state"])
        if actual!=expected:
            raise RoutingError("v0.20 source endpoint changed")
        manager.bind_session(store); routing.bind_session(store); confidence.bind_session(store)
        before_pr2=deepcopy(manager.state["problems"]["PR-0002"])
        before_pr3=deepcopy(manager.state["problems"]["PR-0003"])
        scoped_before=deepcopy(before_pr3["route_budgets"]["problem_scoped_relation_probe"])
        ordinary_probe_before=confidence.state["last_probe_authorized_decision"]
        graph=authenticated_transition_graph(store); selection=select_one_step(
            graph,current_state=store.checkpoint["current_state"],target_state=1)
        relevant={**selection,"graph_sha256":digest(graph),"graph_edge_count":graph["edge_count"]}
        if digest(relevant)!=policy["route_proof_sha256"]:
            raise RoutingError("zero-inference reacquisition proof changed")
        if selection["status"]!="RELATION_REACQUISITION_ROUTE_AVAILABLE":
            result=dict(identity=policy["mode"],status=selection["status"],
                route_proof=relevant,fresh_decisions=0,model_calls=0,
                final_checkpoint=deepcopy(store.checkpoint))
            atomic_json(output,result); return result
        manager.record_target_relation_not_current(problem_id="PR-0003",
            target_relation=TARGET,current_state=store.checkpoint["current_state"])
        manager.authorize_grounded_relation_reacquisition(problem_id="PR-0003",
            target_relation=TARGET,selected_action=selection["selected_action"],
            supporting_receipt_identity=selection["supporting_receipt"]["receipt_identity"],
            authorization_sha256=policy["authorization_sha256"],
            graph_sha256=digest(graph))
        runtime=ReacquisitionRuntime(store,joint,specialists,registry,routing,confidence,"A",
            problem_manager=manager,supporting_receipt=selection["supporting_receipt"])
        navigation=runtime.execute_autonomous(); remaining_probe=None; followup=None
        eviction=None; added=None; score=None; post_values=None
        if navigation["status"]!="AUTHORIZED":
            manager.attach_operational(decision_sequence=navigation["prediction_batch_sequence"],
                problem_type="EXTERNAL_SERVICE_PROBLEM",
                scope={"kind":"service","service_id":"MODEL_SERVICE"},owner="MODEL_SERVICE",
                blocked_problem_id="PR-0003")
            outcome="OPERATIONAL_FAILURE"
        elif navigation["receipt"]["next_state"]!=1:
            outcome="REACQUISITION_FAILED"
        else:
            before_window=[row["record"] for row in routing.records
                if relation_key(row["record"]["relation"])==relation_key(TARGET)][-6:]
            runtime.confidence_store.explorer=RemainingScopedExplorer(
                GroundedExplorer(runtime.confidence_store.registry["policy"]),manager,store)
            remaining_probe=runtime.execute_autonomous()
            if remaining_probe["status"]!="AUTHORIZED":
                manager.attach_operational(decision_sequence=remaining_probe[
                    "prediction_batch_sequence"],problem_type="EXTERNAL_SERVICE_PROBLEM",
                    scope={"kind":"service","service_id":"MODEL_SERVICE"},owner="MODEL_SERVICE",
                    blocked_problem_id="PR-0003")
                outcome="OPERATIONAL_FAILURE"
            else:
                after_window=[row["record"] for row in routing.records
                    if relation_key(row["record"]["relation"])==relation_key(TARGET)][-6:]
                eviction=_window_row(before_window[0]) if len(before_window)==6 else None
                added=_window_row(after_window[-1])
                scores=remaining_probe["routing_evidence"]["router_score_after"]
                lead=scores["G3"]["correct"]-scores["G2"]["correct"]
                score=dict(G2=deepcopy(scores["G2"]),G3=deepcopy(scores["G3"]),
                    challenger_lead=lead,selected_specialist_before=remaining_probe[
                        "routing_evidence"]["selected_specialist"],
                    selected_specialist_after=remaining_probe["routing_evidence"][
                        "selected_specialist_after"],switch_occurred=remaining_probe[
                        "routing_evidence"]["switch_occurred"])
                post_values=_post_values(remaining_probe)
                if score["switch_occurred"]: outcome="G3_SWITCHES"
                else:
                    before_diff=sum(row["correctness"]["G2"] for row in before_window)-sum(
                        row["correctness"]["G3"] for row in before_window)
                    after_diff=scores["G2"]["correct"]-scores["G3"]["correct"]
                    outcome=("G2_STRENGTHENS" if after_diff>before_diff else "G2_REMAINS")
                if score["switch_occurred"] and not post_values["ordinary_abstained"]:
                    runtime.confidence_store.explorer=ProblemManagedExplorer(
                        GroundedExplorer(runtime.confidence_store.registry["policy"]),manager,store)
                    followup=runtime.execute_autonomous()
        calls=joint.requests-joint_before+sum(client.requests-specialist_before[key]
                                              for key,client in specialists.items())
        decisions=1+(remaining_probe is not None)+(followup is not None)
        if calls!=9*decisions or calls>policy["maximum_model_calls"]:
            raise RoutingError("v0.21 call accounting changed")
        after_pr2=deepcopy(manager.state["problems"]["PR-0002"])
        after_pr3=deepcopy(manager.state["problems"]["PR-0003"])
        scoped_after=deepcopy(after_pr3["route_budgets"]["problem_scoped_relation_probe"])
        if outcome=="G3_SWITCHES" and post_values and not post_values["ordinary_abstained"]:
            final_assessment="RELATION_ROUTING_RESOLVED"
        elif outcome=="G3_SWITCHES": final_assessment="VALUE_TIE_PERSISTS"
        elif outcome in ("G2_REMAINS","G2_STRENGTHENS"):
            final_assessment="MORE_RELATION_EVIDENCE_REQUIRED"
        elif outcome=="REACQUISITION_FAILED": final_assessment="REACQUISITION_FAILED"
        else: final_assessment="OPERATIONAL_FAILURE"
        result=dict(identity=policy["mode"],parent_commit=policy["parent_commit"],
            status=outcome,final_pr0003_assessment=final_assessment,
            route_proof=relevant,authorization_sha256=policy["authorization_sha256"],
            navigation=navigation,state1_reacquired=(navigation.get("receipt",{}).get(
                "next_state")==1),remaining_scoped_probe=remaining_probe,
            rolling_window_evicted=eviction,rolling_window_added=added,
            router_score_after_second_probe=score,resulting_state1_reassessment=post_values,
            ordinary_follow_up=followup,ordinary_follow_up_used=followup is not None,
            behavioral_decisions=decisions,model_calls=calls,maximum_model_calls=27,
            scoped_budget_before=scoped_before,scoped_budget_after=scoped_after,
            scoped_budget_reset=False,ordinary_probe_marker_before=ordinary_probe_before,
            ordinary_probe_marker_after=confidence.state["last_probe_authorized_decision"],
            pr0002_unchanged=(before_pr2==after_pr2),pr0002_sha256=digest(before_pr2),
            before_pr3=before_pr3,after_pr3=after_pr3,training_runs=0,
            models_changed=False,router_threshold_changed=False,global_navigation=False,
            predicted_transition_used_for_navigation=False,simulator_transition_used=False,
            final_checkpoint=deepcopy(store.checkpoint),problem_graph=deepcopy(manager.state))
    atomic_json(output,result); return result
