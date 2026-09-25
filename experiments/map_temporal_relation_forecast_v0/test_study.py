import json,unittest
from unittest.mock import patch
from .contexts import Context,schedule,SEQUENCES
from experiments.model_map_proposal_v0.adapter import parse,INVALID
class Tests(unittest.TestCase):
    def context(self,arm='P'):return Context(next(d for d in schedule() if d['arm']==arm))
    def test_schedule(self):
        ds=schedule();self.assertEqual(len(ds),96)
        for f in ('O1','O2'):
            for j in range(12):
                rs=[d for d in ds if d['family']==f and d['schedule']==j]
                self.assertEqual({d['arm'] for d in rs},set(SEQUENCES));self.assertEqual({d['seed'] for d in rs},{95001+j})
    def test_all_histories_and_mapping(self):
        with patch('socket.socket',side_effect=AssertionError('network')):
            for d in schedule():
                c=Context(d);self.assertTrue(c.audit()['passed'])
    def test_world_guard(self):
        c=self.context();c.c.begin_step('HOLD')
        with self.assertRaises(AssertionError):c.c.execute_pending()
        self.assertEqual(c.c._active.world.read_indices,list(range(6)))
    def test_finite_wrong_forecasts_remain_wrong(self):
        for ns in range(4):
            for co in (-1,0,1):
                c=self.context();v=dict(next_state=ns,consequence=co);latched=[]
                result=c.finish(json.dumps(v),v,latched.append)
                self.assertEqual(len(latched),1);self.assertTrue(result['event']['result']['committed'])
                self.assertEqual(result['score']['actual'],dict(next_state=1,consequence=1))
                self.assertEqual(result['score']['exact_match'],ns==1 and co==1)
                self.assertEqual(result['event']['pending']['prediction']['consequence'],co)
    def test_invalid_no_event(self):
        for raw in (*INVALID,'{"next_state":1,"consequence":1,"consequence":-1}', '{"next_state":"1","consequence":1}'):
            with self.assertRaises((ValueError,TypeError)):parse(raw)
            c=self.context();self.assertIsNone(c.finish(raw,None)['event']);c.audit()
    def test_seventh_value_cannot_change_prompt(self):
        c=self.context();before=c.request()
        c.c._active.world._TemporalWorld__sequence=(1,-1,1,-1,1,-1,-1)
        self.assertEqual(c.request(),before)
        v=dict(next_state=1,consequence=1);r=c.finish(json.dumps(v),v)
        self.assertEqual(r['score']['actual']['consequence'],-1)
        self.assertFalse(r['score']['exact_match'])
    def test_fp_discriminator(self):
        f=self.context('F').view;p=self.context('P').view
        x=[r['consequence'] for r in f['VERIFIED_CHRONOLOGICAL_HISTORY']];y=[r['consequence'] for r in p['VERIFIED_CHRONOLOGICAL_HISTORY']]
        self.assertEqual(sorted(x),sorted(y));self.assertEqual(x[-1],y[-1]);self.assertNotEqual(x,y)
if __name__=='__main__':unittest.main()
