"""Authenticated collection only: no correctness or contribution scoring.

An incomplete technical attempt may be resumed identically at most three times.
A durably completed response is never regenerated, regardless of quality.
"""
import argparse,os,subprocess,sys,time
from common import *
from machines import PASSIVE,outcomes,reset_observation
from interface import messages,parse_choice,parse_analysis,parse_prediction
from receipts import Stream,experiment
class Worker:
 def __init__(self):
  self.p=subprocess.Popen([sys.executable,'-u',str(P/'model_worker.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,bufsize=1)
  assert json.loads(self.p.stdout.readline())==dict(ready=True,adapter_sha256=ADAPTER_SHA)
 def call(self,request):
  self.p.stdin.write(canon(request)+'\n');self.p.stdin.flush();line=self.p.stdout.readline()
  assert line,'Technical interruption: worker returned no durable complete response'
  result=json.loads(line);assert result['id']==request['id'] and result['semantic_messages_sha256']==sha(request['messages'])
  return result
 def close(self):
  if self.p.poll() is None:self.p.stdin.close();self.p.wait(timeout=60)

def collect(worlds,stream,worker,authorization,progress=True):
 index={};visited=set()
 for e in stream.records:
  r=e['record'];key=(e['kind'],r['id']);assert key not in index;index[key]=r
 started=time.monotonic();fresh_calls=0
 def append(kind,r):
  key=kind,r['id'];assert key not in index;stream.append(kind,r);index[key]=r
 def exact(kind,r):
  visited.add((kind,r['id']))
  if (kind,r['id']) in index:assert index[kind,r['id']]==r
  else:append(kind,r)
 def call(ident,msgs,mode,legal=None,prediction_shape=None):
  nonlocal fresh_calls
  request=dict(id=ident,messages=msgs,mode=mode)
  if legal is not None:request['legal_ids']=[r['id'] for r in legal]
  if prediction_shape is not None:request['prediction_shape']=prediction_shape
  intent=dict(id=ident,request=request,semantic_messages_sha256=sha(msgs),authorization=authorization)
  exact('MODEL_REQUEST',intent)
  visited.add(('MODEL_RESPONSE',ident))
  if ('MODEL_RESPONSE',ident) in index:return index['MODEL_RESPONSE',ident]['result']
  attempts=[r for (k,_),r in index.items() if k=='MODEL_ATTEMPT' and r['logical_id']==ident]
  if attempts:
   last=max(attempts,key=lambda r:r['attempt'])
   exact('TECHNICAL_INTERRUPTION',dict(id=last['id'],logical_id=ident,attempt=last['attempt'],reason='No durable complete response. No experiment was executed from this attempt.'))
  number=len(attempts)+1;assert number<=3,'Technical attempt cap reached; STOP'
  append('MODEL_ATTEMPT',dict(id=f'{ident}:attempt:{number}',logical_id=ident,attempt=number,request_sha256=sha(request)))
  result=worker.call(request);assert result['semantic_messages_sha256']==sha(msgs)
  append('MODEL_RESPONSE',dict(id=ident,attempt=number,result=result));fresh_calls+=1
  if progress and fresh_calls%10==0:
   done=sum(k=='MODEL_RESPONSE' for k,_ in index);elapsed=time.monotonic()-started
   print(canon(dict(model_responses_complete=done,model_responses_planned=60*len(worlds),new_calls_this_process=fresh_calls,elapsed_seconds=round(elapsed,1),estimated_remaining_seconds=round(elapsed/fresh_calls*(60*len(worlds)-done),1))),flush=True)
  return result
 for w in worlds:
  ports={k:w[k] for k in ['actuators','sensors']};reset=dict(zip(w['sensors'],reset_observation(w['root_ids'])))
  legal=[dict(id=r['id'],sequence=[w['actuators'][a] for a in r['sequence']]) for r in w['legal_probes']]
  abstract={r['id']:tuple(r['sequence']) for r in w['legal_probes']};by_sequence={v:k for k,v in abstract.items()}
  target=dict(zip(w['sensors'],w['target'])) if w['cohort']=='control' else None
  for arm in ('P','A','T'):
   exact('ARM_STARTED',dict(id=f"{w['id']}:{arm}:start",world_id=w['id'],world_hash=w['world_hash'],arm=arm,ports=ports,reset_observation=reset,legal_probes=legal,target_before_discovery=target,authorization=authorization))
   ledger=[];previous_analysis=None
   for step in range(1,13):
    base=f"{w['id']}:{arm}:discovery:{step}";analysis=None
    if arm=='P':probe_id=by_sequence[PASSIVE[step-1]]
    else:
     if arm=='T':
      r=call(base+':analysis',messages(ports,reset,ledger,'analysis',legal=legal,previous_analysis=previous_analysis,target=target),'analysis')
      analysis=r['text'];previous_analysis=analysis
      try:parse_analysis(analysis);valid=True
      except (ValueError,AssertionError,TypeError,KeyError):valid=False
      exact('ANALYSIS_SCHEMA',dict(id=base+':analysis-schema',analysis_response_id=base+':analysis',valid=valid,authority='UNVERIFIED_MODEL_HYPOTHESIS'))
     r=call(base+':choice',messages(ports,reset,ledger,'choice',legal=legal,analysis=analysis,target=target),'choice',legal=legal)
     assert r['finite_choice']['illegal_support_zero'] and r['finite_choice']['all_generated_tokens_legal']
     probe_id=parse_choice(r['text'],legal);assert r['probe_id']==probe_id
    ap=abstract[probe_id];assert list(ap) not in w['reserved']
    probe=[w['actuators'][a] for a in ap];trace=[dict(zip(w['sensors'],row)) for row in outcomes(w['root_ids'],ap)]
    after=ledger+[dict(experiment=step,probe_id=probe_id,probe=probe,observations=trace)]
    r=dict(id=base,**experiment(w,arm,step,probe_id,probe,trace,ledger,after,reset,authorization,sha(analysis) if analysis is not None else None))
    exact('EXECUTED_PROBE',r);ledger=after
   if w['cohort']=='primary':
    for kind,queries in [('short',w['reserved']),('long',w['long_queries'])]:
     for q,ap in enumerate(queries):
      probe=[w['actuators'][a] for a in ap]
      assert all(e['probe']!=probe for e in ledger)
      call(f"{w['id']}:{arm}:{kind}:{q}",messages(ports,reset,ledger,'prediction',query=probe),'prediction',prediction_shape=dict(sensors=w['sensors'],length=len(ap)))
   else:
    predictions=[]
    for q,ap in enumerate(w['control_candidates']):
     probe=[w['actuators'][a] for a in ap]
     r=call(f"{w['id']}:{arm}:control-prediction:{q}",messages(ports,reset,ledger,'prediction',query=probe,target=target),'prediction',prediction_shape=dict(sensors=w['sensors'],length=3))
     try:predictions.append(parse_prediction(r['text'],w['sensors'],3))
     except (ValueError,AssertionError,TypeError,KeyError):predictions.append(None)
    def distance(i):return 5 if predictions[i] is None else sum(predictions[i][-1][s]!=target[s] for s in w['sensors'])
    order=sorted(range(8),key=lambda i:(distance(i),i));control_ledger=[]
    for step,q in enumerate(order[:4],1):
     ap=w['control_candidates'][q];probe_id=by_sequence[tuple(ap)];probe=[w['actuators'][a] for a in ap]
     trace=[dict(zip(w['sensors'],row)) for row in outcomes(w['root_ids'],ap)]
     after=control_ledger+[dict(experiment=step,probe_id=probe_id,probe=probe,observations=trace)]
     r=dict(id=f"{w['id']}:{arm}:control-execution:{step}",candidate_index=q,target=target,discovery_ledger_sha256=sha(ledger),**experiment(w,arm,step,probe_id,probe,trace,control_ledger,after,reset,authorization))
     exact('CONTROL_EXECUTION',r);control_ledger=after
     if trace[-1]==target:break
  if progress:print(canon(dict(world_complete=w['id'],elapsed_seconds=round(time.monotonic()-started,1))),flush=True)
 stream.verify()
 return visited

def main(world_commit):
 freeze=json.loads((P/'world-data-freeze.json').read_text());method=json.loads((P/'method-freeze.json').read_text())
 for name,digest in method['files_sha256'].items():assert filehash(P/name)==digest,name
 for name,digest in method['inherited_dependencies_sha256'].items():assert filehash(ROOT/name)==digest,name
 assert filehash(ASSETS/'private/worlds.jsonl')==freeze['private_worlds_sha256']
 assert subprocess.check_output(['git','show',world_commit+':research/horus-triangulation-learning-v0/world-data-freeze.json'],cwd=ROOT)==(P/'world-data-freeze.json').read_bytes()
 private=ASSETS/'private';key=private/'authority.key'
 if not key.exists():
  fd=os.open(key,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,'wb') as f:f.write(os.urandom(32));f.flush();os.fsync(f.fileno())
 stream=Stream(private/'campaign-signed.jsonl',key.read_bytes())
 authorization=dict(study='Horus Triangulation Learning v0',method_freeze_sha=freeze['method_freeze_sha'],world_freeze_sha=world_commit,adapter_sha256=ADAPTER_SHA,operation='Frozen inference-only discovery, sealed prediction and control; no training')
 worlds=[json.loads(x) for x in (private/'worlds.jsonl').read_text().splitlines()]
 worker=Worker()
 try:collect(worlds,stream,worker,authorization)
 finally:worker.close()
 save(P/'raw-freeze.json',dict(status='RAW_COMPLETE_UNSCORED',method_freeze_sha=freeze['method_freeze_sha'],world_freeze_sha=world_commit,private_worlds_sha256=filehash(private/'worlds.jsonl'),private_raw_sha256=filehash(stream.path),authenticated_records=len(stream.records),model_responses=sum(e['kind']=='MODEL_RESPONSE' for e in stream.records),correctness_scored=False,contribution_scored=False))
 print('Complete raw manifest ready. Commit before any correctness/contribution scoring.',flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--world-freeze',required=True);a=ap.parse_args();main(a.world_freeze)
