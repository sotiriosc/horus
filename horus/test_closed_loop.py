"""Acceptance tests for the runnable Horus v0 composition."""
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from experiments.cross_episode_initialization_boundary_v1.boundary import (
    EpisodeController, EpisodePlan, EpisodeWorld)
from experiments.realized_event_grounding_v0.framework import evidence
from experiments.map_guided_explorer_interface_v0.interface import AuthenticatedReader
from .core import (CheckpointAuthority, ConsequenceInput, HorusRuntime,
    MechanicalExplorer, SplitMapV0, run_demo)


class FixedConsequence:
    def predict(self, value):
        return 1 if value.action == "HOLD" else 0


class InvalidConsequence:
    def predict(self, value):
        return None if value.action == "HOLD" else 0


class SpyConsequence:
    def __init__(self): self.seen = []
    def predict(self, value):
        self.seen.append(value)
        assert isinstance(value, ConsequenceInput)
        assert not hasattr(value, "predicted_next_state")
        return 0


class FixedNextState:
    def predict(self, value): return 3


class FixedNegativeConsequence:
    def predict(self, value): return -1


class AlternatingHoldWorld(EpisodeWorld):
    def __init__(self, initial_state):
        super().__init__(initial_state)
        self.holds = 0

    def execute(self, epoch, transaction_id, action):
        actual = super().execute(epoch, transaction_id, action)
        if action == "HOLD":
            self.holds += 1
            actual = replace(actual, consequence=1 if self.holds == 1 else -1)
            self.fixture.last_actual = actual
        return actual


class AlternatingController(EpisodeController):
    def _make_world(self, initial_state):
        return AlternatingHoldWorld(initial_state)


class ClosedLoopTests(unittest.TestCase):
    def test_proposal_cannot_manufacture_receipt_and_only_root_enters_memory(self):
        controller = EpisodeController("HORUS_V0_FORGERY", EpisodePlan(initial_state=1))
        controller.begin_step("HOLD")
        receipt = controller.execute_pending()
        forged = replace(receipt)
        before = list(controller._active.framework.inner.memory.records)
        rejected = controller.submit_package(evidence(forged))
        self.assertFalse(rejected.committed)
        self.assertEqual(before, controller._active.framework.inner.memory.records)
        controller.release(receipt)

        valid = EpisodeController("HORUS_V0_VALID", EpisodePlan(initial_state=1))
        valid.begin_step("HOLD")
        original = valid.execute_pending()
        accepted = valid.submit_package(evidence(original))
        self.assertTrue(accepted.committed)
        self.assertIs(valid._active.framework.packages[-1].receipt, original)
        self.assertEqual(valid._active.framework.inner.memory.records[-1].consequence,
                         original.realized_consequence)
        valid.release(original)

    def test_experience_changes_later_behavior_and_survives_runtime_restart(self):
        runtime = HorusRuntime()
        first = runtime.step(1)
        self.assertEqual(first["explorer"]["action"], "ADVANCE")
        with TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.json"
            authority = CheckpointAuthority(b"test-key")
            authority.save(runtime, path)
            resumed = authority.resume(path)
            resumed.start_episode(1002, 1)
            second = resumed.step(2)
        self.assertEqual(second["explorer"]["action"], "HOLD")
        self.assertEqual(second["memory_used"]["ADVANCE"][0]["consequence"], -1)
        self.assertEqual(len(second["before"]["protected"]["memory"]), 1)

    def test_later_prediction_projection_contains_authorized_earlier_experience(self):
        runtime = HorusRuntime()
        first = runtime.step(1)
        runtime.start_episode(1002, 1)
        capture = AuthenticatedReader(runtime.controller, runtime.authentic,
            runtime.executions).capture({"K1": "ADVANCE", "K2": "HOLD", "K3": "RETREAT"})
        history = capture["map_inputs"]["ADVANCE"]["VERIFIED_CHRONOLOGICAL_HISTORY"]
        self.assertEqual(history, [{"epoch": 1001, "transaction_id": 1,
            "surface_action": "K1", "next_state": 2, "consequence": -1}])
        self.assertEqual(first["receipt"]["event_id"], 1)
        self.assertIs(runtime.controller._active.framework.packages[0].receipt,
                      runtime.authentic[tuple(first["training_record"]["receipt_identity"])])

    def test_checkpoint_tamper_is_rejected(self):
        runtime = HorusRuntime()
        runtime.step(1)
        with TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.json"
            authority = CheckpointAuthority(b"test-key")
            authority.save(runtime, path)
            document = json.loads(path.read_text())
            document["payload"]["steps"] = 99
            path.write_text(json.dumps(document))
            with self.assertRaisesRegex(ValueError, "authentication failed"):
                authority.resume(path)

    def test_contradictory_authenticated_experiences_coexist(self):
        controller = AlternatingController("HORUS_V0_CONTRADICTION",
            EpisodePlan(initial_state=1))
        runtime = HorusRuntime(controller,
            split_map=SplitMapV0(consequence=FixedConsequence()))
        first = runtime.step(1)
        second = runtime.step(1)
        self.assertEqual(first["explorer"]["action"], "HOLD")
        self.assertEqual(second["explorer"]["action"], "HOLD")
        records = controller._active.framework.inner.memory.records
        self.assertEqual([record.consequence for record in records], [1, -1])
        self.assertNotEqual((records[0].epoch, records[0].transaction_id),
                            (records[1].epoch, records[1].transaction_id))

    def test_explorer_and_reconciliation_are_mechanical(self):
        runtime = HorusRuntime(split_map=SplitMapV0(consequence=FixedConsequence()))
        reader = runtime.controller.projections
        capture = AuthenticatedReader(runtime.controller, runtime.authentic,
            runtime.executions).capture(
                {"K1": "ADVANCE", "K2": "HOLD", "K3": "RETREAT"})
        forecasts = runtime.split_map.forecasts(capture)
        choice = MechanicalExplorer().choose(forecasts)
        self.assertEqual(choice.action, "HOLD")
        selected = next(row for row in forecasts if row.action == "HOLD")
        self.assertEqual(selected.next_state, 1)
        self.assertEqual(selected.consequence, 1)
        self.assertFalse(selected.abstained)
        self.assertTrue(callable(reader))

    def test_reconciliation_copies_exact_component_values(self):
        runtime = HorusRuntime(split_map=SplitMapV0(
            next_state=FixedNextState(), consequence=FixedNegativeConsequence()))
        capture = AuthenticatedReader(runtime.controller, runtime.authentic,
            runtime.executions).capture(
                {"K1": "ADVANCE", "K2": "HOLD", "K3": "RETREAT"})
        forecast = runtime.split_map.forecast(capture, "HOLD")
        self.assertEqual((forecast.next_state, forecast.consequence), (3, -1))
        self.assertFalse(forecast.abstained)

    def test_consequence_boundary_never_receives_predicted_next_state(self):
        spy = SpyConsequence()
        runtime = HorusRuntime(split_map=SplitMapV0(consequence=spy))
        capture = AuthenticatedReader(runtime.controller, runtime.authentic,
            runtime.executions).capture(
                {"K1": "ADVANCE", "K2": "HOLD", "K3": "RETREAT"})
        runtime.split_map.forecasts(capture)
        self.assertEqual(len(spy.seen), 3)

    def test_invalid_component_abstains_without_execution(self):
        runtime = HorusRuntime(split_map=SplitMapV0(consequence=InvalidConsequence()))
        before = runtime.controller.snapshot()
        row = runtime.step(1)
        self.assertEqual(row["status"], "ABSTAINED")
        self.assertTrue(row["explorer"]["abstained"])
        self.assertEqual(before, runtime.controller.snapshot())

    def test_demo_artifact_and_training_records(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "run.json"
            artifact = run_demo(path)
            saved = json.loads(path.read_text())
        self.assertTrue(artifact["experience_changed_later_behavior"])
        self.assertEqual(saved, json.loads(json.dumps(artifact)))
        self.assertEqual(len(artifact["training_records"]), 2)
        required = {"input_context", "chosen_action", "predicted_next_state",
            "predicted_consequence", "realized_next_state", "realized_consequence",
            "receipt_identity", "authorization_status", "memory_identity",
            "memory_reference"}
        self.assertEqual(set(artifact["training_records"][0]), required)

    def test_demo_does_not_modify_historical_experiments(self):
        root = Path(__file__).resolve().parents[1]
        files = sorted(path for path in (root / "experiments").rglob("*") if path.is_file())
        before = {str(path.relative_to(root)): sha256(path.read_bytes()).hexdigest()
                  for path in files}
        with TemporaryDirectory() as directory:
            run_demo(Path(directory) / "run.json")
        after = {str(path.relative_to(root)): sha256(path.read_bytes()).hexdigest()
                 for path in files}
        self.assertEqual(before, after)

    def test_module_entrypoint_completes(self):
        root = Path(__file__).resolve().parents[1]
        with TemporaryDirectory() as directory:
            path = Path(directory) / "run.json"
            completed = subprocess.run(
                (sys.executable, "-m", "horus.run", "--output", str(path)),
                cwd=root, text=True, capture_output=True, check=True)
            artifact = json.loads(path.read_text())
        self.assertIn("Grounded behavior change: ADVANCE -> HOLD", completed.stdout)
        self.assertTrue(artifact["experience_changed_later_behavior"])


if __name__ == "__main__":
    unittest.main()
