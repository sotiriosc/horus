import unittest

from .harness import CALL_BUDGET, EVENTS
from .preflight import main as preflight


class TrialTests(unittest.TestCase):
    def test_protected_preflight_without_inference(self):
        result = preflight()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["inference_calls"], 0)
        self.assertTrue(all(result["checks"].values()))

    def test_schedule_and_budget(self):
        self.assertEqual(CALL_BUDGET, 48)
        self.assertEqual(len(EVENTS), 24)
        self.assertEqual([row["phase"] for row in EVENTS].count("STABLE"), 6)
        self.assertEqual([row["phase"] for row in EVENTS].count("CHANGE"), 10)
        self.assertEqual([row["phase"] for row in EVENTS].count("RESTORATION"), 8)


if __name__ == "__main__": unittest.main()
