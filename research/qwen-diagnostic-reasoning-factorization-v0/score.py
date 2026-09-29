"""Frozen exact scoring, separate stage gates and noncausal matched associations."""
import argparse,collections,hashlib,json,math,subprocess
from pathlib import Path
import jsonschema
from generate import P,CLASSES,ARMS,raw,canonical
SCHEMAS=json.loads((P/'schemas.json').read_bytes())
FIELDS=list(SCHEMAS['S']['properties'])
def strict(text):
 def pairs(items):
  obj={}
  for k,v in items:
   if k in obj:raise ValueError('duplicate JSON key')
   obj[k]=v
  return obj
 def bad(s):raise ValueError('nonfinite JSON')
 def number(s):
  v=float(s)
  if not math.isfinite(v):raise ValueError('nonfinite JSON')
  return v
 return json.loads(text,object_pairs_hook=pairs,parse_constant=bad,parse_float=number)
def normalize_state(obj):
 if isinstance(obj,dict):return {k:normalize_state(v) for k,v in sorted(obj.items())}
 if isinstance(obj,list):return sorted([normalize_state(v) for v in obj],key=canonical)
 return obj

def grade(text,arm,want):
 result={'parsed':False,'schema_valid':False,'correct':False,'selected':None,'error_category':None};obj=None
 try:obj=strict(text);result['parsed']=True
 except (ValueError,TypeError):result['error_category']='PARSE_FAILURE'
 if result['parsed']:
  if arm in ('R','E') and isinstance(obj,dict) and obj.get('classification') in CLASSES:result['selected']=obj['classification']
  try:jsonschema.Draft7Validator(SCHEMAS[arm]).validate(obj);result['schema_valid']=True
  except jsonschema.ValidationError:result['error_category']='SCHEMA_FAILURE'
 if arm=='O':
  result['individual_correct']=[False,False]
  if result['schema_valid']:
   result['individual_correct']=[a==b for a,b in zip(obj['results'],want['results'])];result['correct']=all(result['individual_correct'])
   if not result['correct']:result['error_category']='REVERSED_RESULT_ORDER' if obj['results']==want['results'][::-1] else 'VALUE_MISMATCH'
 elif arm=='S':
  result['fields']={field:result['schema_valid'] and normalize_state(obj[field])==normalize_state(want[field]) for field in FIELDS};result['correct']=all(result['fields'].values())
  if result['schema_valid'] and not result['correct']:result['error_category']='STATE_FIELD_MISMATCH'
 else:
  result['correct']=result['schema_valid'] and result['selected']==want['classification']
  if result['schema_valid'] and not result['correct']:result['error_category']='CLASS_MISMATCH'
 return result

def interpretation(gates):
 o,s,r,e=[gates[a] for a in ARMS];patterns=[]
 if o and not s and r and not e:patterns.append('A_BINDING_PATTERN')
 if o and s and not r and not e:patterns.append('B_EPISTEMIC_PATTERN')
 if o and s and r and not e:patterns.append('C_COMPOSITION_PATTERN')
 if sum(not x for x in (o,s,r))>=2:patterns.append('D_MULTIPLE_ISOLATED_LIMITATIONS')
 if all((o,s,r,e)):patterns.append('ALL_ARMS_SUPPORTED_WITHIN_CASES')
 return patterns or ['OTHER_MIXED_PATTERN']

def summarize(rows,gold):
 summaries={};glookup={g['world_id']:g for g in gold}
 for arm in ARMS:
  rr=[r for r in rows if r['arm']==arm];assert len(rr)==20
  s={'correct':sum(r['correct'] for r in rr),'schema_valid':sum(r['schema_valid'] for r in rr),'parsed':sum(r['parsed'] for r in rr),'error_categories':dict(collections.Counter(r['error_category'] for r in rr if r['error_category'])),'per_class':{c:sum(r['correct'] for r in rr if r['gold_class']==c) for c in CLASSES},'by_composition':{c:sum(r['correct'] for r in rr if r['composition']==c) for c in ('simpler','composition-dependent')}}
  if arm=='O':
   families={}
   for family in sorted({r['family'] for r in rr}):
    subset=[r for r in rr if r['family']==family];families[family]={'joint_correct':sum(r['correct'] for r in subset),'individual_correct':sum(sum(r['individual_correct']) for r in subset),'worlds':2,'computations':4}
   s.update(individual_correct=sum(sum(r['individual_correct']) for r in rr),per_family=families,gate=s['correct']>=17 and all(f['joint_correct']>=1 for f in families.values()))
  elif arm=='S':
   fields={field:sum(r['fields'][field] for r in rr) for field in FIELDS};s.update(fields=fields,gate=s['correct']>=17 and min(fields.values())>=18)
  else:
   matrix={c:{selected:0 for selected in CLASSES+['INVALID_OUTPUT']} for c in CLASSES}
   for r in rr:matrix[r['gold_class']][r['selected'] if r['schema_valid'] and r['selected'] is not None else 'INVALID_OUTPUT']+=1
   subset=sum(r['correct'] for r in rr if r['gold_class'] in CLASSES[2:]);s.update(gate=s['correct']>=17 and min(s['per_class'].values())>=3,critical_epistemic_correct=subset,critical_epistemic_threshold_passed=subset>=10,confusion_matrix=matrix,matched_decisive_change='NOT_APPLICABLE_NO_PAIRS_PREREGISTERED')
  summaries[arm]=s
 lookup={(r['world_id'],r['arm']):r for r in rows};matched=[]
 for wid in sorted(glookup):
  stages={arm:lookup[wid,arm]['correct'] for arm in ARMS};matched.append({'world_id':wid,'family':glookup[wid]['family'],'class':glookup[wid]['class'],'correctness':stages,'R_selected':lookup[wid,'R']['selected'],'E_selected':lookup[wid,'E']['selected']})
 def association(condition,denominator):
  eligible=[w for w in matched if denominator(w['correctness'])];hits=[w['world_id'] for w in eligible if condition(w['correctness'])];return {'count':len(hits),'denominator':len(eligible),'worlds':hits}
 associations={
 'O_wrong_and_E_wrong':association(lambda x:not x['E'],lambda x:not x['O']),
 'O_correct_S_wrong':association(lambda x:not x['S'],lambda x:x['O']),
 'S_correct_R_wrong':association(lambda x:not x['R'],lambda x:x['S']),
 'all_isolated_correct_E_wrong':association(lambda x:not x['E'],lambda x:all(x[a] for a in 'OSR')),
 'E_correct_despite_isolated_error':association(lambda x:not all(x[a] for a in 'OSR'),lambda x:x['E']),
 'at_least_two_isolated_errors':association(lambda x:sum(not x[a] for a in 'OSR')>=2,lambda x:True)}
 for i,a in enumerate(ARMS):
  for b in ARMS[i+1:]:associations[a+'_'+b+'_both_wrong']=association(lambda x,b=b:not x[b],lambda x,a=a:not x[a])
 changed=[];missing=[];transitions={k:[] for k in ('correct_to_wrong','wrong_to_correct','wrong_to_different_wrong','unchanged')}
 for w in matched:
  wid=w['world_id'];r=lookup[wid,'R'];e=lookup[wid,'E'];recognized=r['selected'] is not None and e['selected'] is not None;different=recognized and r['selected']!=e['selected']
  if different:changed.append(wid)
  if not recognized:missing.append(wid)
  key='correct_to_wrong' if r['correct'] and not e['correct'] else 'wrong_to_correct' if not r['correct'] and e['correct'] else 'wrong_to_different_wrong' if not r['correct'] and not e['correct'] and different else 'unchanged';transitions[key].append(wid)
 gates={a:summaries[a]['gate'] for a in ARMS};finding_names={'O':'OPERATIONAL_COMPUTATION','S':'EVIDENCE_STATE_REASONING','R':'EPISTEMIC_REDUCTION','E':'END_TO_END_DIAGNOSIS'}
 return {'status':'DIAGNOSTIC_REASONING_FACTORIZATION_COMPLETE_V0','arms':summaries,'gates':gates,'findings':[finding_names[a]+('_COMPETENCE_ESTABLISHED' if gates[a] else '_COMPETENCE_NOT_ESTABLISHED') for a in ARMS],'registered_interpretation':interpretation(gates),'matched_worlds':matched,'associations':associations,'R_E_comparison':{'E_minus_R_correct':summaries['E']['correct']-summaries['R']['correct'],'recognized_class_disagreements':len(changed),'disagreement_worlds':changed,'missing_label_worlds':missing,'transitions':{k:len(v) for k,v in transitions.items()},'transition_worlds':transitions},'combined_system_capability':'NOT_TESTED_NO_STAGE_CHAINING','rows':rows}

def load_raw(folder):
 freeze=json.loads((folder/'raw-freeze.json').read_bytes());assert freeze['purpose']=='SCIENTIFIC_FACTORIZATION_V0','Mock evidence cannot be scored as scientific output'
 for name,want in freeze['sha256'].items():assert hashlib.sha256((folder/'raw'/name).read_bytes()).hexdigest()==want,name
 return json.loads((folder/'raw/execution.json').read_bytes())
def score(folder=P):
 execution=load_raw(folder)
 if execution['stop'] or execution['completed_calls']!=80:return {'status':'INVALID_STUDY','execution':execution,'findings':'NOT_ESTABLISHED_DUE_TO_INVALID_STUDY'}
 gold=json.loads((folder/'materialized/gold.json').read_bytes());lookup={g['world_id']:g for g in gold};manifest=json.loads((folder/'materialized/render-manifest.json').read_bytes());rows=[]
 for entry in manifest['entries']:
  g=lookup[entry['world_id']];arm=entry['arm'];r=grade((folder/'raw/finals'/(entry['render_id']+'.txt')).read_text(),arm,g[arm]);r.update(world_id=g['world_id'],render_id=entry['render_id'],arm=arm,gold_class=g['class'],family=g['family'],composition=g['composition']);rows.append(r)
 result=summarize(rows,gold);result.update(attempted=execution['attempted_calls'],completed=execution['completed_calls']);return result
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--raw-commit',required=True);ap.add_argument('--out',required=True,type=Path);args=ap.parse_args();root=P.parents[1];rel=str(P.relative_to(root));commit=args.raw_commit
 def git(*a):return subprocess.check_output(['git',*a],cwd=root)
 assert git('merge-base','--is-ancestor',commit,'HEAD')==b'';assert git('show',commit+':'+rel+'/raw-freeze.json')==(P/'raw-freeze.json').read_bytes();assert not git('ls-tree','--name-only',commit,'--',rel+'/scores.json').strip()
 freeze=json.loads((P/'raw-freeze.json').read_bytes())
 for name in freeze['sha256']:assert git('show',commit+':'+rel+'/raw/'+name)==(P/'raw'/name).read_bytes()
 result=score();result['raw_commit_before_scoring']=commit
 with args.out.open('xb') as f:f.write(raw(result))
 print(json.dumps({k:v for k,v in result.items() if k in ('status','gates','findings','registered_interpretation','attempted','completed')}))
