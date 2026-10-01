"""New finite compositional hypothesis family; inherited synchronous semantics.

A candidate machine is an ordered Cartesian product of four sensor roots.
Roots are quotient representatives of identical reset + 84-probe behavior.
The uniform prior is over these distinct observable root types, independently
per sensor, restricted by the publicly provided reset observation. This is an
exact finite family, not a sampled approximation to a larger DSL.
"""
import importlib.util,itertools
from functools import lru_cache
import numpy as np
from common import *
spec=importlib.util.spec_from_file_location('preserved_causal_dsl',OLD/'dsl.py')
dsl=importlib.util.module_from_spec(spec);spec.loader.exec_module(dsl)
PROBES=tuple(p for n in (1,2,3) for p in itertools.product(range(4),repeat=n))
PASSIVE=((0,),(1,),(2,),(3,),(0,1),(1,0),(2,3),(3,2),(0,1,2),(1,2,3),(2,3,0),(3,0,1))
def trace(root,probe):return tuple(row[0] for row in dsl.reference([root],probe)[1:])
@lru_cache(None)
def catalogue():
 expressions={}
 for a,b,c in itertools.permutations(range(4),3):
  a,b,c=('input',a),('input',b),('input',c)
  for gate in ('and','or'):
   for invert in (False,True):
    forms=[(gate,a,b),('select',a,b,c),(gate,('delay',1,a),b),('select',('delay',1,a),b,c),('xor',('latch',a,b),c),('xor',('counter',3,2,a),b),('xor',('delay',1,(gate,a,b)),c),('select',c,(gate,a,b),('not',a)),('xor',(gate,a,b),('delay',1,c)),(gate,('not',a),('delay',1,b)),('xor',('latch',(gate,a,b),c),a),('select',a,('delay',1,b),('not',c))]
    for e in forms:
     if invert:e=('not',e)
     e=dsl.normalize(e);expressions[canon(e)]=e
 # Canonical first structural representative, never scientific-world dependent.
 distinct={}
 for key,e in sorted(expressions.items()):
  reset=dsl.reference([e],[])[0][0]
  signature=(reset,tuple(trace(e,p) for p in PROBES))
  distinct.setdefault(signature,e)
 return tuple(distinct.values())
@lru_cache(None)
def table():
 roots=catalogue();out=np.zeros((len(roots),84),dtype=np.uint8)
 reset=np.array([dsl.reference([r],[])[0][0] for r in roots],dtype=np.uint8)
 for i,r in enumerate(roots):
  for j,p in enumerate(PROBES):out[i,j]=sum(b<<t for t,b in enumerate(trace(r,p)))
 return reset,out

def outcomes(root_ids,probe):
 j=PROBES.index(tuple(probe));_,t=table()
 return [[int((t[i,j]>>step)&1) for i in root_ids] for step in range(len(probe))]
def reset_observation(root_ids):return [int(table()[0][i]) for i in root_ids]
def graph_hash(root_ids):return dsl.program_signature([catalogue()[i] for i in root_ids])
def pattern(p):
 mapping={};return ''.join(str(mapping.setdefault(a,len(mapping))) for a in p)
