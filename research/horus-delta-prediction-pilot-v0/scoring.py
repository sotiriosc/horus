"""Raw-first frozen pilot scoring and exact zero-inference reconstruction."""
import argparse,collections,hashlib,json,math,subprocess
from pathlib import Path
import numpy as np
from common import *
from machines import PROBES,outcomes,reset_observation
from information import VersionSpace
from interface import parse_prediction
from contribution import structural
from receipts import Stream
from campaign import collect
from legal_choice import LegalChoiceTrie
from prediction_format import PredictionFormat
from analysis_format import AnalysisFormat
from gates import decision
from prediction_audit import measure,aggregate

def mean(xs):return sum(xs)/len(xs)
def median(xs):return float(np.median(xs))
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
 raw=json.loads(subprocess.check_output(['git','show',raw_commit+':research/horus-delta-prediction-pilot-v0/raw-freeze.json'],cwd=ROOT))
 assert raw['status']=='RAW_COMPLETE_UNSCORED'
 private=ASSETS/'private';path=private/'campaign-signed.jsonl';assert filehash(path)==raw['private_raw_sha256']
 assert filehash(private/'worlds.jsonl')==raw['private_worlds_sha256']
 class ReadOnlyStream(Stream):
  def append(self,*args):raise AssertionError('Replay attempted to append missing raw record')
 stream=ReadOnlyStream(path,(private/'authority.key').read_bytes());stream.verify()
 worlds=[json.loads(x) for x in (private/'worlds.jsonl').read_text().splitlines()]
 auth=dict(study='Horus Delta Prediction Pilot v0',method_freeze_sha=raw['method_freeze_sha'],world_freeze_sha=raw['world_freeze_sha'],adapter_sha256=ADAPTER_SHA,operation='Frozen six-probe inference-only B/D/T delta-prediction pilot; no training')
 class NoInference:
  def call(self,*args):raise AssertionError('Replay attempted inference')
 visited=collect(worlds,stream,NoInference(),auth,progress=False)
 assert filehash(path)==raw['private_raw_sha256']
 records={(e['kind'],e['record']['id']):e['record'] for e in stream.records};assert len(records)==len(stream.records)
 from transformers import AutoTokenizer
 tok=AutoTokenizer.from_pretrained('/mnt/d/horus-research-assets/qwen3-14b-qlora-v0/231c69a380487f6c0e52d02dcf0d5456d1918201',local_files_only=True)
 requests=[r for (kind,_),r in records.items() if kind=='MODEL_REQUEST'];assert len(requests)==544
 attempts_by_id=collections.defaultdict(list)
 for (kind,_),r in records.items():
  if kind=='MODEL_ATTEMPT':attempts_by_id[r['logical_id']].append(r)
 response_count=0;choices=0;predictions=0;analyses=0;interrupted=0
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
  elif request['mode']=='analysis':
   grammar=AnalysisFormat(tok,**request['analysis_shape']);assert grammar.validate(result['generated_token_ids'])==result['text'];analyses+=1
  else:raise AssertionError('Unknown inference mode')
 assert visited==set(records),'Unexpected/unaccounted authenticated records'
 assert response_count==544 and choices==288 and predictions==96 and analyses==160
 assert sum(k=='MODEL_RESPONSE' for k,_ in records)==544
 return raw,worlds,records,dict(receipt_authentication=True,byte_identical_durable_execution_replay=True,full_ledger_and_prompt_reconstruction=True,rendered_template_and_generated_tokens=True,legal_ID_support=True,prediction_shape_language=True,no_reserved_probe_execution=True,evidence_analysis_and_prediction_receipts_reconstructed=True,oracle_boundary=True,complete_population=True,new_inference_calls=0,technical_interrupted_attempts=interrupted,model_responses=544)

def summarize(rows,preds):
 curves={}
 for step in [0,1,2,3,4,6]:
  cells=[r['curves'][step] for r in rows]
  curves[step]=dict(median_log2_H=median([r['bits'] for r in cells]),median_H=median([r['H'] for r in cells]),mean_cumulative_bits=mean([r['information'] for r in cells]),median_cumulative_bits=median([r['information'] for r in cells]),exact_repeats=sum(r['repeats'] for r in cells),zero_information=sum(r['zero_information'] for r in cells),useful_contrasts=sum(r['useful_contrasts'] for r in cells))
 ds=[d for r in rows for d in r['decisions']]
 return dict(worlds=len(rows),experiments=len(ds),exact_repeats=sum(r['repeats'] for r in rows),zero_information=sum(r['zero_information'] for r in rows),unique_probe_sequences=sum(r['unique_probes'] for r in rows),mean_unique_probes=mean([r['unique_probes'] for r in rows]),mean_information_bits=mean([r['information'] for r in rows]),median_information_bits=median([r['information'] for r in rows]),median_final_H=median([r['final_H'] for r in rows]),median_final_log2_H=median([r['final_bits'] for r in rows]),useful_controlled_contrasts=sum(r['useful_contrasts'] for r in rows),time_contrasts=sum(d['time_contrast'] for d in ds),relation_contrasts=sum(d['relation_contrast'] for d in ds),controlled_contrasts=sum(d['controlled_contrast'] for d in ds),temporal_constraints_added=sum(d['temporal_constraints_added'] for d in ds),relational_distinctions_added=sum(d['relational_distinctions_added'] for d in ds),mean_selected_rank=mean([d['midrank'] for d in ds]),median_selected_rank=median([d['midrank'] for d in ds]),mean_regret_bits=mean([d['regret'] for d in ds]),mean_information_per_probe=mean([r['information']/6 for r in rows]),mean_actuator_actions=mean([sum(d['probe_length'] for d in r['decisions']) for r in rows]),curves=curves,prediction=prediction_summary(preds),probe_length_counts=dict(collections.Counter(d['probe_length'] for d in ds)),abstract_sequence_counts=dict(collections.Counter(','.join(map(str,d['probe'])) for d in ds)))

def comparisons(rows,summaries):
 result={}
 for x,a in [('D','B'),('T','B'),('T','D')]:
  pairs=[]
  for target,base in zip(rows[x],rows[a]):
   assert target['world_id']==base['world_id']
   pairs.append(dict(world_id=target['world_id'],information_advantage_bits=target['information']-base['information'],repeat_difference=target['repeats']-base['repeats'],zero_information_difference=target['zero_information']-base['zero_information'],useful_contrast_difference=target['useful_contrasts']-base['useful_contrasts'],unique_probes_difference=target['unique_probes']-base['unique_probes'],short_exact_difference=target['short_exact']-base['short_exact'],short_correct_bits_difference=target['short_correct_bits']-base['short_correct_bits']))
  d=[p['information_advantage_bits'] for p in pairs];t,b=summaries[x],summaries[a]
  result[x+'-'+a]=dict(paired_worlds=pairs,information_wins=sum(v>1e-12 for v in d),information_ties=sum(abs(v)<=1e-12 for v in d),information_losses=sum(v< -1e-12 for v in d),median_paired_information_advantage_bits=median(d),mean_information_per_probe_advantage=mean(d)/6,repeat_reduction=b['exact_repeats']-t['exact_repeats'],repeat_ratio=t['exact_repeats']/b['exact_repeats'] if b['exact_repeats'] else None,zero_information_reduction=b['zero_information']-t['zero_information'],zero_information_ratio=t['zero_information']/b['zero_information'] if b['zero_information'] else None,useful_contrast_mean_advantage=(t['useful_controlled_contrasts']-b['useful_controlled_contrasts'])/len(pairs),short_exact_difference=t['prediction']['exact']-b['prediction']['exact'],short_bit_accuracy_difference=t['prediction']['bit_accuracy']-b['prediction']['bit_accuracy'])
 return result

def score(raw_commit,output):
 raw,worlds,records,audits=audit(raw_commit);output.mkdir(parents=True,exist_ok=True);arms=['B','D','T'];rows={a:[] for a in arms};predictions={a:[] for a in arms};costs={a:collections.Counter() for a in arms}
 details=output/'contribution-details.private.jsonl'
 with details.open('w') as f:
  for w in worlds:
   sensors=w['sensors'];reset=reset_observation(w['root_ids']);mapping={r['id']:tuple(r['sequence']) for r in w['legal_probes']};allowed=tuple(p for p in PROBES if p in set(mapping.values()))
   for arm in arms:
    vs=VersionSpace(reset);initial=vs.bits;seen=set();prior=[];traces=[];decisions=[];repeats=zero=useful=0
    curves={0:dict(H=vs.count,bits=vs.bits,information=0.,repeats=0,zero_information=0,useful_contrasts=0)}
    for step in range(1,7):
     base=f"{w['id']}:{arm}:discovery:{step}";e=records['EXECUTED_PROBE',base];probe=mapping[e['probe_id']];trace=[[o[s] for s in sensors] for o in e['complete_observed_trace']]
     before=vs.bits;before_count=vs.count;claims=vs.claim_counts();value=vs.decision(probe,allowed);vs.observe(probe,trace);after_claims=vs.claim_counts();gain=before-vs.bits
     contrast=structural(probe,prior,trace,traces,gain);repeat=probe in seen;seen.add(probe);prior.append(probe);traces.append(trace)
     assert not repeat or abs(gain)<=1e-12
     repeats+=repeat;zero+=abs(gain)<=1e-12;useful+=contrast['useful_controlled_contrast']
     d=dict(world_id=w['id'],arm=arm,step=step,probe=list(probe),probe_length=len(probe),pre_H=before_count,post_H=vs.count,realized_bits=gain,repeat=repeat,zero_information=abs(gain)<=1e-12,temporal_constraints_added=after_claims['temporal_onset_claims_identified']-claims['temporal_onset_claims_identified'],relational_distinctions_added=after_claims['context_and_order_claims_identified']-claims['context_and_order_claims_identified'],**contrast,**value)
     f.write(canon(d)+'\n');decisions.append({k:v for k,v in d.items() if k not in ['all_probe_values','partition_counts_by_sensor','contrasts']})
     if step in [1,2,3,4,6]:curves[step]=dict(H=vs.count,bits=vs.bits,information=initial-vs.bits,repeats=repeats,zero_information=zero,useful_contrasts=useful)
    exact=bits=0
    for q,probe in enumerate(w['reserved']):
     r=records['MODEL_RESPONSE',f"{w['id']}:{arm}:prediction:{q}"]['result'];true=[dict(zip(sensors,o)) for o in outcomes(w['root_ids'],probe)];scored,_=score_prediction(r['text'],sensors,true);predictions[arm].append(dict(world_id=w['id'],query=q,**scored));exact+=scored['exact'];bits+=scored['correct_bits']
    rows[arm].append(dict(world_id=w['id'],final_H=vs.count,final_bits=vs.bits,information=initial-vs.bits,repeats=repeats,zero_information=zero,useful_contrasts=useful,unique_probes=len(seen),short_exact=exact,short_correct_bits=bits,curves=curves,decisions=decisions))
 mechanism={}
 for arm in ['D','T']:
  measurements=[]
  for w,row,base_row in zip(worlds,rows[arm],rows['B']):
   measurement=measure(w,arm,records,row['decisions'],base_row['decisions']);row['prediction_receipt_audit']=measurement;measurements.append(measurement)
  mechanism[arm]=aggregate(measurements)
 for (kind,ident),r in records.items():
  if kind=='MODEL_RESPONSE':
   arm=ident.split(':')[1];v=r['result'];costs[arm]['model_calls']+=1
   for key in ['prompt_tokens','generation_token_count','seconds']:costs[arm][key]+=v[key]
 summaries={a:summarize(rows[a],predictions[a]) for a in arms};comp=comparisons(rows,summaries);integrity=all(summaries[a]['prediction']['valid']==len(predictions[a]) for a in arms)
 result=dict(raw_freeze_commit=raw_commit,private_raw_sha256=raw['private_raw_sha256'],arms=summaries,paired_comparisons=comp,decision=decision(comp,mechanism,integrity),prediction_mechanism=mechanism,costs={a:dict(v) for a,v in costs.items()},audits=audits,contribution_details_sha256=filehash(details),planned_model_calls=544)
 save(output/'results.json',result);save(output/'per-world-results.private.json',dict(rows=rows,predictions=predictions));print(canon(dict(status='SCORED',classification=result['decision']['classification'],recommended_arm=result['decision']['recommended_arm'])),flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--raw-commit',required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();score(a.raw_commit,a.output)
