"""Non-scientific prospective engineering checks; no Horus decisions or Memory."""
import json,statistics,time
from pathlib import Path
from .runtime import *

def main():
 plan=json.loads((PUBLIC/'engineering-plan.json').read_text());root=PRIVATE/'qualification-v1';root.mkdir(parents=True,exist_ok=False)
 # Preserve historical decision model and sampling. CPU parking is an empty load-only request.
 from horus.live import ModelClient
 from experiments.grounded_authority_autonomous_agent_v0.protocol import MODEL as ORDINARY,ACTION_SYSTEM,ACTION_OPTIONS
 prior=json.loads((PRIVATE/'qualification/ordinary-envelope.json').read_text());assert prior['transport_error'] is None
 answer=json.loads(prior['raw_output']);assert set(answer)=={'selected_action'} and answer['selected_action'] in CANDIDATES
 ordinary=dict(model=ORDINARY,digest=plan['ordinary_digest'],synthetic_schema_valid=True,decision_seconds=prior['response_metadata']['total_duration']/1e9,parking_no_generation=True,parking_method='empty prompt, template and system with num_gpu=0; source routes.go v0.1.16 load-only branch',idle_samples=idle(),server_binary_sha256=file_sha('/usr/local/bin/ollama'),preserved_initial_attempt='qualification/ordinary-envelope.json')
 write(PUBLIC/'ordinary-qualification.json',ordinary)
 print(json.dumps(dict(stage='ordinary_qualification',status='PASS',seconds=round(ordinary['decision_seconds'],1))),flush=True)
 rows=[]
 for action in CANDIDATES:
  with Server(action,root/action) as server:
   for n in (64,1800,6500):
    r=request('Return only the requested JSON object.','Non-scientific runtime qualification. '+('parcel ' * n)+'\nReturn {"ready":true}.',64,READY_SCHEMA)
    row=server.measure(r,f'context-{n}','json');assert row['valid'] and row['prompt_tokens']+64<=8192
    rows.append(row)
   if action=='HOLD':
    noise=request('Return a JSON object with a summary string.','Non-scientific engineering variance fixture. '+('Parcel records are synthetic. '*350)+'Write a summary of approximately 120 words.',512,{'type':'object','properties':{'summary':{'type':'string'}},'required':['summary'],'additionalProperties':False})
    for i in range(7):
     row=server.measure(noise,f'noise-{i}','json');assert row['valid'];rows.append({**row,'noise':True})
  print(json.dumps(dict(stage='candidate_qualification',action=action,status='PASS',elapsed_seconds=round(sum(r['wall_seconds'] for r in rows if r['action']==action),1))),flush=True)
 noise_rows=[r for r in rows if r.get('noise')];latencies=[r['wall_seconds'] for r in noise_rows];median=statistics.median(latencies);deviation=max(abs(x/median-1) for x in latencies)
 # Set conservative thresholds from synthetic noise only; never use candidate speed for selection.
 import math
 margin=max(.10,math.ceil(3*deviation*100)/100)
 if margin>.30:raise RuntimeError('Synthetic variance too high to support v0 operational threshold; stop before method freeze')
 result=dict(status='PASS',scientific_calls=0,candidates=CANDIDATES,rows=rows,noise=dict(samples=len(latencies),median_seconds=median,maximum_relative_deviation=deviation,rule='margin=max(10%,ceil(3*max absolute relative deviation to whole percentage point)); stop if >30%',margin=margin,positive_ratio=1-margin,negative_ratio=1+margin),ordinary=ordinary)
 write(PUBLIC/'qualification.json',result);print(json.dumps(dict(stage='engineering_complete',status='PASS',noise=result['noise'])),flush=True)
if __name__=='__main__':main()
