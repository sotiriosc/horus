"""Independent tests for the v1 cross-source authority boundary."""

from __future__ import annotations

from pathlib import Path
import unittest

from experiments.base_framework_v1 import source_a, source_b
from experiments.base_framework_v1.campaign import (
    audit_commit,
    clean_episode,
    execute_campaign,
    independently_structural,
    scenario,
)
from experiments.base_framework_v1.framework import CrossSourceFramework, StepResult
from experiments.base_framework_v1.hidden_oracle import TrueWorldOracle
from experiments.base_framework_v1.types import ObservationRequest


class SourceSeparationTests(unittest.TestCase):
    def test_sources_and_oracle_agree_for_complete_world(self) -> None:
        for state in range(4):
            for transaction_id, action in enumerate(("ADVANCE", "HOLD", "RETREAT"), 1):
                oracle = TrueWorldOracle(state)
                event = oracle.execute(7, transaction_id, action)
                request = ObservationRequest(7, transaction_id, state, action, 0)
                a = source_a.observe(request)
                b = source_b.observe(request)
                self.assertTrue(independently_structural(a, b))
                self.assertEqual(
                    (a.observed_next_state, a.observed_consequence),
                    (event.next_state, event.consequence),
                )

    def test_runtime_and_sources_do_not_import_hidden_or_each_other(self) -> None:
        directory = Path(__file__).resolve().parent
        framework = (directory / "framework.py").read_text()
        a = (directory / "source_a.py").read_text()
        b = (directory / "source_b.py").read_text()
        self.assertNotIn("hidden_oracle", framework)
        self.assertNotIn("source_b", a)
        self.assertNotIn("source_a", b)
        self.assertNotIn("hidden_oracle", a + b)


class CrossSourceBoundaryTests(unittest.TestCase):
    def test_first_receipt_never_commits(self) -> None:
        system = CrossSourceFramework()
        oracle = TrueWorldOracle()
        pending = system.begin_step()
        self.assertNotIsInstance(pending, StepResult)
        event = oracle.execute(1, 1, pending.action)
        request = system.observation_request(event.pre_state)
        partial = system.submit_receipt("A", source_a.observe(request))
        self.assertFalse(partial.committed)
        self.assertFalse(partial.continued)
        self.assertEqual(system.memory.records, [])
        self.assertEqual(system.map.current.state, 0)

    def test_transient_fault_reobserves_once_and_recovers(self) -> None:
        row, system = scenario("a_transient", 17)
        self.assertEqual(row["result_class"], "SUCCESSFUL_RECOVERY")
        self.assertTrue(row["committed"])
        self.assertEqual(row["rounds"], 2)
        self.assertEqual(system.metrics["reobservations"], 1)

    def test_persistent_fault_stops_without_selecting_clean_source(self) -> None:
        row, system = scenario("a_persistent", 17)
        self.assertEqual(row["result_class"], "SAFE_REJECTION")
        self.assertFalse(row["committed"])
        self.assertFalse(row["continued"])
        self.assertEqual(system.metrics["persistent_disagreement_rejections"], 1)

    def test_duplicate_derived_and_shared_evidence_never_authorize(self) -> None:
        for name in ("duplicate_a", "derived_b", "shared_ancestor"):
            row, _ = scenario(name, 19)
            self.assertFalse(row["committed"], name)
        derived, _ = scenario("derived_b", 20)
        shared, _ = scenario("shared_ancestor", 20)
        self.assertTrue(derived["naive_agreement"])
        self.assertTrue(shared["naive_agreement"])
        self.assertFalse(derived["external_structural_final_pair"])
        self.assertFalse(shared["external_structural_final_pair"])

    def test_common_mode_failure_is_visible_only_to_hidden_oracle(self) -> None:
        row, system = scenario("common_mode", 29)
        self.assertEqual(row["result_class"], "OUT_OF_MODEL_COMMON_MODE_FAILURE")
        self.assertTrue(row["external_false_accept"])
        self.assertEqual(system.metrics["common_mode_pair_false_confidence"], 1)
        self.assertEqual(system.metrics["common_mode_false_accepts"], 1)

    def test_external_audit_catches_wrong_commit(self) -> None:
        system = CrossSourceFramework()
        oracle = TrueWorldOracle()
        pending = system.begin_step()
        event = oracle.execute(1, 1, pending.action)
        request = system.observation_request(event.pre_state)
        partial = system.submit_receipt("A", source_a.observe(request, "wrong"))
        self.assertFalse(partial.committed)
        result = system.submit_receipt(
            "B", source_b.observe(request, "wrong"), common_mode=True
        )
        self.assertTrue(result.committed)
        self.assertTrue(audit_commit(system, event, result))


class ClosedLoopTests(unittest.TestCase):
    def test_clean_memory_changes_explorer_and_rotates_pairs(self) -> None:
        row, system = clean_episode(31)
        self.assertEqual(row["state1_actions"][0], "ADVANCE")
        self.assertIn("HOLD", row["state1_actions"][1:])
        self.assertEqual(len(system.memory.records), 8)
        self.assertEqual(len(system.pairs.decisions), 8)
        self.assertEqual(system.memory.evictions, 4)

    def test_complete_frozen_campaign(self) -> None:
        result = execute_campaign()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["totals"]["scenario_runs"], 69)
        self.assertEqual(result["totals"]["protected_false_accepts"], 0)
        self.assertEqual(result["totals"]["externally_observed_false_rejects"], 0)
        self.assertEqual(result["totals"]["duplicate_authorizations"], 0)
        self.assertEqual(result["totals"]["common_mode_false_accepts"], 3)


if __name__ == "__main__":
    unittest.main()
