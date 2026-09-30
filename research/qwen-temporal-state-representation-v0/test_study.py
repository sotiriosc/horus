import copy,json,tempfile,shutil,unittest
from unittest.mock import patch
from common import *
from generate import generate,old_signatures
from validate import validate,audit_case
from score import parse,gate
class StudyTests(unittest.TestCase):
 def test_reproducible_generation(self):
  for n,b in generate().items():self.assertEqual(b,(P/'materialized'/n).read_bytes())
 def test_independent_validator(self):self.assertEqual(validate()['status'],'PASS')
 def test_semantic_freshness(self):
  prior=old_signatures();new={semantic_signature(c['state']) for c in json.loads((P/'materialized/cases.json').read_bytes())};self.assertFalse(prior&new)
 def test_wrong_temporal_field_rejected(self):
  c=json.loads((P/'materialized/cases.json').read_bytes())[0];c['gold']['prior_violation']='UNKNOWN'
  with self.assertRaises(AssertionError):audit_case(c)
 def test_wrong_primitive_rejected(self):
  c=json.loads((P/'materialized/cases.json').read_bytes())[0];c['state']['current_trial']['currentness']='NOT_CURRENT'
  with self.assertRaises(AssertionError):audit_case(c)
 def test_strict_schema(self):
  self.assertEqual(parse(raw(dict(current_violation='NO',prior_violation='YES'))),dict(current_violation='NO',prior_violation='YES'))
  for x in ['{}','null','[]','```json {} ```','{"current_violation":"NO"}', '{"current_violation":"NO","prior_violation":"YES","prior_violation":"NO"}', '{"current_violation":"NO","prior_violation":"YES","rationale":"x"}', '{"current_violation":"no","prior_violation":"YES"}']:self.assertIsNone(parse(x))
 def boundary(self):return dict(joint_correct=32,field_correct=dict(current_violation=34,prior_violation=34),historical_focus=dict(correct=11),changing_pairs=dict(passed=9),stable_pairs=dict(passed=8),schema_valid=35)
 def test_exact_gate_boundary_passes(self):self.assertTrue(gate(self.boundary())['passed'])
 def test_each_gate_required(self):
  paths=[['joint_correct'],['field_correct','current_violation'],['field_correct','prior_violation'],['historical_focus','correct'],['changing_pairs','passed'],['stable_pairs','passed'],['schema_valid']]
  for path in paths:
   m=self.boundary();d=m
   for k in path[:-1]:d=d[k]
   d[path[-1]]-=1;self.assertFalse(gate(m)['passed'],str(path))
 def synthetic_score(self,malformed=False):
  import score as module
  with tempfile.TemporaryDirectory(prefix='temporal-state-score-qualification-') as tmp:
   p=Path(tmp);shutil.copytree(P/'materialized',p/'materialized');(p/'raw/finals').mkdir(parents=True);(p/'raw/metadata').mkdir()
   cases=json.loads((p/'materialized/cases.json').read_bytes());entries={e['render_id']:e for e in json.loads((p/'materialized/render-manifest.json').read_bytes())['entries']}
   for i,c in enumerate(cases):
    sid=c['id'];b=b'{"current_violation":"NO"}' if malformed and i==0 else raw(c['gold']);(p/'raw/finals'/(sid+'.txt')).write_bytes(b);dump(p/'raw/metadata'/(sid+'.json'),dict(final_sha256=sha(b),request_sha256=entries[sid]['request_sha256']))
   with patch.object(module,'load_raw',return_value={}):return module.score(p)
 def test_full_perfect_scoring(self):
  r=self.synthetic_score();self.assertTrue(r['gate']['passed']);self.assertEqual(r['metrics']['joint_correct'],36);self.assertEqual(r['metrics']['matched_pairs']['passed'],18);self.assertEqual(r['metrics']['historical_focus']['correct'],12)
 def test_invalid_schema_both_fields_fail(self):
  r=self.synthetic_score(True);self.assertEqual(r['metrics']['schema_valid'],35);self.assertEqual(r['metrics']['field_correct'],dict(current_violation=35,prior_violation=35));self.assertEqual(r['metrics']['joint_correct'],35)
if __name__=='__main__':unittest.main(verbosity=2)
