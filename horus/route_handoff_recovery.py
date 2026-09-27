"""Bounded v0.22 recovery of the authenticated decision-91 prediction tail."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from hmac import compare_digest, new as new_hmac
import json
from pathlib import Path
from typing import Any

from experiments.base_framework_v0.framework import ACTION_ORDER

from .core import GroundedObservation, MapForecast, digest
from .grounded_exploration import ExplorerConfidenceStore, GroundedExplorer
from .grounded_learning import atomic_json
from .live import SessionStore, _atomic_write, _canonical, _now
from .problem_manager import ProblemManager, ProblemOwnershipRuntime
from .relation_routing import (RelationEvidenceStore, load_relation_routing_registry,
                               relation_identity, relation_key)
from .routing import RoutedForecastBatch, RoutingError


EXPECTED_CHECKPOINT_COUNT = 2502
EXPECTED_PHYSICAL_COUNT = 2529
EXPECTED_TAIL_RECORDS = 27
EXPECTED_DECISION_SEQUENCE = 91
EXPECTED_LOGICAL_ID = (
    "a67e675004193a13c31485bad53fbb86:e2015:relation-reacquisition:d91")
TARGET = relation_identity(1, "ADVANCE")
SAFETY_KEYS = (
    "tail_authenticated", "chain_continuous", "single_unfinished_decision",
    "no_receipt", "no_memory_publication", "no_routing_evidence",
    "no_explorer_completion", "no_contradictory_state")


def _stream_head(envelope: dict) -> str:
    return sha256(_canonical(envelope).encode()).hexdigest()


def _authenticated_file(path: Path, key: bytes) -> list[dict]:
    rows: list[dict] = []
    previous = None
    try:
        lines = path.read_text().splitlines()
    except OSError as exc:
        raise RoutingError(f"missing durable stream: {path.name}") from exc
    for sequence, line in enumerate(lines, 1):
        try:
            envelope = json.loads(line)
            signed = {name: envelope[name] for name in
                      ("sequence", "previous_sha256", "kind", "record")}
        except (ValueError, KeyError, TypeError) as exc:
            raise RoutingError(f"invalid durable stream: {path.name}") from exc
        expected_mac = new_hmac(key, _canonical(signed).encode(), "sha256").hexdigest()
        if envelope["sequence"] != sequence or envelope[
                "previous_sha256"] != previous or not compare_digest(
                    expected_mac, envelope.get("hmac_sha256", "")):
            raise RoutingError(f"unauthenticated durable stream: {path.name}")
        previous = _stream_head(envelope)
        rows.append(envelope)
    return rows


def _checkpoint(session_root: Path, key: bytes) -> tuple[dict, dict]:
    try:
        document = json.loads((session_root / "checkpoint.json").read_text())
        payload = document["payload"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise RoutingError("invalid recovery checkpoint") from exc
    expected = new_hmac(key, _canonical(payload).encode(), "sha256").hexdigest()
    if not compare_digest(expected, document.get("hmac_sha256", "")):
        raise RoutingError("recovery checkpoint authentication failed")
    return document, payload


def _tail_calls(tail: list[dict]) -> tuple[dict[str, dict], dict[str, str]]:
    calls: dict[str, dict] = {}
    logical_ids: set[str] = set()
    for envelope in tail:
        record = envelope["record"]
        call_id = record.get("call_id")
        if not isinstance(call_id, str) or ":d91:" not in call_id:
            raise RoutingError("tail is not the known unfinished decision")
        logical, action, role = call_id.rsplit(":", 2)
        if logical != EXPECTED_LOGICAL_ID or action not in ACTION_ORDER or role not in (
                "J", "G2", "G3"):
            raise RoutingError("tail call identity is outside decision 91")
        logical_ids.add(logical)
        item = calls.setdefault(call_id, {})
        if envelope["kind"] in item:
            raise RoutingError("duplicate tail call stage")
        item[envelope["kind"]] = envelope
    expected_ids = {f"{EXPECTED_LOGICAL_ID}:{action}:{role}"
                    for action in ACTION_ORDER for role in ("J", "G2", "G3")}
    if logical_ids != {EXPECTED_LOGICAL_ID} or set(calls) != expected_ids:
        raise RoutingError("tail does not contain exactly nine known calls")
    request_hashes: dict[str, str] = {}
    for call_id, stages in calls.items():
        if set(stages) != {"REQUEST_INTENT", "RESPONSE", "PARSED"}:
            raise RoutingError("tail call lacks one authenticated stage")
        intent = stages["REQUEST_INTENT"]["record"]
        response = stages["RESPONSE"]["record"]
        parsed = stages["PARSED"]["record"]
        if intent.get("request_sha256") != digest(intent.get("request")) or \
                response.get("response_sha256") != digest(response.get("response")) or \
                parsed.get("parse_error") is not None or parsed.get("parsed") is None:
            raise RoutingError("tail request/response/parse binding failed")
        request_hashes[call_id] = intent["request_sha256"]
    return calls, request_hashes


def tail_safety(*, chain_continuous: bool, event_matches: list,
                training_matches: list, routing_matches: list,
                explorer_matches: list, contradictory_state: bool) -> dict:
    """Name all fail-closed recovery predicates in one reviewable decision."""
    return dict(tail_authenticated=True,chain_continuous=chain_continuous,
        single_unfinished_decision=True,no_receipt=not event_matches,
        no_memory_publication=not event_matches and not training_matches,
        no_routing_evidence=not routing_matches,
        no_explorer_completion=not explorer_matches,
        no_contradictory_state=not contradictory_state)


def inspect_tail(session_root: Path, registry_root: Path) -> dict:
    """Authenticate and classify the exact physical suffix without mutating it."""
    session_root, registry_root = session_root.resolve(), registry_root.resolve()
    try:
        key = bytes.fromhex((session_root / "authority.key").read_text().strip())
    except (OSError, ValueError) as exc:
        raise RoutingError("invalid recovery authority key") from exc
    if len(key) != 32:
        raise RoutingError("invalid recovery authority key")
    _, checkpoint = _checkpoint(session_root, key)
    streams = {name: _authenticated_file(session_root / filename, key)
               for name, filename in SessionStore.STREAMS.items()}
    calls = streams["calls"]
    registered = checkpoint["streams"]["calls"]
    prefix_head = _stream_head(calls[EXPECTED_CHECKPOINT_COUNT - 1])
    chain_continuous = registered == {
        "count": EXPECTED_CHECKPOINT_COUNT, "head_sha256": prefix_head}
    if len(calls) != EXPECTED_PHYSICAL_COUNT or not chain_continuous:
        raise RoutingError("checkpoint/call-tail boundary differs from v0.21")
    tail = calls[EXPECTED_CHECKPOINT_COUNT:]
    parsed_calls, request_hashes = _tail_calls(tail)
    event_matches = [row for row in streams["events"] if row["record"].get(
        "prediction_batch_sequence") == EXPECTED_DECISION_SEQUENCE]
    training_matches = [row for row in streams["training"] if row["record"].get(
        "prediction_batch_sequence") == EXPECTED_DECISION_SEQUENCE]
    with RelationEvidenceStore(registry_root) as routing, \
            ExplorerConfidenceStore(registry_root) as confidence, \
            ProblemManager(registry_root) as manager:
        call_ids = set(parsed_calls)
        routing_matches = [row for row in routing.records if any(
            commitment.get("call_id") in call_ids for commitment in (
                [row["record"].get("prediction_commitment",{}).get("joint",{})] +
                list(row["record"].get("prediction_commitment",{}).get(
                    "specialists",{}).values())))]
        explorer_matches = [row for row in confidence.records if row["record"].get(
            "decision_sequence") == EXPECTED_DECISION_SEQUENCE]
        contradictory = not (
            checkpoint["attempted_decisions"] == 90 and
            checkpoint["completed_steps"] == 57 and
            checkpoint["current_state"] == 1 and
            len(streams["events"]) == 57 and len(streams["training"]) == 93 and
            confidence.state["attempted_decisions"] == 90 and
            confidence.state["authorized_decisions"] == 57 and
            confidence.state["pending_decision"] is None and
            manager.state["attempted_decisions"] == 90 and
            manager.state["authorized_executions"] == 57 and
            manager.state["pending_decision"] is None and
            routing.state["evidence_count"] == 57)
    safety = tail_safety(chain_continuous=chain_continuous,
        event_matches=event_matches,training_matches=training_matches,
        routing_matches=routing_matches,explorer_matches=explorer_matches,
        contradictory_state=contradictory)
    if set(safety) != set(SAFETY_KEYS) or not all(safety.values()):
        raise RoutingError("DURABLE_TAIL_RECOVERY_REJECTED")
    return dict(identity="UNCOMMITTED_AUTHENTICATED_CALL_TAIL",
        checkpoint_count=EXPECTED_CHECKPOINT_COUNT,
        checkpoint_head_sha256=prefix_head, physical_count=len(calls),
        physical_head_sha256=_stream_head(calls[-1]), tail_records=len(tail),
        tail_first_sequence=tail[0]["sequence"],tail_last_sequence=tail[-1]["sequence"],
        logical_decision_id=EXPECTED_LOGICAL_ID,
        decision_sequence=EXPECTED_DECISION_SEQUENCE,
        request_hashes=request_hashes, safety_conditions=safety, calls=parsed_calls)


def advance_checkpoint(session_root: Path, proof: dict) -> dict:
    """Register the already-authenticated physical head; never touch the stream."""
    session_root = session_root.resolve()
    key = bytes.fromhex((session_root / "authority.key").read_text().strip())
    _, payload = _checkpoint(session_root, key)
    current = payload["streams"]["calls"]
    if current != {"count": proof["checkpoint_count"],
                   "head_sha256": proof["checkpoint_head_sha256"]}:
        raise RoutingError("checkpoint changed before recovery")
    before_bytes = (session_root / SessionStore.STREAMS["calls"]).read_bytes()
    payload = deepcopy(payload)
    payload["streams"]["calls"] = {
        "count": proof["physical_count"],
        "head_sha256": proof["physical_head_sha256"]}
    payload["updated_at"] = _now()
    document = {"payload": payload, "hmac_sha256": new_hmac(
        key, _canonical(payload).encode(), "sha256").hexdigest()}
    _atomic_write(session_root / "checkpoint.json", document)
    if (session_root / SessionStore.STREAMS["calls"]).read_bytes() != before_bytes:
        raise RoutingError("call stream changed during checkpoint recovery")
    return dict(status="DURABLE_TAIL_RECOVERED",registered_count=proof[
        "physical_count"],registered_head_sha256=proof["physical_head_sha256"],
        stream_records_rewritten=False,model_calls_reissued=False)


def choose_route(ordinary: dict, fallback: dict | None) -> dict:
    """Freeze route precedence: ordinary, then existing fallback, then abstain."""
    ordinary_available = (ordinary.get("action") in ACTION_ORDER and
                          ordinary.get("abstained") is False and
                          ordinary.get("reason") != "INVALID_MAP_COMPONENT")
    if ordinary_available:
        return dict(selected_route="ORDINARY_EXPLORER", decision=deepcopy(ordinary),
                    status="NORMAL_ROUTE_REGAINS_CONTROL")
    if fallback is not None and fallback.get("action") in ACTION_ORDER and \
            fallback.get("abstained") is False:
        return dict(selected_route="PROBLEM_SCOPED_FALLBACK",
                    decision=deepcopy(fallback),status="FALLBACK_ROUTE_SELECTED")
    return dict(selected_route=None,decision=deepcopy(ordinary),
                status="ABSTAIN_OR_REQUEST_AUTHORITY")


def _recovered_batch(proof: dict, capture: dict, registry: dict) -> RoutedForecastBatch:
    calls = proof["calls"]
    forecasts = {"G2": [], "G3": []}
    evidence, commitments = {}, {}
    for action in ACTION_ORDER:
        by_role = {role: calls[f"{EXPECTED_LOGICAL_ID}:{action}:{role}"]
                   for role in ("J", "G2", "G3")}
        payloads = [json.loads(by_role[role]["REQUEST_INTENT"]["record"][
            "request"]["prompt"]) for role in ("J", "G2", "G3")]
        if payloads[1:] != payloads[:1] * 2 or payloads[0] != capture[
                "map_inputs"][action]:
            raise RoutingError("recovered request inputs differ from current authenticated capture")
        payload = payloads[0]
        history = tuple(GroundedObservation(**item) for item in payload[
            "VERIFIED_CHRONOLOGICAL_HISTORY"])
        input_context = dict(state=capture["state"],action=action,
            action_alias=payload["target_action"],epoch=capture["epoch"],
            transaction_id=capture["transaction_id"],
            authenticated_history=[item.__dict__ for item in history],
            memory_sha256=capture["memory_sha256"],
            authenticated_history_reference=capture["authenticated_history_reference"],
            recovered_request_decision_id=EXPECTED_LOGICAL_ID)
        j = by_role["J"]["PARSED"]["record"]["parsed"]
        commitments[action] = dict(joint=dict(
            call_id=f"{EXPECTED_LOGICAL_ID}:{action}:J",
            request_sequence=by_role["J"]["REQUEST_INTENT"]["sequence"],
            response_sequence=by_role["J"]["RESPONSE"]["sequence"],
            parsed_sequence=by_role["J"]["PARSED"]["sequence"],
            request_sha256=by_role["J"]["REQUEST_INTENT"]["record"][
                "request_sha256"]), specialists={})
        evidence[action] = {}
        for specialist in ("G2", "G3"):
            stages = by_role[specialist]
            consequence = stages["PARSED"]["record"]["parsed"]["consequence"]
            forecasts[specialist].append(MapForecast(action,payload["target_action"],
                j["next_state"],consequence,False,None,len(history),deepcopy(input_context)))
            evidence[action][specialist] = dict(recovered=True,
                response_sha256=stages["RESPONSE"]["record"]["response_sha256"],
                parsed_sha256=digest(stages["PARSED"]["record"]["parsed"]))
            commitments[action]["specialists"][specialist] = dict(
                call_id=f"{EXPECTED_LOGICAL_ID}:{action}:{specialist}",
                request_sequence=stages["REQUEST_INTENT"]["sequence"],
                response_sequence=stages["RESPONSE"]["sequence"],
                parsed_sequence=stages["PARSED"]["sequence"],
                request_sha256=stages["REQUEST_INTENT"]["record"]["request_sha256"],
                prediction=consequence,
                artifact_sha256=registry["specialists"][specialist]["artifact_sha256"])
    return RoutedForecastBatch({key:tuple(value) for key,value in forecasts.items()},
                               evidence,commitments,True)


def zero_inference_proof(proof: dict, registry_root: Path) -> dict:
    """Replay the post-navigation policy from durable data before recovery."""
    registry = load_relation_routing_registry(registry_root)
    capture = dict(state=1,epoch=2015,transaction_id=2,memory_sha256="replay-only",
        authenticated_history_reference={},map_inputs={})
    for action in ACTION_ORDER:
        intent=proof["calls"][f"{EXPECTED_LOGICAL_ID}:{action}:J"][
            "REQUEST_INTENT"]["record"]
        capture["map_inputs"][action]=json.loads(intent["request"]["prompt"])
    batch = _recovered_batch(proof,capture,registry)
    with RelationEvidenceStore(registry_root) as routing, \
            ExplorerConfidenceStore(registry_root) as confidence, \
            ProblemManager(registry_root) as manager:
        previews=routing.preview_state(1)
        selections={action:previews[action]["selected_specialist"] for action in ACTION_ORDER}
        routed=tuple(next(row for row in batch.forecasts[selections[action]]
                          if row.action==action) for action in ACTION_ORDER)
        public=ProblemOwnershipRuntime._public_forecasts(batch,selections)
        ordinary=GroundedExplorer(confidence.registry["policy"]).derive(pre_state=1,
            forecasts=public,routed_forecasts=routed,previews=previews,
            routing_records=routing.records,confidence_state=confidence.state,
            all_predictions_valid=True)
        pr3=deepcopy(manager.state["problems"]["PR-0003"])
        route=choose_route(ordinary,{"mode":"PROBLEM_SCOPED_PROBE","action":"ADVANCE",
            "reason":"GROUND_RELATION_FOR_SPECIALIST_SELECTION","abstained":False})
        cadence=dict(authorized_decisions=confidence.state["authorized_decisions"],
            last_probe_authorized_decision=confidence.state[
                "last_probe_authorized_decision"],next_authorized_decision=confidence.state[
                "authorized_decisions"]+1,minimum_distance=confidence.registry["policy"][
                "probe_budget"]["minimum_decision_distance"])
    expected=(ordinary["decision_sequence"]==91 and ordinary["mode"]=="PROBE" and
              ordinary["reason"]=="PROBE_DISAGREEMENT" and ordinary["action"]=="ADVANCE" and
              ordinary["abstained"] is False and ordinary["probe_budget_available"] is True and
              pr3.get("target_relation_reacquired") is True and
              route["selected_route"]=="ORDINARY_EXPLORER")
    if not expected:
        raise RoutingError("zero-inference route handoff did not replay exactly")
    return dict(identity="ZERO_INFERENCE_ROUTE_HANDOFF_PROOF",state=1,
        problem_id="PR-0003",problem_applicable=True,target_relation_reacquired=True,
        cadence=cadence,ordinary_decision=ordinary,route_precedence=route["status"],
        selected_route=route["selected_route"],scoped_fallback_eligible_to_supersede=False,
        model_calls=0)


class NoCallClient:
    def __init__(self, model_id: str, identity: dict | None=None):
        self.model_id=model_id; self.horus_model_identity=identity or {}; self.requests=0
    def generate(self, _request: dict):
        raise RoutingError("recovered execution attempted a model call")


class RecoveredDecisionRuntime(ProblemOwnershipRuntime):
    def __init__(self,*args,recovery_proof: dict,**kwargs):
        self.recovery_proof=recovery_proof
        super().__init__(*args,**kwargs)
    def _next_batch(self):
        capture=self.reader.capture()
        batch=_recovered_batch(self.recovery_proof,capture,self.registry)
        return capture,batch,EXPECTED_DECISION_SEQUENCE,EXPECTED_LOGICAL_ID
    def execute_autonomous(self):
        row=super().execute_autonomous()
        if row.get("model_calls")!=9:
            raise RoutingError("unexpected recovered runtime call accounting")
        row["model_calls"]=0; row["recovered_model_calls"]=9
        return row


def _window(routing: RelationEvidenceStore) -> list[dict]:
    return [deepcopy(row["record"]) for row in routing.records
            if relation_key(row["record"]["relation"])==relation_key(TARGET)][-6:]


def _compact_window(row: dict) -> dict:
    return {key:deepcopy(row[key]) for key in ("evidence_sequence","relation",
        "receipt_identity","realized_consequence","specialist_predictions","correctness")}


def execute_recovered(*, session_root: Path, registry_root: Path,
                      output: Path) -> dict:
    proof=inspect_tail(session_root,registry_root)
    zero=zero_inference_proof(proof,registry_root)
    recovery=advance_checkpoint(session_root,proof)
    registry=load_relation_routing_registry(registry_root)
    specialists={}
    for name in ("G2","G3"):
        row=registry["specialists"][name]
        identity=dict(specialist_id=name,generation=row["generation"],
            parent_generation=row["parent_generation"],
            base_model_identity=row["base_model_identity"],
            artifact_sha256=row["artifact_sha256"],
            adapter_identity=f"generation-{row['generation']}:{row['artifact_sha256']}",
            global_lifecycle_status=row["global_lifecycle_status"],
            routing_eligibility=row["routing_eligibility"])
        specialists[name]=NoCallClient(f"recovered-{name}",identity)
    joint=NoCallClient("recovered-joint")
    with SessionStore(session_root,True) as store, \
            RelationEvidenceStore(registry_root) as routing, \
            ExplorerConfidenceStore(registry_root) as confidence, \
            ProblemManager(registry_root) as manager:
        manager.bind_session(store); before_pr3=deepcopy(manager.state["problems"]["PR-0003"])
        budget_before=deepcopy(before_pr3["route_budgets"]["problem_scoped_relation_probe"])
        window_before=_window(routing)
        manager.record_uncommitted_call_tail(problem_id="PR-0005",
            logical_decision_id=proof["logical_decision_id"],decision_sequence=91,
            checkpoint_count=proof["checkpoint_count"],physical_count=proof["physical_count"],
            tail_records=proof["tail_records"],tail_head_sha256=proof[
                "physical_head_sha256"],safety_conditions=proof["safety_conditions"])
        manager.record_tail_recovered(problem_id="PR-0005",**recovery)
        manager.record_normal_route_handoff(problem_id="PR-0005",
            blocked_problem_id="PR-0003",ordinary_decision=zero["ordinary_decision"],
            selected_route="ORDINARY_EXPLORER",scoped_fallback_superseded=True)
        runtime=RecoveredDecisionRuntime(store,joint,specialists,registry,routing,confidence,"A",
            problem_manager=manager,recovery_proof=proof)
        row=runtime.execute_autonomous()
        calls_issued=joint.requests+sum(client.requests for client in specialists.values())
        if calls_issued!=0 or row["status"]!="AUTHORIZED" or row[
                "explorer"]["mode"]!="PROBE" or row["explorer"][
                "reason"]!="PROBE_DISAGREEMENT" or row["explorer"]["action"]!="ADVANCE":
            raise RoutingError("recovered ordinary decision changed")
        receipt=row["receipt"]; routing_compact={key:deepcopy(row["routing_evidence"][key])
            for key in ("relation","evidence_sequence","selected_specialist",
                "selected_specialist_after","router_score_after","switch_occurred",
                "realized_consequence","receipt_identity")}
        receipt_compact=dict(receipt_identity=[receipt[k] for k in (
            "source_identity","event_id","epoch","transaction_id")],
            action=receipt["action"],realized_consequence=receipt["realized_consequence"],
            realized_next_state=receipt["next_state"],receipt_is_authenticated=True)
        scores=routing_compact["router_score_after"]
        threshold=(scores["G2"]["total"]>=3 and abs(scores["G2"]["correct"]-
                   scores["G3"]["correct"])>=2)
        manager.record_normal_route_reassessment(problem_id="PR-0003",
            decision_sequence=91,receipt=receipt_compact,routing_evidence=routing_compact,
            switch_threshold_satisfied=threshold)
        manager.close_route_handoff_repair(problem_id="PR-0005",
            model_calls_issued=0,decision_status=row["status"])
        window_after=_window(routing)
        budget_after=deepcopy(manager.state["problems"]["PR-0003"][
            "route_budgets"]["problem_scoped_relation_probe"])
        if budget_after!=budget_before:
            raise RoutingError("ordinary route consumed scoped fallback budget")
        selection_after={action:routing.preview(action=action,pre_state=1)[
            "selected_specialist"] for action in ACTION_ORDER}
        values={action:row["forecasts"][action][f"{selection_after[action]}_consequence"]
                for action in ACTION_ORDER}
        maximum=max(values.values()); maximizing=[a for a in ACTION_ORDER if values[a]==maximum]
        result=dict(identity="HORUS_V022_ROUTE_HANDOFF_DURABLE_RECOVERY",
            status="COMPLETED",route_handoff_rule=["ORDINARY_LEGITIMATE_EXPLORER_ROUTE",
                "EXISTING_PROBLEM_SCOPED_FALLBACK","ABSTAIN_OR_REQUEST_AUTHORITY"],
            zero_inference_proof=zero,
            tail_recovery={key:value for key,value in proof.items() if key not in ("calls",)},
            checkpoint_recovery=recovery,model_calls_issued=calls_issued,
            recovered_model_calls=9,reconstructed_decision=deepcopy(row["explorer"]),
            action_executed=receipt["action"],receipt=deepcopy(receipt),
            receipt_provenance_sha256=digest(receipt),
            rolling_window=dict(evicted=_compact_window(window_before[0]),
                added=_compact_window(window_after[-1]),before=[_compact_window(x) for x in window_before],
                after=[_compact_window(x) for x in window_after]),
            router_scores=deepcopy(scores),selected_specialist_before=routing_compact[
                "selected_specialist"],selected_specialist_after=routing_compact[
                "selected_specialist_after"],specialist_switched=routing_compact["switch_occurred"],
            state_1_values=dict(values=values,maximizing_actions=maximizing,
                                tie_present=len(maximizing)>1),
            ordinary_followup=dict(executed=False,reason=(
                "NO_REUSABLE_PREDICTION_BATCH; NEW_MODEL_CALLS_REQUIRE_SEPARATE_AUTHORIZATION")),
            scoped_budget_before=budget_before,scoped_budget_after=budget_after,
            pr0003_final=deepcopy(manager.state["problems"]["PR-0003"]),
            pr0005_final=deepcopy(manager.state["problems"]["PR-0005"]),
            final_checkpoint=deepcopy(store.checkpoint),
            training_performed=False,weights_modified=False,new_route_created=False,
            limitation=("The single recovered probe tests one realized regime-A outcome; "
                        "no ordinary follow-up ran because it would require new model calls."))
    atomic_json(output,result)
    return result
