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
  if r['mode']=='analysis':
   context=json.loads(r['messages'][1]['content']);d['text']=canon(dict(supported_so_far=[],unresolved_discrepancies=[],current_questions=[dict(question='What trace will this measurement show?',probe_id=context['legal_probes'][0]['id'],sensor=next(iter(context['reset_observation'])))],limits_of_current_discrimination=['Synthetic evidence is limited.'],status='UNRESOLVED_BEYOND_CURRENT_DISCRIMINATION'))
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
 s=Stream(path,key);stub=Stub();collect(worlds,s,stub,dict(synthetic=True),progress=False);assert stub.n==62
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
 for a in ['A','B','O']:
  z=r['arms'][a];assert z['exact_repeats']==14 and z['unique_probe_sequences']==2 and z['prediction']['exact']==6
 assert r['arms']['A']==r['arms']['B']==r['arms']['O']
 assert not r['decision']['bookkeeping']['supported'] and not r['decision']['open_frontier']['supported']

 from report import render
 rendered=render(r,dict(synthetic=True),dict(status='PASS'),dict(status='PASS'))
 assert 'Ten requested answers' in rendered and 'NEITHER_INTERVENTION_CONFIRMED' in rendered
 assert r['question_counts']['generated_questions']==16
 assert r['question_counts']['already_observed_question_targets']==14
 assert r['question_counts']['unobserved_questions_later_answered_by_execution']==2
 assert r['question_counts'].get('questions_repeated_without_new_target_evidence',0)==0

save(P/'campaign-scoring-tests.json',dict(status='PASS',model_calls=0,synthetic_stub_responses=82,completed_response_reuse=True,technical_resume=True,corruption_rejected=True,byte_identical_collection_and_scoring=True,repeat_information_zero=True,perfect_prediction_check=True,question_execution_resolution_checked=True));print('Synthetic recovery, scoring replay and question resolution PASS',flush=True)
