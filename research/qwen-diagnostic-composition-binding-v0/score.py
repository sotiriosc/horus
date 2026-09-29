"""Frozen final-channel scoring; separate invariance and decisive-sensitivity gates."""
import argparse,collections,hashlib,json,math,subprocess
from pathlib import Path
import jsonschema
from generate import P,CLASSES,SCHEMA,raw,TAGS_A,FAMILIES

def strict(text):
 def pairs(items):
  result={}
  for k,v in items:
   if k in result:raise ValueError('duplicate key')
   result[k]=v
  return result
 def bad(s):raise ValueError('nonfinite number')
 def num(s):
  value=float(s)
  if not math.isfinite(value):raise ValueError('nonfinite number')
  return value
 return json.loads(text,object_pairs_hook=pairs,parse_constant=bad,parse_float=num)
def grade(text,gold):
 r={'parsed':False,'schema_valid':False,'selected':None,'correct':False}
 try:
  obj=strict(text);r['parsed']=True
  if isinstance(obj,dict) and obj.get('classification') in CLASSES:r['selected']=obj['classification']
  jsonschema.Draft7Validator(SCHEMA).validate(obj);r['schema_valid']=True
 except (ValueError,TypeError,jsonschema.ValidationError):pass
 r['correct']=r['schema_valid'] and r['selected']==gold;return r

def transitions(pairs):
 bins={k:[] for k in ('correct_to_wrong','wrong_to_correct','wrong_to_different_wrong','unchanged')};dis=[];missing=[];schema=[];stable=[];both=[]
 for unit,a,b in pairs:
  recognized=a['selected'] is not None and b['selected'] is not None;different=recognized and a['selected']!=b['selected']
  if different:dis.append(unit)
  if not recognized:missing.append(unit)
  if recognized and not different:stable.append(unit)
  if a['correct'] and b['correct']:both.append(unit)
  if a['selected']==b['selected'] and a['schema_valid']!=b['schema_valid']:schema.append(unit)
  key='correct_to_wrong' if a['correct'] and not b['correct'] else 'wrong_to_correct' if not a['correct'] and b['correct'] else 'wrong_to_different_wrong' if not a['correct'] and not b['correct'] and different else 'unchanged'
  bins[key].append(unit)
 return {'counts':{k:len(v) for k,v in bins.items()},'unit_memberships':bins,'selected_class_disagreements':len(dis),'disagreement_units':dis,'missing_label_units':missing,'same_label_schema_flips':schema,'recognized_stable':len(stable),'correct_at_both':len(both)}

def summarize(rows):
 levels={}
 for level in range(5):
  rr=[r for r in rows if r['part']=='A' and r['level']==level];assert len(rr)==10
  levels[str(level)]={'correct':sum(r['correct'] for r in rr),'schema_valid':sum(r['schema_valid'] for r in rr),'per_class':{c:sum(r['correct'] for r in rr if r['gold']==c) for c in CLASSES}}
 units=sorted({r['unit_id'] for r in rows if r['part']=='A'});lookup={(r['unit_id'],r['level']):r for r in rows if r['part']=='A'};cores=[]
 for u in units:
  rr=[lookup[u,l] for l in range(5)];labels=[r['selected'] for r in rr];valid=all(x is not None for x in labels);invariant=valid and len(set(labels))==1
  cores.append({'unit_id':u,'gold':rr[0]['gold'],'selected':labels,'correct':[r['correct'] for r in rr],'invariant':invariant,'correct_all_levels':all(r['correct'] for r in rr),'first_changed_level':next((l for l in range(1,5) if labels[0] is not None and labels[l] is not None and labels[l]!=labels[0]),None),'first_incorrect_level':next((l for l in range(5) if not rr[l]['correct']),None),'first_invalid_label_level':next((l for l in range(5) if labels[l] is None),None)})
 contrasts={f'L{x}_L{y}':transitions([(u,lookup[u,x],lookup[u,y]) for u in units]) for x,y in ((0,1),(1,2),(2,3),(3,4),(0,4))}
 pairs=[]
 for u in sorted({r['unit_id'] for r in rows if r['part']=='B'}):
  rr=sorted([r for r in rows if r['part']=='B' and r['unit_id']==u],key=lambda r:r['endpoint']);assert len(rr)==2
  changed=all(r['selected'] is not None for r in rr) and rr[0]['selected']!=rr[1]['selected'];passed=all(r['correct'] for r in rr) and changed
  pairs.append({'unit_id':u,'family':rr[0]['family'],'tag':rr[0]['tag'],'gold':[r['gold'] for r in rr],'selected':[r['selected'] for r in rr],'correct':[r['correct'] for r in rr],'class_changed':changed,'passed':passed})
 family={f:sum(p['passed'] for p in pairs if p['family']==f) for f in FAMILIES};endpoint=sum(r['correct'] for r in rows if r['part']=='B');npass=sum(p['passed'] for p in pairs);corepass=levels['0']['correct']>=9 and min(levels['0']['per_class'].values())>=1;allcorrect=sum(c['correct_all_levels'] for c in cores);invariance=allcorrect>=8;flip=npass>=8 and min(family.values())>=1
 findings=['MINIMAL_CORE_COMPETENCE_'+('ESTABLISHED' if corepass else 'NOT_ESTABLISHED'),'COMPOSITIONAL_INVARIANCE_'+('SUPPORTED' if invariance else 'NOT_ESTABLISHED'),'DECISIVE_COUNTERFACTUAL_SENSITIVITY_'+('SUPPORTED' if flip else 'NOT_ESTABLISHED')]
 tags_a={tag:{'level':l,'accuracy':levels[str(l)]['correct'],'denominator':10,'recognized_class_stability':contrasts[f'L{l-1}_L{l}']['recognized_stable'],'correct_both_levels':contrasts[f'L{l-1}_L{l}']['correct_at_both']} for l,tag in TAGS_A.items()};tags_b={}
 for tag in sorted({p['tag'] for p in pairs}):
  pp=[p for p in pairs if p['tag']==tag];tags_b[tag]={'pairs':len(pp),'pair_passes':sum(p['passed'] for p in pp),'class_changes':sum(p['class_changed'] for p in pp),'endpoint_correct':sum(sum(p['correct']) for p in pp),'endpoint_denominator':2*len(pp)}
 interpretations=[]
 if corepass and not invariance and flip:interpretations.append('A_STRONG_CORES_WEAK_INVARIANCE_STRONG_FLIPS')
 if not corepass:interpretations.append('B_WEAK_CORES')
 if invariance and not flip:interpretations.append('C_STRONG_INVARIANCE_WEAK_FLIPS')
 if not invariance and not flip:interpretations.append('D_BOTH_WEAK')
 if invariance and flip:interpretations.append('E_BOTH_STRONG')
 return {'status':'QWEN_DIAGNOSTIC_COMPOSITION_BINDING_COMPLETE_V0','findings':findings,'registered_patterns':interpretations,'A':{'levels':levels,'minimal_core_gate':corepass,'invariant_cores':sum(c['invariant'] for c in cores),'gold_preserving_invariant_cores':allcorrect,'compositional_invariance_gate':invariance,'cores':cores,'transitions':contrasts,'nonincreasing_aggregate_accuracy':all(levels[str(l)]['correct']>=levels[str(l+1)]['correct'] for l in range(4)),'tags':tags_a},'B':{'endpoint_accuracy':endpoint,'pair_passes':npass,'per_family':family,'sensitivity_gate':flip,'pairs':pairs,'tags':tags_b},'schema_valid':sum(r['schema_valid'] for r in rows),'rows':rows}

def load_raw(folder):
 freeze=json.loads((folder/'raw-freeze.json').read_bytes());assert freeze['purpose']=='SCIENTIFIC_BINDING_V0','Mock evidence cannot be scored as science'
 for name,want in freeze['sha256'].items():assert hashlib.sha256((folder/'raw'/name).read_bytes()).hexdigest()==want,name
 return json.loads((folder/'raw/execution.json').read_bytes())
def score(folder=P):
 execution=load_raw(folder)
 if execution['stop'] or execution['completed_calls']!=70:return {'status':'INVALID_STUDY','execution':execution,'findings':'NOT_ESTABLISHED_DUE_TO_INVALID_STUDY'}
 gold=json.loads((folder/'materialized/gold.json').read_bytes());rows=[]
 for g in gold:
  rid=g['render_id'];r=grade((folder/'raw/finals'/(rid+'.txt')).read_text(),g['classification']);r.update({k:g[k] for k in ('render_id','unit_id','part','level','endpoint','family','tag') if k in g});r['gold']=g['classification'];rows.append(r)
 result=summarize(rows);result.update(attempted=execution['attempted_calls'],completed=execution['completed_calls']);return result
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--raw-commit',required=True);ap.add_argument('--out',required=True,type=Path);args=ap.parse_args();root=P.parents[1];relative=str(P.relative_to(root));commit=args.raw_commit
 def git(*a):return subprocess.check_output(['git',*a],cwd=root)
 assert git('merge-base','--is-ancestor',commit,'HEAD')==b'';assert git('show',commit+':'+relative+'/raw-freeze.json')==(P/'raw-freeze.json').read_bytes();assert not git('ls-tree','--name-only',commit,'--',relative+'/scores.json').strip()
 freeze=json.loads((P/'raw-freeze.json').read_bytes())
 for name in freeze['sha256']:assert git('show',commit+':'+relative+'/raw/'+name)==(P/'raw'/name).read_bytes()
 result=score();result['raw_commit_before_scoring']=commit
 with args.out.open('xb') as f:f.write(raw(result))
 print(json.dumps({k:v for k,v in result.items() if k in ('status','findings','registered_patterns','attempted','completed','schema_valid')}))
