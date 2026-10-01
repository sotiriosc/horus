"""Prospective prerequisite: reproduce published M1 in its unchanged inference stack."""
import hashlib,importlib.metadata,json,os,subprocess,sys,time
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[1];OLD=R/'research/qwen-error-driven-qlora-learning-v0';sys.path.insert(0,str(OLD))
import runtime
from data import messages,rows,canonical
from analysis import score
from peft import set_peft_model_state_dict,get_peft_model_state_dict
from safetensors.torch import load_file
import torch
A=Path('/mnt/d/horus-research-assets/causal-machine-v0');PRIVATE=A/'private'
SOURCE=Path('/mnt/d/horus-research-assets/qwen3-14b-qlora-v0/study-adapters/M1/adapter_model.safetensors')
EXPECTED='ba679e10cac31b5b17c8589c0740d74ac98c2db1882d7edd39419cb9110a0b01'
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=R,text=True).strip()
def commit(msg):
 subprocess.run(['git','add','--',str(P.relative_to(R))],cwd=R,check=True);subprocess.run(['git','commit','-m',msg],cwd=R,check=True)
def dump(name,x):(P/name).write_text(json.dumps(x,indent=2)+'\n')
if __name__=='__main__':
 start=time.monotonic();assert git('status','--porcelain')=='';assert SOURCE.exists() and digest(SOURCE)==EXPECTED
 frozen=json.loads((OLD/'data-freeze.json').read_bytes())
 for n,want in frozen['files'].items():assert digest(OLD/n)==want
 provenance=json.loads((OLD/'upstream-provenance.json').read_bytes())
 for n,want in provenance['safetensor_hashes'].items():assert digest(runtime.BASE/n)==want
 q=json.loads((OLD/'engineering-qualification.json').read_bytes());assert sorted(subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True).splitlines())==sorted(q['package_lock'])
 model,tok=runtime.load();base=runtime.fingerprints(model,False);assert base==json.loads((OLD/'M0-base-fingerprints.json').read_bytes())
 source=load_file(str(SOURCE));set_peft_model_state_dict(model,source);before=runtime.fingerprints(model,True);prior=json.loads((OLD/'M1-artifact-freeze.json').read_bytes());assert before==prior['adapter_parameter_fingerprints']
 saved=A/'C0-roundtrip';saved.mkdir(exist_ok=True);model.save_pretrained(saved);disk=load_file(str(saved/'adapter_model.safetensors'));assert source.keys()==disk.keys() and all(torch.equal(source[k],disk[k]) for k in source);set_peft_model_state_dict(model,disk);assert runtime.fingerprints(model,True)==before
 cs=rows(OLD/'materialized/T1.jsonl');raw=PRIVATE/'C0-prior-T1-raw.jsonl';existing=rows(raw) if raw.exists() else [];assert len(existing)%4==0
 assert [o['id'] for o in existing]==[c['id'] for c in cs[:len(existing)]]
 for c,o in zip(cs,existing):assert o['messages']==messages(c)
 inference_start=time.monotonic()
 with raw.open('a') as f:
  for i in range(len(existing),len(cs),4):
   chunk=cs[i:i+4];requests=[messages(c) for c in chunk];outputs=runtime.infer(model,tok,requests,True)
   for c,msg,o in zip(chunk,requests,outputs):f.write(canonical(dict(id=c['id'],messages=msg,rendered_prompt=runtime.prompt(tok,msg),**o))+'\n')
   f.flush();os.fsync(f.fileno())
   if i%40==0 or i+4==len(cs):
    n=i+len(chunk)-len(existing);elapsed=time.monotonic()-inference_start;print(json.dumps(dict(stage='C0-prior-T1-reproduction',done=i+len(chunk),total=len(cs),elapsed_seconds=round(elapsed,1),estimated_remaining_seconds=round(elapsed/n*(len(cs)-i-len(chunk)),1))),flush=True)
 raw.chmod(0o444);assert runtime.fingerprints(model,False)==base and runtime.fingerprints(model,True)==before
 dump('incumbent-reproduction-raw-freeze.json',dict(private_file=raw.name,sha256=digest(raw),count=len(cs),scoring_performed=False,protocol_commit=git('log','-1','--format=%H','--',str((P/'incumbent-verification-plan.json').relative_to(R))),adapter_sha256=EXPECTED,base_matches_published_fingerprints=True,adapter_load_save_tensor_fidelity=True,roundtrip_adapter_sha256=digest(saved/'adapter_model.safetensors')));commit('Freeze incumbent reproduction outputs before scoring')
 scored=score(cs,rows(raw));passed=sum(x['joint'] for x in scored)==540 and all(x['schema'] for x in scored)
 dump('incumbent-verification.json',dict(status='PASS' if passed else 'STOP',base_repository='Qwen/Qwen3-14B',base_revision=provenance['hf_revision'],adapter_sha256=EXPECTED,base_shards_rehashed=len(provenance['safetensor_hashes']),published_frozen_files_verified=len(frozen['files']),exact_package_lock_unchanged=True,adapter_load_save_tensor_fidelity=True,base_fingerprints_match=True,temporal_joint_correct=sum(x['joint'] for x in scored),temporal_total=len(scored),schema_valid=sum(x['schema'] for x in scored),raw_freeze_commit=git('rev-parse','HEAD'),wall_seconds=round(time.monotonic()-start,2),causal_scientific_calls=0));commit('Record unchanged incumbent identity and temporal reproduction');print(json.dumps(dict(status='PASS' if passed else 'STOP',joint=sum(x['joint'] for x in scored),total=len(cs))),flush=True)
 if not passed:sys.exit(42)
