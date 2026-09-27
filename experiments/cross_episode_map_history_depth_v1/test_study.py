"""Zero-inference checks for depth truth, frozen gates and durable read-only probes."""
import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from dataclasses import replace
from .contexts import Context,schedule,CAMPAIGN
from .analysis import score,criteria
from .run import perform
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import Journal,inspect

class Tests(unittest.TestCase):
    def test_all_depths_authentic_and_only_history_differs(self):
        ds=schedule();self.assertEqual(len(ds),12)
        for d in ds:
            c=Context(d);before=c.evidence();requests=[c.request(k) for k in ('D0','D1','D2')]
            for r in requests:
                self.assertEqual(r['options'],requests[0]['options']);self.assertEqual(r['system'],requests[0]['system'])
                self.assertEqual(r['options']['seed'],91001+d['mapping_index'])
                self.assertFalse(any(k in r['prompt'] for k in ('D0','D1','D2','CARRY','FRESH','UNTRIED','memory','confidence')))
            shown=[json.loads(r['prompt']) for r in requests]
            self.assertEqual([len(v['VERIFIED_CHRONOLOGICAL_HISTORY']) for v in shown],[0,1,2])
            self.assertEqual(shown[1]['VERIFIED_CHRONOLOGICAL_HISTORY'],shown[2]['VERIFIED_CHRONOLOGICAL_HISTORY'][:1])
            self.assertEqual(c.carries['D2']['after']['protected']['memory'][1]['action'],'RETREAT')
            self.assertEqual(c.evidence(),before)
    def test_receipt_and_memory_corruption_rejected(self):
        c=Context(schedule()[0]);v=c.carries['D2'];v['controller']._active.framework.inner.memory.records[0]=replace(v['controller']._active.framework.inner.memory.records[0],consequence=0)
        with self.assertRaises((AssertionError,RuntimeError,ValueError)):c.audit()
        c=Context(schedule()[0]);v=c.carries['D1'];v['authentic'][c.receipt.identity()]=replace(c.receipt)
        with self.assertRaises(AssertionError):c.audit()
    def test_parser_unchanged_strict(self):
        c=Context(schedule()[0])
        for raw in ('{"next_state":true,"consequence":1}','{"next_state":1.0,"consequence":1}',
                    '{"next_state":1,"consequence":1,"extra":0}','{"next_state":1,"next_state":1,"consequence":1}',
                    '{"next_state":4,"consequence":1}','{"next_state":1,"consequence":1} explanation'):
            self.assertFalse(score(raw,c.receipt)['valid'])
    def test_frozen_edges_no_component_or_family_rescue(self):
        m=dict(conditions={k:dict(valid=11,exact=n) for k,n in [('D0',4),('D1',2),('D2',9)]},
            comparisons=dict(D2_vs_D0=dict(favorable=5,reverse=1)),
            families={f:dict(comparisons=dict(D2_vs_D0=dict(favorable=2,reverse=0))) for f in ('O1','O2')})
        self.assertTrue(all(criteria(m,True,True,True).values()))
        self.assertFalse(all(criteria(m,True,True,None).values()))
        m['conditions']['D2']['exact']=8;m['conditions']['D2']['next_state']=12
        self.assertFalse(all(criteria(m,True,True,True).values()))
        m['conditions']['D2']['exact']=9;m['families']['O2']['comparisons']['D2_vs_D0']['reverse']=2
        self.assertFalse(all(criteria(m,True,True,True).values()))
    def test_durable_order_read_only_and_budget(self):
        c=Context(schedule()[0]);before=c.evidence()
        with tempfile.TemporaryDirectory() as td:
            j=Journal(Path(td)/'evidence',campaign=CAMPAIGN)
            class Client:
                requests=0
                def generate(self,call):
                    rows=[json.loads(x) for x in (j.directory/'journal.jsonl').read_text().splitlines()]
                    assert rows[-1]['status']=='REQUEST_INTENT_RECORDED'
                    self.requests+=1
                    return dict(raw_output='{"next_state":1,"consequence":1}',transport_error=None,response_metadata={'done':True})
            from . import run
            original=run.score
            def checked(*args):
                rows=[json.loads(x) for x in (j.directory/'journal.jsonl').read_text().splitlines()]
                assert rows[-1]['status']=='RESPONSE_RECEIVED'
                return original(*args)
            try:
                with (j.directory/'model-calls.jsonl').open('x') as stream,patch.object(run,'score',checked):
                    row=perform(c,'D1',0,j,Client(),stream)
                    with self.assertRaises(AssertionError):perform(c,'D0',36,j,Client(),stream)
                    with self.assertRaises(RuntimeError):perform(c,'D1',0,j,Client(),stream)
                self.assertTrue(row['scoring']['exact']);self.assertEqual(before,c.evidence())
                self.assertTrue(inspect(j.directory)['journal_valid'])
            finally:j.close()
    def test_interruption_never_reissues(self):
        with tempfile.TemporaryDirectory() as td:
            j=Journal(Path(td)/'evidence',campaign=CAMPAIGN)
            try:
                j.append('REQUEST_INTENT_RECORDED',{},'uncertain');audit=inspect(j.directory)
                self.assertEqual(audit['ambiguous_calls'],['uncertain']);self.assertFalse(audit['automatic_reissue_allowed'])
            finally:j.close()
if __name__=='__main__':unittest.main()
