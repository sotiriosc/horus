"""Zero-inference schedule, authenticity, gate, latency and write-ahead checks."""
import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from .contexts import Context,schedule,CAMPAIGN
from .analysis import score,criteria,path_kind,trajectories
from .run import perform
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import Journal,inspect
class Tests(unittest.TestCase):
    def test_full_schedule_and_matched_authentic_prompts(self):
        plan=schedule();self.assertEqual(len(plan),144);requests={}
        with patch('socket.socket',side_effect=AssertionError('zero inference')):
            for d in plan:
                c=Context(d);body=c.request();self.assertEqual(body['options']['seed'],92001+d['schedule'])
                key=(d['family'],d['schedule'],d['stage']);requests.setdefault(key,{})[d['arm']]=body
                self.assertEqual(len(json.loads(body['prompt'])['VERIFIED_CHRONOLOGICAL_HISTORY']),2+d['stage_index'])
                self.assertEqual(c.audit()['native_state_Recovery_calls'],d['stage_index'] if d['arm']=='CHANGED' else 0)
        for key,pair in requests.items():
            a,b=pair['CONTROL'],pair['CHANGED'];self.assertEqual(a['options'],b['options']);self.assertEqual(a['system'],b['system'])
            if key[-1]=='P0':self.assertEqual(a,b)
            else:
                av,bv=json.loads(a['prompt']),json.loads(b['prompt'])
                for row in bv['VERIFIED_CHRONOLOGICAL_HISTORY']:row['consequence']=1
                self.assertEqual(av,bv)
        self.assertEqual([d['family'] for d in plan[:12]],['O1']*6+['O2']*6)
        self.assertEqual([d['family'] for d in plan[12:24]],['O2']*6+['O1']*6)
    def test_strict_parser_and_P0_scoring_separation(self):
        current=dict(next_state=1,consequence=-1);s=score('{"next_state":1,"consequence":1}',current)
        self.assertTrue(s['old_exact']);self.assertFalse(s['current_exact']);self.assertTrue(s['next_state_correct'])
        for raw in ('{"next_state":true,"consequence":1}','{"next_state":1.0,"consequence":1}','{"next_state":1,"consequence":1,"x":0}',
                    '{"next_state":1,"next_state":1,"consequence":1}','{"next_state":1,"consequence":"1"}','{}'):
            self.assertFalse(score(raw,current)['valid'])
    def test_all_global_valid_and_old_prior_gates_required(self):
        cells={'CHANGED/P0':dict(old_exact=10),'CHANGED/P2':dict(new_exact=9),'CONTROL/P2':dict(old_exact=9)}
        pairs=dict(favorable=8,reverse=1)
        self.assertTrue(all(criteria(cells,pairs,True,True,True,True).values()))
        self.assertFalse(all(criteria(cells,pairs,True,False,True,True).values()))
        self.assertFalse(all(criteria(cells,pairs,True,True,True,None).values()))
        cells['CHANGED/P0']['old_exact']=9
        self.assertFalse(all(criteria(cells,pairs,True,True,True,True).values()))
    def test_latency_exclusion_and_reversal(self):
        rows=[]
        for d in schedule():
            category=['old','new','old'][d['stage_index']] if d['schedule']!=0 else ['new','new','new'][d['stage_index']]
            s=score(json.dumps(dict(next_state=1,consequence=1 if category=='old' else -1)),dict(next_state=1,consequence=-1))
            rows.append(dict(descriptor=d,scoring=s))
        ts=trajectories(rows);self.assertEqual(ts[0]['latency'],'excluded_no_old_P0')
        self.assertEqual(ts[1]['latency'],'P1');self.assertEqual(ts[1]['path_classes']['CHANGED'],'new_then_old')
    def test_corrupted_history_rejected(self):
        from dataclasses import replace
        c=Context(schedule()[0]);mem=c.c._active.framework.inner.memory
        mem.records[0]=replace(mem.records[0],consequence=-1)
        with self.assertRaises((AssertionError,ValueError,RuntimeError)):c.audit()
    def test_write_ahead_order_budget_no_mutation(self):
        c=Context(schedule()[0]);before=c.evidence()
        with tempfile.TemporaryDirectory() as td:
            j=Journal(Path(td)/'evidence',campaign=CAMPAIGN)
            class Client:
                requests=0
                def generate(self,call):
                    assert json.loads((j.directory/'journal.jsonl').read_text().splitlines()[-1])['status']=='REQUEST_INTENT_RECORDED'
                    self.requests+=1;return dict(raw_output='{"next_state":1,"consequence":1}',transport_error=None,response_metadata={'done':True})
            from . import run
            original=run.score
            def checked(*args):
                assert json.loads((j.directory/'journal.jsonl').read_text().splitlines()[-1])['status']=='RESPONSE_RECEIVED'
                return original(*args)
            try:
                with (j.directory/'model-calls.jsonl').open('x') as stream,patch.object(run,'score',checked):
                    perform(c,j,Client(),stream)
                    with self.assertRaises(RuntimeError):perform(c,j,Client(),stream)
                    c.d={**c.d,'index':144}
                    with self.assertRaises(AssertionError):perform(c,j,Client(),stream)
                c.d=schedule()[0];self.assertEqual(c.evidence(),before);self.assertTrue(inspect(j.directory)['journal_valid'])
            finally:j.close()
if __name__=='__main__':unittest.main()
