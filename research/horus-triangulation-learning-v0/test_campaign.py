"""Synthetic collection, hypothesis boundaries and technical recovery tests."""
import json,tempfile
from pathlib import Path
from common import *
from campaign import collect
from receipts import Stream
from interface import ANALYSIS_SHAPE
from machines import outcomes
worlds=json.loads((ASSETS/'engineering/design-worlds.json').read_text())[:2]
for i,w in enumerate(worlds):
 w['id']=f'SYNTHETIC-{i}';w['cohort']='primary' if i==0 else 'control'
 if i:
  w['control_candidates']=[r['sequence'] for r in w['legal_probes'] if len(r['sequence'])==3][:8]
  w['target']=outcomes(w['root_ids'],w['control_candidates'][0])[-1]
 w['world_hash']=sha(w)
class Stub:
 def __init__(self,fail_after=None,forbid=False):self.calls=0;self.fail_after=fail_after;self.forbid=forbid
 def call(self,request):
  assert not self.forbid,'Durable scientific response regenerated'
  self.calls+=1
  if self.fail_after is not None and self.calls>self.fail_after:raise OSError('Synthetic interrupted attempt')
  mode=request['mode'];r=dict(id=request['id'],mode=mode,semantic_messages_sha256=sha(request['messages']),synthetic=True)
  if mode=='analysis':r['text']=canon(ANALYSIS_SHAPE)
  elif mode=='choice':
   r.update(text=canon(dict(probe_id=request['legal_ids'][0])),probe_id=request['legal_ids'][0],finite_choice=dict(illegal_support_zero=True,all_generated_tokens_legal=True))
  else:
   shape=request['prediction_shape'];r['text']=canon(dict(predicted_observations=[dict.fromkeys(shape['sensors'],0) for _ in range(shape['length'])]))
  return r
with tempfile.TemporaryDirectory() as d:
 path=Path(d)/'signed.jsonl';secret=b'synthetic-study-key-material-0000';stream=Stream(path,secret)
 try:collect(worlds,stream,Stub(fail_after=30),{'synthetic':True},progress=False)
 except OSError:pass
 else:raise AssertionError('Technical interruption not exercised')
 assert sum(e['kind']=='MODEL_RESPONSE' for e in stream.records)==30
 resumed=Stream(path,secret);stub=Stub();collect(worlds,resumed,stub,{'synthetic':True},progress=False)
 assert stub.calls==90 and sum(e['kind']=='MODEL_RESPONSE' for e in resumed.records)==120
 assert sum(e['kind']=='TECHNICAL_INTERRUPTION' for e in resumed.records)==1
 before=path.read_bytes();collect(worlds,Stream(path,secret),Stub(forbid=True),{'synthetic':True},progress=False);assert path.read_bytes()==before
 for e in resumed.records:
  if e['kind']=='ARM_STARTED' and e['record']['world_id']=='SYNTHETIC-1':assert e['record']['target_before_discovery']==dict(zip(worlds[1]['sensors'],worlds[1]['target']))
  if e['kind']=='EXECUTED_PROBE':
   r=e['record'];w=next(w for w in worlds if w['id']==r['world_id']);ap=[w['actuators'].index(x) for x in r['selected_probe']];assert ap not in w['reserved']
  if e['kind']=='MODEL_REQUEST':
   req=e['record']['request'];data=json.loads(req['messages'][1]['content'].split('\n',1)[0])
   if req['mode']=='prediction':assert 'triangulation_analysis' not in data and 'previous_model_hypothesis' not in data
 record_count=len(resumed.records)
save(P/'campaign-tests.json',dict(status='PASS',synthetic_stub_complete_responses=120,model_calls=0,authenticated_records=record_count,completed_responses_never_regenerated=True,incomplete_technical_attempt_resumed_identically=True,byte_identical_durable_replay=True,target_exposed_before_control_discovery_in_all_arms=True,reserved_probes_never_executed=True,prediction_uses_only_authoritative_ledger=True))
print('Synthetic P/A/T campaign, protected hypotheses, target disclosure and technical recovery PASS.')
