"""Safety tests for the consequence-model generation lifecycle."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from .core import digest
from .grounded_learning import BASE_MODEL_ID, file_hash
from .learning_cycle import promotion_decision, validate_optimizer_separation
from .model_registry import (RegistryError, _write_active, _write_state,
    active_model_spec, finalize_generation, initialize_registry, load_registry)


def score(correct, accuracy, by_target, invalid=0, examples=12):
    return dict(correct=correct, accuracy=accuracy, by_target=by_target,
                invalid=invalid, examples=examples)


BY_GOOD = {"-1": {"n": 4, "correct": 3, "accuracy": .75},
           "0": {"n": 2, "correct": 1, "accuracy": .5},
           "1": {"n": 6, "correct": 5, "accuracy": 5/6}}
BY_OLD = {"-1": {"n": 4, "correct": 2, "accuracy": .5},
          "0": {"n": 2, "correct": 1, "accuracy": .5},
          "1": {"n": 6, "correct": 4, "accuracy": 2/3}}


class LearningCycleTests(unittest.TestCase):
    def test_promotion_rule_accepts_net_grounded_improvement(self):
        before = score(7, 7/12, BY_OLD)
        after = score(9, 9/12, BY_GOOD)
        comparison = {"categories": {"wrong_to_correct": 3,
                                      "correct_to_wrong": 1}}
        self.assertEqual(promotion_decision(before, after, comparison)["decision"],
                         "ACTIVE")

    def test_promotion_rule_rejects_worse_candidate(self):
        before = score(9, 9/12, BY_GOOD)
        after = score(7, 7/12, BY_OLD)
        comparison = {"categories": {"wrong_to_correct": 1,
                                      "correct_to_wrong": 3}}
        self.assertEqual(promotion_decision(before, after, comparison)["decision"],
                         "REJECTED")

    def _registry(self, directory):
        root = Path(directory) / "registry"
        initialize_registry(root)
        return root

    def _candidate(self, root, generation=2, parent=1):
        folder = root / f"generations/generation-{generation:04d}"
        folder.mkdir(parents=True, exist_ok=True)
        adapter = folder / "trained-adapter.safetensors"
        adapter.write_bytes(b"synthetic-adapter-" + str(generation).encode())
        return dict(generation=generation, parent_generation=parent,
            base_model_identity=BASE_MODEL_ID,
            adapter_path=str(adapter.relative_to(root)),
            adapter_sha256=file_hash(adapter), artifact_kind="LORA_ADAPTER",
            dataset_manifest_sha256="dataset", grounded_training_examples=42,
            training_configuration={"synthetic": True},
            training_strategy="continue-active", creation_timestamp="test",
            evaluation_artifact=None, evaluation_sha256=None,
            lineage_artifact=None, lineage_sha256=None, dataset_path=None,
            example_usage_artifact=None, example_usage_sha256=None,
            evaluation_summary=None)

    def test_atomic_promotion_loads_new_generation(self):
        with TemporaryDirectory() as directory:
            root = self._registry(directory)
            result = finalize_generation(root, self._candidate(root), "ACTIVE", "pass")
            self.assertEqual(result["active_generation"], 2)
            self.assertEqual(active_model_spec(root)["generation"], 2)
            self.assertEqual([x["status"] for x in load_registry(root)["entries"]],
                             ["RETIRED", "RETIRED", "ACTIVE"])

    def test_rejection_keeps_incumbent_active(self):
        with TemporaryDirectory() as directory:
            root = self._registry(directory)
            result = finalize_generation(root, self._candidate(root),
                                         "REJECTED", "worse")
            self.assertEqual(result["active_generation"], 1)
            self.assertEqual(active_model_spec(root)["generation"], 1)

    def test_broken_adapter_hash_fails_closed(self):
        with TemporaryDirectory() as directory:
            root = self._registry(directory)
            spec = active_model_spec(root)
            Path(spec["adapter_path"]).write_bytes(b"tampered")
            with self.assertRaisesRegex(RegistryError, "adapter hash mismatch"):
                load_registry(root)

    def test_tampered_registry_state_fails_closed(self):
        with TemporaryDirectory() as directory:
            root = self._registry(directory)
            active = json.loads((root / "active-model.json").read_text())
            state = root / active["payload"]["registry_state_file"]
            document = json.loads(state.read_text())
            document["payload"]["generations"][0]["reason"] = "tampered"
            state.write_text(json.dumps(document))
            with self.assertRaisesRegex(RegistryError, "state hash mismatch"):
                load_registry(root)

    def test_duplicate_generation_is_rejected(self):
        with TemporaryDirectory() as directory:
            root = self._registry(directory)
            registry = load_registry(root)
            entries = deepcopy(registry["entries"])
            entries.append(deepcopy(entries[-1]))
            relative, state = _write_state(root, entries)
            _write_active(root, relative, state, entries[-1])
            with self.assertRaisesRegex(RegistryError, "duplicate generation"):
                load_registry(root)

    def test_missing_or_wrong_parent_is_rejected(self):
        with TemporaryDirectory() as directory:
            root = self._registry(directory)
            with self.assertRaisesRegex(RegistryError, "parent is not the incumbent"):
                finalize_generation(root, self._candidate(root, parent=99),
                                    "REJECTED", "bad parent")

    def test_candidate_crash_and_evaluation_interruption_preserve_incumbent(self):
        for reason in ("candidate training crash", "evaluation interruption"):
            with self.subTest(reason=reason), TemporaryDirectory() as directory:
                root = self._registry(directory)
                failed = self._candidate(root)
                failed["adapter_path"] = None
                failed["adapter_sha256"] = digest({"failure": reason})
                failed["artifact_kind"] = "FAILED_CANDIDATE_ATTEMPT"
                result = finalize_generation(root, failed, "REJECTED", reason)
                self.assertEqual(result["active_generation"], 1)
                self.assertEqual(active_model_spec(root)["generation"], 1)

    def test_evaluation_leakage_is_rejected(self):
        row = {"example_id": "same"}
        with self.assertRaisesRegex(RuntimeError, "evaluation leakage"):
            validate_optimizer_separation([
                {**row, "split": "train"}, {**row, "split": "evaluation"}])

    def test_active_reference_corruption_fails_closed(self):
        with TemporaryDirectory() as directory:
            root = self._registry(directory)
            document = json.loads((root / "active-model.json").read_text())
            document["payload"]["generation"] = 0
            (root / "active-model.json").write_text(json.dumps(document))
            with self.assertRaisesRegex(RegistryError, "active model hash mismatch"):
                load_registry(root)

    def test_runtime_resolution_returns_exact_active_generation(self):
        with TemporaryDirectory() as directory:
            root = self._registry(directory)
            spec = active_model_spec(root)
            self.assertEqual(spec["generation"], 1)
            self.assertEqual(file_hash(Path(spec["adapter_path"])),
                             spec["artifact_sha256"])


if __name__ == "__main__":
    unittest.main()
