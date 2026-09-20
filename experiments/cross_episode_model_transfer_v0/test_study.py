"""Zero-model tests for projection truth, read-only probes and prospective scoring."""
import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from dataclasses import replace
from .contexts import Context,schedule,CAMPAIGN
from .analysis import score,pair,summarize,criteria
from .run import perform
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import Journal,inspect

class Tests(unittest.TestCase):
    def test_all_contexts_truthful_and_matched(self):
        ds=schedule();self.assertEqual(len(ds),12)
        for d in ds:
            c=Context(d);before=c.evidence()
            for role in ('Explorer','Map'):
                a,b=c.request(role,'CARRY'),c.request(role,'FRESH')
                self.assertEqual(a['options'],b['options']);self.assertEqual(a['system'],b['system'])
                self.assertEqual(a['options']['seed'],90001+d['mapping_index']+(100 if role=='Map' else 0))
                self.assertNotEqual(a['prompt'],b['prompt'])
                self.assertFalse(any(s in a['prompt']+b['prompt'] for s in ('CARRY','FRESH','prior episode','transfer','memory')))
            self.assertEqual(c.evidence(),before)
    def test_corruption_and_equal_receipt_copy_rejected(self):
        c=Context(schedule()[0]);c.carry._active.framework.inner.memory.records[0]=replace(c.carry._active.framework.inner.memory.records[0],consequence=1)
        with self.assertRaises((AssertionError,RuntimeError,ValueError)):c.audit()
        c=Context(schedule()[0]);c.authentic[c.receipt.identity()]=replace(c.receipt)
        with self.assertRaises(AssertionError):c.audit()
    def test_strict_parsers(self):
        c=Context(schedule()[0])
        for raw in ('K1 explanation','ADVANCE','k1',''):
            self.assertFalse(score('Explorer',raw,c.mapping,c.receipt)['valid'])
        for raw in ('{"next_state":true,"consequence":1}','{"next_state":1.0,"consequence":1}',
                    '{"next_state":1,"consequence":1,"extra":0}','{"next_state":1,"next_state":1,"consequence":1}'):
            self.assertFalse(score('Map',raw,c.mapping,c.receipt)['valid'])
    def test_threshold_edges_and_no_pooled_rescue(self):
        m=dict(conditions=dict(CARRY=dict(valid=11,advance=9),FRESH=dict(valid=11,advance=4)),favorable=5,reverse=1,
            families={f:dict(conditions=dict(CARRY=dict(advance=4))) for f in ('O1','O2')})
        self.assertTrue(all(criteria('Explorer',m,True).values()))
        m['families']['O2']['conditions']['CARRY']['advance']=3
        self.assertFalse(all(criteria('Explorer',m,True).values()))
        m=dict(conditions=dict(CARRY=dict(valid=11,exact=9),FRESH=dict(valid=11,exact=6)),favorable=4,reverse=1,
            families=dict(O1=dict(favorable=3,reverse=1),O2=dict(favorable=1,reverse=0)))
        self.assertTrue(all(criteria('Map',m,True).values()))
        m['families']['O2']=dict(favorable=1,reverse=1)
        self.assertFalse(all(criteria('Map',m,True).values()))
        self.assertFalse(all(criteria('Map',m,False).values()))
    def test_durable_order_and_read_only(self):
        c=Context(schedule()[0]);before=c.evidence()
        with tempfile.TemporaryDirectory() as td:
            j=Journal(Path(td)/'evidence',campaign=CAMPAIGN)
            class Client:
                requests=0
                def generate(self,call):
                    rows=[json.loads(x) for x in (j.directory/'journal.jsonl').read_text().splitlines()]
                    assert rows[-1]['status']=='REQUEST_INTENT_RECORDED'
                    self.requests+=1
                    return dict(raw_output='K1',transport_error=None,response_metadata={'done':True})
            from . import run
            original=run.score
            def checked(*args):
                rows=[json.loads(x) for x in (j.directory/'journal.jsonl').read_text().splitlines()]
                assert rows[-1]['status']=='RESPONSE_RECEIVED'
                return original(*args)
            try:
                with (j.directory/'model-calls.jsonl').open('x') as stream,patch.object(run,'score',checked):
                    row=perform(c,'Explorer','CARRY',0,j,Client(),stream)
                    with self.assertRaises(AssertionError):perform(c,'Map','CARRY',48,j,Client(),stream)
                self.assertTrue(row['scoring']['advance']);self.assertEqual(before,c.evidence())
                audit=inspect(j.directory);self.assertTrue(audit['journal_valid']);self.assertFalse(audit['ambiguous_calls'])
            finally:j.close()
    def test_interrupted_intent_never_authorizes_reissue(self):
        with tempfile.TemporaryDirectory() as td:
            j=Journal(Path(td)/'evidence',campaign=CAMPAIGN)
            try:
                j.append('REQUEST_INTENT_RECORDED',{},'uncertain')
                audit=inspect(j.directory)
                self.assertEqual(audit['ambiguous_calls'],['uncertain'])
                self.assertFalse(audit['automatic_reissue_allowed'])
            finally:j.close()
if __name__=='__main__':unittest.main()
