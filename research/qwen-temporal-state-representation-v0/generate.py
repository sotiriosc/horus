"""Fresh prospective author with finite offline witnesses; never reads prior predictions."""
import copy,itertools,random
from collections import Counter
from common import *
def trial(obs='MATCH',suff='DETERMINATE',unknown=False,prior=False):
 return dict(currentness='NOT_CURRENT' if prior else 'CURRENT',knownness='UNKNOWN' if unknown else 'KNOWN',alternative_completion='ALTERNATIVE_EXISTS' if unknown else 'NO_ALTERNATIVE',observation_requirement=obs,evidence_sufficiency=suff)
def tstatus(t):
 return 'UNKNOWN' if t['evidence_sufficiency']=='UNDERDETERMINED' else 'YES' if t['observation_requirement']=='MISMATCH' else 'NO'
def author_gold(s):
 old=[tstatus(t) for t in s['non_current_trials']]
 return dict(current_violation=tstatus(s['current_trial']),prior_violation='YES' if 'YES' in old else 'UNKNOWN' if 'UNKNOWN' in old else 'NO')
def witness(s):
 def w(t):
  v=t['observation_requirement']=='MISMATCH';values=[v]
  if t['knownness']=='UNKNOWN':values.append(not v if t['evidence_sufficiency']=='UNDERDETERMINED' else v)
  return dict(deployed=t['currentness']=='CURRENT',reference_input=0,admissible_inputs=list(range(len(values))),observed_output=401,required_outputs=[409 if x else 401 for x in values])
 return dict(provenance_values=[503,509] if s['package']['consistency']=='CONTRADICTORY' else [503,503],current=w(s['current_trial']),non_current=[w(t) for t in s['non_current_trials']])
def old_signatures():
 signatures=set()
 # Access only state objects; no prior gold, model outputs or scored predictions are loaded.
 for name in ['qwen-primitive-to-ontology-reduction-v0','qwen-role-grounded-temporal-reduction-v0']:
  for f in (P.parent/name/'materialized/states').glob('*.json'):signatures.add(semantic_signature(json.loads(f.read_bytes())))
 # Conservatively include all 56 aligned-state projections, without reading outputs or gold.
 for f in (P.parent/'qwen-epistemic-primitive-factorization-v0/materialized/states').glob('*.json'):
  old=json.loads(f.read_bytes());deployment=old['deployment']['build'];assertions={}
  for row in old['assertions']:assertions.setdefault(canonical(row['subject']),set()).add(row['asserted_value'])
  converted=[]
  for t in old['trials']:
   inputs=t['admissible_inputs'] if t['reported_input']=='UNKNOWN' else [t['reported_input']]
   requirements={r['input']:r['result'] for r in t['required_results']}
   violations={t['observed_result']!=requirements[i] for i in inputs}
   converted.append(dict(currentness='CURRENT' if t['build']==deployment else 'NOT_CURRENT',knownness='KNOWN' if len(inputs)==1 else 'UNKNOWN',alternative_completion='ALTERNATIVE_EXISTS' if any(i!=t['reference_input'] for i in inputs) else 'NO_ALTERNATIVE',observation_requirement='MATCH' if t['observed_result']==requirements[t['reference_input']] else 'MISMATCH',evidence_sufficiency='DETERMINATE' if len(violations)==1 else 'UNDERDETERMINED'))
  current=[t for t in converted if t['currentness']=='CURRENT'];assert len(current)==1
  signatures.add(semantic_signature(dict(package=dict(consistency='CONTRADICTORY' if any(len(v)>1 for v in assertions.values()) else 'CONSISTENT'),current_trial=current[0],non_current_trials=[t for t in converted if t['currentness']=='NOT_CURRENT'])))
 return signatures

def generate():
 rng=random.Random(SEED);excluded=old_signatures();used=set();cases=[];pairs=[]
 NY=('NO','YES');YN=('YES','NO');NN=('NO','NO');UY=('UNKNOWN','YES');UN=('UNKNOWN','NO');YY=('YES','YES');NU=('NO','UNKNOWN');UU=('UNKNOWN','UNKNOWN')
 specs=[(NY,YY,'CURRENT_RELATION'),(NY,YY,'CURRENT_RELATION'),(NY,UY,'CURRENT_SUFFICIENCY'),(NN,NY,'PRIOR_RELATION'),(NY,NU,'PRIOR_SUFFICIENCY'),(NU,NY,'PRIOR_SUFFICIENCY'),(YN,YY,'PRIOR_RELATION'),(YN,NN,'CURRENT_RELATION'),(UY,UN,'PRIOR_RELATION'),(NU,UU,'CURRENT_SUFFICIENCY'),(NY,NY,'PACKAGE_CONSISTENCY'),(NY,NY,'IRRELEVANT_PRIOR_RELATION'),(NY,NY,'PACKAGE_CONSISTENCY'),(YN,YN,'PACKAGE_CONSISTENCY'),(NN,NN,'PACKAGE_CONSISTENCY'),(UY,UY,'IRRELEVANT_PRIOR_RELATION'),(UN,UN,'PACKAGE_CONSISTENCY'),(UU,UU,'IRRELEVANT_PRIOR_RELATION')]
 def make(combo,n,unknowns,positions,bad,refmismatch):
  cur,prior=combo
  ct=trial('MISMATCH' if cur=='YES' or cur=='UNKNOWN' and refmismatch else 'MATCH','UNDERDETERMINED' if cur=='UNKNOWN' else 'DETERMINATE',cur=='UNKNOWN' or unknowns[0])
  old=[trial(unknown=unknowns[i+1],prior=True) for i in range(n)]
  if prior in ['YES','UNKNOWN']:
   old[positions[0]]=trial('MISMATCH','DETERMINATE' if prior=='YES' else 'UNDERDETERMINED',True,True)
  return dict(proposition_scope=SCOPE,package=dict(consistency='CONTRADICTORY' if bad else 'CONSISTENT'),current_trial=ct,non_current_trials=old)
 for i,(a,b,family) in enumerate(specs,1):
  found=False
  options=list(itertools.product([1,2,3,4],[False,True],range(16),[False,True]));rng.shuffle(options)
  for n,bad,mask,refmismatch in options:
   if family=='PACKAGE_CONSISTENCY':bad=False
   if family=='IRRELEVANT_PRIOR_RELATION' and n<2:continue
   order=list(range(n));rng.shuffle(order);bits=[bool((mask>>j)&1) for j in range(n+1)]
   if family=='CURRENT_SUFFICIENCY':bits[0]=True
   s=make(a,n,bits,order,bad,refmismatch);t=copy.deepcopy(s)
   if family=='CURRENT_RELATION':t['current_trial']['observation_requirement']='MISMATCH' if b[0]=='YES' else 'MATCH';field='.current_trial.observation_requirement'
   elif family=='CURRENT_SUFFICIENCY':t['current_trial']['evidence_sufficiency']='UNDERDETERMINED' if b[0]=='UNKNOWN' else 'DETERMINATE';field='.current_trial.evidence_sufficiency'
   elif family=='PRIOR_RELATION':
    j=order[0];s['non_current_trials'][j]=trial('MISMATCH' if a[1]=='YES' else 'MATCH',unknown=bits[j+1],prior=True);t=copy.deepcopy(s);t['non_current_trials'][j]['observation_requirement']='MISMATCH' if b[1]=='YES' else 'MATCH';field=f'.non_current_trials.{j}.observation_requirement'
   elif family=='PRIOR_SUFFICIENCY':
    j=order[0];t['non_current_trials'][j]['evidence_sufficiency']='UNDERDETERMINED' if b[1]=='UNKNOWN' else 'DETERMINATE';field=f'.non_current_trials.{j}.evidence_sufficiency'
   elif family=='PACKAGE_CONSISTENCY':t['package']['consistency']='CONTRADICTORY';field='.package.consistency'
   elif family=='IRRELEVANT_PRIOR_RELATION':
    # Change only a reference relation inside an uncertain older trial; another older trial establishes YES when applicable.
    j=order[-1];s['non_current_trials'][j]=trial('MATCH','UNDERDETERMINED',True,True);t=copy.deepcopy(s);t['non_current_trials'][j]['observation_requirement']='MISMATCH';field=f'.non_current_trials.{j}.observation_requirement'
   else:raise ValueError(family)
   if tuple(author_gold(s).values())!=a or tuple(author_gold(t).values())!=b:continue
   signatures=[semantic_signature(z) for z in [s,t]]
   if any(x in excluded or x in used for x in signatures) or signatures[0]==signatures[1]:continue
   # UNKNOWN-prior states must include a reference mismatch whose violation remains unresolved.
   pid=f'ts-p{i:02d}';endpoints={}
   for side,z,combo,signature in zip('AB',[s,t],[a,b],signatures):
    sid='ts-v0-'+sha(f'{SEED}:{i}:{side}'.encode())[:14];endpoints[side]=sid;gold=author_gold(z);w=witness(z)
    cases.append(dict(id=sid,pair=pid,side=side,state=z,gold=gold,historical_focus=combo==NY,author_proof=dict(current='Current resolved sufficiency and reference relation give '+gold['current_violation'],prior='Combine all explicitly older trial statuses: '+str([tstatus(x) for x in z['non_current_trials']])+'; existential demonstrated violation state is '+gold['prior_violation'],provenance='Separate provenance contradiction cannot change supplied trial propositions.'),witness=w,family=family));used.add(signature)
   pairs.append(dict(id=pid,endpoints=endpoints,changing=a!=b,declared_field=field,family=family,gold_A=dict(zip(FIELDS,a)),gold_B=dict(zip(FIELDS,b))));found=True;break
  if not found:raise RuntimeError(('No fresh coherent pair',i,family))
 assert Counter('/'.join(c['gold'][k] for k in FIELDS) for c in cases)==EXPECTED_COUNTS
 # Six six-call blocks, each with two focus endpoints; 9 A-first / 9 B-first.
 focus=[c for c in cases if c['historical_focus']];other=[c for c in cases if not c['historical_focus']]
 for attempt in range(100000):
  rng.shuffle(focus);rng.shuffle(other);schedule=[]
  for block in range(6):
   chunk=focus[block*2:block*2+2]+other[block*4:block*4+4];rng.shuffle(chunk);schedule+=chunk
  if any(a['pair']==b['pair'] for a,b in zip(schedule,schedule[1:])):continue
  pos={c['id']:i for i,c in enumerate(schedule)}
  if sum(pos[p['endpoints']['A']]<pos[p['endpoints']['B']] for p in pairs)!=9:continue
  # Every non-focus output combination appears in both halves; all calls remain prospectively fixed.
  if any(set('/'.join(c['gold'][k] for k in FIELDS) for c in schedule[i:i+18])!=set(EXPECTED_COUNTS) for i in [0,18]):continue
  break
 else:raise RuntimeError('No balanced schedule')
 files={};entries=[]
 for c in cases:
  sid=c['id'];sb=raw(c['state']);messages=[dict(role='system',content=INSTRUCTION),dict(role='user',content=DEFINITIONS+'\n\nResolved primitive state:\n'+sb.decode())]
  req=dict(messages=messages,response_format=dict(type='json_object',schema=SCHEMA),temperature=.2,top_p=.9,top_k=40,min_p=.05,seed=SEED,max_tokens=2048,cache_prompt=False,stream=False,chat_template_kwargs=dict(enable_thinking=True));rb=raw(req)
  files['states/'+sid+'.json']=sb;files['requests/'+sid+'.json']=rb;entries.append(dict(render_id=sid,request_path='requests/'+sid+'.json',request_sha256=sha(rb),state_sha256=sha(sb)))
 files['cases.json']=raw(cases);files['pairs.json']=raw(pairs);files['render-manifest.json']=raw(dict(seed=SEED,schedule=[c['id'] for c in schedule],entries=entries));return files
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 for n,b in generate().items():f=a.out/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
 print('36 fresh states, 18 disjoint pairs, 36 two-field requests; zero model calls.')
