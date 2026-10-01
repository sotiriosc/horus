"""Append-only study receipts verified by the preserved Horus HMAC verifier."""
import hmac,os,sys
from common import *
sys.path.insert(0,str(ROOT))
from horus.route_handoff_recovery import _authenticated_file
from horus.live import _canonical
assert _canonical({'a':1,'b':[0,1]})==canon({'a':1,'b':[0,1]})
class Stream:
 def __init__(self,path,secret):
  self.path=Path(path);self.secret=secret
  self.records=_authenticated_file(self.path,secret) if self.path.exists() else []
 def append(self,kind,record):
  payload=json.loads(canon(record))
  signed=dict(sequence=len(self.records)+1,previous_sha256=sha(self.records[-1]) if self.records else None,kind=kind,record=payload)
  envelope=dict(signed,hmac_sha256=hmac.new(self.secret,canon(signed).encode(),'sha256').hexdigest())
  fd=os.open(self.path,os.O_WRONLY|os.O_APPEND|os.O_CREAT,0o600)
  with os.fdopen(fd,'a') as f:f.write(canon(envelope)+'\n');f.flush();os.fsync(f.fileno())
  self.records.append(envelope);return envelope
 def verify(self):
  records=_authenticated_file(self.path,self.secret);assert records==self.records;return records

def experiment(world,arm,index,probe,observations,before,after,reset,authorization):
 assert after==before+[dict(experiment=index,probe=probe,observations=observations)]
 return dict(world_id=world['id'],world_hash=world['world_hash'],arm=arm,experiment_index=index,model_identity='Qwen/Qwen3-14B@231c69a380487f6c0e52d02dcf0d5456d1918201+A0',adapter_sha256=ADAPTER_SHA,previous_ledger_sha256=sha(before),selected_probe=probe,reset_state_sha256=sha(dict(world_hash=world['world_hash'],input_bits=[0]*4,all_registers_zero=True,reset_observation=reset)),complete_observed_trace=observations,resulting_ledger_sha256=sha(after),authorization=authorization,executed=True,correctness=None,information_value=None)
