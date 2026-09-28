"""Pure preregistered world schedule checks; no model or world execution."""
import unittest
from .worker import override,GROUPS,CONTROL_SETUP

class ScenarioTests(unittest.TestCase):
    def test_family_and_relation_variation(self):
        self.assertEqual(len(GROUPS),4)
        self.assertEqual(len(CONTROL_SETUP),6)
        self.assertEqual(override('R1',3,'HOLD',1,4),(3,0))
        self.assertEqual(override('R4',3,'HOLD',1,4),(3,1))
        self.assertEqual(override('R3',1,'HOLD',1,4),(1,-1))
        self.assertEqual(override('R5',2,'HOLD',1,4),(2,0))
        self.assertEqual(override('R6',3,'RETREAT',1,4),(3,0))
    def test_resets_and_controls(self):
        self.assertEqual(override('R6',3,'HOLD',4,3),(3,0))
        self.assertEqual(override('R6',3,'HOLD',5,4),(0,0))
        self.assertEqual(override('C1',3,'ADVANCE',1,1),(3,1))
        self.assertEqual(override('C3',3,'HOLD',1,0),(3,1))
        self.assertEqual(override('C3',3,'HOLD',2,0),(3,-1))
        self.assertEqual(override('C5',2,'ADVANCE',2,1),(3,0))
        self.assertEqual(override('C6',3,'ADVANCE',4,3),(2,0))

if __name__=='__main__':unittest.main()
