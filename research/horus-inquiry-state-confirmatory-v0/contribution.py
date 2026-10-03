"""Inherited structural contrast metric; no model analysis or target scoring."""
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

