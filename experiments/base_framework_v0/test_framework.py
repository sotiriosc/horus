"""Independent checks for the bounded base framework v0."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import unittest

from experiments.base_framework_v0.campaign import checked_clean, execute_campaign
from experiments.base_framework_v0.environment import BoundedWorld
from experiments.base_framework_v0.framework import (
    BaseFramework,
    CANDIDATE_DERIVED,
    MapModel,
    StateAuthorizer,
    StateCandidate,
    descendant_checker,
)


class GroundAndModelTests(unittest.TestCase):
    def test_environment_and_map_agree_for_complete_finite_space(self) -> None:
        for state in range(4):
            for transaction_id, action in enumerate(
                ("ADVANCE", "HOLD", "RETREAT"), start=1
            ):
                world = BoundedWorld(state)
                receipt = world.step(action, epoch=7, transaction_id=transaction_id)
                prediction = MapModel.predict_from(
                    state, action, epoch=7, transaction_id=transaction_id
                )
                self.assertEqual(
                    (prediction.next_state, prediction.consequence),
                    (receipt.next_state, receipt.consequence),
                )

    def test_environment_and_framework_do_not_import_each_other(self) -> None:
        directory = Path(__file__).resolve().parent
        environment_source = (directory / "environment.py").read_text()
        framework_source = (directory / "framework.py").read_text()
        self.assertNotIn("base_framework_v0.framework", environment_source)
        self.assertNotIn("base_framework_v0.environment", framework_source)


class AuthorityBoundaryTests(unittest.TestCase):
    def test_invalid_explorer_proposal_cannot_execute(self) -> None:
        world = BoundedWorld()
        system = BaseFramework(world)
        result = system.run_step({"forced_action": "JUMP"})
        self.assertFalse(result.executed)
        self.assertFalse(result.committed)
        self.assertFalse(result.continued)
        self.assertEqual(world.execution_count, 0)
        self.assertEqual(system.memory.records, [])

    def test_wrong_measure_and_wrong_recovery_stop_after_execution(self) -> None:
        world = BoundedWorld()
        system = BaseFramework(world)
        result = system.run_step(
            {"wrong_measure": True, "wrong_measure_recovery": True}
        )
        self.assertTrue(result.executed)
        self.assertFalse(result.committed)
        self.assertFalse(result.continued)
        self.assertEqual(world.execution_count, 1)
        self.assertEqual(system.memory.records, [])
        self.assertEqual(system.map.current.state, 0)

    def test_wrong_transaction_cannot_authorize_original_candidate(self) -> None:
        world = BoundedWorld()
        system = BaseFramework(world, epoch=11)
        result = system.run_step({"candidate_transaction": 99})
        self.assertTrue(result.committed)
        self.assertTrue(result.recovery_authorized)
        self.assertEqual(system.metrics["provenance_rejections"], 1)
        self.assertNotIn(
            99, {key[1] for key in system.state_authorizer.authorized_keys}
        )

    def test_shared_descendant_agreement_is_not_authority(self) -> None:
        world = BoundedWorld()
        system = BaseFramework(world)
        result = system.run_step({"shared_descendant": True})
        self.assertTrue(result.executed)
        self.assertFalse(result.committed)
        self.assertEqual(system.metrics["descendant_false_confidence"], 1)
        self.assertEqual(system.metrics["lineage_rejections"], 1)

        receipt = world.snapshot(1, 2)
        candidate = StateCandidate(
            1, 2, receipt.observation_id, receipt.source_identity, world.state
        )
        correlated = replace(candidate, lineage="SHARED_ANCESTOR")
        self.assertTrue(descendant_checker(candidate, candidate))
        self.assertFalse(
            StateAuthorizer().authorize(
                replace(candidate, lineage=CANDIDATE_DERIVED),
                correlated,
                world.state,
                "test",
            )
        )


class ClosedLoopTests(unittest.TestCase):
    def test_memory_changes_behavior_and_rotation_preserves_identity(self) -> None:
        row, system = checked_clean(seed=23)
        self.assertTrue(row["memory_changed_future_behavior"])
        self.assertEqual(row["state1_actions"][0], "ADVANCE")
        self.assertIn("HOLD", row["state1_actions"][1:])
        self.assertEqual(len(system.memory.records), 8)
        self.assertEqual(len(system.evidence.receipts), 8)
        self.assertEqual(system.memory.evictions, 4)

    def test_corrupt_memory_is_repaired_before_it_drives_explorer(self) -> None:
        world = BoundedWorld()
        system = BaseFramework(world)
        for _ in range(5):
            self.assertTrue(system.run_step().committed)
        system.memory.corrupt_consequence(2)
        result = system.run_step()
        self.assertEqual(result.action, "HOLD")
        self.assertTrue(result.committed)
        self.assertEqual(system.metrics["memory_corruptions_detected"], 1)
        self.assertEqual(system.memory.quarantine, [])

    def test_valid_incumbent_survives_bad_candidate(self) -> None:
        world = BoundedWorld(initial_state=1)
        system = BaseFramework(world)
        result = system.run_step({"forced_action": "HOLD", "candidate_value": 2})
        self.assertTrue(result.committed)
        self.assertTrue(result.incumbent_retained)
        self.assertEqual(system.map.current.state, 1)

    def test_invalid_incumbent_and_failed_recovery_cannot_continue(self) -> None:
        world = BoundedWorld()
        system = BaseFramework(world)
        system.map.current.state = 3
        result = system.run_step({"failed_recovery": True})
        self.assertFalse(result.executed)
        self.assertFalse(result.committed)
        self.assertFalse(result.continued)
        self.assertFalse(system.map.current.valid)

    def test_complete_predeclared_campaign(self) -> None:
        result = execute_campaign()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["totals"]["scenario_runs"], 42)
        self.assertEqual(result["totals"]["protected_false_accepts"], 0)
        self.assertEqual(result["totals"]["false_rejects"], 0)
        self.assertEqual(result["totals"]["duplicate_authorizations"], 0)


if __name__ == "__main__":
    unittest.main()
