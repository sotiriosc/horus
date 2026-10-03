"""Independent finite-world mathematics and public-only frontier tests."""
import itertools,math,random,time,copy
import numpy as np
from common import *
from machines import *
from information import VersionSpace
from interface import inquiry,messages
from qualify_interface import synthetic_analysis
from qualify_interface import fixture
from legal_choice import LegalChoiceTrie

def main():
 start=time.monotonic();roots=catalogue();reset,t=table();checks=0
 for i,row in enumerate(roots):
  vm=dsl.Circuit([row['root']]);assert vm.observation(vm.initial)[0]==reset[i]
  for j,p in enumerate(PROBES):
   state=vm.initial;trace=[]
   for a in p:state,o=vm.step(state,a);trace.append(o[0])
   assert sum(v<<k for k,v in enumerate(trace))==int(t[i,j]);checks+=1
 assert len(roots)==656 and len({r['behavior_sha256'] for r in roots})==656
 vs=VersionSpace([0]*4);vs.h=[h[:3] for h in vs.h];combos=list(itertools.product(*vs.h))
 for p in PROBES:
  vector=root_traces(p);bins={}
  for ids in combos:
   key=tuple(int(vector[i]) for i in ids);bins[key]=bins.get(key,0)+1
  n=len(combos);v=vs.values(p)
  assert abs(v['information_gain']+sum(c/n*math.log2(c/n) for c in bins.values()))<1e-10
  assert abs(v['expected_posterior_count']-sum(c*c for c in bins.values())/n)<1e-10
  assert v['worst_case_count']==max(bins.values())
 ports,reset,legal,history=fixture();mapping={x['id']:x['sequence'] for x in legal}
 for n in range(6):
  h=history[:n];state=inquiry(h,legal);assert set(state['tested_probe_ids']).isdisjoint(state['untried_probe_ids']);assert len(state['tested_probe_ids'])+len(state['untried_probe_ids'])==82
  for arm in ['B','D','T']:
   msg=messages(ports,reset,h,'choice',arm,legal=legal,analysis=synthetic_analysis(arm,h,legal,ports['sensors']) if arm!='B' and h else None);data=json.loads(msg[1]['content']);assert len(data['legal_probes'])==82 and data['authenticated_experiments']==h
   assert set(x['id'] for x in data['legal_probes'])>=set(state['tested_probe_ids'])
  if h:
   for arm in ['D','T']:
    reconstructed=messages(ports,reset,h,'analysis',arm,legal=legal);assert 'fresh_model_analysis' not in json.loads(reconstructed[1]['content'])
  preds=[messages(ports,reset,h,'prediction',a,query=['K7']*3) for a in ['B','D','T']];assert preds[0]==preds[1]==preds[2]
 from transformers import AutoTokenizer
 tok=AutoTokenizer.from_pretrained('/mnt/d/horus-research-assets/qwen3-14b-qlora-v0/231c69a380487f6c0e52d02dcf0d5456d1918201',local_files_only=True)
 trie=LegalChoiceTrie(tok,[x['id'] for x in legal]);assert set(trie.leaves())==set(trie.paths.values());assert all(trie.identify(path)==ident for ident,path in trie.paths.items())
 save(P/'design-tests.json',dict(status='PASS',model_calls=0,root_types=656,compiled_reference_comparisons=checks,explicit_joint_partition_checks=84,fresh_analysis_not_persisted=True,repeats_remain_legal=True,all82_legal_decoder_leaves_verified=True,prediction_prompts_identical=True,seconds=round(time.monotonic()-start,2)));print('Design, exact evaluator, frontier and language tests PASS',flush=True)
if __name__=='__main__':main()
