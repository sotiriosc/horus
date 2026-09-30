"""Frozen scorer: exact schema, paired semantic units, registered gates; no model access."""
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
 freeze=json.loads((p/'raw-freeze.json').read_bytes());assert freeze['purpose']=='SCIENTIFIC_ROLE_TEMPORAL_V0','Mock evidence forbidden'
 assert freeze['scoring_has_occurred'] is False
 for n,h in freeze['sha256'].items():
  f=p/'raw'/n;assert sha(f.read_bytes())==h and f.stat().st_mode&0o222==0
 e=json.loads((p/'raw/execution.json').read_bytes());assert e['attempted_calls']==e['completed_calls']==90 and e['stop'] is None
 return freeze
def gates(arms):
 a,b,c=[arms[x] for x in ARMS]
 def counts(x,k):return x['per_class'][k]['correct']
 conditions=dict(historical_at_least_5=counts(c,T)>=5,historical_gain_at_least_2=counts(c,T)-counts(a,T)>=2,overall_at_least_26=c['correct']>=26,each_nonhistorical_at_least_5=all(counts(c,k)>=5 for k in CLASSES if k!=T),changing_at_least_4=c['changing_pairs']['passed']>=4,stable_at_least_2=c['stable_pairs']['passed']>=2)
 primary=all(conditions.values());generic=counts(b,T)-counts(a,T)>=2 and all(counts(b,k)>=counts(a,k)-1 for k in CLASSES if k!=T)
 tradeoff=[]
 for arm in ['B','C']:
  x=arms[arm]
  if counts(x,T)-counts(a,T)>=2 and any(counts(x,k)<5 or counts(x,k)<counts(a,k)-1 for k in CLASSES if k!=T):tradeoff.append(arm)
 interpretation='GENERAL_OPERATIONAL_ROLE_GROUNDING_SUPPORTED' if primary and generic else 'TEMPORAL_ROLE_GROUNDING_SUPPORTED' if primary else 'ROLE_GROUNDING_TRADEOFF' if tradeoff else 'ROLE_GROUNDING_NOT_ESTABLISHED'
 return dict(primary_C_pass=primary,primary_conditions=conditions,generic_B_descriptive_indicator=generic,tradeoff_arms=tradeoff,registered_interpretation=interpretation,bare_replication_difference_flag=counts(a,T)>=5,partial_improvement_without_primary_pass=not primary and (generic or counts(c,T)>counts(a,T)))
def score(p=P):
 load_raw(p);cases=json.loads((p/'materialized/cases.json').read_bytes());pairs=json.loads((p/'materialized/pairs.json').read_bytes());manifest=json.loads((p/'materialized/render-manifest.json').read_bytes());entries={e['render_id']:e for e in manifest['entries']};selections={};armrows={a:[] for a in ARMS}
 for c in cases:
  sid=c['id'];selections[sid]={}
  for arm in ARMS:
   rid=sid+'-'+arm;final=(p/'raw/finals'/(rid+'.txt')).read_bytes();m=json.loads((p/'raw/metadata'/(rid+'.json')).read_bytes());assert m['final_sha256']==sha(final) and m['request_sha256']==entries[rid]['request_sha256']
   chosen=parse(final);selections[sid][arm]=chosen;armrows[arm].append(dict(id=sid,gold=c['gold'],selected=chosen,correct=chosen==c['gold'],schema_valid=chosen is not None))
 arms={}
 for arm,rr in armrows.items():
  pc={k:dict(correct=sum(r['correct'] for r in rr if r['gold']==k),total=6) for k in CLASSES};matrix={k:{label:0 for label in CLASSES+['INVALID_OUTPUT']} for k in CLASSES}
  for r in rr:matrix[r['gold']][r['selected'] or 'INVALID_OUTPUT']+=1
  pp=[]
  for pair in pairs:
   a,b=selections[pair['A']][arm],selections[pair['B']][arm];ok=a==pair['gold_A'] and b==pair['gold_B'] and (a!=b)==pair['changing']
   pp.append(dict(id=pair['id'],gold_A=pair['gold_A'],gold_B=pair['gold_B'],selected_A=a,selected_B=b,changing=pair['changing'],tracks_required_transition=ok,exact_pair_pass=ok))
  arms[arm]=dict(correct=sum(r['correct'] for r in rr),total=30,schema_valid=sum(r['schema_valid'] for r in rr),per_class=pc,confusion=matrix,historical=pc[T],non_historical=dict(correct=sum(r['correct'] for r in rr if r['gold']!=T),total=24),changing_pairs=dict(passed=sum(r['exact_pair_pass'] for r in pp if r['changing']),total=5),stable_pairs=dict(passed=sum(r['exact_pair_pass'] for r in pp if not r['changing']),total=3),pairs=pp)
 state_rows=[];patterns=Counter()
 for c in cases:
  chosen=selections[c['id']];correct={a:chosen[a]==c['gold'] for a in ARMS};pattern=''.join('1' if correct[a] else '0' for a in ARMS);patterns[pattern]+=1
  state_rows.append(dict(id=c['id'],gold=c['gold'],selected=chosen,correct=correct,correctness_pattern_ABC=pattern,C_regression=(correct['A'] or correct['B']) and not correct['C'],explicit_noncurrent_mismatch=any(t['observation_requirement']=='MISMATCH' for t in c['state']['non_current_trials']),temporal_facts=c['state'] if c['gold']==T else None))
 contrasts={}
 for before,after in [('A','B'),('B','C'),('A','C')]:
  groups={}
  for name,subset in [('all',state_rows),('historical',[r for r in state_rows if r['gold']==T]),('non_historical',[r for r in state_rows if r['gold']!=T]),('explicit_noncurrent_mismatch',[r for r in state_rows if r['explicit_noncurrent_mismatch']]),('no_explicit_noncurrent_mismatch',[r for r in state_rows if not r['explicit_noncurrent_mismatch']])]:
   groups[name]=dict(total=len(subset),wrong_to_correct=sum(not r['correct'][before] and r['correct'][after] for r in subset),correct_to_wrong=sum(r['correct'][before] and not r['correct'][after] for r in subset),both_correct=sum(r['correct'][before] and r['correct'][after] for r in subset),both_wrong=sum(not r['correct'][before] and not r['correct'][after] for r in subset))
  contrasts[before+'→'+after]=groups
 return dict(study='QWEN_ROLE_GROUNDED_TEMPORAL_REDUCTION_V0',scientific_units=30,scheduled=90,attempted=90,completed=90,arms=arms,gates=gates(arms),correctness_patterns_ABC={''.join(x):patterns[''.join(x)] for x in __import__('itertools').product('01',repeat=3)},contrasts=contrasts,state_table=state_rows,historical_states_all_explicit_noncurrent_mismatch=all(r['explicit_noncurrent_mismatch'] for r in state_rows if r['gold']==T),c_regressions=[r['id'] for r in state_rows if r['C_regression']])
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);a.add_argument('--raw-commit',required=True);args=a.parse_args();prefix='research/qwen-role-grounded-temporal-reduction-v0/'
 freeze=subprocess.check_output(['git','show',args.raw_commit+':'+prefix+'raw-freeze.json'],cwd=P);assert freeze==(P/'raw-freeze.json').read_bytes()
 for n in json.loads(freeze)['sha256']:assert subprocess.check_output(['git','show',args.raw_commit+':'+prefix+'raw/'+n],cwd=P)==(P/'raw'/n).read_bytes()
 assert subprocess.check_output(['git','show',args.raw_commit+':'+prefix+'score.py'],cwd=P)==Path(__file__).read_bytes()
 dump(args.out,score())
