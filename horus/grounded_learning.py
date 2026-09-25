"""Grounded consequence-model dataset, LoRA training, and evaluation.

Only authorized realized receipts supply labels.  The held-out split is made by
whole session before any optimizer step.  This module never trains next-state
or Explorer.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import random
from typing import Any

from experiments.map_consequence_only_isolation_v0.protocol import parse

from .core import MAPPING, MapForecast, MechanicalExplorer, digest
from .live import CONSEQUENCE_SYSTEM, ModelClient, SessionStore, run_live


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = Path(__file__).with_name("training_config.json")
BASE_MODEL_REPOSITORY = "Qwen/Qwen2.5-0.5B-Instruct"
BASE_MODEL_REVISION = "7ae557604adf67be50417f59c2c2f167def9a775"
BASE_MODEL_ID = f"{BASE_MODEL_REPOSITORY}@{BASE_MODEL_REVISION}"
CANDIDATES = tuple(json.dumps({"consequence": value}, separators=(",", ":"))
                   for value in (-1, 0, 1))


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def file_hash(path: Path) -> str:
    value = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    with temporary.open("rb") as stream:
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def default_adapter_path() -> Path:
    return ROOT / "models/horus_consequence_v0_2/trained-adapter.safetensors"


def _model_path(path: Path | None = None) -> Path:
    if path is None:
        from huggingface_hub import snapshot_download
        try:
            candidate = Path(snapshot_download(
                repo_id=BASE_MODEL_REPOSITORY,
                revision=BASE_MODEL_REVISION,
                local_files_only=True,
            ))
        except Exception as exc:
            raise RuntimeError(
                "the pinned Qwen base snapshot is not in the local Hugging Face "
                "cache; supply its directory explicitly"
            ) from exc
    else:
        candidate = Path(path)
    if not (candidate / "model.safetensors").is_file():
        raise RuntimeError(f"base model snapshot unavailable: {candidate}")
    return candidate


def chat_prefix(system: str, prompt: str) -> str:
    return (f"<|im_start|>system\n{system}<|im_end|>\n"
            f"<|im_start|>user\n{prompt}<|im_end|>\n"
            "<|im_start|>assistant\n")


class LoRALinear:
    """Factory namespace; implementation is created lazily after torch import."""


def inject_lora(model, config: dict):
    import torch
    from torch import nn

    class Layer(nn.Module):
        def __init__(self, base):
            super().__init__()
            self.base = base
            self.base.requires_grad_(False)
            rank = config["adapter_rank"]
            self.lora_A = nn.Linear(base.in_features, rank, bias=False,
                                    dtype=torch.float32).to(base.weight.device)
            self.lora_B = nn.Linear(rank, base.out_features, bias=False,
                                    dtype=torch.float32).to(base.weight.device)
            nn.init.kaiming_uniform_(self.lora_A.weight, a=math.sqrt(5))
            nn.init.zeros_(self.lora_B.weight)
            self.dropout = nn.Dropout(config["adapter_dropout"])
            self.scaling = config["adapter_alpha"] / rank

        def forward(self, value):
            original = self.base(value)
            adapted = self.lora_B(self.lora_A(
                self.dropout(value).to(self.lora_A.weight.dtype))) * self.scaling
            return original + adapted.to(original.dtype)

    model.requires_grad_(False)
    targets = set(config["target_modules"])
    replacements = []
    for name, module in list(model.named_modules()):
        if name.rsplit(".", 1)[-1] in targets and isinstance(module, nn.Linear):
            parent_name, child = name.rsplit(".", 1)
            parent = model.get_submodule(parent_name)
            replacements.append((name, parent, child, module))
    if not replacements:
        raise RuntimeError("no registered LoRA target modules found")
    for _, parent, child, module in replacements:
        setattr(parent, child, Layer(module))
    trainable = sum(parameter.numel() for parameter in model.parameters()
                    if parameter.requires_grad)
    return [name for name, *_ in replacements], trainable


def adapter_state(model) -> dict:
    return {name: value.detach().cpu().contiguous()
            for name, value in model.state_dict().items()
            if ".lora_A." in name or ".lora_B." in name}


def save_adapter(model, path: Path) -> None:
    from safetensors.torch import save_file
    save_file(adapter_state(model), str(path))


def load_adapter(model, path: Path) -> None:
    from safetensors.torch import load_file
    values = load_file(str(path))
    expected = set(adapter_state(model))
    if set(values) != expected:
        raise RuntimeError("adapter tensor registry mismatch")
    result = model.load_state_dict(values, strict=False)
    if result.unexpected_keys:
        raise RuntimeError("unexpected adapter tensor")


class QwenConsequenceClient:
    """Constrained consequence scorer over the three permitted JSON values."""
    def __init__(self, adapter_path: Path | None = None,
                 model_path: Path | None = None, device: str | None = None):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.requests = 0
        self.path = _model_path(model_path)
        self.adapter_path = adapter_path
        self.model_id = (BASE_MODEL_ID if adapter_path is None else
            f"horus-consequence-v0.2:{file_hash(adapter_path)}")
        device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.device = torch.device(device)
        dtype = torch.bfloat16 if device == "cuda" else torch.float32
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.path, local_files_only=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.path, local_files_only=True, dtype=dtype).to(self.device)
        if adapter_path is not None:
            config = json.loads(CONFIG_PATH.read_text())
            inject_lora(self.model, config)
            load_adapter(self.model, adapter_path)
        self.model.eval()

    def _score(self, system: str, prompt: str):
        import torch
        prefix = chat_prefix(system, prompt)
        prefix_ids = self.tokenizer(prefix, add_special_tokens=False).input_ids
        rows, lengths = [], []
        for candidate in CANDIDATES:
            ids = self.tokenizer(prefix + candidate + "<|im_end|>\n",
                                 add_special_tokens=False).input_ids
            rows.append(ids)
            lengths.append(len(ids))
        maximum = max(lengths)
        pad = self.tokenizer.pad_token_id
        input_ids = torch.tensor([row + [pad] * (maximum - len(row))
                                  for row in rows], device=self.device)
        mask = torch.tensor([[1] * len(row) + [0] * (maximum - len(row))
                             for row in rows], device=self.device)
        with torch.no_grad():
            logits = self.model(input_ids=input_ids,
                                attention_mask=mask).logits.float()
        log_probs = logits[:, :-1].log_softmax(-1)
        token_ids = input_ids[:, 1:]
        gathered = log_probs.gather(-1, token_ids.unsqueeze(-1)).squeeze(-1)
        scores = []
        for index, length in enumerate(lengths):
            start = len(prefix_ids) - 1
            stop = length - 1
            scores.append(float(gathered[index, start:stop].mean().item()))
        best = max(range(3), key=lambda index: scores[index])
        return CANDIDATES[best], scores

    def generate(self, request_body: dict) -> dict:
        self.requests += 1
        if request_body.get("system") != CONSEQUENCE_SYSTEM:
            return dict(raw_output=None, transport_error="ROLE_VIOLATION",
                        response_metadata={})
        raw, scores = self._score(request_body["system"], request_body["prompt"])
        return dict(raw_output=raw, transport_error=None,
            response_metadata=dict(model=self.model_id,
                decoding="mean_log_probability_over_three_exact_JSON_candidates",
                candidate_scores=dict(zip(CANDIDATES, scores)), done=True))


def collect(root: Path, target: int = 60, max_sessions: int = 20,
            steps_per_session: int = 6) -> dict:
    if root.exists():
        raise RuntimeError("collection root already exists")
    if not 60 <= target <= 120:
        raise ValueError("registered target must be 60..120")
    root.mkdir(parents=True)
    joint = ModelClient()
    consequence = QwenConsequenceClient(device="cuda")
    sessions, authorized = [], 0
    for index in range(max_sessions):
        remaining = target - authorized
        if remaining <= 0:
            break
        path = root / f"session-{index:03d}"
        result = run_live(path, min(steps_per_session, remaining), False,
                          client=joint, consequence_client=consequence)
        count = sum(row["status"] == "AUTHORIZED" for row in result["steps"])
        sessions.append(dict(name=path.name, authorized=count,
            attempted=len(result["steps"]), joint_calls=result["joint_model_calls"],
            consequence_calls=result["consequence_model_calls"]))
        authorized += count
        print(f"collection {path.name}: authorized={count}; total={authorized}/{target}",
              flush=True)
    distribution = {-1: 0, 0: 0, 1: 0}
    for item in sessions:
        with SessionStore(root / item["name"], True) as store:
            for row in store.imported_history():
                distribution[row["receipt"]["realized_consequence"]] += 1
    result = dict(status="COMPLETE" if authorized >= target else "INSUFFICIENT",
        target=target, authorized=authorized, sessions=sessions,
        consequence_distribution={str(key): value for key, value in distribution.items()},
        joint_model="dolphin-mixtral:latest", consequence_model=BASE_MODEL_ID,
        selection="fixed target/max-session schedule; no outcome-based extension beyond target")
    atomic_json(root / "collection.json", result)
    if authorized < target:
        raise RuntimeError("bounded collection ended below registered target")
    return result


def _iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _build_example(store: SessionStore, session_name: str,
                   event_envelope: dict, training_envelope: dict) -> dict:
    event, training = event_envelope["record"], training_envelope["record"]
    receipt = event["receipt"]
    if event["authorization_status"] != "AUTHORIZED" or \
            training["authorization_status"] != "AUTHORIZED":
        raise RuntimeError("unauthorized training candidate")
    if training["receipt_identity"] != event["receipt_identity"] or \
            training["receipt_provenance_sha256"] != event["receipt_provenance_sha256"]:
        raise RuntimeError("training/event receipt provenance mismatch")
    if digest(receipt) != event["receipt_provenance_sha256"]:
        raise RuntimeError("receipt provenance hash mismatch")
    memory = event["memory_record"]
    for key, receipt_key in (("epoch", "epoch"), ("transaction_id", "transaction_id"),
            ("pre_state", "pre_state"), ("action", "action"),
            ("next_state", "next_state"), ("consequence", "realized_consequence")):
        if memory[key] != receipt[receipt_key]:
            raise RuntimeError("authorized Memory differs from receipt")
    call_id = training["decision_id"] + ":" + training["chosen_action"] + ":C"
    rows = [row for row in store.records["calls"]
            if row["record"].get("call_id") == call_id]
    kinds = [row["kind"] for row in rows]
    if kinds != ["REQUEST_INTENT", "RESPONSE", "PARSED"]:
        raise RuntimeError("consequence call lifecycle incomplete or duplicated")
    intent, response, parsed = (row["record"] for row in rows)
    request = intent["request"]
    if intent["request_sha256"] != training["consequence_request_sha256"] or \
            digest(request) != intent["request_sha256"]:
        raise RuntimeError("registered consequence request hash mismatch")
    if request["system"] != CONSEQUENCE_SYSTEM or \
            intent.get("independent_of_joint_response") is not True:
        raise RuntimeError("consequence independence contract missing")
    if not (_iso(intent["recorded_at"]) <= _iso(response["recorded_at"]) <=
            _iso(parsed["recorded_at"]) < _iso(event["recorded_at"])):
        raise RuntimeError("prediction was not durably complete before receipt")
    payload = json.loads(request["prompt"])
    alias = next(key for key, value in MAPPING.items() if value == receipt["action"])
    earlier = [row["record"]["receipt"] for row in store.records["events"]
               if row["sequence"] < event_envelope["sequence"]]
    expected_history = [dict(epoch=row["epoch"], transaction_id=row["transaction_id"],
        surface_action=alias, next_state=row["next_state"],
        consequence=row["realized_consequence"]) for row in earlier
        if row["pre_state"] == receipt["pre_state"] and row["action"] == receipt["action"]]
    expected = dict(state=receipt["pre_state"], target_action=alias,
                    VERIFIED_CHRONOLOGICAL_HISTORY=expected_history)
    if payload != expected or training["chosen_action"] != receipt["action"]:
        raise RuntimeError("pre-execution context/action does not bind receipt")
    target = canonical({"consequence": receipt["realized_consequence"]})
    identity = dict(session_id=store.checkpoint["session_id"],
        receipt_identity=event["receipt_identity"], request_sha256=intent["request_sha256"],
        target=receipt["realized_consequence"])
    return dict(example_id=digest(identity), session_name=session_name,
        session_id=store.checkpoint["session_id"], order=training["order"],
        system=request["system"], prompt=request["prompt"],
        request_sha256=intent["request_sha256"],
        receipt_identity=event["receipt_identity"],
        receipt_provenance_sha256=event["receipt_provenance_sha256"],
        event_sequence=event_envelope["sequence"], target=receipt["realized_consequence"],
        target_json=target, prediction_before_execution=parsed["parsed"],
        prediction_raw_sha256=digest(response["response"]))


def freeze_dataset(collection_root: Path, output: Path) -> dict:
    if output.exists():
        raise RuntimeError("dataset output already exists")
    collection_result = json.loads((collection_root / "collection.json").read_text())
    names = [row["name"] for row in collection_result["sessions"] if row["authorized"]]
    if len(names) < 3:
        raise RuntimeError("session-level split requires at least three sessions")
    train_end = max(1, int(len(names) * 0.70))
    validation_end = max(train_end + 1, int(len(names) * 0.85))
    if validation_end >= len(names):
        validation_end = len(names) - 1
    assignment = {name: ("train" if index < train_end else
                         "validation" if index < validation_end else "evaluation")
                  for index, name in enumerate(names)}
    examples, seen = [], set()
    for name in names:
        with SessionStore(collection_root / name, True) as store:
            events = store.records["events"]
            training = store.records["training"]
            if len(events) != len(training):
                raise RuntimeError("event/training stream length mismatch")
            for event, train in zip(events, training):
                example = _build_example(store, name, event, train)
                if example["example_id"] in seen or tuple(example["receipt_identity"]) in seen:
                    raise RuntimeError("duplicate example or receipt identity")
                seen.add(example["example_id"]); seen.add(tuple(example["receipt_identity"]))
                example["split"] = assignment[name]
                examples.append(example)
    if not 60 <= len(examples) <= 120:
        raise RuntimeError("frozen dataset size outside registered bound")
    output.mkdir(parents=True)
    examples_path = output / "examples.jsonl"
    with examples_path.open("x") as stream:
        for row in examples:
            stream.write(canonical(row) + "\n")
    counts = {split: sum(row["split"] == split for row in examples)
              for split in ("train", "validation", "evaluation")}
    distribution = {split: {str(value): sum(row["split"] == split and
        row["target"] == value for row in examples) for value in (-1, 0, 1)}
        for split in counts}
    payload = dict(version=1, frozen_at=datetime.now().astimezone().isoformat(),
        collection_sha256=file_hash(collection_root / "collection.json"),
        examples_sha256=file_hash(examples_path), example_count=len(examples),
        split_counts=counts, consequence_distribution=distribution,
        session_assignment=assignment,
        ordered_example_ids=[row["example_id"] for row in examples],
        ordered_request_sha256=[row["request_sha256"] for row in examples],
        ordered_receipt_identities=[row["receipt_identity"] for row in examples],
        ordered_targets=[row["target"] for row in examples],
        training_config_sha256=file_hash(CONFIG_PATH), base_model=BASE_MODEL_ID,
        base_weights_sha256=file_hash(_model_path() / "model.safetensors"))
    document = dict(payload=payload, manifest_sha256=digest(payload))
    atomic_json(output / "manifest.json", document)
    return document


def load_dataset(directory: Path) -> tuple[dict, list[dict]]:
    manifest = json.loads((directory / "manifest.json").read_text())
    if digest(manifest["payload"]) != manifest["manifest_sha256"]:
        raise RuntimeError("dataset manifest hash mismatch")
    path = directory / "examples.jsonl"
    if file_hash(path) != manifest["payload"]["examples_sha256"]:
        raise RuntimeError("frozen examples hash mismatch")
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    if [row["example_id"] for row in rows] != manifest["payload"]["ordered_example_ids"]:
        raise RuntimeError("example order/identity mismatch")
    return manifest, rows


def evaluate(dataset: Path, output: Path, adapter: Path | None = None) -> dict:
    if output.exists():
        raise RuntimeError("evaluation output already exists")
    manifest, examples = load_dataset(dataset)
    rows = [row for row in examples if row["split"] == "evaluation"]
    client = QwenConsequenceClient(adapter_path=adapter, device="cuda")
    results = []
    for index, row in enumerate(rows, 1):
        response = client.generate(dict(system=row["system"], prompt=row["prompt"]))
        try:
            parsed = parse(response["raw_output"], "C")
            predicted, error = parsed["consequence"], None
        except (ValueError, TypeError) as exc:
            predicted, error = None, type(exc).__name__
        results.append(dict(example_id=row["example_id"], session_name=row["session_name"],
            target=row["target"], raw_response=response["raw_output"], predicted=predicted,
            parse_error=error, correct=predicted == row["target"],
            response_metadata=response["response_metadata"]))
        print(f"evaluation {index}/{len(rows)} target={row['target']} predicted={predicted}",
              flush=True)
    by_target = {str(value): dict(n=sum(row["target"] == value for row in results),
        correct=sum(row["target"] == value and row["correct"] for row in results))
        for value in (-1, 0, 1)}
    for item in by_target.values():
        item["accuracy"] = None if not item["n"] else item["correct"] / item["n"]
    output_value = dict(status="FROZEN", phase="POST_TRAINING" if adapter else "PRE_TRAINING",
        fresh_process_pid=os.getpid(), dataset_manifest_sha256=manifest["manifest_sha256"],
        model=client.model_id, adapter_sha256=None if adapter is None else file_hash(adapter),
        examples=len(results), correct=sum(row["correct"] for row in results),
        accuracy=sum(row["correct"] for row in results) / len(results),
        invalid=sum(row["predicted"] is None for row in results),
        by_target=by_target, results=results)
    atomic_json(output, output_value)
    return output_value


def _batch(tokenizer, rows: list[dict], max_length: int, device):
    import torch
    sequences, labels = [], []
    for row in rows:
        prefix = chat_prefix(row["system"], row["prompt"])
        prefix_ids = tokenizer(prefix, add_special_tokens=False).input_ids
        full_ids = tokenizer(prefix + row["target_json"] + "<|im_end|>\n",
                             add_special_tokens=False).input_ids[:max_length]
        if len(prefix_ids) >= len(full_ids):
            raise RuntimeError("training target truncated")
        sequences.append(full_ids)
        labels.append([-100] * len(prefix_ids) + full_ids[len(prefix_ids):])
    width = max(map(len, sequences)); pad = tokenizer.pad_token_id
    ids = torch.tensor([row + [pad] * (width - len(row)) for row in sequences],
                       device=device)
    mask = torch.tensor([[1] * len(row) + [0] * (width - len(row))
                         for row in sequences], device=device)
    target = torch.tensor([row + [-100] * (width - len(row)) for row in labels],
                          device=device)
    return ids, mask, target


def train(dataset: Path, pre_evaluation: Path, output: Path) -> dict:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    if output.exists():
        raise RuntimeError("training output already exists")
    config = json.loads(CONFIG_PATH.read_text())
    manifest, examples = load_dataset(dataset)
    pre = json.loads(pre_evaluation.read_text())
    if pre.get("phase") != "PRE_TRAINING" or \
            pre.get("dataset_manifest_sha256") != manifest["manifest_sha256"]:
        raise RuntimeError("frozen pre-training evaluation does not bind dataset")
    if file_hash(CONFIG_PATH) != manifest["payload"]["training_config_sha256"]:
        raise RuntimeError("training configuration changed after dataset freeze")
    training = [row for row in examples if row["split"] == "train"]
    validation = [row for row in examples if row["split"] == "validation"]
    evaluation_ids = {row["example_id"] for row in examples if row["split"] == "evaluation"}
    if evaluation_ids & {row["example_id"] for row in training + validation}:
        raise RuntimeError("held-out leakage")
    random.seed(config["seed"]); torch.manual_seed(config["seed"])
    torch.cuda.manual_seed_all(config["seed"])
    device = torch.device("cuda")
    tokenizer = AutoTokenizer.from_pretrained(_model_path(), local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(_model_path(), local_files_only=True,
                                                dtype=torch.bfloat16).to(device)
    modules, trainable = inject_lora(model, config)
    output.mkdir(parents=True)
    initial = output / "initial-adapter.safetensors"
    final = output / "trained-adapter.safetensors"
    save_adapter(model, initial)
    initial_hash = file_hash(initial)
    implementation_hash = file_hash(Path(__file__))
    atomic_json(output / "training-progress.json", dict(status="INITIALIZED",
        initial_adapter_sha256=initial_hash, optimizer_steps=0, epoch_metrics=[],
        training_implementation_sha256=implementation_hash))
    parameters = [parameter for parameter in model.parameters() if parameter.requires_grad]
    optimizer = torch.optim.AdamW(parameters, lr=config["learning_rate"],
        weight_decay=config["weight_decay"])

    def validation_loss():
        model.eval(); values = []
        with torch.no_grad():
            for start in range(0, len(validation), config["batch_size"]):
                ids, mask, labels = _batch(tokenizer,
                    validation[start:start + config["batch_size"]],
                    config["max_length"], device)
                values.append(float(model(input_ids=ids, attention_mask=mask,
                                          labels=labels).loss.item()))
        return sum(values) / len(values)

    before_validation = validation_loss()
    epoch_rows, optimizer_steps = [], 0
    for epoch in range(config["epochs"]):
        model.train(); order = list(range(len(training)))
        random.Random(config["seed"] + epoch).shuffle(order)
        optimizer.zero_grad(set_to_none=True); losses = []
        batches = math.ceil(len(order) / config["batch_size"])
        for batch_number, start in enumerate(range(0, len(order), config["batch_size"]), 1):
            rows = [training[index] for index in order[start:start + config["batch_size"]]]
            ids, mask, labels = _batch(tokenizer, rows, config["max_length"], device)
            loss = model(input_ids=ids, attention_mask=mask, labels=labels).loss
            losses.append(float(loss.item()))
            (loss / config["gradient_accumulation"]).backward()
            if batch_number % config["gradient_accumulation"] == 0 or batch_number == batches:
                torch.nn.utils.clip_grad_norm_(parameters, 1.0)
                optimizer.step(); optimizer.zero_grad(set_to_none=True); optimizer_steps += 1
        value = dict(epoch=epoch + 1, mean_training_loss=sum(losses) / len(losses),
                     validation_loss=validation_loss(), optimizer_steps=optimizer_steps)
        epoch_rows.append(value)
        atomic_json(output / "training-progress.json", dict(status="TRAINING",
            initial_adapter_sha256=initial_hash, optimizer_steps=optimizer_steps,
            epoch_metrics=epoch_rows,
            training_implementation_sha256=implementation_hash))
        print(value, flush=True)
    save_adapter(model, final)
    final_hash = file_hash(final)
    if initial_hash == final_hash:
        raise RuntimeError("adapter parameters did not change")
    adapter_config = dict(**config, format="horus-manual-lora-v1",
        injected_modules=modules, base_model_identity=BASE_MODEL_ID,
        base_weights_sha256=manifest["payload"]["base_weights_sha256"],
        trainable_parameters=trainable,
        total_base_parameters=sum(parameter.numel() for parameter in model.parameters()) - trainable)
    atomic_json(output / "adapter-config.json", adapter_config)
    lineage = dict(parent_model=BASE_MODEL_ID,
        base_weights_sha256=manifest["payload"]["base_weights_sha256"],
        authenticated_dataset_manifest_sha256=manifest["manifest_sha256"],
        examples_sha256=manifest["payload"]["examples_sha256"],
        training_config_sha256=file_hash(CONFIG_PATH),
        pre_evaluation_sha256=file_hash(pre_evaluation),
        initial_adapter_sha256=initial_hash, final_adapter_sha256=final_hash,
        initial_adapter_file=initial.name, final_adapter_file=final.name,
        training_examples=len(training), validation_examples=len(validation),
        held_out_examples_seen_by_optimizer=0, trainable_parameters=trainable,
        optimizer_steps=optimizer_steps, epoch_metrics=epoch_rows,
        validation_loss_before=before_validation,
        validation_loss_after=epoch_rows[-1]["validation_loss"],
        training_implementation_sha256=implementation_hash,
        fresh_training_process_pid=os.getpid())
    atomic_json(output / "learning-lineage.json", lineage)
    atomic_json(output / "training-progress.json", dict(status="COMPLETE",
        initial_adapter_sha256=initial_hash, final_adapter_sha256=final_hash,
        optimizer_steps=optimizer_steps, epoch_metrics=epoch_rows,
        training_implementation_sha256=implementation_hash))
    return lineage


def compare(pre_path: Path, post_path: Path, output: Path) -> dict:
    if output.exists():
        raise RuntimeError("comparison output already exists")
    pre, post = json.loads(pre_path.read_text()), json.loads(post_path.read_text())
    if pre["dataset_manifest_sha256"] != post["dataset_manifest_sha256"]:
        raise RuntimeError("evaluation dataset mismatch")
    old = {row["example_id"]: row for row in pre["results"]}
    new = {row["example_id"]: row for row in post["results"]}
    if set(old) != set(new):
        raise RuntimeError("evaluation identity mismatch")
    changes, categories = [], {name: 0 for name in
        ("wrong_to_correct", "correct_to_wrong", "unchanged_wrong", "unchanged_correct")}
    for identity in old:
        before, after = old[identity], new[identity]
        category = ("wrong_to_correct" if not before["correct"] and after["correct"] else
                    "correct_to_wrong" if before["correct"] and not after["correct"] else
                    "unchanged_correct" if before["correct"] else "unchanged_wrong")
        categories[category] += 1
        changes.append(dict(example_id=identity, target=before["target"],
            before=before["predicted"], after=after["predicted"], category=category,
            prediction_changed=before["predicted"] != after["predicted"]))
    result = dict(dataset_manifest_sha256=pre["dataset_manifest_sha256"],
        before=dict(accuracy=pre["accuracy"], by_target=pre["by_target"], invalid=pre["invalid"]),
        after=dict(accuracy=post["accuracy"], by_target=post["by_target"], invalid=post["invalid"]),
        categories=categories, changed_predictions=[row for row in changes if row["prediction_changed"]],
        all_examples=changes)
    atomic_json(output, result)
    return result


def compare_context(adapter: Path, output: Path, state: int = 1) -> dict:
    """Score one frozen pre-execution context; neither path can execute."""
    if output.exists():
        raise RuntimeError("context comparison output already exists")
    if state not in range(4):
        raise ValueError("state outside finite domain")
    base = QwenConsequenceClient(device="cuda")
    trained = QwenConsequenceClient(adapter_path=adapter, device="cuda")
    rows = []
    for action in ("ADVANCE", "HOLD", "RETREAT"):
        alias = next(key for key, value in MAPPING.items() if value == action)
        payload = dict(state=state, target_action=alias,
                       VERIFIED_CHRONOLOGICAL_HISTORY=[])
        request = dict(system=CONSEQUENCE_SYSTEM, prompt=canonical(payload))
        old = base.generate(request); new = trained.generate(request)
        old_value = parse(old["raw_output"], "C")["consequence"]
        new_value = parse(new["raw_output"], "C")["consequence"]
        rows.append(dict(action=action, alias=alias, request_sha256=digest(request),
            base_raw=old["raw_output"], base_consequence=old_value,
            trained_raw=new["raw_output"], trained_consequence=new_value,
            changed=old_value != new_value))
    def choice(key):
        forecasts = tuple(MapForecast(row["action"], row["alias"], 0, row[key],
            False, None, 0, {}) for row in rows)
        return MechanicalExplorer().choose(forecasts)
    base_choice, trained_choice = choice("base_consequence"), choice("trained_consequence")
    result = dict(status="FROZEN_PRE_EXECUTION_COMPARISON", state=state,
        authenticated_history=[], base_model=base.model_id, trained_model=trained.model_id,
        adapter_sha256=file_hash(adapter), forecasts=rows,
        base_choice=dict(action=base_choice.action, reason=base_choice.reason),
        trained_choice=dict(action=trained_choice.action, reason=trained_choice.reason),
        decision_changed=base_choice.action != trained_choice.action,
        executions=0, receipts=0, memory_publications=0)
    atomic_json(output, result)
    return result


def summarize_session(session: Path, output: Path) -> dict:
    """Create a public-safe summary after validating a private live session."""
    if output.exists():
        raise RuntimeError("session summary output already exists")
    with SessionStore(session, True) as store:
        events = store.records["events"]
        training = store.records["training"]
        if len(events) != len(training):
            raise RuntimeError("event/training stream length mismatch")
        steps = []
        for event_envelope, training_envelope in zip(events, training):
            event, trained = event_envelope["record"], training_envelope["record"]
            forecasts = []
            for action in ("ADVANCE", "HOLD", "RETREAT"):
                call_root = trained["decision_id"] + ":" + action
                joint = next(row for row in store.records["calls"]
                    if row["kind"] == "PARSED" and
                       row["record"].get("call_id") == call_root + ":J")
                consequence = next(row for row in store.records["calls"]
                    if row["kind"] == "PARSED" and
                       row["record"].get("call_id") == call_root + ":C")
                intent = next(row for row in store.records["calls"]
                    if row["kind"] == "REQUEST_INTENT" and
                       row["record"].get("call_id") == call_root + ":C")
                payload = json.loads(intent["record"]["request"]["prompt"])
                forecasts.append(MapForecast(action, payload["target_action"],
                    joint["record"]["parsed"]["next_state"],
                    consequence["record"]["parsed"]["consequence"],
                    False, None, len(payload["VERIFIED_CHRONOLOGICAL_HISTORY"]), {}))
            choice = MechanicalExplorer().choose(tuple(forecasts))
            if choice.action != trained["chosen_action"]:
                raise RuntimeError("recorded action differs from reconstructed Explorer")
            steps.append(dict(step=trained["order"], state=event["receipt"]["pre_state"],
                epoch=event["receipt"]["epoch"], transaction_id=event["receipt"]["transaction_id"],
                history_counts={row.action: row.history_count for row in forecasts},
                forecasts=[dict(action=row.action, next_state=row.next_state,
                                consequence=row.consequence) for row in forecasts],
                explorer=dict(action=choice.action, reason=choice.reason),
                receipt=event["receipt"], authorization=event["authorization_status"],
                prediction_match=trained["prediction_match"],
                input_context_hash=trained["input_context_hash"],
                consequence_request_sha256=trained["consequence_request_sha256"]))
        result = dict(status="VERIFIED", session_id=store.checkpoint["session_id"],
            consequence_model=next(row["record"]["request"]["model"]
                for row in store.records["calls"] if row["kind"] == "REQUEST_INTENT" and
                row["record"]["role"] == "independent-consequence"),
            actual_model_calls=sum(row["kind"] == "RESPONSE"
                                   for row in store.records["calls"]),
            authorized_steps=len(steps), stream_heads=store.checkpoint["streams"],
            steps=steps)
    atomic_json(output, result)
    return result
