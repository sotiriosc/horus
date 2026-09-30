"""Public operational workloads from preserved Horus requests, no answer labels."""
import json,random
from .runtime import PUBLIC,ROOT,request,sha,write
from experiments.grounded_self_diagnosis_v0.protocol import build_inputs,SYSTEM
from experiments.grounded_authority_autonomous_agent_v0.protocol import ACTION_SYSTEM,GOAL
from experiments.modern_memory_vs_horus_v0.storage import canonical

def main():
 inputs=build_inputs();workloads=[]
 schema={'type':'object','properties':{'selected_action':{'type':'string','enum':['ADVANCE','HOLD','RETREAT']}},'required':['selected_action'],'additionalProperties':False}
 for profile in range(4):
  for j,run in enumerate(('A','B','C')):
   source=inputs[run]
   if profile==0:
    d=source['completed_decisions'][(0,5,10)[j]]
    payload=dict(goal=GOAL,current_state=d['world_state'],available_actions=d['admissible_actions'],grounded_assessments=d['action_assessments'],recent_agent_working_context=[])
    r=request(ACTION_SYSTEM,canonical(payload),64,schema);validator='action'
    derivation=dict(run=run,decision=(0,5,10)[j]+1,fields='goal,current_state,available_actions,grounded_assessments; no selected answer or future consequence')
   else:
    n=({1:5,2:11}[profile] if profile<3 else (26,28,30)[j]);start=0 if profile==3 else (0,6,12)[j];payload={**source,'completed_decisions':source['completed_decisions'][start:start+n]}
    r=request(SYSTEM,canonical(payload),1024);validator='review';derivation=dict(run=run,first_decision=start+1,decision_count=n,fields='public-safe historical review input; no prior review answer or evaluation labels')
   name=f'P{profile}-{j}';f=PUBLIC/'workloads'/f'{name}.json';write(f,r)
   workloads.append(dict(id=name,profile=profile,request_path=str(f.relative_to(ROOT)),sha256=sha(f.read_bytes()),validator=validator,source='experiments.grounded_self_diagnosis_v0.protocol.build_inputs',source_base='26cdae9de75811dd492d32de8f3337e0b67d09b7',derivation=derivation,cap=r['max_tokens'],prompt_characters=len(r['messages'][1]['content'])))
 assert len({sha((ROOT/w['request_path']).read_bytes()) for w in workloads})==12,'Independent prompts required'
 rng=random.Random(29092026);profile_order=list(range(4));rng.shuffle(profile_order);prompt_orders={p:rng.sample(list(range(3)),3) for p in range(4)};schedule=[]
 for half in range(2):
  for p in profile_order:
   for j in prompt_orders[p]:
    order=['A','B','C'];rng.shuffle(order)
    schedule.append(dict(index=len(schedule)+1,half=half,profile=p,workload=f'P{p}-{j}',arm_order=order))
 write(PUBLIC/'workload-manifest.json',dict(profiles={str(p):{'label':f'P{p}','shape':['structured action','5-decision review','11-decision review','30-decision review'][p],'independent_prompts':3} for p in range(4)},workloads=workloads))
 write(PUBLIC/'schedule.json',dict(seed=29092026,decisions_per_arm=24,arms=['A','B','C'],restart_after_schedule_index=12,schedule=schedule,profile_order=profile_order,prompt_orders=prompt_orders,policy_visibility='current profile state and authenticated local history only; no prompt identity, arm order, global schedule index or future position'))
 print(json.dumps(dict(workloads=12,decisions_per_arm=24,profiles=4)))
if __name__=='__main__':main()
