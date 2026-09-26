"""Regime, evaluation-bank, and historical-retention acceptance tests."""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from experiments.base_framework_v0.framework import MapModel

from .live import CONSEQUENCE_SYSTEM, JOINT_SYSTEM, SessionStore, run_live
from .stability_cycle import (initialize_stability_registry, load_evaluation_bank,
    stability_decision, _select_rehearsal)


ALIASES = {"K1": "ADVANCE", "K2": "HOLD", "K3": "RETREAT"}


class DeterministicClient:
    model_id = "deterministic"

    def __init__(self):
        self.requests = 0

    def generate(self, request):
        self.requests += 1
        payload = json.loads(request["prompt"])
        action = ALIASES[payload["target_action"]]
        prediction = MapModel.predict_from(payload["state"], action, 1, 1)
        if request["system"] == JOINT_SYSTEM:
            raw = json.dumps({"next_state": prediction.next_state,
                              "consequence": prediction.consequence})
        elif request["system"] == CONSEQUENCE_SYSTEM:
            raw = json.dumps({"consequence": prediction.consequence})
        else:
            raise AssertionError("unexpected role")
        return {"raw_output": raw, "transport_error": None,
                "response_metadata": {}}


def evaluation(correct, n, by_target, forgetting=0):
    return dict(incumbent=dict(correct=correct[0], examples=n,
            accuracy=correct[0] / n, invalid=0, by_target=by_target[0]),
        candidate=dict(correct=correct[1], examples=n,
            accuracy=correct[1] / n, invalid=0, by_target=by_target[1]),
        transitions={"correct_to_wrong": forgetting})


def classes(a, b, n=(4, 8, 4)):
    def side(values):
        return {str(target): {"n": count, "correct": value,
            "accuracy": value / count} for target, count, value in
            zip((-1, 0, 1), n, values)}
    return side(a), side(b)


class StabilityTests(unittest.TestCase):
    def test_hidden_regime_shift_and_restart_preserve_both_histories(self):
        with TemporaryDirectory() as directory:
            session = Path(directory) / "bridge"
            first = run_live(session, 3, False, DeterministicClient(),
                             regime_version="A")
            second = run_live(session, 2, True, DeterministicClient(),
                              regime_version="B", allow_regime_transition=True)
            self.assertNotEqual(first["steps"][-1]["receipt"]["source_identity"],
                                second["steps"][0]["receipt"]["source_identity"])
            with SessionStore(session, True) as store:
                events = [row["record"] for row in store.records["events"]]
                self.assertEqual([row["external_regime_version"] for row in events],
                                 ["A", "A", "A", "B", "B"])
                self.assertTrue(all(not row["regime_model_visible"] for row in events))
                prompts = [row["record"]["request"]["prompt"]
                           for row in store.records["calls"]
                           if row["kind"] == "REQUEST_INTENT" and
                           row["record"].get("role") == "independent-consequence"]
                self.assertTrue(all("regime" not in prompt.lower() for prompt in prompts))
                self.assertTrue(any(any(item["epoch"] == first["epoch"] for item in
                    json.loads(prompt)["VERIFIED_CHRONOLOGICAL_HISTORY"])
                    for prompt in prompts))
                self.assertEqual([x["version"] for x in
                                  store.checkpoint["regime_history"]], ["A", "B"])

    def test_unapproved_regime_change_fails_closed(self):
        with TemporaryDirectory() as directory:
            session = Path(directory) / "session"
            run_live(session, 1, False, DeterministicClient(), regime_version="A")
            with self.assertRaisesRegex(RuntimeError, "not explicitly authorized"):
                run_live(session, 1, True, DeterministicClient(), regime_version="B")

    def test_initial_bank_uses_only_prior_heldout_examples(self):
        with TemporaryDirectory() as directory:
            root = Path(directory) / "registry"
            result = initialize_stability_registry(root)
            manifest, rows = load_evaluation_bank(root)
            self.assertEqual(result["active_generation"], 2)
            self.assertEqual(manifest["payload"]["example_count"], 24)
            self.assertEqual(manifest["payload"]["batch_distribution"],
                {"v0.2-grounded-learning": 12, "v0.3-learning-cycle": 12})
            self.assertEqual(manifest["payload"]["model_visible_regime_examples"], 0)
            self.assertTrue(all(row["source_split"] == "evaluation" for row in rows))
            exclusions = json.loads((root / "evaluation-bank/exclusions.json").read_text())
            self.assertTrue(all(row["source_split"] != "evaluation"
                                for row in exclusions["rows"]))

    def test_bank_tampering_is_rejected(self):
        with TemporaryDirectory() as directory:
            root = Path(directory) / "registry"
            initialize_stability_registry(root)
            _, rows = load_evaluation_bank(root)
            pointer = json.loads((root / "evaluation-bank/current.json").read_text())
            path = root / pointer["payload"]["manifest"]
            examples = path.parent / "examples.jsonl"
            examples.write_text(examples.read_text() + json.dumps(rows[0]) + "\n")
            with self.assertRaisesRegex(RuntimeError, "examples hash mismatch"):
                load_evaluation_bank(root)

    def test_stability_rule_accepts_adaptation_with_retention(self):
        fresh = evaluation((6, 8), 12, classes((2, 3, 1), (3, 4, 1), (4, 4, 4)))
        historical = evaluation((20, 19), 24,
            classes((5, 9, 6), (5, 8, 6), (6, 10, 8)), forgetting=1)
        combined = evaluation((26, 27), 36,
            classes((7, 12, 7), (8, 12, 7), (10, 16, 10)))
        self.assertEqual(stability_decision(fresh, historical, combined)["decision"],
                         "ACTIVE")

    def test_stability_rule_rejects_forgetting_and_enables_one_rehearsal(self):
        fresh = evaluation((6, 10), 12, classes((2, 3, 1), (4, 5, 1), (4, 4, 4)))
        historical = evaluation((20, 14), 24,
            classes((5, 9, 6), (2, 7, 5), (6, 10, 8)), forgetting=6)
        combined = evaluation((26, 24), 36,
            classes((7, 12, 7), (6, 12, 6), (10, 16, 10)))
        result = stability_decision(fresh, historical, combined)
        self.assertEqual(result["decision"], "REJECTED")
        self.assertTrue(result["forgetting_failure"])

    def test_rehearsal_uses_twelve_old_training_examples_outside_bank(self):
        with TemporaryDirectory() as directory:
            root = Path(directory) / "registry"
            initialize_stability_registry(root)
            selection_path = Path(directory) / "selection.json"
            rehearsal = _select_rehearsal(root, selection_path)
            _, bank = load_evaluation_bank(root)
            self.assertEqual(len(rehearsal), 12)
            self.assertFalse({row["example_id"] for row in rehearsal} &
                             {row["example_id"] for row in bank})
            self.assertTrue(all(row["split"] == "train" for row in rehearsal))


if __name__ == "__main__":
    unittest.main()
