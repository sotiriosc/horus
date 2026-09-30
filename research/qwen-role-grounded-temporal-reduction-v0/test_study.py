import copy,json,unittest
from common import *
from generate import generate
from validate import validate,audit_case
from score import parse,gates
class StudyTests(unittest.TestCase):
 def test_materialization_reproducible(self):
  for n,b in generate().items():self.assertEqual(b,(P/'materialized'/n).read_bytes())
 def test_independent_validation(self):self.assertEqual(validate()['status'],'PASS')
 def test_primitive_corruption_rejected(self):
  c=json.loads((P/'materialized/cases.json').read_bytes())[0];c['state']['non_current_trials'][0]['currentness']='CURRENT'
  with self.assertRaises(AssertionError):audit_case(c)
 def test_bad_gold_rejected(self):
  c=json.loads((P/'materialized/cases.json').read_bytes())[0];c['gold']=X
  with self.assertRaises(AssertionError):audit_case(c)
 def test_strict_output(self):
  for c in CLASSES:self.assertEqual(parse(json.dumps({'classification':c})),c)
  for x in ['{}','null','[]','```json {} ```',json.dumps({'classification':N,'rationale':'x'}),'{'+'"classification":"'+N+'","classification":"'+D+'"}',json.dumps({'classification':[]})]:self.assertIsNone(parse(x))
 def fixture(self,aT=3,bT=3,cT=5):
  def arm(t):return dict(correct=21+t,per_class={k:dict(correct=t if k==T else 6 if k==D else 5,total=6) for k in CLASSES},changing_pairs=dict(passed=4),stable_pairs=dict(passed=2))
  a={name:arm(t) for name,t in zip(ARMS,[aT,bT,cT])};a['C']['correct']=26;return a
 def test_temporal_pattern(self):self.assertEqual(gates(self.fixture())['registered_interpretation'],'TEMPORAL_ROLE_GROUNDING_SUPPORTED')
 def test_generic_pattern(self):self.assertEqual(gates(self.fixture(bT=5))['registered_interpretation'],'GENERAL_OPERATIONAL_ROLE_GROUNDING_SUPPORTED')
 def test_each_primary_boundary(self):
  edits=[('historical',None),('gain',None),('overall',None),('nonhist',None),('changing',None),('stable',None)]
  for name,_ in edits:
   a=self.fixture()
   if name=='historical':a['C']['per_class'][T]['correct']=4
   if name=='gain':a['A']['per_class'][T]['correct']=4
   if name=='overall':a['C']['correct']=25
   if name=='nonhist':a['C']['per_class'][D]['correct']=4
   if name=='changing':a['C']['changing_pairs']['passed']=3
   if name=='stable':a['C']['stable_pairs']['passed']=1
   self.assertFalse(gates(a)['primary_C_pass'],name)
 def test_tradeoff(self):
  a=self.fixture();a['C']['per_class'][D]['correct']=4;self.assertEqual(gates(a)['registered_interpretation'],'ROLE_GROUNDING_TRADEOFF')
 def test_b_only_does_not_rescue_c(self):
  a=self.fixture(bT=5,cT=3);r=gates(a);self.assertFalse(r['primary_C_pass']);self.assertTrue(r['generic_B_descriptive_indicator']);self.assertEqual(r['registered_interpretation'],'ROLE_GROUNDING_NOT_ESTABLISHED');self.assertTrue(r['partial_improvement_without_primary_pass'])
 def test_ceiling_reported_not_reinterpreted(self):
  a=self.fixture(aT=6,bT=6,cT=6);r=gates(a);self.assertFalse(r['primary_C_pass']);self.assertTrue(r['bare_replication_difference_flag'])
if __name__=='__main__':unittest.main(verbosity=2)

class ScoringIntegrationTests(unittest.TestCase):
 def synthetic(self,fix_control=False):
  import tempfile,shutil
  from unittest.mock import patch
  import score as module
  with tempfile.TemporaryDirectory(prefix='role-score-qualification-') as tmp:
   p=Path(tmp);shutil.copytree(P/'materialized',p/'materialized');(p/'raw/finals').mkdir(parents=True);(p/'raw/metadata').mkdir()
   cases=json.loads((p/'materialized/cases.json').read_bytes());entries={e['render_id']:e for e in json.loads((p/'materialized/render-manifest.json').read_bytes())['entries']};changed=0
   for c in cases:
    is_error=fix_control and c['gold']==T and changed<3
    if is_error:changed+=1
    for arm in ARMS:
     rid=c['id']+'-'+arm;label=N if is_error and arm=='A' else c['gold'];b=raw({'classification':label});(p/'raw/finals'/(rid+'.txt')).write_bytes(b);dump(p/'raw/metadata'/(rid+'.json'),dict(final_sha256=sha(b),request_sha256=entries[rid]['request_sha256']))
   with patch.object(module,'load_raw',return_value={}):return module.score(p)
 def test_perfect_control_is_ceiling_not_intervention_support(self):
  r=self.synthetic();self.assertTrue(all(v['correct']==30 for v in r['arms'].values()));self.assertEqual(r['correctness_patterns_ABC']['111'],30);self.assertFalse(r['gates']['primary_C_pass']);self.assertEqual(r['gates']['registered_interpretation'],'ROLE_GROUNDING_NOT_ESTABLISHED')
 def test_full_scoring_matched_historical_repairs(self):
  r=self.synthetic(True);self.assertEqual(r['arms']['A']['correct'],27);self.assertEqual(r['arms']['A']['historical']['correct'],3);self.assertEqual(r['correctness_patterns_ABC']['011'],3);self.assertEqual(r['contrasts']['A→C']['historical']['wrong_to_correct'],3);self.assertEqual(r['arms']['C']['changing_pairs']['passed'],5);self.assertEqual(r['gates']['registered_interpretation'],'GENERAL_OPERATIONAL_ROLE_GROUNDING_SUPPORTED')
