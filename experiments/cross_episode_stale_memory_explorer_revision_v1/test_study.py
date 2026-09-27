"""Zero-inference checks for fixed gates, parser, provenance and durable ordering."""
import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from dataclasses import replace
from .contexts import Context,schedule,CAMPAIGN
from .analysis import score,criteria,validity_gate,trajectories
from .run import perform
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import Journal,inspect
class Tests(unittest.TestCase):
    def test_registered_schedule_and_prompt_pairs(self):
        plan=schedule();self.assertEqual(len(plan),144);pairs={}
        with patch('socket.socket',side_effect=AssertionError('zero inference')):
            for d in plan:
                c=Context(d);b=c.request();self.assertEqual(b['options']['seed'],93001+d['schedule'])
                self.assertEqual(c.audit()['Memory_length'],6+d['stage_index'])
                pairs.setdefault((d['family'],d['schedule'],d['stage']),{})[d['arm']]=b
        for key,pair in pairs.items():
            a,b=pair['CONTROL'],pair['CHANGED'];self.assertEqual(a['options'],b['options']);self.assertEqual(a['system'],b['system'])
            if key[-1]=='P0':self.assertEqual(a,b)
            else:
                av,bv=json.loads(a['prompt']),json.loads(b['prompt'])
                for row in bv['actions']:
                    if len(row['verified_outcomes'])>1 and row['verified_outcomes'][0]==1:row['verified_outcomes']=[1]*len(row['verified_outcomes'])
                self.assertEqual(av,bv)
        self.assertEqual([d['family'] for d in plan[:12]],['O1']*6+['O2']*6)
        self.assertEqual([d['family'] for d in plan[12:24]],['O2']*6+['O1']*6)
    def test_strict_parser_and_hidden_P0(self):
        m=schedule()[0]['mapping'];alias=next(k for k,v in m.items() if v=='HOLD')
        s=score(alias,m,'RETREAT');self.assertTrue(s['old']);self.assertFalse(s['current_best'])
        for raw in ('HOLD','{"action":"'+alias+'"}',alias+' because',alias+' K3','UNKNOWN',''):
            self.assertFalse(score(raw,m,'HOLD')['valid'])
    def test_validity_threshold_edges(self):
        self.assertTrue(validity_gate(140,[11]*4+[12]*8))
        self.assertFalse(validity_gate(139,[11]*5+[12]*7))
        self.assertFalse(validity_gate(142,[10]+[12]*11))
        self.assertTrue(validity_gate(144,[12]*12))
    def test_all_family_gates_and_no_pooling(self):
        c={'CHANGED/P0':dict(counts=dict(HOLD=10)),'CHANGED/P2':dict(counts=dict(RETREAT=9)),'CONTROL/P2':dict(counts=dict(HOLD=9))};p=dict(favorable=8,reverse=1)
        self.assertTrue(all(criteria(c,p,True,True,True,True).values()))
        for key in ('CHANGED/P0','CHANGED/P2','CONTROL/P2'):
            n=next(iter(c[key]['counts']));c[key]['counts'][n]-=1
            self.assertFalse(all(criteria(c,p,True,True,True,True).values()));c[key]['counts'][n]+=1
        self.assertFalse(all(criteria(c,p,True,False,True,True).values()));self.assertFalse(all(criteria(c,p,True,True,True,None).values()))
    def test_latency_exclusion_reversal_and_invalid(self):
        rows=[]
        for d in schedule():
            a=('HOLD','RETREAT','HOLD')[d['stage_index']] if d['schedule'] else 'RETREAT'
            raw=next(k for k,v in d['mapping'].items() if v==a)
            if d['schedule']==2 and d['stage']=='P1':raw='INVALID'
            rows.append(dict(descriptor=d,scoring=score(raw,d['mapping'],'RETREAT')))
        t=trajectories(rows);self.assertEqual(t[0]['latency'],'excluded_no_HOLD_P0')
        self.assertEqual(t[1]['latency'],'P1');self.assertEqual(t[1]['path_classes']['CHANGED'],'RETREAT_then_HOLD')
        self.assertEqual(t[2]['path_classes']['CHANGED'],'invalid_path')
    def test_old_history_corruption_rejected(self):
        c=Context(schedule()[0]);mem=c.c._active.framework.inner.memory;mem.records[0]=replace(mem.records[0],consequence=-1)
        with self.assertRaises((AssertionError,ValueError,RuntimeError)):c.audit()
    def test_durable_order_no_reissue_no_execution(self):
        c=Context(schedule()[0]);before=c.evidence()
        with tempfile.TemporaryDirectory() as td:
            j=Journal(Path(td)/'evidence',campaign=CAMPAIGN)
            class Client:
                requests=0
                def generate(self,call):
                    assert json.loads((j.directory/'journal.jsonl').read_text().splitlines()[-1])['status']=='REQUEST_INTENT_RECORDED'
                    self.requests+=1;return dict(raw_output='K2',transport_error=None,response_metadata={'done':True})
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
