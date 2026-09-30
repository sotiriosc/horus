"""Independent finite-world auditor; no import of author or generator."""
import json
from collections import Counter,defaultdict
from common import *
def audit_case(c):
 s,w=c['state'],c['witness'];assert s['proposition_scope']==SCOPE
 aa=w['assertions'];values=defaultdict(set)
 for a in aa:values[a['subject']].add(a['value'])
 conflict=any(len(v)>1 for v in values.values())
 assert s['package']==dict(same_referent=aa[0]['subject']==aa[1]['subject'],equal_value=aa[0]['value']==aa[1]['value'],consistency='CONTRADICTORY' if conflict else 'CONSISTENT')
 assert len(s['non_current_trials'])==len(w['non_current'])
 outcomes=[]
 for i,(t,v) in enumerate(zip([s['current_trial']]+s['non_current_trials'],[w['current']]+w['non_current'])):
  domain=v['admissible_inputs'];assert domain and len(set(domain))==len(domain) and v['reference_input'] in domain and len(v['required_outputs'])==len(domain)
  assert v['deployed']==(i==0)
  vv={v['observed_output']!=v['required_outputs'][j] for j in domain};outcomes.append(vv)
  expected=dict(currentness='CURRENT' if i==0 else 'NOT_CURRENT',knownness='KNOWN' if len(domain)==1 else 'UNKNOWN',alternative_completion='ALTERNATIVE_EXISTS' if any(j!=v['reference_input'] for j in domain) else 'NO_ALTERNATIVE',observation_requirement='MATCH' if v['observed_output']==v['required_outputs'][v['reference_input']] else 'MISMATCH',evidence_sufficiency='DETERMINATE' if len(vv)==1 else 'UNDERDETERMINED')
  assert t==expected,(c['id'],i,t,expected)
 cur=outcomes[0];historical=any(v=={True} for v in outcomes[1:])
 candidates={X:conflict,U:not conflict and cur=={False,True},D:not conflict and cur=={True},T:not conflict and cur=={False} and historical,N:not conflict and cur=={False} and not historical}
 gold=[k for k,v in candidates.items() if v];assert gold==[c['gold']]
 return dict(id=c['id'],audited_gold=gold[0],possible_violation_by_trial=[sorted(v) for v in outcomes],conflict=conflict,proof='Every primitive was independently recomputed from all finite admissible worlds; exactly one ontology condition holds.',state_sha256=sha(raw(s)))
def delta(a,b,path=''):
 if isinstance(a,dict) and isinstance(b,dict):
  assert a.keys()==b.keys();return sum([delta(a[k],b[k],path+'.'+k) for k in a],[])
 if isinstance(a,list) and isinstance(b,list):
  assert len(a)==len(b);return sum([delta(x,y,path+'.'+str(i)) for i,(x,y) in enumerate(zip(a,b))],[])
 return [] if a==b else [dict(path=path,before=a,after=b)]
def validate():
 m=P/'materialized';cases=json.loads((m/'cases.json').read_bytes());pairs=json.loads((m/'pairs.json').read_bytes());manifest=json.loads((m/'render-manifest.json').read_bytes());lookup={c['id']:c for c in cases}
 assert len(cases)==len(lookup)==30 and len({canonical(c['state']) for c in cases})==30
 assert Counter(c['gold'] for c in cases)=={c:6 for c in CLASSES}
 proofs=[audit_case(c) for c in cases];pairproof=[];assert Counter(p['changing'] for p in pairs)=={True:5,False:3}
 for p in pairs:
  a,b=lookup[p['A']],lookup[p['B']];dd=delta(a['state'],b['state']);assert len(dd)==1 and dd[0]['path']==p['declared_field']
  assert (p['gold_A'],p['gold_B'])==(a['gold'],b['gold']) and p['changing']==(a['gold']!=b['gold'])
  pairproof.append(dict(id=p['id'],delta=dd,transition=[a['gold'],b['gold']],coupled_changes=False))
 entries={e['render_id']:e for e in manifest['entries']};schedule=manifest['schedule'];assert len(schedule)==len(set(schedule))==90 and set(schedule)==set(entries)
 assert all(entries[a]['state_id']!=entries[b]['state_id'] for a,b in zip(schedule,schedule[1:]))
 for i in range(0,90,15):
  ee=[entries[x] for x in schedule[i:i+15]];assert Counter(e['arm'] for e in ee)=={a:5 for a in ARMS};assert Counter(lookup[e['state_id']]['gold'] for e in ee)=={c:3 for c in CLASSES}
 perms=Counter(tuple(e) for e in manifest['arm_order_by_state'].values());assert len(perms)==6 and set(perms.values())=={5}
 for c in cases:
  reqs=[]
  for arm in ARMS:
   rid=c['id']+'-'+arm;e=entries[rid];rb=(m/e['request_path']).read_bytes();assert sha(rb)==e['request_sha256'];r=json.loads(rb);reqs.append(r)
   assert r['messages'][0]['content']==CHARTERS[arm] and r['response_format']['schema']==SCHEMA and len(r['messages'])==2
   assert r['messages'][1]['content'].split('Primitive epistemic state:\n',1)[1]==raw(c['state']).decode()
   for forbidden in [c['id'],'author_proof','audited_gold','witness','rt-p']:assert forbidden not in str(r['messages'])
  assert len({canonical(r['messages'][1]) for r in reqs})==1
  assert len({canonical({k:v for k,v in r.items() if k!='messages'}) for r in reqs})==1
 assert all(label not in GENERIC+TEMPORAL for label in CLASSES)
 assert 'histor' not in GENERIC.lower() and 'non-current' not in GENERIC.lower()
 old=json.loads((P.parent/'qwen-primitive-to-ontology-reduction-v0/materialized/cases.json').read_bytes())
 assert not {c['id'] for c in cases}&{c['id'] for c in old}
 assert not {canonical(c['state']) for c in cases}&{canonical(c['state']) for c in old}
 # Every fresh state has >=2 independently scoped older trials; old states had <=1.
 assert all(len(c['state']['non_current_trials'])>=2 for c in cases)
 return dict(status='PASS',model_calls=0,states=30,requests=90,class_counts=Counter(c['gold'] for c in cases),changing_pairs=5,stable_pairs=3,pair_unique_endpoints=len({p[k] for p in pairs for k in ['A','B']}),all_single_field_deltas=True,identical_state_user_message_and_parameters_across_arms=True,no_charter_class_labels=True,prior_objects_or_ids_reused=False,prior_predictions_used=False,new_temporal_structures=True,arm_permutations={''.join(k):v for k,v in perms.items()},auditor_proofs=proofs,pair_proofs=pairproof)
if __name__=='__main__':dump(P/'validation.json',validate());print('Independent coherence, gold, temporal deltas, 3-arm isolation and freshness: PASS')
