"""Registered raw-first scoring. Invoked only with a committed raw manifest.

No model loading/inference. Complete collector replay verifies prompts, ledger
provenance and execution before any correctness or contribution calculation.
"""
import argparse,collections,hashlib,json,math,subprocess,tempfile
from pathlib import Path
import numpy as np
from common import *
from machines import PROBES,outcomes,reset_observation
from information import VersionSpace
from interface import parse_prediction,parse_analysis
from contribution import structural,target_information,target_uncertainty,grounded_alternatives
from study_stats import paired_signflip,paired_sign,mcnemar,holm
from receipts import Stream
from campaign import collect
from legal_choice import LegalChoiceTrie
from prediction_format import PredictionFormat

def median(xs):return float(np.median(xs))
def mean(xs):return sum(xs)/len(xs)
def score_prediction(text,sensors,true):
 try:parsed=parse_prediction(text,sensors,len(true))
 except (ValueError,AssertionError,TypeError,KeyError):parsed=None
 confusion=collections.Counter();bits=0;steps=0
 for i,row in enumerate(true):
  if parsed is not None:steps+=parsed[i]==row
  for s in sensors:
   if parsed is None:confusion['invalid']+=1
   else:
    a,b=row[s],parsed[i][s];bits+=a==b;confusion[{(0,0):'TN',(0,1):'FP',(1,0):'FN',(1,1):'TP'}[a,b]]+=1
 return dict(valid=parsed is not None,exact=parsed==true,correct_steps=steps,steps=len(true),correct_bits=bits,bits=len(true)*len(sensors),confusion=dict(confusion)),parsed

def prediction_summary(rows):
 totals={k:sum(r[k] for r in rows) for k in ['valid','exact','correct_steps','steps','correct_bits','bits']}
 totals.update(endpoints=len(rows),exact_accuracy=totals['exact']/len(rows),step_accuracy=totals['correct_steps']/totals['steps'],bit_accuracy=totals['correct_bits']/totals['bits'])
 confusion=collections.Counter()
 for r in rows:confusion.update(r['confusion'])
 totals['confusion']=dict(confusion);return totals

def audit(raw_commit):
 raw=json.loads(subprocess.check_output(['git','show',raw_commit+':research/horus-triangulation-learning-v0/raw-freeze.json'],cwd=ROOT))
 assert raw['status']=='RAW_COMPLETE_UNSCORED'
 private=ASSETS/'private';path=private/'campaign-signed.jsonl';assert filehash(path)==raw['private_raw_sha256']
 assert filehash(private/'worlds.jsonl')==raw['private_worlds_sha256']
 class ReadOnlyStream(Stream):
  def append(self,*args):raise AssertionError('Replay attempted to append missing raw record')
 stream=ReadOnlyStream(path,(private/'authority.key').read_bytes());stream.verify()
 worlds=[json.loads(x) for x in (private/'worlds.jsonl').read_text().splitlines()]
 auth=dict(study='Horus Triangulation Learning v0',method_freeze_sha=raw['method_freeze_sha'],world_freeze_sha=raw['world_freeze_sha'],adapter_sha256=ADAPTER_SHA,operation='Frozen inference-only discovery, sealed prediction and control; no training')
 class NoInference:
  def call(self,*args):raise AssertionError('Replay attempted inference')
 visited=collect(worlds,stream,NoInference(),auth,progress=False)
 assert filehash(path)==raw['private_raw_sha256']
 records={(e['kind'],e['record']['id']):e['record'] for e in stream.records};assert len(records)==len(stream.records)
 from transformers import AutoTokenizer
 tok=AutoTokenizer.from_pretrained('/mnt/d/horus-research-assets/qwen3-14b-qlora-v0/231c69a380487f6c0e52d02dcf0d5456d1918201',local_files_only=True)
 requests=[r for (kind,_),r in records.items() if kind=='MODEL_REQUEST'];assert len(requests)==9600
 attempts_by_id=collections.defaultdict(list)
 for (kind,_),r in records.items():
  if kind=='MODEL_ATTEMPT':attempts_by_id[r['logical_id']].append(r)
 response_count=0;choices=0;predictions=0;interrupted=0
 for r in requests:
  request=r['request'];ident=r['id'];response=records['MODEL_RESPONSE',ident];result=response['result'];response_count+=1
  assert request['id']==ident and result['id']==ident and result['mode']==request['mode']
  rendered=tok.apply_chat_template(request['messages'],tokenize=False,add_generation_prompt=True,enable_thinking=False)
  assert hashlib.sha256(rendered.encode()).hexdigest()==result['prompt_sha256']
  assert len(tok.encode(rendered,add_special_tokens=False))==result['prompt_tokens']
  assert tok.decode(result['generated_token_ids'],skip_special_tokens=True)==result['text']
  assert result['semantic_messages_sha256']==sha(request['messages'])
  attempts=sorted(attempts_by_id[ident],key=lambda x:x['attempt'])
  assert 1<=len(attempts)<=3 and [x['attempt'] for x in attempts]==list(range(1,len(attempts)+1))
  assert response['attempt']==len(attempts)
  for attempt in attempts:
   assert attempt['request_sha256']==sha(request)
   visited.add(('MODEL_ATTEMPT',attempt['id']))
   if attempt['attempt']<response['attempt']:
    interruption=records['TECHNICAL_INTERRUPTION',attempt['id']]
    assert interruption==dict(id=attempt['id'],logical_id=ident,attempt=attempt['attempt'],reason='No durable complete response. No experiment was executed from this attempt.')
    visited.add(('TECHNICAL_INTERRUPTION',attempt['id']));interrupted+=1
  if request['mode']=='choice':
   grammar=LegalChoiceTrie(tok,request['legal_ids']);ident_chosen=grammar.identify(result['generated_token_ids'])
   assert ident_chosen==result['probe_id'] and result['finite_choice']['legal_ids']==request['legal_ids']
   assert result['finite_choice']['illegal_support_zero'];choices+=1
  elif request['mode']=='prediction':
   grammar=PredictionFormat(tok,**request['prediction_shape']);assert grammar.validate(result['generated_token_ids'])==result['text'];predictions+=1
 assert visited==set(records),'Unexpected/unaccounted authenticated records'
 assert response_count==9600 and choices==3840 and predictions==3840
 assert sum(k=='MODEL_RESPONSE' for k,_ in records)==9600
 return raw,worlds,records,dict(receipt_authentication=True,byte_identical_durable_execution_replay=True,full_ledger_and_prompt_reconstruction=True,rendered_template_and_generated_tokens=True,legal_ID_support=True,prediction_shape_language=True,no_reserved_probe_execution=True,target_before_control_discovery=True,oracle_boundary=True,complete_population=True,new_inference_calls=0,technical_interrupted_attempts=interrupted,model_responses=9600)

def summarize_information(world_rows):
 curves={}
 for t in [0,1,2,3,4,6,8,12]:
  rows=[r['curves'][t] for r in world_rows]
  curves[t]=dict(median_H=median([r['H'] for r in rows]),median_log2_H=median([r['bits'] for r in rows]),uniquely_identified=sum(r['H']==1 for r in rows),fraction_unique=sum(r['H']==1 for r in rows)/len(rows),mean_cumulative_information=mean([r['cumulative_bits'] for r in rows]),median_cumulative_information=median([r['cumulative_bits'] for r in rows]),mean_useful_controlled_contrasts=mean([r['useful_contrasts'] for r in rows]),mean_zero_information_probes=mean([r['zero_information'] for r in rows]),mean_exact_repeats=mean([r['repeats'] for r in rows]))
 decisions=[d for r in world_rows for d in r['decisions']]
 counts={k:sum(bool(d[k]) for d in decisions) for k in ['repeat','zero_information','controlled_contrast','useful_controlled_contrast','time_contrast','relation_contrast']}
 return dict(worlds=len(world_rows),curves=curves,mean_final_H=mean([r['final_H'] for r in world_rows]),median_final_H=median([r['final_H'] for r in world_rows]),mean_cumulative_bits=mean([r['cumulative_bits'] for r in world_rows]),median_cumulative_bits=median([r['cumulative_bits'] for r in world_rows]),mean_uncertainty_area=mean([r['uncertainty_area'] for r in world_rows]),mean_information_per_experiment=mean([r['cumulative_bits']/12 for r in world_rows]),mean_information_per_actuator_action=mean([r['cumulative_bits']/r['actuator_actions'] for r in world_rows]),mean_actuator_actions=mean([r['actuator_actions'] for r in world_rows]),mean_unique_sequences=mean([r['unique_sequences'] for r in world_rows]),mean_regret=mean([d['regret'] for d in decisions]),median_regret=median([d['regret'] for d in decisions]),mean_rank=mean([d['midrank'] for d in decisions]),top_quartile_fraction=mean([d['top_quartile'] for d in decisions]),mean_useful_contrasts_per_world=counts['useful_controlled_contrast']/len(world_rows),useful_contrast_fraction=counts['useful_controlled_contrast']/len(decisions),positive_information_repeats=sum(d['repeat'] and not d['zero_information'] for d in decisions),counts=counts,mean_temporal_constraints_added=mean([sum(d['temporal_constraints_added'] for d in r['decisions']) for r in world_rows]),mean_relational_distinctions_added=mean([sum(d['relational_distinctions_added'] for d in r['decisions']) for r in world_rows]),probe_length_counts=dict(collections.Counter(d['probe_length'] for d in decisions)),abstract_sequence_counts=dict(collections.Counter(','.join(map(str,d['probe'])) for d in decisions)))

def score(raw_commit,output):
 raw,worlds,records,audits=audit(raw_commit);output.mkdir(parents=True,exist_ok=True)
 details_path=output/'contribution-details.private.jsonl';arm_names=['P','A','T']
 information={cohort:{a:[] for a in arm_names} for cohort in ['primary','control']}
 predictions={kind:{a:[] for a in arm_names} for kind in ['short','long']};controls={a:[] for a in arm_names}
 baselines={kind:{a:collections.Counter() for a in arm_names} for kind in ['short','long']};analysis_valid={c:[] for c in ['primary','control']}
 directions={a:[] for a in arm_names};falsification={c:collections.Counter() for c in ['primary','control']}
 costs={a:collections.Counter() for a in arm_names};errors={k:{a:collections.Counter() for a in arm_names} for k in ['short','long']}
 for (kind,ident),r in records.items():
  if kind=='MODEL_RESPONSE':
   arm=ident.split(':')[1];z=r['result'];costs[arm]['model_calls']+=1;costs[arm]['prompt_tokens']+=z['prompt_tokens'];costs[arm]['generated_tokens']+=z['generation_token_count'];costs[arm]['inference_seconds']+=z['seconds']
 with details_path.open('w') as details:
  for w in worlds:
   cohort=w['cohort'];reset=reset_observation(w['root_ids']);sensors=w['sensors']
   legal_map={r['id']:tuple(r['sequence']) for r in w['legal_probes']};allowed=tuple(p for p in PROBES if p in set(legal_map.values()))
   target=w.get('target');queries=tuple(tuple(q) for q in w['reserved']+w['long_queries'])
   for arm in arm_names:
    vs=VersionSpace(reset);initial_bits=vs.bits;seen=set();prior_probes=[];prior_traces=[];ledger=[];decisions=[];areas=[];actions=0;useful=zero=repeats=0
    curves={0:dict(H=vs.count,bits=vs.bits,cumulative_bits=0.,useful_contrasts=0,zero_information=0,repeats=0)}
    for step in range(1,13):
     base=f"{w['id']}:{arm}:discovery:{step}";r=records['EXECUTED_PROBE',base];probe=legal_map[r['probe_id']]
     trace=[[row[s] for s in sensors] for row in r['complete_observed_trace']]
     analysis=None
     if arm=='T':
      analysis=records['MODEL_RESPONSE',base+':analysis']['result']['text'];analysis_valid[cohort].append(records['ANALYSIS_SCHEMA',base+':analysis-schema']['valid'])
     pre_count=vs.count;pre_bits=vs.bits;claims_before=vs.claim_counts();value=vs.decision(probe,allowed)
     grounded=grounded_alternatives(analysis,vs,probe,sensors,trace) if analysis is not None else {}
     for k,v in grounded.items():falsification[cohort][k]+=v
     if target is not None:
      goal_before=target_uncertainty(vs,w['control_candidates'],target);goal_gain=target_information(vs,probe,w['control_candidates'],target)
     else:query_before=vs.query_uncertainty(queries)
     vs.observe(probe,trace);realized=pre_bits-vs.bits;claims_after=vs.claim_counts()
     contrast=structural(probe,prior_probes,trace,prior_traces,realized)
     repeat=probe in seen;seen.add(probe);prior_probes.append(probe);prior_traces.append(trace);actions+=len(probe)
     useful+=contrast['useful_controlled_contrast'];zero+=abs(realized)<=1e-12;repeats+=repeat
     row=dict(world_id=w['id'],cohort=cohort,arm=arm,step=step,probe_id=r['probe_id'],probe=list(probe),probe_length=len(probe),pre_H=pre_count,post_H=vs.count,eliminated=pre_count-vs.count,realized_bits=realized,repeat=repeat,zero_information=abs(realized)<=1e-12,temporal_constraints_added=claims_after['temporal_onset_claims_identified']-claims_before['temporal_onset_claims_identified'],relational_distinctions_added=claims_after['context_and_order_claims_identified']-claims_before['context_and_order_claims_identified'],**contrast,**value,**grounded)
     if target is not None:
      goal_after=target_uncertainty(vs,w['control_candidates'],target)
      row.update(expected_target_information=goal_gain,target_uncertainty_change=goal_before['mean_target_entropy']-goal_after['mean_target_entropy'],new_target_propositions_resolved=goal_after['resolved_target_propositions']-goal_before['resolved_target_propositions'])
      directions[arm].append({k:row[k] for k in ['world_id','step','expected_target_information','target_uncertainty_change','new_target_propositions_resolved']})
     else:row['sealed_query_uncertainty_change']=query_before-vs.query_uncertainty(queries)
     details.write(canon(row)+'\n');decisions.append({k:v for k,v in row.items() if k not in ['all_probe_values','partition_counts_by_sensor','contrasts']})
     ledger.append(dict(experiment=step,probe_id=r['probe_id'],probe=r['selected_probe'],observations=r['complete_observed_trace']))
     areas.append(vs.bits/initial_bits)
     if step in [1,2,3,4,6,8,12]:curves[step]=dict(H=vs.count,bits=vs.bits,cumulative_bits=initial_bits-vs.bits,useful_contrasts=useful,zero_information=zero,repeats=repeats)
    information[cohort][arm].append(dict(world_id=w['id'],final_H=vs.count,cumulative_bits=initial_bits-vs.bits,uncertainty_area=mean(areas),actuator_actions=actions,unique_sequences=len(seen),curves=curves,decisions=decisions))
    if cohort=='primary':
     marginal=[]
     for j in range(3):
      observations=[e['observations'][j] for e in ledger if len(e['observations'])>j]
      marginal.append({s:int(2*sum(o[s] for o in observations)>len(observations)) if observations else reset[i] for i,s in enumerate(sensors)})
     reset_dict=dict(zip(sensors,reset));last=ledger[-1]['observations'][-1];last_trace=ledger[-1]['observations']
     for kind,qset in [('short',w['reserved']),('long',w['long_queries'])]:
      for q,probe in enumerate(qset):
       result=records['MODEL_RESPONSE',f"{w['id']}:{arm}:{kind}:{q}"]['result']
       true=[dict(zip(sensors,row)) for row in outcomes(w['root_ids'],probe)]
       scored,parsed=score_prediction(result['text'],sensors,true);predictions[kind][arm].append(dict(world_id=w['id'],query=q,length=len(probe),**scored))
       candidates=dict(reset=[reset_dict]*len(probe),last_observation=[last]*len(probe),marginal=[marginal[min(j,2)] for j in range(len(probe))],repeat_last_probe=[last_trace[j%len(last_trace)] for j in range(len(probe))])
       for key,pred in candidates.items():baselines[kind][arm][key]+=pred==true
       if not scored['exact']:
        errors[kind][arm]['incorrect_full_trace']+=1
        errors[kind][arm]['invalid_schema']+=parsed is None
        errors[kind][arm]['some_steps_correct']+=0<scored['correct_steps']<len(probe)
        errors[kind][arm]['no_steps_correct']+=scored['correct_steps']==0
        for key,pred in candidates.items():errors[kind][arm]['equals_'+key]+=parsed==pred
    else:
     candidate_scores=[]
     for q,probe in enumerate(w['control_candidates']):
      result=records['MODEL_RESPONSE',f"{w['id']}:{arm}:control-prediction:{q}"]['result']
      true=[dict(zip(sensors,row)) for row in outcomes(w['root_ids'],probe)];candidate_scores.append(score_prediction(result['text'],sensors,true)[0])
     executions=[records['CONTROL_EXECUTION',f"{w['id']}:{arm}:control-execution:{j}"] for j in range(1,5) if ('CONTROL_EXECUTION',f"{w['id']}:{arm}:control-execution:{j}") in records]
     success=executions[-1]['complete_observed_trace'][-1]==dict(zip(sensors,target))
     controls[arm].append(dict(world_id=w['id'],success=success,probes=len(executions),actuator_actions=3*len(executions),failed_probes=len(executions)-int(success),all_prediction_errors=sum(not x['exact'] for x in candidate_scores),selected_prediction_errors=sum(not candidate_scores[e['candidate_index']]['exact'] for e in executions),all_prediction_schemas_valid=all(x['valid'] for x in candidate_scores)))
 summaries={k:{a:prediction_summary(v) for a,v in arms.items()} for k,arms in predictions.items()}
 info={c:{a:summarize_information(v) for a,v in arms.items()} for c,arms in information.items()}
 baseline_results={k:{a:{name:dict(exact=count,endpoints=len(predictions[k][a]),accuracy=count/len(predictions[k][a])) for name,count in vals.items()} for a,vals in arms.items()} for k,arms in baselines.items()}
 comparisons={}
 for treatment,base in [('A','P'),('T','P'),('T','A')]:
  name=treatment+'-'+base;comp={}
  for kind in ['short','long']:
   totals={a:collections.Counter() for a in [treatment,base]}
   for a in totals:
    for r in predictions[kind][a]:totals[a][r['world_id']]+=r['exact']
   ids=sorted(totals[base]);differences=[int(totals[treatment][i]-totals[base][i]) for i in ids]
   comp[kind]=dict(exact_gain=summaries[kind][treatment]['exact']-summaries[kind][base]['exact'],accuracy_gain=summaries[kind][treatment]['exact_accuracy']-summaries[kind][base]['exact_accuracy'],world_paired_signflip=paired_signflip(differences),descriptive_endpoint_mcnemar=mcnemar([r['exact'] for r in predictions[kind][base]],[r['exact'] for r in predictions[kind][treatment]]))
  ds=[t['cumulative_bits']-b['cumulative_bits'] for b,t in zip(information['primary'][base],information['primary'][treatment])]
  comp['information']=dict(median_paired_bits=median(ds),paired_sign=paired_sign(ds),smaller_H_worlds=sum(t['final_H']<b['final_H'] for b,t in zip(information['primary'][base],information['primary'][treatment])),uncertainty_area_ratio=info['primary'][treatment]['mean_uncertainty_area']/info['primary'][base]['mean_uncertainty_area'] if info['primary'][base]['mean_uncertainty_area'] else None,useful_contrasts_mean_advantage=info['primary'][treatment]['mean_useful_contrasts_per_world']-info['primary'][base]['mean_useful_contrasts_per_world'])
  cp=mcnemar([r['success'] for r in controls[base]],[r['success'] for r in controls[treatment]])
  common=[(b,t) for b,t in zip(controls[base],controls[treatment]) if b['success'] and t['success']]
  comp['control']=dict(success_gain=sum(r['success'] for r in controls[treatment])-sum(r['success'] for r in controls[base]),paired_mcnemar=cp,common_success_worlds=len(common),mean_probe_difference_common_success=mean([t['probes']-b['probes'] for b,t in common]) if common else None)
  comparisons[name]=comp
 for kind in ['short','long']:
  adjusted=holm({name:comparisons[name][kind]['world_paired_signflip']['p'] for name in ['T-P','T-A']})
  for name,value in adjusted.items():comparisons[name][kind]['holm_p']=value
 adjusted=holm({name:comparisons[name]['control']['paired_mcnemar']['p'] for name in ['T-P','T-A']})
 for name,value in adjusted.items():comparisons[name]['control']['holm_p']=value
 baseline_pass={k:all(x['accuracy']<=.30 for a in baseline_results[k].values() for x in a.values()) for k in ['short','long']}
 short_schema=all(x['valid']==x['endpoints'] for x in summaries['short'].values());long_schema=all(x['valid']==x['endpoints'] for x in summaries['long'].values())
 def evidence_conditions(name,holm_test=True):
  c=comparisons[name];v=c['information']
  return dict(short_gain_at_least_48=c['short']['exact_gain']>=48,prediction_p_below_001=(c['short']['holm_p'] if holm_test else c['short']['world_paired_signflip']['p'])<.01,median_paired_bits_at_least_1=v['median_paired_bits']>=1-1e-12,smaller_H_at_least_78=v['smaller_H_worlds']>=78,uncertainty_area_at_most_90pct=v['uncertainty_area_ratio'] is not None and v['uncertainty_area_ratio']<=.90)
 primary={name:evidence_conditions(name) for name in ['T-P','T-A']}
 for name in primary:primary[name]['paired_information_sign_p_below_001']=comparisons[name]['information']['paired_sign']['p']<.01
 common_conditions=dict(useful_contrast_advantage_at_least_1=comparisons['T-A']['information']['useful_contrasts_mean_advantage']>=1-1e-12,T_useful_contrast_fraction_at_least_quarter=info['primary']['T']['useful_contrast_fraction']>=.25,all_primary_T_analyses_valid=all(analysis_valid['primary']),all_short_prediction_schemas_valid=short_schema,legal_choice_and_integrity_pass=True,baselines_pass=baseline_pass['short'] and baseline_pass['long'])
 primary_support=all(all(x.values()) for x in primary.values()) and all(common_conditions.values())
 active_conditions=evidence_conditions('A-P',False)|dict(all_short_prediction_schemas_valid=all(summaries['short'][a]['valid']==600 for a in ['P','A']),baseline_integrity_pass=baseline_pass['short'] and baseline_pass['long'])
 over_conditions=primary['T-A']|common_conditions
 long_conditions={name:dict(exact_gain_at_least_29=comparisons[name]['long']['exact_gain']>=29,paired_holm_p_below_001=comparisons[name]['long']['holm_p']<.01) for name in ['T-P','T-A']}
 long_common=dict(T_exact_at_least_half=summaries['long']['T']['exact']>=180,all_long_schemas_valid=long_schema,baselines_integrity_pass=baseline_pass['long'])
 control_conditions={}
 for name in ['T-P','T-A']:
  c=comparisons[name]['control'];control_conditions[name]=dict(success_gain_at_least_6=c['success_gain']>=6,paired_holm_p_below_005=c['holm_p']<.05,common_success_action_nonregression=c['mean_probe_difference_common_success'] is not None and c['mean_probe_difference_common_success']<=.5)
 control_schema=all(analysis_valid['control']) and all(r['all_prediction_schemas_valid'] for rows in controls.values() for r in rows)
 control_summary={}
 for arm,rows in controls.items():
  successes=[r for r in rows if r['success']]
  control_summary[arm]=dict(successes=len(successes),worlds=40,mean_probes_successful=mean([r['probes'] for r in successes]) if successes else None,mean_actuator_actions_successful=mean([r['actuator_actions'] for r in successes]) if successes else None,total_probes=sum(r['probes'] for r in rows),failed_probes=sum(r['failed_probes'] for r in rows),all_candidate_prediction_errors=sum(r['all_prediction_errors'] for r in rows),selected_prediction_errors=sum(r['selected_prediction_errors'] for r in rows),mean_target_information_per_probe=mean([r['expected_target_information'] for r in directions[arm]]),target_zero_information_probe_fraction=mean([r['expected_target_information']<=1e-12 for r in directions[arm]]),mean_realized_target_uncertainty_change=mean([r['target_uncertainty_change'] for r in directions[arm]]),mean_target_propositions_resolved_per_world=sum(r['new_target_propositions_resolved'] for r in directions[arm])/40)
 gates=dict(TRIANGULATION_EVIDENCE_ACQUISITION_SUPPORTED=dict(supported=primary_support,comparisons=primary,common=common_conditions),ACTIVE_EVIDENCE_ACQUISITION_SUPPORTED=dict(supported=all(active_conditions.values()),conditions=active_conditions),TRIANGULATION_OVER_ACTIVE_SUPPORTED=dict(supported=all(over_conditions.values()),conditions=over_conditions),SHORT_TO_LONG_CAUSAL_EXTRAPOLATION_SUPPORTED=dict(supported=all(all(x.values()) for x in long_conditions.values()) and all(long_common.values()),comparisons=long_conditions,common=long_common),TRIANGULATION_CONTROL_BENEFIT_SUPPORTED=dict(supported=all(all(x.values()) for x in control_conditions.values()) and control_schema,comparisons=control_conditions,all_control_schemas_valid=control_schema))
 result=dict(raw_freeze_commit=raw_commit,private_raw_sha256=raw['private_raw_sha256'],contribution_details_sha256=filehash(details_path),prediction=summaries,information=info,comparisons=comparisons,baselines=baseline_results,control=control_summary,grounded_falsification={k:dict(v) for k,v in falsification.items()},analysis_schema={k:dict(valid=sum(v),total=len(v)) for k,v in analysis_valid.items()},costs={k:dict(v) for k,v in costs.items()},errors={k:{a:dict(v) for a,v in arms.items()} for k,arms in errors.items()},gates=gates,audits=audits,classification='TRIANGULATION_EVIDENCE_ACQUISITION_SUPPORTED' if primary_support else 'TRIANGULATION_EVIDENCE_ACQUISITION_NOT_ESTABLISHED')
 save(output/'results.json',result);save(output/'per-world-results.private.json',dict(information=information,predictions=predictions,controls=controls,direction=directions))
 print(canon(dict(status='SCORED',classification=result['classification'],gates={k:v['supported'] for k,v in gates.items()},short_exact={a:summaries['short'][a]['exact'] for a in arm_names},long_exact={a:summaries['long'][a]['exact'] for a in arm_names})),flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--raw-commit',required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();score(args.raw_commit,args.output)
