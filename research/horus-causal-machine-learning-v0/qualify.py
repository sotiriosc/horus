"""Synthetic engineering only. No scientific case, gold label or accuracy is read."""
import importlib.metadata,itertools,json,os,subprocess,time,traceback
from pathlib import Path
import torch
from peft import get_peft_model_state_dict,set_peft_model_state_dict
from safetensors.torch import load_file
from stack import runtime,load,attach
from stack import *
seed=runtime.seed; fingerprints=runtime.fingerprints; infer=runtime.infer; loss=runtime.loss; prompt=runtime.prompt
RANK=runtime.RANK; CONTEXT=runtime.CONTEXT; MAX_NEW=runtime.MAX_NEW; INFERENCE_BATCH=runtime.INFERENCE_BATCH
P=Path(__file__).resolve().parent
OUT=Path('/mnt/d/horus-research-assets/causal-machine-v0/engineering');OUT.mkdir(parents=True,exist_ok=True)
start=time.monotonic();result={'scientific_calls':0,'purpose':'Synthetic copy/schema transport and full-context train/save/reload qualification, not scientific accuracy selection','recipe':{'rank':RANK,'alpha':2*RANK,'dropout':0,'target_modules':'all-linear','context':CONTEXT,'microbatch':1,'gradient_accumulation':8,'inference_batch':INFERENCE_BATCH,'max_new_tokens':MAX_NEW,'reasoning':'enable_thinking=False','decoding':'greedy','quantization':'NF4 double quant BF16 compute','attention':'sdpa','gradient_checkpointing':'non-reentrant'}}
def emit(x):print(json.dumps(dict(x,elapsed_seconds=round(time.monotonic()-start,1))),flush=True)
def write():
 result['wall_seconds']=round(time.monotonic()-start,2);(P/'engineering-qualification.json').write_text(json.dumps(result,indent=2)+'\n')
try:
 model,tok=load('C0');torch.cuda.reset_peak_memory_stats();result['trainable_parameters']=sum(p.numel() for p in model.parameters() if p.requires_grad);result['targeted_linear_modules']=280
 result['all_parameters_cuda']=all(p.device.type=='cuda' for p in model.parameters());result['gpu']=torch.cuda.get_device_name();result['vram_bytes']=torch.cuda.get_device_properties(0).total_memory;result['cuda']=torch.version.cuda;result['bf16_supported']=torch.cuda.is_bf16_supported()
 result['packages']={n:importlib.metadata.version(n) for n in ['torch','transformers','peft','bitsandbytes','accelerate','huggingface-hub','tokenizers','safetensors']};result['trl_used']=False
 result['package_lock']=subprocess.check_output([os.sys.executable,'-m','pip','freeze'],text=True).splitlines();result['gpu_driver']=subprocess.check_output(['nvidia-smi','--query-gpu=driver_version,uuid,memory.total','--format=csv,noheader'],text=True).strip()
 before=fingerprints(model,False);initial=fingerprints(model,True);model.save_pretrained(OUT/'initial');emit({'stage':'loaded','trainable_parameters':result['trainable_parameters'],'allocated_GiB':torch.cuda.memory_allocated()/2**30})
 fixtures=[];targets=[]
 for bits in itertools.product([0,1],repeat=4):
  target=json.dumps({'next_observation':dict(zip(['K1','L2','M3','N4'],bits))},separators=(',',':'));targets.append(target);fixtures.append([{'role':'system','content':'Synthetic transport test. Copy the requested JSON object exactly. Do not explain.'},{'role':'user','content':'Copy this JSON: '+target}])
 outputs=[]
 for i in range(0,16,INFERENCE_BATCH):outputs+=infer(model,tok,fixtures[i:i+INFERENCE_BATCH],enabled=True)
 result['synthetic_copy_schema']=[{'target':t,'output':o['text'],'valid':json.loads(o['text'])==json.loads(t)} for t,o in zip(targets,outputs)]
 assert all(x['valid'] for x in result['synthetic_copy_schema'])
 # Reserve full configured context in a neutral synthetic copy fixture; no scientific state semantics.
 longmsg=[{'role':'system','content':'Copy the final JSON object exactly. Ignore padding.'},{'role':'user','content':''}]
 padding='neutral '*(CONTEXT-200);longmsg[1]['content']=padding+'\nCopy this JSON: '+targets[0]
 while len(tok.encode(prompt(tok,longmsg),add_special_tokens=False))>CONTEXT-MAX_NEW:longmsg[1]['content']=longmsg[1]['content'][8:]
 longout=infer(model,tok,[longmsg]*INFERENCE_BATCH,True);assert all(json.loads(x['text'])==json.loads(targets[0]) for x in longout)
 result['long_inference_prompt_tokens']=longout[0]['prompt_tokens'];emit({'stage':'synthetic_inference_pass','peak_GiB':torch.cuda.max_memory_allocated()/2**30})
 model.train();params=[p for p in model.parameters() if p.requires_grad];opt=torch.optim.AdamW(params,lr=1e-4,weight_decay=.01,foreach=False);losses=[];gradnorm=[]
 for step in range(2):
  opt.zero_grad(set_to_none=True)
  for micro in range(8):
   value=loss(model,tok,fixtures[(step*8+micro)%16],targets[(step*8+micro)%16],synthetic_length=CONTEXT);assert torch.isfinite(value);losses.append(float(value.detach()));(value/8).backward()
   emit({'stage':'synthetic_training','step':step+1,'microbatch':micro+1,'estimated_remaining_seconds':round((time.monotonic()-start)*(16-(step*8+micro+1))/max(1,step*8+micro+1),1)})
  norm=torch.nn.utils.clip_grad_norm_(params,1.0,error_if_nonfinite=True);gradnorm.append(float(norm));assert float(norm)>0;opt.step()
  assert all(torch.isfinite(p).all() for p in params)
 model.eval();after=fingerprints(model,False);trained=fingerprints(model,True);assert before==after;assert initial!=trained;result['base_unchanged']=True;result['adapter_changed']=True
 model.save_pretrained(OUT/'trained');saved=load_file(str(OUT/'trained/adapter_model.safetensors'));inmem={k:v.detach().cpu() for k,v in get_peft_model_state_dict(model).items()};assert saved.keys()==inmem.keys() and all(torch.equal(saved[k],inmem[k]) for k in saved)
 prediction=infer(model,tok,fixtures[:4],True)
 set_peft_model_state_dict(model,load_file(str(OUT/'initial/adapter_model.safetensors')));assert fingerprints(model,True)==initial
 set_peft_model_state_dict(model,saved);assert fingerprints(model,True)==trained;assert infer(model,tok,fixtures[:4],True)==prediction
 attach(model,'C0');assert fingerprints(model,True)==initial;result['C0_restored_exactly']=True
 result.update(status='PASS',checkpoint_reload_exact=True,losses=losses,gradient_norms=gradnorm,peak_allocated_bytes=torch.cuda.max_memory_allocated(),peak_reserved_bytes=torch.cuda.max_memory_reserved(),synthetic_optimizer_steps=2,synthetic_microbatches=16)
except Exception as e:
 result.update(status='FAIL',exception_type=type(e).__name__,exception=str(e));traceback.print_exc();write();raise
write();emit({'stage':'qualification_complete','status':result['status'],'peak_allocated_GiB':result['peak_allocated_bytes']/2**30})
