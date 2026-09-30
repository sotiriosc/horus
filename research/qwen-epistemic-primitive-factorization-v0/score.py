"""Frozen exact scoring of seven separate primitives and independent reduction."""
import argparse,collections,hashlib,json,math,subprocess
from pathlib import Path
import jsonschema
from generate import P,FAMILIES,CLASSES,REDUCTION,raw,canonical
SCHEMAS=json.loads((P/'schemas.json').read_bytes())
SPEC=json.loads((P/'case-spec.json').read_bytes())
def strict(text):
 def pairs(items):
  out={}
  for k,v in items:
   if k in out:raise ValueError('duplicate key')
   out[k]=v
  return out
 def bad(value):raise ValueError('nonfinite')
 def num(value):
  n=float(value)
  if not math.isfinite(n):raise ValueError('nonfinite')
  return n
 return json.loads(text,object_pairs_hook=pairs,parse_constant=bad,parse_float=num)
def grade(text,task,want):
 out={'parsed':False,'schema_valid':False,'correct':False,'selected':None,'error_category':None}
 try:obj=strict(text);out['parsed']=True
 except (ValueError,TypeError):out['error_category']='PARSE_FAILURE';obj=None
 if out['parsed']:
  try:jsonschema.Draft7Validator(SCHEMAS[task]).validate(obj);out['schema_valid']=True;out['selected']=obj
  except jsonschema.ValidationError:out['error_category']='SCHEMA_FAILURE'
 if out['schema_valid']:
  out['correct']=obj==want
  if not out['correct']:out['error_category']='VALUE_MISMATCH'
 if task==FAMILIES[0]:out['fields']={field:out['schema_valid'] and obj[field]==want[field] for field in ('same_referent','equal_value')}
 return out

def confusion(rows,labels,key):
 m={str(x):{str(y):0 for y in labels+['INVALID_OUTPUT']} for x in labels}
 for r in rows:
  gold=key(r['gold']);selected=key(r['selected']) if r['schema_valid'] else 'INVALID_OUTPUT';m[str(gold)][str(selected)]+=1
 return m

def pair_pass(a,b,expected_a,expected_b,field=None):
 if not (a['correct'] and b['correct']):return False
 if field is not None:return a['selected'][field]==expected_a[field] and b['selected'][field]==expected_b[field] and a['selected'][field]!=b['selected'][field]
 return a['selected']==expected_a and b['selected']==expected_b and a['selected']!=b['selected']
def joint(items,left,right,idkey):
 keys=['P_correct_R_correct','P_correct_R_wrong','P_wrong_R_correct','P_wrong_R_wrong'];members={k:[] for k in keys}
 for x in items:
  k='P_'+('correct' if x[left] else 'wrong')+'_R_'+('correct' if x[right] else 'wrong');members[k].append(x[idkey])
 return {k:{'count':len(v),'members':v} for k,v in members.items()}

def interpretation(primitive_gates,reduction_gate,subset_gates):
 failed=[f for f in FAMILIES if not primitive_gates[f]];mixed=[f for f in failed if subset_gates[f]]
 if not failed:return {'pattern':'BOUNDED_ALIGNED_STATE_EPISTEMIC_CAPABILITY_ESTABLISHED' if reduction_gate else 'PRIMITIVES_ESTABLISHED_REDUCTION_NOT_ESTABLISHED','registered_category':'C' if reduction_gate else 'A','failed_primitives':[],'failed_primitive_with_strong_matching_reduction_subset':[]}
 is_mixed=reduction_gate or bool(mixed)
 return {'pattern':'MIXED_PRIMITIVE_REDUCTION_PATTERN' if is_mixed else 'PRIMITIVE_LIMITATIONS_NOT_RESOLVED','registered_category':'D' if is_mixed else 'B','failed_primitives':failed,'failed_primitive_with_strong_matching_reduction_subset':mixed,'reduction_gate_passed_despite_primitive_failure':bool(reduction_gate)}

def summarize(rows,pairs):
 lookup={(r['world_id'],r['arm']):r for r in rows};primitive={};pair_rows=[];endpoint_rows=[]
 for pair in pairs:
  f=pair['family'];aa={arm:lookup[pair['endpoints']['A'],arm] for arm in 'PR'};bb={arm:lookup[pair['endpoints']['B'],arm] for arm in 'PR'}
  pp=pair_pass(aa['P'],bb['P'],aa['P']['gold'],bb['P']['gold'],pair['identity_flip_field'])
  changes=pair['coupling']['five_class_changes'];rp=aa['R']['correct'] and bb['R']['correct']
  if changes:rp=rp and pair_pass(aa['R'],bb['R'],aa['R']['gold'],bb['R']['gold'])
  else:rp=rp and aa['R']['selected']==bb['R']['selected']
  pair_rows.append({'pair_id':pair['pair_id'],'family':f,'endpoints':pair['endpoints'],'P_pair_pass':pp,'R_exact_pair_pass':rp,'diagnostic_gold_changes':changes,'R_flip_pass':rp if changes else None,'R_stable_class_retention_pass':rp if not changes else None,'P_gold_transition':[aa['P']['gold'],bb['P']['gold']],'P_selected_transition':[aa['P']['selected'],bb['P']['selected']],'R_gold_transition':[aa['R']['gold'],bb['R']['gold']],'R_selected_transition':[aa['R']['selected'],bb['R']['selected']],'identity_flip_field':pair['identity_flip_field'],'non_target_changes':pair['coupling']['changed_non_target_primitives'],'coupling_explanation':pair['coupling']['coupling_explanation'],'exact_state_delta':pair['coupling']['exact_state_delta']})
  for side in 'AB':
   sid=pair['endpoints'][side];pr,rr=lookup[sid,'P'],lookup[sid,'R'];endpoint_rows.append({'world_id':sid,'pair_id':pair['pair_id'],'side':side,'family':f,'P_correct':pr['correct'],'R_correct':rr['correct'],'P_selected':pr['selected'],'P_gold':pr['gold'],'R_selected':rr['selected'],'R_gold':rr['gold']})
 for f in FAMILIES:
  rr=[r for r in rows if r['family']==f and r['arm']=='P'];pp=[p for p in pair_rows if p['family']==f];assert len(rr)==8 and len(pp)==4
  correct=sum(r['correct'] for r in rr);passed=sum(p['P_pair_pass'] for p in pp);s={'correct':correct,'endpoints':8,'schema_valid':sum(r['schema_valid'] for r in rr),'parsed':sum(r['parsed'] for r in rr),'pair_passes':passed,'pairs':4,'gate':correct>=7 and passed>=3,'error_categories':dict(collections.Counter(r['error_category'] for r in rr if r['error_category'])),'missing_or_invalid':[r['world_id'] for r in rr if not r['schema_valid']]}
  if f==FAMILIES[0]:
   s['fields']={field:sum(r['fields'][field] for r in rr) for field in ('same_referent','equal_value')};s['field_confusion']={field:confusion(rr,[False,True],lambda o,field=field:o[field]) for field in ('same_referent','equal_value')};s['joint_confusion']=confusion(rr,['false,false','false,true','true,false','true,true'],lambda o:','.join(str(o[k]).lower() for k in ('same_referent','equal_value')))
  else:s['confusion']=confusion(rr,SCHEMAS[f]['properties']['answer']['enum'],lambda o:o['answer'])
  primitive[f]=s
 rr=[r for r in rows if r['arm']=='R'];assert len(rr)==56
 perclass={c:{'correct':sum(r['correct'] for r in rr if r['gold']['classification']==c),'denominator':sum(r['gold']['classification']==c for r in rr),'minimum':SPEC['reduction_gate']['per_class_correct_minimum'][c]} for c in CLASSES}
 n=sum(r['correct'] for r in rr);gate=n>=48 and all(v['correct']>=v['minimum'] for v in perclass.values())
 reduction={'correct':n,'endpoints':56,'schema_valid':sum(r['schema_valid'] for r in rr),'parsed':sum(r['parsed'] for r in rr),'gate':gate,'overall_minimum':48,'per_class':perclass,'confusion':confusion(rr,CLASSES,lambda o:o['classification']),'error_categories':dict(collections.Counter(r['error_category'] for r in rr if r['error_category'])),'missing_or_invalid':[r['world_id'] for r in rr if not r['schema_valid']],'exact_pair_passes':sum(p['R_exact_pair_pass'] for p in pair_rows),'pairs':28,'flip_pair_passes':sum(bool(p['R_flip_pass']) for p in pair_rows),'flip_pairs':sum(p['diagnostic_gold_changes'] for p in pair_rows),'stable_pair_passes':sum(bool(p['R_stable_class_retention_pass']) for p in pair_rows),'stable_pairs':sum(not p['diagnostic_gold_changes'] for p in pair_rows)}
 family_results={};subset_gates={}
 for f in FAMILIES:
  eps=[r for r in endpoint_rows if r['family']==f];ps=[r for r in pair_rows if r['family']==f];flip=[r for r in ps if r['diagnostic_gold_changes']];stable=[r for r in ps if not r['diagnostic_gold_changes']];rn=sum(r['R_correct'] for r in eps);pn=sum(r['R_exact_pair_pass'] for r in ps);subset_gates[f]=rn>=7 and pn>=3
  family_results[f]={'P_correct':primitive[f]['correct'],'P_pair_passes':primitive[f]['pair_passes'],'R_correct':rn,'R_schema_valid':sum(r['schema_valid'] for r in rr if r['family']==f),'R_exact_pair_passes':pn,'R_flip_pair_passes':sum(r['R_exact_pair_pass'] for r in flip),'R_flip_pairs':len(flip),'R_stable_pair_passes':sum(r['R_exact_pair_pass'] for r in stable),'R_stable_pairs':len(stable),'R_subset_descriptive_threshold_passed':subset_gates[f],'endpoint_joint':joint(eps,'P_correct','R_correct','world_id'),'pair_joint':joint(ps,'P_pair_pass','R_exact_pair_pass','pair_id'),'flip_pair_joint':joint(flip,'P_pair_pass','R_exact_pair_pass','pair_id')}
 pgates={f:primitive[f]['gate'] for f in FAMILIES};findings=[f+('_COMPETENCE_ESTABLISHED' if pgates[f] else '_COMPETENCE_NOT_ESTABLISHED') for f in FAMILIES]+['FIVE_CLASS_REDUCTION_COMPETENCE_'+('ESTABLISHED' if gate else 'NOT_ESTABLISHED')]
 return {'status':'QWEN_EPISTEMIC_PRIMITIVE_FACTORIZATION_COMPLETE_V0','primitives':primitive,'reduction':reduction,'family_comparisons':family_results,'registered_interpretation':interpretation(pgates,gate,subset_gates),'findings':findings,'endpoint_joint_descriptive_counts':joint(endpoint_rows,'P_correct','R_correct','world_id'),'pair_joint_descriptive_counts':joint(pair_rows,'P_pair_pass','R_exact_pair_pass','pair_id'),'endpoint_comparisons':endpoint_rows,'pair_comparisons':pair_rows,'combined_system_capability':'NOT_TESTED_NO_CHAINING','rows':rows}

def load_raw(folder):
 freeze=json.loads((folder/'raw-freeze.json').read_bytes());assert freeze['purpose']=='SCIENTIFIC_EPISTEMIC_PRIMITIVES_V0','Mock evidence cannot be scored as scientific output'
 for name,want in freeze['sha256'].items():assert hashlib.sha256((folder/'raw'/name).read_bytes()).hexdigest()==want,name
 return json.loads((folder/'raw/execution.json').read_bytes())
def score(folder=P):
 execution=load_raw(folder)
 if execution['stop'] or execution['completed_calls']!=112:return {'status':'INVALID_STUDY','execution':execution,'findings':'NOT_ESTABLISHED_DUE_TO_INVALID_STUDY'}
 gold={g['world_id']:g for g in json.loads((folder/'materialized/gold.json').read_bytes())};pairs=json.loads((folder/'materialized/pairs.json').read_bytes());entries=json.loads((folder/'materialized/render-manifest.json').read_bytes())['entries'];rows=[]
 for e in entries:
  g=gold[e['world_id']];task=e['family'] if e['arm']=='P' else REDUCTION;want=g[e['arm']];r=grade((folder/'raw/finals'/(e['render_id']+'.txt')).read_text(),task,want);r.update(world_id=e['world_id'],pair_id=e['pair_id'],side=e['side'],family=e['family'],arm=e['arm'],render_id=e['render_id'],gold=want);rows.append(r)
 result=summarize(rows,pairs);result.update(attempted=execution['attempted_calls'],completed=execution['completed_calls']);return result
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--raw-commit',required=True);ap.add_argument('--out',required=True,type=Path);args=ap.parse_args();root=P.parents[1];rel=str(P.relative_to(root));commit=args.raw_commit
 def git(*a):return subprocess.check_output(['git',*a],cwd=root)
 assert git('merge-base','--is-ancestor',commit,'HEAD')==b'';assert git('show',commit+':'+rel+'/raw-freeze.json')==(P/'raw-freeze.json').read_bytes();assert not git('ls-tree','--name-only',commit,'--',rel+'/scores.json').strip()
 freeze=json.loads((P/'raw-freeze.json').read_bytes())
 for name in freeze['sha256']:assert git('show',commit+':'+rel+'/raw/'+name)==(P/'raw'/name).read_bytes()
 result=score();result['raw_commit_before_scoring']=commit
 with args.out.open('xb') as f:f.write(raw(result))
 print(json.dumps({k:v for k,v in result.items() if k in ('status','registered_interpretation','findings','attempted','completed')}))
