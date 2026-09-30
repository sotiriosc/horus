"""Zero-inference regression tests for source semantics and matched comparison rules."""
import copy,json,unittest
import score
class Scoring(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.gold=json.loads((score.SOURCE/'materialized/gold.json').read_bytes());cls.pairs=json.loads((score.SOURCE/'materialized/pairs.json').read_bytes());lookup={g['world_id']:g for g in cls.gold};cls.rows=[]
  for e in json.loads((score.P/'materialized/render-manifest.json').read_bytes())['entries']:
   want=lookup[e['world_id']][e['arm']];task=e['family'] if e['arm']=='P' else score.source.REDUCTION;r=score.grade(json.dumps(want),task,want);r.update({k:e[k] for k in ('world_id','pair_id','side','family','arm','render_id')});r['gold']=want;cls.rows.append(r)
  cls.perfect=score.summarize(cls.rows,cls.pairs)
 def test_perfect_source_semantics(self):
  c=self.perfect;self.assertTrue(all(x['gate'] for x in c['primitives'].values()));self.assertEqual(c['reduction']['correct'],56);self.assertEqual(c['reduction']['exact_pair_passes'],28);self.assertEqual(c['reduction']['flip_pair_passes'],19);self.assertEqual(c['reduction']['stable_pair_passes'],9)
 def test_strict_duplicate_prose_and_nonfinite(self):
  task='IDENTITY_EQUALITY';want={'same_referent':True,'equal_value':False}
  for text in ['{"same_referent":true,"same_referent":true,"equal_value":false}','text '+json.dumps(want),'{"same_referent":NaN,"equal_value":false}','{"same_referent":1,"equal_value":false}']:
   self.assertFalse(score.grade(text,task,want)['correct'])
 def test_identity_invalid_has_no_field_credit(self):
  r=score.grade('{"same_referent":true,"equal_value":false,"extra":0}','IDENTITY_EQUALITY',{'same_referent':True,'equal_value':False});self.assertEqual(r['fields'],{'same_referent':False,'equal_value':False})
 def test_primitive_gate_pair_floor(self):
  rows=copy.deepcopy(self.rows);bad=[r for r in rows if r['arm']=='P' and r['family']==score.FAMILIES[1]][0];bad['correct']=False;c=score.summarize(rows,self.pairs);self.assertTrue(c['primitives'][score.FAMILIES[1]]['gate']);self.assertEqual(c['primitives'][score.FAMILIES[1]]['correct'],7);self.assertEqual(c['primitives'][score.FAMILIES[1]]['pair_passes'],3)
 def test_reduction_class_floor_even_high_total(self):
  rows=copy.deepcopy(self.rows);bad=[r for r in rows if r['arm']=='R' and r['gold']['classification']==score.CLASSES[0]][:4]
  for r in bad:r['correct']=False
  c=score.summarize(rows,self.pairs);self.assertEqual(c['reduction']['correct'],52);self.assertFalse(c['reduction']['gate'])
 def test_disjoint_interpretations(self):
  c=copy.deepcopy(self.perfect);self.assertEqual(score.classify(c,0)['category'],'A');c['reduction']['gate']=False;self.assertEqual(score.classify(c,7)['category'],'E');self.assertEqual(score.classify(c,8)['category'],'B');c['primitives'][score.FAMILIES[0]]['gate']=False;self.assertEqual(score.classify(c,15)['category'],'C');c['reduction']['gate']=True;self.assertEqual(score.classify(c,0)['category'],'D')
 def test_matched_same_has_no_disagreements(self):
  m=score.compare(self.perfect,self.perfect);self.assertEqual(len(m['tasks']),112);self.assertEqual(len(m['states']),56);self.assertEqual(len(m['pairs']),28);self.assertEqual(m['state_categories']['both_P_correct_both_R_correct']['count'],56);self.assertEqual(m['state_categories']['primitive_answers_differ']['count'],0);self.assertEqual(len(m['evidence_sufficiency']['states']),8);self.assertEqual(len(m['evidence_sufficiency']['pairs']),4)
 def test_mismatched_gold_rejected(self):
  c=copy.deepcopy(self.perfect);c['rows'][0]['gold']={'bad':1}
  with self.assertRaises(AssertionError):score.compare(self.perfect,c)
 def test_comparison_does_not_mutate_reference(self):
  before=score.raw(self.perfect);score.compare(self.perfect,self.perfect);self.assertEqual(score.raw(self.perfect),before)
if __name__=='__main__':unittest.main(verbosity=2)
