"""Only synthetic observations qualify public message/transport/schema/context."""
import random,time
from common import *
from interface import *
from machines import PROBES
from legal_choice import LegalChoiceTrie
from runtime import CONTEXT,TEXT_MAX_NEW

def fixture():
 ports=dict(actuators=['K7','Q2','N4','W8'],sensors=['V9','R3','Z8','M6']);reset=dict.fromkeys(ports['sensors'],0)
 legal=[dict(id=f'P{i:03d}',sequence=[ports['actuators'][a] for a in p]) for i,p in enumerate(p for p in PROBES if p not in [(0,0,0),(0,1,0),(0,1,2)])]
 ledger=[dict(experiment=i+1,probe_id=r['id'],probe=r['sequence'],observations=[{s:(i+j+k)%2 for k,s in enumerate(ports['sensors'])} for j in range(len(r['sequence']))]) for i,r in enumerate([r for r in legal if len(r['sequence'])==3][:8])]
 return ports,reset,legal,ledger

def sample_frontier(legal,sensors):
 return canon(dict(supported_so_far=['x'*120],unresolved_discrepancies=['x'*120],current_questions=[dict(question='x'*120,probe_id=legal[-1]['id'],sensor=sensors[-1])],limits_of_current_discrimination=['x'*120],status='UNRESOLVED_BEYOND_CURRENT_DISCRIMINATION'))

def cpu(tok):
 ports,reset,legal,history=fixture();rng=random.Random(100302);maximum=0;count=0
 for i in range(160):
  selected=rng.sample(legal,8);ledger=[dict(experiment=j+1,probe_id=r['id'],probe=r['sequence'],observations=[dict.fromkeys(ports['sensors'],(j+k)%2) for k in range(len(r['sequence']))]) for j,r in enumerate(selected)]
  for arm,mode in [('A','choice'),('B','choice'),('O','analysis'),('O','choice'),('A','prediction')]:
   msg=messages(ports,reset,ledger if mode=='prediction' else ledger[:7],mode,arm,legal=legal,query=['K7']*3 if mode=='prediction' else None,interpretation=sample_frontier(legal,ports['sensors']) if arm=='O' and mode=='choice' else None)
   n=len(tok.apply_chat_template(msg,tokenize=True,add_generation_prompt=True,enable_thinking=False))+(TEXT_MAX_NEW if mode=='analysis' else 128)
   maximum=max(maximum,n);count+=1;assert n<=CONTEXT,(mode,arm,n)
 return dict(context_cases=count,maximum_prompt_plus_generation=maximum)

def main():
 from runtime import load,infer
 start=time.monotonic();model,tok=load();check=cpu(tok);ports,reset,legal,ledger=fixture();rows=[]
 def retain(row):rows.append(row);save(ASSETS/'engineering/interface-responses.private.json',rows)
 for n in [0,7]:
  for arm in ['A','B','O']:
   frontier=None
   if arm=='O':
    r=infer(model,tok,messages(ports,reset,ledger[:n],'analysis','O',legal=legal));retain(dict(kind='analysis',arm=arm,ledger_size=n,**r));frontier=r['text'];assert parse_frontier(frontier,legal,ports['sensors']) is not None,'Synthetic frontier schema failed'
   r=infer(model,tok,messages(ports,reset,ledger[:n],'choice',arm,legal=legal,interpretation=frontier),legal_ids=[x['id'] for x in legal]);retain(dict(kind='choice',arm=arm,ledger_size=n,**r));parse_choice(r['text'],legal)
 for arm in ['A','O']:
  r=infer(model,tok,messages(ports,reset,ledger,'prediction',arm,query=['K7','Q2','K7']),prediction_shape=dict(sensors=ports['sensors'],length=3));retain(dict(kind='prediction',arm=arm,**r));parse_prediction(r['text'],ports['sensors'],3)
 for target in ['P002','P079']:
  msg=[dict(role='system',content='Synthetic transport check. Copy the requested legal ID exactly.'),dict(role='user',content='Return '+canon(dict(probe_id=target)))]
  r=infer(model,tok,msg,legal_ids=[x['id'] for x in legal]);retain(dict(kind='directed',**r));assert r['probe_id']==target
 import torch
 report=dict(status='PASS',scientific_model_calls=0,synthetic_model_calls=len(rows),context=CONTEXT,**check,all_parameters_frozen=all(not p.requires_grad for p in model.parameters()),all_parameters_cuda=all(p.device.type=='cuda' for p in model.parameters()),all_schemas_valid=True,legal_choices=81,peak_allocated_bytes=torch.cuda.max_memory_allocated(),seconds=round(time.monotonic()-start,2),mean_seconds_by_kind={kind:sum(r['seconds'] for r in rows if r['kind']==kind)/sum(r['kind']==kind for r in rows) for kind in ['analysis','choice','prediction']},private_responses_sha256=filehash(ASSETS/'engineering/interface-responses.private.json'))
 save(P/'interface-qualification.json',report);print(canon(report),flush=True)
if __name__=='__main__':main()
