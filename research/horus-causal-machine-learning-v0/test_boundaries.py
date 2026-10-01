import copy,json,os,tempfile,unittest
from pathlib import Path
from receipts import Stream,validate_bundle,execution
from scoring import *
from planner import choose
from common import sha,STUDY_ID
class BoundaryTests(unittest.TestCase):
 def test_existing_horus_verifier_accepts_local_chain(self):
  with tempfile.TemporaryDirectory() as d:
   s=Stream(Path(d)/'receipts.jsonl',os.urandom(32));s.append('AUTHORIZATION',{'study_id':STUDY_ID});s.append('EXECUTED_TRANSITION',{'executed':True});self.assertEqual(len(s.verify()),2)
 def test_tampering_deletion_reordering_rejected(self):
  for mutation in ['edit','delete','reorder']:
   with tempfile.TemporaryDirectory() as d:
    path=Path(d)/'receipts.jsonl';secret=os.urandom(32);s=Stream(path,secret)
    for n in range(3):s.append('EXECUTED_TRANSITION',{'step':n,'actual':0})
    rows=copy.deepcopy(s.records)
    if mutation=='edit':rows[1]['record']['actual']=1
    elif mutation=='delete':rows.pop(1)
    else:rows[0],rows[1]=rows[1],rows[0]
    path.write_text(''.join(json.dumps(x)+'\n' for x in rows))
    with self.assertRaises(Exception):Stream(path,secret)
 def test_parser_requires_exact_sensor_set_integer_bits(self):
  self.assertEqual(parse('{"next_observation":{"A1":0,"B2":1}}',['A1','B2']),{'A1':0,'B2':1})
  for bad in ['{}','{"next_observation":{"A1":true}}','{"next_observation":{"A1":0,"A1":1}}','{"next_observation":{"A1":2}}','{"next_observation":{"A1":0},"explanation":"x"}']:
   self.assertIsNone(parse(bad,['A1']))
 def test_planner_uses_predictions_and_fixed_ties_only(self):
  v=dict(actuators=['A','B','C','D'],sensors=['S'],history=[],candidate_action='A')
  self.assertEqual(choose(v,{'S':1},[{'S':0},{'S':1},{'S':1},None]),'B');self.assertEqual(choose(v,{'S':1},[None]*4),'A')
  with self.assertRaises(AssertionError):choose(dict(v,hidden_state=1),{'S':1},[None]*4)
 def test_exact_paired_test_known_and_symmetric(self):
  a=[dict(id=str(i),exact=False) for i in range(10)];b=[dict(id=str(i),exact=True) for i in range(10)];self.assertEqual(paired(a,b)['mcnemar_exact_two_sided_p'],2/1024)
  self.assertEqual(paired(a,a)['mcnemar_exact_two_sided_p'],1.)
 def fixture(self):
  v=dict(actuators=['A'],sensors=['S'],history=[['RESET','0']],candidate_action='A');c=dict(id='H1-0',world_hash='world',cycle=1,pool='H1');auth=dict(adapter_sha256='adapter',training_eligible_pools=['H1','V1']);pred='{"next_observation":{"S":0}}'
  r=execution(c,'C0','adapter',v,'A',pred,{'S':1},65,sha(auth));e=dict(kind='EXECUTED_TRANSITION',record=r);s=dict(kind='SCORING_ATTESTATION',record=dict(study_id=STUDY_ID,execution_receipt_sha256=sha(e),prediction_sha256=sha(pred),actual_next_observation={'S':1},raw_freeze_commit='a'*40,exact_correct=False,field_correctness={'S':False}))
  return e,s,c,v,pred,auth
 def test_executed_authenticated_bundle_admission(self):self.assertEqual(validate_bundle(*self.fixture()),{'S':1})
 def test_unexecuted_or_sealed_or_wrong_hash_or_false_scoring_rejected(self):
  for field in ['executed','pool','prediction_sha256','exact_correct']:
   e,s,c,v,p,a=self.fixture()
   if field=='executed':e['record'][field]=False
   elif field=='pool':c[field]='T1';e['record'][field]='T1'
   elif field=='prediction_sha256':e['record'][field]='wrong'
   else:s['record'][field]=True
   with self.assertRaises(AssertionError):validate_bundle(e,s,c,v,p,a)
 def good(self):
  metric=dict(n=160,gain_pp=10,incumbent_correct=100,candidate_correct=116,incumbent_accuracy=.625,candidate_accuracy=.725,mcnemar_exact_two_sided_p=.009)
  comp=dict(exact=metric,schema=dict(candidate_accuracy=1),strata=dict(family={str(i):dict(metric) for i in range(3)}));temporal=dict(joint_correct=540,schema_valid=540);artifact=dict(adapter_changed=True,base_unchanged=True);audit=dict(status='PASS');return comp,temporal,artifact,audit
 def test_cycle1_retention_and_all_conditions_required(self):
  c,t,a,l=self.good();self.assertTrue(cycle1_gate(c,t,a,l)['cycle2_authorized']);t['joint_correct']=529;self.assertFalse(cycle1_gate(c,t,a,l)['cycle2_authorized']);t['joint_correct']=530;self.assertTrue(cycle1_gate(c,t,a,l)['cycle2_authorized']);c['exact']['mcnemar_exact_two_sided_p']=.01;self.assertFalse(cycle1_gate(c,t,a,l)['cycle2_authorized'])
 def test_control_is_separate_and_requires_six_targets(self):
  a=[dict(id=str(i),success=i<20,actions=2,prediction_errors=0) for i in range(40)];b=[dict(id=str(i),success=i<26,actions=2,prediction_errors=0) for i in range(40)]
  self.assertEqual(control_compare(a,b)['classification'],'CAUSAL_CONTROL_BENEFIT_SUPPORTED');b[25]['success']=False;self.assertEqual(control_compare(a,b)['classification'],'CAUSAL_CONTROL_BENEFIT_NOT_ESTABLISHED')
if __name__=='__main__':unittest.main()
