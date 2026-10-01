"""Prospective world construction and independent exhaustive ambiguity checks."""
import argparse,collections,itertools,json,random,time
from pathlib import Path
from dsl import *
SEED=20261001
N_SENSORS=4
PROBE_LENGTH=64
PROBE_SCHEDULES=16
COUNTS={'H1':960,'V1':240,'T1':480,'U1':40,'H2':960,'V2':240,'T2':480,'U2':40}
FAMILIES={1:['delayed_combination','input_gated_delay','conditional_delay'],2:['parity_interaction','persistent_latch','counter_threshold']}
SYSTEM='Predict the next observable state of this unfamiliar deterministic binary machine from its executed intervention history. Every actuator starts at 0 after RESET. An action toggles exactly its named actuator. Each history pair is [action, observed sensor bits], with bits in the listed sensors order. Internal dynamics are hidden. Return only JSON with exactly one key next_observation, mapping every listed sensor name to an integer 0 or 1. Do not explain.'
def messages(visible):
 assert set(visible)=={'actuators','sensors','history','candidate_action'}
 import re
 assert len(visible['actuators'])==N_INPUTS and len(visible['sensors'])==N_SENSORS
 names=visible['actuators']+visible['sensors'];assert len(set(names))==len(names) and all(re.fullmatch('[A-Z][0-9]',x) for x in names)
 assert visible['candidate_action'] in visible['actuators'] and visible['history']
 for i,row in enumerate(visible['history']):
  assert isinstance(row,list) and len(row)==2 and row[0] in (['RESET'] if i==0 else visible['actuators'])
  assert isinstance(row[1],str) and len(row[1])==N_SENSORS and set(row[1])<={'0','1'}
 return [{'role':'system','content':SYSTEM},{'role':'user','content':canon(visible)}]
def history_signature(visible,target=None):
 acts=visible['actuators'];seen={};sequence=[]
 for action,bits in visible['history']:
  if action=='RESET':sequence.append('R');continue
  if action not in seen:seen[action]=len(seen)
  sequence.append(seen[action])
 candidate=visible.get('candidate_action')
 if candidate is not None and candidate not in seen:seen[candidate]=len(seen)
 columns=[]
 for j,s in enumerate(visible['sensors']):
  col=''.join(row[1][j] for row in visible['history'])
  if target is not None:col+=':'+str(target[s])
  columns.append(col)
 return sha(dict(n_actuators=len(acts),actions=sequence,sensor_columns=sorted(columns),candidate=None if candidate is None else seen[candidate]))
def probes():
 schedules=[]
 for index in range(PROBE_SCHEDULES):
  rng=random.Random(SEED+10000+index)
  while True:
   actions=[rng.randrange(N_INPUTS) for _ in range(PROBE_LENGTH)];query=rng.randrange(N_INPUTS);bits=0;edges=set()
   for a in actions:nxt=bits^(1<<a);edges.add((bits,nxt));bits=nxt
   if (bits,bits^(1<<query)) not in edges:break
  schedules.append((tuple(actions),query))
 return schedules
class Hypotheses:
 def __init__(self):
  self.entries=catalog();self.roots=[c['expression'] for c in self.entries];self.schedules=probes();self.tables={}
 def table(self,index):
  if index in self.tables:return self.tables[index]
  actions,query=self.schedules[index];groups=collections.defaultdict(list)
  for i,e in enumerate(self.roots):
   output=reference([e],(*actions,query));column=bytes(o[0] for o in output[:-1]);groups[column].append((i,output[-1][0]))
  self.tables[index]=dict(groups);return self.tables[index]
 def check(self,index,observations):
  groups=self.table(index);matches=[];values=[]
  for j in range(N_SENSORS):
   candidates=groups.get(bytes(o[j] for o in observations),[])
   if not candidates:return None
   bits={bit for _,bit in candidates}
   if len(bits)!=1:return None
   matches.append([i for i,_ in candidates]);values.append(next(iter(bits)))
  return dict(matches=matches,values=values)
 def control_identifiable(self,index,matches,budget=4):
  # Independent reference states, not simulator states, for all consistent roots.
  actions,_=self.schedules[index]
  for candidates in matches:
   unique={}
   for i in candidates:unique.setdefault(behavior_signatures(canon(self.roots[i]))[0],i)
   if len(unique)==1:continue
   initial=[]
   for i in unique.values():
    _,state=reference([self.roots[i]],actions,return_state=True);initial.append((i,state))
   frontier=[initial]
   for depth in range(budget):
    following=[]
    for hypotheses in frontier:
     for a in range(N_INPUTS):
      advanced=[];predictions=set()
      for i,state in hypotheses:
       observed,nxt=reference([self.roots[i]],[a],state=state,return_state=True);predictions.add(observed[-1][0]);advanced.append((i,nxt))
      if len(predictions)!=1:return False
      following.append(advanced)
    frontier=following
  return True

def make_worlds(out,counts=COUNTS):
 out=Path(out);out.mkdir(parents=True,exist_ok=False);hyp=Hypotheses();start=time.monotonic();programs=set();behaviors=set();histories=set();seeds=set();rejections=collections.Counter();world_rows=[];manifest={};max_features={}
 pool_entries={}
 for c in hyp.entries:pool_entries.setdefault((c['cycle'],c['family'],c['level']),[]).append(c)
 for pool,count in counts.items():
  cycle=int(pool[-1]);level='test' if pool[0] in 'TU' else 'train';cases=[];attempt=0;pool_seed=SEED+10000000*(list(COUNTS).index(pool)+1)
  while len(cases)<count:
   attempt+=1
   if attempt>count*200:raise RuntimeError(('Too many prospective invalid/colliding candidates',pool,len(cases),dict(rejections)))
   family=len(cases)%3;world_seed=pool_seed+attempt;rng=random.Random(world_seed);entries=rng.sample(pool_entries[cycle,family,level],N_SENSORS);roots=[c['expression'] for c in entries]
   pg=program_signature(roots)
   if pg in programs:rejections['program_graph_equivalence']+=1;continue
   bg=behavior_signature(roots)
   if bg in behaviors:rejections['exact_behavior_equivalence']+=1;continue
   index=rng.randrange(PROBE_SCHEDULES);actions,query=hyp.schedules[index];vm=Circuit(roots);state=vm.initial;observed=[vm.observation(state)]
   for a in actions:state,obs=vm.step(state,a);observed.append(obs)
   assert observed==reference(roots,actions)
   if any(len({o[j] for o in observed})<2 for j in range(N_SENSORS)):rejections['uninformative_diagnostic_sensor']+=1;continue
   identified=hyp.check(index,observed)
   if identified is None:rejections['ambiguous_prediction']+=1;continue
   checkstate,checkobs=vm.step(state,query);assert list(checkobs)==identified['values'] # endpoint validation only, never a training target
   labels=rng.sample([chr(65+i)+str(j) for i in range(26) for j in range(10)],N_INPUTS+N_SENSORS);actuators=labels[:N_INPUTS];sensors=labels[N_INPUTS:]
   visible=dict(actuators=actuators,sensors=sensors,history=[['RESET',''.join(map(str,observed[0]))]]+[[actuators[a],''.join(map(str,o))] for a,o in zip(actions,observed[1:])],candidate_action=actuators[query])
   endpoint_signature=history_signature(visible);hs=history_signature(dict(visible,candidate_action=None))
   if hs in histories:rejections['normalized_history_and_query']+=1;continue
   target=None
   if pool[0]=='U':
    # Target is chosen without oracle advice; oracle only accepts/rejects reachability.
    target_bits=tuple(rng.randrange(2) for _ in sensors)
    if target_bits==observed[-1]:rejections['control_already_at_target']+=1;continue
    if not hyp.control_identifiable(index,identified['matches']):rejections['ambiguous_control_horizon']+=1;continue
    frontier=[state];reachable=False
    for depth in range(4):
     following=[]
     for st in frontier:
      for a in range(N_INPUTS):
       nxt,o=vm.step(st,a);following.append(nxt);reachable|=o==target_bits
     frontier=following
    if not reachable:rejections['unreachable_control_target']+=1;continue
    target=dict(zip(sensors,target_bits))
   assert world_seed not in seeds;seeds.add(world_seed);programs.add(pg);behaviors.add(bg);histories.add(hs)
   world_id=f'{pool}-{len(cases):04d}';program=dict(roots=roots,initial_inputs=0,initial_registers_zero=True);world_hash=sha(dict(seed=world_seed,program=program));metrics=dict(components=sum(c['features']['components'] for c in entries),causal_depth=max(c['features']['depth'] for c in entries),delay_length=max(c['features']['delay_chain'] for c in entries),hidden_components=sum(c['features']['registers'] for c in entries),persistent_components=sum(c['features']['persistent'] for c in entries))
   case=dict(id=world_id,pool=pool,cycle=cycle,seed=world_seed,world_hash=world_hash,program_signature=pg,behavior_signature=bg,history_signature=hs,endpoint_signature=endpoint_signature,family=FAMILIES[cycle][family],**metrics,visible=visible,identifiability=dict(exhaustive_declared_sensor_hypotheses=len(hyp.roots),consistent_per_sensor=[len(x) for x in identified['matches']],unique_next_observation=True,control_all_action_paths_budget4=pool[0]=='U'))
   if target is not None:case['target']=target
   cases.append(case);world_rows.append(dict(id=world_id,seed=world_seed,world_hash=world_hash,program=program,probe_schedule=index,diagnostic_actions=actions,state_after_diagnostics=state,last_observation=observed[-1],diagnostic_transitions_executed=len(actions)))
   if len(cases)%80==0:print(json.dumps(dict(stage='offline-world-construction',pool=pool,done=len(cases),total=count,elapsed_seconds=round(time.monotonic()-start,1))),flush=True)
  (out/(pool+'.jsonl')).write_text(''.join(canon(x)+'\n' for x in cases));manifest[pool]=dict(count=len(cases),worlds=len(cases),prediction_endpoints=0 if pool[0]=='U' else len(cases),diagnostic_execution_steps=len(cases)*PROBE_LENGTH,seed_base=pool_seed,candidate_attempts=attempt,families=dict(collections.Counter(x['family'] for x in cases)),feature_ranges={k:[min(c[k] for c in cases),max(c[k] for c in cases)] for k in metrics})
  print(json.dumps(dict(stage='offline-pool-complete',pool=pool,**manifest[pool])),flush=True)
 (out/'worlds-private.jsonl').write_text(''.join(canon(x)+'\n' for x in world_rows))
 report=dict(seed=SEED,counts=manifest,declared_sensor_hypotheses=len(hyp.roots),hypothesis_family='Cartesian product of the complete finite sensor-root catalog, independent of actual sampling family/level and without oracle narrowing.',rejections=dict(rejections),all_exact_program_graph_and_behavior_and_history_signatures_disjoint=True,probe_schedules=[dict(actions=a,candidate_action=q) for a,q in hyp.schedules],wall_seconds=round(time.monotonic()-start,2))
 (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--sample',type=int);a=p.parse_args();print(json.dumps(make_worlds(a.out,COUNTS if a.sample is None else {k:a.sample for k in COUNTS})),flush=True)
