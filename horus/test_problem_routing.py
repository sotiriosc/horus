"""Zero-inference tests for the bounded Horus v0.8 problem/route layer."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from experiments.base_framework_v0.framework import ACTION_ORDER

from .grounded_exploration import GroundedExplorationRuntime
from .problem_routing import (ProblemRouteStore, RouteBroker,
    initialize_problem_route_registry, load_problem_route_registry)
from .routing import RoutingError


class FakeStore:
    def __init__(self):
        self.checkpoint = dict(session_id="test-session", attempted_decisions=0)
        self.records = {"events": []}


def metadata(state=2):
    rows = {}
    for index, action in enumerate(ACTION_ORDER):
        rows[action] = dict(relation={"pre_state": state, "action": action},
            authenticated_observations=3 + index,
            most_recent_observation_sequence=10 + index,
            recent_realized_consequences=[1], recent_correctness={},
            local_scores={"G2": {"correct": 2, "total": 3},
                          "G3": {"correct": 1, "total": 3}},
            selected_specialist="G2",
            specialists_disagree=(action == "RETREAT"),
            clear_local_preference=False,
            observations_since_last_execution=1 + index,
            unresolved_recent_contradiction=(
                {"observed": True} if action == "ADVANCE" else None),
            qualifying_probe_reasons=[])
    return rows


def forecasts(tie=True):
    values = {"ADVANCE": 1, "HOLD": 0, "RETREAT": 1 if tie else -1}
    return {action: dict(G2_consequence=values[action],
        G3_consequence=(-1 if action == "RETREAT" else values[action]),
        selected_specialist="G2", routed_consequence=values[action],
        next_state=2, action_alias=f"K{index + 1}", history_count=3,
        valid=True) for index, action in enumerate(ACTION_ORDER)}


def ordinary(sequence, *, tie=True, state=2):
    return dict(decision_sequence=sequence, mode="EXPLOIT",
        action=None if tie else "ADVANCE",
        reason="EXPLOIT_TIED_MAXIMUM" if tie else "UNIQUE_ROUTED_MAXIMUM",
        abstained=tie, probe_budget_available=True,
        relation_confidence=metadata(state), coverage={})


class ProblemRouteRuleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.root = Path(self.tmp.name) / "registry"
        initialize_problem_route_registry(self.root)
        self.store = FakeStore()
        self.problems = ProblemRouteStore(self.root)

    def tearDown(self):
        self.problems.close(); self.tmp.cleanup()

    def prepare(self, tie=True, state=2):
        sequence = self.store.checkpoint["attempted_decisions"] + 1
        return self.problems.prepare(store=self.store,
            ordinary_decision=ordinary(sequence, tie=tie, state=state),
            pre_state=state, forecasts=forecasts(tie))

    def finish(self, decision, authorized=False):
        self.store.checkpoint["attempted_decisions"] += 1
        row = dict(prediction_batch_sequence=decision["decision_sequence"],
                   status="AUTHORIZED" if authorized else "ABSTAINED")
        if authorized:
            self.store.records["events"].append({"record": {}})
            row.update(receipt_identity=["source", 1, 1,
                       decision["decision_sequence"]],
                receipt={"source_identity": "source", "event_id": 1,
                         "epoch": 1,
                         "transaction_id": decision["decision_sequence"],
                         "next_state": 1,
                         "realized_consequence": 1},
                routing_evidence={"evidence_sequence": len(
                    self.store.records["events"])})
        return self.problems.complete(store=self.store, row=row)

    def open_problem(self):
        first = self.prepare(); self.finish(first)
        second = self.prepare()
        self.assertEqual(second["reason"], "PROBE_TIED_MAXIMUM")
        return second

    def test_01_one_tie_does_not_create_problem(self):
        decision = self.prepare()
        self.assertTrue(decision["abstained"])
        self.assertEqual(self.problems.state["problems"], {})

    def test_02_persistent_identical_tie_creates_one_problem(self):
        second = self.open_problem()
        self.assertEqual(len(self.problems.state["problems"]), 1)
        self.assertEqual(second["problem_id"], "PR-0001")

    def test_03_problem_object_has_no_execution_authority(self):
        self.open_problem()
        problem = next(iter(self.problems.state["problems"].values()))
        for field in ("authoritative", "controls_execution", "alters_memory",
                      "alters_specialist_selection", "changes_prediction",
                      "trains_model", "changes_protected_bound",
                      "alters_simulator", "creates_receipt"):
            self.assertIs(problem[field], False)

    def test_04_broker_rejects_unregistered_route(self):
        with self.assertRaisesRegex(RoutingError, "not registered"):
            RouteBroker().validate_route("MODEL_WRITES_NEW_ROUTE")

    def test_05_tie_probe_is_one_of_tied_maxima(self):
        decision = self.open_problem()
        self.assertIn(decision["action"], ("ADVANCE", "RETREAT"))
        self.assertNotEqual(decision["action"], "HOLD")

    def test_06_information_priority_is_deterministic(self):
        first = self.open_problem()
        self.assertEqual(first["action"], "RETREAT")
        self.assertTrue(first["tie_information_priority"][
            "specialists_disagree"])

    def test_07_receipt_updates_problem_evidence(self):
        decision = self.open_problem(); self.finish(decision, authorized=True)
        problem = next(iter(self.problems.state["problems"].values()))
        self.assertEqual((problem["probe_count"], len(problem["receipt_evidence"])),
                         (1, 1))

    def test_08_probe_receipt_does_not_false_resolve(self):
        decision = self.open_problem(); self.finish(decision, authorized=True)
        problem = next(iter(self.problems.state["problems"].values()))
        self.assertEqual(problem["status"], "ROUTE_EXECUTED")

    def test_09_solved_ordinary_decision_resolves_problem(self):
        decision = self.open_problem(); self.finish(decision, authorized=True)
        solved = self.prepare(tie=False)
        problem = next(iter(self.problems.state["problems"].values()))
        self.assertEqual(problem["status"], "RESOLVED")
        self.assertEqual(solved["ordinary_route"], "NORMAL_EXPLOIT")

    def test_10_maximum_two_probe_bound(self):
        decision = self.open_problem(); self.finish(decision, authorized=True)
        decision = self.prepare(); self.finish(decision, authorized=True)
        decision = self.prepare()
        problem = next(iter(self.problems.state["problems"].values()))
        self.assertTrue(decision["abstained"])
        self.assertEqual((problem["probe_count"], problem["status"]),
                         (2, "UNRESOLVED"))

    def test_11_restart_preserves_open_problem_and_budget(self):
        decision = self.open_problem(); self.finish(decision, authorized=True)
        problem_before = deepcopy(self.problems.state["problems"])
        self.problems.close(); self.problems = ProblemRouteStore(self.root)
        self.problems.bind_session(self.store)
        self.assertEqual(self.problems.state["problems"], problem_before)
        self.assertEqual(next(iter(problem_before.values()))["probe_count"], 1)

    def test_12_unrelated_state_cannot_resolve_problem(self):
        decision = self.open_problem(); self.finish(decision, authorized=True)
        unrelated = self.prepare(tie=False, state=1)
        problem = next(iter(self.problems.state["problems"].values()))
        self.assertEqual(problem["status"], "ROUTE_EXECUTED")
        self.assertEqual(unrelated["action"], "ADVANCE")

    def test_13_hidden_answers_are_absent_from_detector_record(self):
        self.prepare()
        record = self.problems.records[-1]["record"]
        self.assertIs(record["hidden_regime_available"], False)
        self.assertIs(record["simulator_law_available"], False)
        self.assertIs(record["future_consequence_available"], False)
        self.assertIs(record["counterfactual_outcomes_available"], False)

    def test_14_internal_problem_can_request_new_runtime(self):
        result = RouteBroker().request("NEW_RUNTIME", context="INTERNAL_ROUTE",
                                       preauthorized_rollover=True)
        self.assertEqual(result["broker_result"],
                         "AUTHORIZED_PREREGISTERED_ROLLOVER")

    def test_15_new_runtime_cannot_bypass_authorization_or_bound(self):
        result = RouteBroker().request("NEW_RUNTIME", context="INTERNAL_ROUTE")
        self.assertEqual(result["broker_result"],
                         "REQUEST_REQUIRES_EXTERNAL_APPROVAL")
        self.assertFalse(result["limit_changed"])

    def test_16_new_specialist_is_external_approval_only(self):
        result = RouteBroker().request("NEW_SPECIALIST", context="VALUE_TIE")
        self.assertEqual(result["broker_result"],
                         "REQUEST_REQUIRES_EXTERNAL_APPROVAL")
        self.assertIsNone(result["selected_route"])

    def test_17_policy_forbids_calibration(self):
        registry = load_problem_route_registry(self.root)
        self.assertEqual(registry["policy"]["calibration_actions"], 0)

    def test_18_r2_framework_refusal_remains_non_authoritative(self):
        from experiments.base_framework_v1.framework import (CrossAuthorityState,
                                                              StepResult)
        rejected = StepResult(13, CrossAuthorityState.REJECTED, "HOLD",
            False, False, False, False, False, False,
            "begin validation failed")
        problem = GroundedExplorationRuntime._internal_route_problem(rejected, 12)
        self.assertIs(problem["authoritative"], False)
        self.assertEqual(problem["observed_constraint"],
                         "PROTECTED_EPISODE_LIMIT")
        self.assertEqual(problem["requested_capability"], "NEW_RUNTIME")


if __name__ == "__main__":
    unittest.main()
