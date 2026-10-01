"""Post-campaign evidence audit without model inference or gate changes."""
import sys,json,hashlib,subprocess
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[1];A=Path('/mnt/d/horus-research-assets/qwen3-14b-qlora-v0');sys.path.insert(0,str(P))
from data import rows,dump,messages
from transformers import AutoTokenizer
from runtime import BASE,MAX_NEW,CONTEXT,prompt

def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=R)
tok=AutoTokenizer.from_pretrained(BASE,local_files_only=True,padding_side='left');tok.pad_token=tok.eos_token
registered={};counts={}
for manifest in sorted(P.glob('*-raw-freeze.json')):
 rel=str(manifest.relative_to(R));assert git('show','HEAD:'+rel)==manifest.read_bytes()
 for rec in json.loads(manifest.read_bytes())['files']:
  path=A/'study-private'/rec['private_file'];assert digest(path)==rec['sha256'];cs=rows(P/'materialized'/(rec['dataset']+'.jsonl'));outs=rows(path);assert len(cs)==len(outs)==rec['count']
  for c,o in zip(cs,outs):
   assert o['id']==c['id'] and o['arm']==rec['arm'] and o['dataset']==rec['dataset']
   assert o['messages']==messages(c)
   rendered=prompt(tok,o['messages']);assert o['rendered_prompt']==rendered
   assert o['prompt_sha256']==hashlib.sha256(rendered.encode()).hexdigest()
   tokens=tok.encode(rendered,add_special_tokens=False);assert o['prompt_tokens']==len(tokens);assert len(tokens)+MAX_NEW<=CONTEXT
   assert tok.decode(o['generated_token_ids'],skip_special_tokens=True)==o['text']
  registered[path.name]=dict(sha256=rec['sha256'],bytes=path.stat().st_size,count=len(outs),committed_manifest=rel)
  counts[path.name]=len(outs)
private_files={p.name:dict(sha256=digest(p),bytes=p.stat().st_size) for p in sorted((A/'study-private').iterdir()) if p.is_file()}
assert {n for n in private_files if n.endswith('-raw.jsonl')}==set(registered)
checkpoints={}
for marker in sorted((A/'study-adapters').glob('M*-recovery-step-*/COMPLETE.json')):
 files=json.loads(marker.read_bytes())['files']
 for name,sha in files.items():assert digest(marker.parent/name)==sha
 checkpoints[marker.parent.name]=dict(marker_sha256=digest(marker),files_verified=len(files))
head=git('rev-parse','HEAD').decode().strip()
tracked=git('ls-tree','-r','--name-only','HEAD').decode().splitlines()
for path in tracked:
 assert not path.startswith(('study-private/','study-adapters/'))
 if path.startswith('research/qwen-error-driven-qlora-learning-v0/'):
  assert Path(path).suffix not in ['.pt','.bin','.safetensors','.gguf','.db','.sqlite','.sqlite3']
result=dict(status='PASS',audited_scientific_head=head,registered_raw_endpoints=sum(counts.values()),raw_files=registered,private_file_inventory=private_files,complete_recovery_checkpoints=checkpoints,exact_frozen_messages_and_tokenizer_rendering=True,output_text_matches_saved_generated_tokens=True,raw_files_all_covered_by_committed_hash_manifests=True,scope='Only synthetic scientific inputs and strict two-field parsed answers are public. Raw model output files, adapter/optimizer binaries, and recovery states remain in local persistent research storage. No model inference or candidate selection occurred in this audit.')
dump(P/'private-evidence-audit.json',result)
print(json.dumps(dict(status='PASS',raw_endpoints=result['registered_raw_endpoints'],private_files=len(private_files),checkpoints=len(checkpoints))))
