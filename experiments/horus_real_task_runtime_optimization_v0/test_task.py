import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from .adapter import *
from grounded_agent.empirical_adapter import recommendation
from experiments.grounded_autonomous_agent_v0_2.worker import parse_action

class TaskTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name);bind_task_metadata()
 def tearDown(self):self.tmp.cleanup()
 def open(self,name='one',resume=False):
  p=self.p/name;store=SessionStore(p/'session',resume);memory=ModernMemory(p/'memory.sqlite3',not resume)
  if not resume:store.save(state=0,next_transaction_id=1)
  self.addCleanup(memory.close);self.addCleanup(store.close)
  return store,memory
 def measured(self,value=0):return dict(valid=True,resource_violation=False,error=None,wall_seconds={-1:12,0:10,1:8}[value],output_sha256='a'*64)
 def execute(self,s,m,i,action='HOLD',value=0):
  ctx=context(s,m,i);info=dict(status='VALID',call_id=None,raw_output_sha256=None,latency_seconds=0)
  choice=(action,'MODEL_FOR_UNRESOLVED',ctx['route'],info,ctx['assessments'],ctx['suffix'])
  world=RuntimeWorld(0,action,lambda a:self.measured(value),10,.1)
  return execute_protected(s,m,i,choice,world,i,'SYNTHETIC_ONLY')
 def test_threshold_boundaries(self):
  m=self.measured()
  for wall,want in [(9,1),(9.01,0),(11,0),(11.01,-1)]:self.assertEqual(consequence({**m,'wall_seconds':wall},10,.1),want)
  self.assertEqual(consequence({**m,'valid':False,'wall_seconds':1},10,.1),-1)
 def test_real_executor_called_before_receipt_and_memory(self):
  s,m=self.open();observed=[]
  def run(a):observed.append((len(s.records['events']),len(m.rows())));return self.measured()
  world=RuntimeWorld(0,'HOLD',run,10,.1);ctx=context(s,m,1)
  info=dict(status='VALID',call_id=None,raw_output_sha256=None,latency_seconds=0)
  with patch('experiments.base_framework_v1.hidden_oracle.TrueWorldOracle.execute',side_effect=AssertionError('simulator execution forbidden')):
   result=execute_protected(s,m,1,('HOLD','MODEL_FOR_UNSEEN',ctx['route'],info,ctx['assessments'],ctx['suffix']),world,1,'SYNTHETIC_ONLY')
  self.assertEqual(observed,[(0,0)]);self.assertEqual(len(m.rows()),1)
  self.assertEqual(result['event']['measurement_sha256'],digest(world.measurement))
 def test_action_is_frozen(self):
  w=RuntimeWorld(0,'HOLD',lambda _:self.measured(),10,.1)
  with self.assertRaises(RuntimeError):w.execute(1,1,'ADVANCE')
  w.execute(1,1,'HOLD')
  with self.assertRaises(RuntimeError):w.execute(1,1,'HOLD')
 def test_model_cannot_assign_consequence(self):
  with self.assertRaises(ValueError):parse_action('{"selected_action":"HOLD","consequence":1}')
 def test_runtime_failure_is_negative_authenticated_experience(self):
  s,m=self.open();r=self.execute(s,m,1,value=-1)
  self.assertEqual(m.rows()[0]['realized_consequence'],-1);self.assertEqual(r['event']['authorization_status'],'AUTHORIZED')
 def test_empirical_typing_does_not_claim_deterministic_knowledge(self):
  s,m=self.open();self.execute(s,m,1)
  a=all_assessments(AuthenticatedMemory(s,m),0)['HOLD'];self.assertEqual(a['relation_type'],'EMPIRICAL');self.assertEqual(a['kind'],'EMPIRICALLY_STABLE')
  self.assertEqual(context(s,m,2)['route']['route'],'MODEL');self.assertEqual(qualifying_suffix(s,m)['count'],0)
 def test_exact_E_trigger_from_executed_history(self):
  s,m=self.open()
  for i in range(1,5):self.execute(s,m,i,value=-1)
  e=recommendation(context(s,m,5),authenticated_projection(s,m));self.assertTrue(e['eligible']);self.assertEqual(e['target_action'],'ADVANCE')
  class NoModel:
   def generate(self,_):raise AssertionError('E called model')
  selected=integrated_decide(s,m,NoModel(),5);self.assertEqual(selected[1],'EMPIRICAL_EVIDENCE_ACQUISITION');self.assertEqual(selected[0],'ADVANCE')
 def test_restart_reconstructs_full_state(self):
  s,m=self.open()
  for i in range(1,5):self.execute(s,m,i)
  before=snapshot(s,m);m.close();s.close();s2,m2=self.open(resume=True)
  self.assertEqual(before,snapshot(s2,m2))
 def test_measurement_tampering_invalidates_authentication(self):
  s,m=self.open();self.execute(s,m,1);m.close();s.close();f=self.p/'one/session/events.jsonl';x=json.loads(f.read_text());x['record']['runtime_measurement']['wall_seconds']=.001;f.write_text(json.dumps(x)+'\n')
  with self.assertRaises(Exception):SessionStore(self.p/'one/session',True)
 def test_arm_isolation(self):
  a,am=self.open('A');b,bm=self.open('B');self.execute(a,am,1)
  self.assertEqual(len(bm.rows()),0);self.assertEqual(len(b.records['events']),0)
 def test_future_workload_not_in_policy_context(self):
  s,m=self.open();p=context(s,m,1)['projection']
  for forbidden in ('workload','latency','reference','arm_order','global_schedule_index','next_profile'):self.assertNotIn(forbidden,p)
 def test_invalid_response_receives_no_manual_rescue(self):
  for raw in ('','{"selected_action":"LAUNCH_SHELL"}','HOLD'):
   with self.assertRaises((ValueError,TypeError)):parse_action(raw)
 def test_score_cannot_confuse_drift_with_growth(self):
  from .score import summarize,gates
  def rows(arm,early,late):
   result=[]
   for i in range(24):
    half=i//12;profile=(i%12)//3;w=f'P{profile}-{i%3}';lat=early if not half else late
    d=None if arm=='C' else dict(decision_source='MODEL_FOR_UNRESOLVED',action_model_latency_seconds=0)
    result.append(dict(global_index=i+1,profile=profile,workload=w,half=half,decision=d,realized_consequence=0 if not half else 1,reference_seconds=10,measurement=dict(action='HOLD' if not half else 'ADVANCE',valid=True,wall_seconds=lat,timings={})))
   return result
  arms={a:summarize(rows(a,10,7 if a!='B' else 10)) for a in 'ABC'}
  self.assertEqual(gates(arms,True)['classification'],'REAL_TASK_INTEGRITY_ONLY')
  arms['C']=summarize(rows('C',10,10))
  self.assertEqual(gates(arms,True)['classification'],'EXPERIENCE_CONDITIONED_IMPROVEMENT_SUPPORTED')
  self.assertEqual(gates(arms,False)['classification'],'INCOMPLETE_OR_INFRASTRUCTURE_INVALID')
if __name__=='__main__':unittest.main()
