"""Frozen zero-inference outcome metrics, usable only after raw commit."""
import argparse,collections,json,statistics,subprocess
from .runtime import ROOT,PUBLIC,write,sha

def mean(xs):return statistics.mean(xs) if xs else None
def summarize(rows):
 rows=sorted(rows,key=lambda x:x['global_index']);seen={};negative=set();relations=set();routes=collections.Counter();negative_repetitions=[];changes=[];last={}
 for r in rows:
  a=r['measurement']['action'];p=r['profile'];key=(p,a);c=r['realized_consequence'];d=r['decision']
  if key in negative:negative_repetitions.append(r['global_index'])
  if c<0:negative.add(key)
  relations.add(key)
  if p in last and last[p]!=a:changes.append(dict(index=r['global_index'],profile=p,previous_action=last[p],action=a,source=d['decision_source'] if d else 'STATIC_HOLD'))
  last[p]=a;routes[d['decision_source'] if d else 'STATIC_HOLD']+=1
 def metrics(rr):
  ratios=[x['measurement']['wall_seconds']/x['reference_seconds'] for x in rr if x['measurement']['wall_seconds'] is not None]
  wall=[x['measurement']['wall_seconds'] for x in rr if x['measurement']['wall_seconds'] is not None]
  return dict(decisions=len(rr),consequence=sum(x['realized_consequence'] for x in rr),outcome_counts={str(k):sum(x['realized_consequence']==k for x in rr) for k in (-1,0,1)},valid=sum(x['measurement']['valid'] for x in rr),invalid=sum(not x['measurement']['valid'] for x in rr),resource_failures=sum(x['measurement'].get('resource_violation',False) for x in rr),truncated=sum(x['measurement'].get('finish_reason')=='length' for x in rr),normalized_latency_mean=mean(ratios),normalized_latency_median=statistics.median(ratios) if ratios else None,request_seconds_total=sum(wall),request_seconds_mean=mean(wall),executor_seconds_total=sum(x['measurement'].get('executor_total_seconds',0) for x in rr),policy_seconds_total=sum(x['decision']['action_model_latency_seconds'] for x in rr if x['decision']),prompt_processing_ms_total=sum((x['measurement'].get('timings') or {}).get('prompt_ms',0) for x in rr),generation_ms_total=sum((x['measurement'].get('timings') or {}).get('predicted_ms',0) for x in rr),generation_tokens_per_second_mean=mean([(x['measurement'].get('timings') or {})['predicted_per_second'] for x in rr if (x['measurement'].get('timings') or {}).get('predicted_per_second')]))
 profiles={str(p):dict(early=metrics([r for r in rows if r['profile']==p and r['half']==0]),late=metrics([r for r in rows if r['profile']==p and r['half']==1]),all=metrics([r for r in rows if r['profile']==p])) for p in range(4)}
 paired=[]
 for wid in sorted({r['workload'] for r in rows}):
  rr=[r for r in rows if r['workload']==wid]
  if len(rr)==2:
   e,l=rr;paired.append(dict(workload=wid,profile=e['profile'],early_action=e['measurement']['action'],late_action=l['measurement']['action'],early_consequence=e['realized_consequence'],late_consequence=l['realized_consequence'],early_normalized=None if e['measurement']['wall_seconds'] is None else e['measurement']['wall_seconds']/e['reference_seconds'],late_normalized=None if l['measurement']['wall_seconds'] is None else l['measurement']['wall_seconds']/l['reference_seconds']))
 return dict(**metrics(rows),early=metrics([r for r in rows if r['half']==0]),late=metrics([r for r in rows if r['half']==1]),profiles=profiles,matched_prompts=paired,unique_action_context_relations=len(relations),relations=[list(x) for x in sorted(relations)],negative_repetitions=negative_repetitions,route_counts=dict(routes),E_acquisitions=routes['EMPIRICAL_EVIDENCE_ACQUISITION'],S_escapes=routes['STAGNATION_ESCAPE'],grounded_mechanical=routes['GROUNDED_MECHANICAL'],ordinary_model_decisions=sum(v for k,v in routes.items() if k not in ('EMPIRICAL_EVIDENCE_ACQUISITION','STAGNATION_ESCAPE','GROUNDED_MECHANICAL','STATIC_HOLD')),action_changes_after_experience=changes,memory_admissions=sum(r['decision'] is not None for r in rows),timeline=[dict(index=r['global_index'],profile=r['profile'],workload=r['workload'],action=r['measurement']['action'],consequence=r['realized_consequence'],source=r['decision']['decision_source'] if r['decision'] else 'STATIC_HOLD',valid=r['measurement']['valid'],wall_seconds=r['measurement']['wall_seconds']) for r in rows])

def gates(arms,integrity):
 a,b,c=(arms[x] for x in 'ABC')
 improved=sum(p['late']['normalized_latency_mean'] is not None and p['early']['normalized_latency_mean'] is not None and p['late']['normalized_latency_mean']<=.9*p['early']['normalized_latency_mean'] for p in a['profiles'].values())
 no_regression=all(p['late']['normalized_latency_mean'] is not None and p['early']['normalized_latency_mean'] is not None and p['late']['normalized_latency_mean']<=1.1*p['early']['normalized_latency_mean'] for p in a['profiles'].values())
 drift=None if not c['early']['normalized_latency_mean'] or c['late']['normalized_latency_mean'] is None else c['late']['normalized_latency_mean']/c['early']['normalized_latency_mean']
 checks=dict(integrity=integrity,A_all_valid=a['valid']==24,late_consequence_gain_at_least_four=a['late']['consequence']>=a['early']['consequence']+4,three_profiles_improve=improved>=3,no_profile_regresses=no_regression,aggregate_improves=bool(a['early']['normalized_latency_mean'] and a['late']['normalized_latency_mean'] is not None and a['late']['normalized_latency_mean']<=.9*a['early']['normalized_latency_mean']),static_drift_control=drift is not None and .9<=drift<=1.1,later_action_changed_after_experience=any(x['index']>12 for x in a['action_changes_after_experience']))
 exp=all(checks.values());eb=dict(experience_gate=exp,E_acquisition=a['E_acquisitions']>0,consequence_advantage=a['consequence']>=b['consequence']+4,latency_advantage=bool(b['normalized_latency_mean'] and a['normalized_latency_mean'] is not None and a['normalized_latency_mean']<=.9*b['normalized_latency_mean']),invalid_no_worse=a['invalid']<=b['invalid'],three_profiles_no_worse=sum(a['profiles'][p]['all']['normalized_latency_mean'] is not None and b['profiles'][p]['all']['normalized_latency_mean'] is not None and a['profiles'][p]['all']['normalized_latency_mean']<=b['profiles'][p]['all']['normalized_latency_mean'] for p in a['profiles'])>=3)
 classification='E_ADDS_REAL_TASK_BENEFIT' if all(eb.values()) else 'EXPERIENCE_CONDITIONED_IMPROVEMENT_SUPPORTED' if exp else 'REAL_TASK_INTEGRITY_ONLY' if integrity else 'INCOMPLETE_OR_INFRASTRUCTURE_INVALID'
 return dict(classification=classification,experience_gate=checks,E_benefit_gate=eb,static_late_early_ratio=drift,A_improved_profiles=improved)

def main():
 p=argparse.ArgumentParser();p.add_argument('--raw-commit',required=True);p.add_argument('--out',required=True);a=p.parse_args()
 subprocess.run(['git','merge-base','--is-ancestor',a.raw_commit,'HEAD'],cwd=ROOT,check=True)
 exists=subprocess.run(['git','cat-file','-e',a.raw_commit+':'+str((PUBLIC/'scores.json').relative_to(ROOT))],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 assert exists.returncode!=0,'raw commit already contains scoring'
 rows=[];hashes={}
 for f in sorted((PUBLIC/'raw').glob('*.json')):
  assert subprocess.check_output(['git','show',a.raw_commit+':'+str(f.relative_to(ROOT))],cwd=ROOT)==f.read_bytes()
  rows.append(json.loads(f.read_text()));hashes[f.name]=sha(f.read_bytes())
 audit=json.loads((PUBLIC/'postflight.json').read_text());restart=json.loads((PUBLIC/'restart.json').read_text()) if (PUBLIC/'restart.json').exists() else {}
 arms={arm:summarize([r for r in rows if r['arm']==arm]) for arm in 'ABC'}
 integrity=len(rows)==72 and audit['status']=='PASS' and restart.get('status')=='PASS'
 result=dict(status='SCORED',raw_pre_analysis_commit=a.raw_commit,raw_sha256=hashes,arms=arms,**gates(arms,integrity),source_attribution='Receipt-backed E overrides are deterministic; ordinary choices are model behavior conditioned on authenticated Memory. No memory ablation isolates the model-mediated effect.',scope='Exact repeated operational contexts only; no transfer, training, model improvement, RSI or promotion',oracle_analysis=False)
 write(a.out,result);print(json.dumps({'classification':result['classification'],'raw_rows':len(rows)}))
if __name__=='__main__':main()
