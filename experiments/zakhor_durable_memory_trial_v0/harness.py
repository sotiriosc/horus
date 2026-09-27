from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import time
from typing import Any

from experiments.map_consequence_only_isolation_v0.protocol import parse as parse_consequence
from experiments.realized_event_grounding_v0.framework import evidence
from horus.core import digest
from horus.grounded_learning import QwenConsequenceClient, file_hash
from horus.live import CONSEQUENCE_SYSTEM, LiveController, SessionStore, _plain

from .storage import DurableMemory, canonical


ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / "research/learning-stability-v0/registry/generations/generation-0002/model/trained-adapter.safetensors"
RELATION = "1:HOLD"
EVENTS = tuple(
    dict(number=i, phase=("STABLE" if i <= 6 else "CHANGE" if i <= 16 else "RESTORATION"),
         regime=("A" if i <= 6 or i >= 17 else "B"), state=1, action="HOLD",
         consequence=(1 if i <= 6 or i >= 17 else -1))
    for i in range(1, 25)
)
SEGMENTS = ((1, 6, "A"), (7, 12, "B"), (13, 16, "B"), (17, 24, "A"))
RESTART_AFTER = 12
CONDITIONS = ("M", "Z")
CALL_BUDGET = 48


def event_head(envelope: dict) -> str:
    return sha256(canonical(envelope).encode()).hexdigest()


def transport_request(client, prompt: str) -> dict:
    return dict(model=client.model_id, system=CONSEQUENCE_SYSTEM, prompt=prompt,
                stream=False, options=dict(temperature=0, seed=20260926))


def model_history(retrieval) -> list[dict]:
    return [{k: row[k] for k in
             ("epoch", "transaction_id", "surface_action", "next_state", "consequence")}
            for row in retrieval.selected]


def predict(store: SessionStore, memory: DurableMemory,
            client: QwenConsequenceClient, condition: str, event_number: int) -> dict:
    retrieval = (memory.retrieve_modern(RELATION) if condition == "M"
                 else memory.retrieve_zakhor(RELATION))
    prompt_value = dict(state=1, target_action="K2",
                        VERIFIED_CHRONOLOGICAL_HISTORY=model_history(retrieval))
    prompt = canonical(prompt_value)
    request = transport_request(client, prompt)
    call_id = f"event-{event_number:02d}:{condition}"
    token_count = len(client.tokenizer(prompt, add_special_tokens=False).input_ids)
    transparency = dict(candidate_memory_count=retrieval.candidate_count,
        selected_memory_identities=list(retrieval.selected_identities),
        retrieval_reasons=list(retrieval.reasons),
        chronological_positions=list(retrieval.chronological_positions),
        candidate_consequences=list(retrieval.candidate_consequences),
        selected_consequences=list(retrieval.selected_consequences),
        contradictions_in_candidates=retrieval.contradictions_in_candidates,
        contradictions_included=retrieval.contradictions_included,
        contradictions_excluded=retrieval.contradictions_excluded,
        context_tokens=token_count, retrieval_seconds=retrieval.retrieval_seconds,
        zakhor_state=retrieval.zakhor_state)
    store.append("calls", "MEMORY_MODEL_REQUEST", dict(call_id=call_id,
        condition=condition, event_number=event_number, request=request,
        request_sha256=digest(request), retrieval=transparency))
    started = time.perf_counter()
    response = client.generate(request)
    model_seconds = time.perf_counter() - started
    store.append("calls", "MEMORY_MODEL_RESPONSE", dict(call_id=call_id,
        condition=condition, event_number=event_number, response=response,
        response_sha256=digest(response), model_seconds=model_seconds))
    prediction, error = None, None
    try:
        if response["transport_error"] is not None:
            raise RuntimeError(response["transport_error"])
        prediction = parse_consequence(response["raw_output"], "C")["consequence"]
    except Exception as exc:
        error = type(exc).__name__
    store.append("calls", "MEMORY_MODEL_PARSED", dict(call_id=call_id,
        condition=condition, event_number=event_number,
        prediction=prediction, parse_error=error))
    return dict(call_id=call_id, condition=condition, event_number=event_number,
        prediction=prediction, parse_error=error, retrieval=transparency,
        prompt_sha256=digest(prompt_value), context_tokens=token_count,
        retrieval_seconds=retrieval.retrieval_seconds,
        model_seconds=model_seconds)


def publish_event(store: SessionStore, memory: DurableMemory,
                  controller: LiveController, specification: dict,
                  predictions: dict[str, dict]) -> dict:
    pending = controller.begin_step("HOLD")
    if getattr(pending, "action", None) != "HOLD":
        raise RuntimeError("protected framework did not accept forced observation action")
    if controller._source.reader().current() is not None:
        raise RuntimeError("receipt existed before external execution")
    receipt = controller.execute_pending()
    actual = _plain(asdict(controller._active.world.last_actual))
    if actual["consequence"] != specification["consequence"]:
        raise RuntimeError("external schedule/truth mismatch")
    result = controller.submit_package(evidence(receipt))
    if not result.committed or not result.continued or result.status.value != "AUTHORIZED":
        controller.release(receipt)
        raise RuntimeError(f"protected publication rejected: {result.reason}")
    core = controller._active.framework.inner
    package = controller._active.framework.packages[-1]
    record = core.memory.records[-1]
    if package.receipt is not receipt:
        raise RuntimeError("original protected receipt identity was not retained")
    for value, expected in zip(
            (record.epoch, record.transaction_id, record.pre_state, record.action,
             record.next_state, record.consequence), receipt.binding()[:6]):
        if type(value) is not type(expected) or value != expected:
            raise RuntimeError("authorized Memory differs from protected receipt")
    receipt_value = _plain(asdict(receipt))
    event = dict(session_id=store.checkpoint["session_id"],
        receipt=receipt_value, receipt_identity=list(receipt.identity()),
        receipt_provenance_sha256=digest(receipt_value),
        authorization_status=result.status.value,
        authorization_reason=result.reason,
        memory_record=_plain(asdict(record)),
        source_scope=dict(runtime_index=store.checkpoint["runtime_index"],
                          imported_after_restart=False,
                          source_identity=receipt.source_identity),
        external_regime_version=specification["regime"],
        regime_model_visible=False,
        schedule_event=specification["number"], schedule_phase=specification["phase"])
    envelope = store.append("events", "AUTHORIZED_REALIZED_EVENT", event)
    admitted = memory.record(store, envelope,
        f'trial:event-{specification["number"]:02d}:{specification["phase"]}')
    audits = {}
    history = memory.history(RELATION)
    current_start = 1 if specification["phase"] == "STABLE" else 7 if \
        specification["phase"] == "CHANGE" else 17
    relevant_available = {row["event_identity"] for row in history
                          if row["chronological_order"] >= current_start}
    stale_available = {row["event_identity"] for row in history
                       if row["realized_consequence"] != specification["consequence"]}
    for condition, prediction in predictions.items():
        selected = set(prediction["retrieval"]["selected_memory_identities"])
        relevant_selected = len(selected & relevant_available)
        stale_selected = len(selected & stale_available)
        correct = prediction["prediction"] == specification["consequence"]
        audits[condition] = dict(**prediction, realized_consequence=specification["consequence"],
            correct=correct, relevant_available=len(relevant_available),
            relevant_selected=relevant_selected, stale_available=len(stale_available),
            stale_selected=stale_selected,
            error_cause=None if correct else classify_error(prediction,
                relevant_selected, stale_selected, len(relevant_available)))
    scoring = dict(event_number=specification["number"], phase=specification["phase"],
        regime=specification["regime"], receipt_identity=list(receipt.identity()),
        receipt_provenance_sha256=event["receipt_provenance_sha256"],
        event_stream_sequence=envelope["sequence"],
        event_stream_head_sha256=event_head(envelope), durable_admission=admitted,
        conditions=audits)
    store.append("training", "MEMORY_TRIAL_SCORED_EVENT", scoring)
    controller.release(receipt)
    store.save(state=receipt.next_state, next_transaction_id=core.next_transaction_id,
               completed_step=True, attempted_decision=True)
    return scoring


def classify_error(prediction: dict, relevant: int, stale: int,
                   relevant_available: int) -> str:
    retrieval = prediction["retrieval"]
    if relevant_available and relevant == 0:
        return "RELEVANT_MEMORY_NOT_RETRIEVED"
    if retrieval["contradictions_in_candidates"] and retrieval["contradictions_excluded"]:
        return "CONTRADICTORY_MEMORY_LOST"
    if stale > relevant:
        return "STALE_MEMORY_OVERWEIGHTED"
    if relevant > stale:
        return "CORRECT_MEMORY_RETRIEVED_MODEL_WRONG"
    return "RETRIEVAL_AMBIGUOUS"


def _runtime(store: SessionStore, regime: str) -> LiveController:
    epoch, source = store.begin_runtime()
    return LiveController(source, store.checkpoint["current_state"], epoch, regime)


def checkpoint_files(output: Path, store: SessionStore, memory: DurableMemory) -> dict:
    memory_checkpoint = memory.checkpoint()
    files = {}
    for name in ("authority.key", "checkpoint.json", "events.jsonl",
                 "model-calls.private.jsonl", "training-records.jsonl"):
        path = output / "protected-session" / name
        files[name] = file_hash(path)
    return dict(memory=memory_checkpoint, protected_files_sha256=files,
                protected_event_count=len(store.records["events"]),
                call_record_count=len(store.records["calls"]),
                scoring_record_count=len(store.records["training"]))


def run_segment(output: Path, start: int, stop: int, initialize: bool) -> dict:
    session_path = output / "protected-session"
    database_path = output / "memory.sqlite3"
    with SessionStore(session_path, not initialize) as store, \
            DurableMemory(database_path, initialize) as memory:
        restore_verification = None
        if not initialize:
            reconciliation = memory.reconcile(store)
            observed = checkpoint_files(output, store, memory)
            expected = json.loads((output / "before-restart.json").read_text())["checkpoint"]
            restore_verification = dict(reconciliation=reconciliation,
                expected=expected, observed=observed, exact_hash_match=observed == expected)
            if observed != expected:
                raise RuntimeError("fresh-process restore differs from pre-restart checkpoint")
        client = QwenConsequenceClient(ADAPTER, device="cuda",
            model_identity=dict(component="COMMON_G2", artifact_sha256=file_hash(ADAPTER)))
        controller = None
        rows = []
        for specification in EVENTS[start - 1:stop]:
            number, regime = specification["number"], specification["regime"]
            if controller is None or number in (7, 13, 17):
                if number == 1:
                    store.configure_regime(regime)
                elif store.checkpoint.get("external_regime_version") != regime:
                    store.configure_regime(regime, allow_transition=True)
                controller = _runtime(store, regime)
            order = CONDITIONS if number % 2 else tuple(reversed(CONDITIONS))
            predictions = {condition: predict(store, memory, client, condition, number)
                           for condition in order}
            rows.append(publish_event(store, memory, controller, specification, predictions))
            print(f"event={number}/24 calls={2*number}/48 phase={specification['phase']}",
                  flush=True)
        checkpoint = checkpoint_files(output, store, memory)
        result = dict(start=start, stop=stop, calls=2 * len(rows),
            rows=len(rows), checkpoint=checkpoint,
            model_artifact_sha256=file_hash(ADAPTER),
            restore_verification=restore_verification,
            first_post_restart=(None if initialize or not rows else dict(
                event_number=rows[0]["event_number"],
                receipt_identity=rows[0]["receipt_identity"],
                conditions={name: dict(prediction=rows[0]["conditions"][name]["prediction"],
                    correct=rows[0]["conditions"][name]["correct"],
                    selected_memory_identities=rows[0]["conditions"][name][
                        "retrieval"]["selected_memory_identities"])
                    for name in CONDITIONS})))
        name = "before-restart.json" if stop == RESTART_AFTER else "after-restart.json"
        (output / name).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        return result
