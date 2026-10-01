"""Zero-model end-to-end receipt and recovery tests on engineering fixtures."""
import tempfile,copy
from pathlib import Path
from common import *
from campaign import collect
from receipts import Stream
from machines import PROBES,outcomes
from interface import strict_json
worlds=json.loads((ASSETS/'engineering/design-worlds.json').read_text())[:2]
for i,w in enumerate(worlds):
 w['id']=f'SYNTHETIC-{i}';w['cohort']='primary' if i==0 else 'control';w['world_hash']=sha(w)
 if i:
  w['control_candidates']=[list(p) for p in PROBES if len(p)==3 and list(p) not in w['reserved']][:8]
  w['target']=outcomes(w['root_ids'],w['control_candidates'][0])[-1]
class Stub:
 def __init__(self,fail=False):self.calls=0;self.fail=fail
 def call(self,ident,msgs):
  assert not self.fail,'Completed durable response was regenerated'
  self.calls+=1;x=json.loads(msgs[1]['content'])
  if 'allowed_probes' in x:
   p=x['allowed_probes'][x['experiment_number']-1];result=dict(probe=p)
  else:result=dict(predicted_observations=[dict.fromkeys(x['sensors'],0) for _ in x['query_probe']])
  return dict(id=ident,text=canon(result),semantic_messages_sha256=sha(msgs),synthetic=True)
with tempfile.TemporaryDirectory() as d:
 p=Path(d)/'raw.jsonl';stream=Stream(p,b'synthetic-authentication-key-0000');stub=Stub()
 collect(worlds,stream,stub,{'synthetic':True},progress=False)
 assert stub.calls==50
 first=p.read_bytes();records=len(stream.records)
 collect(worlds,Stream(p,stream.secret),Stub(fail=True),{'synthetic':True},progress=False)
 assert p.read_bytes()==first
 for e in stream.records:
  if e['kind']=='EXECUTED_PROBE':
   w=next(w for w in worlds if w['id']==e['record']['world_id'])
   abstract=[w['actuators'].index(a) for a in e['record']['selected_probe']]
   assert abstract not in w['reserved']
 # A persisted intent without a complete response must never be reissued.
 broken=Stream(Path(d)/'ambiguous.jsonl',stream.secret)
 broken.append('MODEL_INTENT',dict(id='SYNTHETIC-0:P:sealed:0'))
 try:collect(worlds,broken,Stub(fail=True),{'synthetic':True},progress=False)
 except AssertionError as e:assert 'Ambiguous interrupted call' in str(e)
 else:raise AssertionError('Ambiguous call was retried')
save(P/'campaign-tests.json',dict(status='PASS',synthetic_stub_calls=50,model_calls=0,authenticated_records=records,byte_identical_durable_resume=True,ambiguous_request_fails_closed=True,reserved_discovery_exclusion=True,full_ledger_reconstruction=True,control_receipts_bind_ledgers=True))
print('Synthetic collection, signed receipts, byte-identical resume and ambiguous-request stop PASS.')
