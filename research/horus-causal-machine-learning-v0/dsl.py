"""Alien-machine synchronous DSL and exact finite-state behavior normalization.

One action toggles one of four input bits. Combinational observations use NEW
inputs and OLD registers. Every register updates simultaneously afterward,
including registers inside inactive select branches. Reset clears all storage.
Expressions are trees; only actuator leaves are shared. Sensor trees have
separate storage. No program or register is part of the model interface.
"""
import hashlib,itertools,json
from functools import lru_cache
N_INPUTS=4
PERMS=tuple(itertools.permutations(range(N_INPUTS)))
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def sha(x):return hashlib.sha256(canon(x).encode()).hexdigest()
def normalize(e,perm=tuple(range(N_INPUTS))):
 op=e[0]
 if op=='input':return ('input',perm[e[1]])
 if op=='not':return (op,normalize(e[1],perm))
 if op in ('and','or','xor'):
  children=sorted((normalize(e[1],perm),normalize(e[2],perm)),key=canon);return (op,*children)
 if op=='select':return (op,*(normalize(c,perm) for c in e[1:]))
 if op=='delay':return (op,e[1],normalize(e[2],perm))
 if op=='latch':return (op,normalize(e[1],perm),normalize(e[2],perm))
 if op=='counter':return (op,e[1],e[2],normalize(e[3],perm))
 raise ValueError(op)
def children(e):
 if e[0]=='input':return ()
 if e[0]=='delay':return (e[2],)
 if e[0]=='counter':return (e[3],)
 return e[1:]
def features(e):
 cs=[features(c) for c in children(e)];op=e[0]
 return dict(components=int(op!='input')+sum(x['components'] for x in cs),depth=int(op!='input')+max([x['depth'] for x in cs] or [0]),delay_chain=(e[1] if op=='delay' else 0)+max([x['delay_chain'] for x in cs] or [0]),registers=int(op in ('delay','latch','counter'))+sum(x['registers'] for x in cs),persistent=int(op in ('latch','counter'))+sum(x['persistent'] for x in cs))
class Circuit:
 def __init__(self,roots):
  self.code=[];self.registers=[]
  def compile_expr(e):
   op=e[0];args=tuple(compile_expr(c) for c in children(e));param=e[1] if op in ('input','delay') else e[1:3] if op=='counter' else None;slot=None
   if op in ('delay','latch','counter'):slot=len(self.registers);self.registers.append((len(self.code),op,args,param))
   self.code.append((op,args,param,slot));return len(self.code)-1
  self.outputs=tuple(compile_expr(e) for e in roots);self.initial=(0,(0,)*len(self.registers))
 def values(self,bits,regs):
  out=[]
  for op,args,param,slot in self.code:
   if op=='input':v=(bits>>param)&1
   elif op=='not':v=1-out[args[0]]
   elif op=='and':v=out[args[0]]&out[args[1]]
   elif op=='or':v=out[args[0]]|out[args[1]]
   elif op=='xor':v=out[args[0]]^out[args[1]]
   elif op=='select':v=out[args[1]] if out[args[0]] else out[args[2]]
   elif op=='delay':v=(regs[slot]>>(param-1))&1
   elif op=='latch':v=regs[slot]
   elif op=='counter':v=int(regs[slot]>=param[1])
   else:raise ValueError(op)
   out.append(v)
  return out
 def observation(self,state):
  values=self.values(*state);return tuple(values[i] for i in self.outputs)
 def step(self,state,action):
  assert type(action) is int and 0<=action<N_INPUTS
  bits=state[0]^(1<<action);values=self.values(bits,state[1]);regs=[]
  for slot,(_,op,args,param) in enumerate(self.registers):
   old=state[1][slot]
   if op=='delay':v=((old<<1)|values[args[0]])&((1<<param)-1)
   elif op=='latch':v=0 if values[args[1]] else 1 if values[args[0]] else old
   else:v=(old+values[args[0]])%param[0]
   regs.append(v)
  return (bits,tuple(regs)),tuple(values[i] for i in self.outputs)

def reference(roots,actions,state=None,return_state=False):
 """Independent recursive interpreter: explicit queues and path-addressed state."""
 storage={}
 def initialize(e,path):
  if e[0]=='delay':storage[path]=(0,)*e[1]
  elif e[0] in ('counter','latch'):storage[path]=0
  for i,c in enumerate(children(e)):initialize(c,path+(i,))
 for i,e in enumerate(roots):initialize(e,(i,))
 inputs=[0]*N_INPUTS
 if state is not None:inputs=list(state[0]);storage=dict(state[1])
 def evaluate(e,path):
  op=e[0]
  if op=='input':return inputs[e[1]]
  if op=='delay':return storage[path][0]
  if op=='latch':return storage[path]
  if op=='counter':return int(storage[path]>=e[2])
  v=[evaluate(c,path+(i,)) for i,c in enumerate(children(e))]
  if op=='not':return int(not v[0])
  if op=='and':return int(all(v))
  if op=='or':return int(any(v))
  if op=='xor':return int(sum(v)==1)
  if op=='select':return v[1] if v[0] else v[2]
  raise ValueError(op)
 def changes(e,path,new):
  op=e[0]
  if op=='delay':new[path]=storage[path][1:]+(evaluate(e[2],path+(0,)),)
  elif op=='latch':new[path]=0 if evaluate(e[2],path+(1,)) else 1 if evaluate(e[1],path+(0,)) else storage[path]
  elif op=='counter':new[path]=(storage[path]+evaluate(e[3],path+(0,)))%e[1]
  for i,c in enumerate(children(e)):changes(c,path+(i,),new)
 outputs=[tuple(evaluate(e,(i,)) for i,e in enumerate(roots))]
 for a in actions:
  inputs[a]=1-inputs[a];outputs.append(tuple(evaluate(e,(i,)) for i,e in enumerate(roots)));new={}
  for i,e in enumerate(roots):changes(e,(i,),new)
  storage.update(new)
 return (outputs,(tuple(inputs),dict(storage))) if return_state else outputs

def catalog():
 """Finite declared hypothesis family; each sensor may use ANY listed root.
 Actual sampling strata never narrow the independent hypothesis checker.
 """
 found={}
 for cycle in (1,2):
  for family in range(3):
   for roles in itertools.permutations(range(N_INPUTS),3):
    for flags in itertools.product((0,1),repeat=3):
     for gate in ('and','or'):
      for invert in (0,1):
       if cycle==1 and sum(flags)>1:continue
       lit=[('not',('input',r)) if f else ('input',r) for r,f in zip(roles,flags)];a,b,c=lit
       if cycle==1:
        base=[('delay',1,(gate,a,b)),(gate,('delay',1,a),b),('select',('delay',1,a),b,c)][family]
        deep=(gate,('delay',1,(gate,('delay',1,base),c)),b)
       else:
        base=[('xor',('delay',2,a),(gate,b,c)),('xor',('latch',a,b),('delay',1,c)),('xor',('counter',3,2,(gate,a,b)),c)][family]
        deep=('xor',('delay',2,base),('latch',c,('delay',1,a)))
       for level,e in [('train',base),('test',deep)]:
        if invert:e=('not',e)
        e=normalize(e);key=(cycle,family,level,canon(e));found[key]=dict(cycle=cycle,family=family,level=level,expression=e,features=features(e))
 return sorted(found.values(),key=lambda x:(x['cycle'],x['family'],x['level'],canon(x['expression'])))

def program_signature(roots):return sha(min(tuple(sorted(canon(normalize(e,p)) for e in roots)) for p in PERMS))
@lru_cache(maxsize=None)
def behavior_signatures(expression_text):
 """Exact reachable Mealy minimization, canonical under each input permutation.
 All register configurations reached from reset are enumerated. No sampled
 behavioral fingerprint is substituted for transducer equivalence.
 """
 e=json.loads(expression_text);vm=Circuit([e]);states=[vm.initial];indices={vm.initial:0};edges=[]
 for state in states:
  row=[]
  for a in range(N_INPUTS):
   nxt,obs=vm.step(state,a)
   if nxt not in indices:indices[nxt]=len(states);states.append(nxt)
   row.append((obs[0],indices[nxt]))
  edges.append(row)
  if len(states)>16384:raise ValueError('Declared root exceeds finite-state engineering bound')
 groups=[0]*len(states)
 while True:
  signatures={};updated=[]
  for row in edges:
   key=tuple((bit,groups[nxt]) for bit,nxt in row)
   if key not in signatures:signatures[key]=len(signatures)
   updated.append(signatures[key])
  if updated==groups:break
  groups=updated
 representatives={}
 for i,g in enumerate(groups):representatives.setdefault(g,i)
 hashes=[]
 for perm in PERMS:
  # New input index perm[old]; visit transitions in new-label order.
  inverse=[perm.index(a) for a in range(N_INPUTS)];queue=[groups[0]];ids={groups[0]:0};table=[]
  for g in queue:
   row=[]
   for a in inverse:
    bit,nxt=edges[representatives[g]][a];ng=groups[nxt]
    if ng not in ids:ids[ng]=len(queue);queue.append(ng)
    row.append((bit,ids[ng]))
   table.append(row)
  hashes.append(sha(dict(reset_observation=vm.observation(vm.initial)[0],transitions=table)))
 return tuple(hashes)
def behavior_signature(roots):
 signatures=[behavior_signatures(canon(e)) for e in roots]
 return sha(min(tuple(sorted(x[i] for x in signatures)) for i in range(len(PERMS))))
