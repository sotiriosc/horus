import copy,json,unittest
from generate import P,CLASSES
from score import grade,strict,summarize
from verify import diff,operation,observed_class
class ScoringChecks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.gold=json.loads((P/'materialized/gold.json').read_bytes())
 def rows(self,changes=None):
  changes=changes or {};out=[]
  for g in self.gold:
   selected=changes.get(g['render_id'],g['classification']);r=grade(json.dumps({'classification':selected}),g['classification']);r.update({k:g[k] for k in ('render_id','unit_id','part','level','endpoint','family','tag') if k in g});r['gold']=g['classification'];out.append(r)
  return out
 def wrong(self,g):return next(c for c in CLASSES if c!=g['classification'])
 def test_strict_json_and_schema(self):
  for bad in ('NaN','Infinity','1e999','{"classification":"x","classification":"y"}','{}tail','```json\n{}\n```'):
   with self.assertRaises(ValueError):strict(bad)
  for obj in ({'classification':CLASSES[0],'rationale':'extra'},[],{'classification':'bad'}):self.assertFalse(grade(json.dumps(obj),CLASSES[0])['correct'])
 def test_recognized_selection_without_schema_credit(self):
  r=grade(json.dumps({'classification':CLASSES[0],'extra':0}),CLASSES[0]);self.assertEqual(r['selected'],CLASSES[0]);self.assertFalse(r['correct'])
 def test_perfect(self):
  s=summarize(self.rows());self.assertTrue(s['A']['minimal_core_gate']);self.assertEqual(s['A']['gold_preserving_invariant_cores'],10);self.assertEqual(s['B']['pair_passes'],10)
 def test_minimal_threshold(self):
  cores=[g for g in self.gold if g['part']=='A' and g['level']==0]
  for n,expected in ((1,True),(2,False)):
   s=summarize(self.rows({g['render_id']:self.wrong(g) for g in cores[:n]}));self.assertEqual(s['A']['minimal_core_gate'],expected)
 def test_invariance_boundary(self):
  late=[g for g in self.gold if g['part']=='A' and g['level']==4]
  for n,expected in ((2,True),(3,False)):
   s=summarize(self.rows({g['render_id']:self.wrong(g) for g in late[:n]}));self.assertEqual(s['A']['compositional_invariance_gate'],expected);self.assertEqual(s['A']['gold_preserving_invariant_cores'],10-n)
 def test_stable_wrong_distinguished(self):
  unit=next(g['unit_id'] for g in self.gold if g['part']=='A');gg=[g for g in self.gold if g['unit_id']==unit];s=summarize(self.rows({g['render_id']:self.wrong(g) for g in gg}));self.assertEqual(s['A']['invariant_cores'],10);self.assertEqual(s['A']['gold_preserving_invariant_cores'],9)
 def test_null_is_not_invariance(self):
  rows=self.rows();unit=rows[0]['unit_id']
  for r in rows:
   if r['unit_id']==unit:r.update(selected=None,correct=False,schema_valid=False)
  s=summarize(rows);self.assertEqual(s['A']['invariant_cores'],9);c=next(c for c in s['A']['cores'] if c['unit_id']==unit);self.assertEqual(c['first_invalid_label_level'],0)
 def test_first_changed_and_first_failure(self):
  g=next(g for g in self.gold if g['part']=='A' and g['level']==2);s=summarize(self.rows({g['render_id']:self.wrong(g)}));c=next(c for c in s['A']['cores'] if c['unit_id']==g['unit_id']);self.assertEqual(c['first_changed_level'],2);self.assertEqual(c['first_incorrect_level'],2);self.assertEqual(s['A']['transitions']['L2_L3']['counts']['wrong_to_correct'],1)
 def test_pair_threshold_and_family_floor(self):
  right=[g for g in self.gold if g['part']=='B' and g['endpoint']=='B']
  for chosen,expected in (([right[0],right[2]],True),([right[0],right[1]],False),([right[0],right[2],right[4]],False)):
   s=summarize(self.rows({g['render_id']:self.wrong(g) for g in chosen}));self.assertEqual(s['B']['sensitivity_gate'],expected);self.assertEqual(s['B']['pair_passes'],10-len(chosen))
 def test_changes_without_correctness_not_pair_success(self):
  rows=self.rows();pair=[r for r in rows if r['part']=='B'][:2]
  for r in pair:r.update(selected=CLASSES[(CLASSES.index(r['gold'])+1)%5],correct=False)
  s=summarize(rows);p=next(p for p in s['B']['pairs'] if p['unit_id']==pair[0]['unit_id']);self.assertTrue(p['class_changed']);self.assertFalse(p['passed'])
 def test_tags_denominators(self):
  s=summarize(self.rows());self.assertEqual(s['B']['tags']['UNKNOWN_DEPENDENCY']['pairs'],4);self.assertEqual(s['B']['tags']['UNKNOWN_DEPENDENCY']['endpoint_denominator'],8)
 def test_recursive_single_leaf_diff(self):
  self.assertEqual(diff({'a':[1,2]},{'a':[1,3]}),['/a/1']);self.assertEqual(diff({'a':1,'b':2},{'a':3,'b':4}),['/a','/b'])
 def test_independent_operator_vectors(self):
  self.assertEqual(operation(0,{'source_octets':[202]}),'cbea');self.assertEqual(operation(2,{'source_octet':57,'whitening_mask':131}),186);self.assertEqual(operation(3,{'source_letters':'BYQ','displacement':9}),'KHZ');self.assertEqual(operation(7,{'signed_integer':-19}),37);self.assertEqual(operation(9,{'dividend':383,'divisor':53}),{'quotient':7,'residue':12})
if __name__=='__main__':unittest.main(verbosity=2)
