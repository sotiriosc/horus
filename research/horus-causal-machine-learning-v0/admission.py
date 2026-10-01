"""Post-freeze score attestations and mechanical authenticated training admission."""
import random
from collections import Counter,defaultdict
from common import *
from engine import cases,verified_tapes
from receipts import Stream,key,validate_bundle
from scoring import endpoint,parse,paired,compare,control_compare
from worlds import messages
from planner import choose,ACTION_BUDGET
import stack

def raw_commit(phase):return git('log','-1','--format=%H','--',PREFIX+'/'+phase+'-raw-freeze.json')
def get_prediction(tape,execution):
 r=execution['record'];response=tape.index['PREDICTION_BATCH',r['call_id']];request=tape.index['REQUEST_BATCH',r['call_id']]
 assert response['record']['request_receipt_sha256']==sha(request)
 j=r['output_index'];assert request['record']['case_ids'][j]==r['world_id'];o=response['record']['outputs'][j];v=request['record']['visible'][j]
 assert sha(o['text'])==r['prediction_sha256'] and sha(v)==r['request_sha256'];return o,v

def score_prediction_tape(tape,phase):
 scored=[];attest=Stream(PRIVATE/(f'{phase}-{tape.arm}-{tape.pool}-scores-signed.jsonl'),key());existing={e['record']['id']:e for e in attest.records};assert len(existing)==len(attest.records)
 for case in cases(tape.pool):
  receipt=tape.index['EXECUTED_TRANSITION',case['id']];r=receipt['record'];output,visible=get_prediction(tape,receipt);assert visible==case['visible'];result=endpoint(case,output['text'],r['actual_next_observation']);pred=result['prediction'];fields={s:pred is not None and pred[s]==result['actual'][s] for s in visible['sensors']}
  record=dict(id=case['id'],study_id=STUDY_ID,execution_receipt_sha256=sha(receipt),prediction_sha256=sha(output['text']),actual_next_observation=result['actual'],raw_freeze_commit=raw_commit(phase),exact_correct=result['exact'],field_correctness=fields)
  if case['id'] in existing:assert existing[case['id']]['record']==record
  else:existing[case['id']]=attest.append('SCORING_ATTESTATION',record)
  if case['pool'][0] in 'HV':validate_bundle(receipt,existing[case['id']],case,visible,output['text'],tape.auth)
  result.update(execution_receipt_sha256=sha(receipt),scoring_attestation_sha256=sha(existing[case['id']]),raw_prediction_sha256=sha(output['text']));scored.append(result)
 attest.verify();write_rows(P/(tape.arm+'-'+tape.pool+'-scored.jsonl'),scored);return scored

def score_controls(tape):
 results=[]
 for c in cases(tape.pool):
  visible=json.loads(canon(c['visible']));target=c['target'];executed=[];invalid=0;errors=0
  for step in range(1,ACTION_BUDGET+1):
   rid=f'{c["id"]}-step-{step}';receipt=tape.index.get(('EXECUTED_TRANSITION',rid))
   if not receipt:break
   response=tape.index['PREDICTION_BATCH',rid]['record']['outputs'];req=tape.index['REQUEST_BATCH',rid]['record'];variants=[dict(visible,candidate_action=a) for a in visible['actuators']];assert req['visible']==variants
   predictions=[parse(o['text'],visible['sensors']) for o in response];selected=choose(visible,target,predictions);j=visible['actuators'].index(selected);r=receipt['record'];assert r['executed_action']==selected and r['output_index']==j and r['request_sha256']==sha(variants[j]) and r['prediction_sha256']==sha(response[j]['text'])
   observation=r['actual_next_observation'];invalid+=predictions[j] is None;errors+=predictions[j]!=observation;executed.append(receipt)
   visible['history'].append([selected,''.join(str(observation[s]) for s in visible['sensors'])])
   if observation==target:break
  assert executed;terminal=tape.index['CONTROL_TERMINAL',c['id']]['record'];assert terminal['actions']==len(executed) and terminal['last_observation']==observation and terminal['target']==target
  success=observation==target;assert success or len(executed)==ACTION_BUDGET
  result=dict(id=c['id'],success=success,actions=len(executed),prediction_errors=errors,selected_schema_invalid=invalid,failure_modes=[] if success else ['action_budget_exhausted']+(['selected_prediction_schema_invalid'] if invalid else []),family=c['family']);results.append(result)
 write_rows(P/(tape.arm+'-'+tape.pool+'-control-scored.jsonl'),results);return results

def score_temporal(tape):
 outputs=[]
 for e in tape.stream.records:
  if e['kind']=='PREDICTION_BATCH':
   request=tape.index['REQUEST_BATCH',e['record']['id']]['record'];outputs += [dict(o,id=cid) for cid,o in zip(request['case_ids'],e['record']['outputs'])]
 old=rows(OLD/'materialized/T1.jsonl');assert len(outputs)==len(old)==540;scored=stack.temporal_analysis.score(old,outputs);write_rows(P/(tape.arm+'-temporal-T1-scored.jsonl'),scored)
 return dict(joint_correct=sum(x['joint'] for x in scored),schema_valid=sum(x['schema'] for x in scored),total=len(scored),reference_joint_correct=540,loss_pp=100*(540-sum(x['joint'] for x in scored))/540)

def replay_sample(entries,count,seed,stratum):
 assert entries;groups=defaultdict(list)
 for e in entries:groups[stratum(e)].append(e)
 keys=sorted(groups);rng=random.Random(seed)
 for values in groups.values():rng.shuffle(values)
 return [dict(groups[keys[i%len(keys)]][(i//len(keys))%len(groups[keys[i%len(keys)]])]) for i in range(count)]
def prepare_temporal_replay():
 training=rows(OLD/'D1.jsonl');lookup={x['id']:x for x in rows(OLD/'materialized/H1.jsonl')};eligible=sorted({x['case_id'] for x in training if x['source']!='counterfactual'});assert all(i in lookup for i in eligible)
 samples=replay_sample([lookup[i] for i in eligible],512,SEED+60000,lambda c:canon(c['gold']));out=[]
 for c in samples:out.append(dict(source='prior_temporal_training_replay',case_id=c['id'],messages=stack.temporal_data.messages(c),target=canon(c['gold'])))
 write_rows(P/'prior-temporal-training-replay.jsonl',out);dump(P/'prior-temporal-replay-lineage.json',dict(prior_D1_sha256=filehash(OLD/'D1.jsonl'),prior_D1_freeze_commit=git('log','-1','--format=%H','--','research/qwen-error-driven-qlora-learning-v0/D1.jsonl'),eligible_unique_prior_H1_training_cases=len(eligible),selected_exposures=len(out),counterfactual_targets_used=False,sealed_targets_used=False,scope='Explicitly authorized retention exception: only previously admitted H1 temporal TRAINING examples, not causal-program oracle labels.'))
 return out

def construct_training(cycle,tapes,scored):
 arm=f'C{cycle-1}';pool=f'H{cycle}';tape=tapes[arm,pool];lookup={c['id']:c for c in cases(pool)};entries=[]
 attest=Stream(PRIVATE/(f'harvest{cycle}-{arm}-{pool}-scores-signed.jsonl'),key());proofs={e['record']['id']:e for e in attest.verify()}
 for s in scored:
  c=lookup[s['id']];receipt=tape.index['EXECUTED_TRANSITION',c['id']];o,v=get_prediction(tape,receipt);target=validate_bundle(receipt,proofs[c['id']],c,v,o['text'],tape.auth)
  entries.append(dict(source='causal_correct_replay' if s['exact'] else 'causal_error',case_id=c['id'],family=c['family'],messages=messages(v),target=canon({'next_observation':target}),stratum=c['family']+':'+''.join(str(target[name]) for name in v['sensors']),execution_receipt_sha256=sha(receipt),scoring_attestation_sha256=sha(proofs[c['id']])))
 errors=[x for x in entries if x['source']=='causal_error'];correct=[x for x in entries if x['source']=='causal_correct_replay']
 if not errors or not correct:raise RuntimeError('ADMISSION_STOP_NO_ERRORS' if not errors else 'ADMISSION_STOP_NO_CORRECT_REPLAY')
 result=list(errors)+replay_sample(correct,len(errors),SEED+cycle*1000,lambda x:x['stratum'])
 if cycle==2:
  old=[x for x in rows(P/'D1.jsonl') if x['source'] in ['causal_error','causal_correct_replay']]
  replay=replay_sample(old,256,SEED+202,lambda x:x['stratum'])
  for r in replay:r['source']='cycle1_authenticated_replay'
  result+=replay
 result+=rows(P/'prior-temporal-training-replay.jsonl')
 for i,r in enumerate(result):r['training_id']=f'D{cycle}-{i:05d}'
 composition=dict(harvest=len(entries),errors=len(errors),correct=len(correct),composition=dict(Counter(e['source'] for e in result)),exposures_per_epoch=len(result),unique_source_cases=len({e['case_id'] for e in result}),all_authenticated_errors_admitted=True,unexecuted_causal_counterfactual_targets=0,hidden_program_labels=0,prior_temporal_replay_exposures=512)
 return result,composition
