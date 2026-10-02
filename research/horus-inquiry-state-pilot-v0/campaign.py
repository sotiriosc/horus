"""Raw-first six-probe matched A/B/C collection; no scientific scores."""
import argparse,os,subprocess,sys,time
from common import *
from machines import outcomes,reset_observation
from interface import messages,parse_choice
from receipts import Stream,experiment
class Worker:
 def __init__(self):
  self.p=subprocess.Popen([sys.executable,'-u',str(P/'model_worker.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,bufsize=1)
  assert json.loads(self.p.stdout.readline())==dict(ready=True,adapter_sha256=ADAPTER_SHA)
 def call(self,request):
  self.p.stdin.write(canon(request)+'\n');self.p.stdin.flush();line=self.p.stdout.readline();assert line,'Worker returned no complete response'
  r=json.loads(line);assert r['id']==request['id'] and r['semantic_messages_sha256']==sha(request['messages']);return r
 def close(self):
  if self.p.poll() is None:self.p.stdin.close();self.p.wait(timeout=60)

def collect(worlds,stream,worker,authorization,progress=True):
 index={};visited=set()
 for e in stream.records:
  key=(e['kind'],e['record']['id']);assert key not in index;index[key]=e['record']
 start=time.monotonic();fresh=0
 def append(kind,r):
  key=kind,r['id'];assert key not in index;stream.append(kind,r);index[key]=r
 def exact(kind,r):
  visited.add((kind,r['id']))
  if (kind,r['id']) in index:assert index[kind,r['id']]==r
  else:append(kind,r)
 def call(ident,msg,mode,legal=None,shape=None):
  nonlocal fresh
  req=dict(id=ident,messages=msg,mode=mode)
  if legal is not None:req['legal_ids']=[r['id'] for r in legal]
  if shape is not None:req['prediction_shape']=shape
  exact('MODEL_REQUEST',dict(id=ident,request=req,semantic_messages_sha256=sha(msg),authorization=authorization));visited.add(('MODEL_RESPONSE',ident))
  if ('MODEL_RESPONSE',ident) in index:return index['MODEL_RESPONSE',ident]['result']
  attempts=[r for (kind,_),r in index.items() if kind=='MODEL_ATTEMPT' and r['logical_id']==ident]
  if attempts:
   last=max(attempts,key=lambda r:r['attempt']);exact('TECHNICAL_INTERRUPTION',dict(id=last['id'],logical_id=ident,attempt=last['attempt'],reason='No durable complete response. No experiment was executed from this attempt.'))
  n=len(attempts)+1;assert n<=3,'Frozen technical-attempt cap reached'
  append('MODEL_ATTEMPT',dict(id=f'{ident}:attempt:{n}',logical_id=ident,attempt=n,request_sha256=sha(req)))
  r=worker.call(req);assert r['semantic_messages_sha256']==sha(msg);append('MODEL_RESPONSE',dict(id=ident,attempt=n,result=r));fresh+=1
  if progress and fresh%8==0:
   done=sum(k=='MODEL_RESPONSE' for k,_ in index);elapsed=time.monotonic()-start
   print(canon(dict(model_responses_complete=done,planned=24*len(worlds),new_calls=fresh,elapsed_seconds=round(elapsed,1),estimated_remaining_seconds=round(elapsed/fresh*(24*len(worlds)-done),1))),flush=True)
  return r
 for w in worlds:
  ports={k:w[k] for k in ['actuators','sensors']};reset=dict(zip(w['sensors'],reset_observation(w['root_ids'])))
  legal=[dict(id=r['id'],sequence=[w['actuators'][a] for a in r['sequence']]) for r in w['legal_probes']];mapping={r['id']:tuple(r['sequence']) for r in w['legal_probes']}
  for arm in ['A','B','C']:
   exact('ARM_STARTED',dict(id=f"{w['id']}:{arm}:start",world_id=w['id'],world_hash=w['world_hash'],arm=arm,ports=ports,reset_observation=reset,legal_probes=legal,authorization=authorization));ledger=[]
   for step in range(1,7):
    base=f"{w['id']}:{arm}:discovery:{step}";r=call(base+':choice',messages(ports,reset,ledger,'choice',arm,legal=legal),'choice',legal=legal)
    assert r['finite_choice']['illegal_support_zero'] and r['finite_choice']['all_generated_tokens_legal']
    ident=parse_choice(r['text'],legal);assert ident==r['probe_id'];ap=mapping[ident];assert list(ap) not in w['reserved']
    probe=[w['actuators'][a] for a in ap];trace=[dict(zip(w['sensors'],row)) for row in outcomes(w['root_ids'],ap)];after=ledger+[dict(experiment=step,probe_id=ident,probe=probe,observations=trace)]
    exact('EXECUTED_PROBE',dict(id=base,**experiment(w,arm,step,ident,probe,trace,ledger,after,reset,authorization)));ledger=after
   for q,ap in enumerate(w['reserved']):
    probe=[w['actuators'][a] for a in ap];assert all(e['probe']!=probe for e in ledger)
    call(f"{w['id']}:{arm}:prediction:{q}",messages(ports,reset,ledger,'prediction',arm,query=probe),'prediction',shape=dict(sensors=w['sensors'],length=3))
  if progress:print(canon(dict(world_complete=w['id'],elapsed_seconds=round(time.monotonic()-start,1))),flush=True)
 stream.verify();return visited

def main(world_sha):
 method=json.loads((P/'method-freeze.json').read_text());freeze=json.loads((P/'world-data-freeze.json').read_text())
 for name,digest in method['files_sha256'].items():assert filehash(P/name)==digest,name
 for name,digest in method['inherited_dependencies_sha256'].items():assert filehash(ROOT/name)==digest,name
 assert filehash(ASSETS/'private/worlds.jsonl')==freeze['private_worlds_sha256']
 assert subprocess.check_output(['git','show',world_sha+':research/horus-inquiry-state-pilot-v0/world-data-freeze.json'],cwd=ROOT)==(P/'world-data-freeze.json').read_bytes()
 private=ASSETS/'private';key=private/'authority.key'
 if not key.exists():
  fd=os.open(key,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,'wb') as f:f.write(os.urandom(32));f.flush();os.fsync(f.fileno())
 stream=Stream(private/'campaign-signed.jsonl',key.read_bytes())
 auth=dict(study='Horus Inquiry State Pilot v0',method_freeze_sha=freeze['method_freeze_sha'],world_freeze_sha=world_sha,adapter_sha256=ADAPTER_SHA,operation='Frozen six-probe inference-only A/B/C pilot; no training')
 timing=private/'collection-timing.json'
 if not timing.exists():save(timing,dict(start_unix=time.time(),start_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())))
 started=json.loads(timing.read_text())
 worlds=[json.loads(x) for x in (private/'worlds.jsonl').read_text().splitlines()];worker=Worker()
 try:collect(worlds,stream,worker,auth)
 finally:worker.close()
 save(P/'raw-freeze.json',dict(status='RAW_COMPLETE_UNSCORED',method_freeze_sha=freeze['method_freeze_sha'],world_freeze_sha=world_sha,private_worlds_sha256=filehash(private/'worlds.jsonl'),private_raw_sha256=filehash(stream.path),collection_started_utc=started['start_utc'],collection_finished_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),collection_wall_seconds=round(time.time()-started['start_unix'],3),authenticated_records=len(stream.records),model_responses=sum(e['kind']=='MODEL_RESPONSE' for e in stream.records),correctness_scored=False,contribution_scored=False))
 print('All384 complete; raw manifest must be committed before scoring.',flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--world-freeze',required=True);args=ap.parse_args();main(args.world_freeze)
