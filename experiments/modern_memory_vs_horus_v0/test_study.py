import unittest

from .protocol import (ISSUED_REQUEST_BUDGET, PERTURBATION_AFTER_EVENT,
                       RESTART_AFTER_EVENT, STAGE_A, STAGE_B_DECISIONS)


class StudyTests(unittest.TestCase):
    def test_frozen_schedule_and_budget(self):
        self.assertEqual(len(STAGE_A), 12)
        self.assertEqual([row["phase"] for row in STAGE_A].count("STABLE"), 4)
        self.assertEqual([row["phase"] for row in STAGE_A].count("CHANGE"), 4)
        self.assertEqual([row["phase"] for row in STAGE_A].count("RESTORATION"), 4)
        self.assertEqual(RESTART_AFTER_EVENT, 6)
        self.assertEqual(PERTURBATION_AFTER_EVENT, 6)
        self.assertEqual(STAGE_B_DECISIONS, 4)
        self.assertEqual(ISSUED_REQUEST_BUDGET, 255)


if __name__ == "__main__": unittest.main()
