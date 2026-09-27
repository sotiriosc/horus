"""Zero-inference scoped relation-routing reassessment for Horus v0.19."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from experiments.base_framework_v0.framework import ACTION_ORDER

from .core import MapForecast, MechanicalExplorer, digest
from .grounded_exploration import ExplorerConfidenceStore
from .grounded_learning import atomic_json, file_hash
from .live import SessionStore, _canonical, _now
from .problem_manager import ProblemManager
from .relation_routing import (RelationEvidenceStore, RelationGroundedRouter,
                               relation_identity, relation_key)
from .routing import RoutingError


CLASSIFICATIONS = ("ROUTING_CORRECT_AS_FROZEN", "ROUTING_SHOULD_HAVE_SWITCHED",
                   "ROUTING_EVIDENCE_INCONSISTENT")
ASSESSMENTS = ("RELATION_ROUTING_RESOLVED", "MORE_RELATION_EVIDENCE_REQUIRED",
               "ROUTING_CONTRADICTION", "VALUE_TIE_PERSISTS")
TARGET_RELATION = relation_identity(1, "ADVANCE")
REQUEST_REASON = "RELATION_SPECIFIC_EVIDENCE_INSUFFICIENT_FOR_SPECIALIST_SELECTION"


def _record(value: dict) -> dict:
    return value["record"] if "record" in value else value


def relation_rows(records: list[dict], relation: dict) -> list[dict]:
    key=relation_key(relation)
    return [_record(row) for row in records
            if relation_key(_record(row)["relation"])==key]


def compact_rows(records: list[dict], relation: dict) -> list[dict]:
    result=[]
    for row in relation_rows(records,relation):
        result.append(dict(evidence_sequence=row["evidence_sequence"],
            G2_frozen_prediction=row["specialists"]["G2"]["frozen_consequence"],
            G3_frozen_prediction=row["specialists"]["G3"]["frozen_consequence"],
            realized_consequence=row["realized_consequence"],
            G2_correct=bool(row["correctness"]["G2"]),
            G3_correct=bool(row["correctness"]["G3"]),
            selected_specialist_before=row["selected_specialist"],
            selected_specialist_after=row["selected_specialist_after"],
            receipt_identity=deepcopy(row["receipt_identity"])))
    return result


def reconstruct_routing(records: list[dict], relation: dict, retained: dict,
                        policy: dict) -> dict:
    """Replay exact local rows and classify retained selection without repair."""
    router=RelationGroundedRouter(policy); prefix=[]; selected="G2"
    try:
        for row in relation_rows(records,relation):
            if row["selected_specialist"]!=selected or \
                    row["router_score_before"]!=router.scores(prefix,relation):
                raise RoutingError("stored before-state does not replay")
            prefix.append(row); update=router.update(prefix,relation,selected)
            if row["router_score_after"]!=update["scores"] or \
                    row["selected_specialist_after"]!=update["selected_after"] or \
                    bool(row["switch_occurred"])!=update["switched"]:
                raise RoutingError("stored router transition does not replay")
            selected=update["selected_after"]
        scores=router.scores(prefix,relation)
        expected=dict(relation=relation,selected_specialist=selected,
            evidence_count=len(prefix),last_evidence_sequence=(None if not prefix else
            prefix[-1]["evidence_sequence"]))
        if retained!=expected:
            final=router.update(prefix,relation,"G2")
            classification=("ROUTING_SHOULD_HAVE_SWITCHED" if
                retained.get("selected_specialist")=="G2" and
                final["selected_after"]=="G3" else "ROUTING_EVIDENCE_INCONSISTENT")
            return dict(classification=classification,consistent=False,
                expected_state=expected,retained_state=deepcopy(retained),scores=scores)
        lead=scores["G3"]["correct"]-scores["G2"]["correct"]
        return dict(classification="ROUTING_CORRECT_AS_FROZEN",consistent=True,
            expected_state=expected,retained_state=deepcopy(retained),scores=scores,
            current_selected_specialist=selected,
            minimum_evidence_threshold=policy["minimum_shared_scored_events"],
            required_challenger_lead=policy["switch_lead_correct"],
            current_G3_challenger_lead=lead,
            switch_rule_satisfied=(scores["G2"]["total"]>=policy[
                "minimum_shared_scored_events"] and lead>=policy["switch_lead_correct"]))
    except (KeyError,TypeError,RoutingError) as exc:
        return dict(classification="ROUTING_EVIDENCE_INCONSISTENT",consistent=False,
                    error=str(exc),retained_state=deepcopy(retained))


def route_availability(confidence_state: dict, exploration_policy: dict,
                       problem: dict) -> dict:
    next_authorized=confidence_state["authorized_decisions"]+1
    last_probe=confidence_state["last_probe_authorized_decision"]
    distance=None if last_probe is None else next_authorized-last_probe
    required=exploration_policy["probe_budget"]["minimum_decision_distance"]
    ordinary_available=last_probe is None or distance>=required
    budget=problem["route_budgets"].get("deadlock_information_probe")
    deadlock_available=bool(budget and budget["granted"]<budget["limit"])
    return dict(existing_route="RELATION_PROBE",
        relation_probe_cadence=dict(next_authorized_decision=next_authorized,
            last_probe_authorized_decision=last_probe,distance=distance,
            minimum_distance=required,available=ordinary_available),
        deadlock_probe_budget=deepcopy(budget),
        deadlock_probe_available=deadlock_available,
        existing_route_legally_available=ordinary_available or deadlock_available,
        selected_route=("RELATION_PROBE" if ordinary_available else
            ("DEADLOCK_INFORMATION_PROBE" if deadlock_available else None)),
        authority_status=("EXISTING_ROUTE" if ordinary_available or deadlock_available
                          else "REQUEST_REQUIRES_EXTERNAL_APPROVAL"))


def latest_state_forecasts(exploration_records: list[dict], state: int) -> dict:
    rows=[_record(row) for row in exploration_records
          if row.get("kind")=="EXPLORER_DECISION_FROZEN" and
          _record(row).get("pre_state")==state]
    if not rows: raise RoutingError("state has no frozen Explorer decision")
    row=rows[-1]
    if not all(row["forecasts"][a].get("valid") is True for a in ACTION_ORDER):
        raise RoutingError("latest state forecasts are not all valid")
    return dict(decision_sequence=row["decision_sequence"],
        values={a:row["forecasts"][a]["routed_consequence"] for a in ACTION_ORDER},
        selected={a:row["forecasts"][a]["selected_specialist"] for a in ACTION_ORDER},
        ordinary_decision=deepcopy(row["decision"]))


def reassess_values(forecasts: dict[str,int]) -> dict:
    maximum=max(forecasts.values()); tied=[a for a in ACTION_ORDER if forecasts[a]==maximum]
    rows=tuple(MapForecast(action=a,action_alias=f"K{index+1}",next_state=None,
        consequence=forecasts[a],abstained=False,failure=None,history_count=1,
        input_context={}) for index,a in enumerate(ACTION_ORDER))
    choice=MechanicalExplorer().choose(rows)
    return dict(values=deepcopy(forecasts),tied_maximum_actions=tied,
        ordinary_action=choice.action,ordinary_abstained=choice.abstained,
        ordinary_reason=("UNIQUE_ROUTED_MAXIMUM" if choice.reason=="UNIQUE_MAXIMUM"
                         else f"EXPLOIT_{choice.reason}"))


def _hash_lines(path: Path) -> dict:
    lines=path.read_text().splitlines()
    return dict(records=len(lines),sha256=file_hash(path),
                head_sha256=(None if not lines else sha256(lines[-1].encode()).hexdigest()))


def run_zero_inference(*, session_root: Path, registry_root: Path,
                       output_root: Path, emit_request: bool=True) -> dict:
    """Authenticate, reconstruct, optionally persist the external route request."""
    output_root.mkdir(parents=True,exist_ok=True)
    session_stats_before={name:_hash_lines(session_root/name) for name in
        ("events.jsonl","model-calls.private.jsonl","training-records.jsonl")}
    with SessionStore(session_root) as session, \
            RelationEvidenceStore(registry_root) as routing, \
            ExplorerConfidenceStore(registry_root) as confidence, \
            ProblemManager(registry_root) as manager:
        routing.bind_session(session); confidence.bind_session(session); manager.bind_session(session)
        before_pr2=deepcopy(manager.state["problems"]["PR-0002"])
        before_pr3=deepcopy(manager.state["problems"]["PR-0003"])
        retained=routing.state["relations"]["1:ADVANCE"]
        advance=reconstruct_routing(routing.records,TARGET_RELATION,retained,
                                    routing.registry["policy"])
        hold_relation=relation_identity(1,"HOLD")
        hold=reconstruct_routing(routing.records,hold_relation,
            routing.state["relations"]["1:HOLD"],routing.registry["policy"])
        recent_G3_superiority=False
        if advance["classification"]!="ROUTING_CORRECT_AS_FROZEN":
            live_required=False; availability=None; request=None
            assessment="ROUTING_CONTRADICTION"
        else:
            latest=relation_rows(routing.records,TARGET_RELATION)[-1]
            recent_G3_superiority=(latest["correctness"]["G3"] is True and
                                   latest["correctness"]["G2"] is False)
            availability=route_availability(confidence.state,confidence.registry["policy"],before_pr3)
            live_required=recent_G3_superiority and not advance["switch_rule_satisfied"]
            request=None
            if live_required and not availability["existing_route_legally_available"] and emit_request:
                existing=[row for row in manager.records if row["kind"]=="RELATION_EVIDENCE_REQUESTED"
                          and row["record"].get("problem_id")=="PR-0003" and
                          row["record"].get("relation")==TARGET_RELATION]
                request=(deepcopy(existing[-1]) if existing else manager.request_relation_evidence(
                    problem_id="PR-0003",relation=TARGET_RELATION,
                    classification=advance["classification"],
                    latest_evidence_sequence=latest["evidence_sequence"],
                    latest_grounded_comparison={"G2_correct":False,"G3_correct":True},
                    current_scores=advance["scores"],
                    selected_specialist=advance["current_selected_specialist"],
                    route_availability=availability))
            assessment=("MORE_RELATION_EVIDENCE_REQUIRED" if live_required else
                        "VALUE_TIE_PERSISTS")
        current=latest_state_forecasts(confidence.records,1)
        value_reassessment=reassess_values(current["values"])
        after_pr2=deepcopy(manager.state["problems"]["PR-0002"])
        after_pr3=deepcopy(manager.state["problems"]["PR-0003"])
        result=dict(identity="HORUS_V019_SCOPED_RELATION_REASSESSMENT",
            generated_at=_now(),parent_commit="3d4ec4ae30f16f42850abcc6f93358bab5488b0e",
            target_problem="PR-0003",target_relation=TARGET_RELATION,
            zero_inference_classification=advance["classification"],
            advance_reconstruction=advance,advance_evidence=compact_rows(
                routing.records,TARGET_RELATION),hold_reconstruction=hold,
            hold_evidence=compact_rows(routing.records,hold_relation),
            pr0003_before=before_pr3,pr0003_after=after_pr3,
            decision_84=dict(selected_action="ADVANCE",
                G2_forecast=compact_rows(routing.records,TARGET_RELATION)[-1]["G2_frozen_prediction"],
                G3_forecast=compact_rows(routing.records,TARGET_RELATION)[-1]["G3_frozen_prediction"],
                realized_consequence=before_pr3["probe_evidence"]["ADVANCE"][-1]["realized_consequence"],
                realized_next_state=before_pr3["probe_evidence"]["ADVANCE"][-1]["realized_next_state"],
                receipt_identity=before_pr3["probe_evidence"]["ADVANCE"][-1]["receipt_identity"]),
            recent_G3_grounded_superiority=recent_G3_superiority,
            live_evidence_required=live_required,route_availability=availability,
            route_request=(None if request is None else request["record"]),
            live_execution_performed=False,fresh_decisions=0,model_calls=0,
            new_receipts=[],router_switch_occurred=False,
            state1_reassessment=value_reassessment,ordinary_follow_up=None,
            final_pr0003_assessment=assessment,
            pr0002_unchanged=(before_pr2==after_pr2),
            pr0002_sha256=digest(before_pr2),pr0003_before_sha256=digest(before_pr3),
            pr0003_after_sha256=digest(after_pr3),option_profile_applied_to_pr0003=False,
            training_runs=0,hidden_transition_destination_used=False,
            stop_reason=("EXTERNAL_APPROVAL_REQUIRED_FOR_SCOPED_RELATION_PROBE" if
                live_required and availability and not availability[
                    "existing_route_legally_available"] else "ZERO_INFERENCE_COMPLETE"))
    session_stats_after={name:_hash_lines(session_root/name) for name in session_stats_before}
    result["session_streams_unchanged"]=session_stats_before==session_stats_after
    result["session_streams"]=session_stats_after
    atomic_json(output_root/"results.json",result)
    atomic_json(output_root/"routing-evidence.json",dict(
        target_relation=TARGET_RELATION,rows=result["advance_evidence"],
        reconstruction=result["advance_reconstruction"],
        hold_rows=result["hold_evidence"],hold_reconstruction=result["hold_reconstruction"]))
    atomic_json(output_root/"route-request.json",dict(
        request=result["route_request"],availability=result["route_availability"],
        authoritative=False,can_execute=False))
    return result


def verify_result(result: dict) -> None:
    if result["zero_inference_classification"] not in CLASSIFICATIONS or \
            result["final_pr0003_assessment"] not in ASSESSMENTS:
        raise RoutingError("unknown reassessment result")
    if result["live_execution_performed"] or result["model_calls"] or \
            result["training_runs"] or not result["pr0002_unchanged"] or \
            not result["session_streams_unchanged"]:
        raise RoutingError("zero-inference boundary was violated")
