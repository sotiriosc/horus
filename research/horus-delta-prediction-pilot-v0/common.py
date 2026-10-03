"""Study constants and canonical serialization; no model or hidden-world loading."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
OLD=P.parent/'horus-causal-machine-learning-v0'
ACTIVE=P.parent/'horus-active-causal-experimentation-v0'
TEMPORAL=P.parent/'qwen-error-driven-qlora-learning-v0'
TRIAG=P.parent/'horus-triangulation-learning-v0'
ASSETS=Path('/mnt/d/horus-research-assets/delta-prediction-pilot-v0')
BASE_SHA='e3aefc6ea33395f7b8fd6dd0d57f7917d774c4ca'
ADAPTER=Path('/mnt/d/horus-research-assets/qwen3-14b-qlora-v0/study-adapters/M1/adapter_model.safetensors')
ADAPTER_SHA='ba679e10cac31b5b17c8589c0740d74ac98c2db1882d7edd39419cb9110a0b01'
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True)
def sha(x):return hashlib.sha256(canon(x).encode()).hexdigest()
def filehash(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(path,obj):Path(path).write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')

PILOT=P.parent/'horus-inquiry-state-pilot-v0'

CONFIRM=P.parent/'horus-inquiry-state-confirmatory-v0'
