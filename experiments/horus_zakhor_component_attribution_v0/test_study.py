import tempfile
import unittest
from pathlib import Path

from .preflight import main as preflight
from .study import CONDITIONS, STAGE_A, consequence, next_state


class AttributionTests(unittest.TestCase):
    def test_preflight_is_zero_inference(self):
        self.assertEqual(preflight()["inference_calls"], 0)

    def test_factorial(self):
        self.assertEqual(set(CONDITIONS), {"F", "H", "Z", "HZ"})
        self.assertEqual(len(set(CONDITIONS.values())), 4)

    def test_workload_has_change_and_restoration(self):
        phases = {row[2] for row in STAGE_A}
        self.assertEqual(phases, {"stable", "change", "restoration"})
        self.assertEqual(consequence(1, "ADVANCE", "stable"), -1)
        self.assertEqual(consequence(1, "ADVANCE", "change"), 1)
        self.assertEqual(consequence(1, "ADVANCE", "restoration"), -1)

    def test_next_state_is_common_and_deterministic(self):
        self.assertEqual(next_state(1, "ADVANCE"), 2)
        self.assertEqual(next_state(1, "HOLD"), 1)
        self.assertEqual(next_state(1, "RETREAT"), 0)


if __name__ == "__main__":
    unittest.main()
