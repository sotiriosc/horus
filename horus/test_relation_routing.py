"""Relation isolation, causal order, restart, and exact campaign tests."""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from experiments.base_framework_v0.framework import MapModel

from .live import CONSEQUENCE_SYSTEM, SessionStore
from .relation_routing import (RelationEvidenceStore, RelationGroundedRouter,
    analyze_relation_routing_campaign, initialize_relation_routing_registry,
    load_relation_routing_registry, relation_identity, run_relation_segment)
from .routing import RoutingError


ALIASES = {"K1": "ADVANCE", "K2": "HOLD", "K3": "RETREAT"}


class JointClient:
    model_id = "deterministic-joint"
    def __init__(self): self.requests = 0
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


def scored(state, action, g2, g3):
    return {"relation": relation_identity(state, action),
            "correctness": {"G2": g2, "G3": g3}}


class RelationRouterUnitTests(unittest.TestCase):
    def test_evidence_isolated_and_hold_cannot_change_advance(self):
        router = RelationGroundedRouter()
        hold, advance = relation_identity(1, "HOLD"), relation_identity(1, "ADVANCE")
        rows = [scored(1, "HOLD", False, True) for _ in range(3)]
        switched = router.update(rows, hold, "G2")
        self.assertEqual(switched["selected_after"], "G3")
        untouched = router.update(rows, advance, "G2")
        self.assertEqual(untouched["scores"]["G3"], {"correct": 0, "total": 0})
        self.assertEqual(untouched["selected_after"], "G2")

    def test_local_minimum_tie_hysteresis_and_switchback(self):
        router = RelationGroundedRouter(); relation = relation_identity(1, "HOLD")
        rows = [scored(1, "HOLD", False, True) for _ in range(2)]
        self.assertFalse(router.update(rows, relation, "G2")["switched"])
        rows.append(scored(1, "HOLD", False, True))
        self.assertEqual(router.update(rows, relation, "G2")["selected_after"], "G3")
        self.assertEqual(router.update(rows, relation, "G3")["selected_after"], "G3")
        rows.extend(scored(1, "HOLD", True, False) for _ in range(4))
        self.assertEqual(router.update(rows, relation, "G3")["selected_after"], "G2")
        tied = [scored(1, "HOLD", True, False),
                scored(1, "HOLD", False, True)] * 2
        self.assertEqual(router.update(tied, relation, "G3")["selected_after"], "G3")

    def test_separate_relations_can_select_different_specialists(self):
        router = RelationGroundedRouter()
        rows = ([scored(1, "HOLD", False, True) for _ in range(3)] +
                [scored(1, "ADVANCE", True, False) for _ in range(3)])
        hold = router.update(rows, relation_identity(1, "HOLD"), "G2")
        advance = router.update(rows, relation_identity(1, "ADVANCE"), "G2")
        self.assertEqual((hold["selected_after"], advance["selected_after"]),
                         ("G3", "G2"))


class RelationRoutingIntegrityTests(unittest.TestCase):
    def test_registry_lifecycle_exact_pool_and_missing_lineage(self):
        with TemporaryDirectory() as directory:
            root = Path(directory) / "routing"
            initialize_relation_routing_registry(root)
            registry = load_relation_routing_registry(root)
            self.assertEqual(set(registry["specialists"]), {"G2", "G3"})
            self.assertEqual(registry["specialists"]["G2"]["global_lifecycle_status"],
                             "ACTIVE")
            self.assertEqual(registry["specialists"]["G3"]["global_lifecycle_status"],
                             "REJECTED")
            self.assertFalse(registry["payload"]["generation_3r_included"])
            (root / registry["specialists"]["G3"]["lineage_path"]).unlink()
            with self.assertRaisesRegex(RoutingError, "lineage_path hash mismatch"):
                load_relation_routing_registry(root)

    def test_untrusted_event_cannot_update_and_corruption_fails_closed(self):
        with TemporaryDirectory() as directory:
            root, session = Path(directory) / "routing", Path(directory) / "session"
            initialize_relation_routing_registry(root)
            with SessionStore(session, False) as store, RelationEvidenceStore(root) as route:
                with self.assertRaisesRegex(RoutingError,
                                            "receipt/routing|receipt was not the next"):
                    route.record(store, context_hash="0" * 64,
                        predictions={"G2": 1, "G3": -1}, commitment={},
                        event_envelope={}, execution_kind="ROUTING_CALIBRATION_EXECUTION",
                        per_action_selection={"HOLD": "G2"})
            path = root / "router-state.json"
            row = json.loads(path.read_text())
            row["payload"]["relations"] = {"1:HOLD": {}}
            path.write_text(json.dumps(row))
            with self.assertRaisesRegex(RoutingError, "authentication failed"):
                RelationEvidenceStore(root)

    def test_exact_campaign_restart_order_memory_labels_and_offline_replay(self):
        with TemporaryDirectory() as directory:
            root, session = Path(directory) / "routing", Path(directory) / "session"
            report = Path(directory) / "report.json"
            initialize_relation_routing_registry(root)
            registry = load_relation_routing_registry(root)
            outputs = []
            for segment, resume in (("A1", False), ("B1", True),
                                    ("B2", True), ("A2", True)):
                outputs.append(run_relation_segment(session, root, segment, resume,
                    joint_client=JointClient(), specialist_clients=clients(registry)))
            result = analyze_relation_routing_campaign(session, root, report)
            self.assertEqual(result["total_model_calls"], 189)
            self.assertEqual(result["prediction_batches"], 21)
            self.assertEqual(result["execution_kind_counts"],
                {"ROUTING_CALIBRATION_EXECUTION": 18,
                 "EXPLORER_SELECTED_EXECUTION": 1})
            trace = result["target_relation_trace"]
            calibrations = [row for row in trace
                            if row["execution_kind"] == "ROUTING_CALIBRATION_EXECUTION"]
            self.assertEqual([row["realized_consequence"] for row in calibrations],
                             [1] * 6 + [-1] * 6 + [1] * 6)
            switches = [(row["from_specialist"], row["to_specialist"])
                        for row in result["target_relation_switches"]]
            self.assertEqual(switches, [("G2", "G3"), ("G3", "G2")])
            self.assertTrue(result["simultaneous_mixed_specialist_examples"])
            self.assertTrue(result["restart_proof"][
                "target_relation_selection_continuity"]["preserved"])
            self.assertTrue(result["restart_proof"][
                "specialist_artifacts_reverified_on_every_runtime"])
            self.assertEqual(result["global_lifecycle_status"],
                             {"G2": "ACTIVE", "G3": "REJECTED"})
            self.assertTrue(result["global_vs_local_offline_replay"]["rows"])
            self.assertEqual(result["memory_contradiction"][
                "chronological_consequences"][:18], [1] * 6 + [-1] * 6 + [1] * 6)
            with SessionStore(session, True) as store, RelationEvidenceStore(root) as route:
                route.bind_session(store)
                self.assertEqual(store.checkpoint["runtime_index"], 4)
                self.assertEqual(len(store.records["events"]), len(route.records), 19)
                requests = [row for row in store.records["calls"]
                            if row["kind"] == "REQUEST_INTENT"]
                self.assertEqual(len(requests), 189)
                self.assertTrue(all("regime" not in json.dumps(
                    row["record"]["request"]).lower() for row in requests))
                self.assertTrue(all(row["kind"] == "REQUEST_INTENT"
                                    for row in store.records["calls"][:9]))
                events = [row["record"] for row in store.records["events"]]
                self.assertEqual(Counter(row["execution_kind"] for row in events),
                    Counter({"ROUTING_CALIBRATION_EXECUTION": 18,
                             "EXPLORER_SELECTED_EXECUTION": 1}))
                self.assertTrue(all(row["authorization_status"] == "AUTHORIZED"
                                    for row in events))
                calls = {row["sequence"]: row for row in store.records["calls"]}
                for envelope, event in zip(route.records, events):
                    commitment = envelope["record"]["prediction_commitment"]
                    for value in commitment["specialists"].values():
                        self.assertLess(calls[value["parsed_sequence"]]["record"][
                            "recorded_at"], event["recorded_at"])
                self.assertTrue(all(row["action_source"] ==
                    "REGISTERED_FORCED_RELATION_PROBE" for row in events[:18]))
                self.assertEqual(events[-1]["action_source"], "MECHANICAL_EXPLORER")


if __name__ == "__main__":
    unittest.main()
