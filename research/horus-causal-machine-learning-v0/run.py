"""Frozen raw-first lifecycle. A failed first-cycle gate cannot authorize cycle 2."""
import argparse,gc,time
from common import *
from engine import *
from admission import *
from scoring import cycle1_gate,cycle2_gate
from audit import preflight,training_audit,evidence_audit
from training import train
import torch

def cycle_allowed(cycle):
 if cycle==2:assert json.loads((P/'cycle1-results.json').read_bytes())['gate']['cycle2_authorized']
def release(model):
 del model;gc.collect();torch.cuda.empty_cache()
def score_harvest(cycle):
 phase=f'harvest{cycle}';tapes=verified_tapes(phase);arm=f'C{cycle-1}';scored=score_prediction_tape(tapes[arm,f'H{cycle}'],phase);score_prediction_tape(tapes[arm,f'V{cycle}'],phase)
 try:training,composition=construct_training(cycle,tapes,scored)
 except RuntimeError as e:
  assert str(e).startswith('ADMISSION_STOP_')
  dump(P/f'cycle{cycle}-results.json',dict(gate=dict(classification='CAUSAL_WORLD_MODEL_LEARNING_NOT_ESTABLISHED' if cycle==1 else 'SECOND_CAUSAL_LEARNING_CYCLE_NOT_ESTABLISHED',cycle2_authorized=False),admission_stop=str(e),harvest_errors=sum(not s['exact'] for s in scored),training_started=False));return False
 write_rows(P/f'D{cycle}.jsonl',training);dump(P/f'D{cycle}-composition.json',composition);dump(P/f'D{cycle}-leakage-audit.json',training_audit(cycle));return True

def public_score_hashes():
 return {f.name:filehash(f) for f in P.iterdir() if f.is_file() and (f.name.endswith('-scored.jsonl') or f.name.startswith(('D1','D2','cycle1-results','cycle2-results')))}
def double_replay(fn,label):
 result=fn();before=public_score_hashes();again=fn();assert result==again and before==public_score_hashes()
 dump(P/(label+'-zero-inference-replay.json'),dict(status='PASS',byte_identical=True,inference_calls=0,files=before));return result

def harvest(cycle):
 phase=f'harvest{cycle}';arm=f'C{cycle-1}'
 if not (P/(phase+'-raw-freeze.json')).exists():
  model,tok=stack.load(arm);worlds=private_worlds();manifests=[predict_pool(model,tok,phase,arm,pool,worlds) for pool in [f'H{cycle}',f'V{cycle}']]
  assert stack.runtime.fingerprints(model,False)==json.loads((OLD/'M0-base-fingerprints.json').read_bytes());freeze_raw(phase,manifests)
 result=double_replay(lambda:score_harvest(cycle),phase);dump(P/(phase+'-oracle-boundary-audit.json'),evidence_audit(phase));commit('Freeze authenticated all-error dataset and replay audit for cycle '+str(cycle));return result

def evaluation_plan(cycle):
 return [('C0','T1'),('C1','T1'),('C0','U1'),('C1','U1'),('C1','temporal-T1')] if cycle==1 else [('C1','T2'),('C2','T2'),('C1','U2'),('C2','U2'),('C2','T1'),('C2','temporal-T1')]
def score_evaluation(cycle):
 phase=f'evaluation{cycle}';tapes=verified_tapes(phase);scores={};temporal=None
 for arm,pool in evaluation_plan(cycle):
  tape=tapes[arm,pool]
  if pool.startswith('temporal'):temporal=score_temporal(tape)
  elif pool.startswith('U'):scores[arm,pool]=score_controls(tape)
  else:scores[arm,pool]=score_prediction_tape(tape,phase)
 old=f'C{cycle-1}';new=f'C{cycle}';comp=compare(scores[old,f'T{cycle}'],scores[new,f'T{cycle}']);ctrl=control_compare(scores[old,f'U{cycle}'],scores[new,f'U{cycle}']);audit=training_audit(cycle);oracle=evidence_audit(phase);assert oracle['status']=='PASS';artifact=stack.artifact(new)
 result=dict(comparison=comp,control=ctrl,temporal_retention=temporal,leakage=audit,oracle_boundary=oracle)
 if cycle==1:result['gate']=cycle1_gate(comp,temporal,artifact,audit)
 else:
  retention=compare(rows(P/'C1-T1-scored.jsonl'),scores['C2','T1']);result['cycle1_retention']=retention;result['gate']=cycle2_gate(comp,retention,temporal,artifact,audit)
 dump(P/f'cycle{cycle}-results.json',result);return result

def evaluate(cycle):
 phase=f'evaluation{cycle}'
 if not (P/(phase+'-raw-freeze.json')).exists():
  model,tok=stack.load(f'C{cycle-1}');worlds=private_worlds();manifests=[];active=f'C{cycle-1}'
  for arm,pool in evaluation_plan(cycle):
   if arm!=active:stack.attach(model,arm);active=arm
   if pool.startswith('temporal'):m=temporal_pool(model,tok,phase,arm)
   elif pool.startswith('U'):m=control_pool(model,tok,phase,arm,pool,worlds)
   else:m=predict_pool(model,tok,phase,arm,pool,worlds)
   manifests.append(m)
  assert stack.runtime.fingerprints(model,False)==json.loads((OLD/'M0-base-fingerprints.json').read_bytes());freeze_raw(phase,manifests)
 result=double_replay(lambda:score_evaluation(cycle),phase);commit('Record cycle '+str(cycle)+' sealed prediction, control, retention and hard gate');print(canon(result['gate']),flush=True)

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['harvest','train','evaluate','replay']);parser.add_argument('cycle',type=int,choices=[1,2]);a=parser.parse_args();preflight();cycle_allowed(a.cycle)
 if a.stage=='replay':
  phase=f'evaluation{a.cycle}';before=public_score_hashes();score_evaluation(a.cycle);assert before==public_score_hashes();print('Byte-identical replay PASS; zero inference',flush=True)
 elif a.stage=='train':
  assert training_audit(a.cycle)['status']=='PASS';train(a.cycle)
 else:globals()[a.stage](a.cycle)
