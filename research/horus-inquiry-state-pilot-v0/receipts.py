"""Study-local HMAC chain; preserved Horus verification, no model authority."""
import hmac,os,sys
from common import *
sys.path.insert(0,str(ROOT))
from horus.route_handoff_recovery import _authenticated_file
class Stream:
 def __init__(self,path,secret):
  self.path=Path(path);self.secret=secret;self.records=_authenticated_file(self.path,secret) if self.path.exists() else []
 def append(self,kind,record):
  signed=dict(sequence=len(self.records)+1,previous_sha256=sha(self.records[-1]) if self.records else None,kind=kind,record=json.loads(canon(record)))
  envelope=dict(signed,hmac_sha256=hmac.new(self.secret,canon(signed).encode(),'sha256').hexdigest())
  fd=os.open(self.path,os.O_WRONLY|os.O_APPEND|os.O_CREAT,0o600)
  with os.fdopen(fd,'a') as f:f.write(canon(envelope)+'\n');f.flush();os.fsync(f.fileno())
  self.records.append(envelope);return envelope
 def verify(self):
  assert _authenticated_file(self.path,self.secret)==self.records;return self.records

def experiment(world,arm,index,probe_id,probe,observations,before,after,reset,authorization,analysis_sha=None):
 expected=dict(experiment=index,probe_id=probe_id,probe=probe,observations=observations)
 assert after==before+[expected]
 return dict(world_id=world['id'],world_hash=world['world_hash'],arm=arm,experiment_index=index,model_identity='Qwen/Qwen3-14B@231c69a380487f6c0e52d02dcf0d5456d1918201+A0',adapter_sha256=ADAPTER_SHA,probe_id=probe_id,selected_probe=probe,complete_observed_trace=observations,previous_ledger_sha256=sha(before),resulting_ledger_sha256=sha(after),reset_state_sha256=sha(dict(world_hash=world['world_hash'],inputs=[0]*4,registers_zero=True,reset_observation=reset)),provisional_analysis_sha256=analysis_sha,authorization=authorization,executed=True,correctness=None,contribution=None)
