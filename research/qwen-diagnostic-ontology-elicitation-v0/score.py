"""Frozen mechanical final-channel scoring. No model calls or subjective rescue."""
import argparse,collections,hashlib,json,math,subprocess
from pathlib import Path
import jsonschema
from generate import CLASSES,raw
P=Path(__file__).resolve().parent

def strict(text):
 def pairs(items):
  out={}
  for k,v in items:
   if k in out:raise ValueError('duplicate JSON key')
   out[k]=v
  return out
 def bad(s):raise ValueError('nonfinite JSON '+s)
 def number(s):
  v=float(s)
  if not math.isfinite(v):raise ValueError("nonfinite JSON number")
  return v
 return json.loads(text,object_pairs_hook=pairs,parse_constant=bad,parse_float=number)
def equal(a,b):return type(a) is type(b) and a==b

def grade(text,schema,gold,mapping=None):
 result={'parsed':False,'schema_valid':False,'selected':None,'correct':False};obj=None
 try:
  obj=strict(text);result['parsed']=True
  if isinstance(obj,dict):
   label=obj.get('classification');decoded={v:k for k,v in mapping.items()}.get(label) if mapping and isinstance(label,str) else label
   if decoded in CLASSES:result['selected']=decoded
  jsonschema.Draft7Validator(schema).validate(obj);result['schema_valid']=True
 except (ValueError,TypeError,jsonschema.ValidationError):pass
 result['correct']=result['schema_valid'] and result['selected']==gold['classification']
 return result,obj

def witness(obj,result,gold,evidence):
 obj=obj if isinstance(obj,dict) else {};cites=obj.get('evidence_ids',[]);cites=cites if isinstance(cites,list) else []
 ids={r['id'] for r in evidence['records']};required=gold['required_evidence_ids'];cited={c for c in cites if isinstance(c,str)}
 out={'required_citations':len(required),'present_required_citations':len(set(required)&cited),'citation_complete':set(required)<=cited,'nonexistent_evidence_ids':sorted(cited-ids)}
 if 'witness' in gold:
  w=gold['witness'];cm=obj.get('causal_mechanism');cm=cm if isinstance(cm,dict) else {}
  criteria={'primary_classification':result['correct'],'affected_component':obj.get('affected_component_ids')==w['affected_component_ids'],'citation_complete':out['citation_complete']}
  for k,v in w.items():
   if k!='affected_component_ids':criteria[k]=equal(cm.get(k),v)
  out.update(criteria=criteria,full_witness=all(criteria.values()),exact_field_value_localization=all(criteria[k] for k in ('decisive_evidence_id','decisive_field','observed_value','required_value')))
 return out

def load_raw(folder):
 freeze=json.loads((folder/'raw-freeze.json').read_bytes());assert freeze['purpose']=='SCIENTIFIC_ONTOLOGY_V0','Mock evidence cannot be scored as scientific output'
 for name,want in freeze['sha256'].items():assert hashlib.sha256((folder/'raw'/name).read_bytes()).hexdigest()==want,name
 return json.loads((folder/'raw/execution.json').read_bytes())

def score(folder=P):
 execution=load_raw(folder)
 if execution['stop'] or execution['completed_calls']!=100:return {'status':'INVALID_STUDY','execution':execution,'findings':'NOT_ESTABLISHED_DUE_TO_INVALID_STUDY'}
 manifest=json.loads((folder/'materialized/render-manifest.json').read_bytes());golds={g['world_id']:g for g in json.loads((folder/'materialized/gold.json').read_bytes())};maps=json.loads((folder/'materialized/label-maps.json').read_bytes())['mappings'];rows=[]
 for e in manifest['entries']:
  w=e['world_id'];g=golds[w];req=json.loads((folder/'materialized'/e['request_path']).read_bytes());schema=req['response_format']['schema']
  text=(folder/'raw/finals'/(e['render_id']+'.txt')).read_text();r,obj=grade(text,schema,g,maps[e['mapping']] if e['arm']=='C' else None)
  r.update(world_id=w,render_id=e['render_id'],arm=e['arm'],gold=g['classification'],difficulty=g['difficulty'])
  if e['arm']=='E':r['evidence']=witness(obj,r,g,json.loads((folder/'materialized/evidence'/(w+'.json')).read_bytes()))
  rows.append(r)
 arms={}
 for a in 'ABCDE':
  rr=[r for r in rows if r['arm']==a];byclass={c:sum(r['correct'] for r in rr if r['gold']==c) for c in CLASSES};ux=sum(r['correct'] for r in rr if r['gold'] in CLASSES[2:])
  arms[a]={'correct':sum(r['correct'] for r in rr),'schema_valid':sum(r['schema_valid'] for r in rr),'parsed':sum(r['parsed'] for r in rr),'by_class':byclass,'critical_epistemic':ux,'by_difficulty':{d:sum(r['correct'] for r in rr if r['difficulty']==d) for d in ('primitive','composite')},'by_class_difficulty':{c:{d:sum(r['correct'] for r in rr if r['gold']==c and r['difficulty']==d) for d in ('primitive','composite')} for c in CLASSES}}
  arms[a]['ontology_gate']=arms[a]['correct']>=17 and min(byclass.values())>=3;arms[a]['epistemic_gate']=ux>=10
 contrasts={};lookup={(r['world_id'],r['arm']):r for r in rows}
 for a in 'BCDE':
  transition={k:[] for k in ('correct_to_wrong','wrong_to_correct','wrong_to_different_wrong','unchanged')};dis=[];missing=[];flips=[]
  for w in sorted(golds):
   x,y=lookup[w,'A'],lookup[w,a];different=x['selected'] is not None and y['selected'] is not None and x['selected']!=y['selected']
   if different:dis.append(w)
   if x['selected'] is None or y['selected'] is None:missing.append(w)
   if x['selected']==y['selected'] and x['schema_valid']!=y['schema_valid']:flips.append(w)
   k='correct_to_wrong' if x['correct'] and not y['correct'] else 'wrong_to_correct' if not x['correct'] and y['correct'] else 'wrong_to_different_wrong' if not x['correct'] and not y['correct'] and different else 'unchanged'
   transition[k].append(w)
  contrasts['A_'+a]={'accuracy_delta_count':arms[a]['correct']-arms['A']['correct'],'class_disagreements':len(dis),'disagreement_worlds':dis,'missing_label_worlds':missing,'same_label_schema_flips':flips,'transitions':{k:len(v) for k,v in transition.items()},'transition_worlds':transition}
 findings=['MINIMAL_ONTOLOGY_GATE_'+('PASSED' if arms['A']['ontology_gate'] else 'FAILED'),'EPISTEMIC_DISTINCTION_GATE_'+('PASSED' if arms['A']['epistemic_gate'] else 'FAILED')]
 for name,yes in [('ORDER_SENSITIVITY',contrasts['A_B']['class_disagreements']>=4),('LABEL_SENSITIVITY',contrasts['A_C']['class_disagreements']>=4),('RATIONALE_BURDEN',arms['D']['correct']<=arms['A']['correct']-4),('STRUCTURED_CLASSIFICATION_BURDEN',arms['E']['correct']<=arms['A']['correct']-4)]:findings.append(name+('_PRESENT' if yes else '_NOT_ESTABLISHED'))
 ee=[r['evidence'] for r in rows if r['arm']=='E'];dd=[e for e in ee if 'criteria' in e]
 metrics={'current_denominator':4,'full_witness':sum(e['full_witness'] for e in dd),'exact_field_value_localization':sum(e['exact_field_value_localization'] for e in dd),'current_criteria':{k:sum(e['criteria'][k] for e in dd) for k in dd[0]['criteria']},'current_required_citations':sum(e['required_citations'] for e in dd),'current_present_required_citations':sum(e['present_required_citations'] for e in dd),'all_complete_citations':sum(e['citation_complete'] for e in ee),'all_required_citations':sum(e['required_citations'] for e in ee),'all_present_required_citations':sum(e['present_required_citations'] for e in ee),'nonexistent_citation_outputs':sum(bool(e['nonexistent_evidence_ids']) for e in ee)}
 return {'status':'QWEN_DIAGNOSTIC_ONTOLOGY_ELICITATION_COMPLETE_V0','attempted':execution['attempted_calls'],'completed':execution['completed_calls'],'findings':findings,'arms':arms,'contrasts':contrasts,'structured_metrics':metrics,'all_arms_strong':all(a['ontology_gate'] and a['epistemic_gate'] for a in arms.values()),'rows':rows}

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--raw-commit',required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
 root=P.parents[1];rel=str(P.relative_to(root));commit=args.raw_commit
 def git(*a):return subprocess.check_output(['git',*a],cwd=root)
 assert git('merge-base','--is-ancestor',commit,'HEAD')==b''
 assert git('show',commit+':'+rel+'/raw-freeze.json')==(P/'raw-freeze.json').read_bytes()
 assert not git('ls-tree','--name-only',commit,'--',rel+'/scores.json').strip(),'Raw freeze commit must precede scoring'
 freeze=json.loads((P/'raw-freeze.json').read_bytes())
 for name in freeze['sha256']:assert git('show',commit+':'+rel+'/raw/'+name)==(P/'raw'/name).read_bytes()
 result=score();result['raw_commit_before_scoring']=commit
 with args.out.open('xb') as f:f.write(raw(result))
 print(json.dumps({k:v for k,v in result.items() if k in ('status','findings','arms','structured_metrics')}))
