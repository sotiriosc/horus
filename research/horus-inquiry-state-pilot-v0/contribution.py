"""Independent post-raw contribution metrics; never model-visible."""
import itertools,math,re
import numpy as np
from machines import root_traces
from interface import parse_analysis

def structural(probe,prior_probes,observations,prior_observations,realized_bits):
 p=tuple(probe);time=False;relation=False;controlled=False;changed=False;comparisons=[]
 for q,trace in zip(prior_probes,prior_observations):
  q=tuple(q)
  if p==q:continue
  short,long=(p,q) if len(p)<len(q) else (q,p)
  extension=len(long)==len(short)+1 and (long[1:]==short or long[:-1]==short)
  repeated_extension=len(long)==len(short)+1 and long[:-1]==short and long[-1]==short[-1]
  swap=False
  if len(p)==len(q):
   for i in range(len(p)-1):
    x=list(p);x[i],x[i+1]=x[i+1],x[i]
    if tuple(x)==q:swap=True
  relation|=extension;time|=swap or repeated_extension;controlled|=extension or swap
  if extension or swap:
   delta=observations[-1]!=trace[-1];changed|=delta
   comparisons.append(dict(prior_probe=list(q),extension=extension,adjacent_swap=swap,repetition_extension=repeated_extension,final_observation_changed=delta))
 return dict(time_contrast=time,relation_contrast=relation,controlled_contrast=controlled,useful_controlled_contrast=bool(controlled and changed and realized_bits>1e-12),contrasts=comparisons)

def hb(p):
 p=np.asarray(p,dtype=float);out=np.zeros_like(p)
 mask=(p>0)&(p<1);x=p[mask];out[mask]=-x*np.log2(x)-(1-x)*np.log2(1-x)
 return out

def target_uncertainty(vs,candidates,target):
 entropies=[];resolved=0
 for candidate in candidates:
  v=(root_traces(tuple(candidate))>>(len(candidate)-1))&1
  p=math.prod(float(np.mean(v[h]==target[s])) for s,h in enumerate(vs.h))
  entropies.append(float(hb(p)));resolved+=p==0 or p==1
 return dict(mean_target_entropy=sum(entropies)/len(entropies),resolved_target_propositions=resolved)

def target_information(vs,probe,candidates,target):
 observed=root_traces(tuple(probe));support=2**len(probe);weights=[]
 for h in vs.h:weights.append(np.bincount(observed[h],minlength=support)/len(h))
 joint=weights[0][:,None,None,None]*weights[1][None,:,None,None]*weights[2][None,None,:,None]*weights[3][None,None,None,:]
 total=0.
 for candidate in candidates:
  v=(root_traces(tuple(candidate))>>(len(candidate)-1))&1;conditional=[];unconditional=[]
  for s,h in enumerate(vs.h):
   match=v[h]==target[s];counts=np.bincount(observed[h],minlength=support);success=np.bincount(observed[h][match],minlength=support)
   conditional.append(np.divide(success,counts,out=np.zeros(support),where=counts>0));unconditional.append(float(np.mean(match)))
  p=conditional[0][:,None,None,None]*conditional[1][None,:,None,None]*conditional[2][None,None,:,None]*conditional[3][None,None,None,:]
  gain=float(hb(math.prod(unconditional)))-float(np.sum(joint*hb(p)))
  assert gain>=-1e-10;total+=max(0.,gain)
 return total/len(candidates)

def grounded_alternatives(text,vs,probe,sensors,observations):
 result=dict(parsed_alternatives=False,viable_discriminating_alternatives=False,favored_expectation_falsified=False)
 try:
  analysis=parse_analysis(text);parsed=[]
  for key in ['what_result_A_would_mean','what_result_B_would_mean']:
   m=re.match(r'^step=([1-3]);sensor=([A-Z][0-9]);bit=([01]);meaning=',analysis[key])
   if m is None:return result
   step,sensor,bit=int(m[1]),m[2],int(m[3]);parsed.append((step,sensor,bit))
  a,b=parsed
  if a[:2]!=b[:2] or a[2]==b[2] or a[1] not in sensors or a[0]>len(probe):return result
  result['parsed_alternatives']=True;s=sensors.index(a[1]);v=(root_traces(tuple(probe))[vs.h[s]]>>(a[0]-1))&1
  if set(int(x) for x in v)!={0,1}:return result
  result['viable_discriminating_alternatives']=True
  result['favored_expectation_falsified']=observations[a[0]-1][s]==b[2]
  return result
 except (ValueError,AssertionError,TypeError,KeyError):return result
