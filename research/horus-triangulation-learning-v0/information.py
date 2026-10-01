"""Exact external factored evaluator. No import in the model runtime/worker."""
import math
import numpy as np
from machines import PROBES,table,root_traces,observable_claims
class VersionSpace:
 def __init__(self,reset):
  r,self.t=table();self.h=[np.flatnonzero(r==v) for v in reset]
 @property
 def count(self):return math.prod(len(h) for h in self.h)
 @property
 def bits(self):return sum(math.log2(len(h)) for h in self.h)
 def values(self,probe):
  vector=root_traces(tuple(probe));parts=[np.bincount(vector[h],minlength=2**len(probe)).tolist() for h in self.h]
  ig=0.;expected=1.;worst=1
  for counts,h in zip(parts,self.h):
   n=len(h);ig+=sum(-(c/n)*math.log2(c/n) for c in counts if c)
   expected*=sum(c*c for c in counts)/n;worst*=max(counts)
  return dict(information_gain=ig,expected_posterior_count=expected,worst_case_count=worst,partition_counts_by_sensor=parts)
 def observe(self,probe,observations):
  vector=root_traces(tuple(probe))
  for s in range(4):
   encoded=sum(row[s]<<i for i,row in enumerate(observations));self.h[s]=self.h[s][vector[self.h[s]]==encoded]
   assert len(self.h[s])
 def identifies(self,probes):return all(all(len(set(root_traces(tuple(p))[h]))==1 for h in self.h) for p in probes)
 def claim_counts(self):
  onset,relation=observable_claims()
  return dict(temporal_onset_claims_identified=sum(len(set(onset[h,j]))==1 for h in self.h for j in range(onset.shape[1])),context_and_order_claims_identified=sum(len(set(relation[h,j]))==1 for h in self.h for j in range(relation.shape[1])))
 def query_uncertainty(self,probes):
  # Mean entropy of predicted query outcomes under uniform current candidates.
  return sum(self.values(p)['information_gain'] for p in probes)/len(probes)
 def decision(self,probe,allowed):
  values=[self.values(p) for p in allowed];i=allowed.index(tuple(probe));gains=[v['information_gain'] for v in values];g=gains[i]
  rank=1+sum(x>g+1e-12 for x in gains)+.5*(sum(abs(x-g)<=1e-12 for x in gains)-1)
  return dict(**values[i],best_information_gain=max(gains),regret=max(0.,max(gains)-g),midrank=rank,top_quartile=bool(g>1e-12 and rank<=len(allowed)/4),all_probe_values=values)
