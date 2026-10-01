"""Prospective exact tests and deterministic control ranking; no inference."""
import math
from interface import parse_prediction

def binomial_upper(k,n):return sum(math.comb(n,i) for i in range(k,n+1))/2**n if n else 1.
def mcnemar(passive,active):
 assert len(passive)==len(active)
 wins=sum(a and not p for p,a in zip(passive,active));losses=sum(p and not a for p,a in zip(passive,active));n=wins+losses
 return dict(active_only=wins,passive_only=losses,p=min(1.,2*binomial_upper(max(wins,losses),n)) if n else 1.)
def paired_sign(differences):
 wins=sum(d>1e-12 for d in differences);losses=sum(d<-1e-12 for d in differences)
 return dict(positive=wins,negative=losses,ties=len(differences)-wins-losses,p=binomial_upper(wins,wins+losses))
def control_order(predictions,sensors,target):
 def distance(text):
  try:o=parse_prediction(text,sensors,3)[-1]
  except (AssertionError,ValueError,TypeError,KeyError):return 5
  return sum(o[s]!=target[s] for s in sensors)
 return sorted(range(len(predictions)),key=lambda i:(distance(predictions[i]),i))
