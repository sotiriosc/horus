"""Frozen exact scorer. No model access; rejects uncommitted, mutable, or qualification raw evidence."""
import argparse,json,subprocess
from collections import Counter
from common import *
def parse(text):
 def unique(items):
  d={}
  for k,v in items:
   if k in d:raise ValueError('duplicate key')
   d[k]=v
  return d
 try:
  x=json.loads(text,object_pairs_hook=unique)
  return x['classification'] if type(x)==dict and set(x)=={'classification'} and x['classification'] in CLASSES else None
 except (ValueError,TypeError,KeyError):return None
def load_raw(p=P):
 freeze=json.loads((p/'raw-freeze.json').read_bytes())
 assert freeze['purpose']=='SCIENTIFIC_PRIMITIVE_REDUCTION_V0','Mock evidence forbidden'
 assert freeze['scoring_has_occurred'] is False
 for n,want in freeze['sha256'].items():
  f=p/'raw'/n;assert sha(f.read_bytes())==want and f.stat().st_mode&0o222==0
 execution=json.loads((p/'raw/execution.json').read_bytes());assert execution['attempted_calls']==execution['completed_calls']==50 and execution['stop'] is None
 return freeze
def score(p=P):
 load_raw(p)
 cases=json.loads((p/'materialized/cases.json').read_bytes());pairs=json.loads((p/'materialized/pairs.json').read_bytes());manifest=json.loads((p/'materialized/render-manifest.json').read_bytes());req={e['render_id']:e for e in manifest['entries']}
 rows=[];confusion={c:{d:0 for d in CLASSES+['INVALID_OUTPUT']} for c in CLASSES};strata={};perclass={};selected={}
 for c in cases:
  sid=c['id'];final=(p/'raw/finals'/(sid+'.txt')).read_bytes();meta=json.loads((p/'raw/metadata'/(sid+'.json')).read_bytes());assert meta['final_sha256']==sha(final) and meta['request_sha256']==req[sid]['request_sha256']
  pred=parse(final);selected[sid]=pred;correct=pred==c['gold'];confusion[c['gold']][pred or 'INVALID_OUTPUT']+=1
  rows.append(dict(id=sid,gold=c['gold'],selected=pred,schema_valid=pred is not None,correct=correct,stratum=c['stratum'],family=c['family']))
 for key,target in [('gold',perclass),('stratum',strata)]:
  for group in sorted({r[key] for r in rows}):
   rr=[r for r in rows if r[key]==group];target[group]=dict(correct=sum(r['correct'] for r in rr),total=len(rr))
 pp=[]
 for pair in pairs:
  a,b=[selected[pair['endpoints'][s]] for s in 'AB'];exact=a==pair['gold_A'] and b==pair['gold_B'];transition=exact and ((a!=b)==pair['changing'])
  pp.append(dict(id=pair['id'],family=pair['family'],gold_A=pair['gold_A'],gold_B=pair['gold_B'],selected_A=a,selected_B=b,gold_changes=pair['changing'],tracks_required_transition=transition,exact_pair_pass=transition))
 groups={}
 for name,subset in [('changing',[r for r in pp if r['gold_changes']]),('stable',[r for r in pp if not r['gold_changes']])]:groups[name]=dict(passed=sum(r['exact_pair_pass'] for r in subset),total=len(subset))
 accuracy=sum(r['correct'] for r in rows);primary=accuracy>=43 and all(x['correct']>=8 for x in perclass.values());secondary=groups['changing']['passed']>=12 and groups['stable']['passed']>=8
 diag={}
 for name in ['SUFFICIENCY','CONTRADICTION','HISTORY','OBSERVATION']:
  rr=[r for r in rows if r['family']==name];pr=[r for r in pp if r['family']==name];diag[name]=dict(correct=sum(r['correct'] for r in rr),total=len(rr),pair_pass=sum(r['exact_pair_pass'] for r in pr),pairs=len(pr))
 # Context subsets fixed by primitive propositions, independent of predictions.
 xsub={}
 for name,condition in [('current_mismatch',lambda c:c['state']['current_trial']['observation_requirement']=='MISMATCH'),('historical_mismatch',lambda c:c['state']['historical_trial'] is not None and c['state']['historical_trial']['observation_requirement']=='MISMATCH'),('current_underdetermined',lambda c:c['state']['current_trial']['evidence_sufficiency']=='UNDERDETERMINED')]:
  cc=[c for c in cases if c['gold']==X and condition(c)];xsub[name]=dict(correct=sum(selected[c['id']]==X for c in cc),total=len(cc))
 return dict(study='QWEN_PRIMITIVE_TO_ONTOLOGY_REDUCTION_V0',scheduled=50,attempted=50,completed=50,schema_valid=sum(r['schema_valid'] for r in rows),correct=accuracy,total=50,per_class=perclass,confusion=confusion,primary_gate='PRIMITIVE_TO_ONTOLOGY_REDUCTION_'+('ESTABLISHED' if primary else 'NOT_ESTABLISHED'),secondary_pair_gate=secondary,pair_groups=groups,strata=strata,diagnostics=diag,contradiction_contexts=xsub,registered_interpretation='EXPLICIT_PRIMITIVE_REDUCTION_SUPPORTED' if primary else 'EXPLICIT_PRIMITIVE_REDUCTION_NOT_ESTABLISHED',pair_caveat='REDUCTION_ACCURACY_WITH_UNRELIABLE_COUNTERFACTUAL_SENSITIVITY' if primary and not secondary else None,endpoints=rows,pairs=pp)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);a.add_argument('--raw-commit',required=True);args=a.parse_args()
 prefix='research/qwen-primitive-to-ontology-reduction-v0/'
 tracked=subprocess.check_output(['git','show',args.raw_commit+':'+prefix+'raw-freeze.json'],cwd=P)
 assert tracked==(P/'raw-freeze.json').read_bytes()
 for n in json.loads(tracked)['sha256']:
  b=subprocess.check_output(['git','show',args.raw_commit+':'+prefix+'raw/'+n],cwd=P);assert b==(P/'raw'/n).read_bytes()
 assert subprocess.check_output(['git','show',args.raw_commit+':'+prefix+'score.py'],cwd=P)==Path(__file__).read_bytes()
 dump(args.out,score())
