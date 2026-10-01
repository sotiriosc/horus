"""Frozen A0 worker. Receives semantic messages only; never imports evaluator.

No training or optimizer. No subject tools. Exact preserved HF chat template.
Technical context/output limits qualify synthetically before Method Freeze.
"""
import importlib.util,sys,time,os
from common import *
CONTEXT=4096
MAX_NEW=256
BATCH=1
spec=importlib.util.spec_from_file_location('preserved_hf_runtime',TEMPORAL/'runtime.py');runtime=importlib.util.module_from_spec(spec);spec.loader.exec_module(runtime)
runtime.CONTEXT=CONTEXT;runtime.MAX_NEW=MAX_NEW

def load():
 from safetensors.torch import load_file
 from peft import set_peft_model_state_dict
 assert filehash(ADAPTER)==ADAPTER_SHA
 model,tok=runtime.load()
 assert runtime.fingerprints(model,False)==json.loads((TEMPORAL/'M0-base-fingerprints.json').read_bytes())
 set_peft_model_state_dict(model,load_file(str(ADAPTER)))
 assert runtime.fingerprints(model,True)==json.loads((TEMPORAL/'M1-artifact-freeze.json').read_bytes())['adapter_parameter_fingerprints']
 for p in model.parameters():p.requires_grad_(False)
 return model,tok

def qualification():
 from interface import synthetic_fixtures,parse_probe,parse_prediction
 start=time.monotonic();model,tok=load();print('Exact loaded base and M1 fingerprints PASS; synthetic schema qualification starting.',flush=True)
 fixtures=synthetic_fixtures();rows=[]
 for first in range(0,len(fixtures),BATCH):
  batch=fixtures[first:first+BATCH]
  results=runtime.infer(model,tok,[x['messages'] for x in batch])
  for fixture,result in zip(batch,results):
   try:
    if fixture['kind']=='selection':parse_probe(result['text'],fixture['allowed'])
    else:parse_prediction(result['text'],fixture['sensors'],fixture['length'])
    valid=True
   except (AssertionError,ValueError,TypeError,KeyError):valid=False
   rows.append(dict(kind=fixture['kind'],schema_valid=valid,**result))
  print(f'Synthetic schemas {len(rows)}/{len(fixtures)}; elapsed {time.monotonic()-start:.1f}s',flush=True)
 import torch
 out=ASSETS/'engineering';out.mkdir(exist_ok=True,parents=True);save(out/'synthetic-runtime-outputs.json',rows)
 report=dict(status='PASS' if all(x['schema_valid'] for x in rows) else 'FAIL',loaded_base_fingerprints_match=True,loaded_adapter_fingerprints_match=True,base_revision='231c69a380487f6c0e52d02dcf0d5456d1918201',adapter_sha256=ADAPTER_SHA,context=CONTEXT,max_new_tokens=MAX_NEW,inference_batch=BATCH,synthetic_calls=len(rows),scientific_calls=0,schemas_valid=sum(x['schema_valid'] for x in rows),max_prompt_tokens=max(x['prompt_tokens'] for x in rows),all_parameters_cuda=all(p.device.type=='cuda' for p in model.parameters()),all_parameters_frozen=all(not p.requires_grad for p in model.parameters()),peak_allocated_bytes=torch.cuda.max_memory_allocated(),seconds=round(time.monotonic()-start,2),output_sha256=filehash(out/'synthetic-runtime-outputs.json'),settings=dict(do_sample=False,enable_thinking=False,use_cache=True,padding_side='left',attention='sdpa',quantization='NF4 double quantization; BF16 compute',seed=runtime.SEED,tools=False,web=False))
 save(P/'runtime-qualification.json',report);print(canon(report),flush=True)
 assert report['status']=='PASS','Synthetic schema qualification failed; STOP before Method Freeze'
if __name__=='__main__':
 assert sys.argv[1:] == ['--qualify'];qualification()
