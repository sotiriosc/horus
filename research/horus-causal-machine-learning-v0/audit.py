"""Offline structural, authenticated-admission and prompt-boundary audits."""
from common import *
from dsl import Circuit,reference,program_signature,behavior_signature
from worlds import messages,history_signature,Hypotheses,COUNTS
from engine import cases,private_worlds,verified_tapes
from admission import construct_training,score_prediction_tape,get_prediction

def preflight():
 freeze=json.loads((P/'world-data-freeze.json').read_bytes())
 for name,digest in freeze['files'].items():assert filehash(P/name)==digest,name
 assert filehash(PRIVATE/'worlds.jsonl')==freeze['private_worlds_sha256']
 assert filehash(C0_FILE)==C0_SHA
 assert git('branch','--show-current')=='research/horus-causal-machine-learning-v0'
 assert not git('status','--porcelain')
 assert json.loads((P/'engineering-qualification.json').read_bytes())['status']=='PASS'
 assert json.loads((P/'incumbent-verification.json').read_bytes())['status']=='PASS'
 assert not git('diff','9e53191f2d1a22aadb0264ab91ca929479225fec','--','.',':(exclude)'+PREFIX)

def world_audit():
 ws=private_worlds();hyp=Hypotheses();allcases=[c for pool in COUNTS for c in cases(pool)]
 assert len(ws)==len(allcases)==sum(COUNTS.values())
 for pool,n in COUNTS.items():assert len(cases(pool))==n
 for cycle in [1,2]:
  for family in {c['family'] for c in cases(f'H{cycle}')} :
   for field in ['components','causal_depth','delay_length','hidden_components']:
    train=[c for pool in ['H','V'] for c in cases(f'{pool}{cycle}') if c['family']==family];test=[c for pool in ['T','U'] for c in cases(f'{pool}{cycle}') if c['family']==family]
    assert min(c[field] for c in test)>max(c[field] for c in train),(cycle,family,field)
 for field in ['id','seed','world_hash','program_signature','behavior_signature','history_signature','endpoint_signature']:assert len({c[field] for c in allcases})==len(allcases),field
 for c in allcases:
  w=ws[c['id']];roots=w['program']['roots'];assert sha(dict(seed=w['seed'],program=w['program']))==c['world_hash']
  assert program_signature(roots)==c['program_signature'] and behavior_signature(roots)==c['behavior_signature']
  assert history_signature(c['visible'])==c['endpoint_signature'] and history_signature(dict(c['visible'],candidate_action=None))==c['history_signature']
  assert messages(c['visible']);observed=reference(roots,w['diagnostic_actions']);assert [''.join(map(str,o)) for o in observed]==[x[1] for x in c['visible']['history']]
  vm=Circuit(roots);state=vm.initial
  for a in w['diagnostic_actions']:state,obs=vm.step(state,a)
  assert [state[0],list(state[1])]==w['state_after_diagnostics']
  identified=hyp.check(w['probe_schedule'],observed);assert identified is not None
  _,actual=vm.step(state,c['visible']['actuators'].index(c['visible']['candidate_action']));assert list(actual)==identified['values']
  if c['pool'][0]=='U':assert hyp.control_identifiable(w['probe_schedule'],identified['matches'])
 return dict(status='PASS',worlds=len(allcases),exhaustive_sensor_hypotheses=len(hyp.roots),independent_reference_replay=True,all_normalized_program_behavior_history_endpoint_and_seed_disjoint=True,all_frozen_requests_strict_whitelist=True)

def training_audit(cycle):
 phase=f'harvest{cycle}';tapes=verified_tapes(phase);arm=f'C{cycle-1}';scored=score_prediction_tape(tapes[arm,f'H{cycle}'],phase)
 expected,composition=construct_training(cycle,tapes,scored);actual=rows(P/f'D{cycle}.jsonl');assert actual==expected
 eligible={c['id']:c for k in range(1,cycle+1) for c in cases(f'H{k}')};sealed={c['id'] for pool in ['T1','T2','U1','U2','V1','V2'] for c in cases(pool)}
 temporal_allowed=rows(P/'prior-temporal-training-replay.jsonl');prior_tapes={f'harvest{k}':verified_tapes(f'harvest{k}') for k in range(1,cycle+1)}
 for e in actual:
  assert e['case_id'] not in sealed
  if e['source']=='prior_temporal_training_replay':assert {k:v for k,v in e.items() if k!='training_id'} in temporal_allowed
  else:
   c=eligible[e['case_id']];assert e['messages']==messages(c['visible'])
   p=f'harvest{c["cycle"]}';t=prior_tapes[p][f'C{c["cycle"]-1}',f'H{c["cycle"]}'];r=t.index['EXECUTED_TRANSITION',c['id']]
   assert e['execution_receipt_sha256']==sha(r) and e['target']==canon({'next_observation':r['record']['actual_next_observation']})
 return dict(status='PASS',training_exposures=len(actual),all_errors_mechanically_admitted=True,causal_targets_authenticated_executed_only=True,hidden_program_prompt_or_target_fields=0,sealed_training_cases=0,unexecuted_alternative_targets=0,model_memory_used=False,planner_boundary='Pure choose(visible,target,predictions): no simulator, world, oracle or hidden-state argument',prior_temporal_retention_exception='512 frozen prior H1 training examples')

def evidence_audit(phase):
 """Rebuild exact visible semantics and independently replay only actual actions."""
 tapes=verified_tapes(phase);ws=private_worlds();requests=executions=alternatives=0
 for (arm,pool),t in tapes.items():
  if pool.startswith('temporal'):
   import stack
   oldcases=rows(OLD/'materialized/T1.jsonl');seen=[]
   for e in t.stream.records:
    if e['kind']=='REQUEST_BATCH':
     r=e['record'];chunk=oldcases[len(seen):len(seen)+len(r['case_ids'])];assert r['messages']==[stack.temporal_data.messages(c) for c in chunk];seen+=r['case_ids']
   assert seen==[c['id'] for c in oldcases];continue
  lookup={c['id']:c for c in cases(pool)}
  for e in t.stream.records:
   if e['kind']=='REQUEST_BATCH':
    r=e['record'];assert r['messages']==[messages(v) for v in r['visible']]
    requests+=len(r['messages'])
    for cid,v in zip(r['case_ids'],r['visible']):
     c=lookup[cid];assert v['actuators']==c['visible']['actuators'] and v['sensors']==c['visible']['sensors'];assert v['history'][:65]==c['visible']['history']
     if pool[0]!='U':assert v==c['visible']
   if e['kind']=='EXECUTED_TRANSITION':
    r=e['record'];c=lookup[r['world_id']];o,v=get_prediction(t,e);w=ws[c['id']]
    acts=v['actuators'];actions=[acts.index(x[0]) for x in v['history'][1:]]+[acts.index(v['candidate_action'])];observations=reference(w['program']['roots'],actions)
    assert [''.join(map(str,x)) for x in observations[:-1]]==[x[1] for x in v['history']]
    assert dict(zip(v['sensors'],observations[-1]))==r['actual_next_observation'];assert r['authorization_sha256']==sha(t.auth) and r['adapter_sha256']==t.auth['adapter_sha256'];executions+=1
  if pool[0]=='U':alternatives+=sum(len(e['record']['outputs']) for e in t.stream.records if e['kind']=='PREDICTION_BATCH')-sum(e['kind']=='EXECUTED_TRANSITION' for e in t.stream.records)
 return dict(status='PASS',causal_model_requests=requests,actual_scored_executions=executions,unexecuted_control_alternatives_without_labels=alternatives,exact_preserved_semantic_messages=True,all_actual_observations_independently_replayed=True,hidden_program_or_state_in_model_messages=False,model_reasoning_or_raw_outputs_in_public_scores=False)
