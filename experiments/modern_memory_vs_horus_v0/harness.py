from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import time

from experiments.base_framework_v0.framework import ACTION_ORDER, Prediction
from experiments.map_consequence_only_isolation_v0.protocol import parse as parse_consequence
from experiments.model_map_proposal_v0.adapter import MODEL, parse as parse_joint
from experiments.model_proposal_role_composition_v2.protocol import OPTIONS
from experiments.realized_event_grounding_v0.framework import evidence
from horus.core import BoundPredictionMap, MAPPING, MapForecast, MechanicalExplorer, digest, unwrap_map
from horus.grounded_exploration import GroundedExplorer
from horus.grounded_learning import QwenConsequenceClient
from horus.live import CONSEQUENCE_SYSTEM, JOINT_SYSTEM, LiveController, ModelClient, SessionStore, _plain
from horus.relation_routing import RelationEvidenceStore, relation_routed_clients

from .protocol import G2_ADAPTER, SEED
from .storage import ModernMemory, canonical


def event_head(envelope: dict) -> str:
    return sha256(canonical(envelope).encode()).hexdigest()


def empty_explorer_state() -> dict:
    return dict(attempted_decisions=0, authorized_decisions=0,
        last_probe_decision_sequence=None, last_probe_authorized_decision=None,
        last_execution_by_relation={}, unresolved_contradictions={})


def _request(system: str, prompt: str, model: str) -> dict:
    return dict(model=model, system=system, prompt=prompt, stream=False,
                options={**dict(OPTIONS["Map"]), "seed": SEED, "temperature": 0})


def _history(retrieval) -> list[dict]:
    return [{key: row[key] for key in
             ("epoch", "transaction_id", "surface_action", "next_state", "consequence")}
            for row in retrieval.selected]


def capture(controller: LiveController, store: SessionStore,
            memory: ModernMemory) -> dict:
    core = controller._active.framework.inner
    if core.pending is not None or controller._source.reader().current() is not None:
        raise RuntimeError("cannot capture in-flight protected event")
    state = core.map.current.state
    inputs, transparency = {}, {}
    for action in ACTION_ORDER:
        retrieval = memory.retrieve(f"{state}:{action}")
        alias = next(key for key, value in MAPPING.items() if value == action)
        inputs[action] = dict(state=state, target_action=alias,
                              VERIFIED_CHRONOLOGICAL_HISTORY=_history(retrieval))
        transparency[action] = dict(candidate_memory_count=retrieval.candidate_count,
            raw_eligible_memories=list(retrieval.selected_identities),
            memories_supplied_to_model=list(retrieval.selected_identities),
            retrieval_reasons=list(retrieval.reasons),
            chronological_positions=list(retrieval.chronological_positions),
            selected_consequences=list(retrieval.selected_consequences),
            contradictions_in_candidates=retrieval.contradictions_in_candidates,
            contradictions_included=retrieval.contradictions_included,
            contradictions_excluded=retrieval.contradictions_excluded,
            retrieval_seconds=retrieval.retrieval_seconds)
    return dict(state=state, epoch=core.epoch,
        transaction_id=core.next_transaction_id,
        authenticated_history_reference=store.checkpoint["streams"]["events"],
        memory_sha256=memory.checkpoint()["event_store_sha256"],
        map_inputs=inputs, retrieval=transparency)


def forecast_batch(*, condition: str, store: SessionStore, memory: ModernMemory,
                   controller: LiveController, joint_client: ModelClient,
                   specialists: dict, routing_store: RelationEvidenceStore | None,
                   explorer_state: dict, opportunity: str,
                   perturb: bool = False) -> dict:
    cap = capture(controller, store, memory)
    clients = ("G2",) if condition == "M" else ("G2", "G3")
    work, total_tokens = {}, 0
    # Freeze all complete request bodies before obtaining any response.
    for action in ACTION_ORDER:
        prompt = canonical(cap["map_inputs"][action])
        total_tokens += len(specialists["G2"].tokenizer(
            prompt, add_special_tokens=False).input_ids) * (1 + len(clients))
        joint = _request(JOINT_SYSTEM, prompt, getattr(joint_client, "model_id", MODEL))
        joint_id = f"{opportunity}:{condition}:{action}:J"
        joint_intent = store.append("calls", "REQUEST_INTENT", dict(
            call_id=joint_id, role="joint-next-state", request=joint,
            request_sha256=digest(joint), condition=condition, opportunity=opportunity))
        rows = {}
        for specialist in clients:
            client = specialists[specialist]
            request = _request(CONSEQUENCE_SYSTEM, prompt, client.model_id)
            request["horus_model_identity"] = _plain(client.horus_model_identity)
            call_id = f"{opportunity}:{condition}:{action}:{specialist}"
            intent = store.append("calls", "REQUEST_INTENT", dict(call_id=call_id,
                role=("modern-consequence:G2" if condition == "M" else
                      f"routed-consequence:{specialist}"), request=request,
                request_sha256=digest(request), condition=condition,
                opportunity=opportunity, same_authenticated_context=True,
                model_generation_identity=client.horus_model_identity))
            rows[specialist] = dict(client=client, request=request, intent=intent)
        work[action] = dict(prompt=prompt, joint=joint, joint_intent=joint_intent,
                            specialists=rows)

    started = time.perf_counter()
    all_valid, forecasts, commitments = True, {key: [] for key in clients}, {}
    for action in ACTION_ORDER:
        row = work[action]
        joint_id = row["joint_intent"]["record"]["call_id"]
        response = joint_client.generate(row["joint"])
        injected = perturb and action == "HOLD"
        if injected:
            response = {**response, "pre_fault_response_sha256": digest(response),
                        "raw_output": "REGISTERED_MALFORMED_RESPONSE",
                        "registered_fault": "MALFORMED_JOINT_OUTPUT"}
        response_env = store.append("calls", "RESPONSE", dict(call_id=joint_id,
            response=response, response_sha256=digest(response), fault_injected=injected))
        parsed, failure = None, response.get("transport_error")
        if failure is None:
            try: parsed = parse_joint(response["raw_output"])
            except Exception as exc: failure = type(exc).__name__
        parsed_env = store.append("calls", "PARSED", dict(call_id=joint_id,
            parsed=parsed, parse_error=failure, strict_parser=True))
        commitments[action] = dict(joint=dict(call_id=joint_id,
            request_sequence=row["joint_intent"]["sequence"],
            response_sequence=response_env["sequence"],
            parsed_sequence=parsed_env["sequence"],
            request_sha256=digest(row["joint"])), specialists={})
        for specialist in clients:
            item = row["specialists"][specialist]
            call_id = item["intent"]["record"]["call_id"]
            result = item["client"].generate(item["request"])
            result_env = store.append("calls", "RESPONSE", dict(call_id=call_id,
                response=result, response_sha256=digest(result), fault_injected=False))
            value, error = None, result.get("transport_error")
            if error is None:
                try: value = parse_consequence(result["raw_output"], "C")
                except Exception as exc: error = type(exc).__name__
            value_env = store.append("calls", "PARSED", dict(call_id=call_id,
                parsed=value, parse_error=error, strict_parser=True))
            valid = parsed is not None and value is not None
            all_valid = all_valid and valid
            payload = cap["map_inputs"][action]
            input_context = dict(state=cap["state"], action=action,
                action_alias=payload["target_action"], epoch=cap["epoch"],
                transaction_id=cap["transaction_id"],
                authenticated_history=payload["VERIFIED_CHRONOLOGICAL_HISTORY"],
                memory_sha256=cap["memory_sha256"],
                authenticated_history_reference=cap["authenticated_history_reference"])
            forecasts[specialist].append(MapForecast(action, payload["target_action"],
                None if parsed is None else parsed["next_state"],
                None if value is None else value["consequence"], not valid,
                None if valid else f"INVALID_COMPONENT:J={failure};{specialist}={error}",
                len(payload["VERIFIED_CHRONOLOGICAL_HISTORY"]), input_context))
            commitments[action]["specialists"][specialist] = dict(call_id=call_id,
                request_sequence=item["intent"]["sequence"],
                response_sequence=result_env["sequence"],
                parsed_sequence=value_env["sequence"], request_sha256=digest(item["request"]),
                prediction=None if value is None else value["consequence"],
                artifact_sha256=item["client"].horus_model_identity["artifact_sha256"])
    latency = time.perf_counter() - started
    forecasts = {key: tuple(value) for key, value in forecasts.items()}
    if condition == "M":
        selected_by_action = {action: "G2" for action in ACTION_ORDER}
        routed = forecasts["G2"]
        choice = MechanicalExplorer().choose(routed if all_valid else tuple(
            MapForecast(x.action, x.action_alias, x.next_state, x.consequence, True,
                        "INVALID_MODERN_MAP", x.history_count, x.input_context) for x in routed))
        decision = dict(mode="BASELINE_MECHANICAL", action=choice.action,
                        reason=choice.reason, abstained=choice.abstained)
        previews = None
    else:
        previews = routing_store.preview_state(cap["state"])
        selected_by_action = {action: previews[action]["selected_specialist"]
                              for action in ACTION_ORDER}
        routed = tuple(next(row for row in forecasts[selected_by_action[action]]
                            if row.action == action) for action in ACTION_ORDER)
        public = _public_forecasts(forecasts, selected_by_action)
        decision = GroundedExplorer().derive(pre_state=cap["state"], forecasts=public,
            routed_forecasts=routed, previews=previews,
            routing_records=routing_store.records, confidence_state=explorer_state,
            all_predictions_valid=all_valid)
    return dict(condition=condition, opportunity=opportunity, capture=cap,
        forecasts=forecasts, public_forecasts=_public_forecasts(forecasts, selected_by_action),
        commitments=commitments, selected_by_action=selected_by_action,
        routing_previews=previews, decision=decision, all_valid=all_valid,
        model_calls=3 * (1 + len(clients)), context_tokens=total_tokens,
        model_seconds=latency, perturbation=perturb)


def _public_forecasts(forecasts: dict, selections: dict) -> dict:
    return {action: dict(
        G2_consequence=next(row.consequence for row in forecasts["G2"] if row.action == action),
        G3_consequence=(None if "G3" not in forecasts else next(
            row.consequence for row in forecasts["G3"] if row.action == action)),
        selected_specialist=selections[action],
        routed_consequence=next(row.consequence for row in forecasts[selections[action]]
                                if row.action == action),
        next_state=next(row.next_state for row in forecasts[selections[action]]
                        if row.action == action),
        history_count=next(row.history_count for row in forecasts[selections[action]]
                           if row.action == action),
        valid=not next(row.abstained for row in forecasts[selections[action]]
                       if row.action == action)) for action in ACTION_ORDER}


def update_explorer_state(state: dict, batch: dict, receipt: dict,
                          route: dict) -> None:
    state["attempted_decisions"] += 1
    state["authorized_decisions"] += 1
    relation = route["relation"]
    key = canonical(relation)
    state["last_execution_by_relation"][key] = dict(relation=relation,
        decision_sequence=batch["decision"]["decision_sequence"],
        authorized_decision=state["authorized_decisions"],
        routing_evidence_sequence=route["evidence_sequence"])
    if batch["decision"]["mode"] == "PROBE":
        state["last_probe_decision_sequence"] = batch["decision"]["decision_sequence"]
        state["last_probe_authorized_decision"] = state["authorized_decisions"]


def publish(*, condition: str, stage: str, event_number: int | None,
            controller: LiveController, store: SessionStore, memory: ModernMemory,
            batch: dict, action: str, routing_store: RelationEvidenceStore | None,
            explorer_state: dict) -> dict:
    selected_specialist = batch["selected_by_action"][action]
    selected = next(row for row in batch["forecasts"][selected_specialist]
                    if row.action == action)
    if selected.abstained or not batch["all_valid"]:
        raise RuntimeError("invalid forecast cannot authorize execution")
    prediction = Prediction(batch["capture"]["epoch"], batch["capture"]["transaction_id"],
        batch["capture"]["state"], action, selected.next_state, selected.consequence)
    core = controller._active.framework.inner
    core.map = BoundPredictionMap(unwrap_map(core.map), prediction)
    pending = controller.begin_step(action)
    if getattr(pending, "action", None) != action:
        raise RuntimeError("protected framework rejected selected action")
    if controller._source.reader().current() is not None:
        raise RuntimeError("receipt existed before external execution")
    receipt = controller.execute_pending()
    actual = _plain(asdict(controller._active.world.last_actual))
    result = controller.submit_package(evidence(receipt))
    if not result.committed or not result.continued or result.status.value != "AUTHORIZED":
        controller.release(receipt); raise RuntimeError("protected publication rejected")
    core = controller._active.framework.inner
    package, record = controller._active.framework.packages[-1], core.memory.records[-1]
    if package.receipt is not receipt:
        raise RuntimeError("original protected receipt identity was not retained")
    receipt_value = _plain(asdict(receipt))
    execution_kind = ("ROUTING_CALIBRATION_EXECUTION" if condition == "MH" and
                      stage == "A" else "EXPLORER_SELECTED_EXECUTION" if condition == "MH"
                      else "MODERN_BASELINE_EXECUTION")
    event = dict(session_id=store.checkpoint["session_id"], stage=stage,
        study_event=event_number, execution_kind=execution_kind,
        action_source=("OBSERVATION_CONTROLLED" if stage == "A" else
                       "GROUNDED_EXPLORER" if condition == "MH" else "MECHANICAL_EXPLORER"),
        receipt=receipt_value, receipt_identity=list(receipt.identity()),
        receipt_provenance_sha256=digest(receipt_value),
        authorization_status=result.status.value, authorization_reason=result.reason,
        memory_record=_plain(asdict(record)), source_scope=dict(
            runtime_index=store.checkpoint["runtime_index"], imported_after_restart=False,
            source_identity=receipt.source_identity),
        external_regime_version=controller._active.world.regime_version,
        regime_model_visible=False)
    envelope = store.append("events", "AUTHORIZED_REALIZED_EVENT", event)
    admission = memory.record(store, envelope,
        f"{condition}:{stage}:{event_number or store.checkpoint['completed_steps'] + 1}")
    route = None
    if condition == "MH":
        predictions = {specialist: next(row.consequence for row in rows
            if row.action == action) for specialist, rows in batch["forecasts"].items()}
        route = routing_store.record(store,
            context_hash=digest(selected.input_context), predictions=predictions,
            commitment=batch["commitments"][action], event_envelope=envelope,
            execution_kind=execution_kind,
            per_action_selection=batch["selected_by_action"])
        if stage == "B":
            update_explorer_state(explorer_state, batch, receipt_value, route)
    result_row = dict(condition=condition, stage=stage, event=event_number,
        state=batch["capture"]["state"], action=action,
        prediction=dict(next_state=selected.next_state,
                        consequence=selected.consequence),
        realized=dict(next_state=receipt.next_state,
                      consequence=receipt.realized_consequence),
        consequence_correct=selected.consequence == receipt.realized_consequence,
        exact_correct=(selected.next_state, selected.consequence) ==
                      (receipt.next_state, receipt.realized_consequence),
        selected_specialist=selected_specialist,
        route_decision=batch["selected_by_action"], explorer=batch["decision"],
        raw_eligible_memories=batch["capture"]["retrieval"][action][
            "raw_eligible_memories"], memories_supplied_to_model=batch[
                "capture"]["retrieval"][action]["memories_supplied_to_model"],
        retrieval=batch["capture"]["retrieval"],
        receipt_identity=list(receipt.identity()),
        receipt_provenance_sha256=event["receipt_provenance_sha256"],
        event_stream_sequence=envelope["sequence"], event_stream_head_sha256=event_head(envelope),
        durable_admission=admission, routing_evidence=route,
        model_calls=batch["model_calls"], context_tokens=batch["context_tokens"],
        model_seconds=batch["model_seconds"], status="AUTHORIZED")
    store.append("training", "MODERN_VS_HORUS_SCORED_EVENT", result_row)
    store.save(state=receipt.next_state, next_transaction_id=core.next_transaction_id,
               completed_step=True, attempted_decision=True)
    controller.release(receipt)
    return result_row


def new_controller(store: SessionStore, regime: str) -> LiveController:
    current = store.checkpoint.get("external_regime_version")
    store.configure_regime(regime, allow_transition=current is not None and current != regime)
    epoch, source = store.begin_runtime()
    return LiveController(source, store.checkpoint["current_state"], epoch, regime)


def load_clients(condition: str, registry_root: Path | None = None):
    joint = ModelClient()
    if condition == "M":
        identity = dict(specialist_id="G2", generation=2,
            artifact_sha256=sha256(G2_ADAPTER.read_bytes()).hexdigest(),
            global_lifecycle_status="ACTIVE", routing_eligibility="BASELINE")
        client = QwenConsequenceClient(G2_ADAPTER, device="cuda", model_identity=identity)
        client.model_id = f"modern-G2:{identity['artifact_sha256']}"
        return joint, {"G2": client}, None
    specialists, registry = relation_routed_clients(registry_root, device="cuda")
    return joint, specialists, registry
