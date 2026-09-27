from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
from hmac import new as new_hmac
import json
import os
from pathlib import Path
import shutil
import time
from typing import Any

from experiments.base_framework_v0.framework import ACTION_ORDER, MapModel
from experiments.map_consequence_only_isolation_v0.protocol import parse as parse_consequence
from horus.core import MapForecast, MechanicalExplorer, digest
from horus.grounded_exploration import GroundedExplorer
from horus.grounded_learning import QwenConsequenceClient
from horus.relation_routing import (
    RelationGroundedRouter,
    relation_identity,
    relation_key,
)

from .zakhor_runtime.controller import LivingMemoryController
from .zakhor_runtime.config import MemoryConfig


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "research/horus-zakhor-component-attribution-v0"
SOURCE_REGISTRY = ROOT / "research/learning-stability-v0/registry"
CONDITIONS = {
    "F": (False, False),
    "H": (True, False),
    "Z": (False, True),
    "HZ": (True, True),
}
ORDER = ("F", "HZ", "H", "Z")
ALIASES = {"ADVANCE": "K1", "HOLD": "K2", "RETREAT": "K3"}
STAGE_A = (
    (1, "ADVANCE", "stable"), (1, "HOLD", "stable"),
    (1, "ADVANCE", "stable"), (1, "HOLD", "stable"),
    (2, "RETREAT", "stable"),
    (1, "ADVANCE", "change"), (1, "HOLD", "change"),
    (1, "ADVANCE", "change"), (1, "HOLD", "change"),
    (1, "ADVANCE", "change"), (1, "HOLD", "change"),
    (1, "ADVANCE", "restoration"), (1, "HOLD", "restoration"),
    (1, "ADVANCE", "restoration"), (1, "HOLD", "restoration"),
    (1, "ADVANCE", "restoration"), (1, "HOLD", "restoration"),
    (2, "RETREAT", "restoration"),
)
STAGE_B_REGIMES = ("stable", "stable", "change", "change", "restoration", "restoration")
RESTART_BEFORE_STAGE_A = 10
PERTURB_STAGE_A = 14
ROLLING_WINDOW = 6


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def file_hash(path: Path) -> str:
    h = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def consequence(state: int, action: str, phase: str) -> int:
    base = MapModel.predict_from(state, action, 1, 1).consequence
    if phase == "change" and state == 1:
        if action == "ADVANCE":
            return 1
        if action == "HOLD":
            return -1
    return base


def next_state(state: int, action: str) -> int:
    return MapModel.predict_from(state, action, 1, 1).next_state


class Chain:
    """Append-only HMAC chain used equally by all four arms."""
    def __init__(self, path: Path, key: bytes):
        self.path, self.key = path, key
        self.previous = None
        self.sequence = 0
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("")

    def append(self, kind: str, record: dict) -> dict:
        self.sequence += 1
        signed = dict(sequence=self.sequence, previous_sha256=self.previous,
                      kind=kind, record=record)
        envelope = {**signed, "hmac_sha256": new_as_hex(self.key, signed)}
        line = canonical(envelope)
        with self.path.open("a") as stream:
            stream.write(line + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        self.previous = sha256(line.encode()).hexdigest()
        return envelope


def new_as_hex(key: bytes, value: Any) -> str:
    return new_hmac(key, canonical(value).encode(), "sha256").hexdigest()


def adapter_paths() -> dict[str, Path]:
    return {
        "G2": SOURCE_REGISTRY / "generations/generation-0002/model/trained-adapter.safetensors",
        "G3": SOURCE_REGISTRY / "generations/generation-0003/model/trained-adapter.safetensors",
    }


class Arm:
    def __init__(self, name: str, output: Path):
        self.name = name
        self.horus_enabled, self.zakhor_enabled = CONDITIONS[name]
        self.output = output
        self.key = sha256(("horus-zakhor-v0:" + name).encode()).digest()
        self.chain = Chain(output / "records.jsonl", self.key)
        self.models: dict[str, QwenConsequenceClient] = {}
        self.controllers: dict[str, LivingMemoryController] = {}
        self.receipts: list[dict] = []
        self.routing_rows: list[dict] = []
        self.route_selected: dict[str, str] = {}
        self.router = RelationGroundedRouter() if self.horus_enabled else None
        self.explorer = GroundedExplorer() if self.horus_enabled else None
        self.mechanical = MechanicalExplorer()
        self.confidence = dict(attempted_decisions=0, authorized_decisions=0,
            last_probe_decision_sequence=None, last_probe_authorized_decision=None,
            last_execution_by_relation={}, unresolved_contradictions={})
        self.epoch = 7001
        self.runtime = 1
        self.source = f"ATTRIBUTION:{name}:runtime:1"
        self.calls = 0
        self.wall_model_seconds = 0.0

    def load_models(self) -> None:
        for specialist, path in adapter_paths().items():
            identity = dict(specialist_id=specialist,
                artifact_sha256=file_hash(path), base_model="Qwen/Qwen2.5-0.5B-Instruct")
            client = QwenConsequenceClient(path, device="cuda", model_identity=identity)
            self.models[specialist] = client
            if self.zakhor_enabled:
                controller = LivingMemoryController(client.model, mode="keeper",
                    cfg=MemoryConfig(), policy="soft", use_gpu_keeper=True).attach()
                self.controllers[specialist] = controller

    def unload_models(self) -> None:
        for controller in self.controllers.values():
            controller.detach()
        self.controllers.clear()
        self.models.clear()
        try:
            import gc, torch
            gc.collect()
            torch.cuda.empty_cache()
        except Exception:
            pass

    def zakhor_snapshot(self) -> dict | None:
        if not self.zakhor_enabled:
            return None
        return {name: controller.tracker_snapshots()
                for name, controller in self.controllers.items()}

    def restart(self) -> dict:
        before = self.zakhor_snapshot()
        for controller in self.controllers.values():
            controller.detach()
        self.controllers = {}
        if self.zakhor_enabled:
            for specialist, client in self.models.items():
                self.controllers[specialist] = LivingMemoryController(
                    client.model, mode="keeper", cfg=MemoryConfig(), policy="soft",
                    use_gpu_keeper=True).attach()
        self.runtime += 1
        self.epoch += 1
        self.source = f"ATTRIBUTION:{self.name}:runtime:{self.runtime}"
        after = self.zakhor_snapshot()
        record = dict(before_tracker_sha256=None if before is None else digest(before),
            after_tracker_sha256=None if after is None else digest(after),
            zakhor_state_restored=False if self.zakhor_enabled else None,
            horus_receipts_retained=len(self.receipts) if self.horus_enabled else None,
            horus_routing_rows_retained=len(self.routing_rows) if self.horus_enabled else None,
            new_epoch=self.epoch, new_source_identity=self.source,
            old_receipt_objects_reconstructed=False)
        self.chain.append("RUNTIME_RESTART", record)
        return record

    def history(self, state: int, action: str) -> list[dict]:
        if not self.horus_enabled:
            return []
        return [dict(epoch=r["epoch"], transaction_id=r["transaction_id"],
            surface_action=ALIASES[action], next_state=r["next_state"],
            consequence=r["realized_consequence"])
            for r in self.receipts if r["pre_state"] == state and r["action"] == action]

    def call(self, specialist: str, state: int, action: str, call_id: str,
             perturb: bool = False) -> dict:
        payload = dict(state=state, target_action=ALIASES[action],
            VERIFIED_CHRONOLOGICAL_HISTORY=self.history(state, action))
        from horus.live import CONSEQUENCE_SYSTEM
        request = dict(model=self.models[specialist].model_id,
            system=CONSEQUENCE_SYSTEM, prompt=canonical(payload), stream=False,
            options=dict(temperature=0, seed=20260926))
        request_hash = digest(request)
        self.chain.append("MODEL_REQUEST", dict(call_id=call_id,
            specialist=specialist, request_sha256=request_hash,
            horus_history_rows=len(payload["VERIFIED_CHRONOLOGICAL_HISTORY"]),
            zakhor_controller_attached=specialist in self.controllers))
        started = time.perf_counter()
        response = self.models[specialist].generate(request)
        elapsed = time.perf_counter() - started
        self.wall_model_seconds += elapsed
        self.calls += 1
        raw = response["raw_output"]
        if perturb and specialist == "G2":
            raw = '{"consequence":2}'
        parsed, error = None, None
        try:
            if response["transport_error"] is not None:
                raise RuntimeError(response["transport_error"])
            parsed = parse_consequence(raw, "C")["consequence"]
        except Exception as exc:
            error = type(exc).__name__
        record = dict(call_id=call_id, specialist=specialist,
            request_sha256=request_hash, raw_output=raw, prediction=parsed,
            error=error, perturbation_applied=bool(perturb and specialist == "G2"),
            elapsed_seconds=elapsed,
            response_metadata=response.get("response_metadata", {}))
        self.chain.append("MODEL_RESPONSE", record)
        return record

    def preview(self, state: int, action: str) -> dict:
        relation = relation_identity(state, action)
        key = relation_key(relation)
        selected = self.route_selected.get(key, "G2")
        scores = self.router.scores(self.routing_rows, relation) if self.horus_enabled else {
            "G2": {"correct": 0, "total": 0}, "G3": {"correct": 0, "total": 0}}
        return dict(relation=relation, selected_specialist=selected, scores=scores,
            relation_evidence_count=sum(relation_key(row["relation"]) == key
                                        for row in self.routing_rows),
            total_evidence_count=len(self.routing_rows))

    def predictions(self, state: int, action: str, identity: str,
                    perturb: bool = False) -> dict:
        calls = {s: self.call(s, state, action, f"{identity}:{s}", perturb)
                 for s in ("G2", "G3")}
        preview = self.preview(state, action)
        selected = preview["selected_specialist"] if self.horus_enabled else "G2"
        return dict(by_specialist={s: calls[s]["prediction"] for s in calls},
            selected_specialist=selected, selected_prediction=calls[selected]["prediction"],
            valid=all(calls[s]["prediction"] in (-1, 0, 1) for s in calls),
            selected_valid=calls[selected]["prediction"] in (-1, 0, 1),
            preview=preview, calls=calls)

    def record_receipt(self, stage: str, opportunity: int, state: int, action: str,
                       phase: str, predictions: dict, decision: dict) -> dict:
        actual_next = next_state(state, action)
        actual_consequence = consequence(state, action, phase)
        receipt = dict(source_identity=self.source,
            event_id=f"{self.name}:{stage}:{opportunity}", epoch=self.epoch,
            transaction_id=len(self.receipts) + 1, pre_state=state, action=action,
            next_state=actual_next, realized_consequence=actual_consequence)
        receipt["receipt_sha256"] = digest(receipt)
        self.receipts.append(receipt)
        before = predictions["preview"]
        switch = False
        if self.horus_enabled:
            correctness = {s: predictions["by_specialist"][s] == actual_consequence
                           for s in ("G2", "G3")}
            row = dict(evidence_sequence=len(self.routing_rows) + 1,
                relation=before["relation"], correctness=correctness,
                realized_consequence=actual_consequence)
            self.routing_rows.append(row)
            update = self.router.update(self.routing_rows, before["relation"],
                                        before["selected_specialist"])
            self.route_selected[relation_key(before["relation"])] = update["selected_after"]
            switch = update["switched"]
            self._update_confidence(before["relation"], actual_consequence,
                                    update["scores"], decision)
        record = dict(stage=stage, opportunity=opportunity, phase=phase,
            decision=decision, receipt=receipt,
            predictions=predictions["by_specialist"],
            selected_specialist=predictions["selected_specialist"],
            predicted_next_state=actual_next,
            predicted_consequence=predictions["selected_prediction"],
            next_state_correct=True,
            consequence_correct=predictions["selected_prediction"] == actual_consequence,
            exact_correct=predictions["selected_prediction"] == actual_consequence,
            invalid=not predictions["selected_valid"], router_switch=switch,
            history_rows_projected=len(self.history(state, action)))
        self.chain.append("AUTHORIZED_RECEIPT", record)
        return record

    def _update_confidence(self, relation: dict, value: int, scores: dict,
                           decision: dict) -> None:
        key = relation_key(relation)
        prior = [row["realized_consequence"] for row in self.routing_rows[:-1]
                 if relation_key(row["relation"]) == key]
        threshold = self.explorer.policy["confidence"][
            "contradiction_baseline_identical_outcomes"]
        if len(prior) >= threshold and len(set(prior[-threshold:])) == 1 and prior[-1] != value:
            self.confidence["unresolved_contradictions"][key] = dict(
                relation=relation, baseline_consequence=prior[-1],
                contradictory_consequence=value)
        minimum = self.explorer.policy["confidence"][
            "clear_preference_minimum_observations"]
        lead = self.explorer.policy["confidence"]["clear_preference_lead_correct"]
        if scores["G2"]["total"] >= minimum and abs(
                scores["G2"]["correct"] - scores["G3"]["correct"]) >= lead:
            self.confidence["unresolved_contradictions"].pop(key, None)
        self.confidence["attempted_decisions"] += 1
        self.confidence["authorized_decisions"] += 1
        self.confidence["last_execution_by_relation"][key] = dict(
            relation=relation,
            authorized_decision=self.confidence["authorized_decisions"])
        if decision.get("mode") == "PROBE":
            self.confidence["last_probe_authorized_decision"] = self.confidence[
                "authorized_decisions"]

    def choose(self, state: int, batch: dict[str, dict]) -> dict:
        forecasts = tuple(MapForecast(action, ALIASES[action], next_state(state, action),
            batch[action]["selected_prediction"], not batch[action]["selected_valid"],
            None if batch[action]["selected_valid"] else "INVALID_COMPONENT",
            len(self.history(state, action)), {}) for action in ACTION_ORDER)
        if not self.horus_enabled:
            choice = self.mechanical.choose(forecasts)
            return dict(mode="MECHANICAL", action=choice.action,
                        reason=choice.reason, abstained=choice.abstained)
        public = {a: {"G2_consequence": batch[a]["by_specialist"]["G2"],
                      "G3_consequence": batch[a]["by_specialist"]["G3"]}
                  for a in ACTION_ORDER}
        previews = {a: batch[a]["preview"] for a in ACTION_ORDER}
        derived = self.explorer.derive(pre_state=state, forecasts=public,
            routed_forecasts=forecasts, previews=previews,
            routing_records=self.routing_rows, confidence_state=self.confidence,
            all_predictions_valid=all(row["valid"] for row in batch.values()))
        return {k: v for k, v in derived.items() if k not in
                ("relation_confidence", "coverage")}


def run_arm(name: str, root: Path) -> dict:
    arm_dir = root / name
    arm_dir.mkdir(parents=True)
    arm = Arm(name, arm_dir)
    started = time.perf_counter()
    arm.load_models()
    rows, restart = [], None
    try:
        for index, (state, action, phase) in enumerate(STAGE_A, 1):
            if index == RESTART_BEFORE_STAGE_A:
                restart = arm.restart()
            prediction = arm.predictions(state, action, f"A:{index}",
                                         perturb=index == PERTURB_STAGE_A)
            decision = dict(mode="OBSERVATION_CONTROLLED", action=action,
                            abstained=False, reason="PREREGISTERED_EVENT")
            rows.append(arm.record_receipt("A", index, state, action, phase,
                                           prediction, decision))
        state = 1
        for index, phase in enumerate(STAGE_B_REGIMES, 1):
            batch = {action: arm.predictions(state, action, f"B:{index}:{action}")
                     for action in ACTION_ORDER}
            decision = arm.choose(state, batch)
            if decision["abstained"]:
                arm.confidence["attempted_decisions"] += int(arm.horus_enabled)
                row = dict(stage="B", opportunity=index, phase=phase,
                    decision=decision, receipt=None, predictions={a: batch[a][
                        "selected_prediction"] for a in ACTION_ORDER},
                    selected_specialist=None, predicted_next_state=None,
                    predicted_consequence=None, next_state_correct=None,
                    consequence_correct=None, exact_correct=None, invalid=True,
                    router_switch=False, history_rows_projected=None)
                arm.chain.append("ABSTENTION", row)
                rows.append(row)
                continue
            action = decision["action"]
            row = arm.record_receipt("B", index, state, action, phase,
                                     batch[action], decision)
            rows.append(row)
            state = row["receipt"]["next_state"]
    finally:
        snapshots = arm.zakhor_snapshot()
        arm.unload_models()
    result = summarize_condition(name, rows, arm.calls, arm.wall_model_seconds,
                                 time.perf_counter() - started, restart, snapshots,
                                 arm.routing_rows, arm.confidence)
    (arm_dir / "summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def ratio(rows: list[dict], key: str) -> float | None:
    values = [row[key] for row in rows if row.get(key) is not None]
    return None if not values else sum(bool(v) for v in values) / len(values)


def latency(rows: list[dict], phase: str, relation: tuple[int, str]) -> int | None:
    candidates = [r for r in rows if r["stage"] == "A" and r["phase"] == phase and
                  r["receipt"] and (r["receipt"]["pre_state"], r["receipt"]["action"]) == relation]
    for offset, row in enumerate(candidates):
        if row["consequence_correct"]:
            return offset
    return None


def window(rows: list[dict]) -> dict:
    return dict(opportunities=len(rows), authorized=sum(r["receipt"] is not None for r in rows),
                accuracy=ratio(rows, "consequence_correct"),
                invalid_rate=sum(bool(r["invalid"]) for r in rows) / len(rows),
                realized_consequence=sum(r["receipt"]["realized_consequence"]
                                         for r in rows if r["receipt"]))


def summarize_condition(name: str, rows: list[dict], calls: int, model_seconds: float,
                        total_seconds: float, restart: dict | None, snapshots: Any,
                        routing_rows: list[dict], confidence: dict) -> dict:
    windows = dict(early=window(rows[:8]), middle=window(rows[8:16]),
                   late=window(rows[16:]))
    rolling = [(i + 1, window(rows[i:i + ROLLING_WINDOW]))
               for i in range(len(rows) - ROLLING_WINDOW + 1)]
    worst = min(rolling, key=lambda item: (-1 if item[1]["accuracy"] is None
                                           else item[1]["accuracy"]))
    contradictory = {}
    for receipt in [r["receipt"] for r in rows if r["receipt"]]:
        key = f'{receipt["pre_state"]}:{receipt["action"]}'
        contradictory.setdefault(key, []).append(receipt["realized_consequence"])
    contradictions = {k: v for k, v in contradictory.items() if len(set(v)) > 1}
    pert_index = next(i for i, r in enumerate(rows) if r["stage"] == "A" and
                      r["opportunity"] == PERTURB_STAGE_A)
    recovery = next((i - pert_index for i in range(pert_index + 1, len(rows))
                     if rows[i].get("invalid") is False), None)
    return dict(condition=name, horus_enabled=CONDITIONS[name][0],
        zakhor_enabled=CONDITIONS[name][1], opportunities=len(rows),
        authorized_executions=sum(r["receipt"] is not None for r in rows),
        abstentions=sum(r["receipt"] is None for r in rows),
        consequence_prediction_accuracy=ratio(rows, "consequence_correct"),
        next_state_accuracy=ratio(rows, "next_state_correct"),
        exact_prediction_accuracy=ratio(rows, "exact_correct"),
        invalid_outputs=sum(bool(r["invalid"]) for r in rows),
        realized_consequence=sum(r["receipt"]["realized_consequence"]
                                 for r in rows if r["receipt"]),
        adaptation_latency=dict(advance=latency(rows, "change", (1, "ADVANCE")),
                                hold=latency(rows, "change", (1, "HOLD"))),
        restoration_latency=dict(advance=latency(rows, "restoration", (1, "ADVANCE")),
                                 hold=latency(rows, "restoration", (1, "HOLD"))),
        contradiction_preserved_relations=len(contradictions),
        contradiction_values=contradictions,
        semantic_history_exposed_to_model=CONDITIONS[name][0],
        zakhor_semantic_provenance_supported=False if CONDITIONS[name][1] else None,
        router_switches=sum(bool(r["router_switch"]) for r in rows),
        probe_decisions=sum(r["decision"].get("mode") == "PROBE" for r in rows),
        unnecessary_probes=None,
        unresolved_contradictions=len(confidence["unresolved_contradictions"])
                                  if CONDITIONS[name][0] else None,
        restart=restart, perturbation_recovery_opportunities=recovery,
        windows={**windows, "worst_rolling": {"starts_at": worst[0], **worst[1]}},
        model_calls=calls, model_seconds=model_seconds, wall_seconds=total_seconds,
        zakhor_final_tracker_sha256=None if snapshots is None else digest(snapshots),
        routing_evidence_rows=len(routing_rows) if CONDITIONS[name][0] else None)


def effects(results: dict[str, dict], metric: str) -> dict:
    f, h, z, hz = (results[k][metric] for k in ("F", "H", "Z", "HZ"))
    if any(v is None for v in (f, h, z, hz)):
        return dict(metric=metric, horus_main=None, zakhor_main=None, interaction=None)
    return dict(metric=metric, horus_main=((h + hz) - (f + z)) / 2,
        zakhor_main=((z + hz) - (f + h)) / 2, interaction=hz - h - z + f)


def run(output: Path) -> dict:
    if output.exists():
        raise RuntimeError("output already exists; no retry/overwrite")
    output.mkdir(parents=True)
    manifest = json.loads((EXPERIMENT / "source-manifest.json").read_text())
    verify_manifest(manifest)
    (output / "frozen-source-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    results = {}
    for name in ORDER:
        print(f"condition={name} stage=loading", flush=True)
        results[name] = run_arm(name, output)
        print(f"condition={name} complete calls={results[name]['model_calls']}", flush=True)
    payload = dict(status="COMPLETE", condition_order=list(ORDER),
        stage_a_events=len(STAGE_A), stage_b_opportunities=len(STAGE_B_REGIMES),
        total_model_calls=sum(r["model_calls"] for r in results.values()),
        conditions=results,
        effects=[effects(results, m) for m in (
            "consequence_prediction_accuracy", "exact_prediction_accuracy",
            "realized_consequence", "invalid_outputs", "model_seconds")])
    (output / "results.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return payload


def verify_manifest(manifest: dict) -> None:
    for relative, expected in manifest["zakhor_source_sha256"].items():
        if file_hash(ROOT / relative) != expected:
            raise RuntimeError(f"Zakhor frozen source mismatch: {relative}")
    for name, expected in manifest["model_artifact_sha256"].items():
        if file_hash(adapter_paths()[name]) != expected:
            raise RuntimeError(f"model artifact mismatch: {name}")


def verify_chain(path: Path, key: bytes) -> int:
    previous, count = None, 0
    for line in path.read_text().splitlines():
        envelope = json.loads(line)
        signed = {k: envelope[k] for k in ("sequence", "previous_sha256", "kind", "record")}
        count += 1
        if envelope["sequence"] != count or envelope["previous_sha256"] != previous:
            raise RuntimeError("broken record sequence/hash chain")
        if envelope["hmac_sha256"] != new_as_hex(key, signed):
            raise RuntimeError("record authentication failed")
        previous = sha256(line.encode()).hexdigest()
    return count


def replay(output: Path) -> dict:
    original = json.loads((output / "results.json").read_text())
    counts = {}
    for name in CONDITIONS:
        counts[name] = verify_chain(output / name / "records.jsonl",
                                    sha256(("horus-zakhor-v0:" + name).encode()).digest())
        summary = json.loads((output / name / "summary.json").read_text())
        if summary != original["conditions"][name]:
            raise RuntimeError(f"condition summary mismatch: {name}")
    if original["total_model_calls"] != 288:
        raise RuntimeError("frozen call budget mismatch")
    return dict(status="PASS", exact_results_match=True, record_counts=counts,
                total_model_calls=original["total_model_calls"])

