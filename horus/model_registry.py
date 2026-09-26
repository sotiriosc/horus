"""Hash-addressed consequence-model registry with atomic active selection."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
from typing import Any

from .core import digest
from .grounded_learning import BASE_MODEL_ID, ROOT, atomic_json, file_hash


VALID_STATUSES = {"CANDIDATE", "ACTIVE", "REJECTED", "RETIRED"}
REGISTRY_VERSION = 1


class RegistryError(RuntimeError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _inside(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise RegistryError("registry path escapes its root") from exc
    return candidate


def _document(payload: dict) -> dict:
    return {"payload": payload, "sha256": digest(payload)}


def _read_document(path: Path, label: str) -> dict:
    try:
        document = json.loads(path.read_text())
        payload = document["payload"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise RegistryError(f"invalid {label} document") from exc
    if digest(payload) != document.get("sha256"):
        raise RegistryError(f"{label} hash mismatch")
    return document


def _write_document(path: Path, payload: dict) -> dict:
    document = _document(payload)
    atomic_json(path, document)
    return document


def _write_state(root: Path, generations: list[dict]) -> tuple[str, dict]:
    payload = dict(version=REGISTRY_VERSION, generations=generations)
    document = _document(payload)
    relative = f"states/state-{document['sha256']}.json"
    path = _inside(root, relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if _read_document(path, "registry state") != document:
            raise RegistryError("state hash collision")
    else:
        atomic_json(path, document)
    return relative, document


def _write_active(root: Path, state_relative: str, state: dict,
                  active_entry: dict) -> dict:
    payload = dict(version=REGISTRY_VERSION,
        generation=active_entry["generation"],
        artifact_sha256=active_entry["artifact_sha256"],
        generation_manifest_sha256=active_entry["manifest_sha256"],
        registry_state_file=state_relative,
        registry_state_sha256=state["sha256"],
        updated_at=_now())
    return _write_document(root / "active-model.json", payload)


def _copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".tmp")
    shutil.copyfile(source, temporary)
    with temporary.open("rb") as stream:
        os.fsync(stream.fileno())
    os.replace(temporary, destination)


def _copy_dataset(source: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=False)
    for name in ("examples.jsonl", "dataset-manifest.json"):
        _copy_file(source / name, destination / name)


def _write_manifest(root: Path, generation: int, payload: dict) -> tuple[str, dict]:
    relative = f"generations/generation-{generation:04d}/generation.json"
    path = _inside(root, relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise RegistryError(f"generation {generation} already exists")
    return relative, _write_document(path, payload)


def initialize_registry(root: Path) -> dict:
    """Import frozen base as generation 0 and v0.2 adapter as generation 1."""
    root = root.resolve()
    if root.exists():
        raise RegistryError("registry already exists")
    (root / "states").mkdir(parents=True)
    source_model = ROOT / "models/horus_consequence_v0_2"
    source_evidence = ROOT / "research/grounded-learning-v0"
    config = json.loads((ROOT / "horus/training_config.json").read_text())

    gen1 = root / "generations/generation-0001"
    _copy_file(source_model / "trained-adapter.safetensors",
               gen1 / "trained-adapter.safetensors")
    _copy_file(source_model / "learning-lineage.json", gen1 / "learning-lineage.json")
    _copy_file(source_evidence / "post-training-evaluation.json",
               gen1 / "evaluation.json")
    (gen1 / "dataset").mkdir(parents=True)
    _copy_file(source_evidence / "examples.jsonl", gen1 / "dataset/examples.jsonl")
    _copy_file(source_evidence / "dataset-manifest.json",
               gen1 / "dataset/manifest.json")
    examples = [json.loads(line) for line in
                (source_evidence / "examples.jsonl").read_text().splitlines()]
    usage = {row["example_id"]: row["split"] for row in examples}
    atomic_json(gen1 / "example-usage.json", usage)
    lineage = json.loads((gen1 / "learning-lineage.json").read_text())
    evaluation = json.loads((gen1 / "evaluation.json").read_text())

    base_payload = dict(generation=0, parent_generation=None,
        base_model_identity=BASE_MODEL_ID, adapter_path=None,
        adapter_sha256=lineage["base_weights_sha256"],
        artifact_kind="FROZEN_BASE_WEIGHTS", dataset_manifest_sha256=None,
        grounded_training_examples=0, training_configuration=None,
        creation_timestamp=_now(), evaluation_artifact=None,
        evaluation_sha256=None, lineage_artifact=None, lineage_sha256=None,
        example_usage_artifact=None, example_usage_sha256=None,
        creation_status="RETIRED",
        reason="Superseded by the imported v0.2 grounded adapter")
    rel0, doc0 = _write_manifest(root, 0, base_payload)

    gen1_payload = dict(generation=1, parent_generation=0,
        base_model_identity=BASE_MODEL_ID,
        adapter_path="generations/generation-0001/trained-adapter.safetensors",
        adapter_sha256=file_hash(gen1 / "trained-adapter.safetensors"),
        artifact_kind="LORA_ADAPTER", dataset_manifest_sha256=
            lineage["authenticated_dataset_manifest_sha256"],
        grounded_training_examples=lineage["training_examples"],
        training_configuration=config, creation_timestamp=_now(),
        evaluation_artifact="generations/generation-0001/evaluation.json",
        evaluation_sha256=file_hash(gen1 / "evaluation.json"),
        lineage_artifact="generations/generation-0001/learning-lineage.json",
        lineage_sha256=file_hash(gen1 / "learning-lineage.json"),
        dataset_path="generations/generation-0001/dataset",
        example_usage_artifact="generations/generation-0001/example-usage.json",
        example_usage_sha256=file_hash(gen1 / "example-usage.json"),
        creation_status="ACTIVE", reason="Imported verified Horus v0.2 incumbent",
        evaluation_summary=dict(examples=evaluation["examples"],
            correct=evaluation["correct"], accuracy=evaluation["accuracy"],
            by_target=evaluation["by_target"], invalid=evaluation["invalid"]))
    rel1, doc1 = _write_manifest(root, 1, gen1_payload)
    entries = [
        dict(generation=0, parent_generation=None, status="RETIRED",
             reason=base_payload["reason"], manifest=rel0,
             manifest_sha256=doc0["sha256"],
             artifact_sha256=base_payload["adapter_sha256"]),
        dict(generation=1, parent_generation=0, status="ACTIVE",
             reason=gen1_payload["reason"], manifest=rel1,
             manifest_sha256=doc1["sha256"],
             artifact_sha256=gen1_payload["adapter_sha256"]),
    ]
    state_rel, state = _write_state(root, entries)
    active = _write_active(root, state_rel, state, entries[1])
    return dict(root=str(root), state=state, active=active)


def _verify_manifest(root: Path, entry: dict) -> dict:
    document = _read_document(_inside(root, entry["manifest"]),
                              f"generation {entry['generation']} manifest")
    if document["sha256"] != entry["manifest_sha256"]:
        raise RegistryError("generation manifest identity mismatch")
    value = document["payload"]
    if value.get("generation") != entry["generation"] or \
            value.get("parent_generation") != entry["parent_generation"]:
        raise RegistryError("generation manifest lineage mismatch")
    if value.get("adapter_sha256") != entry["artifact_sha256"]:
        raise RegistryError("generation artifact identity mismatch")
    adapter = value.get("adapter_path")
    if adapter is not None:
        path = _inside(root, adapter)
        if not path.is_file() or file_hash(path) != value["adapter_sha256"]:
            raise RegistryError("generation adapter hash mismatch")
    for path_key, hash_key in (("evaluation_artifact", "evaluation_sha256"),
                               ("lineage_artifact", "lineage_sha256"),
                               ("example_usage_artifact", "example_usage_sha256")):
        relative = value.get(path_key)
        if relative is not None:
            path = _inside(root, relative)
            if not path.is_file() or file_hash(path) != value[hash_key]:
                raise RegistryError(f"generation {path_key} hash mismatch")
    return value


def load_registry(root: Path) -> dict:
    root = root.resolve()
    active = _read_document(root / "active-model.json", "active model")
    active_payload = active["payload"]
    state_path = _inside(root, active_payload["registry_state_file"])
    state = _read_document(state_path, "registry state")
    if state["sha256"] != active_payload["registry_state_sha256"]:
        raise RegistryError("active reference/state mismatch")
    entries = state["payload"].get("generations")
    if state["payload"].get("version") != REGISTRY_VERSION or not isinstance(entries, list):
        raise RegistryError("unsupported registry state")
    numbers = [entry.get("generation") for entry in entries]
    if len(numbers) != len(set(numbers)):
        raise RegistryError("duplicate generation")
    by_number, manifests = {}, {}
    for entry in entries:
        if entry.get("status") not in VALID_STATUSES:
            raise RegistryError("invalid generation status")
        manifests[entry["generation"]] = _verify_manifest(root, entry)
        by_number[entry["generation"]] = entry
    for entry in entries:
        parent = entry["parent_generation"]
        if parent is not None and parent not in by_number:
            raise RegistryError("missing parent generation")
        if parent is not None and parent >= entry["generation"]:
            raise RegistryError("invalid generation ordering")
    active_entries = [entry for entry in entries if entry["status"] == "ACTIVE"]
    if len(active_entries) != 1:
        raise RegistryError("registry must contain exactly one ACTIVE generation")
    selected = active_entries[0]
    if selected["generation"] != active_payload["generation"] or \
            selected["manifest_sha256"] != active_payload["generation_manifest_sha256"] or \
            selected["artifact_sha256"] != active_payload["artifact_sha256"]:
        raise RegistryError("active reference does not bind ACTIVE generation")
    return dict(root=root, active_document=active, state_document=state,
                entries=entries, manifests=manifests, active_entry=selected,
                active_manifest=manifests[selected["generation"]])


def active_model_spec(root: Path) -> dict:
    registry = load_registry(root)
    value = registry["active_manifest"]
    return dict(generation=value["generation"],
        parent_generation=value["parent_generation"],
        base_model_identity=value["base_model_identity"],
        adapter_path=None if value["adapter_path"] is None else
            str(_inside(registry["root"], value["adapter_path"])),
        artifact_sha256=value["adapter_sha256"],
        adapter_identity=("BASE" if value["adapter_path"] is None else
                          f"generation-{value['generation']}:{value['adapter_sha256']}"),
        registry_state_sha256=registry["state_document"]["sha256"],
        generation_manifest_sha256=registry["active_entry"]["manifest_sha256"])


def consumed_examples(registry: dict) -> dict[str, list[dict]]:
    consumed: dict[str, list[dict]] = {}
    for entry in registry["entries"]:
        manifest = registry["manifests"][entry["generation"]]
        relative = manifest.get("example_usage_artifact")
        if relative is None:
            continue
        usage = json.loads(_inside(registry["root"], relative).read_text())
        for identity, role in usage.items():
            consumed.setdefault(identity, []).append(dict(
                generation=entry["generation"], role=role))
    return consumed


def finalize_generation(root: Path, manifest_payload: dict, status: str,
                        reason: str) -> dict:
    """Publish one completed decision through a new immutable state snapshot."""
    if status not in {"ACTIVE", "REJECTED"}:
        raise ValueError("candidate final status must be ACTIVE or REJECTED")
    registry = load_registry(root)
    generation = manifest_payload["generation"]
    if generation in registry["manifests"]:
        raise RegistryError("duplicate generation")
    expected = max(registry["manifests"]) + 1
    if generation != expected:
        raise RegistryError(f"next generation must be {expected}")
    if manifest_payload["parent_generation"] != registry["active_entry"]["generation"]:
        raise RegistryError("candidate parent is not the incumbent")
    manifest_payload = deepcopy(manifest_payload)
    manifest_payload["creation_status"] = "CANDIDATE"
    manifest_payload["final_status"] = status
    manifest_payload["reason"] = reason
    relative, document = _write_manifest(root, generation, manifest_payload)
    entries = deepcopy(registry["entries"])
    if status == "ACTIVE":
        for entry in entries:
            if entry["status"] == "ACTIVE":
                entry["status"] = "RETIRED"
                entry["reason"] = f"Superseded by generation {generation}"
    entry = dict(generation=generation,
        parent_generation=manifest_payload["parent_generation"], status=status,
        reason=reason, manifest=relative, manifest_sha256=document["sha256"],
        artifact_sha256=manifest_payload["adapter_sha256"])
    entries.append(entry)
    state_rel, state = _write_state(registry["root"], entries)
    selected = entry if status == "ACTIVE" else next(
        item for item in entries if item["status"] == "ACTIVE")
    active = _write_active(registry["root"], state_rel, state, selected)
    return dict(decision=status, generation=generation,
                active_generation=selected["generation"], state=state, active=active)


def history(root: Path) -> list[dict]:
    registry = load_registry(root)
    rows = []
    for entry in registry["entries"]:
        manifest = registry["manifests"][entry["generation"]]
        rows.append(dict(generation=entry["generation"],
            candidate_label=manifest.get("candidate_label", str(entry["generation"])),
            parent_generation=entry["parent_generation"], status=entry["status"],
            reason=entry["reason"], base_model=manifest["base_model_identity"],
            adapter_sha256=entry["artifact_sha256"],
            grounded_training_examples=manifest["grounded_training_examples"],
            evaluation_summary=manifest.get("evaluation_summary"),
            evaluation_bank_version=manifest.get("evaluation_bank_version")))
    return rows
