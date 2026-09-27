"""Boundary tests, independent parser domain matrix, protected staging checks."""
from copy import deepcopy
import json
import unittest
from experiments.base_framework_v0.framework import MapModel
from .adapter import MapProposalAdapter, parse, INVALID
from .gate import run


class MapTests(unittest.TestCase):
    def test_zero_call_authority_gate(self):
        result=run()
        self.assertEqual(result["summary"]["gate"],"PASS")
        self.assertEqual(result["summary"]["actual_model_calls"],0)
        cases={r["case"]:r["probe"] for r in result["cases"]}
        for name in ("wrong_old","wrong_state_and_consequence"):
            p=cases[name]
            self.assertTrue(p["latched_before_execution"])
            self.assertFalse(p["measurement_matches"])
            self.assertEqual(p["receipt"]["realized_consequence"],-1)
            self.assertEqual(p["after"]["memory"][-1]["consequence"],-1)
            self.assertEqual(p["after"]["map"]["state"],1)
        self.assertEqual(cases["measure_recovery_rejected"]["before"],cases["measure_recovery_rejected"]["after"])

    def test_finite_schema(self):
        for n in range(4):
            for c in (-1,0,1):
                p=dict(next_state=n,consequence=c)
                self.assertEqual(parse(json.dumps(p)),p)
        for raw in (*INVALID,'{"next_state":1,"consequence":1,"consequence":-1}',
                    'null','[]','"HOLD"','{"next_state":1,"consequence":false}',
                    '{"next_state":1,"consequence":1.0}','{"next_state":1,"consequence":NaN}'):
            with self.subTest(raw=raw),self.assertRaises(ValueError): parse(raw)

    def test_staged_protected_state_isolation(self):
        a=MapProposalAdapter(MapModel(1,1001),lambda p,s:'{"next_state":1,"consequence":-1}',"bounded",50001)
        b=deepcopy(a);b.quarantine_incumbent();b.commit(2,1001)
        self.assertEqual(a.current.state,1)
        self.assertEqual(a.current.version,0)
        self.assertTrue(a.current.valid)
        self.assertEqual(a.quarantine,[])
        self.assertEqual(b.current.state,2)
        self.assertEqual(b.current.version,1)

    def test_registered_history_and_probe(self):
        from .campaign import registration, probe
        plan,_=registration()
        self.assertEqual(len(plan),144)
        for family in ("O1","O2"):
            cell=[d for d in plan if d["family"]==family and d["arm"]=="SHIFT" and d["stage"]=="H2"]
            self.assertEqual(sorted(d["seed"] for d in cell),list(range(50001,50013)))
            self.assertEqual({m:sum(d["mapping_index"]==m for d in cell) for m in range(6)},dict.fromkeys(range(6),2))
        d=next(d for d in plan if d["arm"]=="SHIFT" and d["stage"]=="H2")
        for raw in ('{"next_state":1,"consequence":-1}','{"next_state":0,"consequence":1}','{'):
            class Synthetic:
                def generate(self,prompt,seed): return raw,{"synthetic":True}
            calls=[];row=probe(Synthetic(),d,None,calls.append)
            self.assertEqual(len(calls),1)
            self.assertEqual(row["probe"]["errors"],[])
            self.assertTrue(row["history_retained"])
            self.assertEqual(row["probe"]["authorization"]["committed"],raw!='{')

    def test_family_thresholds_and_global_validity(self):
        from .campaign import schedule
        from .analysis import summarize
        rows=[]
        for d in schedule():
            value=-1 if d["arm"]=="SHIFT" and d["stage"]=="H2" else 1
            pred=dict(next_state=1,consequence=value)
            outcome=dict(next_state=1,consequence=1 if d["arm"]=="CONTROL" else -1)
            rows.append(dict(descriptor=d,valid=True,history_retained=True,evaluator_outcome=outcome,
                model_call=dict(parsed_prediction=pred),probe=dict(errors=[],latched_before_execution=True,
                receipt_unchanged=True,metric_delta={},measurement_matches=pred==outcome,
                authorization=dict(committed=True,recovery_authorized=False),observations=[],
                bounds=dict(memory=8,pairs=8,packages=8,trace=24,pending_authentic=1,map_quarantine=0,memory_quarantine=0))))
        self.assertTrue(summarize(rows,[])["overall"].endswith(" REPLICATED"))
        d=next(r for r in rows if r["descriptor"]["family"]=="O2")
        d["valid"]=False;d["model_call"]["parsed_prediction"]=None
        result=summarize(rows,[])
        self.assertTrue(result["overall"].endswith("NOT ESTABLISHED"))
        self.assertEqual(result["families"]["O1"]["revision"],"NOT_ESTABLISHED")

if __name__=="__main__": unittest.main()
