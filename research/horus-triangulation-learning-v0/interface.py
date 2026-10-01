"""Model-visible messages and schemas. No simulator or hypothesis imports."""
import json,itertools
from collections import Counter
GENERIC='Choose the legal experiment that you expect will provide the most useful evidence about how this unfamiliar machine works.'
CHOICE=GENERIC+' Every experiment starts from the known reset state. Past executed observations are authoritative. Model analyses, if supplied, are provisional hypotheses. Choose an ID from legal_probes. Return only {"probe_id":"P000"} with your chosen legal ID.'
ANALYSIS='''Investigate this unfamiliar deterministic reset machine using Time, Relation and Direction. Truthful observations must be compatible, but your explanations are provisional. Use the complete execution ledger. Time: consider onset, persistence, delay, order and repetition; an unobserved effect is not a proved temporal bound. Relation: seek controlled contrasts, such as B/AB, AB/BA or B/BB; no direct effect does not imply no modifier effect. Direction: identify the unresolved distinction relevant to the current objective. Prefer the smallest legal contrast that could distinguish an explanation from a viable alternative; use longer sequences when shorter contrasts cannot resolve it. Do not repeat just because a probe is familiar. Do not claim an unexecuted outcome. Return the requested JSON analysis with concise phrases, at most 120 words total. Treat previous_model_hypothesis as unverified. For each what_result field, begin with "step=N;sensor=NAME;bit=V;meaning=" identifying a predicted observable alternative for your proposed experiment: A is your favored expectation and B a contradictory viable alternative at the same step/sensor. The meaning text is provisional. Do not output a probe choice here; a separate legal-ID choice follows.'''
ANALYSIS_SHAPE={
 'unresolved_question':'...',
 'time':{'known_constraints':'...','remaining_temporal_uncertainty':'...'},
 'relation':{'known_relations':'...','comparison_needed':'...'},
 'direction':{'current_objective':'...','why_this_uncertainty_matters':'...'},
 'candidate_experiment_logic':'...',
 'what_result_A_would_mean':'step=1;sensor=NAME;bit=0;meaning=...',
 'what_result_B_would_mean':'step=1;sensor=NAME;bit=1;meaning=...'}
PREDICT='''Each experiment and query start independently from the same known reset state. Predict the complete sensor trace for query_probe using only the executed experiment ledger. Return only {"predicted_observations":[...]} with one object per query action, every named sensor in each object, and integer bits 0 or 1. Do not output explanations.'''
def strict_json(text):
 def pairs(items):
  d={}
  for k,v in items:
   if k in d:raise ValueError('Duplicate JSON key')
   d[k]=v
  return d
 return json.loads(text,object_pairs_hook=pairs)
def parse_analysis(text):
 x=strict_json(text);assert type(x) is dict and set(x)==set(ANALYSIS_SHAPE)
 for k,template in ANALYSIS_SHAPE.items():
  if type(template) is dict:
   assert type(x[k]) is dict and set(x[k])==set(template)
   assert all(type(v) is str and v.strip() for v in x[k].values())
  else:assert type(x[k]) is str and x[k].strip()
 return x

def parse_choice(text,legal):
 x=strict_json(text);assert type(x) is dict and set(x)=={'probe_id'}
 assert type(x['probe_id']) is str and x['probe_id'] in {r['id'] for r in legal}
 return x['probe_id']
def parse_prediction(text,sensors,length):
 x=strict_json(text);assert type(x) is dict and set(x)=={'predicted_observations'}
 obs=x['predicted_observations'];assert type(obs) is list and len(obs)==length
 assert all(type(row) is dict and set(row)==set(sensors) and all(type(v) is int and v in (0,1) for v in row.values()) for row in obs)
 return obs

def messages(ports,reset,ledger,mode,legal=None,analysis=None,previous_analysis=None,query=None,target=None):
 data=dict(actuators=ports['actuators'],sensors=ports['sensors'],reset_observation=reset,authenticated_experiments=ledger,exact_probe_repeat_counts=dict(sorted(Counter(','.join(x['probe']) for x in ledger).items())))
 if mode in ('analysis','choice'):
  assert legal is not None
  data.update(legal_probes=legal,experiment_number=len(ledger)+1,remaining_experiments=12-len(ledger),current_objective='Reduce uncertainty to predict unfamiliar probe outcomes.')
  if target is not None:data['current_objective']='Learn distinctions useful for reaching the supplied target.';data['target']=target
  if mode=='analysis':
   instruction=ANALYSIS;data['required_analysis_shape']=ANALYSIS_SHAPE
   if previous_analysis is not None:data['previous_model_hypothesis']=dict(authority='UNVERIFIED_MODEL_HYPOTHESIS',raw_text=previous_analysis)
  else:
   instruction=CHOICE
   if analysis is not None:data['triangulation_analysis']=dict(authority='UNVERIFIED_MODEL_HYPOTHESIS',raw_text=analysis)
 elif mode=='prediction':
  assert query is not None;instruction=PREDICT;data['query_probe']=query
  if target is not None:data['control_target']=target
 else:raise ValueError(mode)
 return [{'role':'system','content':instruction},{'role':'user','content':json.dumps(data,separators=(',',':'))}]

def synthetic_fixture():
 ports=dict(actuators=['K7','Q2','N4','W8'],sensors=['V9','R3','Z8','M6']);reset=dict.fromkeys(ports['sensors'],0)
 allp=[list(p) for n in (1,2,3) for p in itertools.product(ports['actuators'],repeat=n)]
 reserved=[['K7','K7','K7'],['K7','K7','Q2'],['K7','Q2','K7'],['K7','Q2','Q2'],['K7','Q2','N4']]
 legal=[dict(id=f'P{i:03d}',sequence=p) for i,p in enumerate(p for p in allp if p not in reserved)]
 ledger=[dict(experiment=i+1,probe_id=legal[-1-i]['id'],probe=legal[-1-i]['sequence'],observations=[{s:(i+j+k)%2 for k,s in enumerate(ports['sensors'])} for j in range(3)]) for i in range(12)]
 return ports,reset,legal,ledger
