"""Frozen stage runner. No test scoring before adapter/raw artifact commits."""
import argparse,contextlib,hashlib,json,math,os,random,subprocess,time,sys
from pathlib import Path
import torch
from safetensors.torch import load_file
from peft import set_peft_model_state_dict
import runtime
from data import *
from analysis import *
P=Path(__file__).resolve().parent;ROOT=P.parents[1];D=P/'materialized'
PRIVATE=Path('/mnt/d/horus-research-assets/qwen3-14b-qlora-v0/study-private')
ARTIFACTS=Path('/mnt/d/horus-research-assets/qwen3-14b-qlora-v0/study-adapters')
PREFIX='research/qwen-error-driven-qlora-learning-v0'

def filehash(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def commit(message):
 subprocess.run(['git','add','--',PREFIX],cwd=ROOT,check=True);subprocess.run(['git','commit','-m',message],cwd=ROOT,check=True)
 return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
def frozen_preflight():
 freeze=json.loads((P/'data-freeze.json').read_bytes())
 for path,digest in freeze['files'].items():assert filehash(P/path)==digest,path
 assert json.loads((P/'engineering-qualification.json').read_bytes())['status']=='PASS'
 assert subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)==''
 assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='research/qwen-error-driven-qlora-learning-v0'
 assert subprocess.run(['git','merge-base','--is-ancestor','379912673e692c7b4b7c28aa5b3a17b2bffbc0d3','HEAD'],cwd=ROOT).returncode==0
 PRIVATE.mkdir(parents=True,exist_ok=True);ARTIFACTS.mkdir(parents=True,exist_ok=True)
def emit(stage,start,done,total,**kwargs):
 elapsed=time.monotonic()-start;print(json.dumps(dict(stage=stage,done=done,total=total,elapsed_seconds=round(elapsed,1),estimated_remaining_seconds=round(elapsed/done*(total-done),1) if done else None,**kwargs)),flush=True)
def artifact_manifest(folder):return {p.name:dict(sha256=filehash(p),bytes=p.stat().st_size) for p in sorted(folder.iterdir()) if p.is_file()}
def attach(model,arm):
 if arm=='M0':return
 path=ARTIFACTS/arm/'adapter_model.safetensors';manifest=json.loads((P/(arm+'-artifact-freeze.json')).read_bytes());assert filehash(path)==manifest['adapter_files'][path.name]['sha256']
 set_peft_model_state_dict(model,load_file(str(path)));assert runtime.fingerprints(model,True)==manifest['adapter_parameter_fingerprints']

def infer_set(model,tok,arm,name):
 cs=rows(D/(name+'.jsonl'));path=PRIVATE/(arm+'-'+name+'-raw.jsonl');start=time.monotonic();existing=rows(path) if path.exists() else []
 assert [x['id'] for x in existing]==[c['id'] for c in cs[:len(existing)]]
 for c,o in zip(cs,existing):assert o['messages']==messages(c)
 # Only whole completed batches are resumed. A malformed/incomplete JSON line stops for investigation.
 with path.open('a') as f:
  for i in range(len(existing),len(cs),runtime.INFERENCE_BATCH):
   chunk=cs[i:i+runtime.INFERENCE_BATCH];requests=[messages(c) for c in chunk];answers=runtime.infer(model,tok,requests,enabled=arm!='M0')
   for c,msg,answer in zip(chunk,requests,answers):f.write(canonical(dict(id=c['id'],arm=arm,dataset=name,messages=msg,rendered_prompt=runtime.prompt(tok,msg),**answer))+'\n')
   f.flush();os.fsync(f.fileno())
   if (i//runtime.INFERENCE_BATCH)%10==0 or i+len(chunk)==len(cs):emit(arm+'-'+name,start,i+len(chunk),len(cs))
 assert len(rows(path))==len(cs);path.chmod(0o444)
 return dict(arm=arm,dataset=name,count=len(cs),private_file=path.name,sha256=filehash(path),exact_messages_and_rendered_prompts_preserved=True)

def freeze_raw(name,manifests):
 path=P/(name+'-raw-freeze.json');assert not path.exists();dump(path,dict(parent_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),scoring_performed=False,files=manifests));return commit('Freeze '+name+' raw model outputs before scoring')
def load_outputs(arm,name):
 path=PRIVATE/(arm+'-'+name+'-raw.jsonl')
 # The exact file must appear in a committed freeze before it may be parsed/scored.
 digest=filehash(path);registered=False
 for f in P.glob('*-raw-freeze.json'):
  tracked=subprocess.run(['git','ls-files','--error-unmatch',str(f.relative_to(ROOT))],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
  if tracked and any(x['private_file']==path.name and x['sha256']==digest for x in json.loads(f.read_bytes())['files']):registered=True
 assert registered,path
 return rows(path)

def harvest(cycle):
 arm='M0' if cycle==1 else 'M1';name=f'H{cycle}'
 if cycle==2:assert json.loads((P/'cycle1-results.json').read_bytes())['gate']['cycle2_authorized']
 model,tok=runtime.load();attach(model,arm);base=runtime.fingerprints(model,False)
 if cycle==1:dump(P/'M0-base-fingerprints.json',base)
 else:assert base==json.loads((P/'M0-base-fingerprints.json').read_bytes())
 manifest=infer_set(model,tok,arm,name);freeze_raw(name,[manifest]);outputs=load_outputs(arm,name);cs=rows(D/(name+'.jsonl'));scored=score(cs,outputs)
 # Public model text is confined to successfully parsed two-field JSON. Invalid raw text remains private, hashed.
 public=[dict(s,final_answer=o['text'] if s['schema'] else None,raw_answer_sha256=sha(o['text']),prompt_sha256=o['prompt_sha256']) for s,o in zip(scored,outputs)]
 write_rows(P/(name+'-scored.jsonl'),public)
 nerrors=sum(not row['joint'] for row in scored)
 if nerrors==0 or nerrors==len(scored):
  classification='ERROR_DRIVEN_PARAMETER_LEARNING_NOT_ESTABLISHED' if cycle==1 else 'SECOND_LEARNING_CYCLE_NOT_ESTABLISHED'
  result=dict(gate=dict(classification=classification,cycle2_authorized=False),admission_stop='No verified errors' if nerrors==0 else 'No correct harvest endpoints for mandatory replay',harvest_count=len(scored),harvest_errors=nerrors,training_started=False,sealed_test_calls=0)
  dump(P/(f'cycle{cycle}-results.json'),result);commit('Record cycle '+str(cycle)+' training-admission stop');print(json.dumps(result),flush=True);sys.exit(42)
 previous=rows(P/'D1.jsonl') if cycle==2 else None
 training,composition=construct_training(cs,rows(D/(f'N{cycle}.jsonl')),scored,cycle,previous)
 write_rows(P/(f'D{cycle}.jsonl'),training);dump(P/(f'D{cycle}-composition.json'),composition);dump(P/(f'D{cycle}-leakage-audit.json'),audit_datasets(D,training));commit('Freeze all-error training set D'+str(cycle))

def train(cycle):
 arm=f'M{cycle}';start=time.monotonic();model,tok=runtime.load();attach(model,'M0' if cycle==1 else 'M1');base_before=runtime.fingerprints(model,False);assert base_before==json.loads((P/'M0-base-fingerprints.json').read_bytes())
 initial=runtime.fingerprints(model,True);initialdir=ARTIFACTS/(arm+'-initial');finaldir=ARTIFACTS/arm;assert not finaldir.exists()
 model.save_pretrained(initialdir);training=rows(P/(f'D{cycle}.jsonl'));lookup={c['id']:c for n in ['H1','N1','H2','N2'] for c in rows(D/(n+'.jsonl'))}
 validation=rows(D/(f'V{cycle}.jsonl'));params=[p for p in model.parameters() if p.requires_grad]
 opt=torch.optim.AdamW(params,lr=1e-4,betas=(.9,.999),eps=1e-8,weight_decay=.01,foreach=False)
 orders=[]
 for epoch in range(2):
  order=list(range(len(training)));random.Random(SEED+1000*cycle+epoch).shuffle(order);orders.append(order)
 chunks=[(epoch,order[i:i+8]) for epoch,order in enumerate(orders) for i in range(0,len(order),8)];total=len(chunks);warmup=max(1,math.ceil(.05*total));losslog=[];validationlog=[];seen=0;torch.cuda.reset_peak_memory_stats()
 def validation_loss(epoch):
  model.eval();losses=[]
  with torch.no_grad():
   for c in validation:
    value=runtime.loss(model,tok,messages(c),canonical(c['gold']));assert torch.isfinite(value);losses.append(float(value))
  result=dict(after_epoch=epoch,mean_loss=sum(losses)/len(losses));validationlog.append(result);emit(arm+'-validation',start,epoch+1,3,mean_loss=result['mean_loss']);return result
 completed_step=0;recovery_used=None
 checkpoints=sorted(ARTIFACTS.glob(arm+'-recovery-step-*/COMPLETE.json'))
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
   e=training[idx];c=lookup[e['case_id']];assert e['target']==canonical(c['gold']);value=runtime.loss(model,tok,messages(c),e['target']);assert torch.isfinite(value);losses.append(float(value.detach()));(value/len(indices)).backward();seen+=1
  norm=float(torch.nn.utils.clip_grad_norm_(params,1.,error_if_nonfinite=True));opt.step();assert all(torch.isfinite(p).all() for p in params)
  record=dict(step=step,epoch=epoch+1,examples_seen=seen,loss=sum(losses)/len(losses),learning_rate=lr,gradient_norm=norm,wall_seconds=round(time.monotonic()-start,2));losslog.append(record)
  with (PRIVATE/(arm+'-training-log.jsonl')).open('a') as f:f.write(canonical(record)+'\n')
  if step%10==0 or step==total:emit(arm+'-training',start,step,total,examples_seen=seen,loss=record['loss'])
  end_epoch=step==total or chunks[step][0]!=epoch
  if end_epoch:validation_loss(epoch+1)
  if step%50==0 or end_epoch:
   checkpoint=ARTIFACTS/(arm+f'-recovery-step-{step:06d}');checkpoint.mkdir(exist_ok=False);model.save_pretrained(checkpoint)
   torch.save(dict(optimizer=opt.state_dict(),completed_step=step,examples_seen=seen,torch_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all(),training_sha256=filehash(P/(f'D{cycle}.jsonl')),initial_fingerprints=initial,losslog=losslog,validationlog=validationlog),checkpoint/'training-state.pt')
   dump(checkpoint/'COMPLETE.json',dict(files={f.name:filehash(f) for f in checkpoint.iterdir() if f.is_file()}))
 model.eval();final=runtime.fingerprints(model,True);base_after=runtime.fingerprints(model,False);assert base_before==base_after;assert initial!=final;model.save_pretrained(finaldir);torch.save(opt.state_dict(),finaldir/'optimizer.pt')
 disk=load_file(str(finaldir/'adapter_model.safetensors'));set_peft_model_state_dict(model,disk);assert runtime.fingerprints(model,True)==final
 result=dict(arm=arm,recovery_used=recovery_used,parent_arm='M0' if cycle==1 else 'M1',base_unchanged=base_before==base_after,adapter_changed=initial!=final,trainable_parameters=sum(p.numel() for p in params),initial_adapter_files=artifact_manifest(initialdir),adapter_files=artifact_manifest(finaldir),initial_adapter_parameter_fingerprints=initial,adapter_parameter_fingerprints=final,epochs=2,optimizer_steps=total,examples_seen=seen,seed=runtime.SEED,optimizer={'name':'AdamW','learning_rate':1e-4,'betas':[.9,.999],'eps':1e-8,'weight_decay':.01,'foreach':False,'gradient_accumulation':8,'clip_norm':1.,'schedule':'5% ceiling warmup then linear decay to zero'},loss_curve=losslog,validation_loss=validationlog,finite_loss_gradient_and_parameter_checks=True,peak_allocated_bytes=torch.cuda.max_memory_allocated(),peak_reserved_bytes=torch.cuda.max_memory_reserved(),wall_seconds=round(time.monotonic()-start,2),sealed_test_calls=0,checkpoint_reload_exact=True,adapter_storage='Immutable local artifacts; hashes/configuration published, binary adapter and optimizer are not Git objects.')
 dump(P/(arm+'-artifact-freeze.json'),result)
 for folder in [initialdir,finaldir]:
  for f in folder.iterdir():
   if f.is_file():f.chmod(0o444)
 commit('Freeze '+arm+' learned adapter before sealed test inference')

def evaluate(cycle):
 model,tok=runtime.load();assert runtime.fingerprints(model,False)==json.loads((P/'M0-base-fingerprints.json').read_bytes());manifests=[]
 plan=[('M0','T1'),('M1','T1'),('M0','R1'),('M1','R1')] if cycle==1 else [('M1','T2'),('M2','T2'),('M2','T1'),('M2','R1'),('M1','R2'),('M2','R2')]
 for arm,name in plan:attach(model,arm);manifests.append(infer_set(model,tok,arm,name))
 freeze_raw('cycle'+str(cycle)+'-evaluation',manifests)
 scored={}
 for arm,name in plan:
  outputs=load_outputs(arm,name);scores=score(rows(D/(name+'.jsonl')),outputs);scored[arm,name]=scores
  public=[dict(s,final_answer=o['text'] if s['schema'] else None,raw_answer_sha256=sha(o['text']),prompt_sha256=o['prompt_sha256']) for s,o in zip(scores,outputs)];write_rows(P/(arm+'-'+name+'-scored.jsonl'),public)
 comp=compare(rows(D/(f'T{cycle}.jsonl')),scored[f'M{cycle-1}',f'T{cycle}'],scored[f'M{cycle}',f'T{cycle}'])
 training=json.loads((P/(f'M{cycle}-artifact-freeze.json')).read_bytes());leakage=audit_datasets(D,rows(P/(f'D{cycle}.jsonl')))
 if cycle==1:
  reg=regress(rows(D/'R1.jsonl'),scored['M0','R1'],scored['M1','R1']);result=dict(comparison=comp,regression=reg,leakage=leakage,gate=cycle1_gate(comp,reg,training,leakage))
 else:
  incumbent_t1=rows(P/'M1-T1-scored.jsonl');incumbent_r1=rows(P/'M1-R1-scored.jsonl');retention=compare(rows(D/'T1.jsonl'),incumbent_t1,scored['M2','T1']);regs=dict(R1=regress(rows(D/'R1.jsonl'),incumbent_r1,scored['M2','R1']),R2=regress(rows(D/'R2.jsonl'),scored['M1','R2'],scored['M2','R2']));result=dict(comparison=comp,retention=retention,regressions=regs,leakage=leakage,gate=cycle2_gate(comp,retention,regs,training,leakage))
 dump(P/(f'cycle{cycle}-results.json'),result);commit('Record frozen cycle '+str(cycle)+' evaluation and hard gate');print(json.dumps(result['gate']),flush=True)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['harvest','train','evaluate']);ap.add_argument('cycle',type=int,choices=[1,2]);a=ap.parse_args();frozen_preflight()
 if a.cycle==2:assert json.loads((P/'cycle1-results.json').read_bytes())['gate']['cycle2_authorized']
 {'harvest':harvest,'train':train,'evaluate':evaluate}[a.stage](a.cycle)
