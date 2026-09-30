import json,subprocess,hashlib
from pathlib import Path
from common import P,BASE,sha
PRIVATE=Path('/tmp/horus-qwen-role-grounded-temporal-reduction-v0-private')
def git(*args):return subprocess.check_output(['git',*args],cwd=P,text=True).strip()
def inheritance():
 baseline=json.loads((P/'preservation-baseline.json').read_bytes());paths=git('diff','--name-only',BASE,'HEAD').splitlines()
 assert all(x.startswith('research/qwen-role-grounded-temporal-reduction-v0/') for x in paths)
 current=dict(line.split(' ',1) for line in git('for-each-ref','--format=%(refname) %(objectname)','refs/heads').splitlines())
 old=dict(line.split(' ',1) for line in baseline['local_heads'].splitlines())
 for ref,head in old.items():
  if ref!='refs/heads/research/qwen-role-grounded-temporal-reduction-v0':assert current[ref]==head
 return dict(status='PASS',inherited_files=len(baseline['inherited_files']),prior_local_refs=len(old)-1)
def runtime_identity():
 expected={'/tmp/horus-development-runtime-assets/model/Qwen3-14B-Q4_K_M.gguf':'500a8806e85ee9c83f3ae08420295592451379b4f8cf2d0f41c15dffeb6b81f0','/tmp/horus-development-runtime-assets/engine/llama-b11242/llama-server':'778f1b3fbbb76e921af1d7f25a5b61d82859962dcd18c71ce86ab84d7f4884e5'}
 for n,want in expected.items():
  h=hashlib.sha256()
  with open(n,'rb') as f:
   for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
  assert h.hexdigest()==want,n
 return dict(status='PASS',sha256=expected)
def frozen_transport(commit):
 assert git('rev-parse','HEAD')==commit
 assert not git('status','--porcelain','--untracked-files=no')
 hashes=json.loads((P/'case-freeze.json').read_bytes())['sha256']
 for n,want in hashes.items():assert sha((P/n).read_bytes())==want,n
 return dict(status='PASS',case_freeze_commit=commit,checked_files=len(hashes))
