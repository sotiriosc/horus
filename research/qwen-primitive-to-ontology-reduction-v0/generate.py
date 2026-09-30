"""Prospective author: constructs new primitive propositions and offline witnesses, never reads outputs."""
import copy,itertools,random
from collections import Counter
from common import *
def trial(obs='MATCH',suff='DETERMINATE',unknown=True,historical=False):
 return dict(currentness='NOT_CURRENT' if historical else 'CURRENT',knownness='UNKNOWN' if unknown else 'KNOWN',alternative_completion='ALTERNATIVE_EXISTS' if unknown else 'NO_ALTERNATIVE',observation_requirement=obs,evidence_sufficiency=suff)
def state(cls,marks,unknown,hist):
 h=copy.deepcopy(hist)
 if cls==T: h=trial('MISMATCH',unknown=hist is None or hist['knownness']=='UNKNOWN',historical=True)
 return dict(proposition_scope=SCOPE,package=dict(same_referent=marks[0],equal_value=marks[1],consistency='CONTRADICTORY' if cls==X else 'CONSISTENT'),current_trial=trial('MISMATCH' if cls==D else 'MATCH','UNDERDETERMINED' if cls==U else 'DETERMINATE',unknown or cls==U),historical_trial=h)
def change(s,a,b):
 s=copy.deepcopy(s)
 if b==X:s['package']['consistency']='CONTRADICTORY'
 elif (a,b)==(N,D):s['current_trial']['observation_requirement']='MISMATCH'
 elif b==U:s['current_trial']['evidence_sufficiency']='UNDERDETERMINED'
 elif (a,b)==(N,T):s['historical_trial']['observation_requirement']='MISMATCH'
 elif (a,b)==(D,T):s['current_trial']['observation_requirement']='MATCH'
 else:raise ValueError((a,b))
 return s
def witness(s):
 def w(t):
  if t is None:return None
  match=t['observation_requirement']=='MATCH'; vals=[not match]
  if t['knownness']=='UNKNOWN':vals.append(not vals[0] if t['evidence_sufficiency']=='UNDERDETERMINED' else vals[0])
  return dict(deployed=t['currentness']=='CURRENT',reference_input=0,admissible_inputs=list(range(len(vals))),observed_output=7,required_outputs=[8 if v else 7 for v in vals])
 marks=s['package'];subjects=['mark-a','mark-a' if marks['same_referent'] else 'mark-b']; values=[19,19 if marks['equal_value'] else 23]
 # Independent provenance assertions permit a package contradiction without changing queried marks.
 bad=marks['consistency']=='CONTRADICTORY'
 assertions=[dict(subject=x,value=y) for x,y in zip(subjects,values)]
 assertions += [dict(subject='provenance-c',value=v) for v in ([31,37] if bad else [31,31])]
 return dict(assertions=assertions,current=w(s['current_trial']),historical=w(s['historical_trial']))
def gold(s):
 p,c,h=s['package'],s['current_trial'],s['historical_trial']
 if p['consistency']=='CONTRADICTORY':return X,'The package has incompatible immutable assertions; trial propositions cannot establish a valid operational diagnosis.'
 if c['evidence_sufficiency']=='UNDERDETERMINED':return U,'Both current violation and benign compliance remain admissible; historical evidence does not resolve current uncertainty.'
 if c['observation_requirement']=='MISMATCH':return D,'Every current completion violates the requirement; a specific active defect is distinguished from benign alternatives.'
 if h and h['evidence_sufficiency']=='DETERMINATE' and h['observation_requirement']=='MISMATCH':return T,'All current completions comply; every older completion violates the same scoped requirement.'
 return N,'All current completions comply and no older defect is demonstrated in the declared complete scope.'
def generate():
 rng=random.Random(SEED); pairs=[]; used=set(); states=[]
 edges=[(N,D),(N,U),(D,U),(N,T),(D,T),(T,U),(N,X),(D,X),(U,X),(T,X),(N,D),(D,U),(T,U),(T,X),(N,X)]
 marks=[(True,True),(False,True),(False,False)]
 histories=[None,trial(historical=True),trial(unknown=False,historical=True),trial('MATCH','UNDERDETERMINED',historical=True),trial('MISMATCH','UNDERDETERMINED',historical=True)]
 def add(a,b,s,t,family,stratum):
  i=len(pairs)+1;pid=f'pro-v0-p{i:02d}'; endpoints={}
  for side,z,g in [('A',s,a),('B',t,b)]:
   sid='pro-v0-'+sha(f'{SEED}:{pid}:{side}'.encode())[:14];endpoints[side]=sid
   computed,proof=gold(z); assert computed==g
   used.add(canonical(z));states.append(dict(id=sid,pair=pid,side=side,state=z,gold=g,author_proof=proof,witness=witness(z),stratum=stratum,family=family))
  pairs.append(dict(id=pid,endpoints=endpoints,gold_A=a,gold_B=b,changing=a!=b,family=family,stratum=stratum))
 for a,b in edges:
  options=list(itertools.product(marks,[False,True],histories));rng.shuffle(options)
  for m,unknown,h in options:
   if b==U:unknown=True
   if (a,b)==(N,T):h=trial(unknown=unknown,historical=True)
   if (a,b)==(D,T):h=trial('MISMATCH',unknown=unknown,historical=True)
   s=state(a,m,unknown,h); t=change(s,a,b)
   if canonical(s) in used or canonical(t) in used:continue
   family='CONTRADICTION' if b==X else 'SUFFICIENCY' if b==U else 'HISTORY' if b==T else 'OBSERVATION'
   competing=bool(s['historical_trial']) or a in (U,T) or b in (U,T,X)
   add(a,b,s,t,family,'PRECEDENCE' if competing else 'SIMPLE');break
  else:raise RuntimeError(('Could not construct fresh changing pair',len(pairs)+1,a,b))
 for cls in CLASSES:
  for repeat in range(2):
   options=list(itertools.product(marks,[False,True],histories));rng.shuffle(options)
   for m,unknown,h in options:
    s=state(cls,m,unknown,h);t=copy.deepcopy(s)
    if cls==X:
     # Probe contradiction over either determinate mismatch or underdetermination, with history present.
     if repeat==1:s['current_trial']=trial('MATCH','UNDERDETERMINED');s['historical_trial']=trial('MISMATCH',historical=True);t=copy.deepcopy(s)
     t['current_trial']['observation_requirement']='MISMATCH'
     family='IRRELEVANT_OBSERVATION'
    elif cls==U and repeat==1:
     s['historical_trial']=trial('MATCH',unknown=unknown,historical=True);t=copy.deepcopy(s);t['historical_trial']['observation_requirement']='MISMATCH';family='IRRELEVANT_HISTORY'
    elif repeat==0:
     if s['package']['equal_value'] is not True:continue
     t['package']['same_referent']=not m[0];family='IRRELEVANT_IDENTITY'
    else:
     if s['package']['same_referent']:continue
     t['package']['equal_value']=not m[1];family='IRRELEVANT_EQUALITY'
    if canonical(s) in used or canonical(t) in used:continue
    add(cls,cls,s,t,family,'IRRELEVANT_CHANGE');break
   else:raise RuntimeError('Could not construct fresh stable pair')
 assert Counter(s['gold'] for s in states)=={c:10 for c in CLASSES}
 # Five balanced ten-call blocks; reject adjacent pairs and enforce 13/12 endpoint order.
 byclass={c:[s for s in states if s['gold']==c] for c in CLASSES}
 for attempt in range(100000):
  for v in byclass.values():rng.shuffle(v)
  schedule=[]
  for block in range(5):
   chunk=[s for c in CLASSES for s in byclass[c][block*2:block*2+2]];rng.shuffle(chunk);schedule+=chunk
  pos={s['id']:i for i,s in enumerate(schedule)}
  if any(schedule[i]['pair']==schedule[i+1]['pair'] for i in range(49)):continue
  if sum(pos[p['endpoints']['A']]<pos[p['endpoints']['B']] for p in pairs)!=13:continue
  if not any(s['stratum']=='SIMPLE' for s in schedule[:25]) or not any(s['stratum']=='SIMPLE' for s in schedule[25:]):continue
  if any(not {'PRECEDENCE','IRRELEVANT_CHANGE'} <= {s['stratum'] for s in schedule[i:i+10]} for i in range(0,50,10)):continue
  break
 else:raise RuntimeError('No balanced schedule')
 files={};entries=[]
 class_text='Class definitions:\n'+'\n'.join(c+': '+d for c,d in zip(CLASSES,DEFS))
 for s in states:
  sid=s['id'];messages=[dict(role='system',content='Classify the supplied already-resolved primitive epistemic state using the class definitions. Return only the classification object satisfying the schema.'),dict(role='user',content=class_text+'\n\nPrimitive epistemic state:\n'+raw(s['state']).decode())]
  req=dict(messages=messages,response_format=dict(type='json_object',schema=SCHEMA),temperature=.2,top_p=.9,top_k=40,min_p=.05,seed=SEED,max_tokens=2048,cache_prompt=False,stream=False,chat_template_kwargs=dict(enable_thinking=True))
  files['states/'+sid+'.json']=raw(s['state']);files['requests/'+sid+'.json']=raw(req)
  entries.append(dict(render_id=sid,request_path='requests/'+sid+'.json',request_sha256=sha(raw(req)),state_sha256=sha(raw(s['state']))))
 files['cases.json']=raw(states);files['pairs.json']=raw(pairs);files['render-manifest.json']=raw(dict(seed=SEED,schedule=[s['id'] for s in schedule],entries=entries))
 return files
if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);args=a.parse_args();args.out.mkdir(parents=True,exist_ok=False)
 for n,b in generate().items():p=args.out/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
 print('50 fresh endpoints, 25 pairs, 50 isolated requests generated; zero model calls.')
