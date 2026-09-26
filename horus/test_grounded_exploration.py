"""Finite grounded exploration, confidence integrity, and autonomous campaign tests."""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from experiments.base_framework_v0.framework import ACTION_ORDER, MapModel
from experiments.base_framework_v1.framework import CrossAuthorityState, StepResult

from .core import MapForecast, digest
from .grounded_exploration import (ExplorerConfidenceStore,
    GroundedExplorationRuntime, GroundedExplorer,
    analyze_grounded_exploration_campaign,
    initialize_grounded_exploration_registry,
    load_grounded_exploration_registry, run_grounded_exploration_segment)
from .live import CONSEQUENCE_SYSTEM, SessionStore
from .relation_routing import (RelationEvidenceStore, RelationGroundedRouter,
                               relation_identity)
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
    return {key: SpecialistClient(key, dict(specialist_id=key,
        generation=registry["specialists"][key]["generation"],
        artifact_sha256=registry["specialists"][key]["artifact_sha256"]))
        for key in ("G2", "G3")}


def confidence_state():
    return dict(attempted_decisions=0, authorized_decisions=0,
        last_probe_decision_sequence=None, last_probe_authorized_decision=None,
        last_execution_by_relation={}, unresolved_contradictions={})


def forecast(action, g2=1, g3=1, routed=1, history=3):
    return dict(G2_consequence=g2, G3_consequence=g3,
        selected_specialist="G2", routed_consequence=routed, next_state=1,
        action_alias={"ADVANCE": "K1", "HOLD": "K2", "RETREAT": "K3"}[action],
        history_count=history, valid=True)


def tuple_forecasts(rows):
    return tuple(MapForecast(action=action, action_alias=rows[action]["action_alias"],
        next_state=rows[action]["next_state"],
        consequence=rows[action]["routed_consequence"], abstained=False,
        failure=None, history_count=rows[action]["history_count"], input_context={})
        for action in ACTION_ORDER)


def previews(state=1, evidence=3, g2=3, g3=0):
    return {action: dict(relation=relation_identity(state, action),
        selected_specialist="G2",
        scores={"G2": {"correct": g2, "total": evidence},
                "G3": {"correct": g3, "total": evidence}},
        relation_evidence_count=evidence, total_evidence_count=evidence * 3)
        for action in ACTION_ORDER}


def route_rows(state=1, count=3):
    rows = []
    sequence = 0
    for action in ACTION_ORDER:
        for _ in range(count):
            sequence += 1
            rows.append(dict(evidence_sequence=sequence,
                relation=relation_identity(state, action), realized_consequence=1,
                correctness={"G2": True, "G3": False}))
    return rows


class GroundedExplorerRuleTests(unittest.TestCase):
    def setUp(self):
        self.explorer = GroundedExplorer()
        self.rows = {action: forecast(action) for action in ACTION_ORDER}

    def metadata(self, action, **updates):
        state = confidence_state(); state.update(updates)
        return self.explorer.relation_metadata(pre_state=1, action=action,
            forecast=self.rows[action], preview=previews()[action],
            routing_records=route_rows(), confidence_state=state)

    def test_01_untried_relation_becomes_probe_candidate(self):
        value = self.explorer.relation_metadata(pre_state=1, action="HOLD",
            forecast=self.rows["HOLD"],
            preview=previews(evidence=0, g2=0, g3=0)["HOLD"],
            routing_records=[], confidence_state=confidence_state())
        self.assertIn("PROBE_UNTRIED", value["qualifying_probe_reasons"])

    def test_02_disagreement_becomes_probe_candidate(self):
        self.rows["HOLD"] = forecast("HOLD", 1, -1)
        value = self.explorer.relation_metadata(pre_state=1, action="HOLD",
            forecast=self.rows["HOLD"],
            preview=previews(evidence=2, g2=1, g3=1)["HOLD"],
            routing_records=route_rows(count=2), confidence_state=confidence_state())
        self.assertIn("PROBE_DISAGREEMENT", value["qualifying_probe_reasons"])

    def test_03_stale_relation_becomes_probe_candidate(self):
        state = confidence_state(); state["authorized_decisions"] = 12
        state["last_execution_by_relation"]["1:HOLD"] = dict(
            authorized_decision=4)
        value = self.explorer.relation_metadata(pre_state=1, action="HOLD",
            forecast=self.rows["HOLD"], preview=previews()["HOLD"],
            routing_records=route_rows(), confidence_state=state)
        self.assertIn("PROBE_STALE", value["qualifying_probe_reasons"])

    def test_04_recent_contradiction_becomes_probe_candidate(self):
        state = confidence_state()
        state["unresolved_contradictions"]["1:HOLD"] = dict(marker=True)
        value = self.explorer.relation_metadata(pre_state=1, action="HOLD",
            forecast=self.rows["HOLD"], preview=previews()["HOLD"],
            routing_records=route_rows(), confidence_state=state)
        self.assertEqual(value["qualifying_probe_reasons"][0],
                         "PROBE_CONTRADICTION")

    def test_05_stable_grounded_relation_is_not_probed(self):
        state = confidence_state(); state["authorized_decisions"] = 5
        state["last_execution_by_relation"]["1:HOLD"] = dict(
            authorized_decision=4)
        value = self.explorer.relation_metadata(pre_state=1, action="HOLD",
            forecast=self.rows["HOLD"], preview=previews()["HOLD"],
            routing_records=route_rows(), confidence_state=state)
        self.assertEqual(value["qualifying_probe_reasons"], [])

    def test_06_probe_budget_is_enforced(self):
        state = confidence_state(); state["last_probe_authorized_decision"] = 1
        state["authorized_decisions"] = 1
        result = self.explorer.derive(pre_state=1, forecasts=self.rows,
            routed_forecasts=tuple_forecasts(self.rows),
            previews=previews(evidence=0, g2=0, g3=0), routing_records=[],
            confidence_state=state, all_predictions_valid=True)
        self.assertEqual(result["mode"], "EXPLOIT")
        self.assertFalse(result["probe_budget_available"])

    def test_07_probe_reason_is_pre_execution_data(self):
        result = self.explorer.derive(pre_state=1, forecasts=self.rows,
            routed_forecasts=tuple_forecasts(self.rows),
            previews=previews(evidence=0, g2=0, g3=0), routing_records=[],
            confidence_state=confidence_state(), all_predictions_valid=True)
        self.assertEqual((result["mode"], result["action"], result["reason"]),
                         ("PROBE", "ADVANCE", "PROBE_UNTRIED"))

    def test_09_probe_evidence_can_contribute_to_g2_g3_switch(self):
        router = RelationGroundedRouter(); relation = relation_identity(1, "HOLD")
        rows = [dict(relation=relation, correctness={"G2": False, "G3": True})
                for _ in range(3)]
        self.assertEqual(router.update(rows, relation, "G2")["selected_after"], "G3")

    def test_10_later_evidence_can_contribute_to_switchback(self):
        router = RelationGroundedRouter(); relation = relation_identity(1, "HOLD")
        rows = [dict(relation=relation, correctness={"G2": True, "G3": False})
                for _ in range(3)]
        self.assertEqual(router.update(rows, relation, "G3")["selected_after"], "G2")

    def test_11_unrelated_relation_evidence_is_isolated(self):
        router = RelationGroundedRouter()
        rows = [dict(relation=relation_identity(1, "HOLD"),
                     correctness={"G2": False, "G3": True}) for _ in range(3)]
        result = router.update(rows, relation_identity(1, "ADVANCE"), "G2")
        self.assertEqual(result["selected_after"], "G2")

    def test_15_exploit_uses_mechanical_unique_maximum(self):
        rows = {"ADVANCE": forecast("ADVANCE", routed=0),
                "HOLD": forecast("HOLD", routed=1),
                "RETREAT": forecast("RETREAT", routed=-1)}
        state = confidence_state(); state["authorized_decisions"] = 1
        for action in ACTION_ORDER:
            state["last_execution_by_relation"][f"1:{action}"] = dict(
                authorized_decision=1)
        result = self.explorer.derive(pre_state=1, forecasts=rows,
            routed_forecasts=tuple_forecasts(rows), previews=previews(),
            routing_records=route_rows(), confidence_state=state,
            all_predictions_valid=True)
        self.assertEqual((result["mode"], result["action"], result["reason"]),
                         ("EXPLOIT", "HOLD", "UNIQUE_ROUTED_MAXIMUM"))


class GroundedExplorationCampaignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = TemporaryDirectory()
        base = Path(cls.tmp.name)
        cls.root, cls.session, cls.report = (base / "registry", base / "session",
                                             base / "report.json")
        initialize_grounded_exploration_registry(cls.root)
        registry = load_grounded_exploration_registry(cls.root)["relation_registry"]
        for segment, resume in (("A1", False), ("B1", True),
                                ("B2", True), ("A2", True)):
            run_grounded_exploration_segment(cls.session, cls.root, segment, resume,
                joint_client=JointClient(), specialist_clients=clients(registry))
        cls.result = analyze_grounded_exploration_campaign(
            cls.session, cls.root, cls.report)

    @classmethod
    def tearDownClass(cls): cls.tmp.cleanup()

    def test_08_only_authenticated_receipts_update_confidence(self):
        with SessionStore(self.session, True) as store, \
                ExplorerConfidenceStore(self.root) as confidence:
            self.assertEqual(confidence.state["authorized_decisions"],
                             len(store.records["events"]))
            self.assertTrue(all(row["record"]["authorization_status"] == "AUTHORIZED"
                                for row in store.records["events"]))

    def test_12_restart_preserves_confidence_and_probe_state(self):
        proof = self.result["restart_proof"]
        self.assertEqual(proof["B_runtime_indices"], [2, 3])
        self.assertTrue(proof["confidence_exact_replay"])
        self.assertTrue(proof["fresh_source_and_epoch_per_runtime"])

    def test_13_hidden_regime_does_not_enter_decision_logic(self):
        self.assertEqual(self.result["hidden_regime_prompt_checks"], 486)

    def test_14_autonomous_mode_contains_zero_calibration_actions(self):
        self.assertEqual(self.result["calibration_executions"], 0)
        self.assertEqual(self.result["autonomous_decision_attempts"], 54)

    def test_16_corrupt_confidence_state_fails_closed(self):
        path = self.root / "exploration-state.json"
        original = path.read_text()
        row = json.loads(original); row["payload"]["attempted_decisions"] += 1
        path.write_text(json.dumps(row))
        try:
            with self.assertRaisesRegex(RoutingError, "authentication failed"):
                ExplorerConfidenceStore(self.root)
        finally:
            path.write_text(original)


class GroundedExplorationR2ScheduleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = TemporaryDirectory()
        base = Path(cls.tmp.name)
        cls.root, cls.session, cls.report = (base / "registry", base / "session",
                                             base / "report.json")
        initialize_grounded_exploration_registry(cls.root)
        registry = load_grounded_exploration_registry(cls.root)["relation_registry"]
        cls.segments = []
        for segment, resume in (("R2_A1_1", False), ("R2_A1_2", True),
                                ("R2_B1", True), ("R2_B2", True),
                                ("R2_A2_1", True), ("R2_A2_2", True)):
            cls.segments.append(run_grounded_exploration_segment(
                cls.session, cls.root, segment, resume,
                joint_client=JointClient(), specialist_clients=clients(registry),
                runtime_schedule="R2"))
        cls.result = analyze_grounded_exploration_campaign(
            cls.session, cls.root, cls.report, runtime_schedule="R2")

    @classmethod
    def tearDownClass(cls): cls.tmp.cleanup()

    def test_17_fixed_nine_plus_nine_rollover_completes_phase(self):
        first, second = self.segments[:2]
        self.assertEqual((first["registered_decision_range"],
                          second["registered_decision_range"]),
                         ([1, 9], [10, 18]))
        self.assertEqual(sum(len(row["rows"]) for row in self.segments[:2]), 18)
        self.assertEqual(self.result["phase_decision_counts"]["A1"], 18)

    def test_18_each_registered_runtime_is_bounded_to_nine(self):
        proof = self.result["restart_proof"]
        self.assertEqual(proof["batches_by_runtime"],
                         {runtime: 9 for runtime in range(1, 7)})
        self.assertLessEqual(max(proof["executions_by_runtime"].values()), 9)
        self.assertEqual(proof["maximum_attempts_per_runtime"], 9)
        self.assertEqual(proof["protected_episode_limit"], 12)

    def test_19_memory_routing_and_confidence_survive_rollover(self):
        first, second = self.segments[:2]
        self.assertEqual(second["rollover_input"]["prior_attempted_decisions"], 9)
        self.assertEqual(second["rollover_input"]["prior_authorized_events"],
                         first["checkpoint"]["completed_steps"])
        self.assertEqual(second["rollover_input"]["prior_routing_evidence"],
                         first["checkpoint"]["completed_steps"])
        self.assertGreater(second["rollover_input"]["prior_authorized_events"], 0)
        imported = [row.get("imported_pre_restart_records", 0)
                    for row in second["rows"] if row["status"] == "AUTHORIZED"]
        self.assertTrue(imported and max(imported) > 0)
        self.assertEqual(second["rollover_input"]["prior_confidence_state_sha256"],
                         digest({key: first["confidence_state"][key] for key in
                            ("attempted_decisions", "authorized_decisions",
                             "last_probe_decision_sequence",
                             "last_probe_authorized_decision",
                             "last_execution_by_relation",
                             "unresolved_contradictions")}))

    def test_20_every_rollover_has_fresh_source_and_epoch(self):
        proof = self.result["restart_proof"]
        self.assertEqual(proof["runtime_indices"], list(range(1, 7)))
        self.assertTrue(proof["fresh_source_and_epoch_per_runtime"])
        self.assertEqual(proof["B_runtime_indices"], [3, 4])

    def test_21_r2_prompts_retain_hidden_state_exclusion(self):
        self.assertEqual(self.result["hidden_regime_prompt_checks"], 486)
        self.assertEqual(self.result["calibration_executions"], 0)


class GroundedExplorationFrameworkRejectionTests(unittest.TestCase):
    def test_22_rejected_step_result_is_recorded_without_execution(self):
        with TemporaryDirectory() as directory:
            base = Path(directory); root = base / "registry"; session = base / "session"
            initialize_grounded_exploration_registry(root)
            relation = load_grounded_exploration_registry(root)["relation_registry"]
            with SessionStore(session, False) as store, \
                    RelationEvidenceStore(root) as routing, \
                    ExplorerConfidenceStore(root) as confidence:
                store.configure_regime("A", False)
                runtime = GroundedExplorationRuntime(store, JointClient(),
                    clients(relation), relation, routing, confidence, "A")
                rejected = StepResult(1, CrossAuthorityState.REJECTED, "ADVANCE",
                    False, False, False, False, False, False,
                    "begin validation failed")
                runtime.controller.begin_step = lambda action: rejected
                row = runtime.execute_autonomous()
                self.assertEqual(row["status"], "FRAMEWORK_REJECTED")
                self.assertEqual(len(store.records["events"]), 0)
                self.assertEqual(len(routing.records), 0)
                self.assertIsNone(runtime.controller._source.reader().current())
                self.assertIsNone(runtime.controller._active.framework.inner.pending)
                self.assertFalse(hasattr(rejected, "prediction"))
                self.assertEqual(confidence.state["attempted_decisions"], 1)
                self.assertEqual(confidence.state["authorized_decisions"], 0)

    def test_23_internal_problem_is_non_authoritative(self):
        rejected = StepResult(13, CrossAuthorityState.REJECTED, "HOLD",
            False, False, False, False, False, False,
            "begin validation failed")
        problem = GroundedExplorationRuntime._internal_route_problem(rejected, 12)
        self.assertEqual(problem["type"], "INTERNAL_ROUTE_PROBLEM")
        self.assertEqual(problem["observed_constraint"],
                         "PROTECTED_EPISODE_LIMIT")
        self.assertEqual(problem["suggested_need"], "NEW_RUNTIME_ROUTE")
        for field in ("authoritative", "controls_execution",
                      "controls_runtime_creation", "controls_schedule",
                      "trains_model", "execution_occurred", "receipt_created",
                      "memory_mutated", "routing_evidence_created"):
            self.assertIs(problem[field], False)


if __name__ == "__main__":
    unittest.main()
