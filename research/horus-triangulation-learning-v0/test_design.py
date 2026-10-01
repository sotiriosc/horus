"""Zero-model mathematical, language, simulator and sealing qualification."""
import itertools,math,random,time,json
import numpy as np
from common import *
from machines import *
from information import VersionSpace
from legal_choice import LegalChoiceTrie
from prediction_format import PredictionFormat
from design import reserve
from transformers import AutoTokenizer

def main():
 start=time.monotonic();roots=catalogue();reset,t=table();checks=0
 for i,row in enumerate(roots):
  vm=dsl.Circuit([row['root']]);assert vm.observation(vm.initial)[0]==reset[i]
  for j,p in enumerate(PROBES):
   state=vm.initial;trace=[]
   for a in p:state,o=vm.step(state,a);trace.append(o[0])
   assert sum(v<<k for k,v in enumerate(trace))==int(t[i,j]);checks+=1
  for p in [(0,1,2,3),(3,2,1,0,3),(0,0,1,2,3,0)]:
   state=vm.initial;trace=[]
   for a in p:state,o=vm.step(state,a);trace.append(o[0])
   assert sum(v<<k for k,v in enumerate(trace))==int(root_traces(p)[i]);checks+=1
 # Find and retain short-equal, full-behavior-distinct roots in the declared class.
 short_groups={}
 for i in range(len(roots)):short_groups.setdefault((int(reset[i]),tuple(t[i])),[]).append(i)
 aliased=sum(len(v)>1 for v in short_groups.values())
 assert len({r['behavior_sha256'] for r in roots})==len(roots)
 vs=VersionSpace([0]*4);vs.h=[h[:3] for h in vs.h];combos=list(itertools.product(*vs.h))
 for p in PROBES:
  vector=root_traces(p);bins={}
  for ids in combos:
   k=tuple(int(vector[i]) for i in ids);bins[k]=bins.get(k,0)+1
  z=len(combos);cs=list(bins.values());v=vs.values(p)
  assert abs(v['information_gain']+sum(c/z*math.log2(c/z) for c in cs))<1e-10
  assert abs(v['expected_posterior_count']-sum(c*c for c in cs)/z)<1e-10
  assert v['worst_case_count']==max(cs)
 for seed in range(100):
  reserved=reserve(random.Random(seed));allowed=[p for p in PROBES if p not in reserved]
  assert len(reserved)==5 and len(allowed)==79 and set(PASSIVE)<=set(allowed)
  assert all(not(len(p)>=len(q) and p[:len(q)]==q) for p in allowed for q in reserved)
 tok=AutoTokenizer.from_pretrained('/mnt/d/horus-research-assets/qwen3-14b-qlora-v0/231c69a380487f6c0e52d02dcf0d5456d1918201',local_files_only=True)
 for ids in [[f'P{i:03d}' for i in range(79)],['P002','P078'],['P009']]:
  trie=LegalChoiceTrie(tok,ids);assert set(trie.leaves())==set(trie.paths.values())
  assert all(trie.identify(p)==k for k,p in trie.paths.items())
 for n in range(1,7):
  grammar=PredictionFormat(tok,['V9','R3','Z8','M6'],n)
  for seed in range(20):
   rng=random.Random(seed);bits=[rng.randrange(2) for _ in range(4*n)]
   text=grammar.render(bits);tokens=tok.encode(text,add_special_tokens=False)+[tok.eos_token_id]
   assert grammar.validate(tokens)==text
 report=dict(status='PASS',root_types=len(roots),short_observation_alias_groups_retained=aliased,complete_behavior_hashes_unique=True,compiled_reference_trace_comparisons=checks,explicit_cartesian_partition_checks=84,sealed_prefix_world_checks=100,finite_choice_language_checks=True,prediction_product_grammar_checks=120,seconds=round(time.monotonic()-start,2),model_calls=0)
 save(P/'design-tests.json',report);print(canon(report))
if __name__=='__main__':main()
