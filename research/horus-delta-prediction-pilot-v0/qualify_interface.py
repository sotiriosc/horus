"""Synthetic qualification only; no scientific prompts or machine outcomes."""
import random,time
from common import *
from interface import *
from machines import PROBES
from legal_choice import LegalChoiceTrie
from runtime import CONTEXT,TEXT_MAX_NEW

def fixture():
 ports=dict(actuators=['K7','Q2','N4','W8'],sensors=['V9','R3','Z8','M6']);reset=dict.fromkeys(ports['sensors'],0)
 legal=[dict(id=f'P{i:03d}',sequence=[ports['actuators'][a] for a in p]) for i,p in enumerate(p for p in PROBES if p not in [(0,0,0),(0,1,0)])]
 chosen=[r for r in legal if len(r['sequence'])==2][:5]
 ledger=[dict(experiment=i+1,probe_id=r['id'],probe=r['sequence'],observations=[{s:(i+j+k)%2 for k,s in enumerate(ports['sensors'])} for j in range(len(r['sequence']))]) for i,r in enumerate(chosen)]
 return ports,reset,legal,ledger

def synthetic_analysis(arm,ledger,legal,sensors):
 seen={e['probe_id'] for e in ledger};target=next(r for r in legal if r['id'] not in seen);a=ledger[0];b=next((e for e in reversed(ledger) if e['probe_id']!=a['probe_id']),None)
 x=dict(status='PREDICTION',evidence_A=a['probe_id'],evidence_B=b['probe_id'] if b else 'NONE',observed_endpoint_A=''.join(str(a['observations'][-1][s]) for s in sensors),observed_endpoint_B=''.join(str(b['observations'][-1][s]) for s in sensors) if b else 'NONE',comparison_kind='other' if b else 'single_observation',prediction=dict(untested_probe_id=target['id'],predicted_trace=['0000']*len(target['sequence'])))
 if arm=='D':
  x.update(observed_input_delta='Synthetic input comparison.',observed_output_delta='Synthetic output comparison.',provisional_relation='Synthetic provisional relation.',why_this_test_matters='Synthetic test.');x['prediction']['predicted_difference']='Synthetic prediction.'
 else:
  x.update(observed_delta=dict(input_or_context='Synthetic input.',outcome='Synthetic outcome.'),time=dict(what_temporal_difference_is_supported='Synthetic difference.',what_temporal_part_remains_unknown='Synthetic unknown.'),relation=dict(what_changed_with_what='Synthetic comparison.',candidate_relation='Synthetic relation.'),direction=dict(which_unknown_distinction_should_be_resolved_next='Synthetic distinction.'),alternative_prediction='Synthetic alternative.',alternative_trace=['1111']*len(target['sequence']),what_result_would_separate_them='Synthetic contrast.');x['prediction']['expected_outcome_or_delta']='Synthetic prediction.'
 return canon(x)

def cpu(tok):
 ports,reset,legal,ledger=fixture();rng=random.Random(100402);maximum=0;cases=0
 for i in range(120):
  selected=rng.sample(legal,6);history=[dict(experiment=j+1,probe_id=r['id'],probe=r['sequence'],observations=[dict.fromkeys(ports['sensors'],(j+k)%2) for k in range(len(r['sequence']))]) for j,r in enumerate(selected)]
  for arm,mode in [('B','choice'),('D','analysis'),('T','analysis'),('D','choice'),('T','choice'),('B','prediction')]:
   h=history if mode=='prediction' else history[:5];msg=messages(ports,reset,h,mode,arm,legal=legal,query=['K7']*3 if mode=='prediction' else None,analysis=synthetic_analysis(arm,h,legal,ports['sensors']) if arm!='B' and mode=='choice' else None)
   n=len(tok.apply_chat_template(msg,tokenize=True,add_generation_prompt=True,enable_thinking=False))+(TEXT_MAX_NEW if mode=='analysis' else 128);assert n<=CONTEXT;maximum=max(maximum,n);cases+=1
 return dict(context_cases=cases,maximum_prompt_plus_generation=maximum)

def main():
 from runtime import load,infer
 start=time.monotonic();model,tok=load();check=cpu(tok);ports,reset,legal,ledger=fixture();rows=[];predictions={'D':0,'T':0}
 def retain(row):rows.append(row);save(ASSETS/'engineering/interface-responses.private.json',rows)
 for arm in ['B','D','T']:
  r=infer(model,tok,messages(ports,reset,[],'choice',arm,legal=legal),legal_ids=[x['id'] for x in legal]);retain(dict(kind='choice',arm=arm,**r));parse_choice(r['text'],legal)
 for n in [1,5]:
  for arm in ['D','T']:
   r=infer(model,tok,messages(ports,reset,ledger[:n],'analysis',arm,legal=legal),analysis_shape=dict(arm=arm,ledger=ledger[:n],legal=legal,sensors=ports['sensors']));retain(dict(kind='analysis',arm=arm,ledger_size=n,**r));parsed=parse_analysis(r['text'],arm,ledger[:n],legal,ports['sensors']);assert parsed is not None,'Synthetic delta schema failed';predictions[arm]+=parsed['status']=='PREDICTION'
   r=infer(model,tok,messages(ports,reset,ledger[:n],'choice',arm,legal=legal,analysis=r['text']),legal_ids=[x['id'] for x in legal]);retain(dict(kind='choice',arm=arm,**r));parse_choice(r['text'],legal)
 assert all(predictions.values()),'Each schema needs a non-abstaining synthetic example'
 for arm in ['B','T']:
  r=infer(model,tok,messages(ports,reset,ledger,'prediction',arm,query=['K7','Q2','K7']),prediction_shape=dict(sensors=ports['sensors'],length=3));retain(dict(kind='prediction',arm=arm,**r));parse_prediction(r['text'],ports['sensors'],3)
 for target in ['P002','P079']:
  msg=[dict(role='system',content='Synthetic transport check. Copy the requested legal ID exactly.'),dict(role='user',content='Return '+canon(dict(probe_id=target)))];r=infer(model,tok,msg,legal_ids=[x['id'] for x in legal]);retain(dict(kind='directed',**r));assert r['probe_id']==target
 import torch
 save(P/'interface-qualification.json',dict(status='PASS',scientific_model_calls=0,synthetic_model_calls=len(rows),context=CONTEXT,**check,all_parameters_cuda=all(p.device.type=='cuda' for p in model.parameters()),all_parameters_frozen=all(not p.requires_grad for p in model.parameters()),all_schemas_valid=True,nonabstaining_examples=predictions,legal_choices=82,peak_allocated_bytes=torch.cuda.max_memory_allocated(),mean_seconds_by_kind={k:sum(r['seconds'] for r in rows if r['kind']==k)/sum(r['kind']==k for r in rows) for k in ['analysis','choice','prediction']},seconds=round(time.monotonic()-start,2),private_responses_sha256=filehash(ASSETS/'engineering/interface-responses.private.json')));print((P/'interface-qualification.json').read_text(),flush=True)
if __name__=='__main__':main()
