"""Independent witness auditor: enumerate possible compliance outcomes, never import author/gold code."""
import json
from collections import Counter,defaultdict
from common import *
def audit_case(case):
 s,w=case['state'],case['witness']; a=w['assertions'];by=defaultdict(set)
 for row in a:by[row['subject']].add(row['value'])
 invalid=any(len(v)>1 for v in by.values())
 assert s['proposition_scope']==SCOPE
 assert s['package']==dict(same_referent=a[0]['subject']==a[1]['subject'],equal_value=a[0]['value']==a[1]['value'],consistency='CONTRADICTORY' if invalid else 'CONSISTENT')
 outcomes={}
 for key,wkey,deployed in [('current_trial','current',True),('historical_trial','historical',False)]:
  t,v=s[key],w[wkey]
  if t is None:assert v is None;outcomes[wkey]=set();continue
  assert v['deployed']==deployed and v['reference_input'] in v['admissible_inputs']
  assert len(v['required_outputs'])==len(v['admissible_inputs']) and len(set(v['admissible_inputs']))==len(v['admissible_inputs'])
  results={v['observed_output']!=v['required_outputs'][i] for i in v['admissible_inputs']};outcomes[wkey]=results
  expected=dict(currentness='CURRENT' if deployed else 'NOT_CURRENT',knownness='KNOWN' if len(v['admissible_inputs'])==1 else 'UNKNOWN',alternative_completion='ALTERNATIVE_EXISTS' if any(i!=v['reference_input'] for i in v['admissible_inputs']) else 'NO_ALTERNATIVE',observation_requirement='MATCH' if v['observed_output']==v['required_outputs'][v['reference_input']] else 'MISMATCH',evidence_sufficiency='DETERMINATE' if len(results)==1 else 'UNDERDETERMINED')
  assert t==expected,(case['id'],t,expected)
 # Classification by mutually exclusive semantic conditions, independent of author precedence procedure.
 cur,hist=outcomes['current'],outcomes['historical']
 conditions={X:invalid,U:not invalid and cur=={False,True},D:not invalid and cur=={True},T:not invalid and cur=={False} and hist=={True},N:not invalid and cur=={False} and hist!={True}}
 selected=[c for c,b in conditions.items() if b];assert selected==[case['gold']]
 return dict(id=case['id'],audited_gold=selected[0],current_possible_violation=sorted(cur),historical_possible_violation=sorted(hist),immutable_conflict=invalid,proof='Enumerated all admissible input completions; independently recomputed every primitive. Exactly one ontology condition holds.',state_sha256=sha(raw(s)))
def delta(a,b,path=''):
 if isinstance(a,dict) and isinstance(b,dict):
  assert a.keys()==b.keys()
  return sum([delta(a[k],b[k],path+'.'+k) for k in a],[])
 return [] if a==b else [dict(path=path,before=a,after=b)]
def validate():
 m=P/'materialized';cases=json.loads((m/'cases.json').read_bytes());pairs=json.loads((m/'pairs.json').read_bytes());manifest=json.loads((m/'render-manifest.json').read_bytes());lookup={c['id']:c for c in cases}
 assert len(cases)==len(lookup)==50 and len(pairs)==25
 assert len({canonical(c['state']) for c in cases})==50
 assert Counter(c['gold'] for c in cases)=={c:10 for c in CLASSES}
 proofs=[audit_case(c) for c in cases];pairproof=[]
 for p in pairs:
  a,b=[lookup[p['endpoints'][side]] for side in 'AB'];d=delta(a['state'],b['state']);assert len(d)==1,(p['id'],d)
  assert p['changing']==(a['gold']!=b['gold']);assert (p['gold_A'],p['gold_B'])==(a['gold'],b['gold'])
  pairproof.append(dict(id=p['id'],delta=d,expected_transition=[a['gold'],b['gold']],class_changes=p['changing']))
 schedule=manifest['schedule'];assert len(schedule)==len(set(schedule))==50 and set(schedule)==set(lookup)
 assert all(lookup[a]['pair']!=lookup[b]['pair'] for a,b in zip(schedule,schedule[1:]))
 assert sum(schedule.index(p['endpoints']['A'])<schedule.index(p['endpoints']['B']) for p in pairs)==13
 for i in range(0,50,10):assert Counter(lookup[x]['gold'] for x in schedule[i:i+10])=={c:2 for c in CLASSES}
 for e in manifest['entries']:
  r=(m/e['request_path']).read_bytes();assert sha(r)==e['request_sha256'];req=json.loads(r);c=lookup[e['render_id']]
  assert len(req['messages'])==2 and req['response_format']['schema']==SCHEMA
  assert req['messages'][1]['content'].split('Primitive epistemic state:\n',1)[1]==raw(c['state']).decode()
  assert all(token not in req['messages'][1]['content'] for token in [c['id'],c['pair'],'author_proof','audited_gold','stratum','witness'])
 return dict(status='PASS',model_calls=0,states=50,pairs=25,changing_pairs=sum(p['changing'] for p in pairs),stable_pairs=sum(not p['changing'] for p in pairs),class_counts=Counter(c['gold'] for c in cases),stratum_counts=Counter(c['stratum'] for c in cases),auditor_proofs=proofs,pair_proofs=pairproof,all_pairs_one_field_delta=True,all_states_unique=True,AB_first=13,BA_first=12)
if __name__=='__main__':dump(P/'validation.json',validate());print('Independent coherence, all primitives, gold, deltas, exact balance and prompt isolation: PASS')
