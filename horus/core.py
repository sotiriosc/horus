"""Minimal grounded Horus v0 application composition.

The existing research framework owns execution, receipts, Measure,
authorization, Recovery, and Memory. This module supplies replaceable predictor
and Explorer interfaces plus a thin coordinator; it does not mint observations.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from hashlib import sha256
from hmac import compare_digest, new as new_hmac
import json
import os
from pathlib import Path
from typing import Protocol

from experiments.base_framework_v0.framework import ACTION_ORDER, MapModel, Prediction
from experiments.cross_episode_initialization_boundary_v1.boundary import EpisodeController, EpisodePlan
from experiments.cross_episode_initialization_boundary_v1.campaign import snap
from experiments.map_guided_explorer_interface_v0.interface import AuthenticatedReader
from experiments.map_consequence_only_isolation_v0.protocol import parse as parse_consequence
from experiments.realized_event_grounding_v0.framework import evidence


MAPPING = {"K1": "ADVANCE", "K2": "HOLD", "K3": "RETREAT"}


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value) -> str:
    return sha256(canonical(value).encode()).hexdigest()


@dataclass(frozen=True)
class GroundedObservation:
    epoch: int
    transaction_id: int
    surface_action: str
    next_state: int
    consequence: int


@dataclass(frozen=True)
class NextStateInput:
    state: int
    action: str
    action_alias: str
    epoch: int
    transaction_id: int
    authenticated_history: tuple[GroundedObservation, ...]
    memory_sha256: str


@dataclass(frozen=True)
class ConsequenceInput:
    """No predicted-next-state field exists at this interface boundary."""
    state: int
    action: str
    action_alias: str
    epoch: int
    transaction_id: int
    authenticated_history: tuple[GroundedObservation, ...]
    memory_sha256: str


class NextStatePredictor(Protocol):
    def predict(self, value: NextStateInput) -> int | None: ...


class ConsequencePredictor(Protocol):
    def predict(self, value: ConsequenceInput) -> int | None: ...


@dataclass(frozen=True)
class MapForecast:
    action: str
    action_alias: str
    next_state: int | None
    consequence: int | None
    abstained: bool
    failure: str | None
    history_count: int
    input_context: dict


@dataclass(frozen=True)
class ExplorerChoice:
    action: str | None
    reason: str
    abstained: bool


class ExistingJointNextStatePredictor:
    """Use the existing joint Map path, consuming only its next_state field."""
    def predict(self, value: NextStateInput) -> int | None:
        joint = MapModel.predict_from(value.state, value.action, value.epoch,
                                     value.transaction_id)
        return joint.next_state


class AuthenticatedHistoryConsequencePredictor:
    """Small deterministic v0 adapter for the independent consequence boundary.

    All authenticated contradictory observations remain in the input. Their
    finite sum is reduced to its sign; untried and exactly balanced histories
    return neutral 0. This is an engineering baseline, not a learned Map claim.
    """
    def predict(self, value: ConsequenceInput) -> int | None:
        total = sum(item.consequence for item in value.authenticated_history)
        consequence = 1 if total > 0 else -1 if total < 0 else 0
        # Reuse the established strict one-field consequence parser/domain.
        return parse_consequence(json.dumps({"consequence": consequence}), "C")["consequence"]


class MechanicalExplorer:
    """Finite consequence comparison plus one explicit bounded tie fallback."""
    def choose(self, forecasts: tuple[MapForecast, ...]) -> ExplorerChoice:
        if len(forecasts) != len(ACTION_ORDER) or {f.action for f in forecasts} != set(ACTION_ORDER):
            return ExplorerChoice(None, "INCOMPLETE_FORECAST_SET", True)
        if any(f.abstained or f.consequence not in (-1, 0, 1) for f in forecasts):
            return ExplorerChoice(None, "INVALID_MAP_COMPONENT", True)
        maximum = max(f.consequence for f in forecasts)
        leaders = [f for f in forecasts if f.consequence == maximum]
        if len(leaders) == 1:
            return ExplorerChoice(leaders[0].action, "UNIQUE_MAXIMUM", False)
        untried = [f for f in leaders if f.history_count == 0]
        if untried:
            chosen = min(untried, key=lambda f: ACTION_ORDER.index(f.action))
            return ExplorerChoice(chosen.action, "BOUNDED_FIRST_UNTRIED_TIE_FALLBACK", False)
        return ExplorerChoice(None, "TIED_MAXIMUM", True)


class SplitMapV0:
    def __init__(self, next_state: NextStatePredictor | None = None,
                 consequence: ConsequencePredictor | None = None):
        self.next_state = next_state or ExistingJointNextStatePredictor()
        self.consequence = consequence or AuthenticatedHistoryConsequencePredictor()

    @staticmethod
    def _history(payload) -> tuple[GroundedObservation, ...]:
        return tuple(GroundedObservation(**row)
                     for row in payload["VERIFIED_CHRONOLOGICAL_HISTORY"])

    def forecast(self, capture: dict, action: str) -> MapForecast:
        payload = capture["map_inputs"][action]
        history = self._history(payload)
        shared = dict(state=capture["state"], action=action,
            action_alias=payload["target_action"], epoch=capture["epoch"],
            transaction_id=capture["transaction_id"], authenticated_history=history,
            memory_sha256=capture["memory_sha256"])
        next_value = self.next_state.predict(NextStateInput(**shared))
        # ConsequenceInput cannot carry next_value by construction.
        consequence_value = self.consequence.predict(ConsequenceInput(**shared))
        valid_next = type(next_value) is int and next_value in range(4)
        valid_consequence = type(consequence_value) is int and consequence_value in (-1, 0, 1)
        abstained = not (valid_next and valid_consequence)
        return MapForecast(action, payload["target_action"],
            next_value if valid_next else None,
            consequence_value if valid_consequence else None,
            abstained, None if not abstained else "INVALID_COMPONENT",
            len(history), dict(state=shared["state"], action=action,
                action_alias=shared["action_alias"], epoch=shared["epoch"],
                transaction_id=shared["transaction_id"],
                authenticated_history=[asdict(row) for row in history],
                memory_sha256=shared["memory_sha256"]))

    def forecasts(self, capture: dict) -> tuple[MapForecast, ...]:
        return tuple(self.forecast(capture, action) for action in ACTION_ORDER)


class BoundPredictionMap:
    """One-decision adapter binding a split forecast into existing Measure."""
    def __init__(self, base, prediction: Prediction):
        self.base = base
        self.prediction = prediction

    def __deepcopy__(self, memo):
        clone = type(self)(deepcopy(self.base, memo), self.prediction)
        memo[id(self)] = clone
        return clone

    @property
    def current(self): return self.base.current

    @property
    def quarantine(self): return self.base.quarantine

    def commit(self, value, epoch): self.base.commit(value, epoch)

    def quarantine_incumbent(self): self.base.quarantine_incumbent()

    def predict(self, action, epoch, transaction_id):
        expected = (epoch, transaction_id, self.current.state, action)
        actual = (self.prediction.epoch, self.prediction.transaction_id,
                  self.prediction.pre_state, self.prediction.action)
        if actual != expected:
            raise ValueError("bound prediction identity mismatch")
        return self.prediction


def unwrap_map(value):
    while isinstance(value, BoundPredictionMap):
        value = value.base
    return value


class CheckpointAuthority:
    """Process-local trusted checkpoint authority for a live source lifetime.

    The file is authenticated with an in-memory key. Restore deliberately
    retains the same controller and source objects; durable cross-process root
    restoration remains outside Horus v0.
    """
    def __init__(self, key: bytes | None = None):
        self._key = key or os.urandom(32)
        self._live = {}

    def save(self, runtime: "HorusRuntime", path: Path) -> dict:
        snapshot = snap(runtime.controller)
        checkpoint_id = digest({"source": runtime.controller._source_identity,
                                "snapshot": snapshot, "steps": len(runtime.steps)})
        payload = dict(version=1, checkpoint_id=checkpoint_id,
            source_identity=runtime.controller._source_identity,
            snapshot=snapshot, steps=len(runtime.steps))
        mac = new_hmac(self._key, canonical(payload).encode(), "sha256").hexdigest()
        document = dict(payload=payload, hmac_sha256=mac)
        path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
        self._live[checkpoint_id] = (runtime.controller, runtime.authentic,
                                     runtime.executions, list(runtime.steps))
        return dict(checkpoint_id=checkpoint_id, path=str(path), verified=True)

    def resume(self, path: Path, split_map: SplitMapV0 | None = None,
               explorer: MechanicalExplorer | None = None) -> "HorusRuntime":
        document = json.loads(path.read_text())
        payload = document["payload"]
        expected = new_hmac(self._key, canonical(payload).encode(), "sha256").hexdigest()
        if not compare_digest(expected, document.get("hmac_sha256", "")):
            raise ValueError("checkpoint authentication failed")
        saved = self._live.get(payload["checkpoint_id"])
        if saved is None:
            raise ValueError("checkpoint source lifetime unavailable")
        controller, authentic, executions, steps = saved
        if snap(controller) != payload["snapshot"]:
            raise ValueError("live protected state differs from checkpoint")
        return HorusRuntime(controller, split_map=split_map, explorer=explorer,
                            authentic=authentic, executions=executions, steps=steps)


class HorusRuntime:
    def __init__(self, controller: EpisodeController | None = None,
                 split_map: SplitMapV0 | None = None,
                 explorer: MechanicalExplorer | None = None,
                 authentic=None, executions=None, steps=None):
        self.controller = controller or EpisodeController(
            "HORUS_V0_DEMO_SOURCE", EpisodePlan(initial_state=1))
        self.split_map = split_map or SplitMapV0()
        self.explorer = explorer or MechanicalExplorer()
        self.authentic = authentic if authentic is not None else {}
        self.executions = executions if executions is not None else {}
        self.steps = steps if steps is not None else []

    def start_episode(self, epoch: int = 1002, initial_state: int = 1) -> dict:
        return self.controller.start_episode(epoch, initial_state)

    def step(self, episode: int) -> dict:
        reader = AuthenticatedReader(self.controller, self.authentic, self.executions)
        capture = reader.capture(MAPPING)
        forecasts = self.split_map.forecasts(capture)
        choice = self.explorer.choose(forecasts)
        if choice.abstained:
            row = dict(episode=episode, state=capture["state"], memory_used={
                f.action: f.input_context["authenticated_history"] for f in forecasts},
                map_forecasts=[asdict(f) for f in forecasts], explorer=asdict(choice),
                status="ABSTAINED")
            self.steps.append(row)
            return row
        selected = next(f for f in forecasts if f.action == choice.action)
        prediction = Prediction(capture["epoch"], capture["transaction_id"],
            capture["state"], selected.action, selected.next_state, selected.consequence)
        core = self.controller._active.framework.inner
        core.map = BoundPredictionMap(unwrap_map(core.map), prediction)
        before = snap(self.controller)
        pending = self.controller.begin_step(selected.action)
        if asdict(pending.prediction) != asdict(prediction):
            raise RuntimeError("split prediction was not latched")
        if self.controller._source.reader().current() is not None:
            raise RuntimeError("receipt existed before execution")
        receipt = self.controller.execute_pending()
        actual = asdict(self.controller._active.world.last_actual)
        self.authentic[receipt.identity()] = receipt
        self.executions[receipt.identity()] = actual
        result = self.controller.submit_package(evidence(receipt))
        if not result.committed or not result.continued:
            self.controller.release(receipt)
            raise RuntimeError(f"grounded publication rejected: {result.reason}")
        record = self.controller._active.framework.inner.memory.records[-1]
        package = self.controller._active.framework.packages[-1]
        if package.receipt is not receipt:
            raise RuntimeError("published receipt object was substituted")
        self.controller.release(receipt)
        after = snap(self.controller)
        training_record = dict(
            input_context=selected.input_context, chosen_action=selected.action,
            predicted_next_state=selected.next_state,
            predicted_consequence=selected.consequence,
            realized_next_state=receipt.next_state,
            realized_consequence=receipt.realized_consequence,
            receipt_identity=list(receipt.identity()),
            authorization_status=result.status.value,
            memory_identity=[record.epoch, record.transaction_id, record.pair_decision_id],
            memory_reference=dict(index=len(after["protected"]["memory"]) - 1,
                                  protected_memory_sha256=digest(after["protected"]["memory"])))
        row = dict(episode=episode, state=capture["state"],
            epoch=capture["epoch"], transaction_id=capture["transaction_id"],
            memory_used={f.action: f.input_context["authenticated_history"] for f in forecasts},
            memory_sha256=capture["memory_sha256"],
            map_forecasts=[asdict(f) for f in forecasts], explorer=asdict(choice),
            prediction=asdict(prediction), receipt=asdict(receipt), actual=actual,
            prediction_match=record.measurement_matches,
            authorization=asdict(result), memory_published=asdict(record),
            original_receipt_object=True, before=before, after=after,
            training_record=training_record, status="AUTHORIZED")
        self.steps.append(row)
        return row


def run_demo(output: Path) -> dict:
    runtime = HorusRuntime()
    first = runtime.step(1)
    authority = CheckpointAuthority()
    checkpoint_path = output.with_suffix(output.suffix + ".checkpoint.json")
    checkpoint = authority.save(runtime, checkpoint_path)
    runtime = authority.resume(checkpoint_path)
    boundary = runtime.start_episode(1002, 1)
    second = runtime.step(2)
    changed = first["explorer"]["action"] != second["explorer"]["action"]
    causal_record = second["memory_used"][first["explorer"]["action"]]
    if not changed or not causal_record:
        raise RuntimeError("grounded experience did not change later behavior")
    artifact = dict(application="horus-v0-closed-loop", model_calls=0,
        architecture="joint-next-state + independent-history-consequence + mechanical reconciliation",
        episodes=runtime.steps, checkpoint=checkpoint, episode_boundary=boundary,
        experience_changed_later_behavior=True,
        causal_moment=dict(earlier_action=first["explorer"]["action"],
            earlier_receipt_identity=first["training_record"]["receipt_identity"],
            later_memory_used=causal_record,
            later_action=second["explorer"]["action"]),
        training_records=[row["training_record"] for row in runtime.steps],
        final_protected_memory=second["after"]["protected"]["memory"],
        claims=dict(general_learning=False, weight_updates=False,
            production_split_map_established=False,
            checkpoint_scope="authenticated process-local restart; not durable source-root recovery"))
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
    return artifact
