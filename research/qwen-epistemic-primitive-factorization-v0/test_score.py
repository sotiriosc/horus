"""Zero-model checks of decision semantics, exact scoring and interpretation boundaries."""
import copy,itertools,json,unittest
from generate import P,FAMILIES,CLASSES,REDUCTION,request_for
from score import grade,summarize,interpretation,pair_pass,strict,SPEC,SCHEMAS
from verify import derive,differences
GOLD=json.loads((P/'materialized/gold.json').read_bytes());PAIRS=json.loads((P/'materialized/pairs.json').read_bytes())
def rows():
 result=[]
 for g in GOLD:
  for arm in 'PR':
   task=g['family'] if arm=='P' else REDUCTION;r=grade(json.dumps(g[arm]),task,g[arm]);r.update(world_id=g['world_id'],pair_id=g['pair_id'],family=g['family'],side=g['side'],arm=arm,gold=g[arm]);result.append(r)
 return result

def change(rr,arm,world,text):
 r=next(x for x in rr if x['world_id']==world and x['arm']==arm);r.update(grade(text,r['family'] if arm=='P' else REDUCTION,r['gold']))

def incorrect(r):
 g=r['gold']
 if r['arm']=='R':return json.dumps({'classification':next(c for c in CLASSES if c!=g['classification'])})
 if r['family']==FAMILIES[0]:return json.dumps({**g,'same_referent':not g['same_referent']})
 vals=SCHEMAS[r['family']]['properties']['answer']['enum'];return json.dumps({'answer':next(v for v in vals if v!=g['answer'])})
class Checks(unittest.TestCase):
 def test_perfect_campaign(self):
  s=summarize(rows(),PAIRS);self.assertTrue(all(x['gate'] for x in s['primitives'].values()));self.assertTrue(s['reduction']['gate']);self.assertEqual(s['reduction']['flip_pair_passes'],19);self.assertEqual(s['reduction']['stable_pair_passes'],9);self.assertEqual(s['registered_interpretation']['registered_category'],'C')
 def test_primitive_seven_and_three_pass(self):
  rr=rows();r=next(r for r in rr if r['arm']=='P' and r['family']==FAMILIES[1]);change(rr,'P',r['world_id'],incorrect(r));s=summarize(rr,PAIRS)['primitives'][FAMILIES[1]];self.assertEqual((s['correct'],s['pair_passes'],s['gate']),(7,3,True))
 def test_primitive_six_and_three_fails(self):
  rr=rows();p=next(p for p in PAIRS if p['family']==FAMILIES[1])
  for sid in p['endpoints'].values():
   r=next(r for r in rr if r['world_id']==sid and r['arm']=='P');change(rr,'P',sid,incorrect(r))
  s=summarize(rr,PAIRS)['primitives'][FAMILIES[1]];self.assertEqual((s['correct'],s['pair_passes'],s['gate']),(6,3,False))
 def test_pair_direction_not_merely_change(self):
  a={'correct':True,'selected':{'answer':'NOT_CURRENT'}};b={'correct':True,'selected':{'answer':'CURRENT'}}
  self.assertFalse(pair_pass(a,b,{'answer':'CURRENT'},{'answer':'NOT_CURRENT'}))
 def test_identity_partial_no_joint_rescue(self):
  want={'same_referent':True,'equal_value':False};g=grade('{"same_referent":true,"equal_value":true}',FAMILIES[0],want);self.assertFalse(g['correct']);self.assertEqual(g['fields'],{'same_referent':True,'equal_value':False})
 def test_identity_boolean_type_is_strict(self):
  g=grade('{"same_referent":1,"equal_value":false}',FAMILIES[0],{'same_referent':True,'equal_value':False});self.assertFalse(g['schema_valid']);self.assertFalse(any(g['fields'].values()))
 def test_strict_json_no_semantic_rescue(self):
  for text in ('{"answer":"CURRENT","answer":"CURRENT"}','{"answer":NaN}','{"answer":1e999}','```json\n{"answer":"CURRENT"}\n```','{"answer":"CURRENT"} trailing'):
   self.assertFalse(grade(text,FAMILIES[1],{'answer':'CURRENT'})['schema_valid'])
 def test_extra_field_is_invalid(self):
  g=grade('{"answer":"CURRENT","reason":"x"}',FAMILIES[1],{'answer':'CURRENT'});self.assertFalse(g['correct']);self.assertFalse(g['schema_valid'])
 def test_invalid_reduction_column(self):
  rr=rows();r=next(r for r in rr if r['arm']=='R');cls=r['gold']['classification'];change(rr,'R',r['world_id'],'{}');s=summarize(rr,PAIRS);self.assertEqual(s['reduction']['confusion'][cls]['INVALID_OUTPUT'],1);self.assertEqual(s['reduction']['schema_valid'],55)
 def test_reduction_exact_integer_boundary(self):
  rr=rows();keep=dict(zip(CLASSES,[10,10,10,10,8]));seen={c:0 for c in CLASSES}
  for r in rr:
   if r['arm']=='R':
    c=r['gold']['classification'];seen[c]+=1
    if seen[c]>keep[c]:change(rr,'R',r['world_id'],incorrect(r))
  self.assertEqual(summarize(rr,PAIRS)['reduction']['correct'],48);self.assertTrue(summarize(rr,PAIRS)['reduction']['gate'])
  r=next(r for r in rr if r['arm']=='R' and r['correct']);change(rr,'R',r['world_id'],incorrect(r));self.assertFalse(summarize(rr,PAIRS)['reduction']['gate'])
 def test_reduction_class_floor_cannot_borrow(self):
  rr=rows();xx=[r for r in rr if r['arm']=='R' and r['gold']['classification']==CLASSES[4]]
  for r in xx[:3]:change(rr,'R',r['world_id'],incorrect(r))
  s=summarize(rr,PAIRS)['reduction'];self.assertEqual(s['correct'],53);self.assertFalse(s['gate'])
 def test_stable_pairs_are_not_flip_failures(self):
  s=summarize(rows(),PAIRS);p=next(p for p in s['pair_comparisons'] if not p['diagnostic_gold_changes']);self.assertIsNone(p['R_flip_pass']);self.assertTrue(p['R_stable_class_retention_pass']);self.assertTrue(p['R_exact_pair_pass'])
 def test_joint_four_outcomes(self):
  rr=rows();ps=[p for p in PAIRS if p['family']==FAMILIES[1]]
  for i,p in enumerate(ps):
   sid=p['endpoints']['A']
   for arm in (['R'] if i==1 else ['P'] if i==2 else ['P','R'] if i==3 else []):
    r=next(r for r in rr if r['world_id']==sid and r['arm']==arm);change(rr,arm,sid,incorrect(r))
  j=summarize(rr,PAIRS)['family_comparisons'][FAMILIES[1]]['endpoint_joint'];self.assertEqual([v['count'] for v in j.values()],[5,1,1,1])
 def test_interpretation_A_B_C_D(self):
  yes={f:True for f in FAMILIES};no={f:False for f in FAMILIES};self.assertEqual(interpretation(yes,False,no)['registered_category'],'A');self.assertEqual(interpretation(yes,True,no)['registered_category'],'C');self.assertEqual(interpretation(no,False,no)['registered_category'],'B');self.assertEqual(interpretation(no,True,no)['registered_category'],'D');self.assertEqual(interpretation(no,False,{**no,FAMILIES[2]:True})['registered_category'],'D')
 def test_all_interpretations_have_failed_list(self):
  for bits in itertools.product((False,True),repeat=7):
   pg=dict(zip(FAMILIES,bits));out=interpretation(pg,False,{f:False for f in FAMILIES});self.assertEqual(out['failed_primitives'],[f for f in FAMILIES if not pg[f]])
 def test_singleton_uncaptured_is_known(self):
  pair=SPEC['pairs'][16];a,_,_=derive(pair['states']['A']);b,_,_=derive(pair['states']['B']);self.assertEqual(a[FAMILIES[2]],{'answer':'KNOWN'});self.assertEqual(b[FAMILIES[2]],{'answer':'UNKNOWN'});self.assertEqual(a[FAMILIES[6]],b[FAMILIES[6]])
 def test_unknown_does_not_imply_underdetermined(self):
  for index in (24,25,26,27):
   a,_,_=derive(SPEC['pairs'][index]['states']['A']);b,_,_=derive(SPEC['pairs'][index]['states']['B']);self.assertEqual(a[FAMILIES[4]],b[FAMILIES[4]]);self.assertEqual(a[FAMILIES[6]],{'answer':'DETERMINATE'});self.assertEqual(b[FAMILIES[6]],{'answer':'UNDERDETERMINED'})
 def test_build_and_cycle_scope(self):
  for index in (13,14,15):
   a,_,_=derive(SPEC['pairs'][index]['states']['A']);b,_,_=derive(SPEC['pairs'][index]['states']['B']);self.assertEqual(a[FAMILIES[3]],{'answer':'CONSISTENT'});self.assertEqual(b[FAMILIES[3]],{'answer':'CONTRADICTORY'})
 def test_newer_nonserving_violation_not_historical(self):
  _,cls,_=derive(SPEC['pairs'][5]['states']['B']);self.assertEqual(cls,CLASSES[1])
 def test_offline_vector_not_scientific_prompt(self):
  pair=SPEC['pairs'][0];state=pair['states']['A'];before=request_for(state,'R',pair['primitive'],'SENTINEL_PRIMITIVE_QUESTION',SCHEMAS);self.assertNotIn('SENTINEL_PRIMITIVE_QUESTION',json.dumps(before));self.assertNotIn('primitive_vector',json.dumps(before));self.assertEqual(json.loads(before[0]['messages'][1]['content'].split('\n\nAligned factual state:\n')[1]),state)
 def test_one_delta_and_independent_all_gold(self):
  for p in SPEC['pairs']:
   self.assertEqual(len(differences(p['states']['A'],p['states']['B'])),1)
   for side in 'AB':
    v,c,_=derive(p['states'][side]);self.assertEqual(v,p['offline_gold'][side]['primitives']);self.assertEqual(c,p['offline_gold'][side]['classification'])
if __name__=='__main__':unittest.main()
