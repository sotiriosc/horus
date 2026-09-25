"""Finite-contract tests. Forced outputs are not language-model evidence."""

import json
from pathlib import Path
import unittest

from experiments.model_explorer_integration_v0.adapter import ForcedOutput, parse_action
from experiments.model_explorer_integration_v0.campaign import Episode, INJECTIONS, verify_frozen


class AdapterTests(unittest.TestCase):
    def test_exact_finite_parser(self):
        for action in ("ADVANCE", "HOLD", "RETREAT"):
            self.assertEqual(parse_action(" \n" + action + "\n"), (action, None))
        for raw in list(INJECTIONS.values()) + ["DELETE_STATE", "hold", "HOLD\x00", None]:
            self.assertIsNone(parse_action(raw)[0])

    def test_invalid_outputs_never_execute_or_mutate_history(self):
        for raw in INJECTIONS.values():
            rows = []
            episode = Episode(1, rows.append)
            row = episode.step("model", ForcedOutput(raw), 1)
            self.assertEqual(episode.world.execution_count, 0)
            self.assertFalse(row["authorization"]["committed"])
            self.assertEqual(row["violations"], [])

    def test_audit_precedes_model_input(self):
        rows = []
        episode = Episode(1, rows.append)
        episode.setup()
        row = episode.step("model", ForcedOutput("HOLD"), 1, fault="corrupt_memory")
        self.assertEqual(row["violations"], [])
        memory = json.loads(row["model_call"]["exact_prompt"])["memory"]
        self.assertTrue(any(r["action"] == "ADVANCE" and r["consequence"] == -1 for r in memory))
        self.assertTrue(all(-1 <= r["consequence"] <= 1 for r in memory))

    def test_framework_files_frozen(self):
        self.assertEqual(len(verify_frozen(Path(__file__).resolve().parents[2])["source_sha256"]), 23)


if __name__ == "__main__":
    unittest.main()
