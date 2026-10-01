"""Frozen strict parsing, exact paired gates, and independently replayable scores."""
import json,math
from collections import Counter
from planner import MATERIAL_ACTION_REGRESSION

def parse(text,sensors):
 def unique(pairs):
  out={}
  for k,v in pairs:
   if k in out:raise ValueError('duplicate key')
   out[k]=v
  return out
 try:
  o=json.loads(text,object_pairs_hook=unique)
  if not isinstance(o,dict) or set(o)!={'next_observation'}:return None
  v=o['next_observation']
  if not isinstance(v,dict) or set(v)!=set(sensors) or any(type(x) is not int or x not in (0,1) for x in v.values()):return None
  return v
 except (ValueError,TypeError):return None

def endpoint(case,text,actual):
 pred=parse(text,case['visible']['sensors']);bits=[pred is not None and pred[s]==actual[s] for s in case['visible']['sensors']]
 return dict(id=case['id'],prediction=pred,actual=actual,schema=pred is not None,exact=all(bits),bits_correct=sum(bits),bits_total=len(bits),family=case['family'],causal_depth=case['causal_depth'],delay_length=case['delay_length'],hidden_components=case['hidden_components'])
def paired(a,b,metric='exact'):
 assert len(a)==len(b) and [x['id'] for x in a]==[x['id'] for x in b]
 old=sum(bool(x[metric]) for x in a);new=sum(bool(x[metric]) for x in b);old_only=sum(bool(x[metric]) and not y[metric] for x,y in zip(a,b));new_only=sum(not x[metric] and bool(y[metric]) for x,y in zip(a,b));d=old_only+new_only;p=min(1.,2*sum(math.comb(d,k) for k in range(min(old_only,new_only)+1))/2**d) if d else 1.
 return dict(n=len(a),incumbent_correct=old,candidate_correct=new,gain_pp=100*(new-old)/len(a),incumbent_accuracy=old/len(a),candidate_accuracy=new/len(a),both_correct=old-old_only,incumbent_only=old_only,candidate_only=new_only,both_wrong=len(a)-old-new_only,mcnemar_exact_two_sided_p=p)
def compare(a,b):
 out=dict(exact=paired(a,b),schema=paired(a,b,'schema'),incumbent_bit_accuracy=sum(x['bits_correct'] for x in a)/sum(x['bits_total'] for x in a),candidate_bit_accuracy=sum(x['bits_correct'] for x in b)/sum(x['bits_total'] for x in b),strata={})
 for field in ['family','causal_depth','delay_length','hidden_components']:
  out['strata'][field]={}
  for value in sorted({x[field] for x in a},key=str):
   aa=[x for x in a if x[field]==value];bb=[x for x in b if x[field]==value];out['strata'][field][str(value)]=paired(aa,bb)
 return out

def no_regression(comp):return all(s['gain_pp']>=-3 for groups in comp['strata'].values() for s in groups.values() if s['n']>=30)
def cycle1_gate(comp,temporal,artifact,audit):
 checks=dict(exact_gain_at_least_10pp=comp['exact']['gain_pp']>=10,paired_p_less_than_001=comp['exact']['mcnemar_exact_two_sided_p']<.01,at_least_three_families_improve=sum(x['gain_pp']>0 for x in comp['strata']['family'].values())>=3,no_major_stratum_regression=no_regression(comp),schema_at_least_99percent=comp['schema']['candidate_accuracy']>=.99,adapter_changed=artifact['adapter_changed'],base_unchanged=artifact['base_unchanged'],leakage_and_oracle_boundary=audit['status']=='PASS',temporal_retention=temporal['joint_correct']>=530,temporal_schema_unchanged=temporal['schema_valid']==540)
 passed=all(checks.values());return dict(checks=checks,classification='CAUSAL_WORLD_MODEL_LEARNING_SUPPORTED' if passed else 'CAUSAL_WORLD_MODEL_LEARNING_NOT_ESTABLISHED',cycle2_authorized=passed)
def cycle2_gate(comp,retention,temporal,artifact,audit):
 checks=dict(exact_gain_at_least_8pp=comp['exact']['gain_pp']>=8,paired_p_less_than_005=comp['exact']['mcnemar_exact_two_sided_p']<.05,at_least_two_families_gain_5pp=sum(x['gain_pp']>=5 for x in comp['strata']['family'].values())>=2,no_major_new_or_old_stratum_regression=no_regression(comp) and no_regression(retention),cycle1_retention_loss_at_most_3pp=retention['exact']['gain_pp']>=-3,temporal_retention=temporal['joint_correct']>=530,temporal_schema_unchanged=temporal['schema_valid']==540,schema_at_least_99percent=min(comp['schema']['candidate_accuracy'],retention['schema']['candidate_accuracy'])>=.99,adapter_changed=artifact['adapter_changed'],base_unchanged=artifact['base_unchanged'],leakage_and_oracle_boundary=audit['status']=='PASS')
 result='TWO_CYCLE_CAUSAL_PARAMETER_LEARNING_SUPPORTED' if all(checks.values()) else 'SECOND_CAUSAL_LEARNING_CYCLE_NOT_ESTABLISHED_DUE_TO_NO_MEASURED_HEADROOM' if comp['exact']['incumbent_correct']==comp['exact']['n'] else 'SECOND_CAUSAL_LEARNING_CYCLE_NOT_ESTABLISHED'
 return dict(checks=checks,classification=result)
def control_compare(a,b):
 result=paired(a,b,'success');common=[(x,y) for x,y in zip(a,b) if x['success'] and y['success']]
 old_mean=sum(x['actions'] for x,_ in common)/len(common) if common else None;new_mean=sum(y['actions'] for _,y in common)/len(common) if common else None
 result.update(common_successes=len(common),common_success_incumbent_mean_actions=old_mean,common_success_candidate_mean_actions=new_mean,incumbent_mean_actions_to_success=sum(x['actions'] for x in a if x['success'])/sum(x['success'] for x in a) if any(x['success'] for x in a) else None,candidate_mean_actions_to_success=sum(x['actions'] for x in b if x['success'])/sum(x['success'] for x in b) if any(x['success'] for x in b) else None,incumbent_cumulative_prediction_errors=sum(x['prediction_errors'] for x in a),candidate_cumulative_prediction_errors=sum(x['prediction_errors'] for x in b))
 checks=dict(at_least_six_more_targets=result['candidate_correct']-result['incumbent_correct']>=6,paired_p_less_than_005=result['mcnemar_exact_two_sided_p']<.05,common_success_action_count_no_material_regression=bool(common) and new_mean<=old_mean+MATERIAL_ACTION_REGRESSION)
 result.update(checks=checks,classification='CAUSAL_CONTROL_BENEFIT_SUPPORTED' if all(checks.values()) else 'CAUSAL_CONTROL_BENEFIT_NOT_ESTABLISHED');return result
