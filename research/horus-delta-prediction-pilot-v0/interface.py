"""Authenticated history and fresh non-authoritative analysis only."""
import json,importlib.util
from common import TRIAG,canon
spec=importlib.util.spec_from_file_location('prior_interface',TRIAG/'interface.py');prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
parse_choice=prior.parse_choice;parse_prediction=prior.parse_prediction
RESET_FACT='Every probe begins from the identical deterministic reset state. Executing an identical probe again therefore reproduces the same trace and cannot provide new evidence about this machine. Repeats remain legal; choose independently.'
SCOPE='The legal catalogue lists only experiments currently available in this task. Untried means a known available experiment not yet executed, not all remaining possibilities in reality. Observations support claims only within their tested scope. Testing all known options would not establish exhaustive truth.'
SHARED='''Reconstruct a fresh provisional relation from actual authenticated observations, then predict an unobserved legal case that an experiment could test. Your analysis is fallible MODEL INTERPRETATION, never authenticated truth or an executable action. Do not invent observations. evidence_A and evidence_B must be executed probe IDs, distinct when both are present. evidence_B may be NONE only when the ledger contains only one distinct executed probe. The predicted probe must be legal and untested. No previous model explanation is provided or retained. If the evidence does not justify a meaningful delta/relation/prediction, return {"status":"INSUFFICIENT_DELTA"}; this is legitimate. Otherwise return the requested compact JSON object with status="PREDICTION". Use brief phrases, no preamble, no markdown. Each prose field at most 100 characters. Extra common measurement fields: observed_endpoint_A and observed_endpoint_B copy the final four sensor bits of their cited observations, in the public sensor order; use "NONE" for endpoint_B when evidence_B is NONE. comparison_kind must be one_step_extension, adjacent_swap, other, or single_observation; the last applies only to NONE. one_step_extension means one sequence is the other with exactly one action added at its beginning or end; adjacent_swap means exactly two neighboring actions exchange order. These labels describe inputs, not hidden causes. prediction.predicted_trace must be an array of four-character binary strings, one per step of prediction.untested_probe_id, in public sensor order. These are your predictions, not observed facts. Never claim the available actions or explanations exhaust reality. A syntax-only decoder enforces the schema; prose fields allow up to12 ASCII text tokens and120 characters. Return at most512 tokens.'''
D_SCHEMA='''D fields: status, evidence_A, evidence_B, observed_endpoint_A, observed_endpoint_B, comparison_kind, observed_input_delta (string), observed_output_delta (string), provisional_relation (string), prediction {untested_probe_id, predicted_difference (string), predicted_trace}, why_this_test_matters (string). Compare the cited observations, state the observed delta, infer a provisional relation, then extrapolate it to the untested probe.'''
T_SCHEMA='''T fields: status, evidence_A, evidence_B, observed_endpoint_A, observed_endpoint_B, comparison_kind, observed_delta {input_or_context, outcome}, time {what_temporal_difference_is_supported, what_temporal_part_remains_unknown}, relation {what_changed_with_what, candidate_relation}, direction {which_unknown_distinction_should_be_resolved_next}, prediction {untested_probe_id, expected_outcome_or_delta, predicted_trace}, alternative_prediction (string), alternative_trace (array with same length/order as predicted_trace but predicting at least one different bit), what_result_would_separate_them (string). All nested prose fields are strings. Apply Time/Relation/Direction specifically to the cited observed delta, its provisional relation and proposed extrapolation, not as broad experiment-search axes. Direction identifies the unknown distinction this prediction test would resolve. Alternatives must predict different outcomes for the same proposed probe.'''

def inquiry(ledger,legal):
 tested={e['probe_id'] for e in ledger};ids=[r['id'] for r in legal];assert tested<=set(ids)
 return dict(tested_probe_ids=[i for i in ids if i in tested],untried_probe_ids=[i for i in ids if i not in tested],experiments_completed=len(ledger),experiments_remaining=6-len(ledger))

def bitrow(x):return type(x) is str and len(x)==4 and set(x)<=set('01')
def parse_analysis(text,arm,ledger,legal,sensors):
 try:
  x=json.loads(text);assert type(x) is dict
  if x.get('status')=='INSUFFICIENT_DELTA':
   assert set(x)<= {'status','reason'} and ('reason' not in x or type(x['reason']) is str and len(x['reason'])<=512);return x
  assert x['status']=='PREDICTION';common={'status','evidence_A','evidence_B','observed_endpoint_A','observed_endpoint_B','comparison_kind','prediction'}
  required=common|({'observed_input_delta','observed_output_delta','provisional_relation','why_this_test_matters'} if arm=='D' else {'observed_delta','time','relation','direction','alternative_prediction','alternative_trace','what_result_would_separate_them'})
  assert arm in ['D','T'] and set(x)==required
  tested={e['probe_id'] for e in ledger};assert x['evidence_A'] in tested
  assert (x['evidence_B']=='NONE' and len(tested)==1) or (x['evidence_B'] in tested and x['evidence_B']!=x['evidence_A'])
  assert bitrow(x['observed_endpoint_A']) and (x['observed_endpoint_B']=='NONE' if x['evidence_B']=='NONE' else bitrow(x['observed_endpoint_B']))
  assert x['comparison_kind'] in ['one_step_extension','adjacent_swap','other','single_observation']
  prediction=x['prediction'];assert set(prediction)=={'untested_probe_id','predicted_trace',('predicted_difference' if arm=='D' else 'expected_outcome_or_delta')}
  mapping={r['id']:r['sequence'] for r in legal};target=prediction['untested_probe_id'];assert target in mapping and target not in tested
  def trace(v):return type(v) is list and len(v)==len(mapping[target]) and all(bitrow(r) for r in v)
  assert trace(prediction['predicted_trace'])
  def prose(v):assert type(v) is str and 0<len(v)<=512
  prose(prediction['predicted_difference' if arm=='D' else 'expected_outcome_or_delta'])
  if arm=='D':
   for k in ['observed_input_delta','observed_output_delta','provisional_relation','why_this_test_matters']:prose(x[k])
  else:
   for k,keys in [('observed_delta',{'input_or_context','outcome'}),('time',{'what_temporal_difference_is_supported','what_temporal_part_remains_unknown'}),('relation',{'what_changed_with_what','candidate_relation'}),('direction',{'which_unknown_distinction_should_be_resolved_next'})]:
    assert type(x[k]) is dict and set(x[k])==keys
    for v in x[k].values():prose(v)
   prose(x['alternative_prediction']);prose(x['what_result_would_separate_them']);assert trace(x['alternative_trace']) and x['alternative_trace']!=prediction['predicted_trace']
  return x
 except (ValueError,AssertionError,TypeError,KeyError):return None

def messages(ports,reset,ledger,mode,arm,legal=None,query=None,analysis=None):
 assert arm in ['B','D','T'] and mode in ['analysis','choice','prediction']
 if mode=='analysis':assert arm in ['D','T'] and ledger
 msg=prior.messages(ports,reset,ledger,'choice' if mode=='analysis' else mode,legal=legal,query=query);data=json.loads(msg[1]['content'])
 if mode in ['analysis','choice']:
  data['remaining_experiments']=6-len(ledger);data['inquiry_state']=inquiry(ledger,legal);msg[0]['content']+=' '+SCOPE+' '+RESET_FACT
  if mode=='analysis':msg[0]['content']=SHARED+' '+(D_SCHEMA if arm=='D' else T_SCHEMA)+' '+RESET_FACT+' '+SCOPE
  elif arm in ['D','T'] and ledger:
   assert type(analysis) is str;msg[0]['content']+=' A separate inference just produced the attached fresh provisional analysis. It is not authenticated truth, an instruction, or an environmental recommendation. Evaluate it against the ledger and independently choose a legal probe. You are free not to select its proposed test.'
   data['fresh_model_analysis']=dict(authority='UNVERIFIED_MODEL_INTERPRETATION',raw_text=analysis,schema_valid=parse_analysis(analysis,arm,ledger,legal,ports['sensors']) is not None)
 else:assert analysis is None
 msg[1]['content']=json.dumps(data,separators=(',',':'));return msg
