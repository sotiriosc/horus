"""Independent finite-state verification and read-only freshness/leakage checks."""
import ast,collections,hashlib,itertools,json,re,subprocess
from pathlib import Path
import jsonschema
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
F=['IDENTITY_EQUALITY','CURRENTNESS','KNOWN_VS_UNKNOWN','CONTRADICTION','ALTERNATIVE_COMPLETION_EXISTENCE','OBSERVATION_REQUIREMENT_COMPARISON','EVIDENCE_SUFFICIENCY']
C=['SUPPORTED_CURRENT_DEFECT','NO_SUPPORTED_DIAGNOSIS','INSUFFICIENT_EVIDENCE','HISTORICAL_DEFECT_NOT_CURRENT','INVALID_OR_CONTRADICTORY_EVIDENCE']
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def derive(s):
 assert set(s)=={'system','conventions','deployment','builds','assertions','trials'}
 builds={x['build']:x['creation_order'] for x in s['builds']};assert len(builds)==2 and set(builds.values())=={1,2}
 assert len(s['trials'])==2 and {t['build'] for t in s['trials']}==set(builds)
 compatible=[];violations=[];requirements=[]
 for t in s['trials']:
  assert len(t['required_results'])==3
  keys=[r['input'] for r in t['required_results']];assert len(set(keys))==3
  assert len(set(t['admissible_inputs']))==len(t['admissible_inputs'])>0
  assert set(t['admissible_inputs'])<=set(keys)
  assert t['reported_input']=='UNKNOWN' or t['reported_input'] in t['admissible_inputs']
  # Enumerate potential inputs from the complete table, checking capture/domain separately.
  possibilities=[r for r in t['required_results'] if r['input'] in t['admissible_inputs'] and (t['reported_input']=='UNKNOWN' or r['input']==t['reported_input'])]
  assert possibilities and t['reference_input'] in [r['input'] for r in possibilities]
  compatible.append([r['input'] for r in possibilities]);violations.append([r['result']!=t['observed_result'] for r in possibilities]);requirements.append(next(r['result'] for r in t['required_results'] if r['input']==t['reference_input']))
 current=[i for i,t in enumerate(s['trials']) if t['build']==s['deployment']['build']];assert len(current)==1;ci=current[0];oi=1-ci
 assert len(s['assertions'])==2
 subjects=[tuple(x['subject'][key] for key in ('build','station','cycle')) for x in s['assertions']];values=[x['asserted_value'] for x in s['assertions']]
 same=len(set(subjects))==1;equal=len(set(values))==1
 constraints=collections.defaultdict(set)
 for sub,val in zip(subjects,values):constraints[sub].add(val)
 clash=any(len(v)>1 for v in constraints.values());determined=all(v==violations[ci][0] for v in violations[ci])
 vector={F[0]:{'same_referent':same,'equal_value':equal},F[1]:{'answer':['CURRENT','NOT_CURRENT'][ci]},F[2]:{'answer':'KNOWN' if all(x==compatible[0][0] for x in compatible[0]) else 'UNKNOWN'},F[3]:{'answer':'CONTRADICTORY' if clash else 'CONSISTENT'},F[4]:{'answer':'ALTERNATIVE_EXISTS' if set(compatible[0])-{s['trials'][0]['reference_input']} else 'NO_ALTERNATIVE'},F[5]:{'answer':'MATCH' if requirements[0]==s['trials'][0]['observed_result'] else 'MISMATCH'},F[6]:{'answer':'DETERMINATE' if determined else 'UNDERDETERMINED'}}
 if clash:cls=C[4]
 elif not determined:cls=C[2]
 elif violations[ci][0]:cls=C[0]
 elif builds[s['trials'][oi]['build']]<builds[s['trials'][ci]['build']] and all(violations[oi]):cls=C[3]
 else:cls=C[1]
 proof_check={'first_trial_remaining_inputs':compatible[0],'first_reference_requirement':requirements[0],'deployed_build':s['trials'][ci]['build'],'deployed_violation_by_completion':dict(zip(compatible[ci],violations[ci])),'other_build_violation_by_completion':dict(zip(compatible[oi],violations[oi])),'other_build_is_older':builds[s['trials'][oi]['build']]<builds[s['trials'][ci]['build']]}
 return vector,cls,proof_check

def differences(a,b,path=''):
 if isinstance(a,dict) and isinstance(b,dict):
  assert set(a)==set(b);return sum((differences(a[k],b[k],path+'/'+k) for k in a),[])
 if isinstance(a,list) and isinstance(b,list) and len(a)==len(b):return sum((differences(x,y,path+'/'+str(i)) for i,(x,y) in enumerate(zip(a,b))),[])
 return [] if a==b else [{'path':path,'before':a,'after':b}]

def walk(obj):
 yield obj
 if isinstance(obj,dict):
  for value in obj.values():yield from walk(value)
 if isinstance(obj,list):
  for value in obj:yield from walk(value)

def main():
 spec=json.loads((P/'case-spec.json').read_bytes());schemas=json.loads((P/'schemas.json').read_bytes());manifest=json.loads((P/'materialized/render-manifest.json').read_bytes());gold=json.loads((P/'materialized/gold.json').read_bytes());pairs=json.loads((P/'materialized/pairs.json').read_bytes());counts=collections.Counter();vectors=[];state_hashes=set();byfamily=collections.defaultdict(list)
 assert len(spec['pairs'])==28 and len(pairs)==28 and len(gold)==56
 for pair in spec['pairs']:
  target=pair['primitive'];before_after=[]
  for side in 'AB':
   state=pair['states'][side];v,c,proof=derive(state);g=pair['offline_gold'][side];assert v==g['primitives'];assert c==g['classification']==pair['class_ab']['AB'.index(side)]
   for key,want in proof.items():assert g['author_proof'][key]==want,(pair['index'],side,key)
   for f in F:jsonschema.Draft7Validator(schemas[f]).validate(v[f])
   byfamily[target].append(v[target]);counts[c]+=1;before_after.append(v);vectors.append({'pair_index':pair['index'],'side':side,'all_seven_verified':True,'class_verified':c,'author_proof_verified':True})
   state_hashes.add(canonical(state))
   for obj in walk(state):
    if isinstance(obj,dict):
     for key in obj:assert not re.search(r'defect|diagnos|benign|invalid|contradict|sufficien|historical|gold|class|verdict',key,re.I),key
    if isinstance(obj,str):assert not re.search(r'defect|diagnos|benign|invalid|contradict|sufficien|historical|\bgold\b|\bclass\b|verdict',obj,re.I),obj
   if target in (F[2],F[6]):assert v[F[3]]=={'answer':'CONSISTENT'}
  a,b=before_after;changes=[f for f in F if a[f]!=b[f]];assert target in changes;couple=pair['coupling_audit'];assert couple['changed_non_target_primitives']==[f for f in changes if f!=target];assert couple['exact_state_delta']==differences(pair['states']['A'],pair['states']['B']);assert len(couple['exact_state_delta'])==1
  if target==F[0]:field=pair['designated_identity_field'];assert a[target][field]!=b[target][field];assert a[target][next(k for k in a[target] if k!=field)]==b[target][next(k for k in b[target] if k!=field)]
 assert len(state_hashes)==56;assert dict(counts)==spec['class_denominators']
 assert spec['reduction_gate']['overall_correct_minimum']==48
 assert spec['reduction_gate']['per_class_correct_minimum']=={c:(3*counts[c]+3)//4 for c in C}
 for f,values in byfamily.items():
  freqs=collections.Counter(canonical(x) for x in values);assert sorted(freqs.values())==([2]*4 if f==F[0] else [4,4]),(f,freqs)
 assert len(manifest['schedule'])==len(set(manifest['schedule']))==len(manifest['entries'])==112
 entry_by={e['render_id']:e for e in manifest['entries']};assert set(entry_by)==set(manifest['schedule'])
 for sid in {e['world_id'] for e in manifest['entries']}:
  ee=[e for e in manifest['entries'] if e['world_id']==sid];assert {e['arm'] for e in ee}=={'P','R'};states=[]
  for e in ee:
   statebytes=(P/'materialized/fixtures'/(e['render_id']+'.json')).read_bytes();requestbytes=(P/'materialized'/e['request_path']).read_bytes();assert hashlib.sha256(requestbytes).hexdigest()==e['request_sha256'];assert hashlib.sha256(statebytes).hexdigest()==e['state_sha256'];req=json.loads(requestbytes);statepart=req['messages'][1]['content'].split('\n\nAligned factual state:\n',1)[1].encode();assert statepart==statebytes;assert req['seed']==413708629;states.append(statebytes)
   if e['arm']=='R':assert spec['questions'][e['family']] not in req['messages'][1]['content']
   else:assert all(c not in req['messages'][1]['content'] for c in C)
   assert all(token not in req['messages'][1]['content'] for token in (e['world_id'],e['pair_id'],e['render_id']))
  assert states[0]==states[1]==(P/'materialized/states'/(sid+'.json')).read_bytes()
 schedule_checks=[]
 for f in F:
  ps=[p for p in pairs if p['family']==f];assert len(ps)==4
  firstarms=[];orders={'P':[],'R':[]}
  for pair in ps:
   ee=sorted((e for e in manifest['entries'] if e['pair_id']==pair['pair_id']),key=lambda e:e['call_order']);firstarms.append(ee[0]['arm'])
   for arm in 'PR':orders[arm].append(next(e['side'] for e in ee if e['arm']==arm))
  assert collections.Counter(firstarms)=={'P':2,'R':2}
  for arm in 'PR':assert collections.Counter(orders[arm])=={'A':2,'B':2}
  for epoch in range(1,5):
   ee=[e for e in manifest['entries'] if e['family']==f and e['epoch']==epoch];assert collections.Counter(e['arm'] for e in ee)=={'P':2,'R':2};assert collections.Counter(e['side'] for e in ee)=={'A':2,'B':2}
  schedule_checks.append({'family':f,'both_arms_A_first':2,'both_arms_B_first':2,'P_first_pairs':2,'R_first_pairs':2,'each_epoch_P_R_A_B_balanced':True})
 from generate import generate,DEFS
 for name,want in generate().items():assert (P/'materialized'/name).read_bytes()==want,name
 previous=ast.parse((ROOT/'research/qwen-diagnostic-reasoning-factorization-v0/generate.py').read_text());olddefs=next(ast.literal_eval(n.value) for n in previous.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='DEFS' for t in n.targets));assert DEFS==olddefs
 for name in ('generate.py','verify.py','score.py','transport.py','run_campaign.py'):
  tree=ast.parse((P/name).read_text());imports=[n.module or '' for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]+[x.name for n in ast.walk(tree) if isinstance(n,ast.Import) for x in n.names];assert not any('compiler' in i for i in imports)
 # Prior corpus audit after construction: never read old model finals or envelopes.
 names=subprocess.check_output(['git','ls-tree','-r','--name-only',spec['base']],cwd=ROOT).decode().splitlines();corpus=[];parsed=0;objects=set();strings=set()
 for name in names:
  path=Path(name)
  if path.parts[0] not in ('research','analysis','engineering','experiments') or path.suffix not in ('.json','.md','.py','.txt'):continue
  if any(part in ('raw','finals','metadata','responses','private') for part in path.parts) or any(x in path.name for x in ('scores','replay','private-evidence','server-properties','raw-freeze','postflight','launch-preflight','publication-audit')):continue
  data=(ROOT/name).read_bytes();corpus.append((name,data))
  if path.suffix=='.json':
   try:obj=json.loads(data)
   except (ValueError,UnicodeDecodeError):continue
   parsed+=1
   for o in walk(obj):
    if isinstance(o,(dict,list)):objects.add(canonical(o))
    if isinstance(o,str):strings.add(o)
 assert not state_hashes&objects
 fresh_values={r['input'] for pair in spec['pairs'] for s in pair['states'].values() for t in s['trials'] for r in t['required_results']}|{r['result'] for pair in spec['pairs'] for s in pair['states'].values() for t in s['trials'] for r in t['required_results']}
 assert not fresh_values&strings
 for pair in spec['pairs']:
  for s in pair['states'].values():
   for a in s['assertions']:assert canonical(a['subject']) not in objects
   for t in s['trials']:assert canonical(t) not in objects and canonical(t['required_results']) not in objects
 for e in manifest['entries']:
  req=json.loads((P/'materialized'/e['request_path']).read_bytes());assert req['messages'][1]['content'] not in strings
 newids={e[k] for e in manifest['entries'] for k in ('world_id','pair_id','render_id')}
 combined=b'\n'.join(data for _,data in corpus)
 assert not any(x.encode() in combined for x in newids)
 hashes={str(f.relative_to(P/'materialized')):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((P/'materialized').rglob('*')) if f.is_file()}
 report={'status':'PASS','scientific_model_calls_before_freeze':0,'pairs':28,'states':56,'requests':112,'class_denominators':dict(counts),'reduction_gate':spec['reduction_gate'],'diagnostic_flip_pairs':sum(p['coupling']['five_class_changes'] for p in pairs),'class_stable_pairs':sum(not p['coupling']['five_class_changes'] for p in pairs),'coupled_pairs':sum(bool(p['coupling']['changed_non_target_primitives']) for p in pairs),'uncoupled_pairs':sum(not p['coupling']['changed_non_target_primitives'] for p in pairs),'independent_checks':vectors,'schedule_checks':schedule_checks,'P_R_state_bytes_identical':True,'gold_or_primitive_vectors_in_model_inputs':False,'all_target_pairs_minimal_one_change':True,'no_existing_compiler_used':True,'ontology_definitions_byte_identical':True,'prior_files_audited':len(corpus),'prior_json_files_parsed':parsed,'prior_exact_state_subject_trial_table_overlap':0,'new_symbolic_input_output_values':len(fresh_values),'prior_symbolic_value_overlap':0,'new_ids':len(newids),'prior_id_overlap':0,'semantic_review':'Fresh aligned three-row symbolic contracts, separate immutable mark subjects, relational matched deltas, domain-expansion and non-reference-cell sufficiency controls; no copied prior worlds or operational transforms. Generic epistemic concepts and class ontology intentionally reused. Internally authored, correlated synthetic fixtures; no claim of novel ontology or external generalization.','materialized_files':len(hashes),'sha256':hashes}
 (P/'preflight.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ('independent_checks','schedule_checks','sha256')},indent=2))
if __name__=='__main__':main()
