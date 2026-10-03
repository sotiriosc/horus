"""Random complete grammar paths validate; no model or hidden outcomes."""
import random
from common import *
from analysis_format import AnalysisFormat
from qualify_interface import fixture
from transformers import AutoTokenizer

tok=AutoTokenizer.from_pretrained('/mnt/d/horus-research-assets/qwen3-14b-qlora-v0/231c69a380487f6c0e52d02dcf0d5456d1918201',local_files_only=True);ports,reset,legal,ledger=fixture();rng=random.Random(100404);maximum=0;counts={'PREDICTION':0,'INSUFFICIENT_DELTA':0}
for arm in ['D','T']:
 for n in [1,5]:
  for iteration in range(16):
   grammar=AnalysisFormat(tok,arm,ledger[:n],legal,ports['sensors']);path=[]
   while len(path)<grammar.max_tokens:
    permitted=grammar.allowed(path);assert permitted
    token=rng.choice(permitted);path.append(token)
    if token==tok.eos_token_id:break
   assert path[-1]==tok.eos_token_id
   text=grammar.validate(path);x=json.loads(text);counts[x['status']]+=1;maximum=max(maximum,len(path))
   if x['status']=='PREDICTION':
    assert x['prediction']['untested_probe_id'] not in {e['probe_id'] for e in ledger[:n]}
    if arm=='T':assert x['prediction']['predicted_trace']!=x['alternative_trace']
assert all(counts.values())
save(P/'analysis-language-tests.json',dict(status='PASS',model_calls=0,random_complete_paths=64,maximum_tokens=maximum,status_counts=counts,public_only_inputs=True,proposed_targets_unexecuted=True,alternative_distinctness=True));print('Analysis language random-path tests PASS',maximum,counts)
