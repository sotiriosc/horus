"""Synthetic durable recovery, corruption rejection, scoring and gate boundaries."""
import tempfile,copy
from pathlib import Path
from common import *
from campaign import collect
from receipts import Stream
from machines import outcomes
from qualify_interface import synthetic_analysis
import scoring

worlds=json.loads((ASSETS/'engineering/design-worlds.json').read_text())[:2]
for i,w in enumerate(worlds):w['id']=f'SYNTHETIC-{i}';w['world_hash']=sha(w)
class Stub:
 def __init__(self,fail=None,forbid=False):self.n=0;self.fail=fail;self.forbid=forbid
 def call(self,r):
  assert not self.forbid;self.n+=1
  if self.fail is not None and self.n>self.fail:raise OSError('Synthetic technical interruption')
  d=dict(id=r['id'],mode=r['mode'],semantic_messages_sha256=sha(r['messages']),prompt_tokens=1,generation_token_count=1,seconds=1)
  if r['mode']=='analysis':
   shape=r['analysis_shape'];d['text']=synthetic_analysis(shape['arm'],shape['ledger'],shape['legal'],shape['sensors'])
  elif r['mode']=='choice':d.update(probe_id=r['legal_ids'][0],text=canon(dict(probe_id=r['legal_ids'][0])),finite_choice=dict(all_generated_tokens_legal=True,illegal_support_zero=True))
  else:
   context=json.loads(r['messages'][1]['content']);w=next(w for w in worlds if r['id'].startswith(w['id']+':'));probe=[w['actuators'].index(a) for a in context['query_probe']]
   d['text']=canon(dict(predicted_observations=[dict(zip(w['sensors'],row)) for row in outcomes(w['root_ids'],probe)]))
  return d
with tempfile.TemporaryDirectory() as d:
 d=Path(d);path=d/'raw.jsonl';key=b'only-synthetic-evidence-test';s=Stream(path,key)
 try:collect(worlds,s,Stub(fail=20),dict(synthetic=True),progress=False)
 except OSError:pass
 else:raise AssertionError('Interruption test did not fire')
 assert sum(e['kind']=='MODEL_RESPONSE' for e in s.records)==20
 s=Stream(path,key);stub=Stub();collect(worlds,s,stub,dict(synthetic=True),progress=False);assert stub.n==48
 before=path.read_bytes();collect(worlds,Stream(path,key),Stub(forbid=True),dict(synthetic=True),progress=False);assert path.read_bytes()==before
 corrupt=d/'corrupt.jsonl';corrupt.write_bytes(before.replace(b'ARM_STARTED',b'ARM_TAMPERD',1))
 try:Stream(corrupt,key)
 except Exception:pass
 else:raise AssertionError('Tampering accepted')
 records={(e['kind'],e['record']['id']):e['record'] for e in s.records}
 scoring.audit=lambda _: (dict(private_raw_sha256=filehash(path)),worlds,records,dict(synthetic=True))
 for folder in ['first','replay']:scoring.score('SYNTHETIC',d/folder)
 for name in ['results.json','per-world-results.private.json','contribution-details.private.jsonl']:assert (d/'first'/name).read_bytes()==(d/'replay'/name).read_bytes()
 r=json.loads((d/'first/results.json').read_text())
 for a in ['B','D','T']:
  z=r['arms'][a];assert z['exact_repeats']==10 and z['unique_probe_sequences']==2 and z['prediction']['exact']==4
 assert r['arms']['B']==r['arms']['D']==r['arms']['T']
 assert not r['decision']['recommend_scale_up']

 from report import render
 report=render(r,dict(synthetic=True),dict(status='PASS'),dict(status='PASS'))
 assert 'Ten requested answers' in report and 'DELTA_PREDICTION_PILOT_NO_SCALE_UP' in report
 for arm in ['D','T']:
  m=r['prediction_mechanism'][arm];assert m['counts']['predictions_generated']==10 and m['counts']['never_tested']==10
  assert m['prediction_testing_experiments']==0 and m['counts'].get('predictions_eventually_tested',0)==0
 assert sum(e['kind']=='NONAUTHORITATIVE_PREDICTION' for e in s.records)==20

save(P/'campaign-scoring-tests.json',dict(status='PASS',model_calls=0,synthetic_stub_responses=68,completed_response_reuse=True,technical_resume=True,corruption_rejected=True,byte_identical_collection_and_scoring=True,repeat_information_zero=True,perfect_prediction_check=True,unexecuted_predictions_never_scored=True,all_prediction_receipts_sequenced=True));print('Synthetic recovery, raw replay and unexecuted-prediction boundary PASS',flush=True)
