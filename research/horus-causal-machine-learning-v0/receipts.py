"""Study-local writer interoperable with Horus's preserved HMAC chain verifier.

Execution records defer correctness until a committed raw freeze. Separate
signed scoring attestations bind correctness to immutable execution receipts.
Only a matched verified bundle can be admitted as causal training evidence.
"""
import hmac,os,sys
from datetime import datetime,timezone
from pathlib import Path
from common import *
sys.path.insert(0,str(ROOT))
from horus.route_handoff_recovery import _authenticated_file
from horus.live import _canonical
assert _canonical({'a':1,'b':[0,1]})==canon({'a':1,'b':[0,1]})
def key(create=False):
 path=PRIVATE/'authority.key'
 if create and not path.exists():
  fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,'wb') as f:f.write(os.urandom(32));f.flush();os.fsync(f.fileno())
 value=path.read_bytes();assert len(value)==32;return value
class Stream:
 def __init__(self,path,secret):
  self.path=Path(path);self.secret=secret;self.records=_authenticated_file(self.path,secret) if self.path.exists() else []
 def append(self,kind,record):
  record=json.loads(canon(record)) # snapshot caller-owned mutable request histories
  signed=dict(sequence=len(self.records)+1,previous_sha256=sha(self.records[-1]) if self.records else None,kind=kind,record=record)
  envelope=dict(signed,hmac_sha256=hmac.new(self.secret,canon(signed).encode(),'sha256').hexdigest())
  with self.path.open('a') as f:f.write(canon(envelope)+'\n');f.flush();os.fsync(f.fileno())
  self.records.append(envelope);return envelope
 def verify(self):
  verified=_authenticated_file(self.path,self.secret);assert verified==self.records;return verified

def authorization(phase,arm,adapter_sha,world_freeze):
 return dict(study_id=STUDY_ID,phase=phase,model_identity='Qwen/Qwen3-14B@231c69a380487f6c0e52d02dcf0d5456d1918201+'+arm,adapter_sha256=adapter_sha,world_freeze_commit=world_freeze,method_freeze_commit=json.loads((P/'world-data-freeze.json').read_bytes())['method_freeze_sha'],allowed_operation='predict_then_execute_frozen_transition',training_eligible_pools=['H1','V1'] if phase=='harvest1' else ['H2','V2'] if phase=='harvest2' else [],authorized_by='User-requested prospective study and frozen conditional gates')
def execution(case,arm,adapter_sha,visible,action,prediction,observation,step,auth_hash):
 return dict(study_id=STUDY_ID,world_id=case['id'],world_hash=case['world_hash'],cycle=case['cycle'],pool=case['pool'],step=step,incumbent=arm,adapter_sha256=adapter_sha,history_sha256=sha(visible['history']),request_sha256=sha(visible),executed_action=action,prediction_sha256=sha(prediction),actual_next_observation=observation,executed=True,timestamp=datetime.now(timezone.utc).isoformat(),authorization_sha256=auth_hash,correctness=None,scoring_state='DEFERRED_UNTIL_RAW_FREEZE')
def validate_bundle(exec_env,score_env,case,visible,prediction,authorization_record):
 # Callers first authenticate BOTH complete chains with the preserved verifier.
 assert exec_env['kind']=='EXECUTED_TRANSITION' and score_env['kind']=='SCORING_ATTESTATION'
 r=exec_env['record'];s=score_env['record'];a=authorization_record
 assert r['study_id']==STUDY_ID==s['study_id'] and r['world_id']==case['id'] and r['world_hash']==case['world_hash']
 assert r['cycle']==case['cycle'] and r['pool']==case['pool'] and r['pool'] in a['training_eligible_pools']
 assert r['executed'] is True and r['correctness'] is None and r['scoring_state']=='DEFERRED_UNTIL_RAW_FREEZE'
 assert r['incumbent']==('C0' if case['cycle']==1 else 'C1') and r['adapter_sha256']==a['adapter_sha256']
 assert r['authorization_sha256']==sha(a) and r['history_sha256']==sha(visible['history']) and r['request_sha256']==sha(visible)
 assert r['executed_action']==visible['candidate_action'] and r['prediction_sha256']==sha(prediction)
 assert s['execution_receipt_sha256']==sha(exec_env) and s['prediction_sha256']==r['prediction_sha256'] and s['actual_next_observation']==r['actual_next_observation']
 assert len(s['raw_freeze_commit'])==40 and type(s['exact_correct']) is bool
 from scoring import parse
 actual=r['actual_next_observation'];assert set(actual)==set(visible['sensors']) and all(type(v) is int and v in (0,1) for v in actual.values())
 parsed=parse(prediction,visible['sensors']);bits={name:parsed is not None and parsed[name]==actual[name] for name in visible['sensors']}
 assert s['field_correctness']==bits and s['exact_correct']==all(bits.values())
 return r['actual_next_observation']
