import json,unittest
from collections import Counter
from .protocol import *
from .analysis import summarize
class Tests(unittest.TestCase):
    def test_full_balance(self):
        with detached_only():
            ds=schedule();self.assertEqual(len(ds),144)
            for family in ('O1','O2'):
                for relation in RELATIONS:
                    rows=[d for d in ds if d['family']==family and d['relation']==relation and d['condition']=='N']
                    self.assertEqual(Counter(d['mapping_index'] for d in rows),{j:2 for j in range(6)})
                    targets=[build(d)[1] for d in rows]
                    self.assertEqual(Counter(t['underlying_action'] for t in targets),{a:4 for a in ACTIONS})
                    self.assertEqual(sorted(Counter(t['alias'] for t in targets).values()),[4,4,4])
                    self.assertEqual(Counter(d['assignment_index'] for d in rows),{j:2 for j in range(6)})
                    ns=[build({**d,'condition':'V'})[1]['assignment'][t['underlying_action']]['next_state'] for d,t in zip(rows,targets)]
                    self.assertEqual(Counter(ns),{0:4,1:4,2:4})
    def test_matched_seed_schema_and_only_next_state_changes(self):
        for d in schedule():
            if d['condition']!='N':continue
            e={**d,'condition':'V'};n,_=build(d);v,_=build(e)
            self.assertEqual(request(d)['options'],request(e)['options'])
            self.assertEqual(n['state'],1);self.assertEqual(v['state'],1)
            self.assertEqual(set(n),{'state','actions'})
            for a,b in zip(n['actions'],v['actions']):
                self.assertEqual(set(a),{'action','map_prediction'});self.assertEqual(set(a['map_prediction']),{'next_state','consequence'})
                self.assertEqual(a['action'],b['action']);self.assertEqual(a['map_prediction']['consequence'],b['map_prediction']['consequence'])
                self.assertEqual(a['map_prediction']['next_state'],1)
            self.assertEqual(len({a['map_prediction']['next_state'] for a in v['actions']}),3)
    def test_relation_patterns_and_unique_target(self):
        for d in schedule():
            view,t=build(d);values=[x['map_prediction']['consequence'] for x in view['actions']]
            self.assertEqual(sorted(values),{'R1':[-1,0,1],'R2':[-1,-1,1],'R3':[-1,-1,0]}[d['relation']])
            self.assertEqual(values.count(max(values)),1)
            self.assertEqual(next(x['action'] for x in view['actions'] if x['map_prediction']['consequence']==max(values)),t['alias'])
    def test_strict_parser_invalid_does_not_count_same(self):
        rows=[]
        for d in schedule():
            for raw in ('ADVANCE','{"action":"K1"}','K1 because',None):self.assertFalse(score(raw,d)['valid'])
            rows.append(dict(descriptor=d,scoring=score('invalid',d)))
        r=summarize(rows,True);self.assertEqual(len(r['pairs']),72)
        self.assertTrue(all(p['not_comparable'] and not p['same'] for p in r['pairs']))
        self.assertFalse(any(f['primary']['supported'] or f['next_state']['supported'] for f in r['families'].values()))
    def test_all_correct_support_and_weak_R3_not_rescued(self):
        rows=[dict(descriptor=d,scoring=score(build(d)[1]['alias'],d)) for d in schedule()]
        perfect=summarize(rows,True);self.assertTrue(all(f['primary']['supported'] and f['next_state']['supported'] for f in perfect['families'].values()))
        for r in rows:
            if r['descriptor']['relation']=='R3':r['scoring']=score('invalid',r['descriptor'])
        weak=summarize(rows,True);self.assertFalse(any(f['primary']['supported'] for f in weak['families'].values()))
        self.assertTrue(all(f['relations']['R1']['N']['correct']==12 and f['relations']['R2']['N']['correct']==12 for f in weak['families'].values()))
    def test_guard_forbids_world_instantiation(self):
        from experiments.cross_episode_initialization_boundary_v1.boundary import EpisodeController
        with self.assertRaises(AssertionError):
            with detached_only():EpisodeController('forbidden')
if __name__=='__main__':unittest.main()
