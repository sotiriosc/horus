"""Fixed two-epoch continuation, final checkpoint only; no accuracy-guided selection."""
import math,random,time,torch
from common import *
import stack
from stack import runtime
from engine import emit,verified_tapes,cases
from admission import get_prediction
from worlds import messages
from safetensors.torch import load_file
from peft import set_peft_model_state_dict

def validation_examples(cycle):
 tape=verified_tapes(f'harvest{cycle}')[f'C{cycle-1}',f'V{cycle}'];result=[]
 for c in cases(f'V{cycle}'):
  r=tape.index['EXECUTED_TRANSITION',c['id']];o,v=get_prediction(tape,r)
  assert v==c['visible'];result.append(dict(messages=messages(v),target=canon({'next_observation':r['record']['actual_next_observation']})))
 return result

def artifact_manifest(folder):return {p.name:dict(sha256=filehash(p),bytes=p.stat().st_size) for p in sorted(folder.iterdir()) if p.is_file()}
def train(cycle):
 arm=f'C{cycle}';start=time.monotonic();model,tok=stack.load(f'C{cycle-1}');base_before=runtime.fingerprints(model,False);assert base_before==json.loads((OLD/'M0-base-fingerprints.json').read_bytes())
 initial=runtime.fingerprints(model,True);initialdir=ADAPTERS/(arm+'-initial');finaldir=ADAPTERS/arm;assert not (P/(arm+'-artifact-freeze.json')).exists()
 model.save_pretrained(initialdir);training=rows(P/(f'D{cycle}.jsonl'))
 validation=validation_examples(cycle);params=[p for p in model.parameters() if p.requires_grad]
 opt=torch.optim.AdamW(params,lr=1e-4,betas=(.9,.999),eps=1e-8,weight_decay=.01,foreach=False)
 orders=[]
 for epoch in range(2):
  order=list(range(len(training)));random.Random(SEED+1000*cycle+epoch).shuffle(order);orders.append(order)
 chunks=[(epoch,order[i:i+8]) for epoch,order in enumerate(orders) for i in range(0,len(order),8)];total=len(chunks);warmup=max(1,math.ceil(.05*total));losslog=[];validationlog=[];seen=0;torch.cuda.reset_peak_memory_stats()
 def validation_loss(epoch):
  model.eval();losses=[]
  with torch.no_grad():
   for c in validation:
    value=runtime.loss(model,tok,c['messages'],c['target']);assert torch.isfinite(value);losses.append(float(value))
  result=dict(after_epoch=epoch,mean_loss=sum(losses)/len(losses));validationlog.append(result);emit(arm+'-validation',start,epoch+1,3,mean_loss=result['mean_loss']);return result
 completed_step=0;recovery_used=None
 checkpoints=sorted(ADAPTERS.glob(arm+'-recovery-step-*/COMPLETE.json'))
 if checkpoints:
  marker=checkpoints[-1];manifest=json.loads(marker.read_bytes());folder=marker.parent
  for name,digest in manifest['files'].items():assert filehash(folder/name)==digest
  state=torch.load(folder/'training-state.pt',map_location='cpu',weights_only=False)
  assert state['training_sha256']==filehash(P/(f'D{cycle}.jsonl')) and state['initial_fingerprints']==initial
  set_peft_model_state_dict(model,load_file(str(folder/'adapter_model.safetensors')));opt.load_state_dict(state['optimizer'])
  completed_step=state['completed_step'];seen=state['examples_seen'];losslog=state['losslog'];validationlog=state['validationlog']
  torch.set_rng_state(state['torch_rng']);torch.cuda.set_rng_state_all(state['cuda_rng']);recovery_used=folder.name
 else:validation_loss(0)
 for step,(epoch,indices) in enumerate(chunks,1):
  if step<=completed_step:continue
  model.train();opt.zero_grad(set_to_none=True);lr=1e-4*min(step/warmup,max(0,(total-step)/(total-warmup)))
  for g in opt.param_groups:g['lr']=lr
  losses=[]
  for idx in indices:
   e=training[idx];value=runtime.loss(model,tok,e['messages'],e['target']);assert torch.isfinite(value);losses.append(float(value.detach()));(value/len(indices)).backward();seen+=1
  norm=float(torch.nn.utils.clip_grad_norm_(params,1.,error_if_nonfinite=True));opt.step();assert all(torch.isfinite(p).all() for p in params)
  record=dict(step=step,epoch=epoch+1,examples_seen=seen,loss=sum(losses)/len(losses),learning_rate=lr,gradient_norm=norm,wall_seconds=round(time.monotonic()-start,2));losslog.append(record)
  with (PRIVATE/(arm+'-training-log.jsonl')).open('a') as f:f.write(canon(record)+'\n')
  if step%10==0 or step==total:emit(arm+'-training',start,step,total,examples_seen=seen,loss=record['loss'])
  end_epoch=step==total or chunks[step][0]!=epoch
  if end_epoch:validation_loss(epoch+1)
  if step%25==0 or end_epoch:
   checkpoint=ADAPTERS/(arm+f'-recovery-step-{step:06d}');checkpoint.mkdir(exist_ok=True);assert not (checkpoint/'COMPLETE.json').exists();model.save_pretrained(checkpoint)
   torch.save(dict(optimizer=opt.state_dict(),completed_step=step,examples_seen=seen,torch_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all(),training_sha256=filehash(P/(f'D{cycle}.jsonl')),initial_fingerprints=initial,losslog=losslog,validationlog=validationlog),checkpoint/'training-state.pt')
   dump(checkpoint/'COMPLETE.json',dict(files={f.name:filehash(f) for f in checkpoint.iterdir() if f.is_file()}))
 model.eval();final=runtime.fingerprints(model,True);base_after=runtime.fingerprints(model,False);assert base_before==base_after;assert initial!=final;model.save_pretrained(finaldir);torch.save(opt.state_dict(),finaldir/'optimizer.pt')
 disk=load_file(str(finaldir/'adapter_model.safetensors'));set_peft_model_state_dict(model,disk);assert runtime.fingerprints(model,True)==final
 result=dict(arm=arm,recovery_used=recovery_used,parent_arm=f'C{cycle-1}',base_unchanged=base_before==base_after,adapter_changed=initial!=final,trainable_parameters=sum(p.numel() for p in params),initial_adapter_files=artifact_manifest(initialdir),adapter_files=artifact_manifest(finaldir),initial_adapter_parameter_fingerprints=initial,adapter_parameter_fingerprints=final,epochs=2,optimizer_steps=total,examples_seen=seen,seed=runtime.SEED,training_order_seed=SEED+1000*cycle,optimizer={'name':'AdamW','learning_rate':1e-4,'betas':[.9,.999],'eps':1e-8,'weight_decay':.01,'foreach':False,'gradient_accumulation':8,'clip_norm':1.,'schedule':'5% ceiling warmup then linear decay to zero'},loss_curve=losslog,validation_loss=validationlog,finite_loss_gradient_and_parameter_checks=True,peak_allocated_bytes=torch.cuda.max_memory_allocated(),peak_reserved_bytes=torch.cuda.max_memory_reserved(),wall_seconds=round(time.monotonic()-start,2),sealed_test_calls=0,checkpoint_reload_exact=True,adapter_storage='Immutable local artifacts; hashes/configuration published, binary adapter and optimizer are not Git objects.')
 dump(P/(arm+'-artifact-freeze.json'),result)
 for folder in [initialdir,finaldir]:
  for f in folder.iterdir():
   if f.is_file():f.chmod(0o444)
 commit('Freeze '+arm+' learned adapter before sealed test inference')

