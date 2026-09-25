"""Model-backed, restartable Horus v0.1 application runtime.

Durable history is authenticated by an application-owned local HMAC key.  A
restart creates a fresh receipt source and framework epoch.  Prior records are
imported as read-only proposal evidence; they are never reconstructed as live
receipt capabilities and cannot authorize new Memory publication.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import fcntl
from hashlib import sha256
from hmac import compare_digest, new as new_hmac
import json
import os
from pathlib import Path
import secrets
from typing import Any
import urllib.request

from experiments.base_framework_v0.framework import ACTION_ORDER, Prediction
from experiments.cross_episode_initialization_boundary_v1.boundary import (
    EpisodeWorld, Publication)
from experiments.map_consequence_only_isolation_v0.protocol import (
    SYSTEMS as CONSEQUENCE_SYSTEMS, parse as parse_consequence)
from experiments.map_output_schema_isolation_v0.protocol import SYSTEMS as SCHEMA_SYSTEMS
from experiments.model_map_proposal_v0.adapter import MODEL, parse as parse_joint
from experiments.model_proposal_role_composition_v2.protocol import OPTIONS
from experiments.realized_event_grounding_v0.framework import evidence
from experiments.realized_event_grounding_v0.receipt import ExternalExecutionBoundary
from experiments.state_recovery_authorizer_status_binding_v1.framework import StatusBoundFramework

from .core import (BoundPredictionMap, GroundedObservation, MAPPING, MapForecast,
                   MechanicalExplorer, digest, unwrap_map)


JOINT_SYSTEM = SCHEMA_SYSTEMS["J"]
CONSEQUENCE_SYSTEM = CONSEQUENCE_SYSTEMS["C"]
FORMAT_VERSION = 1


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _plain(value: Any) -> Any:
    return json.loads(json.dumps(value, default=lambda item: item.value))


def _atomic_write(path: Path, value: Any, mode: int = 0o600) -> None:
    temporary = path.with_name(path.name + ".tmp")
    data = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)
    try:
        os.write(descriptor, data)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


class SessionError(RuntimeError):
    pass


class SessionStore:
    """Signed checkpoint plus HMAC-chained append-only session streams.

    The key and files share a local trust domain.  This detects accidental or
    unkeyed alteration; it is not protection from an attacker able to replace
    both the key and the session.
    """
    STREAMS = {
        "events": "events.jsonl",
        "calls": "model-calls.private.jsonl",
        "training": "training-records.jsonl",
    }

    def __init__(self, directory: Path, resume: bool):
        self.directory = directory.resolve()
        self.directory.mkdir(parents=True, exist_ok=True)
        os.chmod(self.directory, 0o700)
        self._lock_file = (self.directory / ".lock").open("a+")
        try:
            fcntl.flock(self._lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise SessionError("session is already open by another process") from exc
        self.key_path = self.directory / "authority.key"
        self.checkpoint_path = self.directory / "checkpoint.json"
        if resume:
            if not self.key_path.exists() or not self.checkpoint_path.exists():
                raise SessionError("resume requires an existing key and checkpoint")
            self._key = bytes.fromhex(self.key_path.read_text().strip())
            if len(self._key) != 32:
                raise SessionError("invalid session authority key")
            self.checkpoint = self._read_checkpoint()
        else:
            if self.key_path.exists() or self.checkpoint_path.exists():
                raise SessionError("session already exists; use --resume")
            self._key = secrets.token_bytes(32)
            descriptor = os.open(self.key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            try:
                os.write(descriptor, (self._key.hex() + "\n").encode())
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
            for filename in self.STREAMS.values():
                descriptor = os.open(self.directory / filename,
                                     os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                os.close(descriptor)
            self.checkpoint = dict(
                version=FORMAT_VERSION, session_id=secrets.token_hex(16),
                created_at=_now(), updated_at=_now(), current_state=1,
                runtime_index=0, current_epoch=2000, current_source_identity=None,
                next_transaction_id=1, completed_steps=0, attempted_decisions=0,
                streams={name: {"count": 0, "head_sha256": None}
                         for name in self.STREAMS})
            self._write_checkpoint()
        self.records = {name: self._read_stream(name) for name in self.STREAMS}
        self._validate_checkpoint_heads()
        self._validate_events()

    def close(self) -> None:
        if not self._lock_file.closed:
            fcntl.flock(self._lock_file, fcntl.LOCK_UN)
            self._lock_file.close()

    def __del__(self):
        lock = getattr(self, "_lock_file", None)
        if lock is not None and not lock.closed:
            self.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def _mac(self, value: Any) -> str:
        return new_hmac(self._key, _canonical(value).encode(), "sha256").hexdigest()

    def _write_checkpoint(self) -> None:
        document = {"payload": self.checkpoint, "hmac_sha256": self._mac(self.checkpoint)}
        _atomic_write(self.checkpoint_path, document)

    def _read_checkpoint(self) -> dict:
        try:
            document = json.loads(self.checkpoint_path.read_text())
            payload = document["payload"]
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise SessionError("invalid checkpoint document") from exc
        if not compare_digest(self._mac(payload), document.get("hmac_sha256", "")):
            raise SessionError("checkpoint authentication failed")
        if payload.get("version") != FORMAT_VERSION:
            raise SessionError("unsupported checkpoint version")
        return payload

    def _read_stream(self, name: str) -> list[dict]:
        rows, previous = [], None
        path = self.directory / self.STREAMS[name]
        try:
            lines = path.read_text().splitlines()
        except OSError as exc:
            raise SessionError(f"missing {name} stream") from exc
        for index, line in enumerate(lines, 1):
            try:
                envelope = json.loads(line)
                signed = {k: envelope[k] for k in
                          ("sequence", "previous_sha256", "kind", "record")}
            except (ValueError, KeyError, TypeError) as exc:
                raise SessionError(f"invalid {name} stream record") from exc
            if envelope["sequence"] != index or envelope["previous_sha256"] != previous:
                raise SessionError(f"broken {name} sequence/hash chain")
            if not compare_digest(self._mac(signed), envelope.get("hmac_sha256", "")):
                raise SessionError(f"{name} record authentication failed")
            previous = sha256(_canonical(envelope).encode()).hexdigest()
            rows.append(envelope)
        return rows

    def _validate_checkpoint_heads(self) -> None:
        expected = set(self.STREAMS)
        if set(self.checkpoint.get("streams", {})) != expected:
            raise SessionError("checkpoint stream registry missing")
        for name, rows in self.records.items():
            registered = self.checkpoint["streams"][name]
            head = None if not rows else sha256(_canonical(rows[-1]).encode()).hexdigest()
            if registered != {"count": len(rows), "head_sha256": head}:
                raise SessionError(f"checkpoint/{name} stream mismatch; fail-closed recovery")

    def _validate_events(self) -> None:
        identities = set()
        for envelope in self.records["events"]:
            row = envelope["record"]
            required = {"receipt", "receipt_identity", "receipt_provenance_sha256",
                        "authorization_status", "memory_record", "source_scope"}
            if not required.issubset(row):
                raise SessionError("event missing provenance")
            receipt = row["receipt"]
            identity = tuple(row["receipt_identity"])
            expected = (receipt.get("source_identity"), receipt.get("event_id"),
                        receipt.get("epoch"), receipt.get("transaction_id"))
            if identity != expected or digest(receipt) != row["receipt_provenance_sha256"]:
                raise SessionError("event receipt identity/provenance mismatch")
            if identity in identities:
                raise SessionError("duplicate/replayed event identity")
            identities.add(identity)
            if row["authorization_status"] != "AUTHORIZED":
                raise SessionError("unauthorized event in durable Memory")

    def append(self, name: str, kind: str, record: dict) -> dict:
        rows = self.records[name]
        previous = None if not rows else sha256(_canonical(rows[-1]).encode()).hexdigest()
        record = {**record, "recorded_at": record.get("recorded_at", _now())}
        signed = dict(sequence=len(rows) + 1, previous_sha256=previous,
                      kind=kind, record=_plain(record))
        envelope = {**signed, "hmac_sha256": self._mac(signed)}
        path = self.directory / self.STREAMS[name]
        with path.open("a") as stream:
            stream.write(_canonical(envelope) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        rows.append(envelope)
        self.checkpoint["streams"][name] = {
            "count": len(rows),
            "head_sha256": sha256(_canonical(envelope).encode()).hexdigest(),
        }
        return envelope

    def save(self, *, state: int, next_transaction_id: int,
             completed_step: bool = False, attempted_decision: bool = False) -> None:
        self.checkpoint["current_state"] = state
        self.checkpoint["next_transaction_id"] = next_transaction_id
        self.checkpoint["completed_steps"] += int(completed_step)
        self.checkpoint["attempted_decisions"] += int(attempted_decision)
        self.checkpoint["updated_at"] = _now()
        self._write_checkpoint()

    def begin_runtime(self) -> tuple[int, str]:
        self.checkpoint["runtime_index"] += 1
        self.checkpoint["current_epoch"] += 1
        source = (f"HORUS:{self.checkpoint['session_id']}:runtime:"
                  f"{self.checkpoint['runtime_index']}:{secrets.token_hex(8)}")
        self.checkpoint["current_source_identity"] = source
        self.checkpoint["next_transaction_id"] = 1
        self.checkpoint["updated_at"] = _now()
        self._write_checkpoint()
        return self.checkpoint["current_epoch"], source

    def imported_history(self) -> list[dict]:
        """Return detached, verified values; never reconstructed receipt objects."""
        self._validate_events()
        return [_plain(row["record"]) for row in self.records["events"]]


class _ExecutionPort:
    def __init__(self, current):
        self._current = current

    def execute(self, *args):
        return self._current().world.execute(*args)


class LiveController:
    """Fresh per-process controller using the unchanged receipt/authority chain."""
    def __init__(self, source_identity: str, state: int, epoch: int):
        self._source_identity = source_identity
        self._active = None
        self._source = ExternalExecutionBoundary(_ExecutionPort(lambda: self._active),
                                                 source_identity)
        self._registered_source = self._source
        self._active = Publication(EpisodeWorld(state),
            StatusBoundFramework(self._source.reader(), state, epoch))

    def begin_step(self, action):
        return self._active.framework.begin_step(forced_action=action)

    def execute_pending(self):
        pending = self._active.framework.inner.pending
        if pending is None:
            raise RuntimeError("no pending transaction")
        return self._source.execute(pending.epoch, pending.transaction_id, pending.action)

    def submit_package(self, package):
        return self._active.framework.submit_package(package)

    def release(self, receipt):
        self._source.release(receipt)


class DurableHistoryReader:
    """Audit current live state and project signed pre/post-restart history."""
    def __init__(self, controller: LiveController, store: SessionStore,
                 authentic: dict, executions: dict):
        self.controller, self.store = controller, store
        self.authentic, self.executions = authentic, executions

    def capture(self) -> dict:
        framework = self.controller._active.framework
        framework.assert_bounds()
        core = framework.inner
        if core.pending is not None or self.controller._source.reader().current() is not None:
            raise SessionError("cannot project an in-flight event")
        if not core.continuation_authorized or not core.map.current.valid:
            raise SessionError("no authorized current state")
        # Current-runtime protected rings must still retain original receipt objects.
        for record, package in zip(core.memory.records, framework.packages):
            receipt = package.receipt
            if self.authentic.get(receipt.identity()) is not receipt:
                raise SessionError("current receipt object substitution")
            actual = self.executions.get(receipt.identity())
            if actual is None or receipt.binding()[:6] != (
                    actual["epoch"], actual["transaction_id"], actual["pre_state"],
                    actual["action"], actual["next_state"], actual["consequence"]):
                raise SessionError("current execution/receipt mismatch")
            if (record.epoch, record.transaction_id, record.pre_state, record.action,
                    record.next_state, record.consequence) != receipt.binding()[:6]:
                raise SessionError("current protected Memory/receipt mismatch")
        history = self.store.imported_history()
        provenance = [dict(
            receipt_identity=row["receipt_identity"],
            origin_runtime_index=row["source_scope"]["runtime_index"],
            restoration_status=("PRE_RESTART_IMPORTED"
                if row["source_scope"]["runtime_index"] <
                   self.store.checkpoint["runtime_index"]
                else "CURRENT_RUNTIME_DURABLE")) for row in history]
        state = core.map.current.state
        inputs = {}
        for action in ACTION_ORDER:
            alias = next(key for key, value in MAPPING.items() if value == action)
            rows = [dict(epoch=r["receipt"]["epoch"],
                         transaction_id=r["receipt"]["transaction_id"],
                         surface_action=alias,
                         next_state=r["receipt"]["next_state"],
                         consequence=r["receipt"]["realized_consequence"])
                    for r in history
                    if r["receipt"]["pre_state"] == state and
                       r["receipt"]["action"] == action]
            inputs[action] = dict(state=state, target_action=alias,
                VERIFIED_CHRONOLOGICAL_HISTORY=rows)
        memory_ref = self.store.checkpoint["streams"]["events"]
        return dict(state=state, epoch=core.epoch,
                    transaction_id=core.next_transaction_id,
                    source_identity=self.controller._source_identity,
                    authenticated_history_reference=memory_ref,
                    authenticated_history_provenance=provenance,
                    memory_sha256=digest(history), map_inputs=inputs)


class ModelClient:
    """One-attempt local model transport; callers durably register first."""
    model_id = MODEL
    def __init__(self, endpoint: str = "http://127.0.0.1:11434"):
        self.endpoint = endpoint.rstrip("/")
        self.requests = 0

    def generate(self, request_body: dict) -> dict:
        self.requests += 1
        request = urllib.request.Request(self.endpoint + "/api/generate",
            data=json.dumps(request_body).encode(),
            headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=600) as response:
                value = json.load(response)
            if value.get("done") is not True or type(value.get("response")) is not str:
                raise ValueError("incomplete model response")
            return dict(raw_output=value["response"], transport_error=None,
                response_metadata={key: value[key] for key in
                    ("model", "created_at", "done", "total_duration", "load_duration",
                     "prompt_eval_count", "prompt_eval_duration", "eval_count",
                     "eval_duration") if key in value})
        except Exception as exc:
            return dict(raw_output=None, transport_error=type(exc).__name__,
                        response_metadata={})


@dataclass(frozen=True)
class ForecastEvidence:
    forecast: MapForecast
    joint_response: dict
    consequence_response: dict
    joint_parsed: dict | None
    consequence_parsed: dict | None
    request_hashes: dict


class LiveSplitMap:
    def __init__(self, store: SessionStore, joint_client: ModelClient,
                 consequence_client=None):
        self.store, self.joint_client = store, joint_client
        self.consequence_client = consequence_client or joint_client

    def _request(self, system: str, prompt: str, model: str) -> dict:
        return dict(model=model, system=system, prompt=prompt, stream=False,
                    options=dict(OPTIONS["Map"]))

    def forecast(self, capture: dict, action: str, decision_id: str) -> ForecastEvidence:
        payload = capture["map_inputs"][action]
        prompt = _canonical(payload)
        joint = self._request(JOINT_SYSTEM, prompt,
                              getattr(self.joint_client, "model_id", MODEL))
        consequence = self._request(CONSEQUENCE_SYSTEM, prompt,
            getattr(self.consequence_client, "model_id", MODEL))
        consequence_identity = getattr(
            self.consequence_client, "horus_model_identity", None)
        if consequence_identity is not None:
            consequence["horus_model_identity"] = _plain(consequence_identity)
        pair_id = f"{decision_id}:{action}"
        # Both complete requests are frozen durably before either response exists.
        self.store.append("calls", "REQUEST_INTENT", dict(
            call_id=pair_id + ":J", role="joint-next-state", request=joint,
            request_sha256=digest(joint)))
        self.store.append("calls", "REQUEST_INTENT", dict(
            call_id=pair_id + ":C", role="independent-consequence", request=consequence,
            request_sha256=digest(consequence), independent_of_joint_response=True,
            model_generation_identity=consequence_identity))
        jr = self.joint_client.generate(joint)
        self.store.append("calls", "RESPONSE", dict(call_id=pair_id + ":J", response=jr,
            response_sha256=digest(jr)))
        cr = self.consequence_client.generate(consequence)
        self.store.append("calls", "RESPONSE", dict(call_id=pair_id + ":C", response=cr,
            response_sha256=digest(cr)))
        jp = cp = None
        jf = cf = None
        if jr["transport_error"] is None:
            try:
                jp = parse_joint(jr["raw_output"])
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
                jf = type(exc).__name__
        else:
            jf = jr["transport_error"]
        if cr["transport_error"] is None:
            try:
                cp = parse_consequence(cr["raw_output"], "C")
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
                cf = type(exc).__name__
        else:
            cf = cr["transport_error"]
        # Parsed values/failures are durable before either value is reconciled.
        self.store.append("calls", "PARSED", dict(call_id=pair_id + ":J",
            parsed=jp, parse_error=jf))
        self.store.append("calls", "PARSED", dict(call_id=pair_id + ":C",
            parsed=cp, parse_error=cf))
        valid = jp is not None and cp is not None
        history = tuple(GroundedObservation(**row)
                        for row in payload["VERIFIED_CHRONOLOGICAL_HISTORY"])
        forecast = MapForecast(action, payload["target_action"],
            None if jp is None else jp["next_state"],
            None if cp is None else cp["consequence"], not valid,
            None if valid else f"INVALID_COMPONENT:J={jf};C={cf}", len(history),
            dict(state=capture["state"], action=action,
                 action_alias=payload["target_action"], epoch=capture["epoch"],
                 transaction_id=capture["transaction_id"],
                 authenticated_history=[asdict(row) for row in history],
                 memory_sha256=capture["memory_sha256"],
                 authenticated_history_reference=capture["authenticated_history_reference"]))
        return ForecastEvidence(forecast, jr, cr, jp, cp,
            {"joint": digest(joint), "consequence": digest(consequence)})

    def forecasts(self, capture: dict, decision_id: str) -> tuple[ForecastEvidence, ...]:
        return tuple(self.forecast(capture, action, decision_id) for action in ACTION_ORDER)


class LiveRuntime:
    def __init__(self, store: SessionStore, client: ModelClient,
                 consequence_client=None):
        self.store, self.client = store, client
        self.consequence_client = consequence_client or client
        epoch, source = store.begin_runtime()
        self.controller = LiveController(source, store.checkpoint["current_state"], epoch)
        self.authentic, self.executions = {}, {}
        self.reader = DurableHistoryReader(self.controller, store,
                                           self.authentic, self.executions)
        self.map = LiveSplitMap(store, client, self.consequence_client)
        self.explorer = MechanicalExplorer()

    def step(self) -> dict:
        capture = self.reader.capture()
        decision_number = self.store.checkpoint["attempted_decisions"] + 1
        decision_id = (f"{self.store.checkpoint['session_id']}:"
                       f"e{capture['epoch']}:d{decision_number}")
        evidence_rows = self.map.forecasts(capture, decision_id)
        forecasts = tuple(row.forecast for row in evidence_rows)
        choice = self.explorer.choose(forecasts)
        if choice.abstained:
            self.store.save(state=capture["state"],
                next_transaction_id=capture["transaction_id"], attempted_decision=True)
            return dict(step=self.store.checkpoint["completed_steps"] + 1,
                decision_id=decision_id, prior_authenticated_observations_used={
                    f.action: f.history_count for f in forecasts},
                map_forecasts=[asdict(f) for f in forecasts], explorer=asdict(choice),
                model_calls=2 * len(forecasts), status="ABSTAINED",
                behavioral_change_attribution=None)
        selected_index = next(i for i, value in enumerate(forecasts)
                              if value.action == choice.action)
        selected = forecasts[selected_index]
        selected_evidence = evidence_rows[selected_index]
        prediction = Prediction(capture["epoch"], capture["transaction_id"],
            capture["state"], selected.action, selected.next_state,
            selected.consequence)
        core = self.controller._active.framework.inner
        core.map = BoundPredictionMap(unwrap_map(core.map), prediction)
        pending = self.controller.begin_step(selected.action)
        if _plain(asdict(pending.prediction)) != _plain(asdict(prediction)):
            raise RuntimeError("reconciled prediction was not latched")
        if self.controller._source.reader().current() is not None:
            raise RuntimeError("receipt existed before execution")
        receipt = self.controller.execute_pending()
        actual = _plain(asdict(self.controller._active.world.last_actual))
        self.authentic[receipt.identity()] = receipt
        self.executions[receipt.identity()] = actual
        result = self.controller.submit_package(evidence(receipt))
        if not result.committed or not result.continued:
            self.controller.release(receipt)
            raise RuntimeError(f"grounded publication rejected: {result.reason}")
        # submit_package stages and replaces the framework core atomically.
        core = self.controller._active.framework.inner
        record = core.memory.records[-1]
        package = self.controller._active.framework.packages[-1]
        if package.receipt is not receipt:
            raise RuntimeError("published receipt object was substituted")
        receipt_value = _plain(asdict(receipt))
        memory_value = _plain(asdict(record))
        event = dict(session_id=self.store.checkpoint["session_id"],
            recorded_at=_now(), receipt=receipt_value,
            receipt_identity=list(receipt.identity()),
            receipt_provenance_sha256=digest(receipt_value),
            authorization_status=result.status.value,
            memory_record=memory_value,
            source_scope=dict(runtime_index=self.store.checkpoint["runtime_index"],
                              imported_after_restart=False,
                              source_identity=receipt.source_identity))
        event_envelope = self.store.append("events", "AUTHORIZED_REALIZED_EVENT", event)
        event_head = sha256(_canonical(event_envelope).encode()).hexdigest()
        training = dict(session_id=self.store.checkpoint["session_id"],
            epoch=receipt.epoch, transaction_id=receipt.transaction_id,
            decision_id=decision_id, order=self.store.checkpoint["completed_steps"] + 1,
            timestamp=event["recorded_at"],
            input_context_hash=digest(selected.input_context),
            authenticated_history_reference=capture["authenticated_history_reference"],
            authenticated_history_provenance_sha256=
                digest(capture["authenticated_history_provenance"]),
            chosen_action=selected.action,
            joint_model_response=selected_evidence.joint_parsed,
            joint_raw_response_sha256=digest(selected_evidence.joint_response),
            predicted_next_state=selected.next_state,
            diagnostic_joint_consequence=(None if selected_evidence.joint_parsed is None
                                          else selected_evidence.joint_parsed["consequence"]),
            consequence_model_response=selected_evidence.consequence_parsed,
            consequence_raw_response_sha256=digest(selected_evidence.consequence_response),
            predicted_consequence=selected.consequence,
            joint_request_sha256=selected_evidence.request_hashes["joint"],
            consequence_request_sha256=
                selected_evidence.request_hashes["consequence"],
            consequence_model_identity=
                selected_evidence.consequence_response.get("response_metadata", {}).get(
                    "horus_model_identity",
                    getattr(self.consequence_client, "horus_model_identity", None)),
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
            labels=dict(prediction_is_authenticated_target=False,
                        realized_receipt_is_authenticated_target=True))
        self.store.append("training", "AUTHORIZED_TRAINING_EXAMPLE", training)
        self.controller.release(receipt)
        self.store.save(state=receipt.next_state,
            next_transaction_id=core.next_transaction_id,
            completed_step=True, attempted_decision=True)
        counts = {f.action: f.history_count for f in forecasts}
        return dict(step=self.store.checkpoint["completed_steps"],
            decision_id=decision_id, state=capture["state"], epoch=capture["epoch"],
            transaction_id=capture["transaction_id"],
            prior_authenticated_observations_used=counts,
            authenticated_history_reference=capture["authenticated_history_reference"],
            imported_pre_restart_records=sum(
                item["restoration_status"] == "PRE_RESTART_IMPORTED"
                for item in capture["authenticated_history_provenance"]),
            map_forecasts=[asdict(f) for f in forecasts], explorer=asdict(choice),
            execution=actual, receipt=receipt_value,
            prediction_match=training["prediction_match"],
            memory_publication=dict(authorization=result.status.value,
                                    event_sequence=event_envelope["sequence"],
                                    event_head_sha256=event_head),
            model_calls=2 * len(forecasts), status="AUTHORIZED",
            behavioral_change_attribution=None)


def run_live(session: Path, steps: int, resume: bool,
             client: ModelClient | None = None, consequence_client=None) -> dict:
    if type(steps) is not int or steps < 0:
        raise ValueError("steps must be a nonnegative integer")
    with SessionStore(session, resume) as store:
        joint = client or ModelClient()
        consequence = consequence_client or joint
        joint_before = joint.requests
        consequence_before = consequence.requests
        runtime = LiveRuntime(store, joint, consequence)
        rows = []
        for _ in range(steps):
            row = runtime.step()
            rows.append(row)
            if row["status"] == "ABSTAINED":
                break
        role_calls = sum(len(row["map_forecasts"]) for row in rows)
        return dict(mode="live", session_id=store.checkpoint["session_id"],
            session=str(store.directory), resumed=resume,
            runtime_index=store.checkpoint["runtime_index"],
            epoch=store.checkpoint["current_epoch"],
            actual_model_calls=(joint.requests - joint_before +
                (0 if consequence is joint else
                 consequence.requests - consequence_before)),
            joint_model_calls=role_calls, consequence_model_calls=role_calls,
            consequence_model=getattr(consequence, "model_id", MODEL), steps=rows,
            consequence_model_identity=getattr(
                consequence, "horus_model_identity", None),
            checkpoint=_plain(store.checkpoint),
            trust_scope=("local HMAC-authenticated application checkpoint; fresh receipt "
                         "source/framework epoch on every process; no physical, hostile-host, "
                         "or Python-object continuity claim"))
