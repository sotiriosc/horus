"""Authenticated, non-learning routing across retained consequence specialists."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from dataclasses import asdict, dataclass
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
from experiments.map_consequence_only_isolation_v0.protocol import parse as parse_consequence
from experiments.model_map_proposal_v0.adapter import MODEL, parse as parse_joint
from experiments.model_proposal_role_composition_v2.protocol import OPTIONS
from experiments.realized_event_grounding_v0.framework import evidence

from .core import (BoundPredictionMap, GroundedObservation, MAPPING, MapForecast,
                   MechanicalExplorer, digest, unwrap_map)
from .grounded_learning import (QwenConsequenceClient, ROOT, atomic_json,
                                file_hash)
from .live import (CONSEQUENCE_SYSTEM, JOINT_SYSTEM, DurableHistoryReader,
                   LiveController, ModelClient, SessionError, SessionStore,
                   _canonical, _now, _plain)
from .model_registry import RegistryError, load_registry


POLICY_PATH = Path(__file__).with_name("routing_policy.json")
DEFAULT_SOURCE_REGISTRY = ROOT / "research/learning-stability-v0/registry"
ROUTING_VERSION = 1


class RoutingError(RuntimeError):
    pass


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


def initialize_routing_registry(root: Path,
                                source_registry: Path = DEFAULT_SOURCE_REGISTRY) -> dict:
    """Copy exactly G2/G3 while retaining their global lifecycle statuses."""
    root = root.resolve()
    if root.exists():
        raise RoutingError("routing registry already exists")
    source = load_registry(source_registry)
    entries = {row["generation"]: row for row in source["entries"]}
    policy = json.loads(POLICY_PATH.read_text())
    if set(entries) < {2, 3} or entries[2]["status"] != "ACTIVE" or \
            entries[3]["status"] != "REJECTED":
        raise RoutingError("source lifecycle does not preserve ACTIVE G2 / REJECTED G3")
    if any(row["generation"] == 4 and row["status"] != "REJECTED"
           for row in source["entries"]):
        raise RoutingError("unexpected generation-4 lifecycle state")
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
        lineage_source = source["root"] / lineage_relative
        destination = root / f"specialists/generation-{generation:04d}"
        adapter_relative = str((destination / "adapter.safetensors").relative_to(root))
        lineage_copy_relative = str((destination / "learning-lineage.json").relative_to(root))
        manifest_copy_relative = str((destination / "source-generation.json").relative_to(root))
        _copy(adapter_source, root / adapter_relative)
        _copy(lineage_source, root / lineage_copy_relative)
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
    payload = dict(version=ROUTING_VERSION, created_at=_now(),
        source_registry_state_sha256=source["state_document"]["sha256"],
        global_active_generation=2, default_specialist=policy["cold_start_specialist"],
        routing_policy_sha256=file_hash(POLICY_PATH), specialists=specialists,
        lifecycle_status_rewritten=False, weights_modified=False,
        generation_3r_included=False)
    atomic_json(root / "routing-registry.json", _document(payload))
    RoutingEvidenceStore.initialize(root)
    return dict(root=str(root), registry_sha256=digest(payload),
                source_registry_state_sha256=payload["source_registry_state_sha256"],
                specialists=specialists)


def load_routing_registry(root: Path) -> dict:
    root = root.resolve()
    document = _read_document(root / "routing-registry.json", "routing registry")
    payload = document["payload"]
    policy = json.loads(POLICY_PATH.read_text())
    if payload.get("version") != ROUTING_VERSION or \
            payload.get("routing_policy_sha256") != file_hash(POLICY_PATH):
        raise RoutingError("routing policy identity mismatch")
    rows = payload.get("specialists")
    if not isinstance(rows, list) or [row.get("id") for row in rows] != ["G2", "G3"]:
        raise RoutingError("routing pool must contain exactly G2 and G3")
    expected = {row["id"]: row for row in policy["specialists"]}
    by_id = {}
    for row in rows:
        if row.get("generation") != expected[row["id"]]["generation"] or \
                row.get("artifact_sha256") != expected[row["id"]]["artifact_sha256"]:
            raise RoutingError("specialist identity differs from frozen policy")
        if row.get("routing_eligibility") != "ROUTABLE_SPECIALIST":
            raise RoutingError("specialist is not routing eligible")
        required_status = "ACTIVE" if row["id"] == "G2" else "REJECTED"
        if row.get("global_lifecycle_status") != required_status:
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


class GroundedRouter:
    """Pure fixed-window score and hysteresis rule."""
    def __init__(self, policy: dict | None = None):
        self.policy = policy or json.loads(POLICY_PATH.read_text())

    def scores(self, evidence_rows: list[dict]) -> dict:
        window = evidence_rows[-self.policy["window_size"]:]
        return {specialist: dict(correct=sum(
                    bool(row["correctness"][specialist]) for row in window),
                total=len(window)) for specialist in ("G2", "G3")}

    def update(self, evidence_rows: list[dict], selected: str) -> dict:
        scores = self.scores(evidence_rows)
        challenger = "G3" if selected == "G2" else "G2"
        eligible = scores[selected]["total"] >= self.policy[
            "minimum_shared_scored_events"]
        lead = scores[challenger]["correct"] - scores[selected]["correct"]
        switched = eligible and lead >= self.policy["switch_lead_correct"]
        after = challenger if switched else selected
        reason = (f"{challenger} grounded lead {scores[challenger]['correct']}/"
                  f"{scores[challenger]['total']} vs {scores[selected]['correct']}/"
                  f"{scores[selected]['total']}" if switched else
                  "incumbent retained: minimum evidence/lead not satisfied")
        return dict(selected_before=selected, selected_after=after,
                    scores=scores, challenger=challenger, challenger_lead=lead,
                    minimum_evidence_satisfied=eligible, switched=switched,
                    reason=reason)


class RoutingEvidenceStore:
    """Local-HMAC append-only receipt-scored router evidence and checkpoint."""
    KEY = "routing-authority.key"
    STATE = "router-state.json"
    STREAM = "routing-evidence.jsonl"

    @staticmethod
    def initialize(root: Path) -> None:
        root = root.resolve()
        for name in (RoutingEvidenceStore.KEY, RoutingEvidenceStore.STATE,
                     RoutingEvidenceStore.STREAM):
            if (root / name).exists():
                raise RoutingError("routing evidence store already exists")
        key = secrets.token_bytes(32)
        descriptor = os.open(root / RoutingEvidenceStore.KEY,
                             os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            os.write(descriptor, (key.hex() + "\n").encode()); os.fsync(descriptor)
        finally:
            os.close(descriptor)
        (root / RoutingEvidenceStore.STREAM).touch(mode=0o600)
        state = dict(version=ROUTING_VERSION, selected_specialist="G2",
            evidence_count=0, evidence_head_sha256=None, session_id=None,
            updated_at=_now())
        RoutingEvidenceStore._write_state_file(root, key, state)

    @staticmethod
    def _write_state_file(root: Path, key: bytes, state: dict) -> None:
        document = {"payload": state, "hmac_sha256": new_hmac(
            key, _canonical(state).encode(), "sha256").hexdigest()}
        temporary = root / (RoutingEvidenceStore.STATE + ".tmp")
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            os.write(descriptor, (json.dumps(document, indent=2, sort_keys=True) +
                                  "\n").encode()); os.fsync(descriptor)
        finally:
            os.close(descriptor)
        os.replace(temporary, root / RoutingEvidenceStore.STATE)

    def __init__(self, root: Path):
        self.registry = load_routing_registry(root)
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
            self.router = GroundedRouter(self.registry["policy"])
            self._validate_replay()
        except Exception:
            self.close()
            raise

    def close(self) -> None:
        if hasattr(self, "_lock") and not self._lock.closed:
            fcntl.flock(self._lock, fcntl.LOCK_UN); self._lock.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

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

    def _validate_replay(self) -> None:
        selected, replay = "G2", []
        previous = None
        for index, envelope in enumerate(self.records, 1):
            row = envelope["record"]
            if row.get("evidence_sequence") != index or \
                    row.get("selected_specialist") != selected or \
                    set(row.get("correctness", {})) != {"G2", "G3"}:
                raise RoutingError("routing evidence state mismatch")
            before = self.router.scores(replay)
            if row.get("router_score_before") != before:
                raise RoutingError("router before-score mismatch")
            replay.append(row)
            result = self.router.update(replay, selected)
            if row.get("router_score_after") != result["scores"] or \
                    row.get("switch_occurred") != result["switched"] or \
                    row.get("selected_specialist_after") != result["selected_after"] or \
                    row.get("switch_reason") != result["reason"]:
                raise RoutingError("router transition does not replay")
            selected = result["selected_after"]
            previous = sha256(_canonical(envelope).encode()).hexdigest()
        if self.state.get("version") != ROUTING_VERSION or \
                self.state.get("evidence_count") != len(self.records) or \
                self.state.get("evidence_head_sha256") != previous or \
                self.state.get("selected_specialist") != selected:
            raise RoutingError("router checkpoint/evidence mismatch")

    def preview(self) -> dict:
        rows = [envelope["record"] for envelope in self.records]
        return dict(selected_specialist=self.state["selected_specialist"],
                    scores=self.router.scores(rows), evidence_count=len(rows))

    @staticmethod
    def _time(value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    def _validate_commitment(self, store: SessionStore, commitment: dict,
                             event_record: dict) -> None:
        by_sequence = {row["sequence"]: row for row in store.records["calls"]}
        event_time = self._time(event_record["recorded_at"])
        for specialist in ("G2", "G3"):
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
            row = envelope["record"]
            actual = event["record"]
            if row["receipt_identity"] != actual["receipt_identity"] or \
                    row["receipt_provenance_sha256"] != actual[
                        "receipt_provenance_sha256"] or \
                    row["realized_consequence"] != actual["receipt"][
                        "realized_consequence"] or \
                    actual["authorization_status"] != "AUTHORIZED":
                raise RoutingError("routing evidence receipt mismatch")
            self._validate_commitment(store, row["prediction_commitment"], actual)

    def record(self, store: SessionStore, *, context_hash: str, pre_state: int,
               selected_action: str, predictions: dict[str, int],
               commitment: dict, event_envelope: dict) -> dict:
        self.bind_session(store, allow_pending_event=True)
        if event_envelope is not store.records["events"][-1] or \
                len(store.records["events"]) != len(self.records) + 1:
            raise RoutingError("receipt was not the next authenticated routing event")
        event = event_envelope["record"]
        self._validate_commitment(store, commitment, event)
        if set(predictions) != {"G2", "G3"} or \
                any(type(value) is not int or value not in (-1, 0, 1)
                    for value in predictions.values()):
            raise RoutingError("invalid specialist prediction set")
        before = self.preview()
        realized = event["receipt"]["realized_consequence"]
        correctness = {key: value == realized for key, value in predictions.items()}
        record = dict(evidence_sequence=len(self.records) + 1,
            context_input_sha256=context_hash, pre_state=pre_state,
            specialists={key: dict(generation=self.registry["specialists"][key][
                "generation"], artifact_sha256=self.registry["specialists"][key][
                    "artifact_sha256"], frozen_consequence=predictions[key])
                for key in ("G2", "G3")},
            selected_specialist=before["selected_specialist"],
            selected_action=selected_action, realized_consequence=realized,
            correctness=correctness, receipt_identity=event["receipt_identity"],
            receipt_provenance_sha256=event["receipt_provenance_sha256"],
            receipt_event_sequence=event_envelope["sequence"],
            router_score_before=before["scores"],
            prediction_commitment=deepcopy(commitment),
            predictions_frozen_before_execution=True,
            evidence_source="AUTHORIZED_ORIGINAL_RECEIPT", recorded_at=_now())
        prospective = [row["record"] for row in self.records] + [record]
        transition = self.router.update(prospective, before["selected_specialist"])
        record.update(router_score_after=transition["scores"],
            switch_occurred=transition["switched"],
            selected_specialist_after=transition["selected_after"],
            switch_reason=transition["reason"])
        previous = None if not self.records else sha256(
            _canonical(self.records[-1]).encode()).hexdigest()
        signed = dict(sequence=len(self.records) + 1, previous_sha256=previous,
                      kind="AUTHORIZED_RECEIPT_SCORED_SPECIALISTS", record=record)
        envelope = {**signed, "hmac_sha256": self._mac(signed)}
        with (self.root / self.STREAM).open("a") as stream:
            stream.write(_canonical(envelope) + "\n"); stream.flush(); os.fsync(stream.fileno())
        self.records.append(envelope)
        self.state.update(selected_specialist=transition["selected_after"],
            evidence_count=len(self.records),
            evidence_head_sha256=sha256(_canonical(envelope).encode()).hexdigest())
        self._write_state()
        return _plain(record)


def routed_clients(registry_root: Path, device: str | None = None) -> tuple[dict, dict]:
    registry = load_routing_registry(registry_root)
    clients = {}
    for specialist in ("G2", "G3"):
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
        client.model_id = f"horus-routed-{specialist}:{row['artifact_sha256']}"
        clients[specialist] = client
    return clients, registry


@dataclass(frozen=True)
class RoutedForecastBatch:
    forecasts: dict[str, tuple[MapForecast, ...]]
    evidence: dict[str, dict[str, Any]]
    commitments: dict[str, dict]
    all_valid: bool


class RoutedSplitMap:
    def __init__(self, store: SessionStore, joint_client: ModelClient,
                 specialists: dict, registry: dict):
        self.store, self.joint_client = store, joint_client
        self.specialists, self.registry = specialists, registry
        for key in ("G2", "G3"):
            actual = getattr(specialists[key], "horus_model_identity", {})
            if actual.get("artifact_sha256") != registry["specialists"][key][
                    "artifact_sha256"]:
                raise RoutingError("loaded specialist identity mismatch")

    @staticmethod
    def _request(system: str, prompt: str, model: str) -> dict:
        return dict(model=model, system=system, prompt=prompt, stream=False,
                    options=dict(OPTIONS["Map"]))

    def forecasts(self, capture: dict, decision_id: str) -> RoutedForecastBatch:
        work = {}
        # Commit every complete request before any response can influence routing.
        for action in ACTION_ORDER:
            payload = capture["map_inputs"][action]
            prompt = _canonical(payload)
            if "regime" in prompt.lower():
                raise RoutingError("hidden regime entered model prompt")
            joint = self._request(JOINT_SYSTEM, prompt,
                                  getattr(self.joint_client, "model_id", MODEL))
            work[action] = dict(payload=payload, prompt=prompt, joint=joint,
                                specialists={})
            call_id = f"{decision_id}:{action}:J"
            intent = self.store.append("calls", "REQUEST_INTENT", dict(
                call_id=call_id, role="joint-next-state", request=joint,
                request_sha256=digest(joint)))
            work[action]["joint_intent"] = intent
            for specialist in ("G2", "G3"):
                client = self.specialists[specialist]
                request = self._request(CONSEQUENCE_SYSTEM, prompt, client.model_id)
                request["horus_model_identity"] = _plain(client.horus_model_identity)
                call_id = f"{decision_id}:{action}:{specialist}"
                intent = self.store.append("calls", "REQUEST_INTENT", dict(
                    call_id=call_id, role=f"routed-consequence:{specialist}",
                    request=request, request_sha256=digest(request),
                    same_authenticated_context=True,
                    independent_of_other_specialist=True,
                    independent_of_router_decision=True,
                    model_generation_identity=client.horus_model_identity))
                work[action]["specialists"][specialist] = dict(
                    request=request, intent=intent)

        forecasts = {"G2": [], "G3": []}; all_valid = True
        evidence_rows, commitments = {}, {}
        for action in ACTION_ORDER:
            row, payload = work[action], work[action]["payload"]
            joint_call_id = row["joint_intent"]["record"]["call_id"]
            jr = self.joint_client.generate(row["joint"])
            jr_env = self.store.append("calls", "RESPONSE", dict(
                call_id=joint_call_id, response=jr, response_sha256=digest(jr)))
            jp = None; jf = jr.get("transport_error")
            if jf is None:
                try: jp = parse_joint(jr["raw_output"])
                except (ValueError, TypeError, json.JSONDecodeError) as exc:
                    jf = type(exc).__name__
            jp_env = self.store.append("calls", "PARSED", dict(
                call_id=joint_call_id, parsed=jp, parse_error=jf))
            history = tuple(GroundedObservation(**item)
                            for item in payload["VERIFIED_CHRONOLOGICAL_HISTORY"])
            input_context = dict(state=capture["state"], action=action,
                action_alias=payload["target_action"], epoch=capture["epoch"],
                transaction_id=capture["transaction_id"],
                authenticated_history=[asdict(item) for item in history],
                memory_sha256=capture["memory_sha256"],
                authenticated_history_reference=capture[
                    "authenticated_history_reference"])
            commitments[action] = dict(joint=dict(call_id=joint_call_id,
                request_sequence=row["joint_intent"]["sequence"],
                response_sequence=jr_env["sequence"], parsed_sequence=jp_env["sequence"],
                request_sha256=digest(row["joint"])), specialists={})
            evidence_rows[action] = {}
            for specialist in ("G2", "G3"):
                item, client = row["specialists"][specialist], self.specialists[specialist]
                call_id = item["intent"]["record"]["call_id"]
                cr = client.generate(item["request"])
                cr_env = self.store.append("calls", "RESPONSE", dict(
                    call_id=call_id, response=cr, response_sha256=digest(cr)))
                cp = None; cf = cr.get("transport_error")
                if cf is None:
                    try: cp = parse_consequence(cr["raw_output"], "C")
                    except (ValueError, TypeError, json.JSONDecodeError) as exc:
                        cf = type(exc).__name__
                cp_env = self.store.append("calls", "PARSED", dict(
                    call_id=call_id, parsed=cp, parse_error=cf))
                valid = jp is not None and cp is not None
                all_valid = all_valid and valid
                forecast = MapForecast(action, payload["target_action"],
                    None if jp is None else jp["next_state"],
                    None if cp is None else cp["consequence"], not valid,
                    None if valid else f"INVALID_COMPONENT:J={jf};{specialist}={cf}",
                    len(history), input_context)
                forecasts[specialist].append(forecast)
                evidence_rows[action][specialist] = dict(response=cr, parsed=cp)
                commitments[action]["specialists"][specialist] = dict(
                    call_id=call_id, request_sequence=item["intent"]["sequence"],
                    response_sequence=cr_env["sequence"], parsed_sequence=cp_env["sequence"],
                    request_sha256=digest(item["request"]),
                    prediction=None if cp is None else cp["consequence"],
                    artifact_sha256=self.registry["specialists"][specialist][
                        "artifact_sha256"])
        return RoutedForecastBatch(
            {key: tuple(value) for key, value in forecasts.items()},
            evidence_rows, commitments, all_valid)


class RoutedRuntime:
    def __init__(self, store: SessionStore, joint_client: ModelClient,
                 specialists: dict, registry: dict,
                 routing_store: RoutingEvidenceStore, regime_version: str):
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

    def step(self) -> dict:
        capture = self.reader.capture()
        decision_number = self.store.checkpoint["attempted_decisions"] + 1
        decision_id = (f"{self.store.checkpoint['session_id']}:"
                       f"e{capture['epoch']}:d{decision_number}")
        batch = self.map.forecasts(capture, decision_id)
        preview = self.routing_store.preview()
        selected_specialist = preview["selected_specialist"]
        selected_forecasts = batch.forecasts[selected_specialist]
        choice = self.explorer.choose(selected_forecasts) if batch.all_valid else \
            self.explorer.choose(tuple(replace_forecast_invalid(selected_forecasts)))
        public_forecasts = {key: [asdict(row) for row in value]
                            for key, value in batch.forecasts.items()}
        if not batch.all_valid or choice.abstained:
            self.store.save(state=capture["state"],
                next_transaction_id=capture["transaction_id"], attempted_decision=True)
            return dict(step=self.store.checkpoint["completed_steps"] + 1,
                decision_id=decision_id, status="ABSTAINED",
                router_before=preview, selected_specialist=selected_specialist,
                specialist_forecasts=public_forecasts, explorer=asdict(choice),
                model_calls=9, routing_evidence=None)
        selected = next(row for row in selected_forecasts if row.action == choice.action)
        specialist_predictions = {key: next(row.consequence for row in forecasts
            if row.action == choice.action) for key, forecasts in batch.forecasts.items()}
        commitment = batch.commitments[choice.action]
        prediction = Prediction(capture["epoch"], capture["transaction_id"],
            capture["state"], selected.action, selected.next_state,
            selected.consequence)
        core = self.controller._active.framework.inner
        core.map = BoundPredictionMap(unwrap_map(core.map), prediction)
        pending = self.controller.begin_step(selected.action)
        if _plain(asdict(pending.prediction)) != _plain(asdict(prediction)):
            raise RoutingError("routed prediction was not latched")
        if self.controller._source.reader().current() is not None:
            raise RoutingError("receipt existed before routed execution")
        receipt = self.controller.execute_pending()
        actual = _plain(asdict(self.controller._active.world.last_actual))
        self.authentic[receipt.identity()] = receipt
        self.executions[receipt.identity()] = actual
        result = self.controller.submit_package(evidence(receipt))
        if not result.committed or not result.continued:
            self.controller.release(receipt)
            raise RoutingError(f"grounded routed publication rejected: {result.reason}")
        core = self.controller._active.framework.inner
        record = core.memory.records[-1]
        package = self.controller._active.framework.packages[-1]
        if package.receipt is not receipt:
            raise RoutingError("routed receipt object was substituted")
        receipt_value, memory_value = _plain(asdict(receipt)), _plain(asdict(record))
        event = dict(session_id=self.store.checkpoint["session_id"],
            recorded_at=_now(), receipt=receipt_value,
            receipt_identity=list(receipt.identity()),
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
            decision_id=decision_id, order=self.store.checkpoint["completed_steps"] + 1,
            timestamp=event["recorded_at"], input_context_hash=digest(selected.input_context),
            authenticated_history_reference=capture["authenticated_history_reference"],
            chosen_action=selected.action, predicted_next_state=selected.next_state,
            predicted_consequence=selected.consequence,
            selected_specialist=selected_specialist,
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
                        realized_receipt_is_authenticated_target=True),
            external_regime_version=self.regime_version, regime_model_visible=False)
        self.store.append("training", "AUTHORIZED_ROUTED_GROUNDING_RECORD", training)
        self.store.save(state=receipt.next_state,
            next_transaction_id=core.next_transaction_id,
            completed_step=True, attempted_decision=True)
        route = self.routing_store.record(self.store,
            context_hash=digest(selected.input_context), pre_state=capture["state"],
            selected_action=selected.action, predictions=specialist_predictions,
            commitment=commitment, event_envelope=event_envelope)
        self.controller.release(receipt)
        return dict(step=self.store.checkpoint["completed_steps"],
            decision_id=decision_id, state=capture["state"], epoch=capture["epoch"],
            transaction_id=capture["transaction_id"], status="AUTHORIZED",
            imported_pre_restart_records=sum(item["restoration_status"] ==
                "PRE_RESTART_IMPORTED" for item in
                capture["authenticated_history_provenance"]),
            router_before=preview, selected_specialist=selected_specialist,
            specialist_forecasts=public_forecasts, explorer=asdict(choice),
            execution=actual, receipt=receipt_value,
            prediction_match=training["prediction_match"],
            memory_publication=dict(authorization=result.status.value,
                event_sequence=event_envelope["sequence"], event_head_sha256=event_head),
            shadow_scoring={key: dict(predicted=specialist_predictions[key],
                correct=specialist_predictions[key] == receipt.realized_consequence)
                for key in ("G2", "G3")}, routing_evidence=route, model_calls=9)


def replace_forecast_invalid(rows: tuple[MapForecast, ...]):
    """Ensure a global shadow failure causes the existing Explorer to abstain."""
    for row in rows:
        yield MapForecast(row.action, row.action_alias, row.next_state, row.consequence,
                          True, "INVALID_ROUTED_SPECIALIST_SET", row.history_count,
                          row.input_context)


def run_routed(session: Path, routing_registry: Path, steps: int, resume: bool,
               regime_version: str = "A", allow_regime_transition: bool = False,
               joint_client=None, specialist_clients=None) -> dict:
    if type(steps) is not int or steps < 0:
        raise ValueError("steps must be a nonnegative integer")
    registry = load_routing_registry(routing_registry)
    if specialist_clients is None:
        specialist_clients, registry = routed_clients(routing_registry, device="cuda")
    joint = joint_client or ModelClient()
    before = {key: specialist_clients[key].requests for key in ("G2", "G3")}
    joint_before = joint.requests
    with SessionStore(session, resume) as store, \
            RoutingEvidenceStore(routing_registry) as routing_store:
        store.configure_regime(regime_version, allow_regime_transition)
        runtime = RoutedRuntime(store, joint, specialist_clients, registry,
                                routing_store, regime_version)
        rows = [runtime.step() for _ in range(steps)]
        final = routing_store.preview()
        return dict(mode="routed-live", session_id=store.checkpoint["session_id"],
            session=str(store.directory), resumed=resume,
            runtime_index=store.checkpoint["runtime_index"],
            epoch=store.checkpoint["current_epoch"], steps=rows,
            actual_model_calls=(joint.requests - joint_before + sum(
                specialist_clients[key].requests - before[key] for key in ("G2", "G3"))),
            model_calls_by_role=dict(joint_next_state=joint.requests - joint_before,
                G2=specialist_clients["G2"].requests - before["G2"],
                G3=specialist_clients["G3"].requests - before["G3"]),
            consequence_specialists=registry["payload"]["specialists"],
            router_final=final, external_regime_version=regime_version,
            regime_model_visible=False, checkpoint=_plain(store.checkpoint))


def analyze_routing_campaign(session: Path, routing_registry: Path,
                             output: Path) -> dict:
    if output.exists():
        raise RoutingError("routing report output already exists")
    policy = json.loads(POLICY_PATH.read_text())
    with SessionStore(session, True) as store, RoutingEvidenceStore(routing_registry) as route:
        route.bind_session(store)
        events = [row["record"] for row in store.records["events"]]
        routing = [row["record"] for row in route.records]
        calls = store.records["calls"]
        checkpoint = deepcopy(store.checkpoint)
    phases, seen_b = [], False
    for event, row in zip(events, routing):
        regime = event["external_regime_version"]
        if regime == "B": seen_b = True; phase = "B"
        else: phase = "A2" if seen_b else "A1"
        phases.append(dict(phase=phase, event=event, routing=row))

    phase_reports = {}
    for plan in policy["schedule"]:
        name = plan["phase"]
        rows = [row for row in phases if row["phase"] == name]
        def correct(specialist):
            return sum(row["routing"]["correctness"][specialist] for row in rows)
        phase_reports[name] = dict(attempted_decisions=plan["attempted_decisions"],
            executed=len(rows), nonexecuted_attempts=plan["attempted_decisions"] - len(rows),
            selected_specialist_distribution=dict(Counter(
                row["routing"]["selected_specialist"] for row in rows)),
            G2_correct=correct("G2"), G3_correct=correct("G3"),
            routed_correct=sum(row["routing"]["correctness"][
                row["routing"]["selected_specialist"]] for row in rows),
            switches=[row["routing"]["evidence_sequence"] for row in rows
                      if row["routing"]["switch_occurred"]],
            action_distribution=dict(Counter(
                row["routing"]["selected_action"] for row in rows)),
            realized_consequence_distribution=dict(Counter(str(
                row["routing"]["realized_consequence"]) for row in rows)))

    switches = []
    for index, row in enumerate(routing):
        if not row["switch_occurred"]:
            continue
        future = routing[index + 1:index + 5]
        former, new = row["selected_specialist"], row["selected_specialist_after"]
        assessment = "NOT_ASSESSABLE"; unnecessary = None
        if len(future) == policy["analysis"]["unnecessary_switch_lookahead"]:
            old_correct = sum(item["correctness"][former] for item in future)
            new_correct = sum(item["correctness"][new] for item in future)
            unnecessary = old_correct - new_correct >= policy["switch_lead_correct"]
            assessment = dict(former_correct=old_correct, new_correct=new_correct,
                              unnecessary=unnecessary)
        switches.append(dict(evidence_sequence=row["evidence_sequence"],
            from_specialist=former, to_specialist=new,
            score_after=row["router_score_after"], reason=row["switch_reason"],
            future_four_assessment=assessment))

    prior: dict[tuple, set] = {}; prior_latest = {}; contradiction_first = {}
    contradiction_trace = {}
    for joined in phases:
        row, name = joined["routing"], joined["phase"]
        key = (row["pre_state"], row["selected_action"])
        outcomes = prior.setdefault(key, set())
        if key in prior_latest and row["realized_consequence"] != prior_latest[key] and \
                name not in contradiction_first:
            contradiction_first[name] = row["evidence_sequence"]
        outcomes.add(row["realized_consequence"])
        prior_latest[key] = row["realized_consequence"]
        contradiction_trace.setdefault(key, []).append(dict(
            sequence=row["evidence_sequence"], phase=name,
            consequence=row["realized_consequence"],
            receipt_identity=row["receipt_identity"]))
    contradiction_trace = [dict(pre_state=key[0], action=key[1], observations=value)
        for key, value in contradiction_trace.items()
        if len({item["consequence"] for item in value}) > 1]

    delays = {}
    for name in ("B", "A2"):
        first = contradiction_first.get(name)
        switch = next((row["evidence_sequence"] for row in routing
            if row["switch_occurred"] and row["evidence_sequence"] >= (first or 10**9)), None)
        delays[name] = dict(first_contradictory_receipt_sequence=first,
            switch_evidence_sequence=switch,
            scored_events_after_first_contradiction=(None if first is None or switch is None
                                                      else switch - first))

    rolling = []
    width = policy["analysis"]["worst_rolling_window"]
    for start in range(max(0, len(routing) - width + 1)):
        window = routing[start:start + width]
        rolling.append(dict(start_evidence_sequence=start + 1, n=len(window),
            correct=sum(row["correctness"][row["selected_specialist"]]
                        for row in window)))
    request_intents = [row for row in calls if row["kind"] == "REQUEST_INTENT"]
    hidden_prompt_checks = 0
    for row in request_intents:
        if "regime" in json.dumps(row["record"]["request"], sort_keys=True).lower():
            raise RoutingError("hidden regime found during final prompt audit")
        hidden_prompt_checks += 1
    by_event_identity = {tuple(event["receipt_identity"]): event for event in events}
    expected_attempts_by_runtime = {1: 12, 2: 6, 3: 6, 4: 12}
    attempts_by_runtime = Counter()
    artifact_verifications = {}
    request_decisions = set()
    for call in request_intents:
        call_id = call["record"].get("call_id", "")
        parts = call_id.split(":")
        epoch_token = next((part for part in parts if part.startswith("e") and
                            part[1:].isdigit()), None)
        decision_token = next((part for part in parts if part.startswith("d") and
                               part[1:].isdigit()), None)
        if epoch_token is None or decision_token is None:
            continue
        epoch = int(epoch_token[1:]); runtime = epoch - 2000
        if runtime < 1 or runtime > checkpoint["runtime_index"]:
            continue
        request_decisions.add((runtime, decision_token))
        if call["record"]["role"].startswith("routed-consequence:"):
            specialist = call["record"]["role"].split(":", 1)[1]
            actual = call["record"].get("model_generation_identity", {}).get(
                "artifact_sha256")
            expected = route.registry["specialists"][specialist]["artifact_sha256"]
            artifact_verifications.setdefault(str(runtime), {}).setdefault(
                specialist, set()).add(actual == expected)
    for runtime, _ in request_decisions:
        attempts_by_runtime[runtime] += 1
    if checkpoint["attempted_decisions"] != 36 or \
            dict(attempts_by_runtime) != expected_attempts_by_runtime:
        raise RoutingError("executed campaign does not match frozen attempt schedule: "
                           f"checkpoint={checkpoint['attempted_decisions']}, "
                           f"by_runtime={dict(attempts_by_runtime)}")
    artifact_verifications = {runtime: {specialist: values == {True}
        for specialist, values in checks.items()}
        for runtime, checks in artifact_verifications.items()}
    artifacts_reverified = all(set(checks) == {"G2", "G3"} and all(checks.values())
                               for checks in artifact_verifications.values()) and \
        set(artifact_verifications) == {"1", "2", "3", "4"}
    phase_by_runtime = {1: "A1", 2: "B", 3: "B", 4: "A2"}
    roles_by_call = {row["record"]["call_id"]: row["record"]["role"]
                     for row in request_intents}
    invalid_predictions = Counter()
    for row in calls:
        if row["kind"] != "PARSED" or row["record"].get("parsed") is not None:
            continue
        call_id = row["record"].get("call_id", "")
        role = roles_by_call.get(call_id, "")
        if not role.startswith("routed-consequence:"):
            continue
        epoch_token = next((part for part in call_id.split(":")
                            if part.startswith("e") and part[1:].isdigit()), None)
        if epoch_token:
            invalid_predictions[phase_by_runtime[int(epoch_token[1:]) - 2000]] += 1
    for name in phase_reports:
        phase_reports[name]["invalid_specialist_predictions"] = invalid_predictions[name]
    b_rows = [(row, by_event_identity[tuple(row["receipt_identity"])]) for row in routing
              if by_event_identity[tuple(row["receipt_identity"])][
                  "external_regime_version"] == "B"]
    b_runtimes = sorted({event["source_scope"]["runtime_index"] for _, event in b_rows})
    continuity = None
    for (prior_row, prior_event), (next_row, next_event) in zip(b_rows, b_rows[1:]):
        if prior_event["source_scope"]["runtime_index"] != \
                next_event["source_scope"]["runtime_index"]:
            continuity = dict(before_restart_selected_after=
                prior_row["selected_specialist_after"],
                after_restart_selected_before=next_row["selected_specialist"],
                preserved=prior_row["selected_specialist_after"] ==
                          next_row["selected_specialist"])
            break
    imported_history_after_b_restart = 0
    if len(b_runtimes) >= 2:
        later_epochs = {event["receipt"]["epoch"] for _, event in b_rows
                        if event["source_scope"]["runtime_index"] == b_runtimes[-1]}
        for call in request_intents:
            call_id = call["record"].get("call_id", "")
            if any(f":e{epoch}:" in call_id for epoch in later_epochs):
                payload = json.loads(call["record"]["request"]["prompt"])
                imported_history_after_b_restart += bool(
                    payload["VERIFIED_CHRONOLOGICAL_HISTORY"])
    total_routed = sum(row["correctness"][row["selected_specialist"]]
                       for row in routing)
    result = dict(status="COMPLETE", schedule=policy["schedule"],
        policy_sha256=file_hash(POLICY_PATH), attempted_decisions=sum(
            row["attempted_decisions"] for row in policy["schedule"]),
        executed_decisions=len(routing), total_model_calls=len(request_intents),
        model_calls_by_role=dict(Counter(row["record"]["role"]
                                         for row in request_intents)),
        phase_metrics=phase_reports,
        overall=dict(routed_correct=total_routed, n=len(routing),
            always_G2_correct=sum(row["correctness"]["G2"] for row in routing),
            always_G3_correct=sum(row["correctness"]["G3"] for row in routing),
            invalid_specialist_predictions=sum(invalid_predictions.values()),
            nonexecuted_attempts=checkpoint["attempted_decisions"] -
                                 checkpoint["completed_steps"],
            worst_rolling_window=(None if not rolling else min(
                rolling, key=lambda row: (row["correct"], row["start_evidence_sequence"])))),
        switches=switches, unnecessary_switches=sum(
            item["future_four_assessment"] != "NOT_ASSESSABLE" and
            item["future_four_assessment"]["unnecessary"] for item in switches),
        switch_delays=delays,
        switch_back_occurred=any(item["from_specialist"] == "G3" and
                                 item["to_specialist"] == "G2" for item in switches),
        final_selected_specialist=route.state["selected_specialist"],
        restart_proof=dict(runtime_indices=sorted({event["source_scope"][
            "runtime_index"] for event in events}), B_runtime_indices=b_runtimes,
            source_identities=sorted({event["source_scope"]["source_identity"]
                                      for event in events}),
            router_selection_continuity=continuity,
            imported_history_requests_after_B_restart=
                imported_history_after_b_restart,
            attempts_by_runtime=dict(attempts_by_runtime),
            artifact_verifications_by_runtime=artifact_verifications,
            specialist_artifacts_reverified_on_every_runtime=artifacts_reverified),
        contradiction_trace=contradiction_trace,
        hidden_regime_prompt_checks=hidden_prompt_checks,
        global_lifecycle_status=dict(G2="ACTIVE", G3="REJECTED"),
        routing_eligibility=dict(G2="ROUTABLE_SPECIALIST",
                                 G3="ROUTABLE_SPECIALIST"),
        no_weight_updates=True,
        comparison_scope=("always-specialist scores use only actions actually executed; "
                          "no counterfactual action/outcome claim"))
    atomic_json(output, result)
    return result
