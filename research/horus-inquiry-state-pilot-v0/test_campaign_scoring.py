"""Synthetic durable recovery, corruption rejection, scoring and gate boundaries."""
import tempfile,copy
from pathlib import Path
from common import *
from campaign import collect
from receipts import Stream
from machines import outcomes
import scoring

worlds=json.loads((ASSETS/'engineering/design-worlds.json').read_text())[:2]
for i,w in enumerate(worlds):w['id']=f'SYNTHETIC-{i}';w['world_hash']=sha(w)
class Stub:
 def __init__(self,fail=None,forbid=False):self.n=0;self.fail=fail;self.forbid=forbid
 def call(self,r):
  assert not self.forbid;self.n+=1
  if self.fail is not None and self.n>self.fail:raise OSError('Synthetic technical interruption')
  d=dict(id=r['id'],mode=r['mode'],semantic_messages_sha256=sha(r['messages']),prompt_tokens=1,generation_token_count=1,seconds=1)
  if r['mode']=='choice':d.update(probe_id=r['legal_ids'][0],text=canon(dict(probe_id=r['legal_ids'][0])),finite_choice=dict(all_generated_tokens_legal=True,illegal_support_zero=True))
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
 s=Stream(path,key);stub=Stub();collect(worlds,s,stub,dict(synthetic=True),progress=False);assert stub.n==28
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
 for a in ['A','B','C']:
  z=r['arms'][a];assert z['exact_repeats']==10 and z['unique_probe_sequences']==2 and z['prediction']['exact']==4
 assert r['arms']['A']==r['arms']['B']==r['arms']['C']
 assert not r['decision']['recommend_scale_up']
 from report import render
 report=render(r,dict(seeds={},populations={}),dict(status='PASS'),dict(status='PASS'))
 assert 'Eight requested answers' in report and 'INQUIRY_STATE_PILOT_NO_SCALE_UP' in report
# Hand-created boundary evidence tests: all conditions must pass; never posthoc alternatives.
def passing():return dict(repeat_ratio=.5,zero_information_ratio=.75,zero_information_reduction=4,median_paired_information_advantage_bits=1.,information_wins=10,useful_contrast_mean_advantage=.5,short_exact_difference=-1,short_bit_accuracy_difference=-.02,repeat_reduction=4)
comp={k:passing() for k in ['B-A','C-A','C-B']};arms={'A':{'exact_repeats':8}}
assert scoring.gates(comp,arms)['recommended_arm']=='C'
for key,bad in [('repeat_ratio',.51),('zero_information_ratio',.76),('zero_information_reduction',3),('median_paired_information_advantage_bits',.99),('information_wins',9),('useful_contrast_mean_advantage',.49),('short_exact_difference',-2),('short_bit_accuracy_difference',-.021)]:
 c=copy.deepcopy(comp);c['B-A'][key]=bad;assert not scoring.gates(c,arms)['screening']['B-A']['passed'],key
c=copy.deepcopy(comp);c['C-B']['information_wins']=9;assert scoring.gates(c,arms)['recommended_arm']=='B'
assert not scoring.gates(comp,arms,False)['recommend_scale_up']
assert not scoring.gates(comp,{'A':{'exact_repeats':0}})['recommend_scale_up']
save(P/'campaign-scoring-tests.json',dict(status='PASS',model_calls=0,synthetic_stub_responses=48,completed_response_reuse=True,technical_resume=True,corruption_rejected=True,byte_identical_collection_and_scoring=True,repeat_information_zero=True,perfect_prediction_check=True,each_numeric_gate_boundary_checked=True,arm_selection_rule_checked=True));print('Synthetic campaign, scoring/replay and gate boundary tests PASS',flush=True)
