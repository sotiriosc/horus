"""Frozen exact two-field scorer; no diagnostic ontology or model access."""
import argparse,json,subprocess,itertools
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
  return x if type(x)==dict and set(x)==set(FIELDS) and all(type(x[k])==str and x[k] in VALUES for k in FIELDS) else None
 except (ValueError,TypeError,KeyError):return None
def load_raw(p=P):
 f=json.loads((p/'raw-freeze.json').read_bytes());assert f['purpose']=='SCIENTIFIC_TEMPORAL_STATE_V0','Mock evidence forbidden';assert f['scoring_has_occurred'] is False
 for n,h in f['sha256'].items():
  path=p/'raw'/n;assert sha(path.read_bytes())==h and path.stat().st_mode&0o222==0
 e=json.loads((p/'raw/execution.json').read_bytes());assert e['attempted_calls']==e['completed_calls']==36 and e['stop'] is None
 return f
def gate(m):
 checks=dict(joint_at_least_32=m['joint_correct']>=32,current_at_least_34=m['field_correct']['current_violation']>=34,prior_at_least_34=m['field_correct']['prior_violation']>=34,historical_focus_at_least_11=m['historical_focus']['correct']>=11,changing_pairs_at_least_9=m['changing_pairs']['passed']>=9,stable_pairs_all_8=m['stable_pairs']['passed']>=8,schema_valid_at_least_35=m['schema_valid']>=35)
 passed=all(checks.values());return dict(passed=passed,conditions=checks,registered_interpretation='TEMPORAL_STATE_REPRESENTATION_ESTABLISHED' if passed else 'TEMPORAL_STATE_REPRESENTATION_NOT_ESTABLISHED',project_recommendation='Consider a separately authorized factorized-state engineering experiment; no architecture change in this study.' if passed else 'Put the current Horus research direction on hold pending a genuinely new technical hypothesis, model capability or architecture. Do not launch another prompt workaround or decomposition benchmark.')
def score(p=P):
 load_raw(p);cases=json.loads((p/'materialized/cases.json').read_bytes());pairs=json.loads((p/'materialized/pairs.json').read_bytes());manifest=json.loads((p/'materialized/render-manifest.json').read_bytes());entries={e['render_id']:e for e in manifest['entries']};rows=[];selected={}
 fconf={k:{v:{pred:0 for pred in VALUES+['INVALID_OUTPUT']} for v in VALUES} for k in FIELDS};labels=['/'.join(x) for x in itertools.product(VALUES,repeat=2)];jconf={v:{pred:0 for pred in labels+['INVALID_OUTPUT']} for v in labels}
 for c in cases:
  sid=c['id'];b=(p/'raw/finals'/(sid+'.txt')).read_bytes();meta=json.loads((p/'raw/metadata'/(sid+'.json')).read_bytes());assert sha(b)==meta['final_sha256'] and entries[sid]['request_sha256']==meta['request_sha256']
  pred=parse(b);selected[sid]=pred;gold=c['gold'];fc={k:pred is not None and pred[k]==gold[k] for k in FIELDS}
  for k in FIELDS:fconf[k][gold[k]][pred[k] if pred else 'INVALID_OUTPUT']+=1
  g='/'.join(gold[k] for k in FIELDS);v='/'.join(pred[k] for k in FIELDS) if pred else 'INVALID_OUTPUT';jconf[g][v]+=1
  rows.append(dict(id=sid,pair=c['pair'],side=c['side'],gold=gold,selected=pred,schema_valid=pred is not None,field_correct=fc,joint_correct=all(fc.values()),historical_focus=c['historical_focus'],family=c['family'],contradictory_package=c['state']['package']['consistency']=='CONTRADICTORY',prior_trial_count=len(c['state']['non_current_trials'])))
 pp=[]
 for pair in pairs:
  a,b=[selected[pair['endpoints'][side]] for side in 'AB'];ga,gb=pair['gold_A'],pair['gold_B'];exact=a==ga and b==gb;changed=[k for k in FIELDS if ga[k]!=gb[k]]
  required_flip=a is not None and b is not None and bool(changed) and all(a[k]==ga[k] and b[k]==gb[k] for k in changed)
  pp.append(dict(id=pair['id'],family=pair['family'],changing=pair['changing'],gold_A=ga,gold_B=gb,selected_A=a,selected_B=b,changed_output_fields=changed,exact_pair_pass=exact,required_flip_on_changed_field=required_flip if changed else None,selected_vector_stable=(a==b) if a is not None and b is not None else False))
 changing=[r for r in pp if r['changing']];stable=[r for r in pp if not r['changing']];focus=[r for r in rows if r['historical_focus']]
 m=dict(joint_correct=sum(r['joint_correct'] for r in rows),field_correct={k:sum(r['field_correct'][k] for r in rows) for k in FIELDS},schema_valid=sum(r['schema_valid'] for r in rows),historical_focus=dict(correct=sum(r['joint_correct'] for r in focus),total=12),changing_pairs=dict(passed=sum(r['exact_pair_pass'] for r in changing),total=10,required_flip_on_changed_field=sum(r['required_flip_on_changed_field'] for r in changing)),stable_pairs=dict(passed=sum(r['exact_pair_pass'] for r in stable),total=8,selected_vector_stable=sum(r['selected_vector_stable'] for r in stable)),matched_pairs=dict(passed=sum(r['exact_pair_pass'] for r in pp),total=18))
 subsets={}
 for name,subset in [('contradictory_packages',[r for r in rows if r['contradictory_package']]),('consistent_packages',[r for r in rows if not r['contradictory_package']]),('multiple_prior_trials',[r for r in rows if r['prior_trial_count']>1]),('prior_unknown',[r for r in rows if r['gold']['prior_violation']=='UNKNOWN']),('current_unknown',[r for r in rows if r['gold']['current_violation']=='UNKNOWN'])]:subsets[name]=dict(correct=sum(r['joint_correct'] for r in subset),total=len(subset))
 return dict(study='HORUS_TEMPORAL_STATE_REPRESENTATION_GATE_V0',scheduled=36,attempted=36,completed=36,optional_arm=False,metrics=m,gate=gate(m),field_confusion=fconf,joint_confusion=jconf,subsets=subsets,endpoints=rows,pairs=pp)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);a.add_argument('--raw-commit',required=True);args=a.parse_args();prefix='research/qwen-temporal-state-representation-v0/'
 f=subprocess.check_output(['git','show',args.raw_commit+':'+prefix+'raw-freeze.json'],cwd=P);assert f==(P/'raw-freeze.json').read_bytes()
 for n in json.loads(f)['sha256']:assert subprocess.check_output(['git','show',args.raw_commit+':'+prefix+'raw/'+n],cwd=P)==(P/'raw'/n).read_bytes()
 assert subprocess.check_output(['git','show',args.raw_commit+':'+prefix+'score.py'],cwd=P)==Path(__file__).read_bytes()
 dump(args.out,score())
