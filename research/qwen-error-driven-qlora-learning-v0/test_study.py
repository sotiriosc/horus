import copy,itertools,json,math,tempfile,unittest
from pathlib import Path
from data import *
from analysis import *
class StudyTests(unittest.TestCase):
 def fixture(self,cur=0,priors=(0,)):
  return case(dict(proposition_scope=SCOPE,package=dict(consistency='CONSISTENT'),current_trial=trial(cur,True),non_current_trials=[trial(i) for i in priors]),'fixture',0)
 def test_all_primitives_and_three_prior_compositions(self):
  for cur in range(6):
   for priors in itertools.product(range(6),repeat=3):independently_audit(self.fixture(cur,priors))
 def test_independent_auditor_rejects_wrong_gold(self):
  c=self.fixture();c['gold']['prior_violation']='YES'
  with self.assertRaises(AssertionError):independently_audit(c)
 def test_unknown_reference_mismatch_is_not_established_violation(self):
  self.assertEqual(self.fixture(5,(0,5))['gold'],dict(current_violation='UNKNOWN',prior_violation='UNKNOWN'))
 def test_one_known_violation_dominates_uncertainty(self):self.assertEqual(self.fixture(0,(4,1,5))['gold']['prior_violation'],'YES')
 def test_contradiction_independent(self):
  a=self.fixture(5,(1,4));b=copy.deepcopy(a);b['state']['package']['consistency']='CONTRADICTORY';self.assertEqual(gold(a['state']),gold(b['state']))
 def test_signature_ignores_order(self):
  a=self.fixture(0,(1,2,4));b=copy.deepcopy(a);b['state']['non_current_trials'].reverse();self.assertEqual(signature(a['state']),signature(b['state']))
 def test_no_model_answer_or_id_in_prompt(self):
  c=self.fixture();text=canonical(messages(c));self.assertNotIn(c['id'],text);self.assertNotIn('witnesses',text);self.assertNotIn('semantic_signature',text)
 def test_parser_exact_keys_values_and_duplicates(self):
  self.assertIsNotNone(parse('{"current_violation":"YES","prior_violation":"NO"}'))
  for bad in ['{}','[]','null','```json\n{}\n```','{"current_violation":"YES","prior_violation":"NO","x":1}','{"current_violation":"YES","current_violation":"NO","prior_violation":"NO"}','{"current_violation":true,"prior_violation":"NO"}']:self.assertIsNone(parse(bad))
 def test_every_error_and_equal_replay(self):
  cs=[self.fixture(i,(j,)) for i,j in [(0,0),(1,1),(4,4),(2,2)]]
  for i,c in enumerate(cs):c['id']=str(i)
  scored=[dict(id=c['id'],joint=i>=2) for i,c in enumerate(cs)];d,m=construct_training(cs,[],scored,1)
  self.assertEqual({e['case_id'] for e in d if e['source']=='error'},{'0','1'});self.assertEqual(m['composition'],{'error':2,'correct_replay':2})
 def test_replay_with_replacement_when_errors_dominate(self):
  c=self.fixture();self.assertEqual(len(stratified_replay([c],20,7)),20)
 def test_no_errors_or_no_correct_stop(self):
  c=self.fixture()
  for good in [True,False]:
   with self.assertRaises(RuntimeError):construct_training([c],[],[dict(id=c['id'],joint=good)],1)
 def test_mcnemar_known(self):
  a=[dict(id=str(i),joint=False) for i in range(10)];b=[dict(id=str(i),joint=True) for i in range(10)];r=paired(a,b);self.assertEqual(r['mcnemar_exact_two_sided_p'],2/1024);self.assertEqual(r['gain_pp'],100)
 def test_mcnemar_symmetric(self):
  a=[dict(id=str(i),joint=i%2==0) for i in range(20)];b=[dict(id=str(i),joint=i%2!=0) for i in range(20)];self.assertEqual(paired(a,b)['mcnemar_exact_two_sided_p'],1)
 def test_cycle1_requires_every_condition(self):
  c=dict(joint={'gain_pp':8,'mcnemar_exact_two_sided_p':.009},targeted={'gain_pp':10},schema={'candidate_accuracy':.99},noncollapsed=True);r={'x':{'gain_pp':-3}};t=dict(adapter_changed=True,base_unchanged=True);l={'status':'PASS'}
  self.assertTrue(cycle1_gate(c,r,t,l)['cycle2_authorized']);t['base_unchanged']=False;self.assertFalse(cycle1_gate(c,r,t,l)['cycle2_authorized'])
 def test_exact_thresholds_p_is_strict(self):
  c=dict(joint={'gain_pp':8,'mcnemar_exact_two_sided_p':.01},targeted={'gain_pp':10},schema={'candidate_accuracy':.99},noncollapsed=True)
  self.assertFalse(cycle1_gate(c,{'x':{'gain_pp':0}},dict(adapter_changed=True,base_unchanged=True),{'status':'PASS'})['cycle2_authorized'])
 def test_neighbor_single_leaf_change(self):
  c=self.fixture(5,(0,1,4));ns=neighbors(c,set(),set())
  def differences(a,b):
   if isinstance(a,dict):return sum(differences(a[k],b[k]) for k in a)
   if isinstance(a,list):return sum(differences(x,y) for x,y in zip(a,b))
   return int(a!=b)
  self.assertTrue(ns)
  for n in ns:self.assertEqual(differences(c['state'],n['state']),1);independently_audit(n)
 def test_second_cycle_replays_exactly_512(self):
  cs=[self.fixture(0,(0,)),self.fixture(1,(1,))];cs[1]['id']='second';scores=[dict(id=c['id'],joint=i==1) for i,c in enumerate(cs)];d,_=construct_training(cs,[],scores,1);d2,m=construct_training(cs,[],scores,2,d);self.assertEqual(m['composition']['cycle1_retained_replay'],512)
 def test_cycle2_requires_schema_retention_and_regression(self):
  comp={'joint':{'gain_pp':4,'mcnemar_exact_two_sided_p':.049},'schema':{'candidate_accuracy':.99}}
  retention={'joint':{'gain_pp':-2},'schema':{'candidate_accuracy':.99}}
  regs={'R1':{'schema':{'gain_pp':0,'candidate_accuracy':1.}},'R2':{'schema':{'gain_pp':0,'candidate_accuracy':1.}}}
  training={'adapter_changed':True,'base_unchanged':True};leakage={'status':'PASS'}
  self.assertEqual(cycle2_gate(comp,retention,regs,training,leakage)['classification'],'TWO_CYCLE_ERROR_DRIVEN_LEARNING_SUPPORTED')
  regs['R2']['schema']['candidate_accuracy']=.98
  self.assertEqual(cycle2_gate(comp,retention,regs,training,leakage)['classification'],'SECOND_LEARNING_CYCLE_NOT_ESTABLISHED')
if __name__=='__main__':unittest.main()
