"""Integrity checks for the bounded v0.2 grounded-learning path."""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from experiments.base_framework_v0.framework import MapModel

from .grounded_learning import _build_example, file_hash
from .live import CONSEQUENCE_SYSTEM, JOINT_SYSTEM, SessionStore, run_live


ALIASES = {"K1": "ADVANCE", "K2": "HOLD", "K3": "RETREAT"}


class JointClient:
    model_id = "test-joint"

    def __init__(self):
        self.requests = 0

    def generate(self, request):
        self.requests += 1
        self.assert_role(request)
        payload = json.loads(request["prompt"])
        action = ALIASES[payload["target_action"]]
        prediction = MapModel.predict_from(payload["state"], action, 1, 1)
        return {"raw_output": json.dumps({
                    "next_state": prediction.next_state,
                    "consequence": prediction.consequence,
                }),
                "transport_error": None, "response_metadata": {}}

    @staticmethod
    def assert_role(request):
        if request["system"] != JOINT_SYSTEM:
            raise AssertionError("joint client received another role")


class AlwaysPositiveConsequenceClient:
    model_id = "test-consequence"

    def __init__(self):
        self.requests = 0

    def generate(self, request):
        self.requests += 1
        if request["system"] != CONSEQUENCE_SYSTEM:
            raise AssertionError("consequence client received another role")
        return {"raw_output": '{"consequence":1}',
                "transport_error": None, "response_metadata": {}}


class GroundedLearningTests(unittest.TestCase):
    def _one_step_store(self, directory):
        session = Path(directory) / "session"
        run_live(session, 1, False, JointClient(),
                 AlwaysPositiveConsequenceClient())
        return session

    def test_label_comes_from_authorized_receipt_not_prediction(self):
        with TemporaryDirectory() as directory:
            session = self._one_step_store(directory)
            with SessionStore(session, True) as store:
                example = _build_example(store, "session",
                                         store.records["events"][0],
                                         store.records["training"][0])
                self.assertEqual(example["prediction_before_execution"],
                                 {"consequence": 1})
                self.assertEqual(example["target"], -1)
                self.assertEqual(example["target_json"], '{"consequence":-1}')

    def test_builder_rejects_prediction_not_completed_before_receipt(self):
        with TemporaryDirectory() as directory:
            session = self._one_step_store(directory)
            with SessionStore(session, True) as store:
                event = store.records["events"][0]
                call_id = (store.records["training"][0]["record"]["decision_id"] +
                           ":ADVANCE:C")
                parsed = next(row for row in store.records["calls"]
                              if row["kind"] == "PARSED" and
                              row["record"]["call_id"] == call_id)
                parsed["record"]["recorded_at"] = event["record"]["recorded_at"]
                with self.assertRaisesRegex(RuntimeError,
                                            "durably complete before receipt"):
                    _build_example(store, "session", event,
                                   store.records["training"][0])

    def test_checked_in_adapter_lineage_proves_parameter_update(self):
        root = Path(__file__).resolve().parents[1]
        model = root / "models/horus_consequence_v0_2"
        lineage = json.loads((model / "learning-lineage.json").read_text())
        initial = file_hash(model / "initial-adapter.safetensors")
        final = file_hash(model / "trained-adapter.safetensors")
        self.assertEqual(initial, lineage["initial_adapter_sha256"])
        self.assertEqual(final, lineage["final_adapter_sha256"])
        self.assertNotEqual(initial, final)
        self.assertEqual(lineage["held_out_examples_seen_by_optimizer"], 0)
        self.assertGreater(lineage["optimizer_steps"], 0)


if __name__ == "__main__":
    unittest.main()
