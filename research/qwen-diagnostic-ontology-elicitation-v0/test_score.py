import copy,json,unittest
from generate import CLASSES
from score import grade,strict,witness
class ScoreChecks(unittest.TestCase):
 def setUp(self):
  self.schema={'type':'object','properties':{'classification':{'enum':CLASSES}},'required':['classification'],'additionalProperties':False};self.gold={'classification':CLASSES[0]}
 def test_strict_json(self):
  for text in ('{"classification":"x","classification":"y"}','NaN','Infinity','1e999','{} trailing','```json\n{}\n```'):
   with self.assertRaises(ValueError):strict(text)
 def test_correct_and_wrong(self):
  self.assertTrue(grade(json.dumps({'classification':CLASSES[0]}),self.schema,self.gold)[0]['correct']);self.assertFalse(grade(json.dumps({'classification':CLASSES[1]}),self.schema,self.gold)[0]['correct'])
 def test_schema_failure_keeps_selection_not_credit(self):
  r,_=grade(json.dumps({'classification':CLASSES[0],'extra':1}),self.schema,self.gold);self.assertFalse(r['correct']);self.assertEqual(r['selected'],CLASSES[0])
 def test_opaque_decoding_only(self):
  m=dict(zip(CLASSES,['K7','M2','R9','T4','V6']));s=copy.deepcopy(self.schema);s['properties']['classification']['enum']=list(m.values())
  self.assertTrue(grade('{"classification":"K7"}',s,self.gold,m)[0]['correct']);self.assertFalse(grade(json.dumps({'classification':CLASSES[0]}),s,self.gold,m)[0]['correct'])
 def test_rationale_length_gate(self):
  s=copy.deepcopy(self.schema);s['properties']['rationale']={'type':'string','minLength':1,'maxLength':500};s['required'].append('rationale')
  for n,expected in ((500,True),(501,False),(0,False)):
   self.assertEqual(grade(json.dumps({'classification':CLASSES[0],'rationale':'x'*n}),s,self.gold)[0]['correct'],expected)
 def test_rationale_never_rescues(self):
  obj={'classification':CLASSES[1],'rationale':CLASSES[0]};self.assertFalse(grade(json.dumps(obj),self.schema,self.gold)[0]['correct'])
 def test_type_exact_witness_and_missing_citation(self):
  w={'affected_component_ids':['component'],'contract_evidence_id':'c','cause_evidence_id':'i','effect_evidence_id':'r','decisive_evidence_id':'i','decisive_field':'/offset','observed_value':0,'required_value':7};g={'witness':w,'required_evidence_ids':['c','i','r']};ev={'records':[{'id':x} for x in ('c','i','r')]};obj={'affected_component_ids':['component'],'evidence_ids':['c','i','r'],'causal_mechanism':{k:v for k,v in w.items() if k!='affected_component_ids'}}
  self.assertTrue(witness(obj,{'correct':True},g,ev)['full_witness']);obj['causal_mechanism']['observed_value']=False;self.assertFalse(witness(obj,{'correct':True},g,ev)['full_witness']);obj['causal_mechanism']['observed_value']=0;obj['evidence_ids']=['c','i'];self.assertFalse(witness(obj,{'correct':True},g,ev)['full_witness'])
class AggregateChecks(unittest.TestCase):
 def campaign(self,changes):
  import tempfile,shutil,hashlib
  from pathlib import Path
  from generate import P,raw
  from score import score
  with tempfile.TemporaryDirectory(prefix='ontology-score-synthetic-') as td:
   root=Path(td);shutil.copytree(P/'materialized',root/'materialized');(root/'raw/finals').mkdir(parents=True)
   manifest=json.loads((root/'materialized/render-manifest.json').read_bytes());golds={g['world_id']:g for g in json.loads((root/'materialized/gold.json').read_bytes())};maps=json.loads((root/'materialized/label-maps.json').read_bytes())['mappings']
   for e in manifest['entries']:
    g=golds[e['world_id']];c=changes.get((e['arm'],g['slot']),g['classification']);obj={'classification':maps[e['mapping']][c] if e['arm']=='C' else c}
    if e['arm']=='D':obj['rationale']='Synthetic qualification only.'
    if e['arm']=='E':
     obj.update(affected_component_ids=g.get('witness',{}).get('affected_component_ids',[]),evidence_ids=g['required_evidence_ids'],observed=[],inferred=[],unknown=[],diagnostic_statement='Synthetic qualification only.',causal_mechanism=None,strongest_alternative_explanation='Synthetic alternative.',falsifier='Synthetic falsifier.')
     if 'witness' in g:obj['causal_mechanism']={k:v for k,v in g['witness'].items() if k!='affected_component_ids'};obj['causal_mechanism']['description']='Synthetic mechanism.'
    (root/'raw/finals'/(e['render_id']+'.txt')).write_bytes(raw(obj))
   (root/'raw/execution.json').write_bytes(raw({'stop':None,'attempted_calls':100,'completed_calls':100}))
   hashes={str(f.relative_to(root/'raw')):hashlib.sha256(f.read_bytes()).hexdigest() for f in (root/'raw').rglob('*') if f.is_file()}
   (root/'raw-freeze.json').write_bytes(raw({'purpose':'SCIENTIFIC_ONTOLOGY_V0','sha256':hashes}))
   return score(root)
 def test_all_correct_and_complete_witness(self):
  s=self.campaign({});self.assertTrue(s['all_arms_strong']);self.assertEqual(s['structured_metrics']['full_witness'],4);self.assertEqual(s['arms']['A']['correct'],20)
 def test_order_label_rationale_exact_four_boundary(self):
  for n in (3,4):
   changes={(a,i):CLASSES[1] for a in 'BCD' for i in range(n)};s=self.campaign(changes)
   for name in ('ORDER_SENSITIVITY','LABEL_SENSITIVITY','RATIONALE_BURDEN'):
    self.assertIn(name+('_PRESENT' if n==4 else '_NOT_ESTABLISHED'),s['findings'])
   self.assertEqual(s['contrasts']['A_C']['transitions']['correct_to_wrong'],n)
 def test_total_pass_but_per_class_fail(self):
  s=self.campaign({('A',i):CLASSES[1] for i in (0,1,2)});self.assertEqual(s['arms']['A']['correct'],17);self.assertFalse(s['arms']['A']['ontology_gate'])
 def test_epistemic_threshold(self):
  for slots,passed in (((8,12),True),((8,12,16),False)):
   s=self.campaign({('A',i):CLASSES[1] for i in slots});self.assertEqual(s['arms']['A']['epistemic_gate'],passed)
if __name__=='__main__':unittest.main(verbosity=2)

