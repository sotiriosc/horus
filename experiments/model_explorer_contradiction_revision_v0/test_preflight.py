"""Bounded overlay/projection checks; no model or synthetic model responses."""

from dataclasses import asdict
import copy
import unittest

from experiments.base_framework_v1.hidden_oracle import TrueWorldOracle
from experiments.base_framework_v2.framework import EvidenceProvenanceFramework
from .overlay import ConsequenceOverlay, changed_consequence
from .preflight import SEQUENCE, chronological_projection, step


class PreflightTests(unittest.TestCase):
    def test_overlay_preserves_all_transitions_and_unrelated_consequences(self):
        for state in range(4):
            for action in ("ADVANCE","HOLD","RETREAT"):
                original=TrueWorldOracle(state).execute(1001,4,action)
                self.assertEqual(changed_consequence(original,False),original)
                actual=changed_consequence(original,True)
                expected=asdict(original)
                if state==1 and action in ("HOLD","ADVANCE"):
                    expected["consequence"]=-1 if action=="HOLD" else 1
                self.assertEqual(asdict(actual),expected)

    def test_switch_occurs_after_three_real_world_executions(self):
        histories={}
        for arm in ("CONTROL","SHIFT"):
            world=ConsequenceOverlay(arm)
            events=[world.execute(1001,i,action) for i,action in enumerate(SEQUENCE,1)]
            histories[arm]=events
            self.assertEqual([e.pre_state for e in events],[1,1,2,1,1,2,1])
            self.assertEqual(world.state,1)
        self.assertEqual(histories["CONTROL"][:3],histories["SHIFT"][:3])
        self.assertEqual([e.consequence for e in histories["CONTROL"]],[1,-1,1,1,-1,1,1])
        self.assertEqual([e.consequence for e in histories["SHIFT"]],[1,-1,1,-1,1,1,-1])

    def test_chronology_filters_navigation_without_rewriting_memory(self):
        system=EvidenceProvenanceFramework(initial_state=1,epoch=1001)
        world=ConsequenceOverlay("CONTROL")
        for action in SEQUENCE:
            row=step(system,world,action)
            self.assertFalse(row["integrity_errors"])
        records=[asdict(r) for r in system.memory.records];before=copy.deepcopy(records)
        projection=chronological_projection(1,records,{"K1":"ADVANCE","K2":"HOLD","K3":"RETREAT"})
        self.assertEqual([r["transaction_id"] for r in projection],[1,2,4,5,7])
        self.assertEqual([r["surface_action"] for r in projection],["K2","K1","K2","K1","K2"])
        self.assertEqual([r["consequence"] for r in projection],[1,-1,1,-1,1])
        self.assertEqual(records,before)
        self.assertEqual(len(system.memory.records),7)


if __name__=="__main__":unittest.main()
