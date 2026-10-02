"""Prospectively specified exact paired tests; no model calls."""
import math
from collections import defaultdict

def paired_signflip(differences):
 assert all(type(d) is int for d in differences)
 observed=sum(differences);dp={0:1};n=0
 for d in differences:
  if not d:continue
  n+=1;next_dp=defaultdict(int)
  for s,ways in dp.items():next_dp[s+d]+=ways;next_dp[s-d]+=ways
  dp=next_dp
 return dict(observed_sum=observed,nonzero_worlds=n,p=sum(ways for s,ways in dp.items() if s>=observed)/2**n)
def paired_sign(differences):
 win=sum(d>1e-12 for d in differences);loss=sum(d<-1e-12 for d in differences);n=win+loss
 return dict(positive=win,negative=loss,ties=len(differences)-n,p=sum(math.comb(n,i) for i in range(win,n+1))/2**n if n else 1.)
def mcnemar(base,treatment):
 win=sum(t and not b for b,t in zip(base,treatment));loss=sum(b and not t for b,t in zip(base,treatment));n=win+loss
 return dict(treatment_only=win,baseline_only=loss,p=min(1.,2*sum(math.comb(n,i) for i in range(max(win,loss),n+1))/2**n) if n else 1.)
def holm(pvalues):
 order=sorted(pvalues,key=lambda k:(pvalues[k],k));result={};previous=0.
 for i,k in enumerate(order):previous=max(previous,min(1.,(len(order)-i)*pvalues[k]));result[k]=previous
 return result
