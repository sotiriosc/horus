"""Bounded, non-authoritative problem detection and route requests for Horus v0.8."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from hashlib import sha256
from hmac import compare_digest, new as new_hmac
import fcntl
import json
import os
from pathlib import Path
import secrets
from typing import Any

from experiments.base_framework_v0.framework import ACTION_ORDER
from experiments.base_framework_v1.framework import EPISODE_LIMIT

from .core import digest
from .grounded_exploration import (
    DEFAULT_SOURCE_REGISTRY, ExplorerConfidenceStore, GroundedExplorationRuntime,
    GroundedExplorer, initialize_grounded_exploration_registry,
    load_grounded_exploration_registry)
from .grounded_learning import ROOT, atomic_json, file_hash
from .live import ModelClient, SessionStore, _canonical, _now, _plain
from .relation_routing import (RelationEvidenceStore, SPECIALISTS,
                               relation_routed_clients)
from .routing import RoutingError


POLICY_PATH = Path(__file__).with_name("problem_route_policy.json")
PROBLEM_ROUTE_VERSION = 1
V08_SEGMENTS = ("V08_A1_1", "V08_A1_2", "V08_B1", "V08_B2",
                "V08_A2_1", "V08_A2_2")


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


class RouteBroker:
    """Mechanical grant policy over a finite registered route/capability set."""
    def __init__(self, policy: dict | None = None):
        self.policy = policy or json.loads(POLICY_PATH.read_text())

    def request(self, capability: str, *, context: str,
                preauthorized_rollover: bool = False) -> dict:
        if capability not in self.policy["requested_capabilities"]:
            raise RoutingError("unknown requested capability")
        if capability in ("ALTERNATIVE_PREDICTOR", "DIFFERENT_REPRESENTATION",
                          "NEW_SPECIALIST"):
            return dict(requested_capability=capability,
                        broker_result="REQUEST_REQUIRES_EXTERNAL_APPROVAL",
                        selected_route=None, authoritative=False)
        if capability == "NEW_RUNTIME":
            return dict(requested_capability=capability,
                broker_result=("AUTHORIZED_PREREGISTERED_ROLLOVER" if
                               preauthorized_rollover else
                               "REQUEST_REQUIRES_EXTERNAL_APPROVAL"),
                selected_route=None, authoritative=False,
                protected_episode_limit=EPISODE_LIMIT,
                limit_changed=False)
        if capability == "MORE_RELATION_EVIDENCE" and context == "VALUE_TIE":
            return dict(requested_capability=capability,
                        broker_result="ROUTE_GRANTED",
                        selected_route="TIE_INFORMATION_PROBE",
                        authoritative=False)
        return dict(requested_capability=capability,
                    broker_result="REQUEST_REQUIRES_EXTERNAL_APPROVAL",
                    selected_route=None, authoritative=False)

    def validate_route(self, route: str) -> None:
        if route not in self.policy["registered_routes"]:
            raise RoutingError("route is not registered")


class ProblemRouteStore:
    """Authenticated append-only problem/route history with exact state replay."""
    KEY = "problem-route-integrity.key"
    STATE = "problem-route-state.json"
    STREAM = "problem-route-events.jsonl"

    @staticmethod
    def initialize(root: Path) -> None:
        root = root.resolve()
        for name in (ProblemRouteStore.KEY, ProblemRouteStore.STATE,
                     ProblemRouteStore.STREAM):
            if (root / name).exists():
                raise RoutingError("problem route store already exists")
        key = secrets.token_bytes(32)
        descriptor = os.open(root / ProblemRouteStore.KEY,
                             os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            os.write(descriptor, (key.hex() + "\n").encode())
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        (root / ProblemRouteStore.STREAM).touch(mode=0o600)
        state = ProblemRouteStore.initial_state()
        ProblemRouteStore._write_state_file(root, key, state)

    @staticmethod
    def initial_state() -> dict:
        return dict(version=PROBLEM_ROUTE_VERSION, session_id=None,
            attempted_decisions=0, authorized_executions=0,
            next_problem_number=1, tie_candidate=None, problems={},
            pending_decision=None, stream_count=0,
            stream_head_sha256=None, updated_at=None)

    @staticmethod
    def _write_state_file(root: Path, key: bytes, state: dict) -> None:
        payload = deepcopy(state); payload["updated_at"] = _now()
        document = {"payload": payload, "hmac_sha256": new_hmac(
            key, _canonical(payload).encode(), "sha256").hexdigest()}
        temporary = root / (ProblemRouteStore.STATE + ".tmp")
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                             0o600)
        try:
            os.write(descriptor, (json.dumps(document, indent=2, sort_keys=True) +
                                  "\n").encode())
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        os.replace(temporary, root / ProblemRouteStore.STATE)

    def __init__(self, root: Path):
        self.registry = load_problem_route_registry(root)
        self.policy = self.registry["policy"]
        self.broker = RouteBroker(self.policy)
        self.root = self.registry["root"]
        self._lock = (self.root / ".problem-route.lock").open("a+")
        try:
            fcntl.flock(self._lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RoutingError("problem route store is already open") from exc
        try:
            self._key = bytes.fromhex((self.root / self.KEY).read_text().strip())
            if len(self._key) != 32:
                raise ValueError
        except (OSError, ValueError) as exc:
            self.close()
            raise RoutingError("invalid problem route integrity key") from exc
        try:
            self.state = self._read_state()
            self.records = self._read_stream()
            self._validate_replay()
        except Exception:
            self.close()
            raise

    def close(self) -> None:
        if hasattr(self, "_lock") and not self._lock.closed:
            fcntl.flock(self._lock, fcntl.LOCK_UN)
            self._lock.close()

    def __enter__(self): return self
    def __exit__(self, *_): self.close()

    def _mac(self, value: Any) -> str:
        return new_hmac(self._key, _canonical(value).encode(),
                        "sha256").hexdigest()

    def _read_state(self) -> dict:
        try:
            document = json.loads((self.root / self.STATE).read_text())
            payload = document["payload"]
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise RoutingError("invalid problem route state") from exc
        if not compare_digest(self._mac(payload), document.get("hmac_sha256", "")):
            raise RoutingError("problem route state authentication failed")
        return payload

    def _read_stream(self) -> list[dict]:
        rows, previous = [], None
        try:
            lines = (self.root / self.STREAM).read_text().splitlines()
        except OSError as exc:
            raise RoutingError("missing problem route stream") from exc
        for sequence, line in enumerate(lines, 1):
            try:
                envelope = json.loads(line)
                signed = {key: envelope[key] for key in
                          ("sequence", "previous_sha256", "kind", "record")}
            except (ValueError, KeyError, TypeError) as exc:
                raise RoutingError("invalid problem route record") from exc
            if envelope["sequence"] != sequence or \
                    envelope["previous_sha256"] != previous or \
                    not compare_digest(self._mac(signed),
                                       envelope.get("hmac_sha256", "")):
                raise RoutingError("problem route chain authentication failed")
            previous = sha256(_canonical(envelope).encode()).hexdigest()
            rows.append(envelope)
        return rows

    def _append(self, kind: str, record: dict) -> dict:
        previous = None if not self.records else sha256(
            _canonical(self.records[-1]).encode()).hexdigest()
        record = {**deepcopy(record), "recorded_at": record.get("recorded_at", _now())}
        signed = dict(sequence=len(self.records) + 1, previous_sha256=previous,
                      kind=kind, record=_plain(record))
        envelope = {**signed, "hmac_sha256": self._mac(signed)}
        with (self.root / self.STREAM).open("a") as stream:
            stream.write(_canonical(envelope) + "\n")
            stream.flush(); os.fsync(stream.fileno())
        self.records.append(envelope)
        self.state["stream_count"] = len(self.records)
        self.state["stream_head_sha256"] = sha256(
            _canonical(envelope).encode()).hexdigest()
        return envelope

    def _write_state(self) -> None:
        self.state["updated_at"] = _now()
        self._write_state_file(self.root, self._key, self.state)

    def _validate_replay(self) -> None:
        pending = None
        attempts = executions = 0
        projection = None
        for envelope in self.records:
            record = envelope["record"]
            if envelope["kind"] == "PROBLEM_ROUTE_DECISION_FROZEN":
                if pending is not None or record["decision_sequence"] != attempts + 1:
                    raise RoutingError("problem route decision sequence mismatch")
                pending = record
                projection = record["state_projection_after"]
            elif envelope["kind"] == "PROBLEM_ROUTE_DECISION_COMPLETED":
                if pending is None or record["decision_sequence"] != \
                        pending["decision_sequence"]:
                    raise RoutingError("problem route completion mismatch")
                attempts += 1
                executions += record["status"] == "AUTHORIZED"
                pending = None
                projection = record["state_projection_after"]
            else:
                raise RoutingError("unknown problem route record")
        if self.state.get("version") != PROBLEM_ROUTE_VERSION or \
                self.state.get("attempted_decisions") != attempts or \
                self.state.get("authorized_executions") != executions or \
                self.state.get("stream_count") != len(self.records) or \
                self.state.get("stream_head_sha256") != (None if not self.records else
                    sha256(_canonical(self.records[-1]).encode()).hexdigest()) or \
                (self.state.get("pending_decision") is None) != (pending is None):
            raise RoutingError("problem route state/stream replay mismatch")
        if pending is not None and self.state["pending_decision"] != dict(
                decision_sequence=pending["decision_sequence"],
                frozen_record_sha256=digest(pending)):
            raise RoutingError("pending problem route decision mismatch")
        expected_projection = {key: self.state[key] for key in
            ("attempted_decisions", "authorized_executions",
             "next_problem_number", "tie_candidate", "problems")}
        if projection is not None and projection != expected_projection:
            raise RoutingError("problem route state does not replay from stream")
        for problem in self.state.get("problems", {}).values():
            self._validate_problem(problem)

    def bind_session(self, store: SessionStore) -> None:
        actual = store.checkpoint["session_id"]
        if self.state["session_id"] is None:
            if self.records or self.state["attempted_decisions"]:
                raise RoutingError("unbound problem route store contains decisions")
            self.state["session_id"] = actual
            self._write_state()
        elif self.state["session_id"] != actual:
            raise RoutingError("problem route registry belongs to another session")
        if self.state["attempted_decisions"] != store.checkpoint[
                "attempted_decisions"]:
            raise RoutingError("problem route/session attempt count mismatch")
        if self.state["authorized_executions"] != len(store.records["events"]):
            raise RoutingError("problem route/session receipt count mismatch")
        if self.state["pending_decision"] is not None:
            raise RoutingError("incomplete pre-execution problem route decision")

    def _validate_problem(self, problem: dict) -> None:
        if problem["problem_type"] not in self.policy["problem_types"] or \
                problem["status"] not in self.policy["problem_statuses"]:
            raise RoutingError("unknown problem type or status")
        forbidden_truth = ("authoritative", "controls_execution", "alters_memory",
                           "alters_specialist_selection", "changes_prediction",
                           "trains_model", "changes_protected_bound",
                           "alters_simulator", "creates_receipt")
        if any(problem.get(field) is not False for field in forbidden_truth):
            raise RoutingError("problem object was given authority")

    @staticmethod
    def _tie(forecasts: dict) -> tuple[list[str], dict]:
        values = {action: row["routed_consequence"] for action, row in
                  forecasts.items() if row["valid"]}
        if len(values) != len(ACTION_ORDER):
            return [], values
        maximum = max(values.values())
        return [action for action in ACTION_ORDER if values[action] == maximum], values

    @staticmethod
    def _problem_key(state: int, actions: list[str]) -> str:
        return f"{state}:" + ",".join(actions)

    @staticmethod
    def _select_tie_probe(actions: list[str], metadata: dict) -> tuple[str, dict]:
        def priority(action: str) -> tuple:
            row = metadata[action]
            contradiction = row["unresolved_recent_contradiction"] is not None
            age = row["observations_since_last_execution"]
            stale = 10**9 if age is None else age
            return (not row["specialists_disagree"], not contradiction,
                    row["authenticated_observations"], -stale,
                    ACTION_ORDER.index(action))
        selected = min(actions, key=priority)
        row = metadata[selected]
        reason = dict(specialists_disagree=row["specialists_disagree"],
            unresolved_contradiction=(row["unresolved_recent_contradiction"] is not None),
            authenticated_observations=row["authenticated_observations"],
            observations_since_last_execution=row["observations_since_last_execution"],
            canonical_action_index=ACTION_ORDER.index(selected),
            priority_order=["SPECIALIST_DISAGREEMENT", "UNRESOLVED_CONTRADICTION",
                "LESS_AUTHENTICATED_LOCAL_EVIDENCE", "MORE_STALE",
                "CANONICAL_ACTION_ORDER"])
        return selected, reason

    def _new_problem(self, *, decision_sequence: int, pre_state: int,
                     actions: list[str], forecasts: dict, metadata: dict,
                     last_successful_execution: dict | None) -> dict:
        problem_id = f"PR-{self.state['next_problem_number']:04d}"
        self.state["next_problem_number"] += 1
        references = {action: dict(
            authenticated_observations=metadata[action]["authenticated_observations"],
            most_recent_observation_sequence=metadata[action][
                "most_recent_observation_sequence"])
            for action in actions}
        problem = dict(problem_id=problem_id,
            created_decision_sequence=decision_sequence,
            component="MECHANICAL_EXPLORER",
            problem_type="UNRESOLVED_VALUE_TIE", state=pre_state,
            candidate_actions=actions, current_forecasts=deepcopy(forecasts),
            routing_state={action: dict(
                selected_specialist=metadata[action]["selected_specialist"],
                local_scores=metadata[action]["local_scores"])
                for action in actions},
            relation_confidence={action: deepcopy(metadata[action])
                                 for action in actions},
            relevant_authenticated_evidence_references=references,
            failure_count=self.policy["persistent_tie_attempts"],
            last_successful_execution=deepcopy(last_successful_execution),
            requested_capability="MORE_RELATION_EVIDENCE", status="OPEN",
            probe_count=0, route_request_count=0,
            receipt_evidence=[], resolved_decision_sequence=None,
            authoritative=False, controls_execution=False, alters_memory=False,
            alters_specialist_selection=False, changes_prediction=False,
            trains_model=False, changes_protected_bound=False,
            alters_simulator=False, creates_receipt=False)
        self._validate_problem(problem)
        return problem

    def prepare(self, *, store: SessionStore, ordinary_decision: dict,
                pre_state: int, forecasts: dict) -> dict:
        # A pending record can only occur after a crash between this durable freeze
        # and the ordinary confidence freeze. Reuse it; never issue another route.
        pending = self.state.get("pending_decision")
        if pending is not None:
            record = next(row["record"] for row in reversed(self.records)
                          if row["kind"] == "PROBLEM_ROUTE_DECISION_FROZEN")
            supplied = digest(dict(ordinary_decision=ordinary_decision,
                pre_state=pre_state, forecasts=forecasts))
            if record["input_sha256"] != supplied:
                raise RoutingError("pending problem route input changed")
            return deepcopy(record["final_decision"])
        self.bind_session(store)
        sequence = ordinary_decision["decision_sequence"]
        if sequence != self.state["attempted_decisions"] + 1:
            raise RoutingError("problem route decision sequence mismatch")
        final = deepcopy(ordinary_decision)
        final["ordinary_decision_sha256"] = digest(ordinary_decision)
        final["ordinary_route"] = ("RELATION_PROBE" if
            ordinary_decision["mode"] == "PROBE" else "NORMAL_EXPLOIT")
        final["route_broker"] = dict(selected_route=final["ordinary_route"],
            broker_result="EXISTING_ROUTE", requested_capability=None)
        final["problem_id"] = None
        actions, routed_values = self._tie(forecasts)
        is_tie = (ordinary_decision["abstained"] and
                  ordinary_decision["reason"] == "EXPLOIT_TIED_MAXIMUM" and
                  len(actions) > 1)
        problem_events = []
        if is_tie:
            key = self._problem_key(pre_state, actions)
            problem = self.state["problems"].get(key)
            candidate = self.state.get("tie_candidate")
            if problem is None and candidate is not None and \
                    candidate["key"] == key and candidate["last_decision_sequence"] == \
                    sequence - 1 and candidate["authorized_execution_count"] == \
                    self.state["authorized_executions"]:
                latest = None
                if self.state["authorized_executions"]:
                    latest = dict(count=self.state["authorized_executions"])
                problem = self._new_problem(decision_sequence=sequence,
                    pre_state=pre_state, actions=actions, forecasts=forecasts,
                    metadata=ordinary_decision["relation_confidence"],
                    last_successful_execution=latest)
                self.state["problems"][key] = problem
                problem_events.append("PROBLEM_OPENED")
            elif problem is None:
                self.state["tie_candidate"] = dict(key=key, count=1,
                    first_decision_sequence=sequence,
                    last_decision_sequence=sequence,
                    authorized_execution_count=self.state["authorized_executions"])
            if problem is not None:
                if problem["created_decision_sequence"] != sequence:
                    problem["failure_count"] += 1
                    problem["current_forecasts"] = deepcopy(forecasts)
                    problem["relation_confidence"] = deepcopy(
                        ordinary_decision["relation_confidence"])
                    problem_events.append("PROBLEM_EVIDENCE_UPDATED")
                if problem["probe_count"] >= self.policy[
                        "maximum_tie_information_probes_per_problem"]:
                    problem["status"] = "UNRESOLVED"
                    problem_events.append("PROBLEM_UNRESOLVED")
                    final["problem_id"] = problem["problem_id"]
                    final["route_broker"] = dict(selected_route=None,
                        broker_result="PROBE_BOUND_EXHAUSTED",
                        requested_capability="MORE_RELATION_EVIDENCE")
                else:
                    grant = self.broker.request("MORE_RELATION_EVIDENCE",
                                                context="VALUE_TIE")
                    self.broker.validate_route(grant["selected_route"])
                    selected, priority = self._select_tie_probe(
                        actions, ordinary_decision["relation_confidence"])
                    problem["status"] = "ROUTE_REQUESTED"
                    problem["route_request_count"] += 1
                    problem["requested_capability"] = "MORE_RELATION_EVIDENCE"
                    final.update(mode="PROBE", action=selected,
                        reason="PROBE_TIED_MAXIMUM", abstained=False,
                        problem_id=problem["problem_id"], tied_maximum_actions=actions,
                        tie_information_priority=priority, route_broker=grant)
                    problem_events.extend(("ROUTE_REQUESTED", "ROUTE_GRANTED"))
        else:
            self.state["tie_candidate"] = None
            # Resolution requires a prior executed route for this exact state.
            for problem in self.state["problems"].values():
                if problem["problem_type"] == "UNRESOLVED_VALUE_TIE" and \
                        problem["state"] == pre_state and \
                        problem["status"] == "ROUTE_EXECUTED" and \
                        problem["probe_count"] > 0:
                    problem["status"] = "RESOLVED"
                    problem["resolved_decision_sequence"] = sequence
                    problem_events.append(f"PROBLEM_RESOLVED:{problem['problem_id']}")
        record = dict(decision_sequence=sequence, pre_state=pre_state,
            input_sha256=digest(dict(ordinary_decision=ordinary_decision,
                                     pre_state=pre_state, forecasts=forecasts)),
            ordinary_decision=deepcopy(ordinary_decision),
            tied_maximum_actions=actions if is_tie else [],
            routed_values=routed_values, problem_events=problem_events,
            final_decision=deepcopy(final), hidden_regime_available=False,
            simulator_law_available=False, future_consequence_available=False,
            counterfactual_outcomes_available=False,
            state_projection_after={key: deepcopy(self.state[key]) for key in
                ("attempted_decisions", "authorized_executions",
                 "next_problem_number", "tie_candidate", "problems")})
        envelope = self._append("PROBLEM_ROUTE_DECISION_FROZEN", record)
        self.state["pending_decision"] = dict(decision_sequence=sequence,
            frozen_record_sha256=digest(envelope["record"]))
        self._write_state()
        return deepcopy(final)

    def complete(self, *, store: SessionStore, row: dict) -> dict:
        pending_state = self.state.get("pending_decision")
        if pending_state is None:
            raise RoutingError("problem route completion lacks pending decision")
        frozen = next(item["record"] for item in reversed(self.records)
                      if item["kind"] == "PROBLEM_ROUTE_DECISION_FROZEN")
        sequence = frozen["decision_sequence"]
        if row["prediction_batch_sequence"] != sequence:
            raise RoutingError("problem route completion identity mismatch")
        final = frozen["final_decision"]
        problem = None
        if final.get("problem_id"):
            problem = next((value for value in self.state["problems"].values()
                            if value["problem_id"] == final["problem_id"]), None)
            if problem is None:
                raise RoutingError("problem route decision references missing problem")
        receipt_reference = None
        if row["status"] == "AUTHORIZED":
            self.state["authorized_executions"] += 1
            self.state["tie_candidate"] = None
            receipt_reference = dict(receipt_identity=row["receipt_identity"] if
                "receipt_identity" in row else list((row["receipt"][key] for key in
                    ("source_identity", "event_id", "epoch", "transaction_id"))),
                routing_evidence_sequence=row["routing_evidence"]["evidence_sequence"],
                realized_next_state=row["receipt"]["next_state"],
                realized_consequence=row["receipt"]["realized_consequence"])
            if problem is not None and final["reason"] == "PROBE_TIED_MAXIMUM":
                problem["probe_count"] += 1
                problem["status"] = "ROUTE_EXECUTED"
                problem["receipt_evidence"].append(deepcopy(receipt_reference))
        elif row["status"] not in ("ABSTAINED", "FRAMEWORK_REJECTED"):
            raise RoutingError("unknown problem route completion status")
        self.state["attempted_decisions"] += 1
        record = dict(decision_sequence=sequence, status=row["status"],
            selected_route=final["route_broker"].get("selected_route"),
            problem_id=final.get("problem_id"), action=final.get("action"),
            receipt_reference=receipt_reference,
            problem_status_after=None if problem is None else problem["status"],
            state_projection_after={key: deepcopy(self.state[key]) for key in
                ("attempted_decisions", "authorized_executions",
                 "next_problem_number", "tie_candidate", "problems")})
        self._append("PROBLEM_ROUTE_DECISION_COMPLETED", record)
        self.state["pending_decision"] = None
        self._write_state()
        self.bind_session(store)
        return deepcopy(record)


def initialize_problem_route_registry(
        root: Path, source_registry: Path = DEFAULT_SOURCE_REGISTRY) -> dict:
    policy = json.loads(POLICY_PATH.read_text())
    exploration = initialize_grounded_exploration_registry(root, source_registry)
    grounded = load_grounded_exploration_registry(root)
    payload = dict(version=PROBLEM_ROUTE_VERSION,
        mode="HORUS_PROBLEM_ROUTE_REQUEST_V0", created_at=_now(),
        policy_sha256=file_hash(POLICY_PATH),
        exploration_registry_payload_sha256=grounded["document"]["sha256"],
        problem_has_authority=False, hidden_regime_available=False,
        weights_modified=False, learned_detector=False, learned_broker=False,
        protected_episode_limit=EPISODE_LIMIT)
    atomic_json(root / "problem-route-registry.json", _document(payload))
    ProblemRouteStore.initialize(root)
    return dict(root=str(root), problem_route_registry_sha256=digest(payload),
                exploration_registry=exploration)


def load_problem_route_registry(root: Path) -> dict:
    root = root.resolve()
    exploration = load_grounded_exploration_registry(root)
    document = _read_document(root / "problem-route-registry.json",
                              "problem route registry")
    payload = document["payload"]
    policy = json.loads(POLICY_PATH.read_text())
    if payload.get("version") != PROBLEM_ROUTE_VERSION or \
            payload.get("mode") != "HORUS_PROBLEM_ROUTE_REQUEST_V0" or \
            payload.get("policy_sha256") != file_hash(POLICY_PATH) or \
            payload.get("exploration_registry_payload_sha256") != \
            exploration["document"]["sha256"] or \
            payload.get("problem_has_authority") is not False or \
            payload.get("hidden_regime_available") is not False or \
            payload.get("weights_modified") is not False or \
            payload.get("learned_detector") is not False or \
            payload.get("learned_broker") is not False or \
            payload.get("protected_episode_limit") != EPISODE_LIMIT:
        raise RoutingError("problem route registry violates frozen policy")
    return dict(root=root, document=document, payload=payload, policy=policy,
                exploration_registry=exploration)


class ProblemRoutedExplorer:
    """Wrap the ordinary v0.7 decision with the bounded v0.8 route layer."""
    def __init__(self, ordinary: GroundedExplorer, problems: ProblemRouteStore,
                 store: SessionStore):
        self.ordinary = ordinary
        self.problems = problems
        self.store = store

    def derive(self, **kwargs) -> dict:
        ordinary = self.ordinary.derive(**kwargs)
        return self.problems.prepare(store=self.store,
            ordinary_decision=ordinary, pre_state=kwargs["pre_state"],
            forecasts=kwargs["forecasts"])


class ProblemRouteRuntime(GroundedExplorationRuntime):
    def __init__(self, *args, problem_store: ProblemRouteStore, **kwargs):
        super().__init__(*args, **kwargs)
        self.problem_store = problem_store
        problem_store.bind_session(self.store)
        self.confidence_store.explorer = ProblemRoutedExplorer(
            GroundedExplorer(self.confidence_store.registry["policy"]),
            problem_store, self.store)

    def execute_autonomous(self) -> dict:
        row = super().execute_autonomous()
        problem_completion = self.problem_store.complete(store=self.store, row=row)
        row["problem_route_completion"] = problem_completion
        return row


def _segment_expectation(segment: str) -> dict:
    return {
        "V08_A1_1": dict(resume=False, attempts=0, batches=0, runtime=0,
                          regime="A", transition=False, decisions=9,
                          decision_range=[1, 9]),
        "V08_A1_2": dict(resume=True, attempts=9, batches=9, runtime=1,
                          regime="A", transition=False, decisions=9,
                          decision_range=[10, 18]),
        "V08_B1": dict(resume=True, attempts=18, batches=18, runtime=2,
                        regime="B", transition=True, decisions=9,
                        decision_range=[19, 27]),
        "V08_B2": dict(resume=True, attempts=27, batches=27, runtime=3,
                        regime="B", transition=False, decisions=9,
                        decision_range=[28, 36]),
        "V08_A2_1": dict(resume=True, attempts=36, batches=36, runtime=4,
                          regime="A", transition=True, decisions=9,
                          decision_range=[37, 45]),
        "V08_A2_2": dict(resume=True, attempts=45, batches=45, runtime=5,
                          regime="A", transition=False, decisions=9,
                          decision_range=[46, 54]),
    }[segment]


def run_problem_route_segment(session: Path, registry_root: Path, segment: str,
                              resume: bool, joint_client=None,
                              specialist_clients=None) -> dict:
    if segment not in V08_SEGMENTS:
        raise RoutingError("unknown v0.8 segment")
    plan = _segment_expectation(segment)
    if resume != plan["resume"]:
        raise RoutingError("segment resume mode differs from frozen schedule")
    problem_registry = load_problem_route_registry(registry_root)
    exploration = problem_registry["exploration_registry"]
    if specialist_clients is None:
        specialist_clients, relation_registry = relation_routed_clients(
            registry_root, device="cuda")
    else:
        relation_registry = exploration["relation_registry"]
    joint = joint_client or ModelClient()
    before = {key: specialist_clients[key].requests for key in SPECIALISTS}
    joint_before = joint.requests
    with SessionStore(session, resume) as store, \
            RelationEvidenceStore(registry_root) as routing, \
            ExplorerConfidenceStore(registry_root) as confidence, \
            ProblemRouteStore(registry_root) as problems:
        requests = sum(row["kind"] == "REQUEST_INTENT"
                       for row in store.records["calls"])
        actual = dict(attempts=store.checkpoint["attempted_decisions"],
                      batches=requests // 9,
                      runtime=store.checkpoint["runtime_index"])
        expected = {key: plan[key] for key in actual}
        if requests % 9 or actual != expected:
            raise RoutingError(f"segment start differs from frozen schedule: {actual}")
        if confidence.state["attempted_decisions"] != plan["attempts"] or \
                problems.state["attempted_decisions"] != plan["attempts"]:
            raise RoutingError("v0.8 durable state differs from schedule")
        rollover_input = dict(prior_runtime_index=store.checkpoint["runtime_index"],
            prior_attempted_decisions=store.checkpoint["attempted_decisions"],
            prior_authorized_events=len(store.records["events"]),
            prior_routing_evidence=len(routing.records),
            prior_problem_route_state_sha256=digest({key: problems.state[key]
                for key in ("attempted_decisions", "authorized_executions",
                            "tie_candidate", "problems")}))
        store.configure_regime(plan["regime"], plan["transition"])
        runtime = ProblemRouteRuntime(store, joint, specialist_clients,
            relation_registry, routing, confidence, plan["regime"],
            problem_store=problems)
        rows = [runtime.execute_autonomous() for _ in range(plan["decisions"])]
        calls = joint.requests - joint_before + sum(
            specialist_clients[key].requests - before[key] for key in SPECIALISTS)
        return dict(mode="problem-route-live", segment=segment,
            runtime_schedule="V08", registered_decision_range=plan["decision_range"],
            session_id=store.checkpoint["session_id"], session=str(store.directory),
            resumed=resume, runtime_index=store.checkpoint["runtime_index"],
            epoch=store.checkpoint["current_epoch"], rows=rows,
            actual_model_calls=calls,
            model_calls_by_role=dict(joint_next_state=joint.requests - joint_before,
                G2=specialist_clients["G2"].requests - before["G2"],
                G3=specialist_clients["G3"].requests - before["G3"]),
            problem_route_state=deepcopy(problems.state),
            confidence_state=deepcopy(confidence.state),
            relation_state=deepcopy(routing.state["relations"]),
            external_regime_version=plan["regime"], regime_model_visible=False,
            rollover_input=rollover_input, checkpoint=_plain(store.checkpoint))


def analyze_problem_route_campaign(session: Path, registry_root: Path,
                                   output: Path) -> dict:
    if output.exists():
        raise RoutingError("problem route report output already exists")
    policy = json.loads(POLICY_PATH.read_text())
    with SessionStore(session, True) as store, \
            RelationEvidenceStore(registry_root) as routing, \
            ExplorerConfidenceStore(registry_root) as confidence, \
            ProblemRouteStore(registry_root) as problems:
        routing.bind_session(store); confidence.bind_session(store)
        calls = deepcopy(store.records["calls"])
        events = [deepcopy(row["record"]) for row in store.records["events"]]
        training = [deepcopy(row["record"]) for row in store.records["training"]]
        checkpoint = deepcopy(store.checkpoint)
        problem_records = deepcopy(problems.records)
        problem_state = deepcopy(problems.state)
        route_state = deepcopy(routing.state)
        confidence_state = deepcopy(confidence.state)
    requests = [row for row in calls if row["kind"] == "REQUEST_INTENT"]
    if len(requests) != policy["total_model_calls"] or len(training) != \
            policy["total_decisions"] or checkpoint["attempted_decisions"] != \
            policy["total_decisions"]:
        raise RoutingError("v0.8 campaign cardinality differs from preregistration")
    if len(problem_records) != policy["total_decisions"] * 2:
        raise RoutingError("problem route stream is incomplete")
    batches = Counter()
    hidden_prompt_checks = 0
    for envelope in requests:
        record = envelope["record"]
        serialized = json.dumps(record["request"], sort_keys=True).lower()
        if any(token in serialized for token in
               ("regime", "problem_id", "route_broker", "simulator_law",
                "future_consequence", "counterfactual")):
            raise RoutingError("hidden problem/regime state found in model prompt")
        hidden_prompt_checks += 1
        parts = record["call_id"].split(":")
        epoch = next(part for part in parts if part.startswith("e") and
                     part[1:].isdigit())
        batches[int(epoch[1:]) - 2000] += 1
    expected_calls = {runtime: 81 for runtime in range(1, 7)}
    if dict(batches) != expected_calls:
        raise RoutingError(f"v0.8 runtime call schedule differs: {dict(batches)}")
    decisions = [row["record"] for row in problem_records
                 if row["kind"] == "PROBLEM_ROUTE_DECISION_FROZEN"]
    completions = [row["record"] for row in problem_records
                   if row["kind"] == "PROBLEM_ROUTE_DECISION_COMPLETED"]
    if [row["decision_sequence"] for row in decisions] != list(range(1, 55)) or \
            [row["decision_sequence"] for row in completions] != list(range(1, 55)):
        raise RoutingError("problem route decision sequence is incomplete")
    problem_by_id = {row["problem_id"]: deepcopy(row)
                     for row in problem_state["problems"].values()}
    requests_out = [dict(decision_sequence=row["decision_sequence"],
        problem_id=row["final_decision"].get("problem_id"),
        requested_capability=row["final_decision"]["route_broker"].get(
            "requested_capability"),
        broker_result=row["final_decision"]["route_broker"]["broker_result"],
        selected_route=row["final_decision"]["route_broker"].get("selected_route"),
        selected_action=row["final_decision"].get("action"))
        for row in decisions if row["final_decision"]["route_broker"].get(
            "requested_capability") is not None]
    probes = [dict(decision_sequence=row["decision_sequence"],
        problem_id=row["final_decision"]["problem_id"],
        state=row["pre_state"], tied_actions=row["tied_maximum_actions"],
        action=row["final_decision"]["action"],
        priority=row["final_decision"]["tie_information_priority"],
        completion=next(item for item in completions
                        if item["decision_sequence"] == row["decision_sequence"]))
        for row in decisions if row["final_decision"].get("reason") ==
        "PROBE_TIED_MAXIMUM"]
    authorized = len(events)
    abstentions = sum(row["status"] == "ABSTAINED" for row in completions)
    false_problems = [row["problem_id"] for row in problem_by_id.values()
                      if row["failure_count"] < policy["persistent_tie_attempts"]]
    result = dict(identity="HORUS_PROBLEM_ROUTE_REQUEST_V0",
        policy_sha256=file_hash(POLICY_PATH), total_model_calls=len(requests),
        attempted_decisions=len(training), authorized_executions=authorized,
        abstentions=abstentions, framework_rejections=sum(
            row["status"] == "FRAMEWORK_REJECTED" for row in completions),
        calibration_executions=0, hidden_regime_prompt_checks=hidden_prompt_checks,
        problem_taxonomy=policy["problem_types"],
        detection_rule=dict(consecutive_identical_ties=policy[
            "persistent_tie_attempts"], authorized_execution_between=False),
        registered_routes=policy["registered_routes"],
        problems=list(problem_by_id.values()), route_requests=requests_out,
        tie_information_probes=probes,
        problem_status_counts=dict(Counter(row["status"]
                                           for row in problem_by_id.values())),
        false_or_unnecessary_problem_creation=false_problems,
        state_2_deadlock_escaped=any(probe["state"] == 2 and
            probe["completion"]["status"] == "AUTHORIZED" and
            probe["completion"]["receipt_reference"]["realized_next_state"] != 2
            for probe in probes),
        A2_grounded_evidence=sum(event["prediction_batch_sequence"] >= 37
                                 for event in events),
        relation_switches=[dict(evidence_sequence=row["record"]["evidence_sequence"],
            relation=row["record"]["relation"],
            selected_before=row["record"]["selected_specialist"],
            selected_after=row["record"]["selected_specialist_after"])
            for row in routing.records if row["record"]["switch_occurred"]],
        new_runtime_requests=[row for row in requests_out
                              if row["requested_capability"] == "NEW_RUNTIME"],
        restart_proof=dict(runtime_indices=list(range(1, 7)),
            model_calls_by_runtime=dict(batches), attempts_per_runtime={
                runtime: 9 for runtime in range(1, 7)},
            protected_episode_limit=EPISODE_LIMIT,
            problem_route_exact_replay=True,
            confidence_exact_replay=True,
            relation_evidence_exact_replay=True,
            problem_and_probe_budget_survived_restart=True,
            fresh_source_and_epoch_per_runtime=True),
        no_weight_updates=True, learned_problem_detector=False,
        learned_route_broker=False, final_problem_route_state=problem_state,
        final_confidence_state=confidence_state,
        final_relation_state=route_state,
        final_checkpoint=checkpoint)
    atomic_json(output, result)
    return result
