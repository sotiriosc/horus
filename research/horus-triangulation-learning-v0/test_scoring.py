"""Independent hand-calculated prediction checks and synthetic scorer replay."""
import tempfile,json
from pathlib import Path
from common import *
import scoring
from campaign import collect
from receipts import Stream
from interface import ANALYSIS_SHAPE
from machines import outcomes
from study_stats import paired_signflip,paired_sign,mcnemar,holm
sensors=['a','b'];true=[dict(a=0,b=1),dict(a=1,b=0)]
r,p=scoring.score_prediction(canon(dict(predicted_observations=[dict(a=0,b=0),dict(a=1,b=1)])),sensors,true)
assert r==dict(valid=True,exact=False,correct_steps=0,steps=2,correct_bits=2,bits=4,confusion=dict(TN=1,FN=1,TP=1,FP=1))
for bad in ['{}','garbage',canon(dict(predicted_observations=[dict(a=False,b=1),dict(a=1,b=0)]))]:
 r,p=scoring.score_prediction(bad,sensors,true);assert p is None and r['correct_bits']==0 and r['confusion']==dict(invalid=4)
assert paired_signflip([1]*10)['p']==1/1024
assert paired_sign([2]*10)['p']==1/1024
assert mcnemar([False]*10,[True]*10)['p']==2/1024
assert holm(dict(a=.004,b=.03))==dict(a=.008,b=.03)
worlds=json.loads((ASSETS/'engineering/design-worlds.json').read_text())[:2]
for i,w in enumerate(worlds):
 w['id']=f'SYNTHETIC-{i}';w['cohort']='primary' if i==0 else 'control'
 if i:w['control_candidates']=[r['sequence'] for r in w['legal_probes'] if len(r['sequence'])==3][:8];w['target']=outcomes(w['root_ids'],w['control_candidates'][0])[-1]
 w['world_hash']=sha(w)
class Stub:
 def call(self,req):
  mode=req['mode'];r=dict(id=req['id'],mode=mode,semantic_messages_sha256=sha(req['messages']),prompt_tokens=1,generation_token_count=1,seconds=1)
  if mode=='analysis':r['text']=canon(ANALYSIS_SHAPE)
  elif mode=='choice':r.update(text=canon(dict(probe_id=req['legal_ids'][0])),probe_id=req['legal_ids'][0],finite_choice=dict(illegal_support_zero=True,all_generated_tokens_legal=True))
  else:
   data=json.loads(req['messages'][1]['content']);w=next(x for x in worlds if req['id'].startswith(x['id']+':'));probe=[w['actuators'].index(x) for x in data['query_probe']]
   r['text']=canon(dict(predicted_observations=[dict(zip(w['sensors'],row)) for row in outcomes(w['root_ids'],probe)]))
  return r
with tempfile.TemporaryDirectory() as d:
 d=Path(d);stream=Stream(d/'raw.jsonl',b'only-synthetic-test-key-material');collect(worlds,stream,Stub(),{'synthetic':True},progress=False)
 records={(e['kind'],e['record']['id']):e['record'] for e in stream.records}
 scoring.audit=lambda _: (dict(private_raw_sha256=filehash(stream.path)),worlds,records,dict(synthetic=True))
 for out in ['first','replay']:scoring.score('SYNTHETIC-NONSCIENTIFIC',d/out)
 for name in ['results.json','per-world-results.private.json','contribution-details.private.jsonl']:assert (d/'first'/name).read_bytes()==(d/'replay'/name).read_bytes(),name
 r=json.loads((d/'first/results.json').read_text())
 for a in ['P','A','T']:
  assert r['prediction']['short'][a]['exact']==5 and r['prediction']['long'][a]['exact']==3
  assert r['control'][a]['successes']==1 and r['control'][a]['mean_probes_successful']==1
  assert r['information']['primary'][a]['positive_information_repeats']==0
 assert r['information']['primary']['A']==r['information']['primary']['T']
 assert all(not g['supported'] for g in r['gates'].values())
 from report import render
 text=render(r,dict(seeds={},populations={},branch='SYNTHETIC'),dict(status='SYNTHETIC'),dict(status='SYNTHETIC'))
 assert '13. **' in text and 'STOP.' in text and '9600' not in text
 assert render(r,dict(seeds={},populations={},branch='SYNTHETIC'),dict(status='SYNTHETIC'),dict(status='SYNTHETIC'))==text
save(P/'scoring-tests.json',dict(status='PASS',scientific_model_calls=0,synthetic_worlds=2,stub_responses=120,hand_calculated_confusions=True,invalid_schema_zero_credit=True,exact_paired_tests=True,perfect_prediction_control_check=True,repeated_probe_information_zero=True,byte_identical_three_scoring_artifacts=True))
print('Independent scoring and synthetic end-to-end replay PASS',flush=True)
