"""Horus v0.11: bounded coverage only, with all behavioral logic frozen."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from .capability_gap import CapabilityGapRuntime, CapabilityGapStore
from .grounded_exploration import ExplorerConfidenceStore
from .grounded_learning import atomic_json, file_hash
from .live import ModelClient, SessionStore, _canonical
from .relation_routing import RelationEvidenceStore, relation_routed_clients
from .repair_resume import RepairStore
from .routing import RoutingError


POLICY_PATH=Path(__file__).with_name("coverage_extension_policy.json")
POLICY=json.loads(POLICY_PATH.read_text())
FROZEN_ROOT=Path(__file__).resolve().parent


def verify_frozen_implementation()->dict:
    for name,expected in POLICY["frozen_sha256"].items():
        actual=file_hash(FROZEN_ROOT/name)
        if actual!=expected: raise RoutingError(f"frozen behavioral file changed: {name}")
    return deepcopy(POLICY["frozen_sha256"])


def verify_consumed_repair(root:Path)->dict:
    repair=RepairStore(root)
    state=repair.state
    if state["lifecycle_state"]!=POLICY["repair_lifecycle_required"] or \
            state["restart_count"]!=POLICY["repair_restart_count_required"] or \
            state["reissue_count"]!=POLICY["repair_reissue_count_required"] or \
            state.get("repair_failed") is not False:
        raise RoutingError("v0.10 repair authority does not match consumed source state")
    return dict(lifecycle_state=state["lifecycle_state"],
        restart_count=state["restart_count"],reissue_count=state["reissue_count"],
        new_restart_authority=0,new_reissue_authority=0)


class CoverageExtensionRuntime(CapabilityGapRuntime):
    """Correct only sequence identity after v0.10's zero-call repaired batch."""
    def _next_batch(self):
        capture=self.reader.capture()
        sequence=self.store.checkpoint["attempted_decisions"]+1
        decision_id=(f"{self.store.checkpoint['session_id']}:e{capture['epoch']}:"
                     f"coverage:d{sequence}")
        return capture,self.map.forecasts(capture,decision_id),sequence,decision_id


def classify_outcome(failure:dict|None,terminal:str|None,decisions:int)->str:
    if failure: return failure["classification"]
    if terminal: return terminal
    if decisions==POLICY["maximum_fresh_behavioral_decisions"]:
        return "INCONCLUSIVE_AT_BOUND"
    raise RoutingError("nonterminal coverage run stopped before its frozen bound")


def eligible_reassessments(validated_gap_records:list[dict])->list[dict]:
    """Select only new authenticated journal records under the frozen contract."""
    return [r for r in validated_gap_records
        if r["kind"]=="CAPABILITY_GAP_DECISION_FROZEN" and
        r["record"]["decision_sequence"]>POLICY["source_attempted_decisions"] and
        r["record"]["pre_state"]==POLICY["required_reassessment_state"] and
        r["record"]["ordinary_decision"]["reason"]=="EXPLOIT_TIED_MAXIMUM" and
        all(v["valid"] for v in r["record"]["forecasts"].values())]


def _operational_failure(row:dict)->dict|None:
    if row.get("status")!="ABSTAINED" or row.get("explorer",{}).get(
            "reason")!="INVALID_MAP_COMPONENT":
        return None
    failures=[]
    for action,value in row.get("forecasts",{}).items():
        for key in ("selected_failure","G2_failure","G3_failure"):
            if value.get(key): failures.append(dict(action=action,component=key,
                                                    failure=value[key]))
    if not failures: return None
    return dict(classification="OPERATIONAL_FAILURE",localization="MODEL_SERVICE",
                failures=failures,repair_authority_consumed=True,
                retry_attempted=False,repair_attempted=False)


def run_coverage_extension(session_path:Path,registry_root:Path,
                           joint_client=None,specialist_clients=None)->dict:
    frozen=verify_frozen_implementation(); repair=verify_consumed_repair(registry_root)
    if specialist_clients is None:
        specialist_clients,relation_registry=relation_routed_clients(registry_root,device="cuda")
    else:
        from .relation_routing import load_relation_routing_registry
        relation_registry=load_relation_routing_registry(registry_root)
    joint=joint_client or ModelClient(); joint_before=joint.requests
    specialist_before={k:specialist_clients[k].requests for k in ("G2","G3")}
    with SessionStore(session_path,True) as session, \
            RelationEvidenceStore(registry_root) as routing, \
            ExplorerConfidenceStore(registry_root) as confidence, \
            CapabilityGapStore(registry_root) as gap:
        if (session.checkpoint["attempted_decisions"],len(session.records["events"]),
                len(session.records["training"]),sum(x["kind"]=="REQUEST_INTENT"
                for x in session.records["calls"])) != (
                POLICY["source_attempted_decisions"],POLICY["source_authorized_executions"],
                POLICY["source_training_records"],POLICY["source_request_intents"]):
            raise RoutingError("v0.10 session differs from frozen endpoint")
        problem=gap.state.get("current_problem")
        if gap.state["terminal_classification"] is not None or not problem or \
                problem["problem_id"]!=POLICY["required_problem_id"] or \
                problem["probe_count"]!=2 or session.checkpoint["current_state"]!=1:
            raise RoutingError("v0.10 unresolved coverage state is absent")
        session.configure_regime("A",False)
        rows=[]; states=[session.checkpoint["current_state"]]; failure=None
        runtime_indices=[]; runtime_boundaries=[]
        for segment,segment_bound in enumerate(POLICY["runtime_decision_schedule"],1):
            runtime=CoverageExtensionRuntime(session,joint,specialist_clients,
                relation_registry,routing,confidence,"A",gap_store=gap)
            runtime_indices.append(session.checkpoint["runtime_index"])
            runtime_boundaries.append(dict(segment=segment,
                runtime_index=session.checkpoint["runtime_index"],
                epoch=session.checkpoint["current_epoch"],
                source_identity=session.checkpoint["current_source_identity"],
                starts_at_fresh_decision=len(rows)+1,
                scheduled_decisions=segment_bound))
            for _ in range(segment_bound):
                row=runtime.execute_autonomous(); rows.append(row)
                states.append(session.checkpoint["current_state"])
                failure=_operational_failure(row)
                if failure or gap.state["terminal_classification"] is not None: break
            if failure or gap.state["terminal_classification"] is not None: break
        calls=joint.requests-joint_before+sum(specialist_clients[k].requests-
            specialist_before[k] for k in ("G2","G3"))
        if calls!=9*len(rows) or calls>POLICY["maximum_ordinary_prediction_calls"]:
            raise RoutingError("ordinary call accounting violates frozen structure")
        eligible=eligible_reassessments(gap.records)
        terminal=gap.state["terminal_classification"]
        status=classify_outcome(failure,terminal,len(rows))
        return dict(identity=POLICY["mode"],status=status,rows=rows,
            behavioral_decisions=len(rows),ordinary_prediction_calls=calls,
            operational_health_calls=0,repair_calls=0,
            authorized_world_executions=len(session.records["events"])-POLICY[
                "source_authorized_executions"],
            abstentions=sum(r["status"]=="ABSTAINED" for r in rows),
            realized_state_sequence=states,state_2_visits=sum(s==2 for s in states[1:]),
            valid_state_2_tied_reassessments=len(eligible),training_runs=0,
            classifier_result=terminal,operational_failure=failure,
            retained_problem=deepcopy(gap.state["current_problem"]),
            final_checkpoint=deepcopy(session.checkpoint),
            repair_authority=repair,frozen_implementation=frozen,
            only_intervention="MAXIMUM_FRESH_BEHAVIORAL_DECISIONS_5_TO_20",
            runtime_segmentation=dict(schedule=POLICY["runtime_decision_schedule"],
                protected_episode_limit=POLICY["protected_episode_limit"],
                boundaries=runtime_boundaries,runtime_indices=runtime_indices,
                outcome_conditioned=False),
            no_result_guaranteed=True)


def analyze_coverage_extension(session_path:Path,registry_root:Path,run:dict,
                               output:Path)->dict:
    if output.exists(): raise RoutingError("coverage report output already exists")
    verify_frozen_implementation(); repair=verify_consumed_repair(registry_root)
    with SessionStore(session_path,True) as session,CapabilityGapStore(registry_root) as gap:
        gap.bind_session(session); checkpoint=deepcopy(session.checkpoint)
        problem=deepcopy(gap.state["current_problem"])
    trace=[]
    for row in run["rows"]:
        receipt=row.get("receipt")
        trace.append(dict(decision_sequence=row["prediction_batch_sequence"],
            pre_state=row.get("pre_state",row.get("state")),status=row["status"],
            explorer_reason=row.get("explorer",{}).get("reason"),
            selected_action=row.get("explorer",{}).get("action"),
            realized_consequence=None if receipt is None else receipt["realized_consequence"],
            realized_next_state=None if receipt is None else receipt["next_state"],
            valid_predictions=all(v["valid"] for v in row.get("forecasts",{}).values())))
    report=dict(campaign_identity=POLICY["mode"],status=run["status"],
        parent_commit=POLICY["source_commit"],
        intervention="increase finite fresh behavioral decision bound from 5 to 20",
        frozen_bound=POLICY["maximum_fresh_behavioral_decisions"],
        accounting={k:run[k] for k in ("behavioral_decisions",
            "ordinary_prediction_calls","operational_health_calls","repair_calls",
            "authorized_world_executions","abstentions","training_runs")},
        realized_state_sequence=run["realized_state_sequence"],
        state_2_visits=run["state_2_visits"],
        valid_state_2_tied_reassessments=run["valid_state_2_tied_reassessments"],
        decision_trace=trace,classifier_result=run["classifier_result"],
        runtime_segmentation=run["runtime_segmentation"],
        operational_failure=run["operational_failure"],
        retained_capability_request=problem["requested_capability"],
        retained_localization=problem["where_did_resolution_stop"],
        problem_evidence=problem["problem_probe_history"],
        repair_authority=repair,frozen_implementation=run["frozen_implementation"],
        final_checkpoint=dict(attempted_decisions=checkpoint["attempted_decisions"],
            completed_steps=checkpoint["completed_steps"],runtime_index=checkpoint[
                "runtime_index"],current_state=checkpoint["current_state"],
            streams=checkpoint["streams"]),
        raw_private_model_stream_included=False,private_authority_material_included=False,
        prompts_included=False,raw_model_responses_included=False,
        equal_immediate_outcomes_prove_longer_horizon_value=False,
        absence_of_state_2_revisit_proves_structural_impossibility=False)
    atomic_json(output,report); return report
