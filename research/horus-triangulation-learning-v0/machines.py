"""Fresh compositional family; exact complete-behavior root deduplication.

The finite family is an ordered product of four labeled sensor-root types.
Short-probe agreement NEVER merges candidate programs. Root equivalence uses
complete reachable finite-state Mealy minimization with preserved semantics.
"""
import importlib.util,itertools
from functools import lru_cache
import numpy as np
from common import *
spec=importlib.util.spec_from_file_location('preserved_causal_dsl',OLD/'dsl.py');dsl=importlib.util.module_from_spec(spec);spec.loader.exec_module(dsl)
PROBES=tuple(p for n in (1,2,3) for p in itertools.product(range(4),repeat=n))
PASSIVE=((0,),(1,),(2,),(3,),(0,1),(1,0),(2,3),(3,2),(0,1,2),(1,2,3),(2,3,0),(3,0,1))
PATTERNS=('000','001','010','011','012')
def pattern(p):
 mapping={};return ''.join(str(mapping.setdefault(a,len(mapping))) for a in p)
@lru_cache(None)
def catalogue():
 raw={}
 for roles in itertools.permutations(range(4),3):
  a,b,c=[('input',i) for i in roles]
  for gate in ('and','or'):
   forms={
    'interaction':[(gate,a,b),('select',a,b,c),('select',c,(gate,a,b),('not',a))],
    'delay':[(gate,('delay',1,a),b),('select',('delay',1,a),b,c),('xor',('delay',1,(gate,a,b)),c),('xor',(gate,a,b),('delay',1,c))],
    'latch':[('xor',('latch',a,b),c),('xor',('latch',(gate,a,b),c),a),('select',c,('latch',a,b),('not',a))],
    'repetition':[('xor',('counter',3,2,a),b),('xor',('counter',3,2,(gate,a,b)),c),('select',c,('counter',3,2,a),b)]}
   for group,expressions in forms.items():
    for e in expressions:
     for invert in (0,1):
      root=dsl.normalize(('not',e) if invert else e);key=canon(root)
      if key not in raw:raw[key]=dict(root=root,groups=set())
      raw[key]['groups'].add(group)
 distinct={}
 for key,row in sorted(raw.items()):
  # Index zero preserves actual actuator labels. Other permutations are used
  # only for world-level freshness, never to identify distinct labeled roots.
  signature=dsl.behavior_signatures(key)[0]
  if signature not in distinct:distinct[signature]=dict(root=row['root'],groups=set(),behavior_sha256=signature)
  distinct[signature]['groups'].update(row['groups'])
 return tuple(dict(root=r['root'],groups=sorted(r['groups']),behavior_sha256=r['behavior_sha256']) for r in distinct.values())
@lru_cache(None)
def root_traces(probe):
 return np.array([sum(row[0]<<i for i,row in enumerate(dsl.reference([r['root']],probe)[1:])) for r in catalogue()],dtype=np.uint8)
@lru_cache(None)
def table():
 reset=np.array([dsl.reference([r['root']],[])[0][0] for r in catalogue()],dtype=np.uint8)
 return reset,np.stack([root_traces(p) for p in PROBES],axis=1)
def outcomes(ids,probe):
 v=root_traces(tuple(probe));return [[int((v[i]>>step)&1) for i in ids] for step in range(len(probe))]
def reset_observation(ids):return [int(table()[0][i]) for i in ids]
def graph_hash(ids):return dsl.program_signature([catalogue()[i]['root'] for i in ids])
@lru_cache(None)
def observable_claims():
 # Finite observable claim vocabulary; no global causal bound is inferred.
 # Onset is change from reset under repeated activation over exactly 3 steps.
 reset,_=table();onset=[];relation=[]
 for a in range(4):
  v=root_traces((a,a,a));onset.append(np.array([next((k+1 for k in range(3) if ((int(x)>>k)&1)!=int(r)),0) for x,r in zip(v,reset)],dtype=np.int8))
 for a,b in itertools.permutations(range(4),2):
  b_alone=root_traces((b,))&1;ab=(root_traces((a,b))>>1)&1;ba=(root_traces((b,a))>>1)&1
  relation.extend([ab.astype(np.int8)-b_alone.astype(np.int8),ab.astype(np.int8)-ba.astype(np.int8)])
 return np.stack(onset,axis=1),np.stack(relation,axis=1)
