"""Raw-first collection. Imports simulator but NEVER information evaluator.

Worker is a separate process receiving only allowlisted semantic messages.
Every intent/response is fsynced. Interrupted ambiguous requests fail closed.
No correctness or information scoring occurs here. Control uses only A0 outputs.
"""
import argparse,os,subprocess,sys,time
from common import *
from machines import PROBES,PASSIVE,outcomes,reset_observation
from interface import messages,parse_probe
from receipts import Stream,experiment
from study_stats import control_order
class Worker:
 def __init__(self):
  self.p=subprocess.Popen([sys.executable,'-u',str(P/'model_worker.py'),'--serve'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,bufsize=1)
  ready=json.loads(self.p.stdout.readline());assert ready==dict(ready=True,adapter_sha256=ADAPTER_SHA)
 def call(self,ident,msgs):
  self.p.stdin.write(canon(dict(id=ident,messages=msgs))+'\n');self.p.stdin.flush()
  line=self.p.stdout.readline();assert line,'Worker exited before durable response; do not regenerate'
  result=json.loads(line);assert result['id']==ident and result['semantic_messages_sha256']==sha(msgs)
  return result
 def close(self):
  if self.p.poll() is None:self.p.stdin.close();self.p.wait(timeout=60)

def collect(worlds,stream,worker,authorization,progress=True):
 index={}
 for e in stream.records:
  r=e['record'];ident=r.get('id')
  if ident:
   key=(e['kind'],ident);assert key not in index;index[key]=r
 def append(kind,r):
  stream.append(kind,r)
  if r.get('id'):index[kind,r['id']]=r
 def call(ident,msgs):
  existing=index.get(('MODEL_RESPONSE',ident))
  if existing:
   assert index['MODEL_INTENT',ident]['messages']==msgs;return existing['result']
  assert ('MODEL_INTENT',ident) not in index,'Ambiguous interrupted call: STOP, no retry'
  append('MODEL_INTENT',dict(id=ident,messages=msgs,semantic_messages_sha256=sha(msgs),authorization=authorization))
  result=worker.call(ident,msgs)
  assert result['semantic_messages_sha256']==sha(msgs)
  append('MODEL_RESPONSE',dict(id=ident,result=result));return result
 start=time.monotonic();finished=0
 for w in worlds:
  ports={k:w[k] for k in ['actuators','sensors']};reset=dict(zip(w['sensors'],reset_observation(w['root_ids'])))
  reserved=tuple(tuple(p) for p in w['reserved']);abstract_allowed=tuple(p for p in PROBES if p not in reserved)
  allowed=[[w['actuators'][a] for a in p] for p in abstract_allowed]
  for arm in ('P','A'):
   ledger=[]
   for t in range(1,13):
    ident=f"{w['id']}:{arm}:discovery:{t}"
    if arm=='P':probe=[w['actuators'][a] for a in PASSIVE[t-1]]
    else:
     result=call(ident,messages(ports,reset,ledger,allowed=allowed))
     try:probe=parse_probe(result['text'],allowed)
     except (AssertionError,ValueError,TypeError,KeyError):
      append('PROTOCOL_FAILURE',dict(id=ident+':failure',reason='Invalid discovery selection; no repair or retry'))
      raise RuntimeError('Invalid discovery selection; scientific campaign terminated')
    ap=tuple(w['actuators'].index(a) for a in probe);assert ap in abstract_allowed
    trace=[dict(zip(w['sensors'],row)) for row in outcomes(w['root_ids'],ap)]
    after=ledger+[dict(experiment=t,probe=probe,observations=trace)]
    receipt=dict(id=ident,**experiment(w,arm,t,probe,trace,ledger,after,reset,authorization))
    if ('EXECUTED_PROBE',ident) in index:assert index['EXECUTED_PROBE',ident]==receipt
    else:append('EXECUTED_PROBE',receipt)
    ledger=after
   if w['cohort']=='primary':
    for q,probe in enumerate(reserved):
     query=[w['actuators'][a] for a in probe]
     assert all(x['probe']!=query for x in ledger)
     call(f"{w['id']}:{arm}:sealed:{q}",messages(ports,reset,ledger,query=query))
   else:
    target=dict(zip(w['sensors'],w['target']));predictions=[]
    for q,probe in enumerate(w['control_candidates']):
     result=call(f"{w['id']}:{arm}:control-prediction:{q}",messages(ports,reset,ledger,query=[w['actuators'][a] for a in probe],target=target))
     predictions.append(result['text'])
    order=control_order(predictions,w['sensors'],target);control_ledger=[]
    for step,q in enumerate(order[:4],1):
     ident=f"{w['id']}:{arm}:control-execution:{step}"
     probe=w['control_candidates'][q];trace=[dict(zip(w['sensors'],row)) for row in outcomes(w['root_ids'],probe)]
     named_probe=[w['actuators'][a] for a in probe]
     control_after=control_ledger+[dict(experiment=step,probe=named_probe,observations=trace)]
     r=dict(id=ident,candidate_index=q,control_probe_index=step,target=target,discovery_ledger_sha256=sha(ledger),**experiment(w,arm,step,named_probe,trace,control_ledger,control_after,reset,authorization))
     control_ledger=control_after
     if ('CONTROL_EXECUTION',ident) in index:assert index['CONTROL_EXECUTION',ident]==r
     else:append('CONTROL_EXECUTION',r)
     if trace[-1]==target:break
  finished+=1
  if progress:
   elapsed=time.monotonic()-start
   print(canon(dict(worlds_complete=finished,worlds_total=len(worlds),elapsed_seconds=round(elapsed,1),estimated_remaining_seconds=round(elapsed/finished*(len(worlds)-finished),1))),flush=True)
 stream.verify()

def main():
 freeze=json.loads((P/'world-data-freeze.json').read_text())
 for name,digest in json.loads((P/'method-freeze.json').read_text())['files_sha256'].items():assert filehash(P/name)==digest,name
 assert filehash(ASSETS/'private/worlds.jsonl')==freeze['private_worlds_sha256']
 method_sha=freeze['method_freeze_sha'];world_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True),'Clean committed worktree required'
 assert subprocess.check_output(['git','show',world_sha+':research/horus-active-causal-experimentation-v0/world-data-freeze.json'],cwd=ROOT)==(P/'world-data-freeze.json').read_bytes()
 private=ASSETS/'private';key=private/'authority.key'
 if not key.exists():
  fd=os.open(key,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,'wb') as f:f.write(os.urandom(32));f.flush();os.fsync(f.fileno())
 secret=key.read_bytes();assert len(secret)==32
 stream=Stream(private/'campaign-signed.jsonl',secret)
 authorization=dict(study='Horus Active Causal Experimentation v0',method_freeze_sha=method_sha,world_freeze_sha=world_sha,operation='frozen discovery and prediction only; no training',adapter_sha256=ADAPTER_SHA)
 worlds=[json.loads(x) for x in (private/'worlds.jsonl').read_text().splitlines()]
 worker=Worker()
 try:collect(worlds,stream,worker,authorization)
 finally:worker.close()
 save(P/'raw-freeze.json',dict(status='RAW_COMPLETE_UNSCORED',world_freeze_sha=world_sha,method_freeze_sha=method_sha,private_raw_sha256=filehash(stream.path),private_worlds_sha256=filehash(private/'worlds.jsonl'),authenticated_records=len(stream.records),model_response_count=sum(x['kind']=='MODEL_RESPONSE' for x in stream.records),correctness_scored=False,information_scored=False))
 print('Raw manifest ready; commit before running any scorer.',flush=True)
if __name__=='__main__':main()
