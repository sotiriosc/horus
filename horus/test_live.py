"""Safety and restart acceptance tests for Horus v0.1 live mode."""
from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from experiments.base_framework_v0.framework import MapModel
from experiments.realized_event_grounding_v0.framework import evidence

from .live import (CONSEQUENCE_SYSTEM, JOINT_SYSTEM, LiveRuntime, ModelClient,
                   SessionError, SessionStore, run_live)


ALIASES = {"K1": "ADVANCE", "K2": "HOLD", "K3": "RETREAT"}


class DeterministicModel(ModelClient):
    def __init__(self, invalid=False):
        self.requests = 0
        self.invalid = invalid
        self.calls = []

    def generate(self, request_body):
        self.requests += 1
        self.calls.append(json.loads(json.dumps(request_body)))
        payload = json.loads(request_body["prompt"])
        action = ALIASES[payload["target_action"]]
        predicted = MapModel.predict_from(payload["state"], action, 1, 1)
        if self.invalid:
            raw = "not-json"
        elif request_body["system"] == JOINT_SYSTEM:
            raw = json.dumps({"next_state": predicted.next_state,
                              "consequence": predicted.consequence})
        elif request_body["system"] == CONSEQUENCE_SYSTEM:
            raw = json.dumps({"consequence": predicted.consequence})
        else:
            raise AssertionError("unexpected system")
        return {"raw_output": raw, "transport_error": None,
                "response_metadata": {"fake": True}}


class LiveTests(unittest.TestCase):
    def test_clean_cross_process_style_restart_imports_history(self):
        with TemporaryDirectory() as directory:
            session = Path(directory) / "session"
            first = run_live(session, 2, False, DeterministicModel())
            self.assertEqual(len(first["steps"]), 2)
            old_source = first["steps"][-1]["receipt"]["source_identity"]
            resumed = run_live(session, 1, True, DeterministicModel())
            row = resumed["steps"][0]
            self.assertGreater(sum(row["prior_authenticated_observations_used"].values()), 0)
            self.assertEqual(row["imported_pre_restart_records"], 2)
            self.assertNotEqual(old_source, row["receipt"]["source_identity"])
            self.assertEqual(resumed["epoch"], first["epoch"] + 1)
            self.assertEqual(row["receipt"]["event_id"], 1)
            training = [json.loads(line) for line in
                        (session / "training-records.jsonl").read_text().splitlines()]
            self.assertEqual(len(training), 3)
            self.assertFalse(training[-1]["record"]["labels"]
                             ["prediction_is_authenticated_target"])
            self.assertTrue(training[-1]["record"]["labels"]
                            ["realized_receipt_is_authenticated_target"])

    def test_checkpoint_alteration_is_rejected(self):
        with TemporaryDirectory() as directory:
            session = Path(directory) / "session"
            run_live(session, 1, False, DeterministicModel())
            path = session / "checkpoint.json"
            document = json.loads(path.read_text())
            document["payload"]["current_state"] = 3
            path.write_text(json.dumps(document))
            with self.assertRaisesRegex(SessionError, "authentication failed"):
                SessionStore(session, True)

    def test_missing_provenance_and_duplicate_identity_rejected(self):
        with TemporaryDirectory() as directory:
            session = Path(directory) / "missing"
            with SessionStore(session, False) as store:
                store.append("events", "AUTHORIZED_REALIZED_EVENT",
                             {"authorization_status": "AUTHORIZED"})
                store.save(state=1, next_transaction_id=1)
            with self.assertRaisesRegex(SessionError, "missing provenance"):
                SessionStore(session, True)

        with TemporaryDirectory() as directory:
            session = Path(directory) / "duplicate"
            run_live(session, 1, False, DeterministicModel())
            with SessionStore(session, True) as store:
                duplicate = store.records["events"][0]["record"]
                store.append("events", "AUTHORIZED_REALIZED_EVENT", duplicate)
                store.save(state=store.checkpoint["current_state"],
                           next_transaction_id=1)
            with self.assertRaisesRegex(SessionError, "duplicate/replayed"):
                SessionStore(session, True)

    def test_consequence_request_is_frozen_independently(self):
        with TemporaryDirectory() as directory:
            client = DeterministicModel()
            result = run_live(Path(directory) / "session", 1, False, client)
            self.assertEqual(result["actual_model_calls"], 6)
            calls = [json.loads(line) for line in
                     (Path(directory) / "session" /
                      "model-calls.private.jsonl").read_text().splitlines()]
            first_joint, first_consequence = calls[0]["record"], calls[1]["record"]
            self.assertEqual(first_joint["request"]["prompt"],
                             first_consequence["request"]["prompt"])
            self.assertTrue(first_consequence["independent_of_joint_response"])
            serialized = json.dumps(first_consequence["request"])
            self.assertNotIn("predicted_next_state", serialized)
            self.assertNotIn("joint_model_response", serialized)

    def test_invalid_component_abstains_without_execution_or_memory(self):
        with TemporaryDirectory() as directory:
            session = Path(directory) / "session"
            result = run_live(session, 3, False, DeterministicModel(invalid=True))
            self.assertEqual(result["actual_model_calls"], 6)
            self.assertEqual(result["steps"][0]["status"], "ABSTAINED")
            self.assertEqual((session / "events.jsonl").read_text(), "")
            self.assertEqual((session / "training-records.jsonl").read_text(), "")

    def test_model_value_cannot_substitute_for_original_receipt(self):
        with TemporaryDirectory() as directory:
            session = Path(directory) / "session"
            with SessionStore(session, False) as store:
                runtime = LiveRuntime(store, DeterministicModel())
                capture = runtime.reader.capture()
                core = runtime.controller._active.framework.inner
                pending = runtime.controller.begin_step("HOLD")
                receipt = runtime.controller.execute_pending()
                forged = replace(receipt)
                before = list(core.memory.records)
                rejected = runtime.controller.submit_package(evidence(forged))
                self.assertFalse(rejected.committed)
                self.assertEqual(before, core.memory.records)
                self.assertEqual(capture["transaction_id"], pending.transaction_id)
                runtime.controller.release(receipt)

    def test_reconciliation_uses_joint_state_and_independent_consequence(self):
        class Disagreeing(DeterministicModel):
            def generate(self, body):
                self.requests += 1
                self.calls.append(body)
                raw = ('{"next_state":3,"consequence":-1}'
                       if body["system"] == JOINT_SYSTEM else '{"consequence":1}')
                return {"raw_output": raw, "transport_error": None,
                        "response_metadata": {}}

        with TemporaryDirectory() as directory:
            with SessionStore(Path(directory) / "session", False) as store:
                runtime = LiveRuntime(store, Disagreeing())
                capture = runtime.reader.capture()
                before = list(runtime.controller._active.framework.inner.memory.records)
                rows = runtime.map.forecasts(capture, "test")
                self.assertTrue(all(row.forecast.next_state == 3 for row in rows))
                self.assertTrue(all(row.forecast.consequence == 1 for row in rows))
                self.assertEqual(before,
                    runtime.controller._active.framework.inner.memory.records)

    def test_uncommitted_call_tail_fails_closed_on_resume(self):
        with TemporaryDirectory() as directory:
            session = Path(directory) / "session"
            with SessionStore(session, False) as store:
                store.append("calls", "REQUEST_INTENT", {"call_id": "ambiguous"})
                # Simulates a crash before the checkpoint commit.
            with self.assertRaisesRegex(SessionError, "stream mismatch"):
                SessionStore(session, True)


if __name__ == "__main__":
    unittest.main()
