import copy,json,tempfile,unittest
from pathlib import Path
from common import *
from generate import generate
from validate import validate,audit_case
from score import parse
class Tests(unittest.TestCase):
 def test_reproducible_materialization(self):
  for n,b in generate().items():self.assertEqual(b,(P/'materialized'/n).read_bytes())
 def test_independent_validation(self):self.assertEqual(validate()['status'],'PASS')
 def test_bad_primitive_rejected(self):
  c=json.loads((P/'materialized/cases.json').read_bytes())[0];c['state']['current_trial']['currentness']='NOT_CURRENT'
  with self.assertRaises(AssertionError):audit_case(c)
 def test_wrong_gold_rejected(self):
  c=json.loads((P/'materialized/cases.json').read_bytes())[0];c['gold']='INVALID'
  with self.assertRaises(AssertionError):audit_case(c)
 def test_strict_schema(self):
  for c in CLASSES:self.assertEqual(parse(json.dumps({'classification':c})),c)
  for x in ['', '{}', '[]', 'null','```json {} ```',json.dumps({'classification':N,'rationale':'x'}),'{'+'"classification":"'+N+'","classification":"'+D+'"}',json.dumps({'classification':[]})]:self.assertIsNone(parse(x))
if __name__=='__main__':unittest.main(verbosity=2)

class ScoreBoundaryTests(unittest.TestCase):
 def run_synthetic(self,errors):
  import shutil
  from unittest.mock import patch
  import score as scorer
  with tempfile.TemporaryDirectory(prefix='reduction-score-qualification-') as tmp:
   p=Path(tmp);shutil.copytree(P/'materialized',p/'materialized');(p/'raw/finals').mkdir(parents=True);(p/'raw/metadata').mkdir()
   cases=json.loads((p/'materialized/cases.json').read_bytes());entries={e['render_id']:e for e in json.loads((p/'materialized/render-manifest.json').read_bytes())['entries']};counts={c:0 for c in CLASSES}
   for c in cases:
    sid=c['id'];label=c['gold'];i=counts[label];counts[label]+=1
    text=raw({'classification':CLASSES[(CLASSES.index(label)+1)%5] if i<errors.get(label,0) else label})
    (p/'raw/finals'/(sid+'.txt')).write_bytes(text);dump(p/'raw/metadata'/(sid+'.json'),dict(final_sha256=sha(text),request_sha256=entries[sid]['request_sha256']))
   # Synthetic score qualification only: raw-commit guard is deliberately mocked; fixtures cannot enter CLI scoring.
   with patch.object(scorer,'load_raw',return_value={}):return scorer.score(p)
 def test_perfect(self):
  r=self.run_synthetic({});self.assertEqual(r['correct'],50);self.assertTrue(r['secondary_pair_gate']);self.assertEqual(r['primary_gate'],'PRIMITIVE_TO_ONTOLOGY_REDUCTION_ESTABLISHED')
 def test_43_with_every_class_8_passes(self):
  r=self.run_synthetic({D:2,N:2,U:1,T:1,X:1});self.assertEqual(r['correct'],43);self.assertEqual(r['primary_gate'],'PRIMITIVE_TO_ONTOLOGY_REDUCTION_ESTABLISHED')
 def test_42_fails(self):
  r=self.run_synthetic({D:2,N:2,U:2,T:1,X:1});self.assertEqual(r['correct'],42);self.assertEqual(r['primary_gate'],'PRIMITIVE_TO_ONTOLOGY_REDUCTION_NOT_ESTABLISHED')
 def test_high_overall_with_7_in_one_class_fails(self):
  r=self.run_synthetic({D:3});self.assertEqual(r['correct'],47);self.assertEqual(r['primary_gate'],'PRIMITIVE_TO_ONTOLOGY_REDUCTION_NOT_ESTABLISHED')
