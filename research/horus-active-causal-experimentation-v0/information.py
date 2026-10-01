"""Exact factored version-space evaluator, never imported by model worker.

Joint trace partitions are Cartesian products of per-sensor partitions. Counts,
expected posterior size, entropy, and worst-case size factor exactly. No hidden
world is used to score a candidate probe; only the executed ledger filters H.
"""
import math
import numpy as np
from machines import PROBES,table
class VersionSpace:
 def __init__(self,reset):
  r,self.t=table();self.h=[np.flatnonzero(r==v) for v in reset]
 @property
 def count(self):return math.prod(len(h) for h in self.h)
 @property
 def bits(self):return sum(math.log2(len(h)) for h in self.h)
 def partitions(self,j):
  return [[int(v) for v in np.bincount(self.t[h,j],minlength=8)] for h in self.h]
 def values(self,j):
  parts=self.partitions(j);ig=0.;expected=1.;worst=1
  for counts,h in zip(parts,self.h):
   n=len(h);ig+=sum(-(c/n)*math.log2(c/n) for c in counts if c)
   expected*=sum(c*c for c in counts)/n;worst*=max(counts)
  return dict(information_gain=ig,expected_posterior_count=expected,worst_case_count=worst,partition_counts_by_sensor=parts)
 def observe(self,probe,observations):
  j=PROBES.index(tuple(probe))
  for s in range(4):
   encoded=sum(row[s]<<k for k,row in enumerate(observations))
   self.h[s]=self.h[s][self.t[self.h[s],j]==encoded]
   assert len(self.h[s]),'Executed evidence contradicts declared family'
 def identifies(self,probes):
  return all(all(len(set(self.t[h,PROBES.index(tuple(p))]))==1 for h in self.h) for p in probes)
 def decision(self,probe,allowed):
  values=[self.values(PROBES.index(tuple(p))) for p in allowed]
  selected=allowed.index(tuple(probe));gains=[v['information_gain'] for v in values]
  g=gains[selected];best=max(gains)
  # Midrank makes all-zero or ubiquitous ties ineligible for top quartile.
  rank=1+sum(x>g+1e-12 for x in gains)+.5*(sum(abs(x-g)<=1e-12 for x in gains)-1)
  return dict(**values[selected],best_information_gain=best,regret=max(0.,best-g),midrank=rank,top_quartile=bool(g>1e-12 and rank<=len(allowed)/4),all_probe_values=values)
