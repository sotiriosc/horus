"""Zero-inference tests of mean targets, pairing, fixed gates and durability."""
import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from .contexts import Context,schedule,CAMPAIGN,mean_policy
from .analysis import score,criteria,pairs,sensitivity
from .run import perform
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import Journal,inspect
class Tests(unittest.TestCase):
    def test_full_fixture_schedule_and_AB_identity(self):
        plan=schedule();self.assertEqual(len(plan),96);matched={}
        with patch('socket.socket',side_effect=AssertionError('zero inference')):
            for d in plan:
                c=Context(d);b=c.request();self.assertEqual(b['options']['seed'],94001+d['schedule'])
                self.assertEqual(c.audit()['Memory_length'],8)
                matched.setdefault((d['family'],d['schedule'],d['arm']),{})[d['condition']]=b
        for key,p in matched.items():
            a,b=dict(p['A']),dict(p['B']);self.assertNotEqual(a.pop('system'),b.pop('system'));self.assertEqual(a,b)
        self.assertEqual(len(matched),48)
        self.assertEqual([d['family'] for d in plan[:8]],['O1']*4+['O2']*4)
        self.assertEqual([d['family'] for d in plan[8:16]],['O2']*4+['O1']*4)
    def test_exact_means_and_no_ties(self):
        d=next(d for d in schedule() if d['arm']=='CHANGED');c=Context(d)
        self.assertEqual(c.policy['means']['HOLD'],dict(numerator=-1,denominator=3));self.assertEqual(c.target,'RETREAT')
        view=json.loads(json.dumps(c.view))
        for row in view['actions']:
            if d['mapping'][row['action']]=='HOLD':row['verified_outcomes']=[1,-1]
        with self.assertRaisesRegex(ValueError,'tied'):mean_policy(view,d['mapping'])
        view['actions'][0]['verified_outcomes']='UNTRIED'
        with self.assertRaises(ValueError):mean_policy(view,d['mapping'])
    def test_strict_alias_parser(self):
        m=schedule()[0]['mapping'];alias=next(k for k,v in m.items() if v=='HOLD')
        self.assertTrue(score(alias,m,'HOLD')['mean_policy_correct'])
        for raw in ('HOLD','{"action":"'+alias+'"}',alias+' because',alias+' K3','UNKNOWN',''):
            self.assertFalse(score(raw,m,'HOLD')['valid'])
    def test_thresholds_and_no_pooling(self):
        cs={'CONTROL/B':dict(calls=12,valid=12,counts=dict(HOLD=10)),'CHANGED/B':dict(calls=12,valid=11,counts=dict(RETREAT=10))};p=dict(favorable=8,reverse=1)
        self.assertTrue(all(criteria(cs,p,True,True).values()))
        self.assertFalse(all(criteria(cs,p,True,None).values()))
        for cell,key in (('CONTROL/B','HOLD'),('CHANGED/B','RETREAT')):
            cs[cell]['counts'][key]-=1;self.assertFalse(all(criteria(cs,p,True,True).values()));cs[cell]['counts'][key]+=1
        cs['CHANGED/B']['valid']=10;self.assertFalse(all(criteria(cs,p,True,True).values()))
        cs['CHANGED/B']['valid']=11;p['favorable']=7;self.assertFalse(all(criteria(cs,p,True,True).values()))
        p['favorable']=8;p['reverse']=2;self.assertFalse(all(criteria(cs,p,True,True).values()))
    def test_invalid_pairs_remain_explicit(self):
        rows=[]
        for d in schedule():
            target='HOLD' if d['arm']=='CONTROL' else 'RETREAT';token=next(k for k,v in d['mapping'].items() if v==target)
            raw=token if d['condition']=='B' else 'INVALID'
            rows.append(dict(descriptor=d,scoring=score(raw,d['mapping'],target),intent=dict(audit=dict(policy_calculation=dict(unique_target=target)))))
        p=pairs(rows)[0];self.assertTrue(p['favorable']);self.assertTrue(p['invalid_in_pair']);self.assertFalse(p['favorable_both_valid'])
        self.assertEqual(p['sensitivity'],'invalid_in_pair')
        self.assertEqual(sensitivity('HOLD','RETREAT'),'HOLD_to_RETREAT');self.assertEqual(sensitivity('HOLD','HOLD'),'same_action')
    def test_authenticated_old_history_cannot_be_rewritten(self):
        from dataclasses import replace
        c=Context(schedule()[0]);mem=c.fixture.c._active.framework.inner.memory;mem.records[0]=replace(mem.records[0],consequence=-1)
        with self.assertRaises((AssertionError,ValueError,RuntimeError)):c.audit()
    def test_write_ahead_and_no_reissue(self):
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
                    c.d={**c.d,'index':96}
                    with self.assertRaises(AssertionError):perform(c,j,Client(),stream)
                c.d=schedule()[0];self.assertEqual(c.evidence(),before);self.assertTrue(inspect(j.directory)['journal_valid'])
            finally:j.close()
if __name__=='__main__':unittest.main()
