"""Direct stage/world construction, frozen representation and criteria tests."""
from copy import deepcopy
import unittest
from experiments.model_map_proposal_v0.adapter import SYSTEM, OPTIONS
from .fixture import fixture, HoldWorld, EXPECTED
from .campaign import registration, probe, controls, schedule
from .preflight import run
from .analysis import summarize


class StageTests(unittest.TestCase):
    def test_all_histories_and_receipt_independence(self):
        result,_=run()
        self.assertEqual(result["summary"]["preflight"],"PASS")
        self.assertEqual(result["summary"]["actual_model_calls"],0)
        self.assertEqual(result["summary"]["constructed_histories"],EXPECTED)
        self.assertEqual(result["summary"]["maximum_probe_memory"],5)

    def test_switch_is_external_after_two_completed_events(self):
        world=HoldWorld()
        with self.assertRaises(ValueError):world.switch()
        self.assertEqual(world.execute(1001,1,"HOLD").consequence,1)
        with self.assertRaises(ValueError):world.switch()
        prior=world.execute(1001,2,"HOLD")
        self.assertEqual(prior.consequence,1)
        world.switch()
        self.assertEqual(prior.consequence,1)
        self.assertEqual(world.execute(1001,3,"HOLD").consequence,-1)
        self.assertEqual(world.execute(1001,4,"HOLD").consequence,-1)
        with self.assertRaises(ValueError):world.switch()

    def test_registered_projection_and_matching(self):
        plan,_=registration()
        self.assertEqual(len(plan),144)
        for family in ("O1","O2"):
            for arm in ("CONTROL","SHIFT"):
                for stage in ("P0","P1","P2"):
                    cell=[d for d in plan if (d["family"],d["arm"],d["stage"])==(family,arm,stage)]
                    self.assertEqual(sorted(d["seed"] for d in cell),list(range(60001,60013)))
                    self.assertEqual({m:sum(d["mapping_index"]==m for d in cell) for m in range(6)},dict.fromkeys(range(6),2))
                    for d in cell:
                        self.assertEqual(set(d["payload"]),{"state","target_action","VERIFIED_CHRONOLOGICAL_HISTORY"})
                        for token in ("HOLD","ADVANCE","RETREAT","CONTROL","SHIFT","Recovery","Measure","prediction"):
                            self.assertNotIn(token,d["exact_prompt"])
        self.assertEqual(OPTIONS['num_predict'],32)
        self.assertTrue(SYSTEM.startswith('Predict the next externally realized outcome'))

    def test_wrong_prediction_and_same_admission_controls(self):
        plan,_=registration()
        d=next(d for d in plan if d["arm"]=="SHIFT" and d["stage"]=="P2")
        class Wrong:
            def generate(self,prompt,seed):return '{"next_state":2,"consequence":1}',{"synthetic":True}
        row=probe(Wrong(),d,None,lambda x:None)
        self.assertFalse(row["probe"]["measurement_matches"])
        self.assertEqual(row["probe"]["after"]["memory"][-1]["consequence"],-1)
        self.assertTrue(row["history_retained"])
        self.assertEqual(row["probe"]["errors"],[])
        outputs=controls(plan)
        self.assertEqual(len(outputs),18)
        self.assertTrue(all(not r["probe"]["authorization"]["executed"] and not r["probe"]["errors"] for r in outputs))

    def test_frozen_family_and_global_gates(self):
        rows=[]
        for d in schedule():
            value=-1 if d["arm"]=="SHIFT" and d["stage"]=="P2" else 1
            pred=dict(next_state=1,consequence=value)
            outcome=dict(next_state=1,consequence=1 if d["arm"]=="CONTROL" else -1)
            rows.append(dict(descriptor=d,valid=True,history_retained=True,evaluator_outcome=outcome,
                model_call=dict(parsed_prediction=pred),probe=dict(errors=[],latched_before_execution=True,
                receipt_unchanged=True,metric_delta={},measurement_matches=pred==outcome,
                authorization=dict(committed=True,recovery_authorized=False),observations=[],
                bounds=dict(memory=5,pairs=5,packages=5,trace=15,pending_authentic=1,map_quarantine=0,memory_quarantine=0))))
        self.assertEqual(summarize(rows,[])["overall"],"ESTABLISHED-PRIOR MAP REVISION REPLICATED")
        altered=deepcopy(rows)
        for row in altered:
            if row["descriptor"]["family"]=="O2" and row["descriptor"]["stage"]=="P0":
                row["model_call"]["parsed_prediction"]["next_state"]=2
        result=summarize(altered,[])
        self.assertEqual(result["families"]["O1"]["revision"],"SUPPORTED")
        self.assertEqual(result["families"]["O2"]["revision"],"NOT_ESTABLISHED")
        self.assertEqual(result["overall"],"ESTABLISHED-PRIOR MAP REVISION NOT ESTABLISHED")
        rows[0]["valid"]=False;rows[0]["model_call"]["parsed_prediction"]=None
        self.assertTrue(all(f["revision"]=="NOT_ESTABLISHED" for f in summarize(rows,[])["families"].values()))

if __name__=="__main__":unittest.main()
