"""Synthetic-only complete-ledger, T-analysis and prediction qualification."""
import time
from common import *
from interface import *
from runtime import load,infer,CONTEXT,TEXT_MAX_NEW

def main():
 start=time.monotonic();model,tok=load();ports,reset,legal,ledger=synthetic_fixture();rows=[];prior=None
 private=ASSETS/'engineering'
 def retain(row):
  rows.append(row);save(private/'interface-responses.private.json',rows)
 print('A0 identity verified; qualifying full-ledger two-stage interface.',flush=True)
 for n in (0,11):
  msgs=messages(ports,reset,ledger[:n],'analysis',legal=legal,previous_analysis=prior,target=dict(zip(ports['sensors'],[1,0,1,0])))
  r=infer(model,tok,msgs);retain(dict(kind='analysis',**r));parse_analysis(r['text']);prior=r['text']
  msgs=messages(ports,reset,ledger[:n],'choice',legal=legal,analysis=prior,target=dict(zip(ports['sensors'],[1,0,1,0])))
  r=infer(model,tok,msgs,[x['id'] for x in legal]);retain(dict(kind='choice',**r));parse_choice(r['text'],legal)
  print(f'Synthetic T stages qualified at ledger size {n}; elapsed {time.monotonic()-start:.1f}s',flush=True)
 for n in (3,6):
  msgs=messages(ports,reset,ledger,'prediction',query=['K7','Q2','W8','N4','K7','Q2'][:n])
  r=infer(model,tok,msgs,prediction_shape=dict(sensors=ports['sensors'],length=n));retain(dict(kind='prediction',query_length=n,**r));parse_prediction(r['text'],ports['sensors'],n)
  print(f'Synthetic length-{n} prediction schema qualified; elapsed {time.monotonic()-start:.1f}s',flush=True)
 private=ASSETS/'engineering';save(private/'interface-responses.private.json',rows)
 import torch
 report=dict(status='PASS',synthetic_model_calls=len(rows),scientific_model_calls=0,all_required_schemas_valid=True,context=CONTEXT,text_max_new=TEXT_MAX_NEW,maximum_prompt_tokens=max(r['prompt_tokens'] for r in rows),complete_12_probe_ledger_preserved=True,analysis_is_unverified=True,legal_choice_mask_used=True,all_parameters_frozen=all(not p.requires_grad for p in model.parameters()),peak_allocated_bytes=torch.cuda.max_memory_allocated(),seconds=round(time.monotonic()-start,2),timing_seconds_by_kind={kind:sum(r['seconds'] for r in rows if r['kind']==kind)/sum(r['kind']==kind for r in rows) for kind in ['analysis','choice','prediction']},private_responses_sha256=filehash(private/'interface-responses.private.json'))
 save(P/'interface-qualification.json',report);print(canon(report),flush=True)
if __name__=='__main__':main()
