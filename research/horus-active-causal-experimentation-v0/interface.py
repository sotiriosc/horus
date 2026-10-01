"""Allowlisted model-visible interface. No oracle, DSL, root IDs, or programs."""
import itertools,json
from collections import Counter
ACTIVE='''You are investigating an unfamiliar deterministic machine. Each probe starts at the same reset state. Choose the next experiment that you expect will most reduce uncertainty about how its actuators influence its observable sensors. Use prior executed experiments. Compare direct effects, interactions, ordering and delays when useful. Repeating an experiment is allowed when informative. You have a limited budget. Return only a JSON object with exactly one key "probe", whose value is one sequence in allowed_probes. Do not output explanations.'''
PREDICT='''You are investigating an unfamiliar deterministic machine. Every experiment and the query start independently at the same reset state. Use only the executed experiments to predict the full sensor trace of query_probe. Return only {"predicted_observations":[...]}: one sensor-to-bit object per query action, with every named sensor present and each value integer 0 or 1. Do not output explanations.'''
def history(ledger):
 return dict(experiments=ledger,exact_probe_repeat_counts=dict(sorted(Counter(','.join(x['probe']) for x in ledger).items())))
def messages(ports,reset,ledger,allowed=None,query=None,target=None):
 data=dict(actuators=ports['actuators'],sensors=ports['sensors'],reset_observation=reset,**history(ledger))
 if allowed is not None:
  data.update(allowed_probes=allowed,experiment_number=len(ledger)+1,remaining_budget=12-len(ledger));instruction=ACTIVE
 else:
  assert query is not None;data['query_probe']=query;instruction=PREDICT
  if target is not None:data['control_target']=target
 return [{'role':'system','content':instruction},{'role':'user','content':json.dumps(data,separators=(',',':'))}]
def strict_json(text):
 def pairs(items):
  out={}
  for k,v in items:
   if k in out:raise ValueError('Duplicate JSON key')
   out[k]=v
  return out
 return json.loads(text,object_pairs_hook=pairs)
def parse_probe(text,allowed):
 x=strict_json(text)
 assert type(x) is dict and set(x)=={'probe'} and type(x['probe']) is list
 assert all(type(a) is str for a in x['probe']) and x['probe'] in allowed
 return x['probe']
def parse_prediction(text,sensors,length):
 x=strict_json(text);assert type(x) is dict and set(x)=={'predicted_observations'}
 obs=x['predicted_observations'];assert type(obs) is list and len(obs)==length
 assert all(type(row) is dict and set(row)==set(sensors) and all(type(v) is int and v in (0,1) for v in row.values()) for row in obs)
 return obs
def synthetic_fixtures():
 ports=dict(actuators=['K7','Q2','N4','W8'],sensors=['V9','R3','Z8','M6'])
 allp=[list(p) for n in (1,2,3) for p in itertools.product(ports['actuators'],repeat=n)]
 reserved=[['K7','K7','K7'],['K7','K7','Q2'],['K7','Q2','K7'],['K7','Q2','Q2'],['K7','Q2','N4']]
 allowed=[p for p in allp if p not in reserved];reset=dict.fromkeys(ports['sensors'],0)
 ledger=[dict(experiment=i+1,probe=allowed[-1-i],observations=[{s:(i+j+k)%2 for k,s in enumerate(ports['sensors'])} for j in range(3)]) for i in range(12)]
 fixtures=[]
 for n in (0,3,9,11):fixtures.append(dict(kind='selection',messages=messages(ports,reset,ledger[:n],allowed=allowed),allowed=allowed))
 for n in (1,2,3):fixtures.append(dict(kind='prediction',messages=messages(ports,reset,ledger,query=['K7']*n),sensors=ports['sensors'],length=n))
 return fixtures
