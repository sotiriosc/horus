"""Posthoc descriptive analysis of frozen scores only; zero model calls, no new gate."""
import json,sys
from pathlib import Path
from collections import Counter
P=Path('/home/sotiriosc/horus-causal-machine-learning-v0/research/horus-causal-machine-learning-v0');sys.path.insert(0,str(P))
from common import rows,dump
result={}
for arm,pool in [('C0','H1'),('C0','T1'),('C1','T1')]:
 scores=rows(P/f'{arm}-{pool}-scored.jsonl');cases={c['id']:c for c in rows(P/'materialized'/f'{pool}.jsonl')};exact=bits=0;position=[0]*4;patterns=Counter()
 for s in scores:
  c=cases[s['id']];names=c['visible']['sensors'];last=c['visible']['history'][-1][1];pred=dict(zip(names,map(int,last)));exact+=pred==s['actual'];bits+=sum(pred[n]==s['actual'][n] for n in names);patterns[''.join(str(s['actual'][n]) for n in names)]+=1
  for j,name in enumerate(names):position[j]+=s['prediction'] is not None and s['prediction'][name]==s['actual'][name]
 result[f'{arm}-{pool}']=dict(n=len(scores),model_exact=sum(s['exact'] for s in scores),model_bit_correct_by_sensor_list_position=position,model_total_bits=4*len(scores),persistence_baseline_exact=exact,persistence_baseline_bit_correct=bits,actual_sensor_pattern_counts=dict(sorted(patterns.items())))
control={}
for arm in ['C0','C1']:
 cs=rows(P/f'{arm}-U1-control-scored.jsonl');control[arm]=dict(actual_control_actions=sum(c['actions'] for c in cs),failures=dict(Counter(mode for c in cs for mode in c['failure_modes'])),selected_schema_invalid=sum(c['selected_schema_invalid'] for c in cs))
dump(P/'descriptive-results.json',dict(scope='Posthoc descriptive scoring of existing frozen endpoints; no inference, new worlds, new training, candidate selection, or gate changes. Persistence predicts the last observed sensor state, ignoring the proposed action.',prediction=result,control=control))
print(json.dumps(dict(persistence={k:v['persistence_baseline_exact'] for k,v in result.items()},control=control)))
