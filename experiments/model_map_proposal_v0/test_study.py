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

if __name__=="__main__": unittest.main()
