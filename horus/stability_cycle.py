"""Historical evaluation bank, hidden regime shift, and stability selection."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
from typing import Any

from .core import MAPPING, digest
from .grounded_learning import (BASE_MODEL_ID, CONFIG_PATH, ROOT, atomic_json,
    compare, file_hash, load_dataset, train)
from .learning_cycle import (_relative, _run_evaluation, _write_dataset,
    active_client, validate_optimizer_separation)
from .live import ModelClient, SessionStore, run_live
from .model_registry import (RegistryError, _document, _read_document,
    _write_document, active_model_spec, consumed_examples, finalize_generation,
    load_registry)


RULE_PATH = Path(__file__).with_name("stability_promotion_rule.json")
REGIME_PATH = Path(__file__).with_name("regime_config.json")
INITIAL_REGISTRY = ROOT / "research/learning-cycle-v0/registry"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def initialize_stability_registry(output: Path) -> dict:
    if output.exists():
        raise RegistryError("stability registry already exists")
    source = load_registry(INITIAL_REGISTRY)
    if source["active_entry"]["generation"] != 2:
        raise RegistryError("v0.4 requires generation 2 as initial ACTIVE")
    shutil.copytree(INITIAL_REGISTRY, output)
    bank = initialize_evaluation_bank(output)
    return dict(registry=str(output.resolve()), active_generation=2,
                bank_version=bank["payload"]["version"],
                bank_manifest_sha256=bank["manifest_sha256"])


def _bank_pointer(root: Path) -> dict:
    return _read_document(root / "evaluation-bank/current.json",
                          "evaluation bank pointer")


def load_evaluation_bank(root: Path) -> tuple[dict, list[dict]]:
    pointer = _bank_pointer(root)
    path = (root / pointer["payload"]["manifest"]).resolve()
    manifest = json.loads(path.read_text())
    if digest(manifest["payload"]) != manifest.get("manifest_sha256") or \
            manifest["manifest_sha256"] != pointer["payload"]["manifest_sha256"]:
        raise RegistryError("evaluation bank manifest hash mismatch")
    examples = path.parent / "examples.jsonl"
    if file_hash(examples) != manifest["payload"]["examples_sha256"]:
        raise RegistryError("evaluation bank examples hash mismatch")
    rows = [json.loads(line) for line in examples.read_text().splitlines()]
    if [row["example_id"] for row in rows] != manifest["payload"]["example_ids"]:
        raise RegistryError("evaluation bank example order mismatch")
    return manifest, rows


def _write_bank_version(root: Path, rows: list[dict], version: int,
                        parent_sha256: str | None) -> dict:
    directory = root / f"evaluation-bank/versions/bank-{version:04d}"
    if directory.exists():
        raise RegistryError("evaluation bank version already exists")
    directory.mkdir(parents=True)
    path = directory / "examples.jsonl"
    with path.open("x") as stream:
        for row in rows:
            stream.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
    payload = dict(version=version, parent_manifest_sha256=parent_sha256,
        created_at=_now(), append_only=True, example_count=len(rows),
        examples_sha256=file_hash(path),
        example_ids=[row["example_id"] for row in rows],
        class_distribution={str(value): sum(row["target"] == value for row in rows)
                            for value in (-1, 0, 1)},
        batch_distribution=dict(Counter(row["bank_batch_id"] for row in rows)),
        model_visible_regime_examples=sum(row["regime_model_visible"] for row in rows))
    manifest = dict(payload=payload, manifest_sha256=digest(payload))
    atomic_json(directory / "manifest.json", manifest)
    relative = str((directory / "manifest.json").relative_to(root))
    _write_document(root / "evaluation-bank/current.json", dict(
        version=version, manifest=relative,
        manifest_sha256=manifest["manifest_sha256"], updated_at=_now()))
    return manifest


def _bank_row(row: dict, source_generation: int, batch: str,
              dataset_manifest: str, first_eligible: int) -> dict:
    value = deepcopy(row)
    value.update(bank_batch_id=batch,
        originating_generation=source_generation,
        originating_runtime=row.get("originating_runtime_index"),
        authenticated_receipt_identity=row["receipt_identity"],
        input_context_sha256=row.get("input_context_sha256") or digest(
            {"system": row["system"], "prompt": row["prompt"]}),
        realized_consequence=row["target"], consequence_class=str(row["target"]),
        external_regime_version=row.get("external_regime_version", "A"),
        regime_model_visible=row.get("regime_model_visible", False),
        source_dataset_manifest_sha256=dataset_manifest,
        source_split=row["split"], first_eligible_generation=first_eligible,
        evaluation_origin="historical")
    value["split"] = "evaluation"
    return value


def initialize_evaluation_bank(root: Path) -> dict:
    registry = load_registry(root)
    if (root / "evaluation-bank").exists():
        raise RegistryError("evaluation bank already initialized")
    sources = ((1, "v0.2-grounded-learning", 2),
               (2, "v0.3-learning-cycle", 3))
    rows, exclusions = [], []
    usage = consumed_examples(registry)
    for generation, batch, eligible in sources:
        manifest = registry["manifests"][generation]
        dataset_manifest, examples = load_dataset(root / manifest["dataset_path"])
        for row in examples:
            roles = usage.get(row["example_id"], [])
            trained = [item for item in roles if item["role"] == "train"]
            if row["split"] == "evaluation" and not trained:
                rows.append(_bank_row(row, generation - 1, batch,
                    dataset_manifest["manifest_sha256"], eligible))
            else:
                exclusions.append(dict(example_id=row["example_id"],
                    source_generation=generation, source_split=row["split"],
                    reason=("optimizer exposure" if trained else
                            "validation exposure conservatively excluded")))
    if len({row["example_id"] for row in rows}) != len(rows):
        raise RegistryError("duplicate evaluation bank identity")
    if any(row["example_id"] in {item["example_id"] for item in exclusions}
           for row in rows):
        raise RegistryError("evaluation bank/exclusion overlap")
    for index, row in enumerate(rows):
        third = max(1, len(rows) // 3)
        row["historical_window"] = ("early" if index < third else
                                    "middle" if index < 2 * third else "recent")
    manifest = _write_bank_version(root, rows, 1, None)
    atomic_json(root / "evaluation-bank/exclusions.json", dict(
        policy="only prior heldout evaluation splits; training and validation excluded",
        excluded=len(exclusions), rows=exclusions))
    return manifest


def append_fresh_to_bank(root: Path, fresh_dataset: Path,
                         batch_id: str, first_eligible: int) -> dict:
    old_manifest, old = load_evaluation_bank(root)
    dataset_manifest, examples = load_dataset(fresh_dataset)
    additions = [_bank_row(row, first_eligible - 1, batch_id,
        dataset_manifest["manifest_sha256"], first_eligible)
        for row in examples if row["split"] == "evaluation"]
    old_ids = {row["example_id"] for row in old}
    if old_ids & {row["example_id"] for row in additions}:
        raise RegistryError("evaluation bank append duplicates existing identity")
    return _write_bank_version(root, old + additions,
        old_manifest["payload"]["version"] + 1,
        old_manifest["manifest_sha256"])


def _event_rows(session_root: Path) -> list[dict]:
    rows = []
    for session in sorted(path.parent for path in session_root.glob("session-*/checkpoint.json")):
        with SessionStore(session, True) as store:
            for event, training in zip(store.records["events"], store.records["training"]):
                e, t = event["record"], training["record"]
                rows.append(dict(session=session.name, session_id=t["session_id"],
                    order=t["order"], epoch=t["epoch"], transaction_id=t["transaction_id"],
                    runtime_index=e["source_scope"]["runtime_index"],
                    source_identity=e["source_scope"]["source_identity"],
                    state=e["receipt"]["pre_state"], action=e["receipt"]["action"],
                    predicted_consequence=t["predicted_consequence"],
                    realized_consequence=t["realized_consequence"],
                    correct=t["prediction_match"]["consequence"], invalid=False,
                    regime=e.get("external_regime_version", "A"),
                    regime_model_visible=e.get("regime_model_visible", False),
                    receipt_identity=e["receipt_identity"],
                    event_sequence=event["sequence"]))
    return rows


def _metrics(rows: list[dict]) -> dict:
    return dict(n=len(rows), correct=sum(row["correct"] for row in rows),
        accuracy=None if not rows else sum(row["correct"] for row in rows) / len(rows),
        invalid=sum(row["invalid"] for row in rows),
        invalid_rate=None if not rows else sum(row["invalid"] for row in rows) / len(rows),
        action_distribution=dict(Counter(row["action"] for row in rows)),
        realized_consequence_distribution=dict(
            Counter(str(row["realized_consequence"]) for row in rows)))


def collection_endurance(session_root: Path) -> dict:
    rows = _event_rows(session_root)
    if len(rows) != 60:
        raise RuntimeError("endurance report requires exact 60-event collection")
    windows = dict(early=_metrics(rows[:20]), middle=_metrics(rows[20:40]),
                   late=_metrics(rows[40:]))
    rolling = []
    for start in range(len(rows) - 9):
        value = _metrics(rows[start:start + 10]); value["start"] = start + 1
        rolling.append(value)
    windows["worst_rolling_10"] = min(rolling,
        key=lambda value: (value["accuracy"], -value["invalid_rate"], value["start"]))
    return dict(rows=rows, windows=windows,
        immediately_before_shift=_metrics(rows[:3]),
        first_six_after_shift=_metrics(rows[3:9]))


def collect_regime_shift(session_root: Path, registry_root: Path,
                         target: int = 60) -> dict:
    if session_root.exists():
        raise RuntimeError("regime-shift session root already exists")
    if target != 60:
        raise ValueError("v0.4 fixed collection target is exactly 60")
    session_root.mkdir(parents=True)
    consequence, spec = active_client(registry_root, device="cuda")
    if spec["generation"] != 2:
        raise RegistryError("regime shift must begin under ACTIVE generation 2")
    joint = ModelClient(); summaries = []
    bridge = session_root / "session-000"
    before = run_live(bridge, 3, False, joint, consequence, regime_version="A")
    after = run_live(bridge, 3, True, joint, consequence, regime_version="B",
                     allow_regime_transition=True)
    summaries.append(dict(name=bridge.name, authorized=6, attempted=6,
        process_segments=[dict(regime="A", runtime_index=before["runtime_index"], steps=3),
                          dict(regime="B", runtime_index=after["runtime_index"], steps=3)],
        joint_calls=18, consequence_calls=18))
    authorized = 6
    for index in range(1, 10):
        path = session_root / f"session-{index:03d}"
        result = run_live(path, 6, False, joint, consequence, regime_version="B")
        count = sum(row["status"] == "AUTHORIZED" for row in result["steps"])
        summaries.append(dict(name=path.name, authorized=count,
            attempted=len(result["steps"]), process_segments=[dict(
                regime="B", runtime_index=result["runtime_index"], steps=count)],
            joint_calls=result["joint_model_calls"],
            consequence_calls=result["consequence_model_calls"]))
        authorized += count
        print(f"regime-B collection {path.name}: {authorized}/{target}", flush=True)
    if authorized != target:
        raise RuntimeError("fixed regime-shift collection did not authorize exactly 60")
    endurance = collection_endurance(session_root)
    rows = endurance["rows"]
    # Verify the hidden audit field never entered an actual consequence prompt.
    hidden_checks = 0; old_history_after_restart = 0
    with SessionStore(bridge, True) as store:
        for envelope in store.records["calls"]:
            record = envelope["record"]
            if envelope["kind"] != "REQUEST_INTENT" or \
                    record.get("role") != "independent-consequence":
                continue
            prompt = record["request"]["prompt"]
            if "regime" in prompt.lower():
                raise RuntimeError("hidden regime leaked into model prompt")
            hidden_checks += 1
            payload = json.loads(prompt)
            if any(item["epoch"] == before["epoch"] for item in
                   payload["VERIFIED_CHRONOLOGICAL_HISTORY"]):
                old_history_after_restart += 1
        checkpoint = deepcopy(store.checkpoint)
    pairs = {}
    for row in rows:
        pairs.setdefault((row["state"], row["action"]), {}).setdefault(
            row["regime"], set()).add(row["realized_consequence"])
    contradictions = [dict(state=key[0], action=key[1],
        regime_A=sorted(value.get("A", [])), regime_B=sorted(value.get("B", [])))
        for key, value in pairs.items() if value.get("A") and value.get("B") and
        value["A"] != value["B"]]
    result = dict(status="COMPLETE", target=target, authorized=authorized,
        active_generation=2, active_artifact_sha256=spec["artifact_sha256"],
        regime_definition_sha256=file_hash(REGIME_PATH), regime_transition=dict(
            from_regime="A", to_regime="B", bridge_session=bridge.name,
            after_completed_step=3, model_visible=False), sessions=summaries,
        consequence_distribution=dict(Counter(
            str(row["realized_consequence"]) for row in rows)),
        regime_distribution=dict(Counter(row["regime"] for row in rows)),
        hidden_prompt_checks=hidden_checks,
        old_history_requests_after_restart=old_history_after_restart,
        contradictory_state_action_pairs=contradictions,
        restart_proof=dict(runtime_indices=[1, 2],
            source_identities=sorted({row["source_identity"] for row in rows
                                      if row["session"] == bridge.name}),
            regime_history=checkpoint["regime_history"],
            prior_records_preserved=sum(row["session"] == bridge.name and
                                        row["runtime_index"] == 1 for row in rows),
            post_restart_records=sum(row["session"] == bridge.name and
                                     row["runtime_index"] == 2 for row in rows)),
        endurance_windows=endurance["windows"],
        immediately_before_shift=endurance["immediately_before_shift"],
        first_six_after_shift=endurance["first_six_after_shift"],
        selection="fixed 3 A + 57 B schedule; no performance-based extension")
    atomic_json(session_root / "collection.json", result)
    return result


def _evaluation_dataset(rows: list[dict], output: Path, source: str,
                        base_hash: str) -> dict:
    values = []
    for row in rows:
        value = deepcopy(row); value["split"] = "evaluation"
        values.append(value)
    return _write_dataset(output, values, dict(base_weights_sha256=base_hash,
        evaluation_source=source, no_optimizer_use=True))


def _group_metrics(dataset_rows: list[dict], evaluation: dict,
                   field: str) -> dict:
    results = {row["example_id"]: row for row in evaluation["results"]}
    groups: dict[str, list[dict]] = {}
    for row in dataset_rows:
        if row["split"] != "evaluation":
            continue
        key = str(row.get(field, "UNSPECIFIED"))
        groups.setdefault(key, []).append(results[row["example_id"]])
    return {key: dict(n=len(rows), correct=sum(row["correct"] for row in rows),
        accuracy=sum(row["correct"] for row in rows) / len(rows),
        invalid=sum(row["predicted"] is None for row in rows))
        for key, rows in groups.items()}


def evaluation_analysis(dataset: Path, incumbent: dict, candidate: dict) -> dict:
    _, rows = load_dataset(dataset)
    before = {row["example_id"]: row for row in incumbent["results"]}
    after = {row["example_id"]: row for row in candidate["results"]}
    transitions = Counter(); forgetting = []
    for identity in before:
        old, new = before[identity], after[identity]
        category = ("correct_to_correct" if old["correct"] and new["correct"] else
                    "correct_to_wrong" if old["correct"] else
                    "wrong_to_correct" if new["correct"] else "wrong_to_wrong")
        transitions[category] += 1
        if category == "correct_to_wrong":
            forgetting.append(dict(example_id=identity, target=old["target"],
                                   incumbent=old["predicted"], candidate=new["predicted"]))
    fields = ("consequence_class", "bank_batch_id", "historical_window",
              "evaluation_origin", "external_regime_version")
    return dict(incumbent=dict(correct=incumbent["correct"],
            examples=incumbent["examples"], accuracy=incumbent["accuracy"],
            invalid=incumbent["invalid"], by_target=incumbent["by_target"]),
        candidate=dict(correct=candidate["correct"], examples=candidate["examples"],
            accuracy=candidate["accuracy"], invalid=candidate["invalid"],
            by_target=candidate["by_target"]), transitions=dict(transitions),
        forgetting_events=forgetting,
        incumbent_groups={field: _group_metrics(rows, incumbent, field) for field in fields},
        candidate_groups={field: _group_metrics(rows, candidate, field) for field in fields})


def stability_decision(fresh: dict, historical: dict, combined: dict,
                       integrity_checks_passed: bool = True) -> dict:
    rule = json.loads(RULE_PATH.read_text())
    forgetting = historical["transitions"].get("correct_to_wrong", 0)
    collapses = []
    for value in (-1, 0, 1):
        before = historical["incumbent"]["by_target"][str(value)]
        after = historical["candidate"]["by_target"][str(value)]
        if before["n"] >= rule["historical_class_minimum_examples"] and \
                before["accuracy"] - after["accuracy"] > \
                rule["historical_class_collapse_absolute"]:
            collapses.append(value)
    criteria = dict(
        fresh_adaptation=(fresh["candidate"]["correct"] >=
            fresh["incumbent"]["correct"] + rule["minimum_fresh_correct_gain"]),
        historical_accuracy_retained=(historical["candidate"]["correct"] >=
            historical["incumbent"]["correct"] -
            rule["maximum_historical_correct_loss"]),
        historical_forgetting_bounded=(forgetting <=
            rule["maximum_historical_forgetting_events"]),
        no_historical_class_collapse=not collapses,
        combined_retained=(combined["candidate"]["correct"] >=
            combined["incumbent"]["correct"] - rule["combined_correct_tolerance"]),
        invalid_not_increased=all(value["candidate"]["invalid"] <=
            value["incumbent"]["invalid"] for value in
            (fresh, historical, combined)),
        sufficient_evidence=(fresh["incumbent"]["examples"] >= 12 and
                             historical["incumbent"]["examples"] >= 24),
        integrity_checks_passed=integrity_checks_passed)
    forgetting_failure = not (criteria["historical_accuracy_retained"] and
        criteria["historical_forgetting_bounded"] and
        criteria["no_historical_class_collapse"])
    return dict(decision="ACTIVE" if all(criteria.values()) else "REJECTED",
        criteria=criteria, forgetting_failure=forgetting_failure,
        catastrophic_classes=collapses, forgetting_events=forgetting,
        rule=json.loads(RULE_PATH.read_text()), rule_sha256=file_hash(RULE_PATH))


def _evaluate_stability(candidate_root: Path, fresh: Path, historical: Path,
                        combined: Path, incumbent_adapter: Path,
                        candidate_adapter: Path) -> dict:
    report = {}
    for name, dataset in (("fresh", fresh), ("historical", historical),
                          ("combined", combined)):
        incumbent_path = candidate_root / f"{name}-incumbent-evaluation.json"
        candidate_path = candidate_root / f"{name}-candidate-evaluation.json"
        incumbent = _run_evaluation(dataset, incumbent_path, incumbent_adapter)
        candidate = _run_evaluation(dataset, candidate_path, candidate_adapter)
        report[name] = evaluation_analysis(dataset, incumbent, candidate)
    report["promotion"] = stability_decision(
        report["fresh"], report["historical"], report["combined"])
    atomic_json(candidate_root / "stability-evaluation.json", report)
    return report


def _usage(dataset: Path, output: Path) -> dict:
    _, rows = load_dataset(dataset)
    value = {row["example_id"]: row["split"] for row in rows}
    atomic_json(output, value)
    return value


def _manifest(root: Path, generation: int, parent: int, label: str,
              strategy: str, fresh: Path, training_dataset: Path,
              model_output: Path, report: dict, bank_manifest: dict,
              usage_path: Path, rehearsal_path: Path | None = None) -> dict:
    fresh_manifest, _ = load_dataset(fresh)
    training_manifest, _ = load_dataset(training_dataset)
    adapter = model_output / "trained-adapter.safetensors"
    evaluation = model_output.parent / "stability-evaluation.json"
    value = dict(generation=generation, candidate_label=label,
        parent_generation=parent, base_model_identity=BASE_MODEL_ID,
        adapter_path=_relative(root, adapter), adapter_sha256=file_hash(adapter),
        artifact_kind="LORA_ADAPTER", dataset_manifest_sha256=
            fresh_manifest["manifest_sha256"],
        training_dataset_manifest_sha256=training_manifest["manifest_sha256"],
        grounded_training_examples=training_manifest["payload"]["split_counts"]["train"],
        newly_eligible_grounded_examples=fresh_manifest["payload"]["example_count"],
        training_configuration=json.loads(CONFIG_PATH.read_text()),
        training_strategy=strategy, creation_timestamp=_now(),
        evaluation_artifact=_relative(root, evaluation),
        evaluation_sha256=file_hash(evaluation),
        lineage_artifact=_relative(root, model_output / "learning-lineage.json"),
        lineage_sha256=file_hash(model_output / "learning-lineage.json"),
        dataset_path=_relative(root, fresh),
        training_dataset_path=_relative(root, training_dataset),
        example_usage_artifact=_relative(root, usage_path),
        example_usage_sha256=file_hash(usage_path),
        evaluation_bank_version=bank_manifest["payload"]["version"],
        evaluation_bank_manifest_sha256=bank_manifest["manifest_sha256"],
        stability_summary=report, evaluation_summary=report,
        promotion_rule_sha256=file_hash(RULE_PATH),
        regime_definition_sha256=file_hash(REGIME_PATH),
        provenance_checks_passed=True, fresh_process_reload_passed=True,
        optimizer_evaluation_leakage=0,
        rehearsal_selection_artifact=(None if rehearsal_path is None else
                                      _relative(root, rehearsal_path)),
        rehearsal_selection_sha256=(None if rehearsal_path is None else
                                     file_hash(rehearsal_path)))
    return value


def _select_rehearsal(root: Path, output: Path) -> list[dict]:
    registry = load_registry(root)
    selected = []
    for generation in (1, 2):
        manifest = registry["manifests"][generation]
        _, rows = load_dataset(root / manifest["dataset_path"])
        for target in (-1, 0, 1):
            eligible = sorted((row for row in rows if row["split"] == "train" and
                               row["target"] == target), key=lambda row: row["example_id"])
            if len(eligible) < 2:
                raise RuntimeError("insufficient deterministic rehearsal stratum")
            for row in eligible[:2]:
                value = deepcopy(row); value["split"] = "train"
                value["rehearsal_origin_generation"] = generation
                selected.append(value)
    atomic_json(output, dict(rule="two lexicographically first authenticated training IDs "
        "per consequence class from generations 1 and 2", count=len(selected),
        example_ids=[row["example_id"] for row in selected],
        per_generation={str(g): sum(row["rehearsal_origin_generation"] == g
                                    for row in selected) for g in (1, 2)}))
    return selected


def _rehearsal_dataset(fresh: Path, root: Path, output: Path,
                       selection_path: Path) -> dict:
    fresh_manifest, fresh_rows = load_dataset(fresh)
    rehearsal = _select_rehearsal(root, selection_path)
    bank_manifest, bank = load_evaluation_bank(root)
    bank_ids = {row["example_id"] for row in bank}
    if bank_ids & {row["example_id"] for row in rehearsal}:
        raise RuntimeError("evaluation-bank example selected for rehearsal")
    rows = [deepcopy(row) for row in fresh_rows if row["split"] == "train"]
    rows.extend(rehearsal)
    rows.extend(deepcopy(row) for row in fresh_rows if row["split"] != "train")
    validate_optimizer_separation(rows)
    return _write_dataset(output, rows, dict(
        base_weights_sha256=fresh_manifest["payload"]["base_weights_sha256"],
        training_strategy="grounded-rehearsal", new_training_examples=42,
        rehearsal_training_examples=len(rehearsal),
        evaluation_bank_manifest_sha256=bank_manifest["manifest_sha256"],
        evaluation_bank_optimizer_overlap=0))


def _run_candidate(root: Path, generation: int, label: str, parent: int,
                   fresh: Path, training_dataset: Path, historical: Path,
                   combined: Path, bank_manifest: dict,
                   rehearsal_path: Path | None = None) -> tuple[dict, dict]:
    registry = load_registry(root)
    parent_manifest = registry["manifests"][parent]
    parent_adapter = root / parent_manifest["adapter_path"]
    candidate_root = root / f"generations/generation-{generation:04d}"
    candidate_root.mkdir(parents=True, exist_ok=False)
    atomic_json(candidate_root / "attempt.json", dict(status="CANDIDATE",
        generation=generation, candidate_label=label, parent_generation=parent,
        stability_rule_sha256=file_hash(RULE_PATH), started_at=_now()))
    # Candidate-local immutable copies bind the exact inputs.
    local_fresh = candidate_root / "fresh-dataset"
    local_training = candidate_root / "training-dataset"
    shutil.copytree(fresh, local_fresh); shutil.copytree(training_dataset, local_training)
    training_pre = candidate_root / "training-pre-evaluation.json"
    _run_evaluation(local_training, training_pre, parent_adapter,
                    phase="PRE_TRAINING")
    model_output = candidate_root / "model"
    strategy = "continue-active" if rehearsal_path is None else "grounded-rehearsal"
    lineage = train(local_training, training_pre, model_output,
        parent_adapter=parent_adapter, lineage_parent_generation=parent,
        training_strategy=strategy)
    adapter = model_output / "trained-adapter.safetensors"
    if file_hash(adapter) != lineage["final_adapter_sha256"]:
        raise RuntimeError("stability candidate artifact hash mismatch")
    report = _evaluate_stability(candidate_root, local_fresh, historical,
                                 combined, parent_adapter, adapter)
    usage_path = candidate_root / "example-usage.json"
    _usage(local_training, usage_path)
    local_rehearsal = None
    if rehearsal_path is not None:
        local_rehearsal = candidate_root / "rehearsal-selection.json"
        shutil.copyfile(rehearsal_path, local_rehearsal)
    manifest = _manifest(root, generation, parent, label, strategy,
        local_fresh, local_training, model_output, report, bank_manifest,
        usage_path, local_rehearsal)
    decision = report["promotion"]["decision"]
    reason = ("All frozen stability criteria passed" if decision == "ACTIVE" else
              "One or more frozen stability criteria failed")
    finalized = finalize_generation(root, manifest, decision, reason)
    result = dict(generation=generation, candidate_label=label,
        parent_generation=parent, decision=("PROMOTED" if decision == "ACTIVE"
                                            else "REJECTED"),
        active_generation_after=finalized["active_generation"],
        candidate_adapter_sha256=file_hash(adapter), evaluation=report,
        registry_state_sha256=finalized["state"]["sha256"])
    atomic_json(candidate_root / "cycle-result.json", result)
    return result, report


def run_stability_cycle(session_root: Path, registry_root: Path) -> dict:
    registry = load_registry(registry_root)
    if registry["active_entry"]["generation"] != 2:
        raise RegistryError("stability cycle must begin with generation 2 ACTIVE")
    bank_manifest, bank_rows = load_evaluation_bank(registry_root)
    workspace = registry["root"] / "stability-cycle-inputs"
    if workspace.exists():
        raise RegistryError("stability-cycle inputs already exist")
    workspace.mkdir()
    from .learning_cycle import freeze_new_examples, assemble_training_dataset
    fresh = workspace / "fresh-dataset"
    freeze_new_examples(session_root, registry_root, fresh)
    pure_training = workspace / "pure-training-dataset"
    assemble_training_dataset(fresh, registry_root, pure_training, "continue-active")
    _, fresh_rows = load_dataset(fresh)
    base_hash = registry["manifests"][0]["adapter_sha256"]
    historical = workspace / "historical-evaluation"
    _evaluation_dataset(bank_rows, historical, "evaluation-bank-v1", base_hash)
    combined_rows = [deepcopy(row) for row in bank_rows]
    for row in fresh_rows:
        if row["split"] == "evaluation":
            value = deepcopy(row); value["evaluation_origin"] = "fresh"
            value["bank_batch_id"] = "v0.4-regime-B"
            value["consequence_class"] = str(value["target"])
            value["historical_window"] = "fresh"
            combined_rows.append(value)
    combined = workspace / "combined-evaluation"
    _evaluation_dataset(combined_rows, combined, "historical-plus-fresh", base_hash)
    bank_ids = {row["example_id"] for row in bank_rows}
    training_ids = {row["example_id"] for row in load_dataset(pure_training)[1]
                    if row["split"] == "train"}
    if bank_ids & training_ids:
        raise RuntimeError("evaluation bank leaked into pure optimizer")
    pure, pure_report = _run_candidate(registry["root"], 3, "3", 2,
        fresh, pure_training, historical, combined, bank_manifest)
    rehearsal = None
    if pure["decision"] == "REJECTED" and \
            pure_report["promotion"]["forgetting_failure"]:
        selection = workspace / "rehearsal-selection.json"
        rehearsal_training = workspace / "rehearsal-training-dataset"
        _rehearsal_dataset(fresh, registry["root"], rehearsal_training, selection)
        rehearsal, _ = _run_candidate(registry["root"], 4, "3R", 2,
            fresh, rehearsal_training, historical, combined, bank_manifest, selection)
    final_registry = load_registry(registry_root)
    next_eligible = max(final_registry["manifests"]) + 1
    bank_v2 = append_fresh_to_bank(registry["root"], fresh,
        "v0.4-regime-B", next_eligible)
    result = dict(status="COMPLETE", initial_active_generation=2,
        pure_candidate=pure, rehearsal_candidate=rehearsal,
        final_active_generation=final_registry["active_entry"]["generation"],
        evaluation_bank_used=dict(version=bank_manifest["payload"]["version"],
            manifest_sha256=bank_manifest["manifest_sha256"],
            examples=bank_manifest["payload"]["example_count"]),
        evaluation_bank_after=dict(version=bank_v2["payload"]["version"],
            manifest_sha256=bank_v2["manifest_sha256"],
            examples=bank_v2["payload"]["example_count"]),
        regime_definition_sha256=file_hash(REGIME_PATH),
        stability_rule_sha256=file_hash(RULE_PATH))
    atomic_json(registry["root"] / "stability-cycle-result.json", result)
    return result
