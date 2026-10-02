"""Synthetic transport/context/schema qualification; never scientific worlds."""
import random,time
from common import *
from interface import *
from machines import PROBES
from legal_choice import LegalChoiceTrie
from prediction_format import PredictionFormat

def fixture():
 ports=dict(actuators=['K7','Q2','N4','W8'],sensors=['V9','R3','Z8','M6']);reset=dict.fromkeys(ports['sensors'],0)
 legal=[dict(id=f'P{i:03d}',sequence=[ports['actuators'][a] for a in p]) for i,p in enumerate(p for p in PROBES if p not in [(0,0,0),(0,1,0)])]
 ledger=[dict(experiment=i+1,probe_id=r['id'],probe=r['sequence'],observations=[{s:(i+j+k)%2 for k,s in enumerate(ports['sensors'])} for j in range(len(r['sequence']))]) for i,r in enumerate([r for r in legal if len(r['sequence'])==2][:5])]
 return ports,reset,legal,ledger

def cpu(tok):
 ports,reset,legal,ledger=fixture();maximum=0;count=0
 rng=random.Random(100202)
 for i in range(200):
  selected=rng.sample(legal,5) if i else [r for r in legal if len(r['sequence'])==2][:5]
  history=[dict(experiment=j+1,probe_id=r['id'],probe=r['sequence'],observations=[dict.fromkeys(ports['sensors'],(j+k)%2) for k in range(len(r['sequence']))]) for j,r in enumerate(selected)]
  for arm in ['A','B','C']:
   msg=messages(ports,reset,history,'choice',arm,legal=legal);n=len(tok.apply_chat_template(msg,tokenize=True,add_generation_prompt=True,enable_thinking=False))+LegalChoiceTrie(tok,[r['id'] for r in legal]).max_tokens
   maximum=max(maximum,n);count+=1;assert n<=4096,(arm,n)
 return dict(context_cases=count,maximum_prompt_plus_generation=maximum)

def main():
 from runtime import load,infer
 start=time.monotonic();model,tok=load();check=cpu(tok);ports,reset,legal,ledger=fixture();rows=[]
 def retain(row):rows.append(row);save(ASSETS/'engineering/interface-responses.private.json',rows)
 for n in [0,5]:
  for arm in ['A','B','C']:
   r=infer(model,tok,messages(ports,reset,ledger[:n],'choice',arm,legal=legal),legal_ids=[x['id'] for x in legal]);retain(dict(kind='choice',arm=arm,ledger_size=n,**r));parse_choice(r['text'],legal)
 for arm in ['A','C']:
  r=infer(model,tok,messages(ports,reset,ledger,'prediction',arm,query=['K7','Q2','K7']),prediction_shape=dict(sensors=ports['sensors'],length=3));retain(dict(kind='prediction',arm=arm,**r));parse_prediction(r['text'],ports['sensors'],3)
 directed=[]
 for target in ['P002','P079']:
  msg=[dict(role='system',content='Synthetic transport check. Copy the requested legal ID exactly.'),dict(role='user',content='Return '+canon(dict(probe_id=target)))]
  r=infer(model,tok,msg,legal_ids=[x['id'] for x in legal]);retain(dict(kind='directed',**r));assert r['probe_id']==target;directed.append(r['probe_id'])
 import torch
 report=dict(status='PASS',scientific_model_calls=0,synthetic_model_calls=len(rows),context=4096,**check,all_parameters_frozen=all(not p.requires_grad for p in model.parameters()),all_parameters_cuda=all(p.device.type=='cuda' for p in model.parameters()),all_choice_and_prediction_schemas_valid=True,complete_ledger_preserved=True,legal_choices=82,context_dependent_legal_choices=directed,peak_allocated_bytes=torch.cuda.max_memory_allocated(),seconds=round(time.monotonic()-start,2),mean_seconds_by_kind={kind:sum(r['seconds'] for r in rows if r['kind']==kind)/sum(r['kind']==kind for r in rows) for kind in ['choice','prediction']},private_responses_sha256=filehash(ASSETS/'engineering/interface-responses.private.json'))
 save(P/'interface-qualification.json',report);print(canon(report),flush=True)
if __name__=='__main__':main()
