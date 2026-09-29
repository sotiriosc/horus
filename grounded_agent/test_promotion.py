"""Zero-inference checks for the exact frozen S candidate and active selector."""

from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import unittest

from horus.live import SessionStore
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory
from experiments.grounded_authority_autonomous_agent_v0.protocol import ACTIONS
from experiments.grounded_stagnation_escape_evaluation_v0 import candidate, worker as base
from experiments.grounded_stagnation_escape_evaluation_v0.analyze import independent_suffix
from experiments.grounded_stagnation_escape_promotion_controlled_v0 import worker as frozen
from grounded_agent import decide, previous_incumbent_decide, promoted_decide


FROZEN_CANDIDATE_SHA256 = "2293c46be58684f6dcf903b82dff7d29bc9fdef69790b4c22e154c750c8a5b92"
FROZEN_CONTROLLED_WORKER_SHA256 = "83d6cb5b0d336558f6b459eaa9eb8da8939e57f59f89a7638c2c36b3fa8d6a74"
FROZEN_PROTECTED_EXECUTION_SHA256 = "5e9b1734e10da48883e55281b883db2ae7df94664fd8334940f6841e759354d2"


def assessment(kind, consequence=None, relation_type="DETERMINISTIC"):
    return dict(kind=kind, relation_type=relation_type,
        established_value=None if consequence is None else dict(next_state=0, consequence=consequence))


def views(fallback="HOLD"):
    return {a: assessment("ESTABLISHED", 0) if a == fallback else assessment("UNSEEN")
            for a in ACTIONS}


def row(index, state=0, action="HOLD", next_state=None, assessments=None):
    return dict(index=index, state=state, selected_action=action,
        decision_source="SAFE_GROUNDED_FALLBACK", policy_route="MODEL",
        action_parse_status="VALID", grounded_assessments_before=assessments or views(action),
        realized=dict(next_state=state if next_state is None else next_state, consequence=0))


class PromotionTests(TestCase):
    def test_frozen_source_and_active_selector(self):
        for module, expected in ((candidate, FROZEN_CANDIDATE_SHA256),
                (frozen, FROZEN_CONTROLLED_WORKER_SHA256),
                (base, FROZEN_PROTECTED_EXECUTION_SHA256)):
            self.assertEqual(sha256(Path(module.__file__).read_bytes()).hexdigest(), expected)
        self.assertEqual(candidate.THRESHOLD, 3)
        self.assertEqual(ACTIONS, ("ADVANCE", "HOLD", "RETREAT"))
        self.assertIs(decide, promoted_decide)
        self.assertIsNot(decide, previous_incumbent_decide)

    def test_exact_candidate_eligibility_and_precedence(self):
        suffix = dict(count=3, relation=[0, "HOLD"])
        with patch.object(candidate, "qualifying_suffix", return_value=suffix):
            self.assertEqual(candidate.escape_choice(None, None, 0, views())[0], "ADVANCE")
            self.assertIsNone(candidate.escape_choice(None, None, 1, views())[0])
            plus = views(); plus["ADVANCE"] = assessment("ESTABLISHED", 1)
            self.assertIsNone(candidate.escape_choice(None, None, 0, plus)[0])
            no_unseen = views(); no_unseen["ADVANCE"] = assessment("ESTABLISHED", -1)
            no_unseen["RETREAT"] = assessment("ESTABLISHED", -1)
            self.assertIsNone(candidate.escape_choice(None, None, 0, no_unseen)[0])
            unresolved = views(); unresolved["ADVANCE"] = assessment("UNRESOLVED_CHANGE")
            unresolved["RETREAT"] = assessment("UNRESOLVED_CHANGE")
            self.assertIsNone(candidate.escape_choice(None, None, 0, unresolved)[0])
            empirical = views(); empirical["HOLD"] = assessment("EMPIRICALLY_STABLE", relation_type="EMPIRICAL")
            self.assertIsNone(candidate.escape_choice(None, None, 0, empirical)[0])
            different = dict(count=3, relation=[0, "RETREAT"])
            with patch.object(candidate, "qualifying_suffix", return_value=different):
                self.assertEqual(candidate.escape_choice(None, None, 0, views("RETREAT"))[0], "ADVANCE")
            short = dict(count=2, relation=[0, "HOLD"])
            with patch.object(candidate, "qualifying_suffix", return_value=short):
                self.assertIsNone(candidate.escape_choice(None, None, 0, views())[0])

    def test_suffix_resets_on_state_and_fallback_identity_change(self):
        first = [row(1), row(2), row(3)]
        self.assertEqual(independent_suffix(first), (3, (0, "HOLD")))
        self.assertEqual(independent_suffix(first + [row(4, next_state=1)]), (0, None))
        changed = row(4, action="RETREAT")
        self.assertEqual(independent_suffix(first + [changed]), (1, (0, "RETREAT")))
        escaped = dict(row(4), decision_source="STAGNATION_ESCAPE", policy_route="ESCAPE")
        self.assertEqual(independent_suffix(first + [escaped]), (0, None))

    def test_signed_restart_and_one_shot_escape_without_model_call(self):
        old_override, old_study = base.scenario_override, base.STUDY
        try:
            frozen.configure()
            with TemporaryDirectory() as temporary:
                root = Path(temporary)
                with SessionStore(root / "session", False) as store, ModernMemory(root / "memory.sqlite3", True) as memory:
                    store.save(state=0, next_transaction_id=1)
                    base.execute(store, memory, "E1", "S", 0, "HOLD", "REGISTERED_SETUP", setup=True)
                    self._fallback(store, memory, 1)
                    self._fallback(store, memory, 2)
                    self.assertEqual(candidate.qualifying_suffix(store, memory), dict(count=2, relation=[0, "HOLD"]))
                with SessionStore(root / "session", True) as store, ModernMemory(root / "memory.sqlite3", False) as memory:
                    self.assertEqual(candidate.qualifying_suffix(store, memory), dict(count=2, relation=[0, "HOLD"]))
                    self._fallback(store, memory, 3)
                    self.assertEqual(candidate.qualifying_suffix(store, memory), dict(count=3, relation=[0, "HOLD"]))
                    before = len(store.records["calls"])
                    with patch.object(frozen, "canonical_action_decision", side_effect=AssertionError("model path called")):
                        action, source, route, info, assessments, suffix = promoted_decide(store, memory, object(), 4)
                    self.assertEqual((action, source, route["route"], info["status"]),
                        ("ADVANCE", "STAGNATION_ESCAPE", "ESCAPE", "NOT_CALLED"))
                    self.assertIsNone(info["call_id"])
                    self.assertEqual(suffix["count"], 3)
                    self.assertEqual(len(store.records["calls"]), before + 1)
                    self.assertEqual(store.records["calls"][-1]["kind"], "ACTION_FROZEN")
                    base.execute(store, memory, "E1", "S", 4, action, source, route, info,
                        assessments, counter_before=suffix["count"])
                    self.assertEqual(candidate.qualifying_suffix(store, memory), dict(count=0, relation=None))
                    self.assertEqual(len(store.records["events"]), len(memory.rows()))
                    self.assertTrue(all(e["record"]["authorization_status"] == "AUTHORIZED"
                        for e in store.records["events"]))
        finally:
            base.scenario_override, base.STUDY = old_override, old_study

    def _fallback(self, store, memory, index):
        context = frozen.context(store, memory, index)
        self.assertEqual(context["route"]["route"], "MODEL")
        self.assertEqual(context["assessments"]["HOLD"]["established_value"]["consequence"], 0)
        info = dict(call_id=f"UNIT:{index}", raw_output_sha256=None,
            context_tokens=0, output_tokens=0, latency_seconds=0, status="VALID")
        base.execute(store, memory, "E1", "S", index, "HOLD", "SAFE_GROUNDED_FALLBACK",
            context["route"], info, context["assessments"],
            counter_before=context["suffix"]["count"])


if __name__ == "__main__":
    unittest.main()
