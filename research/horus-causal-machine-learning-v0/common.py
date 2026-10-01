import hashlib,json,os,subprocess
from pathlib import Path
ROOT=Path(os.environ.get('HORUS_CAUSAL_ROOT','/home/sotiriosc/horus-causal-machine-learning-v0'))
P=ROOT/'research/horus-causal-machine-learning-v0'
OLD=ROOT/'research/qwen-error-driven-qlora-learning-v0'
ASSETS=Path('/mnt/d/horus-research-assets/causal-machine-v0')
PRIVATE=ASSETS/'private'
ADAPTERS=ASSETS/'adapters'
C0_FILE=Path('/mnt/d/horus-research-assets/qwen3-14b-qlora-v0/study-adapters/M1/adapter_model.safetensors')
C0_SHA='ba679e10cac31b5b17c8589c0740d74ac98c2db1882d7edd39419cb9110a0b01'
STUDY_ID='horus-causal-machine-learning-v0'
SEED=20261001
PREFIX='research/horus-causal-machine-learning-v0'
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def sha(x):return hashlib.sha256(canon(x).encode()).hexdigest()
def filehash(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def rows(p):return [json.loads(x) for x in Path(p).read_text().splitlines()]
def write_rows(p,x):Path(p).write_text(''.join(canon(r)+'\n' for r in x))
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def commit(message):
 subprocess.run(['git','add','--',PREFIX],cwd=ROOT,check=True);subprocess.run(['git','commit','-m',message],cwd=ROOT,check=True);return git('rev-parse','HEAD')
