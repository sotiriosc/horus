import itertools,math
import numpy as np
from common import *
from machines import table,root_traces
from information import VersionSpace
from contribution import target_information,target_uncertainty,structural,hb
vs=VersionSpace([0]*4);vs.h=[h[:3] for h in vs.h]
probe=(0,1,0);candidates=[(0,0,1),(1,2,3)];target=[0,1,0,1]
combos=list(itertools.product(*vs.h));values=root_traces(probe);gains=[]
for candidate in candidates:
 final=(root_traces(candidate)>>(len(candidate)-1))&1
 bins={};hits=0
 for ids in combos:
  trace=tuple(int(values[i]) for i in ids);hit=all(int(final[i])==target[s] for s,i in enumerate(ids));hits+=hit
  bins.setdefault(trace,[]).append(hit)
 expected=sum(len(xs)/len(combos)*float(hb(sum(xs)/len(xs))) for xs in bins.values())
 gains.append(float(hb(hits/len(combos)))-expected)
assert abs(target_information(vs,probe,candidates,target)-sum(gains)/len(gains))<1e-10
s=structural((0,1),[(1,)],[[0]*4,[1]*4],[[[0]*4]],1.)
assert s['relation_contrast'] and s['useful_controlled_contrast'] and not s['time_contrast']
s=structural((1,0),[(0,1)],[[0]*4,[0]*4],[[[0]*4,[1]*4]],0.)
assert s['time_contrast'] and not s['useful_controlled_contrast']
save(P/'contribution-tests.json',dict(status='PASS',target_mutual_information_matches_explicit_joint_enumeration=True,controlled_contrast_scope_checks=True,model_calls=0))
print('Direction mutual-information and scoped contrast tests PASS.')
