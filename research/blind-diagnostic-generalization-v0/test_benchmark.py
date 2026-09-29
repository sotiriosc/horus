"""Development-seed synthetic checks; never model outputs or final-seed selection."""
import ast,copy,json,re,unittest
from pathlib import Path
from collections import Counter
from world_generator import *
from renderer import render,unrender,normalized,anti_coaching,replace,strings
from materialize import bundle,DECLARED_PAIR_PATHS,P
from scorer import score_rendering,score_benchmark,strict_json
DEV='development-only/blind-diagnostic-generalization-v0/test-v1'

def synthetic_answer(gold):
 m=copy.deepcopy(gold['mechanism_witness'])
 if m is not None:m['description']='Synthetic test assertion, never a model response.'
 return dict(classification=gold['classification'],affected_component_ids=gold['affected_components'],evidence_ids=gold['required_evidence'],observed=['Synthetic fixture'],inferred=[],unknown=[],diagnostic_statement='Synthetic fixture',causal_mechanism=m,strongest_alternative_explanation='Synthetic fixture',falsifier='Synthetic fixture')

def fixtures(seed=DEV):
 files=bundle(seed);decode=lambda n:json.loads(files[n]);grading=decode('grading.json')
 rendered={rid:decode('rendered/'+rid+'.json') for rid in grading}
 finals={rid:json.dumps(synthetic_answer(row['gold'])) for rid,row in grading.items()}
 protocol=json.loads((P/'protocol.json').read_text());protocol['matched_pairs']=decode('matched-pairs.json')
 return files,grading,rendered,finals,protocol

class BenchmarkTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.files,cls.grades,cls.rendered,cls.finals,cls.protocol=fixtures()
  cls.schema=json.loads((P/'diagnostic-schema.json').read_text());cls.cases,cls.pairs=generate(DEV)
 def grade(self,finals=None,violations=()):return score_benchmark(self.finals if finals is None else finals,self.grades,self.rendered,self.schema,self.protocol,violations)
 def ids(self,klass):return [rid for rid,row in self.grades.items() if row['gold']['classification']==klass]
 def altered(self,rid,**changes):
  out=self.finals.copy();v=json.loads(out[rid]);v.update(changes);out[rid]=json.dumps(v);return out
 def test_01_regeneration(self):
  self.assertEqual(generate(DEV),generate(DEV));self.assertEqual(self.files,bundle(DEV));self.assertEqual(len(self.files),184)
 def test_02_distribution(self):
  self.assertEqual(Counter(c['gold']['classification'] for c in self.cases),dict(zip(CLASSES,[6,4,4,3,3])))
  self.assertEqual(len(self.grades),80);self.assertEqual(len({c['case_id'] for c in self.cases}),20)
  self.assertEqual({c['family'] for c in self.cases if c['gold']['classification']==D},set(FAMILIES))
 def test_03_independent_injection_expectations(self):
  for family in range(6):
   for n in (11,19,30):
    good,go=frame(family,'@v2',False,n);bad,bo=frame(family,'@v2',True,n)
    self.assertFalse(operational_violation(family,good['data'],go['data']));self.assertTrue(operational_violation(family,bad['data'],bo['data']))
    # Explicit numerical/identity expectations independent of generate()'s class labels.
    field=('returned_value','final_decision','attributed_entity','attempt_total_after','posted_units','command_issued')[family]
    self.assertEqual(go['data'][field],(n+7,'DENY','@entity0',n+5,n,False)[family])
    self.assertEqual(bo['data'][field],(n,'ALLOW','@entity0',n,2*n,True)[family])
    if family==2:self.assertNotEqual(bad['data']['record_owner'],bad['data']['requested_entity'])
 def test_04_unknowns_have_both_completions(self):
  for family in (0,3,4,5):
   w=make_world(family,'unknown',DEV);self.assertEqual(oracle(family,w),U)
   for bad in (False,True):
    v=copy.deepcopy(w);cause=v['records'][4]['data']
    if family==0:cause['active_config']='@cfg2' if bad else '@cfg1'
    if family==3:cause.update(batch_size=8 if bad else 5,other_writes_in_interval=0,publication_fields=['attempt_total'])
    if family==4:cause['entries'][1]['operation_token']='@op0' if bad else '@op1';cause['key_column']='attempt_token' if bad else 'operation_token'
    if family==5:cause.update(sensed_level=cause['target_level'] if bad else cause['target_level']+1,implemented_comparator='>=' if bad else '>',comparison_result=True,readings=[cause['target_level'] if bad else cause['target_level']+1]*3)
    self.assertEqual(oracle(family,v),D if bad else H,(family,bad))
 def test_05_historical_repairs(self):
  for family in (0,1,4):
   w=make_world(family,'historical',DEV);r=w['records']
   self.assertTrue(operational_violation(family,r[2]['data'],r[3]['data']));self.assertFalse(operational_violation(family,r[4]['data'],r[5]['data']));self.assertEqual(oracle(family,w),T)
 def test_06_invalid_is_capture_not_operational_defect(self):
  for family,variant in ((2,'identity_conflict'),(0,'deployment_conflict'),(3,'digest_conflict')):
   w=make_world(family,variant,DEV);self.assertEqual(oracle(family,w),X)
   good=make_world(family,'healthy',DEV);w['records'][6]=good['records'][6];self.assertEqual(oracle(family,w),H)
 def test_07_pair_paths(self):
  self.assertEqual(len(self.pairs),6)
  for pair in self.pairs:
   self.assertEqual(pair['changed_paths'],DECLARED_PAIR_PATHS[pair['left_spec'],pair['right_spec']]);self.assertNotEqual(*pair['classes'])
 def test_08_alias_order_roundtrip(self):
  for c in self.cases:
   maps=[]
   for label in ('A','B'):
    for order in (1,2):
     out,mapping=render(c['world'],DEV,c['case_id'],label,order)
     self.assertEqual(unrender(out,mapping),normalized(c['world']));self.assertFalse(anti_coaching(out));maps.append(set(mapping.values()))
   a,am=render(c['world'],DEV,c['case_id'],'A',1);b,bm=render(c['world'],DEV,c['case_id'],'B',1)
   self.assertEqual(replace(a,{v:k for k,v in am.items()}),replace(b,{v:k for k,v in bm.items()}))
   self.assertEqual(maps[0],maps[1]);self.assertEqual(maps[2],maps[3]);self.assertFalse(maps[0]&maps[2])
 def test_09_no_gold_boundary(self):
  c=self.cases[0]
  with self.assertRaises(ValueError):render(c,DEV,c['case_id'],'A',1)
  polluted=copy.deepcopy(c['world']);polluted['records'][0]['gold']=D
  with self.assertRaises(ValueError):render(polluted,DEV,c['case_id'],'A',1)
  for token in ('Horus','S','E','ADVANCE',*FAMILIES,*CLASSES):self.assertTrue(anti_coaching({'neutral':token}))
 def test_10_prompt_projection_and_lexical_audit(self):
  for rid,row in self.grades.items():
   req=json.loads(self.files['requests/'+rid+'.json']);user=req['messages'][1]['content']
   self.assertEqual(json.loads(user.split('SYSTEM_RECORDS:\n')[1]),self.rendered[rid])
   self.assertEqual(req['messages'][0]['content'],self.protocol['system_prompt'])
   text=' '.join(m['content'] for m in req['messages'])
   self.assertFalse(re.search(r'\b(?:Horus|Qwen|Dolphin|ADVANCE|HOLD|RETREAT|S|E)\b',text,re.I))
   for family in FAMILIES:self.assertNotIn(family,text)
   for secret in ('gold','spec_id','variant','generator_metadata','mechanism_witness','case_id'):self.assertNotIn('"'+secret+'"',text)
   self.assertEqual(req['response_format']['schema'],self.schema)
 def test_11_gold_ids_and_decisive_values(self):
  for rid,row in self.grades.items():
   g=row['gold'];case=self.rendered[rid];records={r['id']:r for r in case['records']}
   self.assertTrue(set(g['required_evidence'])<=set(records))
   if g['classification']==D:
    m=g['mechanism_witness'];self.assertEqual(records[m['decisive_evidence_id']]['data'][m['decisive_field'][1:]],m['observed_value']);self.assertNotEqual(m['observed_value'],m['required_value'])
 def test_12_perfect_synthetic_handcheck(self):
  result=self.grade();self.assertEqual(result['classification'],'BLIND_DIAGNOSTIC_CAPABILITY_SUPPORTED_V0')
  self.assertEqual(result['measured']['semantic_classification_min'],20);self.assertEqual(result['measured']['counterfactual_pairs_min'],6);self.assertEqual(result['measured']['current_defect_localization_min'],6)
  self.assertEqual(result['factor_classification_disagreements'],dict(label_map=0,presentation_order=0))
  for v in result['factor_accuracy'].values():self.assertEqual(v,dict(correct=40,total=40))
 def test_13_single_healthy_false_positive_hard_fail(self):
  result=self.grade(self.altered(self.ids(H)[0],classification=D));self.assertFalse(result['gates']['healthy_rendering_current_false_positives_max']);self.assertEqual(result['measured']['semantic_classification_min'],20)
 def test_14_single_historical_false_positive_hard_fail(self):
  self.assertFalse(self.grade(self.altered(self.ids(T)[0],classification=D))['gates']['historical_rendering_current_false_positives_max'])
 def test_15_no_prose_rescue(self):
  rid=self.ids(D)[0];r=self.grade(self.altered(rid,classification=H,diagnostic_statement=D))['renderings'][rid];self.assertFalse(r['classification_correct']);self.assertFalse(r['localized'])
 def test_16_localization_requires_contract_value(self):
  finals=self.finals.copy();cids=list(dict.fromkeys(self.grades[r]['case_id'] for r in self.ids(D)))[:3]
  for rid in self.ids(D):
   if self.grades[rid]['case_id'] in cids:
    v=json.loads(finals[rid]);v['causal_mechanism']['required_value']=v['causal_mechanism']['observed_value'];finals[rid]=json.dumps(v)
  result=self.grade(finals);self.assertEqual(result['measured']['current_defect_classification_min'],6);self.assertEqual(result['measured']['current_defect_localization_min'],3);self.assertFalse(result['gates']['current_defect_localization_min'])
 def test_17_invented_ids_in_valid_or_malformed_answer(self):
  rid=self.ids(H)[0]
  for changes in (dict(evidence_ids=['zffffffffffffffff']),dict(evidence_ids=['zffffffffffffffff'],extra=1)):
   result=self.grade(self.altered(rid,**changes));self.assertFalse(result['renderings'][rid]['classification_correct']);self.assertFalse(result['gates']['invented_ids_max'])
 def test_18_malformed_is_wrong_no_repair(self):
  rid=self.ids(H)[0]
  for raw in ('```json\n'+self.finals[rid]+'\n```','{"classification":"NO_SUPPORTED_DIAGNOSIS","classification":"NO_SUPPORTED_DIAGNOSIS"}','NaN','[]','truncated'):
   finals=self.finals.copy();finals[rid]=raw;r=self.grade(finals)['renderings'][rid];self.assertFalse(r['schema_valid']);self.assertFalse(r['classification_correct'])
 def test_19_majority_and_representation(self):
  rid=self.ids(U)[0];cid=self.grades[rid]['case_id'];ids=[r for r,row in self.grades.items() if row['case_id']==cid]
  finals=self.finals.copy();finals[ids[0]]='{}';one=self.grade(finals);self.assertTrue(one['semantic_cases'][cid]['classification_correct']);self.assertFalse(one['semantic_cases'][cid]['consistent'])
  finals[ids[1]]='{}';self.assertFalse(self.grade(finals)['semantic_cases'][cid]['classification_correct'])
 def test_20_citations_are_mandatory(self):
  rid=self.ids(D)[0];result=self.grade(self.altered(rid,evidence_ids=[self.grades[rid]['gold']['required_evidence'][0]]))['renderings'][rid]
  self.assertTrue(result['classification_correct']);self.assertFalse(result['evidence_grounded']);self.assertFalse(result['localized'])
 def test_21_reasoning_transport_and_inventory_rejected(self):
  rid=self.ids(H)[0]
  with self.assertRaises(ValueError):strict_json({'content':self.finals[rid],'reasoning_content':'correct private answer'})
  finals=self.finals.copy();finals[rid]={'content':finals[rid],'reasoning_content':'anything'};self.assertEqual(self.grade(finals)['classification'],'INVALID_STUDY')
  finals=self.finals.copy();del finals[rid];self.assertEqual(self.grade(finals)['classification'],'INVALID_STUDY')
  self.assertEqual(self.grade(violations=['unauthorized retry'])['classification'],'INVALID_STUDY')
 def test_22_no_private_io_or_inference_dependencies(self):
  for name in ('scorer.py','renderer.py','world_generator.py'):
   tree=ast.parse((P/name).read_text());imports={n.module.split('.')[0] for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)}|{a.name.split('.')[0] for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names}
   self.assertFalse(imports&{'requests','urllib','http','socket','subprocess','openai'})
   if name=='scorer.py':self.assertFalse(any(isinstance(n,ast.Call) and ((isinstance(n.func,ast.Name) and n.func.id=='open') or (isinstance(n.func,ast.Attribute) and n.func.attr in ('read_text','read_bytes','open'))) for n in ast.walk(tree)))
 def test_23_context_and_different_development_seeds(self):
  manifest=json.loads(self.files['render-manifest.json']);self.assertEqual(len(manifest['schedule']),80)
  self.assertLessEqual(max(e['conservative_context_reservation'] for e in manifest['entries']),16384)
  for seed in ('development-only/edge-a','development-only/edge-b'):
   files=bundle(seed);self.assertEqual(len(files),184);self.assertNotEqual(files['grading.json'],self.files['grading.json'])
 def test_24_equivalent_output_witness(self):
  rid=next(r for r,g in self.grades.items() if g['gold'].get('mechanism_alternatives'))
  m=copy.deepcopy(self.grades[rid]['gold']['mechanism_alternatives'][0]);m['description']='Equivalent contract violation'
  self.assertTrue(self.grade(self.altered(rid,causal_mechanism=m))['renderings'][rid]['localized'])
 def test_25_counterfactual_pair_wrong_endpoint(self):
  finals=self.finals.copy()
  for p in self.pairs[:2]:
   for rid,row in self.grades.items():
    if row['case_id']==p['left']:finals[rid]='{}'
  result=self.grade(finals);self.assertEqual(result['measured']['counterfactual_pairs_min'],4);self.assertFalse(result['gates']['counterfactual_pairs_min'])

if __name__=='__main__':unittest.main(verbosity=2)
