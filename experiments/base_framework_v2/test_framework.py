"""Independent tests for the v2 evidence-package authority boundary."""

from __future__ import annotations

from pathlib import Path
import unittest

from experiments.base_framework_v1 import source_a, source_b
from experiments.base_framework_v1.hidden_oracle import TrueWorldOracle
from experiments.base_framework_v2 import witness_c
from experiments.base_framework_v2.campaign import clean_episode, execute_campaign, scenario
from experiments.base_framework_v2.framework import EvidenceProvenanceFramework
from experiments.base_framework_v2.registry import corrupted_registry, normal_registry
from experiments.base_framework_v2.types import RegisteredSourceEvidence


class RegistryTests(unittest.TestCase):
    def test_registry_is_fixed_and_immutable(self) -> None:
        registry = normal_registry()
        self.assertEqual(len(registry.nodes), 9)
        with self.assertRaises(TypeError):
            registry._by_id["X"] = registry.nodes[0]

    def test_declared_paths_distinguish_dependencies(self) -> None:
        registry = normal_registry()
        self.assertTrue(registry.declared_separate("OBSERVATION_PATH_A", "OBSERVATION_PATH_B"))
        self.assertFalse(registry.declared_separate("OBSERVATION_PATH_A", "DERIVED_B_REFERENCE"))
        self.assertFalse(registry.declared_separate("SHARED_PATH_A", "SHARED_PATH_B"))


class WitnessAndAuthorityTests(unittest.TestCase):
    def test_witness_c_covers_complete_world(self) -> None:
        system = EvidenceProvenanceFramework()
        for state in range(4):
            for action in ("ADVANCE", "HOLD", "RETREAT"):
                request = __import__("experiments.base_framework_v1.types", fromlist=["ObservationRequest"]).ObservationRequest(1, 1, state, action, 0)
                a = source_a.observe(request)
                c = witness_c.observe(request, system.registry.version)
                self.assertEqual(c.relation_code, witness_c.encode_relation(a.observed_next_state, a.observed_consequence))

    def test_runtime_does_not_import_hidden_oracle(self) -> None:
        directory = Path(__file__).resolve().parent
        runtime = "".join((directory / name).read_text() for name in ("framework.py", "registry.py", "witness_c.py", "types.py"))
        self.assertNotIn("hidden_oracle", runtime)
        self.assertNotIn("source_a", (directory / "witness_c.py").read_text())
        self.assertNotIn("source_b", (directory / "witness_c.py").read_text())

    def test_a_and_ab_cannot_commit_without_witness(self) -> None:
        system = EvidenceProvenanceFramework()
        oracle = TrueWorldOracle()
        pending = system.begin_step()
        event = oracle.execute(1, 1, pending.action)
        request = system.observation_request(event.pre_state)
        a = RegisteredSourceEvidence(source_a.observe(request), "OBSERVATION_PATH_A", "source_a", system.registry.version)
        b = RegisteredSourceEvidence(source_b.observe(request), "OBSERVATION_PATH_B", "source_b", system.registry.version)
        self.assertIsNone(system.stage("source_a", a))
        self.assertIsNone(system.stage("source_b", b))
        self.assertEqual(system.memory.records, [])
        self.assertEqual(system.map.current.state, 0)

    def test_transients_recover(self) -> None:
        for name in ("a_transient", "b_transient", "c_transient"):
            row, _ = scenario(name, 17)
            self.assertEqual(row["result_class"], "SUCCESSFUL_RECOVERY")
            self.assertEqual(row["rounds"], 2)

    def test_ab_common_mode_is_blocked_by_c(self) -> None:
        for name in ("ab_common_c_correct", "ab_common_c_different"):
            row, _ = scenario(name, 19)
            self.assertFalse(row["committed"])
            self.assertEqual(row["result_class"], "SAFE_REJECTION")

    def test_registered_derived_and_shared_paths_reject(self) -> None:
        for name in ("false_process_separation", "shared_ancestor", "candidate_witness"):
            row, _ = scenario(name, 23)
            self.assertFalse(row["committed"])

    def test_provenance_identity_and_duplicate_controls_reject(self) -> None:
        for name in ("stale_witness", "duplicate_witness", "spoof_process"):
            row, _ = scenario(name, 29)
            self.assertFalse(row["committed"])

    def test_all_three_common_corruption_exposes_trust_root(self) -> None:
        row, _ = scenario("abc_common", 31)
        self.assertTrue(row["committed"])
        self.assertTrue(row["external_false_accept"])

    def test_corrupt_registry_exposes_trust_root(self) -> None:
        row, _ = scenario("registry_corrupt", 37)
        self.assertTrue(row["committed"])
        self.assertTrue(row["external_false_accept"])


class ClosedLoopTests(unittest.TestCase):
    def test_clean_memory_changes_explorer_and_rotates_packages(self) -> None:
        row, system = clean_episode(41)
        self.assertEqual(row["state1_actions"][0], "ADVANCE")
        self.assertIn("HOLD", row["state1_actions"][1:])
        self.assertEqual((len(system.memory.records), len(system.pairs.decisions), len(system.packages)), (8, 8, 8))

    def test_complete_frozen_campaign(self) -> None:
        result = execute_campaign()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["totals"]["scenario_runs"], 57)
        self.assertEqual(result["totals"]["protected_false_accepts"], 0)
        self.assertEqual(result["totals"]["abc_common_mode_false_accepts"], 3)
        self.assertEqual(result["totals"]["registry_corruption_false_accepts"], 3)


if __name__ == "__main__":
    unittest.main()
