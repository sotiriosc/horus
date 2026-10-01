"""Durable raw-first model requests and executed transitions; no accuracy scoring."""
import time
from common import *
from receipts import Stream,key,authorization,execution
from worlds import messages
from dsl import Circuit
from scoring import parse
from planner import choose,ACTION_BUDGET
import stack

def freeze_commit():return git('log','-1','--format=%H','--',PREFIX+'/world-data-freeze.json')
def private_worlds():return {x['id']:x for x in rows(PRIVATE/'worlds.jsonl')}
def cases(pool):return rows(P/'materialized'/(pool+'.jsonl'))
class Tape:
 def __init__(self,phase,arm,pool):
  self.phase=phase;self.arm=arm;self.pool=pool;self.filename=f'{phase}-{arm}-{pool}-signed.jsonl';self.stream=Stream(PRIVATE/self.filename,key());self.auth=authorization(phase,arm,stack.identity(arm),freeze_commit())
  if not self.stream.records:self.stream.append('AUTHORIZATION',self.auth)
  assert self.stream.records[0]['kind']=='AUTHORIZATION' and self.stream.records[0]['record']==self.auth
  self.index={}
  for e in self.stream.records[1:]:
   idx=(e['kind'],e['record']['id']);assert idx not in self.index;self.index[idx]=e
 def append(self,kind,record):
  idx=(kind,record['id']);assert idx not in self.index;e=self.stream.append(kind,record);self.index[idx]=e;return e
 def predict(self,model,tok,call_id,ids,requests,visible):
  rendered=[stack.runtime.prompt(tok,m) for m in requests]
  record=dict(id=call_id,case_ids=ids,messages=requests,visible=visible,rendered_prompts=rendered,prompt_token_ids=[tok.encode(s,add_special_tokens=False) for s in rendered])
  assert all(len(x)+stack.runtime.MAX_NEW<=stack.runtime.CONTEXT for x in record['prompt_token_ids'])
  intent=self.index.get(('REQUEST_BATCH',call_id))
  if intent:assert intent['record']==record
  else:intent=self.append('REQUEST_BATCH',record)
  response=self.index.get(('PREDICTION_BATCH',call_id))
  if response:
   assert response['record']['request_receipt_sha256']==sha(intent);return response['record']['outputs']
  # An interrupted request with no durable response may be resumed for technical
  # reasons only. Every durable response is reused, even if malformed or wrong.
  outputs=stack.runtime.infer(model,tok,requests,True)
  for o,s in zip(outputs,rendered):assert o['prompt_sha256']==__import__('hashlib').sha256(s.encode()).hexdigest()
  self.append('PREDICTION_BATCH',dict(id=call_id,request_receipt_sha256=sha(intent),outputs=outputs));return outputs
 def execute(self,case,visible,prediction,vm,state,step,record_id,call_id,output_index):
  action=visible['candidate_action'];a=visible['actuators'].index(action);nxt,obs=vm.step(state,a);actual=dict(zip(visible['sensors'],obs));existing=self.index.get(('EXECUTED_TRANSITION',record_id))
  if existing:
   r=existing['record'];assert r['actual_next_observation']==actual and r['executed_action']==action and r['history_sha256']==sha(visible['history']) and r['prediction_sha256']==sha(prediction)
   return nxt,actual,existing
  r=execution(case,self.arm,stack.identity(self.arm),visible,action,prediction,actual,step,sha(self.auth));r.update(id=record_id,call_id=call_id,output_index=output_index)
  return nxt,actual,self.append('EXECUTED_TRANSITION',r)
 def manifest(self):
  self.stream.verify();path=self.stream.path;path.chmod(0o444)
  return dict(private_file=self.filename,sha256=filehash(path),arm=self.arm,pool=self.pool,phase=self.phase,records=len(self.stream.records),request_batches=sum(e['kind']=='REQUEST_BATCH' for e in self.stream.records),predictions=sum(len(e['record']['outputs']) for e in self.stream.records if e['kind']=='PREDICTION_BATCH'),executions=sum(e['kind']=='EXECUTED_TRANSITION' for e in self.stream.records),correctness_deferred=True)

def emit(stage,start,done,total,**kwargs):
 elapsed=time.monotonic()-start;print(json.dumps(dict(stage=stage,done=done,total=total,elapsed_seconds=round(elapsed,1),estimated_remaining_seconds=round(elapsed/max(done,1)*(total-done),1),**kwargs)),flush=True)
def environment(case,worlds):
 w=worlds[case['id']];assert w['world_hash']==case['world_hash']==sha(dict(seed=w['seed'],program=w['program']));vm=Circuit(w['program']['roots']);state=(w['state_after_diagnostics'][0],tuple(w['state_after_diagnostics'][1]));return vm,state

def predict_pool(model,tok,phase,arm,pool,worlds):
 cs=cases(pool);tape=Tape(phase,arm,pool);start=time.monotonic()
 for i in range(0,len(cs),4):
  chunk=cs[i:i+4];visible=[c['visible'] for c in chunk];call_id=f'{pool}-batch-{i:04d}';outputs=tape.predict(model,tok,call_id,[c['id'] for c in chunk],[messages(v) for v in visible],visible)
  for j,(c,v,o) in enumerate(zip(chunk,visible,outputs)):
   vm,state=environment(c,worlds);tape.execute(c,v,o['text'],vm,state,len(v['history']),c['id'],call_id,j)
  if i%40==0 or i+len(chunk)==len(cs):emit(arm+'-'+pool,start,i+len(chunk),len(cs))
 return tape.manifest()

def control_pool(model,tok,phase,arm,pool,worlds):
 cs=cases(pool);tape=Tape(phase,arm,pool);start=time.monotonic()
 for number,c in enumerate(cs,1):
  vm,state=environment(c,worlds);visible=json.loads(canon(c['visible']));last_obs=dict(zip(visible['sensors'],worlds[c['id']]['last_observation']));used=0
  for step in range(1,ACTION_BUDGET+1):
   variants=[dict(visible,candidate_action=a) for a in visible['actuators']];call_id=f'{c["id"]}-step-{step}';outputs=tape.predict(model,tok,call_id,[c['id']]*len(variants),[messages(v) for v in variants],variants)
   parsed=[parse(o['text'],visible['sensors']) for o in outputs];chosen=choose(visible,c['target'],parsed);j=visible['actuators'].index(chosen);v=variants[j]
   state,last_obs,_=tape.execute(c,v,outputs[j]['text'],vm,state,len(v['history']),call_id,call_id,j);used=step
   visible['history'].append([chosen,''.join(str(last_obs[s]) for s in visible['sensors'])])
   # Goal termination is the fixed control policy, not prediction-correctness
   # scoring. Predictive correctness is never computed during execution.
   if last_obs==c['target']:break
  terminal=dict(id=c['id'],actions=used,last_observation=last_obs,target=c['target'],termination='target_observed' if last_obs==c['target'] else 'action_budget_exhausted')
  existing=tape.index.get(('CONTROL_TERMINAL',c['id']))
  if existing:assert existing['record']==terminal
  else:tape.append('CONTROL_TERMINAL',terminal)
  emit(arm+'-'+pool+'-control',start,number,len(cs))
 return tape.manifest()

def temporal_pool(model,tok,phase,arm):
 cs=rows(OLD/'materialized/T1.jsonl');tape=Tape(phase,arm,'temporal-T1');start=time.monotonic()
 for i in range(0,len(cs),4):
  chunk=cs[i:i+4];tape.predict(model,tok,f'temporal-batch-{i:04d}',[c['id'] for c in chunk],[stack.temporal_data.messages(c) for c in chunk],[None]*len(chunk))
  if i%40==0 or i+len(chunk)==len(cs):emit(arm+'-temporal-retention',start,i+len(chunk),len(cs))
 return tape.manifest()

def freeze_raw(phase,manifests):
 assert not (P/(phase+'-raw-freeze.json')).exists()
 dump(P/(phase+'-raw-freeze.json'),dict(phase=phase,parent_commit=git('rev-parse','HEAD'),world_freeze_commit=freeze_commit(),scoring_performed=False,files=manifests));return commit('Freeze '+phase+' requests, responses and executed receipts before scoring')
def verified_tapes(phase):
 manifest_path=P/(phase+'-raw-freeze.json');manifest=json.loads(manifest_path.read_bytes());assert subprocess.check_output(['git','show','HEAD:'+str(manifest_path.relative_to(ROOT))],cwd=ROOT)==manifest_path.read_bytes()
 result={}
 for row in manifest['files']:
  assert filehash(PRIVATE/row['private_file'])==row['sha256'];tape=Tape(phase,row['arm'],row['pool']);tape.stream.verify();result[row['arm'],row['pool']]=tape
 return result
