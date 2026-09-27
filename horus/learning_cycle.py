"""Bounded collection, candidate training, evaluation, and atomic selection."""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

from .core import digest
from .grounded_learning import (BASE_MODEL_ID, CONFIG_PATH, QwenConsequenceClient,
    ROOT, _build_example, atomic_json, compare, file_hash, load_dataset, train)
from .live import ModelClient, SessionStore, run_live
from .model_registry import (RegistryError, active_model_spec, consumed_examples,
    finalize_generation, load_registry)


RULE_PATH = Path(__file__).with_name("promotion_rule.json")
STRATEGIES = ("continue-active", "base-cumulative")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _identity(spec: dict) -> dict:
    return {key: spec[key] for key in ("generation", "parent_generation",
        "base_model_identity", "artifact_sha256", "adapter_identity")}


def active_client(registry_root: Path, device: str | None = None):
    spec = active_model_spec(registry_root)
    adapter = None if spec["adapter_path"] is None else Path(spec["adapter_path"])
    client = QwenConsequenceClient(adapter_path=adapter, device=device,
                                   model_identity=_identity(spec))
    if client.horus_model_identity["artifact_sha256"] != spec["artifact_sha256"]:
        raise RegistryError("loaded active artifact identity mismatch")
    client.model_id = f"horus-consequence-generation-{spec['generation']}:{spec['artifact_sha256']}"
    return client, spec


def collect_active(session_root: Path, registry_root: Path, target: int = 60,
                   max_sessions: int = 20, steps_per_session: int = 6) -> dict:
    if session_root.exists():
        raise RuntimeError("session root already exists")
    if not 60 <= target <= 120:
        raise ValueError("bounded target must be 60..120")
    session_root.mkdir(parents=True)
    consequence, spec = active_client(registry_root, device="cuda")
    joint = ModelClient()
    sessions, authorized = [], 0
    for index in range(max_sessions):
        remaining = target - authorized
        if remaining <= 0:
            break
        path = session_root / f"session-{index:03d}"
        result = run_live(path, min(steps_per_session, remaining), False,
                          client=joint, consequence_client=consequence)
        count = sum(row["status"] == "AUTHORIZED" for row in result["steps"])
        sessions.append(dict(name=path.name, authorized=count,
            attempted=len(result["steps"]), joint_calls=result["joint_model_calls"],
            consequence_calls=result["consequence_model_calls"]))
        authorized += count
        print(f"active collection {path.name}: {authorized}/{target}", flush=True)
    distribution = {-1: 0, 0: 0, 1: 0}
    for item in sessions:
        with SessionStore(session_root / item["name"], True) as store:
            for row in store.imported_history():
                distribution[row["receipt"]["realized_consequence"]] += 1
    result = dict(status="COMPLETE" if authorized >= target else "INSUFFICIENT",
        target=target, authorized=authorized, sessions=sessions,
        consequence_distribution={str(key): value for key, value in distribution.items()},
        active_generation=spec["generation"],
        active_artifact_sha256=spec["artifact_sha256"],
        selection="fixed target/max-session schedule; no outcome-based extension")
    atomic_json(session_root / "collection.json", result)
    if authorized < target:
        raise RuntimeError("bounded active collection ended below target")
    return result


def _write_dataset(output: Path, examples: list[dict], extra: dict) -> dict:
    if output.exists():
        raise RuntimeError("dataset output already exists")
    output.mkdir(parents=True)
    path = output / "examples.jsonl"
    with path.open("x") as stream:
        for row in examples:
            stream.write(_canonical(row) + "\n")
    splits = ("train", "validation", "evaluation")
    counts = {split: sum(row["split"] == split for row in examples) for split in splits}
    distribution = {split: {str(value): sum(row["split"] == split and
        row["target"] == value for row in examples) for value in (-1, 0, 1)}
        for split in splits}
    payload = dict(version=2, frozen_at=_now(), examples_sha256=file_hash(path),
        example_count=len(examples), split_counts=counts,
        consequence_distribution=distribution,
        ordered_example_ids=[row["example_id"] for row in examples],
        ordered_request_sha256=[row["request_sha256"] for row in examples],
        ordered_receipt_identities=[row["receipt_identity"] for row in examples],
        ordered_targets=[row["target"] for row in examples],
        training_config_sha256=file_hash(CONFIG_PATH), base_model=BASE_MODEL_ID,
        base_weights_sha256=extra.pop("base_weights_sha256"), **extra)
    document = dict(payload=payload, manifest_sha256=digest(payload))
    atomic_json(output / "manifest.json", document)
    return document


def freeze_new_examples(session_root: Path, registry_root: Path,
                        output: Path) -> dict:
    registry = load_registry(registry_root)
    used = consumed_examples(registry)
    session_dirs = sorted(path.parent for path in session_root.rglob("checkpoint.json"))
    if len(session_dirs) < 3:
        raise RuntimeError("at least three complete sessions are required")
    groups = []
    for session in session_dirs:
        with SessionStore(session, True) as store:
            if len(store.records["events"]) != len(store.records["training"]):
                raise RuntimeError("event/training stream length mismatch")
            rows = [_build_example(store, str(session.relative_to(session_root)), event, training)
                    for event, training in zip(store.records["events"],
                                               store.records["training"])]
        old = [row["example_id"] in used for row in rows]
        if any(old) and not all(old):
            raise RuntimeError("partially consumed session would break session-level split")
        if not any(old):
            groups.append((session, rows))
    if len(groups) < 3:
        raise RuntimeError("insufficient wholly new sessions")
    total = sum(len(rows) for _, rows in groups)
    if not 60 <= total <= 120:
        raise RuntimeError("new grounded example count outside bounded range")
    train_end = max(1, int(len(groups) * 0.70))
    validation_end = max(train_end + 1, int(len(groups) * 0.85))
    if validation_end >= len(groups):
        validation_end = len(groups) - 1
    examples, assignments = [], {}
    for index, (session, rows) in enumerate(groups):
        split = ("train" if index < train_end else
                 "validation" if index < validation_end else "evaluation")
        assignments[str(session.relative_to(session_root))] = split
        for row in rows:
            row["split"] = split
            examples.append(row)
    if len({row["example_id"] for row in examples}) != len(examples):
        raise RuntimeError("duplicate eligible example identity")
    base_hash = registry["manifests"][0]["adapter_sha256"]
    return _write_dataset(output, examples, dict(
        base_weights_sha256=base_hash, session_assignment=assignments,
        source="authenticated session scan", excluded_consumed_examples=len(used),
        active_generation_at_freeze=registry["active_entry"]["generation"],
        active_registry_state_sha256=registry["state_document"]["sha256"]))


def assemble_training_dataset(fresh: Path, registry_root: Path,
                              output: Path, strategy: str) -> dict:
    if strategy not in STRATEGIES:
        raise ValueError("unsupported candidate training strategy")
    fresh_manifest, fresh_rows = load_dataset(fresh)
    if strategy == "continue-active":
        rows = fresh_rows
        sources = [fresh_manifest["manifest_sha256"]]
    else:
        registry = load_registry(registry_root)
        rows, sources, seen = [], [], set()
        for entry in registry["entries"]:
            if entry["status"] == "REJECTED":
                continue
            manifest = registry["manifests"][entry["generation"]]
            relative = manifest.get("dataset_path")
            if relative is None:
                continue
            old_manifest, old_rows = load_dataset(registry["root"] / relative)
            sources.append(old_manifest["manifest_sha256"])
            for row in old_rows:
                if row["split"] == "train" and row["example_id"] not in seen:
                    rows.append(row); seen.add(row["example_id"])
        sources.append(fresh_manifest["manifest_sha256"])
        for row in fresh_rows:
            if row["split"] == "train" and row["example_id"] not in seen:
                rows.append(row); seen.add(row["example_id"])
        rows.extend(row for row in fresh_rows if row["split"] != "train")
    validate_optimizer_separation(rows)
    return _write_dataset(output, rows, dict(
        base_weights_sha256=fresh_manifest["payload"]["base_weights_sha256"],
        training_strategy=strategy, source_manifest_sha256=sources,
        fresh_evaluation_manifest_sha256=fresh_manifest["manifest_sha256"]))


def validate_optimizer_separation(rows: list[dict]) -> None:
    optimized = {row["example_id"] for row in rows if row["split"] == "train"}
    evaluation = {row["example_id"] for row in rows if row["split"] == "evaluation"}
    if optimized & evaluation:
        raise RuntimeError("evaluation leakage into optimizer")
    identities = [(row["example_id"], row["split"]) for row in rows]
    if len(identities) != len(set(identities)):
        raise RuntimeError("duplicate example within a split")


def promotion_decision(incumbent: dict, candidate: dict, comparison: dict,
                       integrity_checks_passed: bool = True) -> dict:
    rule = json.loads(RULE_PATH.read_text())
    represented = all(candidate["by_target"][str(value)]["n"] >=
                      rule["minimum_examples_per_class"] for value in (-1, 0, 1))
    collapses = []
    for value in (-1, 0, 1):
        before, after = incumbent["by_target"][str(value)], candidate["by_target"][str(value)]
        if before["n"] >= rule["catastrophic_class_minimum_examples"] and \
                before["accuracy"] - after["accuracy"] > \
                rule["maximum_absolute_class_accuracy_drop"]:
            collapses.append(value)
    categories = comparison["categories"]
    criteria = dict(
        sufficient_evidence=(candidate["examples"] >= rule["minimum_evaluation_examples"]
                             and represented),
        overall_improved=candidate["accuracy"] > incumbent["accuracy"],
        invalid_not_increased=candidate["invalid"] <= incumbent["invalid"],
        net_corrections=(categories["wrong_to_correct"] >
                         categories["correct_to_wrong"]),
        no_catastrophic_class_collapse=not collapses,
        integrity_checks_passed=integrity_checks_passed)
    promoted = all(criteria.values())
    return dict(rule_sha256=file_hash(RULE_PATH), rule=rule, criteria=criteria,
                catastrophic_classes=collapses,
                decision="ACTIVE" if promoted else "REJECTED")


def _run_evaluation(dataset: Path, output: Path,
                    adapter: Path | None = None,
                    phase: str | None = None) -> dict:
    log = output.with_suffix(output.suffix + ".stdout")
    command = [sys.executable, "-m", "horus.learn", "evaluate",
               "--dataset", str(dataset), "--output", str(output)]
    if adapter is not None:
        command.extend(("--adapter", str(adapter)))
    if phase is not None:
        command.extend(("--phase", phase))
    with log.open("x") as stream:
        completed = subprocess.run(command, cwd=ROOT, stdout=stream,
                                   stderr=subprocess.STDOUT, text=True)
    if completed.returncode != 0 or not output.is_file():
        raise RuntimeError("fresh-process evaluation interrupted or failed")
    value = json.loads(output.read_text())
    if value.get("fresh_process_pid") == os.getpid():
        raise RuntimeError("evaluation did not run in a fresh process")
    return value


def _relative(root: Path, path: Path) -> str:
    return str(path.resolve().relative_to(root.resolve()))


def run_cycle(session_root: Path, registry_root: Path,
              strategy: str = "continue-active") -> dict:
    if strategy not in STRATEGIES:
        raise ValueError("unsupported candidate training strategy")
    registry = load_registry(registry_root)
    incumbent = registry["active_manifest"]
    generation = max(registry["manifests"]) + 1
    parent_generation = incumbent["generation"]
    candidate_root = registry["root"] / f"generations/generation-{generation:04d}"
    if candidate_root.exists():
        raise RegistryError("candidate generation directory already exists")
    candidate_root.mkdir(parents=True)
    attempt = dict(status="CANDIDATE", generation=generation,
        parent_generation=parent_generation, strategy=strategy,
        promotion_rule_sha256=file_hash(RULE_PATH),
        training_config_sha256=file_hash(CONFIG_PATH), started_at=_now())
    atomic_json(candidate_root / "attempt.json", attempt)
    try:
        fresh = candidate_root / "fresh-dataset"
        fresh_manifest = freeze_new_examples(session_root, registry_root, fresh)
        training_dataset = candidate_root / "training-dataset"
        training_manifest = assemble_training_dataset(
            fresh, registry_root, training_dataset, strategy)
        parent_adapter = (None if strategy == "base-cumulative" else
            registry["root"] / incumbent["adapter_path"])
        # The pre-evaluation freezes the exact heldout requests before any update.
        incumbent_eval = candidate_root / "incumbent-evaluation.json"
        incumbent_result = _run_evaluation(
            fresh, incumbent_eval, registry["root"] / incumbent["adapter_path"])
        training_pre = candidate_root / "training-pre-evaluation.json"
        _run_evaluation(training_dataset, training_pre, parent_adapter,
                        phase="PRE_TRAINING")
        model_output = candidate_root / "model"
        lineage = train(training_dataset, training_pre, model_output,
            parent_adapter=parent_adapter,
            lineage_parent_generation=(None if strategy == "base-cumulative"
                                       else parent_generation),
            training_strategy=strategy)
        adapter = model_output / "trained-adapter.safetensors"
        if file_hash(adapter) != lineage["final_adapter_sha256"]:
            raise RuntimeError("candidate artifact hash mismatch")
        candidate_eval = candidate_root / "candidate-evaluation.json"
        candidate_result = _run_evaluation(fresh, candidate_eval, adapter)
        comparison_path = candidate_root / "evaluation-comparison.json"
        comparison = compare(incumbent_eval, candidate_eval, comparison_path)
        decision = promotion_decision(incumbent_result, candidate_result, comparison)
        usage = {row["example_id"]: row["split"] for row in
                 load_dataset(training_dataset)[1]}
        usage_path = candidate_root / "example-usage.json"
        atomic_json(usage_path, usage)
        config = json.loads(CONFIG_PATH.read_text())
        manifest = dict(generation=generation,
            parent_generation=parent_generation,
            base_model_identity=BASE_MODEL_ID,
            adapter_path=_relative(registry["root"], adapter),
            adapter_sha256=file_hash(adapter), artifact_kind="LORA_ADAPTER",
            dataset_manifest_sha256=fresh_manifest["manifest_sha256"],
            training_dataset_manifest_sha256=training_manifest["manifest_sha256"],
            grounded_training_examples=training_manifest["payload"]["split_counts"]["train"],
            newly_eligible_grounded_examples=fresh_manifest["payload"]["example_count"],
            training_configuration=config, training_strategy=strategy,
            creation_timestamp=_now(),
            evaluation_artifact=_relative(registry["root"], comparison_path),
            evaluation_sha256=file_hash(comparison_path),
            incumbent_evaluation_artifact=_relative(registry["root"], incumbent_eval),
            incumbent_evaluation_sha256=file_hash(incumbent_eval),
            candidate_evaluation_artifact=_relative(registry["root"], candidate_eval),
            candidate_evaluation_sha256=file_hash(candidate_eval),
            lineage_artifact=_relative(registry["root"], model_output / "learning-lineage.json"),
            lineage_sha256=file_hash(model_output / "learning-lineage.json"),
            dataset_path=_relative(registry["root"], fresh),
            training_dataset_path=_relative(registry["root"], training_dataset),
            example_usage_artifact=_relative(registry["root"], usage_path),
            example_usage_sha256=file_hash(usage_path),
            evaluation_summary=dict(incumbent=dict(examples=incumbent_result["examples"],
                correct=incumbent_result["correct"], accuracy=incumbent_result["accuracy"],
                invalid=incumbent_result["invalid"], by_target=incumbent_result["by_target"]),
                candidate=dict(examples=candidate_result["examples"],
                correct=candidate_result["correct"], accuracy=candidate_result["accuracy"],
                invalid=candidate_result["invalid"], by_target=candidate_result["by_target"]),
                transitions=comparison["categories"], promotion=decision),
            promotion_rule_sha256=file_hash(RULE_PATH),
            provenance_checks_passed=True, fresh_process_reload_passed=True,
            optimizer_evaluation_leakage=0)
        reason = ("All frozen promotion criteria passed" if decision["decision"] == "ACTIVE"
                  else "One or more frozen promotion criteria failed")
        finalized = finalize_generation(registry_root, manifest,
                                        decision["decision"], reason)
        result = dict(status="COMPLETE", generation=generation,
            parent_generation=parent_generation, strategy=strategy,
            decision="PROMOTED" if decision["decision"] == "ACTIVE" else "REJECTED",
            active_generation_after=finalized["active_generation"],
            fresh_dataset_manifest_sha256=fresh_manifest["manifest_sha256"],
            training_dataset_manifest_sha256=training_manifest["manifest_sha256"],
            incumbent_evaluation=manifest["evaluation_summary"]["incumbent"],
            candidate_evaluation=manifest["evaluation_summary"]["candidate"],
            transitions=comparison["categories"], promotion=decision,
            candidate_adapter_sha256=file_hash(adapter),
            registry_state_sha256=finalized["state"]["sha256"])
        atomic_json(candidate_root / "cycle-result.json", result)
        return result
    except Exception as exc:
        failure = dict(status="FAILED", generation=generation,
            parent_generation=parent_generation, strategy=strategy,
            failed_at=_now(), error_type=type(exc).__name__, reason=str(exc))
        atomic_json(candidate_root / "failure.json", failure)
        failure_manifest = dict(generation=generation,
            parent_generation=parent_generation, base_model_identity=BASE_MODEL_ID,
            adapter_path=None, adapter_sha256=digest(failure),
            artifact_kind="FAILED_CANDIDATE_ATTEMPT", dataset_manifest_sha256=None,
            grounded_training_examples=0,
            training_configuration=json.loads(CONFIG_PATH.read_text()),
            training_strategy=strategy, creation_timestamp=_now(),
            evaluation_artifact=None, evaluation_sha256=None,
            lineage_artifact=None, lineage_sha256=None, dataset_path=None,
            example_usage_artifact=None, example_usage_sha256=None,
            evaluation_summary=None, promotion_rule_sha256=file_hash(RULE_PATH),
            provenance_checks_passed=False, fresh_process_reload_passed=False,
            optimizer_evaluation_leakage=None)
        finalized = finalize_generation(registry_root, failure_manifest, "REJECTED",
            f"Cycle failed closed: {type(exc).__name__}: {exc}")
        return dict(status="FAILED_CLOSED", generation=generation,
            decision="REJECTED", active_generation_after=finalized["active_generation"],
            failure=failure)
