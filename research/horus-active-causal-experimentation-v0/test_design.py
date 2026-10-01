"""Independent mathematical, simulator, schema and sealing checks. No A0 calls."""
import itertools,math,time,json
import numpy as np
from common import *
from machines import *
from information import VersionSpace
from design import reserve,qualify
from interface import parse_probe,parse_prediction,synthetic_fixtures

def run():
 start=time.monotonic();roots=catalogue();r,t=table();n=0
 for i,root in enumerate(roots):
  vm=dsl.Circuit([root]);assert vm.observation(vm.initial)[0]==r[i]
  for j,p in enumerate(PROBES):
   state=vm.initial;obs=[]
   for a in p:state,o=vm.step(state,a);obs.append(o[0])
   assert tuple(obs)==trace(root,p)
   assert sum(v<<k for k,v in enumerate(obs))==int(t[i,j]);n+=1
 # Independently enumerate a small full Cartesian candidate class and partition.
 vs=VersionSpace([0]*4);vs.h=[h[:3] for h in vs.h]
 combos=list(itertools.product(*vs.h))
 for j in range(84):
  bins={}
  for ids in combos:
   key=tuple(int(t[i,j]) for i in ids);bins[key]=bins.get(key,0)+1
  counts=list(bins.values());z=len(combos);v=vs.values(j)
  ig=-sum(c/z*math.log2(c/z) for c in counts)
  assert abs(v['information_gain']-ig)<1e-10
  assert abs(v['expected_posterior_count']-sum(c*c for c in counts)/z)<1e-10
  assert v['worst_case_count']==max(counts)
 # Sealing is stronger than exact equality: no allowed discovery trace contains
 # an entire reserved trace as a prefix from the same reset.
 import random
 for seed in range(100):
  sealed=reserve(random.Random(seed));allowed=tuple(p for p in PROBES if p not in sealed)
  assert len(sealed)==5 and len(set(sealed))==5 and len(allowed)==79
  assert set(PASSIVE)<=set(allowed)
  assert all(not (len(p)>=len(q) and p[:len(q)]==q) for p in allowed for q in sealed)
  assert len(set(pattern(p) for p in sealed))==5
 # Exact deterministic repeats always have zero IG after first execution.
 vs=VersionSpace([0]*4);ids=[int(h[-1]) for h in vs.h];p=(0,1,0)
 vs.observe(p,outcomes(ids,p));assert vs.values(PROBES.index(p))['information_gain']==0
 valid_probe='{"probe":["K7"]}';assert parse_probe(valid_probe,[['K7']])==['K7']
 for text in ('{"probe":["bad"]}','{"probe":["K7"],"extra":0}','{"probe":"K7"}'):
  try:parse_probe(text,[['K7']])
  except (AssertionError,ValueError,TypeError):pass
  else:raise AssertionError('Malformed probe accepted')
 try:parse_prediction('{"predicted_observations":[{"s":true}]}',['s'],1)
 except AssertionError:pass
 else:raise AssertionError('Boolean accepted as integer')
 report=dict(status='PASS',root_types=len(roots),compiled_reference_probe_comparisons=n,independently_enumerated_joint_partition_checks=84,sealed_prefix_checks_worlds=100,deterministic_repeat_information_zero=True,strict_schema_checks=True,seconds=round(time.monotonic()-start,2),model_calls=0)
 save(P/'design-tests.json',report);print(canon(report))
if __name__=='__main__':run()
