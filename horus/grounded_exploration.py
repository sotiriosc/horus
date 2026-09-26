"""Production-style mechanical exploration over authenticated relation evidence."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from dataclasses import asdict
import fcntl
from hashlib import sha256
from hmac import compare_digest, new as new_hmac
import json
import os
from pathlib import Path
import secrets
from typing import Any

from experiments.base_framework_v0.framework import ACTION_ORDER, Prediction
from experiments.base_framework_v1.framework import (EPISODE_LIMIT,
                                                      PendingTransaction,
                                                      StepResult)
from experiments.realized_event_grounding_v0.framework import evidence

from .core import (BoundPredictionMap, MapForecast, MechanicalExplorer, digest,
                   unwrap_map)
from .grounded_learning import ROOT, atomic_json, file_hash
from .live import ModelClient, SessionStore, _canonical, _now, _plain
from .relation_routing import (RelationEvidenceStore, RelationGroundedRouter,
                               RelationRoutedRuntime, SPECIALISTS,
                               initialize_relation_routing_registry,
                               load_relation_routing_registry, relation_identity,
                               relation_key, relation_routed_clients)
from .routing import RoutingError


POLICY_PATH = Path(__file__).with_name("grounded_exploration_policy.json")
DEFAULT_SOURCE_REGISTRY = ROOT / "research/learning-stability-v0/registry"
EXPLORATION_VERSION = 1
SEGMENTS = ("A1", "B1", "B2", "A2")
R2_SEGMENTS = ("R2_A1_1", "R2_A1_2", "R2_B1", "R2_B2", "R2_A2_1",
               "R2_A2_2")
PROBLEM_TYPES = ("EXTERNAL_SERVICE_PROBLEM", "INTERNAL_ROUTE_PROBLEM",
                 "UNRESOLVED_RELATION_PROBLEM")


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


def initialize_grounded_exploration_registry(
        root: Path, source_registry: Path = DEFAULT_SOURCE_REGISTRY) -> dict:
    policy = json.loads(POLICY_PATH.read_text())
    relation = initialize_relation_routing_registry(root, source_registry)
    relation_registry = load_relation_routing_registry(root)
    frozen_router = {key: relation_registry["policy"][key] for key in
                     ("window_size", "minimum_shared_scored_events",
                      "switch_lead_correct", "cold_start_specialist")}
    if frozen_router != policy["routing_policy"]:
        raise RoutingError("exploration router differs from frozen relation router")
    actual_specialists = [{key: row[key] for key in
                           ("id", "generation", "artifact_sha256")}
                          for row in relation_registry["payload"]["specialists"]]
    if actual_specialists != policy["specialists"]:
        raise RoutingError("exploration specialist pool differs from policy")
    payload = dict(version=EXPLORATION_VERSION,
        mode="GROUNDED_RELATION_EXPLORATION",
        created_at=_now(), policy_sha256=file_hash(POLICY_PATH),
        relation_registry_payload_sha256=relation_registry["document"]["sha256"],
        relation_identity=policy["relation_identity"],
        lifecycle_status_rewritten=False, weights_modified=False,
        learned_explorer=False, hidden_regime_available=False)
    atomic_json(root / "exploration-registry.json", _document(payload))
    ExplorerConfidenceStore.initialize(root)
    return dict(root=str(root), exploration_registry_sha256=digest(payload),
                relation_registry=relation)


def load_grounded_exploration_registry(root: Path) -> dict:
    root = root.resolve()
    relation = load_relation_routing_registry(root)
    document = _read_document(root / "exploration-registry.json",
                              "exploration registry")
    payload, policy = document["payload"], json.loads(POLICY_PATH.read_text())
    if payload.get("version") != EXPLORATION_VERSION or \
            payload.get("mode") != "GROUNDED_RELATION_EXPLORATION" or \
            payload.get("policy_sha256") != file_hash(POLICY_PATH) or \
            payload.get("relation_registry_payload_sha256") != \
            relation["document"]["sha256"] or \
            payload.get("relation_identity") != ["pre_state", "action"] or \
            payload.get("lifecycle_status_rewritten") is not False or \
            payload.get("weights_modified") is not False or \
            payload.get("learned_explorer") is not False or \
            payload.get("hidden_regime_available") is not False:
        raise RoutingError("exploration registry violates frozen policy")
    return dict(root=root, document=document, payload=payload,
                policy=policy, relation_registry=relation)


class GroundedExplorer:
    """Finite probe-priority policy with a deterministic global probe budget."""
    def __init__(self, policy: dict | None = None):
        self.policy = policy or json.loads(POLICY_PATH.read_text())
        self.mechanical = MechanicalExplorer()

    def relation_metadata(self, *, pre_state: int, action: str,
                          forecast: dict, preview: dict,
                          routing_records: list[dict], confidence_state: dict) -> dict:
        relation = relation_identity(pre_state, action)
        key = relation_key(relation)
        local = [row["record"] if "record" in row else row
                 for row in routing_records
                 if relation_key((row["record"] if "record" in row else row)[
                     "relation"]) == key]
        observations = len(local)
        scores = preview["scores"]
        minimum = self.policy["confidence"][
            "clear_preference_minimum_observations"]
        lead_required = self.policy["confidence"]["clear_preference_lead_correct"]
        lead = abs(scores["G2"]["correct"] - scores["G3"]["correct"])
        clear = scores["G2"]["total"] >= minimum and lead >= lead_required
        disagree = forecast["G2_consequence"] != forecast["G3_consequence"]
        last = confidence_state["last_execution_by_relation"].get(key)
        completed = confidence_state["authorized_decisions"]
        age = None if last is None else completed - last["authorized_decision"]
        contradiction = confidence_state["unresolved_contradictions"].get(key)
        reasons = []
        if contradiction is not None:
            reasons.append("PROBE_CONTRADICTION")
        if observations == 0:
            reasons.append("PROBE_UNTRIED")
        if disagree and not clear:
            reasons.append("PROBE_DISAGREEMENT")
        if age is not None and age >= self.policy["confidence"][
                "stale_after_completed_decisions"]:
            reasons.append("PROBE_STALE")
        return dict(relation=relation, authenticated_observations=observations,
            most_recent_observation_sequence=(None if not local else
                                              local[-1]["evidence_sequence"]),
            recent_realized_consequences=[row["realized_consequence"]
                                          for row in local[-6:]],
            recent_correctness={specialist: [bool(row["correctness"][specialist])
                for row in local[-6:]] for specialist in SPECIALISTS},
            local_scores=deepcopy(scores),
            selected_specialist=preview["selected_specialist"],
            specialists_disagree=disagree,
            clear_local_preference=clear,
            observations_since_last_execution=age,
            unresolved_recent_contradiction=deepcopy(contradiction),
            qualifying_probe_reasons=reasons)

    def derive(self, *, pre_state: int, forecasts: dict,
               routed_forecasts: tuple, previews: dict,
               routing_records: list[dict], confidence_state: dict,
               all_predictions_valid: bool) -> dict:
        metadata = {action: self.relation_metadata(pre_state=pre_state,
            action=action, forecast=forecasts[action], preview=previews[action],
            routing_records=routing_records, confidence_state=confidence_state)
            for action in ACTION_ORDER}
        coverage = dict(state=pre_state, legal_relations=len(ACTION_ORDER),
            relations_with_authenticated_evidence=sum(
                row["authenticated_observations"] > 0 for row in metadata.values()),
            relations_recently_grounded=sum(
                row["authenticated_observations"] > 0 and
                row["observations_since_last_execution"] is not None and
                row["observations_since_last_execution"] < self.policy[
                    "confidence"]["stale_after_completed_decisions"] and
                row["unresolved_recent_contradiction"] is None
                for row in metadata.values()),
            relations_unresolved=sum(bool(row["qualifying_probe_reasons"])
                                     for row in metadata.values()))
        next_sequence = confidence_state["attempted_decisions"] + 1
        next_authorized = confidence_state["authorized_decisions"] + 1
        last_probe = confidence_state["last_probe_authorized_decision"]
        budget_available = last_probe is None or \
            next_authorized - last_probe >= self.policy["probe_budget"][
                "minimum_decision_distance"]
        if not all_predictions_valid:
            return dict(decision_sequence=next_sequence, mode="ABSTAIN",
                action=None, reason="INVALID_MAP_COMPONENT", abstained=True,
                probe_budget_available=budget_available,
                relation_confidence=metadata, coverage=coverage)
        candidates = []
        priority = self.policy["probe_budget"]["priority"]
        for action, row in metadata.items():
            if not row["qualifying_probe_reasons"]:
                continue
            reason = min(row["qualifying_probe_reasons"], key=priority.index)
            last = confidence_state["last_execution_by_relation"].get(
                relation_key(row["relation"]), {})
            candidates.append((priority.index(reason),
                               last.get("authorized_decision", -1),
                               ACTION_ORDER.index(action), action, reason))
        if budget_available and candidates:
            _, _, _, action, reason = min(candidates)
            return dict(decision_sequence=next_sequence, mode="PROBE",
                action=action, reason=reason, abstained=False,
                probe_budget_available=True, relation_confidence=metadata,
                coverage=coverage)
        base = self.mechanical.choose(routed_forecasts)
        reason = ("UNIQUE_ROUTED_MAXIMUM" if base.reason == "UNIQUE_MAXIMUM"
                  else f"EXPLOIT_{base.reason}")
        return dict(decision_sequence=next_sequence, mode="EXPLOIT",
            action=base.action, reason=reason, abstained=base.abstained,
            probe_budget_available=budget_available,
            qualifying_probe_blocked_by_budget=bool(candidates and not budget_available),
            relation_confidence=metadata, coverage=coverage)


class ExplorerConfidenceStore:
    """Authenticated pre-execution decisions and reconstructible confidence state."""
    KEY = "exploration-authority.key"
    STATE = "exploration-state.json"
    STREAM = "exploration-decisions.jsonl"

    @staticmethod
    def initialize(root: Path) -> None:
        root = root.resolve()
        for name in (ExplorerConfidenceStore.KEY, ExplorerConfidenceStore.STATE,
                     ExplorerConfidenceStore.STREAM):
            if (root / name).exists():
                raise RoutingError("exploration confidence store already exists")
        key = secrets.token_bytes(32)
        descriptor = os.open(root / ExplorerConfidenceStore.KEY,
                             os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            os.write(descriptor, (key.hex() + "\n").encode()); os.fsync(descriptor)
        finally:
            os.close(descriptor)
        (root / ExplorerConfidenceStore.STREAM).touch(mode=0o600)
        state = dict(version=EXPLORATION_VERSION, session_id=None,
            attempted_decisions=0, authorized_decisions=0,
            last_probe_decision_sequence=None, last_probe_authorized_decision=None,
            last_execution_by_relation={},
            unresolved_contradictions={}, pending_decision=None,
            stream_count=0, stream_head_sha256=None, updated_at=_now())
        ExplorerConfidenceStore._write_state_file(root, key, state)

    @staticmethod
    def _write_state_file(root: Path, key: bytes, state: dict) -> None:
        document = {"payload": state, "hmac_sha256": new_hmac(
            key, _canonical(state).encode(), "sha256").hexdigest()}
        temporary = root / (ExplorerConfidenceStore.STATE + ".tmp")
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            os.write(descriptor, (json.dumps(document, indent=2, sort_keys=True) +
                                  "\n").encode()); os.fsync(descriptor)
        finally:
            os.close(descriptor)
        os.replace(temporary, root / ExplorerConfidenceStore.STATE)

    def __init__(self, root: Path):
        self.registry = load_grounded_exploration_registry(root)
        self.root = self.registry["root"]
        self._lock = (self.root / ".exploration.lock").open("a+")
        try:
            fcntl.flock(self._lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RoutingError("exploration confidence store is already open") from exc
        try:
            self._key = bytes.fromhex((self.root / self.KEY).read_text().strip())
        except (OSError, ValueError) as exc:
            self.close(); raise RoutingError("invalid exploration authority key") from exc
        if len(self._key) != 32:
            self.close(); raise RoutingError("invalid exploration authority key")
        try:
            self.state = self._read_state()
            self.records = self._read_stream()
            self.explorer = GroundedExplorer(self.registry["policy"])
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
            raise RoutingError("invalid exploration state") from exc
        if not compare_digest(self._mac(payload), document.get("hmac_sha256", "")):
            raise RoutingError("exploration state authentication failed")
        return payload

    def _read_stream(self) -> list[dict]:
        rows, previous = [], None
        try:
            lines = (self.root / self.STREAM).read_text().splitlines()
        except OSError as exc:
            raise RoutingError("missing exploration decision stream") from exc
        for sequence, line in enumerate(lines, 1):
            try:
                envelope = json.loads(line)
                signed = {key: envelope[key] for key in
                          ("sequence", "previous_sha256", "kind", "record")}
            except (ValueError, KeyError, TypeError) as exc:
                raise RoutingError("invalid exploration decision record") from exc
            if envelope["sequence"] != sequence or \
                    envelope["previous_sha256"] != previous or \
                    not compare_digest(self._mac(signed),
                                       envelope.get("hmac_sha256", "")):
                raise RoutingError("exploration decision chain authentication failed")
            previous = sha256(_canonical(envelope).encode()).hexdigest()
            rows.append(envelope)
        return rows

    def _append(self, kind: str, record: dict) -> dict:
        previous = None if not self.records else sha256(
            _canonical(self.records[-1]).encode()).hexdigest()
        record = {**record, "recorded_at": record.get("recorded_at", _now())}
        signed = dict(sequence=len(self.records) + 1, previous_sha256=previous,
                      kind=kind, record=_plain(record))
        envelope = {**signed, "hmac_sha256": self._mac(signed)}
        with (self.root / self.STREAM).open("a") as stream:
            stream.write(_canonical(envelope) + "\n"); stream.flush(); os.fsync(stream.fileno())
        self.records.append(envelope)
        self.state["stream_count"] = len(self.records)
        self.state["stream_head_sha256"] = sha256(
            _canonical(envelope).encode()).hexdigest()
        return envelope

    def _write_state(self) -> None:
        self.state["updated_at"] = _now()
        self._write_state_file(self.root, self._key, self.state)

    @staticmethod
    def _apply_completion(replay: dict, freeze: dict, completion: dict) -> None:
        if completion["decision_sequence"] != freeze["decision_sequence"]:
            raise RoutingError("exploration completion identity mismatch")
        replay["attempted_decisions"] += 1
        if completion["status"] in ("ABSTAINED", "FRAMEWORK_REJECTED"):
            return
        if completion["status"] != "AUTHORIZED":
            raise RoutingError("invalid exploration completion status")
        replay["authorized_decisions"] += 1
        relation = completion["relation"]
        key = relation_key(relation)
        prior = replay.setdefault("outcomes", {}).setdefault(key, [])
        threshold = completion["contradiction_baseline_required"]
        contradiction_started = len(prior) >= threshold and \
            len(set(prior[-threshold:])) == 1 and \
            prior[-1] != completion["realized_consequence"]
        if contradiction_started != completion["contradiction_started"]:
            raise RoutingError("contradiction derivation does not replay")
        if contradiction_started:
            replay["unresolved_contradictions"][key] = dict(
                relation=relation,
                baseline_consequence=prior[-1],
                contradictory_consequence=completion["realized_consequence"],
                detected_decision_sequence=completion["decision_sequence"],
                detected_routing_evidence_sequence=completion[
                    "routing_evidence_sequence"])
        prior.append(completion["realized_consequence"])
        scores = completion["router_score_after"]
        qualifying_lead = scores["G2"]["total"] >= completion[
            "clear_preference_minimum_observations"] and abs(
                scores["G2"]["correct"] - scores["G3"]["correct"]) >= \
            completion["clear_preference_lead_correct"]
        if qualifying_lead != completion["contradiction_resolved"]:
            raise RoutingError("contradiction resolution does not replay")
        if qualifying_lead:
            replay["unresolved_contradictions"].pop(key, None)
        replay["last_execution_by_relation"][key] = dict(
            relation=relation, decision_sequence=completion["decision_sequence"],
            authorized_decision=replay["authorized_decisions"],
            routing_evidence_sequence=completion["routing_evidence_sequence"])
        if freeze["decision"]["mode"] == "PROBE":
            replay["last_probe_decision_sequence"] = completion["decision_sequence"]
            replay["last_probe_authorized_decision"] = replay["authorized_decisions"]

    def _validate_replay(self) -> None:
        replay = dict(attempted_decisions=0, authorized_decisions=0,
            last_probe_decision_sequence=None, last_probe_authorized_decision=None,
            last_execution_by_relation={},
            unresolved_contradictions={}, outcomes={})
        pending = None
        for envelope in self.records:
            if envelope["kind"] == "EXPLORER_DECISION_FROZEN":
                if pending is not None:
                    raise RoutingError("multiple pending exploration decisions")
                pending = envelope["record"]
                if pending["decision_sequence"] != replay["attempted_decisions"] + 1:
                    raise RoutingError("exploration decision sequence mismatch")
            elif envelope["kind"] == "EXPLORER_DECISION_COMPLETED":
                if pending is None:
                    raise RoutingError("exploration completion lacks frozen decision")
                self._apply_completion(replay, pending, envelope["record"])
                pending = None
            else:
                raise RoutingError("unknown exploration decision record")
        expected = {key: replay[key] for key in
                    ("attempted_decisions", "authorized_decisions",
                     "last_probe_decision_sequence", "last_execution_by_relation",
                     "unresolved_contradictions", "last_probe_authorized_decision")}
        actual = {key: self.state.get(key) for key in expected}
        if self.state.get("version") != EXPLORATION_VERSION or actual != expected or \
                self.state.get("stream_count") != len(self.records) or \
                self.state.get("stream_head_sha256") != (None if not self.records else
                    sha256(_canonical(self.records[-1]).encode()).hexdigest()) or \
                (self.state.get("pending_decision") is None) != (pending is None):
            raise RoutingError("exploration state/decision replay mismatch")
        if pending is not None and self.state["pending_decision"] != dict(
                decision_sequence=pending["decision_sequence"],
                frozen_record_sha256=digest(pending)):
            raise RoutingError("pending exploration decision mismatch")

    def bind_session(self, store: SessionStore) -> None:
        session = self.state.get("session_id")
        actual = store.checkpoint["session_id"]
        if session is None:
            if self.records or self.state["attempted_decisions"]:
                raise RoutingError("unbound exploration store contains decisions")
            self.state["session_id"] = actual; self._write_state()
        elif session != actual:
            raise RoutingError("exploration registry belongs to another session")
        if self.state["attempted_decisions"] != store.checkpoint[
                "attempted_decisions"]:
            raise RoutingError("exploration/session attempt count mismatch")
        if self.state["authorized_decisions"] != len(store.records["events"]):
            raise RoutingError("exploration/session receipt count mismatch")
        if self.state["pending_decision"] is not None:
            raise RoutingError("incomplete pre-execution exploration decision")

    def freeze(self, *, store: SessionStore, routing_store: RelationEvidenceStore,
               pre_state: int, forecasts: dict, routed_forecasts: tuple,
               previews: dict, all_predictions_valid: bool,
               prediction_batch_sequence: int, decision_id: str) -> dict:
        self.bind_session(store)
        decision = self.explorer.derive(pre_state=pre_state, forecasts=forecasts,
            routed_forecasts=routed_forecasts, previews=previews,
            routing_records=routing_store.records, confidence_state=self.state,
            all_predictions_valid=all_predictions_valid)
        if decision["decision_sequence"] != prediction_batch_sequence:
            raise RoutingError("prediction and exploration decision sequences differ")
        record = dict(decision_sequence=decision["decision_sequence"],
            prediction_batch_sequence=prediction_batch_sequence,
            decision_id=decision_id, pre_state=pre_state,
            decision=decision, forecasts=deepcopy(forecasts),
            relation_selections_before={action: previews[action][
                "selected_specialist"] for action in ACTION_ORDER},
            derived_from_authenticated_state=True,
            frozen_before_external_execution=True)
        envelope = self._append("EXPLORER_DECISION_FROZEN", record)
        self.state["pending_decision"] = dict(
            decision_sequence=record["decision_sequence"],
            frozen_record_sha256=digest(envelope["record"]))
        self._write_state()
        return _plain(record)

    def complete_abstained(self, store: SessionStore, frozen: dict) -> dict:
        if frozen["decision"]["action"] is not None or \
                not frozen["decision"]["abstained"]:
            raise RoutingError("only an abstained decision may complete without receipt")
        record = dict(decision_sequence=frozen["decision_sequence"],
            status="ABSTAINED", action=None, receipt_identity=None,
            routing_evidence_sequence=None,
            contradiction_baseline_required=self.registry["policy"][
                "confidence"]["contradiction_baseline_identical_outcomes"],
            contradiction_started=False, router_switch_occurred=False,
            router_score_after={"G2": {"correct": 0, "total": 0},
                                "G3": {"correct": 0, "total": 0}},
            clear_preference_minimum_observations=self.registry["policy"][
                "confidence"]["clear_preference_minimum_observations"],
            clear_preference_lead_correct=self.registry["policy"][
                "confidence"]["clear_preference_lead_correct"],
            contradiction_resolved=False)
        self._append("EXPLORER_DECISION_COMPLETED", record)
        self.state["attempted_decisions"] += 1
        self.state["pending_decision"] = None
        self._write_state(); self.bind_session(store)
        return _plain(record)

    def complete_rejected(self, store: SessionStore, frozen: dict,
                          rejected: StepResult, problem: dict) -> dict:
        if frozen["decision"]["action"] is None or \
                frozen["decision"]["abstained"] or \
                rejected.status.value != "REJECTED" or rejected.executed or \
                rejected.committed or rejected.continued or \
                problem.get("type") != "INTERNAL_ROUTE_PROBLEM" or \
                problem.get("authoritative") is not False:
            raise RoutingError("invalid fail-closed framework rejection")
        record = dict(decision_sequence=frozen["decision_sequence"],
            status="FRAMEWORK_REJECTED", action=frozen["decision"]["action"],
            receipt_identity=None, routing_evidence_sequence=None,
            framework_reason=rejected.reason, problem=deepcopy(problem),
            contradiction_started=False, router_switch_occurred=False,
            contradiction_resolved=False)
        self._append("EXPLORER_DECISION_COMPLETED", record)
        self.state["attempted_decisions"] += 1
        self.state["pending_decision"] = None
        self._write_state(); self.bind_session(store)
        return _plain(record)

    def complete_authorized(self, store: SessionStore,
                            routing_store: RelationEvidenceStore, frozen: dict,
                            event_envelope: dict, routing_record: dict) -> dict:
        event = event_envelope["record"]
        receipt = event["receipt"]
        if event_envelope is not store.records["events"][-1] or \
                frozen["decision"]["action"] != receipt["action"] or \
                routing_record["receipt_identity"] != event["receipt_identity"]:
            raise RoutingError("authorized exploration completion binding failed")
        key = relation_key(routing_record["relation"])
        threshold = self.registry["policy"]["confidence"][
            "contradiction_baseline_identical_outcomes"]
        # The routing record is already appended; exclude it from prior history.
        local = [row["record"] for row in routing_store.records[:-1]
                 if relation_key(row["record"]["relation"]) == key]
        prior_values = [row["realized_consequence"] for row in local]
        started = len(prior_values) >= threshold and \
            len(set(prior_values[-threshold:])) == 1 and \
            prior_values[-1] != receipt["realized_consequence"]
        record = dict(decision_sequence=frozen["decision_sequence"],
            status="AUTHORIZED", action=receipt["action"],
            relation=routing_record["relation"],
            realized_consequence=receipt["realized_consequence"],
            receipt_identity=event["receipt_identity"],
            receipt_provenance_sha256=event["receipt_provenance_sha256"],
            routing_evidence_sequence=routing_record["evidence_sequence"],
            contradiction_baseline_required=threshold,
            contradiction_started=started,
            router_switch_occurred=routing_record["switch_occurred"],
            router_score_after=routing_record["router_score_after"],
            clear_preference_minimum_observations=self.registry["policy"][
                "confidence"]["clear_preference_minimum_observations"],
            clear_preference_lead_correct=self.registry["policy"][
                "confidence"]["clear_preference_lead_correct"],
            contradiction_resolved=(routing_record["router_score_after"]["G2"][
                "total"] >= self.registry["policy"]["confidence"][
                    "clear_preference_minimum_observations"] and abs(
                routing_record["router_score_after"]["G2"]["correct"] -
                routing_record["router_score_after"]["G3"]["correct"]) >=
                self.registry["policy"]["confidence"][
                    "clear_preference_lead_correct"]))
        self._append("EXPLORER_DECISION_COMPLETED", record)
        replay = dict(attempted_decisions=self.state["attempted_decisions"],
            authorized_decisions=self.state["authorized_decisions"],
            last_probe_decision_sequence=self.state["last_probe_decision_sequence"],
            last_probe_authorized_decision=self.state[
                "last_probe_authorized_decision"],
            last_execution_by_relation=deepcopy(
                self.state["last_execution_by_relation"]),
            unresolved_contradictions=deepcopy(
                self.state["unresolved_contradictions"]), outcomes={key: prior_values})
        self._apply_completion(replay, frozen, record)
        for name in ("attempted_decisions", "authorized_decisions",
                     "last_probe_decision_sequence",
                     "last_probe_authorized_decision",
                     "last_execution_by_relation", "unresolved_contradictions"):
            self.state[name] = replay[name]
        self.state["pending_decision"] = None
        self._write_state(); self.bind_session(store)
        return _plain(record)


class GroundedExplorationRuntime(RelationRoutedRuntime):
    """Relation-routed runtime whose action comes only from GroundedExplorer."""
    def __init__(self, store: SessionStore, joint_client: ModelClient,
                 specialists: dict, registry: dict,
                 routing_store: RelationEvidenceStore,
                 confidence_store: ExplorerConfidenceStore,
                 regime_version: str):
        super().__init__(store, joint_client, specialists, registry,
                         routing_store, regime_version)
        self.confidence_store = confidence_store
        confidence_store.bind_session(store)

    @staticmethod
    def _internal_route_problem(rejected: StepResult,
                                episode_steps: int) -> dict:
        constraint = ("PROTECTED_EPISODE_LIMIT" if
                      episode_steps >= EPISODE_LIMIT else
                      "PROTECTED_CONTINUATION_REFUSAL")
        problem = dict(type="INTERNAL_ROUTE_PROBLEM",
            component="execution lifecycle", requested_operation="begin_step",
            observed_constraint=constraint, protected_limit=EPISODE_LIMIT,
            episode_steps=episode_steps, authority_result="rejected",
            framework_reason=rejected.reason, execution_occurred=False,
            receipt_created=False, memory_mutated=False,
            routing_evidence_created=False, suggested_need="NEW_RUNTIME_ROUTE",
            authoritative=False, controls_execution=False,
            controls_runtime_creation=False, controls_schedule=False,
            trains_model=False)
        if problem["type"] not in PROBLEM_TYPES:
            raise RoutingError("unknown problem type")
        return problem

    def execute_autonomous(self) -> dict:
        capture, batch, batch_sequence, decision_id = self._next_batch()
        previews, selections, routed = self._route_batch(capture, batch)
        public_forecasts = self._public_forecasts(batch, selections)
        frozen = self.confidence_store.freeze(store=self.store,
            routing_store=self.routing_store, pre_state=capture["state"],
            forecasts=public_forecasts,
            routed_forecasts=routed["routed_forecasts"], previews=previews,
            all_predictions_valid=batch.all_valid,
            prediction_batch_sequence=batch_sequence, decision_id=decision_id)
        explorer = frozen["decision"]
        selected_action = explorer["action"]
        if explorer["abstained"] or selected_action is None:
            record = dict(prediction_batch_sequence=batch_sequence,
                decision_id=decision_id, execution_kind="EXPLORER_ABSTAINED",
                action_source="GROUNDED_EXPLORER", status="ABSTAINED",
                pre_state=capture["state"], relation_previews=previews,
                relation_selections_before=selections,
                forecasts=public_forecasts, choices=routed["choices"],
                explorer=explorer, actual_execution=False,
                source_scope=dict(runtime_index=self.store.checkpoint["runtime_index"],
                                  source_identity=self.store.checkpoint[
                                      "current_source_identity"]),
                external_regime_version=self.regime_version,
                regime_model_visible=False, model_calls=9)
            self.store.append("training", "GROUNDED_EXPLORER_ABSTENTION", record)
            self.store.save(state=capture["state"],
                next_transaction_id=capture["transaction_id"],
                attempted_decision=True)
            completion = self.confidence_store.complete_abstained(self.store, frozen)
            return {**_plain(record), "confidence_completion": completion}

        execution_kind = ("EXPLORER_PROBE_EXECUTION" if explorer["mode"] == "PROBE"
                          else "EXPLORER_EXPLOIT_EXECUTION")
        if execution_kind not in ("EXPLORER_PROBE_EXECUTION",
                                  "EXPLORER_EXPLOIT_EXECUTION"):
            raise RoutingError("grounded Explorer produced an unsupported mode")
        selected_specialist = selections[selected_action]
        selected = next(row for row in batch.forecasts[selected_specialist]
                        if row.action == selected_action)
        specialist_predictions = {key: next(row.consequence for row in forecasts
            if row.action == selected_action) for key, forecasts in batch.forecasts.items()}
        commitment = batch.commitments[selected_action]
        prediction = Prediction(capture["epoch"], capture["transaction_id"],
            capture["state"], selected.action, selected.next_state,
            selected.consequence)
        core = self.controller._active.framework.inner
        core.map = BoundPredictionMap(unwrap_map(core.map), prediction)
        pending = self.controller.begin_step(selected.action)
        if isinstance(pending, StepResult):
            problem = self._internal_route_problem(pending, core.episode_steps)
            record = dict(prediction_batch_sequence=batch_sequence,
                decision_id=decision_id,
                execution_kind="EXPLORER_FRAMEWORK_REJECTION",
                action_source="GROUNDED_EXPLORER", status="FRAMEWORK_REJECTED",
                pre_state=capture["state"], requested_action=selected.action,
                relation_previews=previews,
                relation_selections_before=selections,
                forecasts=public_forecasts, choices=routed["choices"],
                explorer=explorer, actual_execution=False,
                receipt_identity=None, routing_evidence=None,
                framework_result=_plain(asdict(pending)), problem=problem,
                source_scope=dict(runtime_index=self.store.checkpoint["runtime_index"],
                                  source_identity=self.store.checkpoint[
                                      "current_source_identity"]),
                external_regime_version=self.regime_version,
                regime_model_visible=False, model_calls=9)
            self.store.append("training",
                              "GROUNDED_EXPLORER_FRAMEWORK_REJECTION", record)
            self.store.save(state=capture["state"],
                next_transaction_id=capture["transaction_id"],
                attempted_decision=True)
            completion = self.confidence_store.complete_rejected(
                self.store, frozen, pending, problem)
            return {**_plain(record), "confidence_completion": completion}
        if not isinstance(pending, PendingTransaction):
            raise RoutingError("begin_step returned an unknown result type")
        if _plain(asdict(pending.prediction)) != _plain(asdict(prediction)):
            raise RoutingError("grounded Explorer prediction was not latched")
        if self.controller._source.reader().current() is not None:
            raise RoutingError("receipt existed before grounded Explorer execution")
        receipt = self.controller.execute_pending()
        actual = _plain(asdict(self.controller._active.world.last_actual))
        self.authentic[receipt.identity()] = receipt
        self.executions[receipt.identity()] = actual
        result = self.controller.submit_package(evidence(receipt))
        if not result.committed or not result.continued:
            self.controller.release(receipt)
            raise RoutingError(f"grounded Explorer publication rejected: {result.reason}")
        core = self.controller._active.framework.inner
        memory_record = core.memory.records[-1]
        package = self.controller._active.framework.packages[-1]
        if package.receipt is not receipt:
            raise RoutingError("grounded Explorer receipt object was substituted")
        receipt_value, memory_value = _plain(asdict(receipt)), _plain(asdict(memory_record))
        event = dict(session_id=self.store.checkpoint["session_id"],
            recorded_at=_now(), prediction_batch_sequence=batch_sequence,
            execution_kind=execution_kind,
            action_source="GROUNDED_EXPLORER",
            explorer_mode=explorer["mode"], explorer_reason=explorer["reason"],
            explorer_decision_sequence=explorer["decision_sequence"],
            explorer_frozen_record_sha256=digest(frozen),
            receipt=receipt_value, receipt_identity=list(receipt.identity()),
            receipt_provenance_sha256=digest(receipt_value),
            authorization_status=result.status.value, memory_record=memory_value,
            source_scope=dict(runtime_index=self.store.checkpoint["runtime_index"],
                              imported_after_restart=False,
                              source_identity=receipt.source_identity),
            external_regime_version=self.regime_version,
            regime_model_visible=False)
        event_envelope = self.store.append("events", "AUTHORIZED_REALIZED_EVENT", event)
        event_head = sha256(_canonical(event_envelope).encode()).hexdigest()
        training = dict(session_id=self.store.checkpoint["session_id"],
            epoch=receipt.epoch, transaction_id=receipt.transaction_id,
            pre_state=capture["state"], prediction_batch_sequence=batch_sequence,
            decision_id=decision_id,
            order=self.store.checkpoint["completed_steps"] + 1,
            timestamp=event["recorded_at"], execution_kind=execution_kind,
            action_source="GROUNDED_EXPLORER",
            explorer=deepcopy(explorer),
            explorer_frozen_record_sha256=digest(frozen),
            source_scope=dict(runtime_index=self.store.checkpoint["runtime_index"],
                              source_identity=receipt.source_identity),
            input_context_hash=digest(selected.input_context),
            authenticated_history_reference=capture[
                "authenticated_history_reference"],
            chosen_action=selected.action,
            predicted_next_state=selected.next_state,
            predicted_consequence=selected.consequence,
            selected_specialist_for_executed_relation=selected_specialist,
            relation_selections_before=selections,
            choices=routed["choices"], forecasts=public_forecasts,
            specialist_predictions=specialist_predictions,
            routing_registry_sha256=self.registry["document"]["sha256"],
            exploration_registry_sha256=self.confidence_store.registry[
                "document"]["sha256"],
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
                        calibration_execution=False,
                        explorer_reason_frozen_before_receipt=True),
            external_regime_version=self.regime_version,
            regime_model_visible=False)
        self.store.append("training", "AUTHORIZED_GROUNDED_EXPLORATION_RECORD",
                          training)
        self.store.save(state=receipt.next_state,
            next_transaction_id=core.next_transaction_id,
            completed_step=True, attempted_decision=True)
        route = self.routing_store.record(self.store,
            context_hash=digest(selected.input_context),
            predictions=specialist_predictions, commitment=commitment,
            event_envelope=event_envelope, execution_kind=execution_kind,
            per_action_selection=selections)
        confidence = self.confidence_store.complete_authorized(
            self.store, self.routing_store, frozen, event_envelope, route)
        self.controller.release(receipt)
        return dict(step=self.store.checkpoint["completed_steps"],
            prediction_batch_sequence=batch_sequence, decision_id=decision_id,
            execution_kind=execution_kind,
            action_source="GROUNDED_EXPLORER", state=capture["state"],
            epoch=capture["epoch"], transaction_id=capture["transaction_id"],
            status="AUTHORIZED", explorer=explorer,
            imported_pre_restart_records=sum(item["restoration_status"] ==
                "PRE_RESTART_IMPORTED" for item in
                capture["authenticated_history_provenance"]),
            relation_previews=previews,
            relation_selections_before=selections,
            forecasts=public_forecasts, choices=routed["choices"],
            execution=actual, receipt=receipt_value,
            prediction_match=training["prediction_match"],
            memory_publication=dict(authorization=result.status.value,
                event_sequence=event_envelope["sequence"],
                event_head_sha256=event_head),
            shadow_scoring={key: dict(predicted=specialist_predictions[key],
                correct=specialist_predictions[key] == receipt.realized_consequence)
                for key in SPECIALISTS},
            routing_evidence=route, confidence_completion=confidence,
            model_calls=9)


def _segment_expectation(segment: str) -> dict:
    return {
        "A1": dict(resume=False, attempts=0, batches=0, runtime=0,
                   regime="A", transition=False, decisions=18),
        "B1": dict(resume=True, attempts=18, batches=18, runtime=1,
                   regime="B", transition=True, decisions=9),
        "B2": dict(resume=True, attempts=27, batches=27, runtime=2,
                   regime="B", transition=False, decisions=9),
        "A2": dict(resume=True, attempts=36, batches=36, runtime=3,
                   regime="A", transition=True, decisions=18),
    }[segment]


def _r2_segment_expectation(segment: str) -> dict:
    return {
        "R2_A1_1": dict(resume=False, attempts=0, batches=0, runtime=0,
                        regime="A", transition=False, decisions=9,
                        decision_range=[1, 9]),
        "R2_A1_2": dict(resume=True, attempts=9, batches=9, runtime=1,
                        regime="A", transition=False, decisions=9,
                        decision_range=[10, 18]),
        "R2_B1": dict(resume=True, attempts=18, batches=18, runtime=2,
                      regime="B", transition=True, decisions=9,
                      decision_range=[19, 27]),
        "R2_B2": dict(resume=True, attempts=27, batches=27, runtime=3,
                      regime="B", transition=False, decisions=9,
                      decision_range=[28, 36]),
        "R2_A2_1": dict(resume=True, attempts=36, batches=36, runtime=4,
                        regime="A", transition=True, decisions=9,
                        decision_range=[37, 45]),
        "R2_A2_2": dict(resume=True, attempts=45, batches=45, runtime=5,
                        regime="A", transition=False, decisions=9,
                        decision_range=[46, 54]),
    }[segment]


def run_grounded_exploration_segment(session: Path, exploration_registry: Path,
                                     segment: str, resume: bool,
                                     joint_client=None,
                                     specialist_clients=None,
                                     runtime_schedule: str = "V0") -> dict:
    if runtime_schedule == "V0" and segment in SEGMENTS:
        plan = _segment_expectation(segment)
    elif runtime_schedule == "R2" and segment in R2_SEGMENTS:
        plan = _r2_segment_expectation(segment)
    else:
        raise RoutingError("unknown grounded-exploration segment")
    if resume != plan["resume"]:
        raise RoutingError("segment resume mode differs from frozen schedule")
    exploration = load_grounded_exploration_registry(exploration_registry)
    if specialist_clients is None:
        specialist_clients, relation_registry = relation_routed_clients(
            exploration_registry, device="cuda")
    else:
        relation_registry = exploration["relation_registry"]
    joint = joint_client or ModelClient()
    before = {key: specialist_clients[key].requests for key in SPECIALISTS}
    joint_before = joint.requests
    with SessionStore(session, resume) as store, \
            RelationEvidenceStore(exploration_registry) as routing_store, \
            ExplorerConfidenceStore(exploration_registry) as confidence_store:
        requests = sum(row["kind"] == "REQUEST_INTENT"
                       for row in store.records["calls"])
        actual = dict(attempts=store.checkpoint["attempted_decisions"],
                      batches=requests // 9,
                      runtime=store.checkpoint["runtime_index"])
        expected = {key: plan[key] for key in actual}
        if requests % 9 or actual != expected:
            raise RoutingError(f"segment start differs from frozen schedule: {actual}")
        if confidence_store.state["attempted_decisions"] != plan["attempts"]:
            raise RoutingError("confidence schedule position differs")
        rollover_input = dict(
            prior_runtime_index=store.checkpoint["runtime_index"],
            prior_attempted_decisions=store.checkpoint["attempted_decisions"],
            prior_authorized_events=len(store.records["events"]),
            prior_routing_evidence=len(routing_store.records),
            prior_confidence_state_sha256=digest({key: confidence_store.state[key]
                for key in ("attempted_decisions", "authorized_decisions",
                            "last_probe_decision_sequence",
                            "last_probe_authorized_decision",
                            "last_execution_by_relation",
                            "unresolved_contradictions")}))
        store.configure_regime(plan["regime"], plan["transition"])
        runtime = GroundedExplorationRuntime(store, joint, specialist_clients,
            relation_registry, routing_store, confidence_store, plan["regime"])
        rows = [runtime.execute_autonomous() for _ in range(plan["decisions"])]
        calls = joint.requests - joint_before + sum(
            specialist_clients[key].requests - before[key] for key in SPECIALISTS)
        return dict(mode="grounded-exploration-live", segment=segment,
            runtime_schedule=runtime_schedule,
            registered_decision_range=plan.get("decision_range"),
            session_id=store.checkpoint["session_id"], session=str(store.directory),
            resumed=resume, runtime_index=store.checkpoint["runtime_index"],
            epoch=store.checkpoint["current_epoch"], rows=rows,
            actual_model_calls=calls,
            model_calls_by_role=dict(joint_next_state=joint.requests - joint_before,
                G2=specialist_clients["G2"].requests - before["G2"],
                G3=specialist_clients["G3"].requests - before["G3"]),
            confidence_state=deepcopy(confidence_store.state),
            relation_state=deepcopy(routing_store.state["relations"]),
            consequence_specialists=relation_registry["payload"]["specialists"],
            external_regime_version=plan["regime"], regime_model_visible=False,
            rollover_input=rollover_input,
            checkpoint=_plain(store.checkpoint))


def _phase(decision_sequence: int) -> tuple[str, str]:
    if decision_sequence <= 18:
        return "A1", "EARLY_A" if decision_sequence <= 9 else "LATE_A"
    if decision_sequence <= 36:
        return "B", "EARLY_B" if decision_sequence <= 27 else "LATE_B"
    return "A2", "EARLY_A2" if decision_sequence <= 45 else "LATE_A2"


def _forecast_tuple(forecasts: dict) -> tuple[MapForecast, ...]:
    return tuple(MapForecast(action=action,
        action_alias=forecasts[action]["action_alias"],
        next_state=forecasts[action]["next_state"],
        consequence=forecasts[action]["routed_consequence"],
        abstained=not forecasts[action]["valid"],
        failure=None if forecasts[action]["valid"] else "INVALID_MAP_COMPONENT",
        history_count=forecasts[action]["history_count"], input_context={})
        for action in ACTION_ORDER)


def analyze_grounded_exploration_campaign(session: Path,
                                          exploration_registry: Path,
                                          output: Path,
                                          runtime_schedule: str = "V0") -> dict:
    if output.exists():
        raise RoutingError("grounded exploration report output already exists")
    policy = json.loads(POLICY_PATH.read_text())
    with SessionStore(session, True) as store, \
            RelationEvidenceStore(exploration_registry) as route, \
            ExplorerConfidenceStore(exploration_registry) as confidence:
        route.bind_session(store); confidence.bind_session(store)
        calls = deepcopy(store.records["calls"])
        events = [deepcopy(row["record"]) for row in store.records["events"]]
        training = [deepcopy(row["record"]) for row in store.records["training"]]
        routing = [deepcopy(row["record"]) for row in route.records]
        confidence_rows = deepcopy(confidence.records)
        checkpoint = deepcopy(store.checkpoint)
        final_route_state = deepcopy(route.state)
        final_confidence_state = deepcopy(confidence.state)
        registry = deepcopy(route.registry)

    requests = [row for row in calls if row["kind"] == "REQUEST_INTENT"]
    if len(requests) != policy["total_model_calls"]:
        raise RoutingError(f"campaign request count differs from frozen 486: {len(requests)}")
    if len(training) != policy["total_decisions"] or \
            checkpoint["attempted_decisions"] != policy["total_decisions"]:
        raise RoutingError("campaign decision count differs from frozen 54")
    if len(confidence_rows) != policy["total_decisions"] * 2:
        raise RoutingError("exploration freeze/completion record count differs")
    if len(events) != len(routing) or len(events) != \
            checkpoint["completed_steps"]:
        raise RoutingError("authorized event/routing/Memory counts differ")
    if any(event["execution_kind"] not in
           ("EXPLORER_PROBE_EXECUTION", "EXPLORER_EXPLOIT_EXECUTION")
           for event in events):
        raise RoutingError("autonomous campaign contains a non-Explorer execution")

    batches: dict[tuple[int, int], list[str]] = {}
    artifact_checks: dict[int, dict[str, set]] = {}
    epoch_ids_by_runtime: dict[int, set[int]] = {}
    hidden_prompt_checks = 0
    for row in requests:
        record = row["record"]
        serialized = json.dumps(record["request"], sort_keys=True).lower()
        if "regime" in serialized or "selected_specialist" in serialized or \
                "probe_" in serialized or "explorer mode" in serialized:
            raise RoutingError("hidden regime/router/Explorer state found in prompt")
        hidden_prompt_checks += 1
        parts = record["call_id"].split(":")
        epoch_token = next((part for part in parts if part.startswith("e") and
                            part[1:].isdigit()), None)
        batch_token = next((part for part in parts if part.startswith("b") and
                            part[1:].isdigit()), None)
        if epoch_token is None or batch_token is None:
            raise RoutingError("grounded-exploration call identity is malformed")
        runtime = int(epoch_token[1:]) - 2000
        epoch_ids_by_runtime.setdefault(runtime, set()).add(
            int(epoch_token[1:]))
        batch = int(batch_token[1:])
        batches.setdefault((runtime, batch), []).append(record["role"])
        if record["role"].startswith("routed-consequence:"):
            specialist = record["role"].split(":", 1)[1]
            expected = registry["specialists"][specialist]["artifact_sha256"]
            actual = record.get("model_generation_identity", {}).get(
                "artifact_sha256")
            artifact_checks.setdefault(runtime, {}).setdefault(
                specialist, set()).add(actual == expected)
    required_roles = Counter({"joint-next-state": 3,
        "routed-consequence:G2": 3, "routed-consequence:G3": 3})
    if len(batches) != 54 or any(Counter(roles) != required_roles
                                for roles in batches.values()):
        raise RoutingError("prediction batch role cardinality mismatch")
    expected_batches = ({1: 18, 2: 9, 3: 9, 4: 18}
                        if runtime_schedule == "V0" else
                        {runtime: 9 for runtime in range(1, 7)}
                        if runtime_schedule == "R2" else None)
    if expected_batches is None:
        raise RoutingError("unknown grounded-exploration runtime schedule")
    batches_by_runtime = dict(Counter(runtime for runtime, _ in batches))
    if batches_by_runtime != expected_batches:
        raise RoutingError(f"runtime schedule differs: {batches_by_runtime}")
    artifact_verification = {runtime: {specialist: values == {True}
        for specialist, values in checks.items()}
        for runtime, checks in artifact_checks.items()}
    artifacts_reverified = set(artifact_verification) == set(expected_batches) and all(
        set(checks) == set(SPECIALISTS) and all(checks.values())
        for checks in artifact_verification.values())

    freezes = [row["record"] for row in confidence_rows
               if row["kind"] == "EXPLORER_DECISION_FROZEN"]
    completions = [row["record"] for row in confidence_rows
                   if row["kind"] == "EXPLORER_DECISION_COMPLETED"]
    if [row["decision_sequence"] for row in freezes] != list(range(1, 55)) or \
            [row["decision_sequence"] for row in completions] != list(range(1, 55)):
        raise RoutingError("confidence decision sequence is incomplete")
    completion_by_sequence = {row["decision_sequence"]: row for row in completions}
    routing_by_sequence = {row["evidence_sequence"]: row for row in routing}

    # Re-derive every pre-execution decision from only the evidence available then.
    explorer = GroundedExplorer(policy)
    router = RelationGroundedRouter(registry["policy"])
    replay_confidence = dict(attempted_decisions=0, authorized_decisions=0,
        last_probe_decision_sequence=None, last_probe_authorized_decision=None,
        last_execution_by_relation={}, unresolved_contradictions={}, outcomes={})
    route_prefix: list[dict] = []
    selected_by_relation: dict[str, str] = {}
    for frozen in freezes:
        state = frozen["pre_state"]
        previews = {}
        for action in ACTION_ORDER:
            relation = relation_identity(state, action)
            key = relation_key(relation)
            previews[action] = dict(relation=relation,
                selected_specialist=selected_by_relation.get(key, "G2"),
                scores=router.scores(route_prefix, relation),
                relation_evidence_count=sum(
                    relation_key(row["relation"]) == key for row in route_prefix),
                total_evidence_count=len(route_prefix))
        expected = explorer.derive(pre_state=state,
            forecasts=frozen["forecasts"],
            routed_forecasts=_forecast_tuple(frozen["forecasts"]),
            previews=previews, routing_records=route_prefix,
            confidence_state=replay_confidence,
            all_predictions_valid=all(row["valid"]
                                      for row in frozen["forecasts"].values()))
        if expected != frozen["decision"]:
            raise RoutingError(f"Explorer decision {frozen['decision_sequence']} does not replay")
        completion = completion_by_sequence[frozen["decision_sequence"]]
        ExplorerConfidenceStore._apply_completion(
            replay_confidence, frozen, completion)
        if completion["status"] == "AUTHORIZED":
            route_row = routing_by_sequence[completion["routing_evidence_sequence"]]
            route_prefix.append(route_row)
            selected_by_relation[relation_key(route_row["relation"])] = \
                route_row["selected_specialist_after"]
    replay_snapshot = {key: replay_confidence[key] for key in
        ("attempted_decisions", "authorized_decisions",
         "last_probe_decision_sequence", "last_probe_authorized_decision",
         "last_execution_by_relation", "unresolved_contradictions")}
    actual_snapshot = {key: final_confidence_state[key] for key in replay_snapshot}
    if replay_snapshot != actual_snapshot:
        raise RoutingError("final confidence state differs from exact replay")

    probe_rows, exploit_rows, abstained_rows = [], [], []
    for frozen in freezes:
        decision = frozen["decision"]
        completion = completion_by_sequence[frozen["decision_sequence"]]
        row = dict(decision_sequence=frozen["decision_sequence"],
            phase=_phase(frozen["decision_sequence"])[0],
            phase_half=_phase(frozen["decision_sequence"])[1],
            pre_state=frozen["pre_state"], action=decision["action"],
            mode=decision["mode"], reason=decision["reason"],
            coverage=decision["coverage"],
            relation_confidence=(None if decision["action"] is None else
                decision["relation_confidence"][decision["action"]]),
            status=completion["status"],
            receipt_identity=completion.get("receipt_identity"),
            realized_consequence=completion.get("realized_consequence"),
            routing_evidence_sequence=completion.get("routing_evidence_sequence"),
            contradiction_revealed=completion.get("contradiction_started", False),
            router_switch_immediate=completion.get("router_switch_occurred", False))
        if decision["mode"] == "PROBE" and completion["status"] == "AUTHORIZED":
            probe_rows.append(row)
        elif decision["mode"] == "EXPLOIT" and completion["status"] == "AUTHORIZED":
            exploit_rows.append(row)
        else:
            abstained_rows.append(row)

    switches = [row for row in routing if row["switch_occurred"]]
    local_ordinals: dict[str, dict[int, int]] = {}
    for row in routing:
        key = relation_key(row["relation"])
        local_ordinals.setdefault(key, {})[row["evidence_sequence"]] = \
            len(local_ordinals.setdefault(key, {})) + 1
    for probe in probe_rows:
        confidence_before = probe["relation_confidence"]
        evidence_sequence = probe["routing_evidence_sequence"]
        relation = routing_by_sequence[evidence_sequence]["relation"]
        key = relation_key(relation)
        later_switch = next((row for row in switches
            if relation_key(row["relation"]) == key and
               local_ordinals[key][row["evidence_sequence"]] >=
               local_ordinals[key][evidence_sequence] and
               local_ordinals[key][row["evidence_sequence"]] -
               local_ordinals[key][evidence_sequence] <
               policy["routing_policy"]["window_size"]), None)
        route_row = routing_by_sequence[evidence_sequence]
        scores = route_row["router_score_after"]
        disagreement_resolved = bool(confidence_before["specialists_disagree"] and
            scores["G2"]["total"] >= policy["confidence"][
                "clear_preference_minimum_observations"] and
            abs(scores["G2"]["correct"] - scores["G3"]["correct"]) >=
                policy["confidence"]["clear_preference_lead_correct"])
        first_evidence = confidence_before["authenticated_observations"] == 0
        contributes = later_switch is not None
        subsequent_effect = dict(observed=None, decision_sequence=None,
                                 alternate_action=None,
                                 reason="NO_SUBSEQUENT_ELIGIBLE_EXPLOIT")
        if later_switch is not None:
            switch_decision = next(event["prediction_batch_sequence"] for event in events
                if event["receipt_identity"] == later_switch["receipt_identity"])
            old_specialist = later_switch["selected_specialist"]
            action = relation["action"]
            for later_frozen in freezes:
                later_decision = later_frozen["decision"]
                if later_frozen["decision_sequence"] <= switch_decision or \
                        later_frozen["pre_state"] != relation["pre_state"] or \
                        later_decision["mode"] != "EXPLOIT" or \
                        later_decision["abstained"]:
                    continue
                alternate = deepcopy(later_frozen["forecasts"])
                alternate[action]["routed_consequence"] = alternate[action][
                    f"{old_specialist}_consequence"]
                choice = MechanicalExplorer().choose(_forecast_tuple(alternate))
                subsequent_effect = dict(
                    observed=choice.action != later_decision["action"],
                    decision_sequence=later_frozen["decision_sequence"],
                    alternate_action=choice.action,
                    actual_action=later_decision["action"],
                    reason="FROZEN_FORECAST_SELECTION_REPLAY")
                break
        probe.update(first_authenticated_evidence=first_evidence,
            specialist_disagreement_resolved=disagreement_resolved,
            contributed_to_router_switch=contributes,
            contributed_switch_evidence=(None if later_switch is None else
                                         later_switch["evidence_sequence"]),
            later_decisions_until_switch=(None if later_switch is None else
                next(event["prediction_batch_sequence"] for event in events
                     if event["receipt_identity"] == later_switch["receipt_identity"]) -
                probe["decision_sequence"]),
            changed_subsequent_exploitation_choice=subsequent_effect,
            useful=first_evidence or probe["contradiction_revealed"] or
                   disagreement_resolved or contributes)

    coverage_timeline = [dict(decision_sequence=row["decision_sequence"],
        phase=row["phase"], phase_half=row["phase_half"],
        pre_state=row["pre_state"], **row["coverage"])
        for row in probe_rows + exploit_rows + abstained_rows]
    coverage_timeline.sort(key=lambda row: row["decision_sequence"])
    final_coverage = []
    for state in sorted({row["pre_state"] for row in coverage_timeline}):
        latest = next(row for row in reversed(coverage_timeline)
                      if row["pre_state"] == state)
        final_coverage.append(latest)

    target_relation = relation_identity(1, "HOLD")
    training_by_receipt = {tuple(row["receipt_identity"]): row for row in training
                           if row.get("receipt_identity") is not None}
    target_trace = []
    for row in routing:
        if row["relation"] != target_relation:
            continue
        training_row = training_by_receipt[tuple(row["receipt_identity"])]
        target_trace.append(dict(decision_sequence=training_row[
            "prediction_batch_sequence"], phase=_phase(training_row[
                "prediction_batch_sequence"])[0],
            mode=training_row["explorer"]["mode"],
            reason=training_row["explorer"]["reason"],
            G2_prediction=row["specialists"]["G2"]["frozen_consequence"],
            G3_prediction=row["specialists"]["G3"]["frozen_consequence"],
            realized_consequence=row["realized_consequence"],
            selected_before=row["selected_specialist"],
            selected_after=row["selected_specialist_after"],
            score_after=row["router_score_after"],
            switch_occurred=row["switch_occurred"],
            receipt_identity=row["receipt_identity"]))
    target_switches = [row for row in switches if row["relation"] == target_relation]
    switch_dependencies = []
    for switch in switches:
        key = relation_key(switch["relation"])
        switch_local = local_ordinals[key][switch["evidence_sequence"]]
        contributors = [probe["decision_sequence"] for probe in probe_rows
            if relation_key(routing_by_sequence[probe[
                "routing_evidence_sequence"]]["relation"]) == key and
               0 <= switch_local - local_ordinals[key][probe[
                   "routing_evidence_sequence"]] <
                   policy["routing_policy"]["window_size"]]
        switch_dependencies.append(dict(
            routing_evidence_sequence=switch["evidence_sequence"],
            relation=switch["relation"],
            from_specialist=switch["selected_specialist"],
            to_specialist=switch["selected_specialist_after"],
            autonomous_probe_decisions_in_scoring_window=contributors,
            depended_on_autonomous_probe_evidence=bool(contributors)))

    phase_halves = ("EARLY_A", "LATE_A", "EARLY_B", "LATE_B",
                    "EARLY_A2", "LATE_A2")
    probe_rates = {}
    for half in phase_halves:
        rows = [row for row in probe_rows + exploit_rows + abstained_rows
                if row["phase_half"] == half]
        probe_count = sum(row["mode"] == "PROBE" and row["status"] == "AUTHORIZED"
                          for row in rows)
        probe_rates[half] = dict(decisions=len(rows), probes=probe_count,
            rate=probe_count / len(rows) if rows else None)

    offline_rows = []
    for frozen in freezes:
        seq = frozen["decision_sequence"]
        actual = frozen["decision"]
        mechanical = MechanicalExplorer().choose(_forecast_tuple(frozen["forecasts"]))
        offline_rows.append(dict(decision_sequence=seq, phase=_phase(seq)[0],
            actual_mode=actual["mode"], actual_action=actual["action"],
            exploit_only_action=mechanical.action,
            exploit_only_reason=mechanical.reason,
            actions_identical=actual["action"] == mechanical.action,
            receipt_legitimate_for_both=(actual["action"] == mechanical.action and
                completion_by_sequence[seq]["status"] == "AUTHORIZED"),
            counterfactual_receipt_created=False))

    reason_counts = Counter(row["reason"] for row in probe_rows)
    phase_counts = Counter(_phase(row["prediction_batch_sequence"])[0]
                           for row in training)
    internal_route_problems = [deepcopy(row["problem"]) | dict(
        decision_sequence=row["prediction_batch_sequence"])
        for row in training if row.get("problem", {}).get("type") ==
        "INTERNAL_ROUTE_PROBLEM"]
    execution_counter = Counter(row["source_scope"]["runtime_index"]
                                for row in events)
    runtime_execution_counts = {runtime: execution_counter[runtime]
                                for runtime in expected_batches}
    verified_history_projection = {}
    for runtime in expected_batches:
        depths = []
        for row in requests:
            record = row["record"]
            token = next(part for part in record["call_id"].split(":")
                         if part.startswith("e") and part[1:].isdigit())
            if int(token[1:]) - 2000 != runtime:
                continue
            payload = json.loads(record["request"]["prompt"])
            depths.append(len(payload["VERIFIED_CHRONOLOGICAL_HISTORY"]))
        verified_history_projection[runtime] = dict(requests=len(depths),
            requests_with_prior_relation_history=sum(depth > 0 for depth in depths),
            minimum_relation_history_depth=min(depths),
            maximum_relation_history_depth=max(depths))
    staleness_reasons = [row for row in probe_rows
                         if row["reason"] == "PROBE_STALE"]
    minimum_probe_rate = min(row["rate"] for row in probe_rates.values())
    worst_windows = [name for name, row in probe_rates.items()
                     if row["rate"] == minimum_probe_rate]
    source_identities = sorted({row["source_scope"]["source_identity"]
                                for row in training})
    b_runtimes = sorted({row["source_scope"]["runtime_index"] for row in training
                         if row["external_regime_version"] == "B"})
    result = dict(status="COMPLETE",
        frozen_exploration_rule=dict(confidence=policy["confidence"],
            probe_budget=policy["probe_budget"],
            routing_policy=policy["routing_policy"],
            evidence_scope="AUTHORIZED_EXACT_RELATION_ONLY"),
        schedule=policy["schedule"], total_model_calls=len(requests),
        model_calls_by_role=dict(Counter(row["record"]["role"] for row in requests)),
        autonomous_decision_attempts=checkpoint["attempted_decisions"],
        autonomous_executions=len(events), abstentions=len(abstained_rows),
        nonexecution_count_by_reason=dict(Counter(
            row["reason"] for row in abstained_rows)),
        framework_rejections=len(internal_route_problems),
        internal_route_problems=internal_route_problems,
        execution_kind_counts=dict(Counter(row["execution_kind"] for row in events)),
        phase_decision_counts=dict(phase_counts),
        probe_count=len(probe_rows), probe_count_by_reason=dict(reason_counts),
        exploit_count=len(exploit_rows), probes=probe_rows,
        useful_probes=sum(row["useful"] for row in probe_rows),
        redundant_probes=sum(not row["useful"] for row in probe_rows),
        probe_rates=probe_rates, relation_coverage_timeline=coverage_timeline,
        staleness_behavior=dict(stale_probes=len(staleness_reasons),
                                decisions=staleness_reasons),
        worst_exploration_window=dict(rate=minimum_probe_rate,
                                      phase_halves=worst_windows),
        final_relation_coverage_by_encountered_state=final_coverage,
        unresolved_relations_at_last_state_encounters=sum(
            row["relations_unresolved"] for row in final_coverage),
        action_trajectory=[dict(decision_sequence=row["decision_sequence"],
            phase=row["phase"], pre_state=row["pre_state"], mode=row["mode"],
            action=row["action"], status=row["status"],
            realized_consequence=row["realized_consequence"])
            for row in sorted(probe_rows + exploit_rows + abstained_rows,
                              key=lambda value: value["decision_sequence"])],
        target_relation_trace=target_trace,
        target_relation_switches=target_switches,
        routing_switch_probe_dependencies=switch_dependencies,
        exploit_only_offline_comparison=dict(scope=(
            "decision/information comparison on frozen contexts; no counterfactual receipts"),
            rows=offline_rows,
            identical_actions=sum(row["actions_identical"] for row in offline_rows),
            different_actions=sum(not row["actions_identical"] for row in offline_rows),
            legitimate_shared_receipts=sum(row["receipt_legitimate_for_both"]
                                           for row in offline_rows),
            counterfactual_receipts_created=0,
            actual_relations_with_evidence=len(final_route_state["relations"])),
        restart_proof=dict(runtime_schedule=runtime_schedule,
            B_runtime_indices=b_runtimes,
            runtime_indices=sorted({row["source_scope"]["runtime_index"]
                                    for row in training}),
            batches_by_runtime=batches_by_runtime,
            executions_by_runtime=runtime_execution_counts,
            verified_history_projection_by_runtime=verified_history_projection,
            source_identities=source_identities,
            epoch_ids_by_runtime={runtime: sorted(values) for runtime, values in
                                  epoch_ids_by_runtime.items()},
            confidence_exact_replay=True,
            confidence_decisions_before_restart=27,
            confidence_decisions_after_restart=27,
            specialist_artifacts_reverified_on_every_runtime=artifacts_reverified,
            artifact_verifications_by_runtime=artifact_verification,
            maximum_attempts_per_runtime=max(batches_by_runtime.values()),
            protected_episode_limit=EPISODE_LIMIT,
            fresh_source_and_epoch_per_runtime=(
                len(source_identities) == len(expected_batches) and
                len(epoch_ids_by_runtime) == len(expected_batches) and
                all(len(values) == 1 for values in
                    epoch_ids_by_runtime.values()))),
        memory_chronology=[dict(decision_sequence=row["prediction_batch_sequence"],
            pre_state=row["receipt"]["pre_state"], action=row["receipt"]["action"],
            realized_consequence=row["receipt"]["realized_consequence"],
            receipt_identity=row["receipt_identity"]) for row in events],
        confidence_exact_replay=True,
        decision_reason_exact_replay=True,
        hidden_regime_prompt_checks=hidden_prompt_checks,
        calibration_executions=0,
        no_weight_updates=True,
        global_lifecycle_status={"G2": "ACTIVE", "G3": "REJECTED"},
        final_checkpoint=dict(attempted_decisions=checkpoint["attempted_decisions"],
            completed_steps=checkpoint["completed_steps"],
            runtime_index=checkpoint["runtime_index"],
            current_state=checkpoint["current_state"], streams=checkpoint["streams"]),
        final_confidence_state=final_confidence_state,
        final_relation_state=final_route_state)
    atomic_json(output, result)
    return result
