"""Grounded expert routing, lifecycle separation, and causal-order tests."""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from experiments.base_framework_v0.framework import MapModel

from .live import CONSEQUENCE_SYSTEM, JOINT_SYSTEM, SessionStore
from .routing import (GroundedRouter, RoutedRuntime, RoutingError,
    RoutingEvidenceStore, analyze_routing_campaign, initialize_routing_registry,
    load_routing_registry, run_routed)


ALIASES = {"K1": "ADVANCE", "K2": "HOLD", "K3": "RETREAT"}


class JointClient:
    model_id = "deterministic-joint"
    def __init__(self):
        self.requests = 0

    def generate(self, request):
        self.requests += 1
        payload = json.loads(request["prompt"])
        action = ALIASES[payload["target_action"]]
        value = MapModel.predict_from(payload["state"], action, 1, 1)
        return dict(raw_output=json.dumps(dict(next_state=value.next_state,
            consequence=value.consequence)), transport_error=None,
            response_metadata={})


class SpecialistClient:
    def __init__(self, specialist, identity):
        self.specialist, self.horus_model_identity = specialist, identity
        self.model_id = f"deterministic-{specialist}"
        self.requests = 0

    def generate(self, request):
        self.requests += 1
        if request["system"] != CONSEQUENCE_SYSTEM:
            return dict(raw_output=None, transport_error="ROLE", response_metadata={})
        payload = json.loads(request["prompt"])
        action = ALIASES[payload["target_action"]]
        value = MapModel.predict_from(payload["state"], action, 1, 1).consequence
        if self.specialist == "G3" and payload["state"] == 1:
            if action == "ADVANCE": value = 1
            elif action == "HOLD": value = -1
        return dict(raw_output=json.dumps({"consequence": value}),
                    transport_error=None,
                    response_metadata={"horus_model_identity": self.horus_model_identity})


def clients(registry):
    result = {}
    for key in ("G2", "G3"):
        row = registry["specialists"][key]
        result[key] = SpecialistClient(key, dict(specialist_id=key,
            generation=row["generation"], artifact_sha256=row["artifact_sha256"]))
    return result


def evidence(g2, g3):
    return {"correctness": {"G2": g2, "G3": g3}}


class RoutingTests(unittest.TestCase):
    def test_cold_start_minimum_ties_and_hysteresis(self):
        router = GroundedRouter()
        selected, rows = "G2", []
        self.assertEqual(router.update(rows, selected)["selected_after"], "G2")
        for _ in range(3): rows.append(evidence(False, True))
        result = router.update(rows, selected)
        self.assertFalse(result["minimum_evidence_satisfied"])
        self.assertEqual(result["selected_after"], "G2")
        rows.append(evidence(True, False))  # 1/4 versus 3/4: exact lead two.
        result = router.update(rows, selected)
        self.assertTrue(result["switched"])
        self.assertEqual(result["selected_after"], "G3")
        # Reapplying the same evidence cannot immediately flap back.
        again = router.update(rows, "G3")
        self.assertFalse(again["switched"])
        self.assertEqual(again["selected_after"], "G3")
        tied = [evidence(True, False), evidence(False, True)] * 2
        self.assertEqual(router.update(tied, "G2")["selected_after"], "G2")

    def test_specialist_can_switch_to_g3_and_later_back_to_g2(self):
        router = GroundedRouter(); rows = []; selected = "G2"; switches = []
        for value in ([evidence(True, False)] * 4 +
                      [evidence(False, True)] * 4 +
                      [evidence(True, False)] * 4):
            rows.append(value)
            result = router.update(rows, selected)
            if result["switched"]:
                switches.append((selected, result["selected_after"]))
            selected = result["selected_after"]
        self.assertEqual(switches, [("G2", "G3"), ("G3", "G2")])

    def test_registry_preserves_rejected_global_status_and_exact_pool(self):
        with TemporaryDirectory() as directory:
            root = Path(directory) / "routing"
            initialize_routing_registry(root)
            registry = load_routing_registry(root)
            self.assertEqual(set(registry["specialists"]), {"G2", "G3"})
            self.assertEqual(registry["specialists"]["G2"]["global_lifecycle_status"],
                             "ACTIVE")
            self.assertEqual(registry["specialists"]["G3"]["global_lifecycle_status"],
                             "REJECTED")
            self.assertTrue(all(row["routing_eligibility"] == "ROUTABLE_SPECIALIST"
                                for row in registry["specialists"].values()))
            self.assertFalse(registry["payload"]["generation_3r_included"])

    def test_missing_lineage_and_artifact_mismatch_fail_closed(self):
        with TemporaryDirectory() as directory:
            root = Path(directory) / "routing"
            initialize_routing_registry(root)
            registry = load_routing_registry(root)
            Path(root / registry["specialists"]["G3"]["lineage_path"]).unlink()
            with self.assertRaisesRegex(RoutingError, "lineage_path hash mismatch"):
                load_routing_registry(root)

    def test_predictions_alone_do_not_change_router_and_hide_regime(self):
        with TemporaryDirectory() as directory:
            root, session = Path(directory) / "routing", Path(directory) / "session"
            initialize_routing_registry(root); registry = load_routing_registry(root)
            with SessionStore(session, False) as store, RoutingEvidenceStore(root) as route:
                store.configure_regime("B")
                runtime = RoutedRuntime(store, JointClient(), clients(registry), registry,
                                        route, "B")
                capture = runtime.reader.capture()
                runtime.map.forecasts(capture, "prediction-only")
                self.assertEqual(route.preview()["evidence_count"], 0)
                requests = [row["record"]["request"] for row in store.records["calls"]
                            if row["kind"] == "REQUEST_INTENT"]
                self.assertEqual(len(requests), 9)
                self.assertTrue(all("regime" not in json.dumps(row).lower()
                                    for row in requests))

    def test_live_order_restart_and_receipt_only_scoring(self):
        with TemporaryDirectory() as directory:
            root, session = Path(directory) / "routing", Path(directory) / "session"
            initialize_routing_registry(root); registry = load_routing_registry(root)
            first = run_routed(session, root, 4, False, "A",
                               joint_client=JointClient(),
                               specialist_clients=clients(registry))
            selected = first["router_final"]["selected_specialist"]
            second = run_routed(session, root, 4, True, "B", True,
                                joint_client=JointClient(),
                                specialist_clients=clients(registry))
            self.assertEqual(first["steps"][-1]["routing_evidence"][
                "selected_specialist_after"], selected)
            self.assertEqual(second["steps"][0]["selected_specialist"], selected)
            with SessionStore(session, True) as store, RoutingEvidenceStore(root) as route:
                route.bind_session(store)
                self.assertEqual(len(route.records), len(store.records["events"]), 8)
                calls = store.records["calls"]
                # First decision: all nine requests precede every response and execution.
                self.assertTrue(all(row["kind"] == "REQUEST_INTENT" for row in calls[:9]))
                first_event_time = store.records["events"][0]["record"]["recorded_at"]
                committed = route.records[0]["record"]["prediction_commitment"]
                self.assertTrue(all(calls[value["parsed_sequence"] - 1]["record"][
                    "recorded_at"] < first_event_time for value in
                    committed["specialists"].values()))
                self.assertTrue(all(row["record"]["evidence_source"] ==
                    "AUTHORIZED_ORIGINAL_RECEIPT" for row in route.records))

    def test_corrupt_routing_history_fails_closed(self):
        with TemporaryDirectory() as directory:
            root, session = Path(directory) / "routing", Path(directory) / "session"
            initialize_routing_registry(root); registry = load_routing_registry(root)
            run_routed(session, root, 1, False, "A", joint_client=JointClient(),
                       specialist_clients=clients(registry))
            path = root / "routing-evidence.jsonl"
            row = json.loads(path.read_text())
            row["record"]["correctness"]["G2"] = not row["record"]["correctness"]["G2"]
            path.write_text(json.dumps(row) + "\n")
            with self.assertRaisesRegex(RoutingError, "authentication failed"):
                RoutingEvidenceStore(root)

    def test_integrated_b_selection_and_lifecycle_remains_separate(self):
        with TemporaryDirectory() as directory:
            root, session = Path(directory) / "routing", Path(directory) / "session"
            report = Path(directory) / "report.json"
            initialize_routing_registry(root); registry = load_routing_registry(root)
            run_routed(session, root, 12, False, "A", joint_client=JointClient(),
                       specialist_clients=clients(registry))
            run_routed(session, root, 6, True, "B", True, joint_client=JointClient(),
                       specialist_clients=clients(registry))
            run_routed(session, root, 6, True, "B", joint_client=JointClient(),
                       specialist_clients=clients(registry))
            run_routed(session, root, 12, True, "A", True, joint_client=JointClient(),
                       specialist_clients=clients(registry))
            with RoutingEvidenceStore(root) as route:
                switches = [(row["record"]["selected_specialist"],
                             row["record"]["selected_specialist_after"])
                            for row in route.records if row["record"]["switch_occurred"]]
            self.assertIn(("G2", "G3"), switches)
            self.assertEqual(registry["specialists"]["G3"][
                "global_lifecycle_status"], "REJECTED")
            result = analyze_routing_campaign(session, root, report)
            self.assertEqual(result["total_model_calls"], 324)
            self.assertEqual(result["restart_proof"]["attempts_by_runtime"],
                             {1: 12, 2: 6, 3: 6, 4: 12})
            self.assertTrue(result["restart_proof"][
                "specialist_artifacts_reverified_on_every_runtime"])
            with SessionStore(session, True) as store:
                requests = [row for row in store.records["calls"]
                            if row["kind"] == "REQUEST_INTENT"]
                self.assertEqual(len(requests), 36 * 9)
                self.assertTrue(all("regime" not in json.dumps(
                    row["record"]["request"]).lower() for row in requests))


if __name__ == "__main__":
    unittest.main()
