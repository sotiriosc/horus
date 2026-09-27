import json,unittest
from unittest.mock import patch
from .contexts import *
from .run import decision
from .analysis import summarize
class Journal:
    def __init__(self):self.rows=[]
    def append(self,*args):self.rows.append(args)
class SyntheticRecorder:
    def __init__(self,mode='correct'):
        self.j=Journal();self.calls=[];self.mode=mode
    def call(self,c,slot,request):
        view=json.loads(request['prompt'])
        if slot.startswith('Map:'):
            a=slot.split(':')[1];h=view['VERIFIED_CHRONOLOGICAL_HISTORY'];p={k:h[-1][k] for k in ('next_state','consequence')}
            if self.mode=='tie':p['consequence']=0
            if self.mode=='wrong':p['consequence']=1 if a=='ADVANCE' else -1
            raw='{' if self.mode=='invalid' and a=='ADVANCE' else json.dumps(p)
            parsed=None if raw=='{' else p
        else:
            alias=max(view['actions'],key=lambda r:r['map_prediction']['consequence'])['action'];raw=alias;parsed=c.d['mapping'][alias]
        row=dict(slot=slot,request=request,response=dict(raw_output=raw,transport_error=None,response_metadata=dict(synthetic=True)),parsed=parsed,parsed_recorded=True)
        self.calls.append(row);return row
class Tests(unittest.TestCase):
    def context(self,world='W1'):return Context(next(d for d in schedule() if d['world']==world))
    def test_all_authentic_fixtures_oracles_mappings(self):
        with patch('socket.socket',side_effect=AssertionError('zero inference')):
            for d in schedule():
                c=Context(d);rec=SyntheticRecorder();r=decision(c,rec)
                self.assertEqual([tuple(r['oracle']['values'][a][k] for k in ('next_state','consequence')) for a in ACTIONS],list(EXPECTED[d['world']]))
                self.assertTrue(r['protected_unchanged']);self.assertEqual(len(rec.calls),6)
                self.assertTrue(r['result']['end_to_end']);self.assertTrue(r['result']['permutation_same'])
    def test_all_map_calls_recorded_before_invalid_stop(self):
        rec=SyntheticRecorder('invalid');r=decision(self.context(),rec)
        self.assertEqual([x['slot'] for x in rec.calls[:3]],['Map:'+a for a in ACTIONS])
        self.assertEqual(len(rec.calls),5);self.assertEqual(r['result']['failure_source'],'MAP_INVALID_NO_EXPLORER')
    def test_tie_is_unissued_without_repair(self):
        rec=SyntheticRecorder('tie');r=decision(self.context(),rec)
        self.assertEqual(len(rec.calls),5);self.assertEqual(r['result']['failure_source'],'MAP_TIE_NO_EXPLORER')
        self.assertEqual(r['interface_binding']['failure'],'TIED_MAXIMUM')
    def test_wrong_map_is_not_repaired(self):
        rec=SyntheticRecorder('wrong');r=decision(self.context(),rec)
        self.assertEqual(r['result']['failure_source'],'MAP_WRONG_EXPLORER_FOLLOWS_MAP')
        self.assertTrue(r['result']['choices']['ModelMap']['follows_Map']);self.assertFalse(r['result']['end_to_end'])
    def test_oracle_requires_all_parsed(self):
        c=self.context()
        with self.assertRaises(AssertionError):c.oracle([])
        with self.assertRaises(AssertionError):c.oracle([dict(parsed_recorded=False)]*3)
        c.audit()
    def test_permutation_only_next_state(self):
        c=self.context();r=decision(c,SyntheticRecorder());base=r['views']['Oracle'];p=r['views']['Permutation']
        self.assertEqual(base['state'],p['state'])
        for i,(x,y) in enumerate(zip(base['actions'],p['actions'])):
            self.assertEqual(x['action'],y['action']);self.assertEqual(x['map_prediction']['consequence'],y['map_prediction']['consequence'])
            self.assertEqual(y['map_prediction']['next_state'],base['actions'][(i+1)%3]['map_prediction']['next_state'])
    def test_schedule_and_all_seeds(self):
        ds=schedule();self.assertEqual(len(ds),48)
        self.assertEqual(len({(d['world'],d['family'],d['mapping_index']) for d in ds}),48)
        for d in ds:
            base=96001+100*d['world_index']+10*d['mapping_index']
            for n,slot in enumerate(['Map:ADVANCE','Map:HOLD','Map:RETREAT','Oracle','Permutation','ModelMap'],1):self.assertEqual(seed(d,slot),base+n)
if __name__=='__main__':unittest.main()
