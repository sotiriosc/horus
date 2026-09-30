"""Independent semantic audit using admissible-world enumeration, not author/gold rules."""
import itertools,json
from collections import Counter
from common import *
def audit_case(c):
 s,w=c['state'],c['witness'];assert s['proposition_scope']==SCOPE
 assert s['package']==dict(consistency='CONSISTENT' if len(set(w['provenance_values']))==1 else 'CONTRADICTORY')
 assert len(s['non_current_trials'])==len(w['non_current'])>=1
 outcomes=[]
 for i,(t,v) in enumerate(zip([s['current_trial']]+s['non_current_trials'],[w['current']]+w['non_current'])):
  domain=v['admissible_inputs'];assert domain and len(set(domain))==len(domain) and v['reference_input'] in domain and len(v['required_outputs'])==len(domain)
  assert v['deployed']==(i==0)
  vv={v['observed_output']!=v['required_outputs'][j] for j in domain};outcomes.append(vv)
  expected=dict(currentness='CURRENT' if i==0 else 'NOT_CURRENT',knownness='KNOWN' if len(domain)==1 else 'UNKNOWN',alternative_completion='ALTERNATIVE_EXISTS' if any(j!=v['reference_input'] for j in domain) else 'NO_ALTERNATIVE',observation_requirement='MATCH' if v['observed_output']==v['required_outputs'][v['reference_input']] else 'MISMATCH',evidence_sufficiency='DETERMINATE' if len(vv)==1 else 'UNDERDETERMINED')
  assert expected==t,(c['id'],i)
 # Independent trial inputs make every Cartesian combination admissible. Evaluate existential prior violation in each world.
 prior_worlds={any(completion) for completion in itertools.product(*outcomes[1:])}
 def label(values):return {frozenset([True]):'YES',frozenset([False]):'NO',frozenset([False,True]):'UNKNOWN'}[frozenset(values)]
 gold=dict(current_violation=label(outcomes[0]),prior_violation=label(prior_worlds));assert gold==c['gold']
 assert c['historical_focus']==(gold==dict(current_violation='NO',prior_violation='YES'))
 return dict(id=c['id'],audited_gold=gold,possible_violation_by_trial=[sorted(v) for v in outcomes],possible_any_prior_violation=sorted(prior_worlds),proof='Enumerated all independent admissible trial-completion combinations. Current truth set and existential older-trial truth set independently determine the two output fields. Separate provenance inconsistency is irrelevant by frozen scope.',state_sha256=sha(raw(s)))
def delta(a,b,path=''):
 if isinstance(a,dict) and isinstance(b,dict):
  assert a.keys()==b.keys();return sum([delta(a[k],b[k],path+'.'+k) for k in a],[])
 if isinstance(a,list) and isinstance(b,list):
  assert len(a)==len(b);return sum([delta(x,y,path+'.'+str(i)) for i,(x,y) in enumerate(zip(a,b))],[])
 return [] if a==b else [dict(path=path,before=a,after=b)]
def validate():
 m=P/'materialized';cases=json.loads((m/'cases.json').read_bytes());pairs=json.loads((m/'pairs.json').read_bytes());manifest=json.loads((m/'render-manifest.json').read_bytes());lookup={c['id']:c for c in cases}
 assert len(cases)==len(lookup)==36 and len({semantic_signature(c['state']) for c in cases})==36
 counts=Counter('/'.join(c['gold'][k] for k in FIELDS) for c in cases);assert counts==EXPECTED_COUNTS
 assert sum(c['historical_focus'] for c in cases)==12
 proofs=[audit_case(c) for c in cases];pairproof=[];assert len(pairs)==18 and Counter(p['changing'] for p in pairs)=={True:10,False:8}
 assert Counter(sid for p in pairs for sid in p['endpoints'].values())=={sid:1 for sid in lookup}
 for p in pairs:
  a,b=[lookup[p['endpoints'][k]] for k in 'AB'];d=delta(a['state'],b['state']);assert len(d)==1 and d[0]['path']==p['declared_field']
  assert p['gold_A']==a['gold'] and p['gold_B']==b['gold'] and p['changing']==(a['gold']!=b['gold'])
  if p['changing']:assert sum(a['gold'][k]!=b['gold'][k] for k in FIELDS)==1
  pairproof.append(dict(id=p['id'],delta=d,expected_outputs=[a['gold'],b['gold']],changing=p['changing'],coupled_changes=False))
 schedule=manifest['schedule'];assert len(schedule)==len(set(schedule))==36 and set(schedule)==set(lookup)
 assert all(lookup[a]['pair']!=lookup[b]['pair'] for a,b in zip(schedule,schedule[1:]))
 assert sum(schedule.index(p['endpoints']['A'])<schedule.index(p['endpoints']['B']) for p in pairs)==9
 for i in range(0,36,6):assert sum(lookup[sid]['historical_focus'] for sid in schedule[i:i+6])==2
 for e in manifest['entries']:
  r=(m/e['request_path']).read_bytes();assert sha(r)==e['request_sha256'];request=json.loads(r);c=lookup[e['render_id']]
  assert len(request['messages'])==2 and request['messages'][0]['content']==INSTRUCTION and request['response_format']['schema']==SCHEMA
  assert request['messages'][1]['content']==DEFINITIONS+'\n\nResolved primitive state:\n'+raw(c['state']).decode()
  for forbidden in FORBIDDEN_LABELS+[c['id'],c['pair'],'author_proof','witness','historical_focus']:
   assert forbidden not in str(request['messages'])
  assert not any(k in raw(c['state']).decode() for k in FIELDS)
 return dict(status='PASS',model_calls=0,states=36,requests=36,combination_counts=counts,historical_focus=12,changing_pairs=10,stable_pairs=8,all_pairs_disjoint=True,all_single_field_changes=True,AB_first=9,BA_first=9,five_class_labels_or_definitions_in_prompts=False,answer_fields_in_input_state=False,prior_trial_counts=Counter(len(c['state']['non_current_trials']) for c in cases),contradictory_states=sum(c['state']['package']['consistency']=='CONTRADICTORY' for c in cases),auditor_proofs=proofs,pair_proofs=pairproof)
if __name__=='__main__':dump(P/'validation.json',validate());print('Independent field gold, coherence, exact balance, pairs and prompt isolation: PASS')
