"""Posthoc descriptive decomposition only; cannot change any gate or candidate."""
import sys,json
from collections import Counter
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[1];sys.path.insert(0,str(P))
from data import rows,dump,FIELDS,status
from analysis import paired
out=dict(purpose='Posthoc descriptive error decomposition, not an additional gate or model-selection rule',cycles={})
for i in [1,2]:
 if not (P/f'M{i}-T{i}-scored.jsonl').exists():continue
 cases=rows(P/'materialized'/f'T{i}.jsonl');a=rows(P/f'M{i-1}-T{i}-scored.jsonl');b=rows(P/f'M{i}-T{i}-scored.jsonl')
 def confusion(scores):return {field:dict(Counter(row['gold'][field]+' -> '+(row['prediction'][field] if row['prediction'] else 'INVALID') for row in scores)) for field in FIELDS}
 subsets={
  'current_UNKNOWN':{c['id'] for c in cases if c['gold']['current_violation']=='UNKNOWN'},
  'prior_UNKNOWN':{c['id'] for c in cases if c['gold']['prior_violation']=='UNKNOWN'},
  'mixed_prior_aggregation':{c['id'] for c in cases if len({status(t) for t in c['state']['non_current_trials']})>1},
  'both_arms_schema_valid':{x['id'] for x,y in zip(a,b) if x['schema'] and y['schema']}}
 result=dict(incumbent_confusion=confusion(a),candidate_confusion=confusion(b),subset_comparisons={})
 for name,ids in subsets.items():
  if ids:result['subset_comparisons'][name]={m:paired([x for x in a if x['id'] in ids],[x for x in b if x['id'] in ids],m) for m in ['joint',*FIELDS]}

 for comparisons in result['subset_comparisons'].values():
  for comparison in comparisons.values():comparison.pop('mcnemar_exact_two_sided_p',None)
 harvest=rows(P/f'H{i}-scored.jsonl');result['harvest_error_breakdown']=dict(total_errors=sum(not x['joint'] for x in harvest),schema_invalid=sum(not x['schema'] for x in harvest),current_wrong=sum(not x['current_violation'] for x in harvest),prior_wrong=sum(not x['prior_violation'] for x in harvest),field_confusions=confusion(harvest));out['cycles'][str(i)]=result
dump(P/'descriptive-error-analysis.json',out)
