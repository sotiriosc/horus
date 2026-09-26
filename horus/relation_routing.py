"""Authenticated per-(pre_state, action) routing across retained specialists."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from dataclasses import asdict
from datetime import datetime
import fcntl
from hashlib import sha256
from hmac import compare_digest, new as new_hmac
import json
import os
from pathlib import Path
import secrets
import shutil
from typing import Any

from experiments.base_framework_v0.framework import ACTION_ORDER, Prediction
from experiments.model_map_proposal_v0.adapter import MODEL
from experiments.realized_event_grounding_v0.framework import evidence

from .core import BoundPredictionMap, MechanicalExplorer, digest, unwrap_map
from .grounded_learning import (QwenConsequenceClient, ROOT, atomic_json,
                                file_hash)
from .live import (DurableHistoryReader, LiveController, ModelClient,
                   SessionStore, _canonical, _now, _plain)
from .model_registry import load_registry
from .routing import (GroundedRouter, RoutedForecastBatch, RoutedSplitMap,
                      RoutingError, replace_forecast_invalid)


POLICY_PATH = Path(__file__).with_name("relation_routing_policy.json")
GLOBAL_POLICY_PATH = Path(__file__).with_name("routing_policy.json")
DEFAULT_SOURCE_REGISTRY = ROOT / "research/learning-stability-v0/registry"
ROUTING_VERSION = 2
SPECIALISTS = ("G2", "G3")
SEGMENTS = ("A1", "B1", "B2", "A2")


def _document(payload: dict) -> dict:
    return {"payload": payload, "sha256": digest(payload)}


def _read_document(path: Path, label: str) -> dict:
    try:
        document = json.loads(path.read_text())
        payload = document["payload"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise RoutingError(f"invalid {label}") from exc
    if digest(payload) != document.get("sha256"):
        raise RoutingError(f"{label} hash mismatch")
    return document


def _inside(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise RoutingError("routing path escapes registry") from exc
    return path


def _copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def relation_identity(pre_state: int, action: str) -> dict:
    if type(pre_state) is not int or pre_state not in range(4) or action not in ACTION_ORDER:
        raise RoutingError("invalid relation identity")
    value = {"pre_state": pre_state, "action": action}
    return {**value, "identity_sha256": digest(value)}


def relation_key(relation: dict) -> str:
    expected = relation_identity(relation.get("pre_state"), relation.get("action"))
    if relation != expected:
        raise RoutingError("relation identity hash mismatch")
    return f"{relation['pre_state']}:{relation['action']}"


def initialize_relation_routing_registry(
        root: Path, source_registry: Path = DEFAULT_SOURCE_REGISTRY) -> dict:
    root = root.resolve()
    if root.exists():
        raise RoutingError("routing registry already exists")
    source = load_registry(source_registry)
    entries = {row["generation"]: row for row in source["entries"]}
    policy = json.loads(POLICY_PATH.read_text())
    if set(entries) < {2, 3} or entries[2]["status"] != "ACTIVE" or \
            entries[3]["status"] != "REJECTED":
        raise RoutingError("source lifecycle does not preserve ACTIVE G2 / REJECTED G3")
    root.mkdir(parents=True)
    specialists = []
    for expected in policy["specialists"]:
        generation = expected["generation"]
        entry, manifest = entries[generation], source["manifests"][generation]
        if entry["artifact_sha256"] != expected["artifact_sha256"]:
            raise RoutingError("specialist artifact does not match frozen policy")
        adapter_source = source["root"] / manifest["adapter_path"]
        lineage_relative = manifest.get("lineage_artifact")
        if lineage_relative is None:
            raise RoutingError("specialist lineage is missing")
        destination = root / f"specialists/generation-{generation:04d}"
        adapter_relative = str((destination / "adapter.safetensors").relative_to(root))
        lineage_copy_relative = str((destination / "learning-lineage.json").relative_to(root))
        manifest_copy_relative = str((destination / "source-generation.json").relative_to(root))
        _copy(adapter_source, root / adapter_relative)
        _copy(source["root"] / lineage_relative, root / lineage_copy_relative)
        _copy(source["root"] / entry["manifest"], root / manifest_copy_relative)
        specialists.append(dict(id=expected["id"], generation=generation,
            artifact_sha256=entry["artifact_sha256"], adapter_path=adapter_relative,
            base_model_identity=manifest["base_model_identity"],
            parent_generation=manifest["parent_generation"],
            lineage_path=lineage_copy_relative,
            lineage_sha256=file_hash(root / lineage_copy_relative),
            source_generation_manifest=manifest_copy_relative,
            source_generation_manifest_sha256=file_hash(root / manifest_copy_relative),
            source_registry_manifest_sha256=entry["manifest_sha256"],
            global_lifecycle_status=entry["status"],
            routing_eligibility="ROUTABLE_SPECIALIST"))
    payload = dict(version=ROUTING_VERSION, routing_mode="RELATION_GROUNDED",
        created_at=_now(), relation_identity=policy["relation_identity"],
        source_registry_state_sha256=source["state_document"]["sha256"],
        global_active_generation=2, default_specialist=policy["cold_start_specialist"],
        routing_policy_sha256=file_hash(POLICY_PATH), specialists=specialists,
        lifecycle_status_rewritten=False, weights_modified=False,
        generation_3r_included=False)
    atomic_json(root / "routing-registry.json", _document(payload))
    RelationEvidenceStore.initialize(root)
    return dict(root=str(root), registry_sha256=digest(payload),
                source_registry_state_sha256=payload["source_registry_state_sha256"],
                specialists=specialists)


def load_relation_routing_registry(root: Path) -> dict:
    root = root.resolve()
    document = _read_document(root / "routing-registry.json", "routing registry")
    payload = document["payload"]
    policy = json.loads(POLICY_PATH.read_text())
    if payload.get("version") != ROUTING_VERSION or \
            payload.get("routing_mode") != "RELATION_GROUNDED" or \
            payload.get("relation_identity") != ["pre_state", "action"] or \
            payload.get("routing_policy_sha256") != file_hash(POLICY_PATH):
        raise RoutingError("relation routing policy identity mismatch")
    rows = payload.get("specialists")
    if not isinstance(rows, list) or [row.get("id") for row in rows] != list(SPECIALISTS):
        raise RoutingError("routing pool must contain exactly G2 and G3")
    expected = {row["id"]: row for row in policy["specialists"]}
    by_id = {}
    for row in rows:
        if row.get("generation") != expected[row["id"]]["generation"] or \
                row.get("artifact_sha256") != expected[row["id"]]["artifact_sha256"]:
            raise RoutingError("specialist identity differs from frozen policy")
        required_status = "ACTIVE" if row["id"] == "G2" else "REJECTED"
        if row.get("global_lifecycle_status") != required_status or \
                row.get("routing_eligibility") != "ROUTABLE_SPECIALIST":
            raise RoutingError("routing eligibility rewrote lifecycle status")
        for path_key, hash_key in (("adapter_path", "artifact_sha256"),
                                   ("lineage_path", "lineage_sha256"),
                                   ("source_generation_manifest",
                                    "source_generation_manifest_sha256")):
            path = _inside(root, row[path_key])
            if not path.is_file() or file_hash(path) != row[hash_key]:
                raise RoutingError(f"specialist {path_key} hash mismatch")
        by_id[row["id"]] = row
    if payload.get("global_active_generation") != 2 or \
            payload.get("lifecycle_status_rewritten") is not False or \
            payload.get("weights_modified") is not False or \
            payload.get("generation_3r_included") is not False:
        raise RoutingError("routing registry violates frozen lifecycle")
    return dict(root=root, document=document, payload=payload,
                specialists=by_id, policy=policy)


class RelationGroundedRouter:
    """Pure local fixed-window score and hysteresis rule."""
    def __init__(self, policy: dict | None = None):
        self.policy = policy or json.loads(POLICY_PATH.read_text())

    @staticmethod
    def local_rows(rows: list[dict], relation: dict) -> list[dict]:
        key = relation_key(relation)
        return [row for row in rows if relation_key(row["relation"]) == key]

    def scores(self, rows: list[dict], relation: dict) -> dict:
        window = self.local_rows(rows, relation)[-self.policy["window_size"]:]
        return {specialist: {"correct": sum(
                    bool(row["correctness"][specialist]) for row in window),
                "total": len(window)} for specialist in SPECIALISTS}

    def update(self, rows: list[dict], relation: dict, selected: str) -> dict:
        scores = self.scores(rows, relation)
        challenger = "G3" if selected == "G2" else "G2"
        eligible = scores[selected]["total"] >= self.policy[
            "minimum_shared_scored_events"]
        lead = scores[challenger]["correct"] - scores[selected]["correct"]
        switched = eligible and lead >= self.policy["switch_lead_correct"]
        after = challenger if switched else selected
        reason = (f"{challenger} local grounded lead "
                  f"{scores[challenger]['correct']}/{scores[challenger]['total']} vs "
                  f"{scores[selected]['correct']}/{scores[selected]['total']}" if switched
                  else "local incumbent retained: minimum evidence/lead not satisfied")
        return dict(selected_before=selected, selected_after=after, scores=scores,
                    challenger=challenger, challenger_lead=lead,
                    minimum_evidence_satisfied=eligible, switched=switched,
                    reason=reason)


class RelationEvidenceStore:
    """HMAC-chained receipt evidence with independent state per relation."""
    KEY = "routing-authority.key"
    STATE = "router-state.json"
    STREAM = "routing-evidence.jsonl"

    @staticmethod
    def initialize(root: Path) -> None:
        root = root.resolve()
        for name in (RelationEvidenceStore.KEY, RelationEvidenceStore.STATE,
                     RelationEvidenceStore.STREAM):
            if (root / name).exists():
                raise RoutingError("routing evidence store already exists")
        key = secrets.token_bytes(32)
        descriptor = os.open(root / RelationEvidenceStore.KEY,
                             os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            os.write(descriptor, (key.hex() + "\n").encode()); os.fsync(descriptor)
        finally:
            os.close(descriptor)
        (root / RelationEvidenceStore.STREAM).touch(mode=0o600)
        state = dict(version=ROUTING_VERSION, relation_identity=["pre_state", "action"],
            evidence_count=0, evidence_head_sha256=None, session_id=None,
            relations={}, updated_at=_now())
        RelationEvidenceStore._write_state_file(root, key, state)

    @staticmethod
    def _write_state_file(root: Path, key: bytes, state: dict) -> None:
        document = {"payload": state, "hmac_sha256": new_hmac(
            key, _canonical(state).encode(), "sha256").hexdigest()}
        temporary = root / (RelationEvidenceStore.STATE + ".tmp")
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            os.write(descriptor, (json.dumps(document, indent=2, sort_keys=True) +
                                  "\n").encode()); os.fsync(descriptor)
        finally:
            os.close(descriptor)
        os.replace(temporary, root / RelationEvidenceStore.STATE)

    def __init__(self, root: Path):
        self.registry = load_relation_routing_registry(root)
        self.root = self.registry["root"]
        self._lock = (self.root / ".routing.lock").open("a+")
        try:
            fcntl.flock(self._lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RoutingError("routing registry is already open") from exc
        try:
            self._key = bytes.fromhex((self.root / self.KEY).read_text().strip())
        except (OSError, ValueError) as exc:
            self.close(); raise RoutingError("invalid routing authority key") from exc
        if len(self._key) != 32:
            self.close(); raise RoutingError("invalid routing authority key")
        try:
            self.state = self._read_state()
            self.records = self._read_stream()
            self.router = RelationGroundedRouter(self.registry["policy"])
            self._validate_replay()
        except Exception:
            self.close(); raise

    def close(self) -> None:
        if hasattr(self, "_lock") and not self._lock.closed:
            fcntl.flock(self._lock, fcntl.LOCK_UN); self._lock.close()

    def __enter__(self): return self
    def __exit__(self, *_): self.close()

    def _mac(self, value: Any) -> str:
        return new_hmac(self._key, _canonical(value).encode(), "sha256").hexdigest()

    def _read_state(self) -> dict:
        try:
            document = json.loads((self.root / self.STATE).read_text())
            payload = document["payload"]
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise RoutingError("invalid router state") from exc
        if not compare_digest(self._mac(payload), document.get("hmac_sha256", "")):
            raise RoutingError("router state authentication failed")
        return payload

    def _write_state(self) -> None:
        self.state["updated_at"] = _now()
        self._write_state_file(self.root, self._key, self.state)

    def _read_stream(self) -> list[dict]:
        rows, previous = [], None
        try:
            lines = (self.root / self.STREAM).read_text().splitlines()
        except OSError as exc:
            raise RoutingError("missing routing evidence stream") from exc
        for index, line in enumerate(lines, 1):
            try:
                envelope = json.loads(line)
                signed = {key: envelope[key] for key in
                          ("sequence", "previous_sha256", "kind", "record")}
            except (ValueError, KeyError, TypeError) as exc:
                raise RoutingError("invalid routing evidence record") from exc
            if envelope["sequence"] != index or envelope["previous_sha256"] != previous:
                raise RoutingError("broken routing evidence hash chain")
            if not compare_digest(self._mac(signed), envelope.get("hmac_sha256", "")):
                raise RoutingError("routing evidence authentication failed")
            previous = sha256(_canonical(envelope).encode()).hexdigest()
            rows.append(envelope)
        return rows

    @staticmethod
    def _relation_state(relation: dict, selected: str, count: int,
                        last_sequence: int) -> dict:
        return dict(relation=relation, selected_specialist=selected,
                    evidence_count=count, last_evidence_sequence=last_sequence)

    def _validate_replay(self) -> None:
        selected, counts, replay = {}, Counter(), []
        previous = None
        for index, envelope in enumerate(self.records, 1):
            row, relation = envelope["record"], envelope["record"].get("relation")
            key = relation_key(relation)
            before_selected = selected.get(key, "G2")
            if row.get("evidence_sequence") != index or \
                    row.get("selected_specialist") != before_selected or \
                    set(row.get("correctness", {})) != set(SPECIALISTS):
                raise RoutingError("relation routing evidence state mismatch")
            before = self.router.scores(replay, relation)
            if row.get("router_score_before") != before:
                raise RoutingError("relation router before-score mismatch")
            replay.append(row); counts[key] += 1
            result = self.router.update(replay, relation, before_selected)
            if row.get("router_score_after") != result["scores"] or \
                    row.get("switch_occurred") != result["switched"] or \
                    row.get("selected_specialist_after") != result["selected_after"] or \
                    row.get("switch_reason") != result["reason"]:
                raise RoutingError("relation router transition does not replay")
            selected[key] = result["selected_after"]
            previous = sha256(_canonical(envelope).encode()).hexdigest()
        expected_relations = {}
        for key, specialist in selected.items():
            latest = next(row["record"] for row in reversed(self.records)
                          if relation_key(row["record"]["relation"]) == key)
            expected_relations[key] = self._relation_state(
                latest["relation"], specialist, counts[key], latest["evidence_sequence"])
        if self.state.get("version") != ROUTING_VERSION or \
                self.state.get("relation_identity") != ["pre_state", "action"] or \
                self.state.get("evidence_count") != len(self.records) or \
                self.state.get("evidence_head_sha256") != previous or \
                self.state.get("relations") != expected_relations:
            raise RoutingError("relation router checkpoint/evidence mismatch")

    def preview(self, pre_state: int, action: str) -> dict:
        relation = relation_identity(pre_state, action); key = relation_key(relation)
        rows = [row["record"] for row in self.records]
        state = self.state["relations"].get(key)
        return dict(relation=relation,
            selected_specialist=("G2" if state is None else state["selected_specialist"]),
            scores=self.router.scores(rows, relation),
            relation_evidence_count=(0 if state is None else state["evidence_count"]),
            total_evidence_count=len(rows))

    def preview_state(self, pre_state: int) -> dict:
        return {action: self.preview(pre_state, action) for action in ACTION_ORDER}

    @staticmethod
    def _time(value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    def _validate_commitment(self, store: SessionStore, commitment: dict,
                             event_record: dict) -> None:
        by_sequence = {row["sequence"]: row for row in store.records["calls"]}
        event_time = self._time(event_record["recorded_at"])
        for specialist in SPECIALISTS:
            value = commitment["specialists"][specialist]
            intent = by_sequence.get(value["request_sequence"])
            response = by_sequence.get(value["response_sequence"])
            parsed = by_sequence.get(value["parsed_sequence"])
            if not intent or not response or not parsed or \
                    intent["kind"] != "REQUEST_INTENT" or \
                    response["kind"] != "RESPONSE" or parsed["kind"] != "PARSED":
                raise RoutingError("specialist prediction was not durably frozen")
            call_id = value["call_id"]
            if any(row["record"].get("call_id") != call_id
                   for row in (intent, response, parsed)):
                raise RoutingError("specialist commitment call identity mismatch")
            request = intent["record"]
            if request.get("role") != f"routed-consequence:{specialist}" or \
                    request.get("request_sha256") != value["request_sha256"] or \
                    request.get("model_generation_identity", {}).get(
                        "artifact_sha256") != self.registry["specialists"][specialist][
                            "artifact_sha256"]:
                raise RoutingError("specialist commitment identity mismatch")
            if parsed["record"].get("parsed", {}).get("consequence") != value["prediction"]:
                raise RoutingError("specialist frozen value mismatch")
            if any(self._time(row["record"]["recorded_at"]) >= event_time
                   for row in (intent, response, parsed)):
                raise RoutingError("shadow response arrived after execution")
            serialized = json.dumps(request["request"], sort_keys=True).lower()
            if "regime" in serialized or "selected_specialist" in serialized or \
                    "predicted_next_state" in serialized:
                raise RoutingError("hidden or correlated input entered specialist request")

    def bind_session(self, store: SessionStore, allow_pending_event: bool = False) -> None:
        session_id = store.checkpoint["session_id"]
        if self.state.get("session_id") is None:
            if self.records or store.records["events"]:
                raise RoutingError("cannot bind nonempty routing/session history")
            self.state["session_id"] = session_id; self._write_state()
        elif self.state["session_id"] != session_id:
            raise RoutingError("routing evidence belongs to another session")
        expected_events = len(self.records) + int(allow_pending_event)
        if len(store.records["events"]) != expected_events:
            raise RoutingError("receipt/routing evidence count mismatch")
        for event, envelope in zip(store.records["events"][:len(self.records)], self.records):
            row, actual = envelope["record"], event["record"]
            receipt = actual["receipt"]
            expected_relation = relation_identity(receipt["pre_state"], receipt["action"])
            if row["relation"] != expected_relation or \
                    row["receipt_identity"] != actual["receipt_identity"] or \
                    row["receipt_provenance_sha256"] != actual[
                        "receipt_provenance_sha256"] or \
                    row["realized_consequence"] != receipt["realized_consequence"] or \
                    actual["authorization_status"] != "AUTHORIZED":
                raise RoutingError("routing evidence receipt mismatch")
            self._validate_commitment(store, row["prediction_commitment"], actual)

    def record(self, store: SessionStore, *, context_hash: str,
               predictions: dict[str, int], commitment: dict,
               event_envelope: dict, execution_kind: str,
               per_action_selection: dict[str, str]) -> dict:
        self.bind_session(store, allow_pending_event=True)
        if event_envelope is not store.records["events"][-1] or \
                len(store.records["events"]) != len(self.records) + 1:
            raise RoutingError("receipt was not the next authenticated routing event")
        event = event_envelope["record"]
        if event.get("execution_kind") != execution_kind or execution_kind not in (
                "ROUTING_CALIBRATION_EXECUTION", "EXPLORER_SELECTED_EXECUTION"):
            raise RoutingError("invalid execution-kind provenance")
        self._validate_commitment(store, commitment, event)
        receipt = event["receipt"]
        relation = relation_identity(receipt["pre_state"], receipt["action"])
        before = self.preview(receipt["pre_state"], receipt["action"])
        if per_action_selection.get(receipt["action"]) != before["selected_specialist"]:
            raise RoutingError("executed relation specialist was not frozen before execution")
        if set(predictions) != set(SPECIALISTS) or any(
                type(value) is not int or value not in (-1, 0, 1)
                for value in predictions.values()):
            raise RoutingError("invalid specialist prediction set")
        realized = receipt["realized_consequence"]
        correctness = {key: value == realized for key, value in predictions.items()}
        record = dict(evidence_sequence=len(self.records) + 1, relation=relation,
            context_input_sha256=context_hash,
            specialists={key: dict(generation=self.registry["specialists"][key][
                "generation"], artifact_sha256=self.registry["specialists"][key][
                    "artifact_sha256"], frozen_consequence=predictions[key])
                for key in SPECIALISTS},
            selected_specialist=before["selected_specialist"],
            per_action_selection_before=deepcopy(per_action_selection),
            execution_kind=execution_kind,
            realized_consequence=realized, correctness=correctness,
            receipt_identity=event["receipt_identity"],
            receipt_provenance_sha256=event["receipt_provenance_sha256"],
            receipt_event_sequence=event_envelope["sequence"],
            router_score_before=before["scores"],
            prediction_commitment=deepcopy(commitment),
            predictions_frozen_before_execution=True,
            evidence_source="AUTHORIZED_ORIGINAL_RECEIPT", recorded_at=_now())
        prospective = [row["record"] for row in self.records] + [record]
        transition = self.router.update(prospective, relation,
                                        before["selected_specialist"])
        record.update(router_score_after=transition["scores"],
            switch_occurred=transition["switched"],
            selected_specialist_after=transition["selected_after"],
            switch_reason=transition["reason"])
        previous = None if not self.records else sha256(
            _canonical(self.records[-1]).encode()).hexdigest()
        signed = dict(sequence=len(self.records) + 1, previous_sha256=previous,
            kind="AUTHORIZED_RECEIPT_SCORED_RELATION_SPECIALISTS", record=record)
        envelope = {**signed, "hmac_sha256": self._mac(signed)}
        with (self.root / self.STREAM).open("a") as stream:
            stream.write(_canonical(envelope) + "\n"); stream.flush(); os.fsync(stream.fileno())
        self.records.append(envelope)
        key = relation_key(relation)
        local_count = before["relation_evidence_count"] + 1
        self.state["relations"][key] = self._relation_state(
            relation, transition["selected_after"], local_count, len(self.records))
        self.state.update(evidence_count=len(self.records),
            evidence_head_sha256=sha256(_canonical(envelope).encode()).hexdigest())
        self._write_state()
        return _plain(record)


def relation_routed_clients(registry_root: Path,
                            device: str | None = None) -> tuple[dict, dict]:
    registry = load_relation_routing_registry(registry_root)
    clients = {}
    for specialist in SPECIALISTS:
        row = registry["specialists"][specialist]
        identity = dict(specialist_id=specialist, generation=row["generation"],
            parent_generation=row["parent_generation"],
            base_model_identity=row["base_model_identity"],
            artifact_sha256=row["artifact_sha256"],
            adapter_identity=f"generation-{row['generation']}:{row['artifact_sha256']}",
            global_lifecycle_status=row["global_lifecycle_status"],
            routing_eligibility=row["routing_eligibility"])
        client = QwenConsequenceClient(_inside(registry["root"], row["adapter_path"]),
                                       device=device, model_identity=identity)
        client.model_id = f"horus-relation-routed-{specialist}:{row['artifact_sha256']}"
        clients[specialist] = client
    return clients, registry


class RelationRoutedRuntime:
    def __init__(self, store: SessionStore, joint_client: ModelClient,
                 specialists: dict, registry: dict,
                 routing_store: RelationEvidenceStore, regime_version: str):
        self.store, self.joint_client = store, joint_client
        self.specialists, self.registry = specialists, registry
        self.routing_store = routing_store
        routing_store.bind_session(store)
        epoch, source = store.begin_runtime()
        self.controller = LiveController(source, store.checkpoint["current_state"], epoch,
                                         regime_version)
        self.regime_version = regime_version
        self.authentic, self.executions = {}, {}
        self.reader = DurableHistoryReader(self.controller, store,
                                           self.authentic, self.executions)
        self.map = RoutedSplitMap(store, joint_client, specialists, registry)
        self.explorer = MechanicalExplorer()

    def _next_batch(self) -> tuple[dict, RoutedForecastBatch, int, str]:
        capture = self.reader.capture()
        request_count = sum(row["kind"] == "REQUEST_INTENT"
                            for row in self.store.records["calls"])
        if request_count % 9:
            raise RoutingError("incomplete prior prediction batch")
        batch_sequence = request_count // 9 + 1
        decision_id = (f"{self.store.checkpoint['session_id']}:"
                       f"e{capture['epoch']}:b{batch_sequence}")
        return capture, self.map.forecasts(capture, decision_id), batch_sequence, decision_id

    def _route_batch(self, capture: dict, batch: RoutedForecastBatch) -> tuple[dict, dict, dict]:
        previews = self.routing_store.preview_state(capture["state"])
        selections = {action: previews[action]["selected_specialist"]
                      for action in ACTION_ORDER}
        routed = tuple(next(row for row in batch.forecasts[selections[action]]
                            if row.action == action) for action in ACTION_ORDER)
        choice_rows = {}
        for name, forecasts in (("G2", batch.forecasts["G2"]),
                                ("G3", batch.forecasts["G3"]),
                                ("relation_routed", routed)):
            values = forecasts if batch.all_valid else tuple(
                replace_forecast_invalid(forecasts))
            choice_rows[name] = asdict(self.explorer.choose(values))
        return previews, selections, {"routed_forecasts": routed, "choices": choice_rows}

    @staticmethod
    def _public_forecasts(batch: RoutedForecastBatch, selections: dict) -> dict:
        by_specialist = {key: {row.action: row for row in values}
                         for key, values in batch.forecasts.items()}
        return {action: dict(
            G2_consequence=by_specialist["G2"][action].consequence,
            G3_consequence=by_specialist["G3"][action].consequence,
            selected_specialist=selections[action],
            routed_consequence=by_specialist[selections[action]][action].consequence,
            next_state=by_specialist[selections[action]][action].next_state,
            action_alias=by_specialist[selections[action]][action].action_alias,
            history_count=by_specialist[selections[action]][action].history_count,
            valid=not by_specialist[selections[action]][action].abstained)
            for action in ACTION_ORDER}

    def comparison(self) -> dict:
        capture, batch, batch_sequence, decision_id = self._next_batch()
        previews, selections, routed = self._route_batch(capture, batch)
        record = dict(prediction_batch_sequence=batch_sequence,
            decision_id=decision_id, execution_kind="COMPARISON_ONLY_NO_EXECUTION",
            pre_state=capture["state"], relation_selections_before=selections,
            relation_previews=previews, choices=routed["choices"],
            forecasts=self._public_forecasts(batch, selections),
            all_predictions_valid=batch.all_valid,
            actual_execution=False, receipt_identity=None,
            external_regime_version=self.regime_version,
            regime_model_visible=False, model_calls=9)
        self.store.append("training", "RELATION_ROUTING_COMPARISON_ONLY", record)
        self.store.save(state=capture["state"],
                        next_transaction_id=capture["transaction_id"])
        return _plain(record)

    def execute(self, execution_kind: str) -> dict:
        if execution_kind not in ("ROUTING_CALIBRATION_EXECUTION",
                                  "EXPLORER_SELECTED_EXECUTION"):
            raise RoutingError("unsupported execution kind")
        capture, batch, batch_sequence, decision_id = self._next_batch()
        previews, selections, routed = self._route_batch(capture, batch)
        public_forecasts = self._public_forecasts(batch, selections)
        if execution_kind == "ROUTING_CALIBRATION_EXECUTION":
            if capture["state"] != 1:
                raise RoutingError("calibration requires authenticated state 1")
            selected_action = "HOLD"
            action_source = "REGISTERED_FORCED_RELATION_PROBE"
        else:
            choice = routed["choices"]["relation_routed"]
            selected_action = choice["action"]
            action_source = "MECHANICAL_EXPLORER"
        if not batch.all_valid or selected_action is None:
            self.store.save(state=capture["state"],
                next_transaction_id=capture["transaction_id"], attempted_decision=True)
            return dict(prediction_batch_sequence=batch_sequence,
                decision_id=decision_id, execution_kind=execution_kind,
                action_source=action_source, status="ABSTAINED",
                state=capture["state"], relation_previews=previews,
                relation_selections_before=selections,
                forecasts=public_forecasts, choices=routed["choices"],
                model_calls=9, routing_evidence=None)
        selected_specialist = selections[selected_action]
        selected = next(row for row in batch.forecasts[selected_specialist]
                        if row.action == selected_action)
        specialist_predictions = {key: next(row.consequence for row in forecasts
            if row.action == selected_action) for key, forecasts in batch.forecasts.items()}
        commitment = batch.commitments[selected_action]
        prediction = Prediction(capture["epoch"], capture["transaction_id"],
            capture["state"], selected.action, selected.next_state, selected.consequence)
        core = self.controller._active.framework.inner
        core.map = BoundPredictionMap(unwrap_map(core.map), prediction)
        pending = self.controller.begin_step(selected.action)
        if _plain(asdict(pending.prediction)) != _plain(asdict(prediction)):
            raise RoutingError("relation-routed prediction was not latched")
        if self.controller._source.reader().current() is not None:
            raise RoutingError("receipt existed before relation-routed execution")
        receipt = self.controller.execute_pending()
        actual = _plain(asdict(self.controller._active.world.last_actual))
        self.authentic[receipt.identity()] = receipt
        self.executions[receipt.identity()] = actual
        result = self.controller.submit_package(evidence(receipt))
        if not result.committed or not result.continued:
            self.controller.release(receipt)
            raise RoutingError(f"grounded relation-routed publication rejected: {result.reason}")
        core = self.controller._active.framework.inner
        memory_record = core.memory.records[-1]
        package = self.controller._active.framework.packages[-1]
        if package.receipt is not receipt:
            raise RoutingError("relation-routed receipt object was substituted")
        receipt_value, memory_value = _plain(asdict(receipt)), _plain(asdict(memory_record))
        event = dict(session_id=self.store.checkpoint["session_id"],
            recorded_at=_now(), prediction_batch_sequence=batch_sequence,
            execution_kind=execution_kind, action_source=action_source,
            receipt=receipt_value, receipt_identity=list(receipt.identity()),
            receipt_provenance_sha256=digest(receipt_value),
            authorization_status=result.status.value, memory_record=memory_value,
            source_scope=dict(runtime_index=self.store.checkpoint["runtime_index"],
                              imported_after_restart=False,
                              source_identity=receipt.source_identity),
            external_regime_version=self.regime_version, regime_model_visible=False)
        event_envelope = self.store.append("events", "AUTHORIZED_REALIZED_EVENT", event)
        event_head = sha256(_canonical(event_envelope).encode()).hexdigest()
        training = dict(session_id=self.store.checkpoint["session_id"],
            epoch=receipt.epoch, transaction_id=receipt.transaction_id,
            pre_state=capture["state"],
            prediction_batch_sequence=batch_sequence, decision_id=decision_id,
            order=self.store.checkpoint["completed_steps"] + 1,
            timestamp=event["recorded_at"], execution_kind=execution_kind,
            action_source=action_source,
            input_context_hash=digest(selected.input_context),
            authenticated_history_reference=capture["authenticated_history_reference"],
            chosen_action=selected.action, predicted_next_state=selected.next_state,
            predicted_consequence=selected.consequence,
            selected_specialist_for_executed_relation=selected_specialist,
            relation_selections_before=selections,
            choices=routed["choices"], forecasts=public_forecasts,
            specialist_predictions=specialist_predictions,
            routing_registry_sha256=self.registry["document"]["sha256"],
            realized_next_state=receipt.next_state,
            realized_consequence=receipt.realized_consequence,
            prediction_match=dict(next_state=selected.next_state == receipt.next_state,
                consequence=selected.consequence == receipt.realized_consequence,
                exact=(selected.next_state, selected.consequence) ==
                      (receipt.next_state, receipt.realized_consequence)),
            receipt_identity=list(receipt.identity()),
            receipt_provenance_sha256=event["receipt_provenance_sha256"],
            authorization_status=result.status.value,
            memory_reference=dict(event_sequence=event_envelope["sequence"],
                                  event_head_sha256=event_head),
            labels=dict(predictions_are_authenticated_targets=False,
                        realized_receipt_is_authenticated_target=True,
                        calibration_is_explorer_choice=(
                            execution_kind == "EXPLORER_SELECTED_EXECUTION")),
            external_regime_version=self.regime_version, regime_model_visible=False)
        self.store.append("training", "AUTHORIZED_RELATION_ROUTING_RECORD", training)
        self.store.save(state=receipt.next_state,
            next_transaction_id=core.next_transaction_id,
            completed_step=True, attempted_decision=True)
        route = self.routing_store.record(self.store,
            context_hash=digest(selected.input_context),
            predictions=specialist_predictions, commitment=commitment,
            event_envelope=event_envelope, execution_kind=execution_kind,
            per_action_selection=selections)
        self.controller.release(receipt)
        return dict(step=self.store.checkpoint["completed_steps"],
            prediction_batch_sequence=batch_sequence, decision_id=decision_id,
            execution_kind=execution_kind, action_source=action_source,
            state=capture["state"], epoch=capture["epoch"],
            transaction_id=capture["transaction_id"], status="AUTHORIZED",
            imported_pre_restart_records=sum(item["restoration_status"] ==
                "PRE_RESTART_IMPORTED" for item in
                capture["authenticated_history_provenance"]),
            relation_previews=previews, relation_selections_before=selections,
            forecasts=public_forecasts, choices=routed["choices"],
            execution=actual, receipt=receipt_value,
            prediction_match=training["prediction_match"],
            memory_publication=dict(authorization=result.status.value,
                event_sequence=event_envelope["sequence"], event_head_sha256=event_head),
            shadow_scoring={key: dict(predicted=specialist_predictions[key],
                correct=specialist_predictions[key] == receipt.realized_consequence)
                for key in SPECIALISTS}, routing_evidence=route, model_calls=9)


def _segment_expectation(segment: str) -> dict:
    return {
        "A1": dict(resume=False, attempts=0, events=0, batches=0, runtime=0,
                   regime="A", transition=False,
                   operations=["calibration"] * 6 + ["comparison"]),
        "B1": dict(resume=True, attempts=6, events=6, batches=7, runtime=1,
                   regime="B", transition=True,
                   operations=["calibration"] * 3),
        "B2": dict(resume=True, attempts=9, events=9, batches=10, runtime=2,
                   regime="B", transition=False,
                   operations=["calibration"] * 3 + ["comparison"]),
        "A2": dict(resume=True, attempts=12, events=12, batches=14, runtime=3,
                   regime="A", transition=True,
                   operations=["calibration"] * 6 + ["ordinary"]),
    }[segment]


def run_relation_segment(session: Path, routing_registry: Path, segment: str,
                         resume: bool, joint_client=None,
                         specialist_clients=None) -> dict:
    if segment not in SEGMENTS:
        raise RoutingError("unknown relation-routing segment")
    plan = _segment_expectation(segment)
    if resume != plan["resume"]:
        raise RoutingError("segment resume mode differs from frozen schedule")
    registry = load_relation_routing_registry(routing_registry)
    if specialist_clients is None:
        specialist_clients, registry = relation_routed_clients(
            routing_registry, device="cuda")
    joint = joint_client or ModelClient()
    before = {key: specialist_clients[key].requests for key in SPECIALISTS}
    joint_before = joint.requests
    with SessionStore(session, resume) as store, \
            RelationEvidenceStore(routing_registry) as routing_store:
        requests = sum(row["kind"] == "REQUEST_INTENT"
                       for row in store.records["calls"])
        actual = dict(attempts=store.checkpoint["attempted_decisions"],
            events=len(store.records["events"]), batches=requests // 9,
            runtime=store.checkpoint["runtime_index"])
        expected = {key: plan[key] for key in actual}
        if requests % 9 or actual != expected or \
                store.checkpoint["completed_steps"] != plan["events"] or \
                store.checkpoint["current_state"] != 1:
            raise RoutingError(f"segment start differs from frozen schedule: {actual}")
        store.configure_regime(plan["regime"], plan["transition"])
        runtime = RelationRoutedRuntime(store, joint, specialist_clients, registry,
                                        routing_store, plan["regime"])
        rows = []
        for operation in plan["operations"]:
            if operation == "comparison": rows.append(runtime.comparison())
            elif operation == "ordinary":
                rows.append(runtime.execute("EXPLORER_SELECTED_EXECUTION"))
            else: rows.append(runtime.execute("ROUTING_CALIBRATION_EXECUTION"))
        calls = joint.requests - joint_before + sum(
            specialist_clients[key].requests - before[key] for key in SPECIALISTS)
        return dict(mode="relation-routed-live", segment=segment,
            session_id=store.checkpoint["session_id"], session=str(store.directory),
            resumed=resume, runtime_index=store.checkpoint["runtime_index"],
            epoch=store.checkpoint["current_epoch"], rows=rows,
            actual_model_calls=calls,
            model_calls_by_role=dict(joint_next_state=joint.requests - joint_before,
                G2=specialist_clients["G2"].requests - before["G2"],
                G3=specialist_clients["G3"].requests - before["G3"]),
            target_relation=routing_store.preview(1, "HOLD"),
            relation_state=routing_store.state["relations"],
            consequence_specialists=registry["payload"]["specialists"],
            external_regime_version=plan["regime"], regime_model_visible=False,
            checkpoint=_plain(store.checkpoint))


def _phase_for_regime(regime: str, seen_b: bool) -> tuple[str, bool]:
    if regime == "B": return "B", True
    return ("A2" if seen_b else "A1"), seen_b


def analyze_relation_routing_campaign(session: Path, routing_registry: Path,
                                      output: Path) -> dict:
    if output.exists():
        raise RoutingError("relation routing report output already exists")
    policy = json.loads(POLICY_PATH.read_text())
    with SessionStore(session, True) as store, \
            RelationEvidenceStore(routing_registry) as route:
        route.bind_session(store)
        events = [deepcopy(row["record"]) for row in store.records["events"]]
        routing = [deepcopy(row["record"]) for row in route.records]
        training = [deepcopy(row) for row in store.records["training"]]
        calls = deepcopy(store.records["calls"])
        checkpoint = deepcopy(store.checkpoint)
        final_relation_state = deepcopy(route.state["relations"])
        registry = deepcopy(route.registry)

    request_intents = [row for row in calls if row["kind"] == "REQUEST_INTENT"]
    if len(request_intents) != 189:
        raise RoutingError(f"campaign request count differs from frozen 189: {len(request_intents)}")
    batches = {}
    artifact_checks: dict[str, dict[str, set]] = {}
    hidden_prompt_checks = 0
    for row in request_intents:
        record = row["record"]
        serialized = json.dumps(record["request"], sort_keys=True).lower()
        if "regime" in serialized or "selected_specialist" in serialized or \
                "predicted_next_state" in serialized:
            raise RoutingError("hidden or correlated routing input found in prompt")
        hidden_prompt_checks += 1
        parts = record["call_id"].split(":")
        epoch_token = next((part for part in parts if part.startswith("e") and
                            part[1:].isdigit()), None)
        batch_token = next((part for part in parts if part.startswith("b") and
                            part[1:].isdigit()), None)
        if epoch_token is None or batch_token is None:
            raise RoutingError("relation campaign call identity is malformed")
        runtime = str(int(epoch_token[1:]) - 2000)
        batch = int(batch_token[1:])
        batches.setdefault((runtime, batch), []).append(record["role"])
        if record["role"].startswith("routed-consequence:"):
            specialist = record["role"].split(":", 1)[1]
            actual = record.get("model_generation_identity", {}).get("artifact_sha256")
            expected = registry["specialists"][specialist]["artifact_sha256"]
            artifact_checks.setdefault(runtime, {}).setdefault(specialist, set()).add(
                actual == expected)
    required_roles = Counter({"joint-next-state": 3,
        "routed-consequence:G2": 3, "routed-consequence:G3": 3})
    if any(Counter(roles) != required_roles for roles in batches.values()):
        raise RoutingError("prediction batch role cardinality mismatch")
    batches_by_runtime = Counter(runtime for runtime, _ in batches)
    expected_batches = {"1": 7, "2": 3, "3": 4, "4": 7}
    if dict(batches_by_runtime) != expected_batches:
        raise RoutingError(f"campaign runtime batches differ: {dict(batches_by_runtime)}")
    artifact_verification = {runtime: {specialist: values == {True}
        for specialist, values in checks.items()}
        for runtime, checks in artifact_checks.items()}
    artifacts_reverified = set(artifact_verification) == set(expected_batches) and all(
        set(checks) == set(SPECIALISTS) and all(checks.values())
        for checks in artifact_verification.values())

    training_rows = [row["record"] for row in training]
    if len(training_rows) != 21 or sorted(
            row["prediction_batch_sequence"] for row in training_rows) != list(range(1, 22)):
        raise RoutingError("campaign decision trace differs from frozen 21 batches")
    by_receipt = {tuple(row["receipt_identity"]): row for row in routing}
    event_by_receipt = {tuple(row["receipt_identity"]): row for row in events}
    if set(by_receipt) != set(event_by_receipt):
        raise RoutingError("event/routing receipt identities differ")
    routing_by_receipt = {key: by_receipt[key] for key in by_receipt}

    seen_b = False; phase_by_receipt = {}; phase_by_batch = {}
    for row in sorted(training_rows, key=lambda value: value["prediction_batch_sequence"]):
        phase, seen_b = _phase_for_regime(row["external_regime_version"], seen_b)
        phase_by_batch[row["prediction_batch_sequence"]] = phase
        if row.get("receipt_identity") is not None:
            phase_by_receipt[tuple(row["receipt_identity"])] = phase

    target = relation_identity(1, "HOLD")
    target_trace = []
    for row in routing:
        if row["relation"] != target:
            continue
        identity = tuple(row["receipt_identity"])
        event = event_by_receipt[identity]
        target_trace.append(dict(evidence_sequence=row["evidence_sequence"],
            phase=phase_by_receipt[identity], execution_kind=row["execution_kind"],
            relation=row["relation"], G2_prediction=row["specialists"]["G2"][
                "frozen_consequence"], G3_prediction=row["specialists"]["G3"][
                "frozen_consequence"], realized_consequence=row["realized_consequence"],
            G2_correct=row["correctness"]["G2"],
            G3_correct=row["correctness"]["G3"],
            selected_before=row["selected_specialist"],
            selected_after=row["selected_specialist_after"],
            local_score_after=row["router_score_after"],
            switch_occurred=row["switch_occurred"],
            receipt_identity=row["receipt_identity"],
            receipt_provenance_sha256=row["receipt_provenance_sha256"],
            runtime_index=event["source_scope"]["runtime_index"]))
    calibration_counts = Counter(row["phase"] for row in target_trace
        if row["execution_kind"] == "ROUTING_CALIBRATION_EXECUTION")
    if dict(calibration_counts) != {"A1": 6, "B": 6, "A2": 6}:
        raise RoutingError(f"target calibration schedule incomplete: {dict(calibration_counts)}")

    def first_change(phase: str, expected_value: int) -> dict | None:
        return next((row for row in target_trace if row["phase"] == phase and
                     row["realized_consequence"] == expected_value), None)

    def first_switch(before: str, after: str, at_or_after: int | None) -> dict | None:
        if at_or_after is None: return None
        return next((row for row in target_trace
            if row["evidence_sequence"] >= at_or_after and row["switch_occurred"] and
               row["selected_before"] == before and row["selected_after"] == after), None)

    first_b = first_change("B", -1)
    first_a2 = first_change("A2", 1)
    switch_b = first_switch("G2", "G3", None if first_b is None else
                            first_b["evidence_sequence"])
    switch_a2 = first_switch("G3", "G2", None if first_a2 is None else
                             first_a2["evidence_sequence"])

    def latency(first: dict | None, switch: dict | None) -> dict:
        if first is None:
            return dict(first_contradictory_receipt=None, switch_evidence=None,
                        authenticated_observations_inclusive=None,
                        additional_observations_after_first=None)
        return dict(first_contradictory_receipt=first["evidence_sequence"],
            switch_evidence=None if switch is None else switch["evidence_sequence"],
            authenticated_observations_inclusive=(None if switch is None else
                switch["evidence_sequence"] - first["evidence_sequence"] + 1),
            additional_observations_after_first=(None if switch is None else
                switch["evidence_sequence"] - first["evidence_sequence"]))

    encountered_states = sorted({row["pre_state"] for row in training_rows})
    per_relation_final = []
    evidence_rows = routing
    router = RelationGroundedRouter(policy)
    for state in encountered_states:
        for action in ACTION_ORDER:
            relation = relation_identity(state, action); key = relation_key(relation)
            stored = final_relation_state.get(key)
            per_relation_final.append(dict(relation=relation,
                selected_specialist=("G2" if stored is None else
                                     stored["selected_specialist"]),
                evidence_count=(0 if stored is None else stored["evidence_count"]),
                local_score=router.scores(evidence_rows, relation)))

    mixed_examples = []
    ordinary_decisions = []
    for row in sorted(training_rows, key=lambda value: value["prediction_batch_sequence"]):
        selections = row["relation_selections_before"]
        if len(set(selections.values())) > 1:
            mixed_examples.append(dict(
                prediction_batch_sequence=row["prediction_batch_sequence"],
                phase=phase_by_batch[row["prediction_batch_sequence"]],
                execution_kind=row["execution_kind"], pre_state=row.get("pre_state", 1),
                selections=selections, choices=row["choices"]))
        if row["execution_kind"] in ("COMPARISON_ONLY_NO_EXECUTION",
                                     "EXPLORER_SELECTED_EXECUTION"):
            choices = row["choices"]
            ordinary_decisions.append(dict(
                prediction_batch_sequence=row["prediction_batch_sequence"],
                phase=phase_by_batch[row["prediction_batch_sequence"]],
                execution_kind=row["execution_kind"],
                choices=choices, selections=selections,
                routed_differs_from_G2=(choices["relation_routed"]["action"] !=
                                        choices["G2"]["action"]),
                routed_differs_from_G3=(choices["relation_routed"]["action"] !=
                                        choices["G3"]["action"]),
                routed_is_distinct_from_both=(choices["relation_routed"]["action"]
                    not in {choices["G2"]["action"], choices["G3"]["action"]}),
                mixed_relation_selection=len(set(selections.values())) > 1,
                executed_action=row.get("chosen_action"),
                receipt_identity=row.get("receipt_identity")))

    global_policy = json.loads(GLOBAL_POLICY_PATH.read_text())
    global_router = GroundedRouter(global_policy)
    global_selected, global_evidence, global_switches = "G2", [], []
    offline_rows = []
    routing_by_event_sequence = {row["receipt_event_sequence"]: row for row in routing}
    for row in sorted(training_rows, key=lambda value: value["prediction_batch_sequence"]):
        batch_sequence = row["prediction_batch_sequence"]
        local = row["relation_selections_before"]
        comparison = dict(prediction_batch_sequence=batch_sequence,
            phase=phase_by_batch[batch_sequence], execution_kind=row["execution_kind"],
            global_selected=global_selected, local_selected_by_action=local,
            differing_actions=[action for action in ACTION_ORDER
                               if local[action] != global_selected],
            executed_action=row.get("chosen_action"),
            executed_relation_selection_differs=(None if row.get("chosen_action") is None
                else local[row["chosen_action"]] != global_selected))
        offline_rows.append(comparison)
        if row.get("receipt_identity") is None:
            continue
        evidence_row = routing_by_receipt[tuple(row["receipt_identity"])]
        global_evidence.append(evidence_row)
        update = global_router.update(global_evidence, global_selected)
        if update["switched"]:
            global_switches.append(dict(evidence_sequence=evidence_row["evidence_sequence"],
                from_specialist=global_selected,
                to_specialist=update["selected_after"], scores=update["scores"],
                reason=update["reason"]))
        global_selected = update["selected_after"]

    b_events = [(row, event_by_receipt[tuple(row["receipt_identity"])])
                for row in routing
                if event_by_receipt[tuple(row["receipt_identity"])][
                    "external_regime_version"] == "B"]
    b_runtimes = sorted({event["source_scope"]["runtime_index"]
                         for _, event in b_events})
    continuity = None
    for (prior_row, prior_event), (next_row, next_event) in zip(b_events, b_events[1:]):
        if prior_event["source_scope"]["runtime_index"] != \
                next_event["source_scope"]["runtime_index"]:
            continuity = dict(relation=prior_row["relation"],
                before_restart_selected_after=prior_row["selected_specialist_after"],
                after_restart_selected_before=next_row["selected_specialist"],
                preserved=prior_row["selected_specialist_after"] ==
                          next_row["selected_specialist"])
            break
    imported_history_requests = 0
    for row in request_intents:
        parts = row["record"]["call_id"].split(":")
        if "e2003" not in parts:
            continue
        payload = json.loads(row["record"]["request"]["prompt"])
        imported_history_requests += bool(payload["VERIFIED_CHRONOLOGICAL_HISTORY"])

    execution_kinds = Counter(event["execution_kind"] for event in events)
    phase_counts = Counter(phase_by_receipt[tuple(event["receipt_identity"])]
                           for event in events)
    actual_switches = [dict(evidence_sequence=row["evidence_sequence"],
        relation=row["relation"], from_specialist=row["selected_specialist"],
        to_specialist=row["selected_specialist_after"],
        score_after=row["router_score_after"], reason=row["switch_reason"])
        for row in routing if row["switch_occurred"]]
    result = dict(status="COMPLETE", relation_identity=["pre_state", "action"],
        routing_rule=dict(window_size=policy["window_size"],
            minimum_shared_scored_events=policy["minimum_shared_scored_events"],
            switch_lead_correct=policy["switch_lead_correct"],
            cold_start_specialist=policy["cold_start_specialist"],
            ties_preserve_incumbent=True, evidence_scope="EXACT_RELATION_ONLY"),
        schedule=policy["schedule"], prediction_batches=21,
        attempted_executions=checkpoint["attempted_decisions"],
        executed_decisions=len(events), execution_kind_counts=dict(execution_kinds),
        phase_execution_counts=dict(phase_counts), total_model_calls=len(request_intents),
        model_calls_by_role=dict(Counter(row["record"]["role"]
                                         for row in request_intents)),
        target_relation_trace=target_trace,
        target_relation_switches=[row for row in actual_switches
                                  if row["relation"] == target],
        adaptation_latency=dict(A_to_B=latency(first_b, switch_b),
                                B_to_A2=latency(first_a2, switch_a2)),
        per_relation_final_state=per_relation_final,
        simultaneous_mixed_specialist_examples=mixed_examples,
        ordinary_decisions=ordinary_decisions,
        global_vs_local_offline_replay=dict(
            scope="specialist selection on identical frozen evidence; no counterfactual outcome",
            global_policy_sha256=file_hash(GLOBAL_POLICY_PATH),
            local_policy_sha256=file_hash(POLICY_PATH), rows=offline_rows,
            global_switches=global_switches, global_final_selected=global_selected,
            local_switches=actual_switches,
            executed_relation_selection_disagreements=sum(
                row["executed_relation_selection_differs"] is True for row in offline_rows)),
        restart_proof=dict(B_runtime_indices=b_runtimes,
            runtime_indices=sorted({event["source_scope"]["runtime_index"]
                                    for event in events}),
            batches_by_runtime=dict(batches_by_runtime),
            target_relation_selection_continuity=continuity,
            imported_history_requests_after_B_restart=imported_history_requests,
            artifact_verifications_by_runtime=artifact_verification,
            specialist_artifacts_reverified_on_every_runtime=artifacts_reverified,
            source_identities=sorted({event["source_scope"]["source_identity"]
                                      for event in events})),
        memory_contradiction=dict(relation=target,
            chronological_consequences=[row["realized_consequence"]
                                        for row in target_trace],
            phase_consequences={phase: [row["realized_consequence"]
                for row in target_trace if row["phase"] == phase]
                for phase in ("A1", "B", "A2")},
            earlier_records_overwritten=False),
        hidden_regime_prompt_checks=hidden_prompt_checks,
        global_lifecycle_status={"G2": "ACTIVE", "G3": "REJECTED"},
        routing_eligibility={"G2": "ROUTABLE_SPECIALIST",
                             "G3": "ROUTABLE_SPECIALIST"},
        no_weight_updates=True,
        final_checkpoint=dict(attempted_decisions=checkpoint["attempted_decisions"],
            completed_steps=checkpoint["completed_steps"],
            runtime_index=checkpoint["runtime_index"],
            current_state=checkpoint["current_state"], streams=checkpoint["streams"]))
    atomic_json(output, result)
    return result
