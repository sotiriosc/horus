"""Prospective deterministic semantic generator; no model outputs are imported."""
import copy,hashlib,importlib.util,itertools,json,random
from collections import Counter,defaultdict
from pathlib import Path
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('preserved_temporal_common',P.parent/'qwen-temporal-state-representation-v0/common.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
SCOPE,DEFINITIONS,INSTRUCTION,FIELDS,SCHEMA=old.SCOPE,old.DEFINITIONS,old.INSTRUCTION,old.FIELDS,old.SCHEMA
SEED=20260930
VALUES=['YES','NO','UNKNOWN']
TYPES=[('KNOWN','NO_ALTERNATIVE','MATCH','DETERMINATE'),('KNOWN','NO_ALTERNATIVE','MISMATCH','DETERMINATE'),('UNKNOWN','ALTERNATIVE_EXISTS','MATCH','DETERMINATE'),('UNKNOWN','ALTERNATIVE_EXISTS','MISMATCH','DETERMINATE'),('UNKNOWN','ALTERNATIVE_EXISTS','MATCH','UNDERDETERMINED'),('UNKNOWN','ALTERNATIVE_EXISTS','MISMATCH','UNDERDETERMINED')]
STATUS=['NO','YES','NO','YES','UNKNOWN','UNKNOWN']
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def sha(x):return hashlib.sha256(x if isinstance(x,bytes) else x.encode()).hexdigest()
def dump(path,x):path.write_text(json.dumps(x,indent=2)+'\n')
def rows(path):return [json.loads(x) for x in path.read_text().splitlines()]
def write_rows(path,xs):path.write_text(''.join(canonical(x)+'\n' for x in xs))
def trial(i,current=False):return dict(zip(['currentness','knownness','alternative_completion','observation_requirement','evidence_sufficiency'],['CURRENT' if current else 'NOT_CURRENT',*TYPES[i]]))
def signature(s):return old.semantic_signature(s)
def status(t):return 'UNKNOWN' if t['evidence_sufficiency']=='UNDERDETERMINED' else 'YES' if t['observation_requirement']=='MISMATCH' else 'NO'
def gold(s):
 prior=[status(t) for t in s['non_current_trials']]
 return dict(current_violation=status(s['current_trial']),prior_violation='YES' if 'YES' in prior else 'UNKNOWN' if 'UNKNOWN' in prior else 'NO')
def witnesses(s):
 def witness(t):
  mismatch=t['observation_requirement']=='MISMATCH';values=[mismatch]
  if t['knownness']=='UNKNOWN':values.append(not mismatch if t['evidence_sufficiency']=='UNDERDETERMINED' else mismatch)
  return {'reference_input':0,'admissible_inputs':list(range(len(values))),'observed_output':17,'required_outputs':[19 if v else 17 for v in values]}
 return [witness(t) for t in [s['current_trial'],*s['non_current_trials']]]
def independently_audit(c):
 s=c['state'];possible=[];assert s['proposition_scope']==SCOPE
 for i,(t,w) in enumerate(zip([s['current_trial'],*s['non_current_trials']],c['witnesses'])):
  vs={w['observed_output']!=w['required_outputs'][j] for j in w['admissible_inputs']};possible.append(vs)
  assert w['reference_input'] in w['admissible_inputs']
  assert t==dict(currentness='CURRENT' if i==0 else 'NOT_CURRENT',knownness='KNOWN' if len(w['admissible_inputs'])==1 else 'UNKNOWN',alternative_completion='ALTERNATIVE_EXISTS' if len(w['admissible_inputs'])>1 else 'NO_ALTERNATIVE',observation_requirement='MATCH' if w['observed_output']==w['required_outputs'][w['reference_input']] else 'MISMATCH',evidence_sufficiency='DETERMINATE' if len(vs)==1 else 'UNDERDETERMINED')
 # Exact reachable truth-set dynamic program: equivalent to Cartesian enumeration without exponential repetition.
 prior={False}
 for vs in possible[1:]:prior={a or b for a in prior for b in vs}
 labels={frozenset([True]):'YES',frozenset([False]):'NO',frozenset([True,False]):'UNKNOWN'}
 independent=dict(current_violation=labels[frozenset(possible[0])],prior_violation=labels[frozenset(prior)])
 assert c['gold']==independent;assert c['semantic_signature']==signature(s);return independent

def messages(c):return [{'role':'system','content':INSTRUCTION+' Output keys: current_violation, prior_violation; each value must be YES, NO, or UNKNOWN. No other keys or text.'},{'role':'user','content':DEFINITIONS+'\n\nResolved primitive state:\n'+canonical(c['state'])}]
def families(s):
 g=gold(s);prior=[status(t) for t in s['non_current_trials']];f=['schema']
 if g['current_violation']!='UNKNOWN':f.append('current_determinate')
 if all(v!='UNKNOWN' for v in prior):f.append('all_prior_determinate')
 if g['current_violation']=='YES' and g['prior_violation']=='YES':f.append('clear_YES')
 if g['current_violation']=='NO' and g['prior_violation']=='NO':f.append('clear_NO')
 if s['package']['consistency']=='CONTRADICTORY':f.append('contradiction_independent')
 if g['current_violation']=='UNKNOWN' or 'UNKNOWN' in prior or len(prior)>1 and len(set(prior))>1:f.append('target_UNKNOWN_or_aggregation')
 return f

def case(s,dataset,index):
 sig=signature(s);c=dict(id=f'{dataset}-{index:05d}-{sha(sig)[:12]}',dataset=dataset,state=s,gold=gold(s),semantic_signature=sig,witnesses=witnesses(s),families=families(s));independently_audit(c);return c

def legacy_signatures():
 # Read state objects only, never historical responses or gold.
 signatures=set()
 for name in ['qwen-temporal-state-representation-v0','qwen-role-grounded-temporal-reduction-v0','qwen-primitive-to-ontology-reduction-v0']:
  for f in (P.parent/name/'materialized/states').glob('*.json'):signatures.add(signature(json.loads(f.read_bytes())))
 for f in (P.parent/'qwen-epistemic-primitive-factorization-v0/materialized/states').glob('*.json'):
  s=json.loads(f.read_bytes());deployment=s['deployment']['build'];trials=[];assertions=defaultdict(set)
  for a in s['assertions']:assertions[canonical(a['subject'])].add(a['asserted_value'])
  for t in s['trials']:
   inputs=t['admissible_inputs'] if t['reported_input']=='UNKNOWN' else [t['reported_input']];req={r['input']:r['result'] for r in t['required_results']};vs={t['observed_result']!=req[i] for i in inputs}
   trials.append(dict(currentness='CURRENT' if t['build']==deployment else 'NOT_CURRENT',knownness='KNOWN' if len(inputs)==1 else 'UNKNOWN',alternative_completion='ALTERNATIVE_EXISTS' if any(i!=t['reference_input'] for i in inputs) else 'NO_ALTERNATIVE',observation_requirement='MATCH' if t['observed_result']==req[t['reference_input']] else 'MISMATCH',evidence_sufficiency='DETERMINATE' if len(vs)==1 else 'UNDERDETERMINED'))
  current=[t for t in trials if t['currentness']=='CURRENT'];assert len(current)==1
  signatures.add(signature(dict(package=dict(consistency='CONTRADICTORY' if any(len(x)>1 for x in assertions.values()) else 'CONSISTENT'),current_trial=current[0],non_current_trials=[t for t in trials if t['currentness']=='NOT_CURRENT'])))
 return signatures

def pool(counts):
 buckets=defaultdict(list)
 for n in counts:
  for prior in itertools.combinations_with_replacement(range(6),n):
   statuses={STATUS[x] for x in prior};p='YES' if 'YES' in statuses else 'UNKNOWN' if 'UNKNOWN' in statuses else 'NO'
   for cur in range(6):
    for inconsistent in [False,True]:buckets[STATUS[cur],p].append((cur,prior,inconsistent))
 for k,v in sorted(buckets.items()):random.Random(SEED+int(sha(canonical([list(counts),k]))[:8],16)).shuffle(v)
 return buckets

def materialize(spec,dataset):
 cur,prior,bad=spec;order=list(prior);h=int(sha(canonical(spec))[:8],16)
 if dataset.startswith('T'):
  # Held-out long lists place uncertainty at the two boundaries, alternately, with determinate trials in the middle.
  unsure=[x for x in order if x>=4];determ=[x for x in order if x<4];order=unsure[::2]+list(reversed(determ))+unsure[1::2]
 else:
  random.Random(SEED+h).shuffle(order)
 return dict(proposition_scope=SCOPE,package=dict(consistency='CONTRADICTORY' if bad else 'CONSISTENT'),current_trial=trial(cur,True),non_current_trials=[trial(x) for x in order])

def neighbors(c,reserved,legacy):
 s=c['state'];candidates=[]
 for i,t in enumerate([s['current_trial'],*s['non_current_trials']]):
  for field in ['observation_requirement','evidence_sufficiency']:
   if field=='evidence_sufficiency' and t['knownness']=='KNOWN':continue
   z=copy.deepcopy(s);dest=z['current_trial'] if i==0 else z['non_current_trials'][i-1]
   choices=['MATCH','MISMATCH'] if field=='observation_requirement' else ['DETERMINATE','UNDERDETERMINED'];dest[field]=choices[1-choices.index(dest[field])]
   sig=signature(z)
   if sig not in reserved and sig not in legacy:candidates.append((f'trial:{i}:{field}',z))
 z=copy.deepcopy(s);z['package']['consistency']='CONTRADICTORY' if z['package']['consistency']=='CONSISTENT' else 'CONSISTENT'
 if signature(z) not in reserved and signature(z) not in legacy:candidates.append(('package:consistency',z))
 # Prospectively prefer a target-changing neighbor, then another hashed one-field neighbor, at most two.
 candidates.sort(key=lambda x:(gold(x[1])==c['gold'],sha(c['id']+x[0]+signature(x[1]))));seen=set();out=[]
 for change,z in candidates:
  sig=signature(z)
  if sig in seen:continue
  item=case(z,'N'+c['dataset'][1:],len(out));item['id']=c['id']+'-neighbor-'+str(len(out));item['parent']=c['id'];item['changed_field']=change;out.append(item);seen.add(sig)
  if len(out)==2:break
 return out

def generate(out):
 out.mkdir(exist_ok=False);legacy=legacy_signatures();used=set(legacy);datasets={}
 # Regression allocation first reserves scarce all-compliant states; fixed before any model call.
 for cycle,counts,testcounts in [(1,range(1,8),range(8,10)),(2,range(10,13),range(13,16))]:
  buckets=pool(counts)
  for label in ['R','V','H']:
   name=f'{label}{cycle}';selected=[]
   for a,b in itertools.product(VALUES,repeat=2):
    amount=(60 if b=='NO' else 120 if b=='YES' else 0) if label=='R' and a!='UNKNOWN' else 0 if label=='R' else (8 if b=='NO' else 56) if label=='V' else (24 if b=='NO' else 318)
    for _ in range(amount):
     while True:
      if not buckets[a,b]:raise RuntimeError(('Insufficient fresh states',name,a,b))
      item=buckets[a,b].pop();s=materialize(item,name);sig=signature(s)
      if sig in used:continue
      # Reserve single-prior states for regression coverage only.
      if label!='R' and len(s['non_current_trials'])==1:continue
      used.add(sig);break
     selected.append(case(s,name,len(selected)))
   random.Random(SEED+cycle+ord(label)).shuffle(selected);datasets[name]=selected
  testpool=pool(testcounts);name=f'T{cycle}';selected=[]
  for a,b in itertools.product(VALUES,repeat=2):
   for _ in range(60):
    s=materialize(testpool[a,b].pop(),name);sig=signature(s);assert sig not in used;used.add(sig);selected.append(case(s,name,len(selected)))
  random.Random(SEED+cycle+84).shuffle(selected);datasets[name]=selected
 reserved={c['semantic_signature'] for n,cs in datasets.items() if not n.startswith('H') for c in cs}
 for i in [1,2]:datasets[f'N{i}']=[n for c in datasets[f'H{i}'] for n in neighbors(c,reserved,legacy)]
 for name,cs in datasets.items():write_rows(out/(name+'.jsonl'),cs)
 manifest={'seed':SEED,'legacy_states_excluded':len(legacy),'scientific_model_calls':0,'datasets':{}}
 for name,cs in sorted(datasets.items()):
  manifest['datasets'][name]=dict(count=len(cs),sha256=sha((out/(name+'.jsonl')).read_bytes()),joint_gold=dict(Counter('/'.join(c['gold'][k] for k in FIELDS) for c in cs)),prior_counts=dict(Counter(len(c['state']['non_current_trials']) for c in cs)),families=dict(Counter(f for c in cs for f in c['families'])))
 dump(out/'manifest.json',manifest);return manifest

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();print(json.dumps(generate(args.out),indent=2))
