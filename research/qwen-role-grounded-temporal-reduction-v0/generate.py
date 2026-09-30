"""Fresh offline author. Never reads any prior response or prediction."""
import copy,itertools,random
from collections import Counter
from common import *
def trial(obs='MATCH',suff='DETERMINATE',unknown=False,old=False):
 return dict(currentness='NOT_CURRENT' if old else 'CURRENT',knownness='UNKNOWN' if unknown else 'KNOWN',alternative_completion='ALTERNATIVE_EXISTS' if unknown else 'NO_ALTERNATIVE',observation_requirement=obs,evidence_sufficiency=suff)
def old(obs='MATCH',suff='DETERMINATE',unknown=False):return trial(obs,suff,unknown,True)
def state(cur,hist,same=False,equal=True,bad=False):
 return dict(proposition_scope=SCOPE,package=dict(same_referent=same,equal_value=equal,consistency='CONTRADICTORY' if bad else 'CONSISTENT'),current_trial=cur,non_current_trials=hist)
def author_gold(s):
 c=s['current_trial'];h=s['non_current_trials']
 if s['package']['consistency']=='CONTRADICTORY':return X,'Immutable provenance assertions conflict; operational package invalid.'
 if c['evidence_sufficiency']=='UNDERDETERMINED':return U,'Current violation and compliance both remain possible; old facts do not resolve that uncertainty.'
 if c['observation_requirement']=='MISMATCH':return D,'All current admissible completions violate the scoped requirement.'
 if any(t['evidence_sufficiency']=='DETERMINATE' and t['observation_requirement']=='MISMATCH' for t in h):return T,'All current completions comply and at least one explicitly older trial demonstrates a violation.'
 return N,'All current completions comply; no older trial demonstrates a defect in this complete scope.'
def witness(s):
 def w(t):
  violate=t['observation_requirement']=='MISMATCH';values=[violate]
  if t['knownness']=='UNKNOWN':values.append(not violate if t['evidence_sufficiency']=='UNDERDETERMINED' else violate)
  return dict(deployed=t['currentness']=='CURRENT',reference_input=0,admissible_inputs=list(range(len(values))),observed_output=101,required_outputs=[103 if v else 101 for v in values])
 p=s['package'];a=[dict(subject='role-mark-1',value=211),dict(subject='role-mark-1' if p['same_referent'] else 'role-mark-2',value=211 if p['equal_value'] else 223)]
 a += [dict(subject='role-provenance',value=v) for v in ([307,311] if p['consistency']=='CONTRADICTORY' else [307,307])]
 return dict(assertions=a,current=w(s['current_trial']),non_current=[w(t) for t in s['non_current_trials']])
def generate():
 rng=random.Random(SEED);cases=[];pairs=[];bylabel={}
 def add(label,s,expected):
  gold,proof=author_gold(s);assert gold==expected,(label,gold,expected)
  sid='rt-v0-'+sha(f'{SEED}:{label}'.encode())[:14]
  c=dict(id=sid,state=s,gold=gold,author_proof=proof,witness=witness(s));cases.append(c);bylabel[label]=c;return c
 def altered(label,source,path,value,gold):
  z=copy.deepcopy(bylabel[source]['state']);v=z
  for key in path[:-1]:v=v[key]
  v[path[-1]]=value;return add(label,z,gold)
 def pair(a,b,changing,field):pairs.append(dict(id=f'rt-p{len(pairs)+1:02d}',A=bylabel[a]['id'],B=bylabel[b]['id'],changing=changing,declared_field=field,gold_A=bylabel[a]['gold'],gold_B=bylabel[b]['gold']))
 add('n1',state(trial(),[old(),old(unknown=True)],same=True),N)
 altered('t1','n1',['non_current_trials',0,'observation_requirement'],'MISMATCH',T);pair('n1','t1',True,'.non_current_trials.0.observation_requirement')
 add('d1',state(trial('MISMATCH',unknown=True),[old('MISMATCH',unknown=True),old()],equal=False),D)
 altered('t2','d1',['current_trial','observation_requirement'],'MATCH',T);pair('d1','t2',True,'.current_trial.observation_requirement')
 add('t3',state(trial(unknown=True),[old('MISMATCH','UNDERDETERMINED',True),old(),old('MISMATCH',unknown=True)]),T)
 altered('u1','t3',['current_trial','evidence_sufficiency'],'UNDERDETERMINED',U);pair('t3','u1',True,'.current_trial.evidence_sufficiency')
 altered('x1','t1',['package','consistency'],'CONTRADICTORY',X);pair('t1','x1',True,'.package.consistency')
 add('n2',state(trial(unknown=True),[old(),old('MISMATCH','UNDERDETERMINED',True)],same=True),N)
 altered('t4','n2',['non_current_trials',1,'evidence_sufficiency'],'DETERMINATE',T);pair('n2','t4',True,'.non_current_trials.1.evidence_sufficiency')
 add('t5',state(trial(),[old(unknown=True),old('MISMATCH'),old('MATCH','UNDERDETERMINED',True)]),T)
 altered('t6','t5',['package','equal_value'],False,T);pair('t5','t6',False,'.package.equal_value')
 add('x2',state(trial(unknown=True),[old(),old('MISMATCH',unknown=True)],bad=True),X)
 altered('x3','x2',['current_trial','observation_requirement'],'MISMATCH',X);pair('x2','x3',False,'.current_trial.observation_requirement')
 add('u2',state(trial('MISMATCH','UNDERDETERMINED',True),[old(),old(unknown=True)],equal=False),U)
 altered('u3','u2',['non_current_trials',0,'observation_requirement'],'MISMATCH',U);pair('u2','u3',False,'.non_current_trials.0.observation_requirement')
 # Fresh non-temporal controls; no old dataset is consulted to select them.
 options=[]
 hoptions=[old(),old(unknown=True),old('MISMATCH'),old('MISMATCH',unknown=True),old('MATCH','UNDERDETERMINED',True),old('MISMATCH','UNDERDETERMINED',True)]
 for cls,unknown,obs,marks,h1,h2 in itertools.product([D,N,U,X],[False,True],['MATCH','MISMATCH'],[(True,True),(False,True),(False,False)],hoptions,hoptions):
  if cls==U and not unknown:continue
  cur=trial('MISMATCH' if cls==D else 'MATCH' if cls==N else obs,'UNDERDETERMINED' if cls==U else 'DETERMINATE',unknown)
  z=state(cur,[copy.deepcopy(h1),copy.deepcopy(h2)],*marks,bad=cls==X)
  if author_gold(z)[0]==cls:options.append((cls,z))
 rng.shuffle(options);used={canonical(c['state']) for c in cases};counts=Counter(c['gold'] for c in cases)
 for cls,z in options:
  if counts[cls]>=6 or canonical(z) in used:continue
  add('control-'+str(len(cases)),z,cls);counts[cls]+=1;used.add(canonical(z))
  if len(cases)==30:break
 assert len(cases)==30 and counts=={c:6 for c in CLASSES}
 perms=list(itertools.permutations(ARMS));assignment={}
 for cls in CLASSES:
  cc=[c for c in cases if c['gold']==cls];pp=perms[:];rng.shuffle(pp)
  for c,perm in zip(cc,pp):assignment[c['id']]=perm
 lookup={c['id']:c for c in cases};epochs=[]
 for epoch in range(3):
  for attempt in range(100000):
   groups={cls:[c['id'] for c in cases if c['gold']==cls] for cls in CLASSES}
   for v in groups.values():rng.shuffle(v)
   ids=[]
   for half in range(2):
    chunk=[sid for cls in CLASSES for sid in groups[cls][half*3:half*3+3]];rng.shuffle(chunk);ids+=chunk
   if any(Counter(assignment[sid][epoch] for sid in ids[i:i+15])!={a:5 for a in ARMS} for i in (0,15)):continue
   if epochs and epochs[-1][-1][0]==ids[0]:continue
   epochs.append([(sid,assignment[sid][epoch]) for sid in ids]);break
  else:raise RuntimeError('No balanced schedule')
 files={};entries=[];class_text='Class definitions:\n'+'\n'.join(c+': '+d for c,d in zip(CLASSES,DEFS))
 for c in cases:
  sid=c['id'];sb=raw(c['state']);files['states/'+sid+'.json']=sb
  for arm in ARMS:
   rid=sid+'-'+arm;messages=[dict(role='system',content=CHARTERS[arm]),dict(role='user',content=class_text+'\n\nPrimitive epistemic state:\n'+sb.decode())]
   req=dict(messages=messages,response_format=dict(type='json_object',schema=SCHEMA),temperature=.2,top_p=.9,top_k=40,min_p=.05,seed=SEED,max_tokens=2048,cache_prompt=False,stream=False,chat_template_kwargs=dict(enable_thinking=True))
   rb=raw(req);files['requests/'+rid+'.json']=rb;entries.append(dict(render_id=rid,state_id=sid,arm=arm,request_path='requests/'+rid+'.json',request_sha256=sha(rb),state_sha256=sha(sb)))
 files['cases.json']=raw(cases);files['pairs.json']=raw(pairs);files['render-manifest.json']=raw(dict(seed=SEED,schedule=[sid+'-'+arm for ep in epochs for sid,arm in ep],entries=entries,arm_order_by_state=assignment))
 return files
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 for n,b in generate().items():f=a.out/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
 print('Generated 30 fresh states, 8 temporal pairs and 90 frozen isolated requests; zero model calls.')
