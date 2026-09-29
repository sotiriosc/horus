"""One-way allowlisted evidence projection. No generator metadata is accepted."""
from copy import deepcopy
import json,re
from world_generator import derive,CLASSES,FAMILIES
WORLD_KEYS={'domain','system_id','components','versions','records'}
FORBIDDEN_WORDS=('horus','zakhor','qwen','dolphin','advance','hold','retreat','broken','stale','faulty','stagnation','escape','exploration','obsolete','suspicious','corruption')
FORBIDDEN_KEYS={'gold','expected','classification','family','fault_type','variant','spec_id','mutation','answer','expected_class','generator_metadata','mechanism_family'}

def strings(v):
 if isinstance(v,str):yield v
 elif isinstance(v,dict):
  for k,x in v.items():yield k;yield from strings(x)
 elif isinstance(v,list):
  for x in v:yield from strings(x)

def replace(v,mapping):
 if isinstance(v,str):return mapping.get(v,v)
 if isinstance(v,list):return [replace(x,mapping) for x in v]
 if isinstance(v,dict):return {mapping.get(k,k):replace(x,mapping) for k,x in v.items()}
 return v

def render(world,seed,case_id,label_map,order):
 if set(world)!=WORLD_KEYS:raise ValueError('Only the public world projection may be rendered')
 assert label_map in ('A','B') and order in (1,2)
 canonical_ids=sorted({s for s in strings(world) if s.startswith('@')})
 mapping={s:'z'+derive(seed,'opaque/'+case_id+'/'+label_map+'/'+s).hex()[:16] for s in canonical_ids}
 assert len(set(mapping.values()))==len(mapping)
 out=replace(world,mapping)
 inverse={v:k for k,v in mapping.items()}
 # Independent presentation factor; causal arrays (priority lists, readings, ordered entries) stay unchanged.
 for name in ('components','versions','records'):
  out[name]=sorted(out[name],key=lambda x:derive(seed,'order/'+case_id+'/'+inverse[x['id']]),reverse=order==2)
 keys=sorted(out,key=lambda k:derive(seed,'sections/'+case_id+'/'+k),reverse=order==2)
 out={k:out[k] for k in keys}
 audit=anti_coaching(out)
 if audit:raise ValueError(audit)
 return out,mapping

def unrender(out,mapping):
 v=replace(out,{value:key for key,value in mapping.items()})
 for k in ('components','versions','records'):v[k]=sorted(v[k],key=lambda x:x['id'])
 return v

def normalized(world):
 v=deepcopy(world)
 for k in ('components','versions','records'):v[k]=sorted(v[k],key=lambda x:x['id'])
 return v

def anti_coaching(case):
 findings=[];alltext='\n'.join(strings(case))
 for word in FORBIDDEN_WORDS:
  if re.search(r'(?i)\b'+re.escape(word)+r'\b',alltext):findings.append('forbidden word '+word)
 for label in (*CLASSES,*FAMILIES,'BOUNDED_STAGNATION_ESCAPE','EMPIRICAL_EVIDENCE_ACQUISITION'):
  if label.lower() in alltext.lower():findings.append('forbidden label '+label)
 if re.search(r'\b(?:S|E)\b',alltext):findings.append('standalone historical identifier')
 if re.search(r'@[A-Za-z0-9_]+',alltext):findings.append('canonical ID exposed')
 def visit(v):
  if isinstance(v,dict):
   for k,x in v.items():
    if k.lower() in FORBIDDEN_KEYS or k.startswith('#'):findings.append('forbidden key '+k)
    visit(x)
  elif isinstance(v,list):
   for x in v:visit(x)
 visit(case)
 return findings
