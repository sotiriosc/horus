"""Public-only JSON grammar: references, shape and bounded prose, never utility."""
import json
from functools import lru_cache
_SAFE_CACHE={}
class AnalysisFormat:
 def __init__(self,tok,arm,ledger,legal,sensors):
  assert arm in ['D','T'] and ledger and len(sensors)==4
  self.tok=tok;self.eos=tok.eos_token_id;self.arm=arm;self.ledger=ledger;self.legal=legal;self.sensors=sensors;self.max_prose_tokens=12;self.max_prose_chars=120
  self.enc=lru_cache(None)(lambda s:tuple(tok.encode(s,add_special_tokens=False)));self.decode=lambda seq:tok.decode(list(seq),skip_special_tokens=False)
  if id(tok) not in _SAFE_CACHE:
   safe={};special=set(tok.all_special_ids)
   for i in range(len(tok)):
    if i in special:continue
    value=self.decode([i])
    if value and all(32<=ord(c)<127 and c not in '\\"' for c in value):safe[i]=value
   _SAFE_CACHE[id(tok)]=safe
  self.safe=_SAFE_CACHE[id(tok)]
  self.safe_by_remaining={};self.cache={};self.max_tokens=512
  # Token segments concatenate literally; no tokenizer boundary assumptions.
  for s in ['{"status":','"PREDICTION"','"INSUFFICIENT_DELTA"','"','0','1']:
   assert self.decode(self.enc(s))==s
 def program(self):
  # The generator consumes completed field values and selects only public shape.
  status=yield ('enum',['INSUFFICIENT_DELTA','PREDICTION'])
  if status=='INSUFFICIENT_DELTA':
   yield ('literal','}');return
  yield ('literal',',"evidence_A":');a=yield ('enum',list(dict.fromkeys(e['probe_id'] for e in self.ledger)))
  yield ('literal',',"evidence_B":');b=yield ('enum',['NONE'] if len({e['probe_id'] for e in self.ledger})==1 else [i for i in dict.fromkeys(e['probe_id'] for e in self.ledger) if i!=a])
  for name,none in [('observed_endpoint_A',False),('observed_endpoint_B',b=='NONE')]:
   yield ('literal',',"'+name+'":')
   if none:yield ('literal','"NONE"')
   else:yield from self.bitrow()
  yield ('literal',',"comparison_kind":');yield ('enum',['one_step_extension','adjacent_swap','other','single_observation'])
  if self.arm=='D':
   for k in ['observed_input_delta','observed_output_delta','provisional_relation']:
    yield ('literal',',"'+k+'":');yield ('prose',None)
  else:
   for name,keys in [('observed_delta',['input_or_context','outcome']),('time',['what_temporal_difference_is_supported','what_temporal_part_remains_unknown']),('relation',['what_changed_with_what','candidate_relation']),('direction',['which_unknown_distinction_should_be_resolved_next'])]:
    yield ('literal',',"'+name+'":{')
    for j,k in enumerate(keys):
     yield ('literal',(',' if j else '')+'"'+k+'":');yield ('prose',None)
    yield ('literal','}')
  yield ('literal',',"prediction":{"untested_probe_id":');tested={e['probe_id'] for e in self.ledger};target=yield ('enum',[r['id'] for r in self.legal if r['id'] not in tested]);length=len(next(r['sequence'] for r in self.legal if r['id']==target))
  yield ('literal',',"'+('predicted_difference' if self.arm=='D' else 'expected_outcome_or_delta')+'":');yield ('prose',None)
  yield ('literal',',"predicted_trace":');primary=yield from self.trace(length)
  yield ('literal','}')
  if self.arm=='D':yield ('literal',',"why_this_test_matters":');yield ('prose',None)
  else:
   yield ('literal',',"alternative_prediction":');yield ('prose',None)
   yield ('literal',',"alternative_trace":');yield from self.trace(length,primary)
   yield ('literal',',"what_result_would_separate_them":');yield ('prose',None)
  yield ('literal','}')
 def bitrow(self,primary=None,changed=False,lastrow=False):
  yield ('literal','"');bits=[]
  for j in range(4):
   allowed=['0','1']
   if primary is not None and lastrow and j==3 and not changed and bits==list(primary[:3]):allowed=[str(1-int(primary[j]))]
   b=yield ('rawenum',allowed);bits.append(b)
  yield ('literal','"');return ''.join(bits)
 def trace(self,n,primary=None):
  yield ('literal','[');rows=[];changed=False
  for i in range(n):
   if i:yield ('literal',',')
   row=yield from self.bitrow(primary[i] if primary else None,changed,i==n-1);rows.append(row)
   if primary and row!=primary[i]:changed=True
  yield ('literal',']');return rows
 def allowed(self,prefix):
  prefix=tuple(map(int,prefix))
  if prefix in self.cache:return self.cache[prefix]
  pos=0
  def consume(paths):
   nonlocal pos
   start=pos
   while True:
    candidates=[(seq,val) for seq,val in paths if seq[:pos-start]==prefix[start:pos]]
    assert candidates,'Invalid analysis prefix'
    done=[v for seq,v in candidates if len(seq)==pos-start]
    if done:return True,done[0]
    allowed=sorted({seq[pos-start] for seq,val in candidates})
    if pos==len(prefix):return False,allowed
    assert prefix[pos] in allowed;pos+=1
  ok,result=consume([(self.enc('{"status":'),None)])
  if not ok:self.cache[prefix]=result;return result
  gen=self.program();node=next(gen);value=None
  while True:
   kind,data=node
   if kind=='literal':paths=[(self.enc(data),None)]
   elif kind in ['enum','rawenum']:
    paths=[(self.enc(json.dumps(v) if kind=='enum' else v),v) for v in data]
   else:
    ok,result=consume([(self.enc('"'),None)])
    if not ok:self.cache[prefix]=result;return result
    text='';count=0
    while True:
     remaining=self.max_prose_chars-len(text);quote=self.enc('"');assert len(quote)==1
     if pos==len(prefix):
      if remaining not in self.safe_by_remaining:self.safe_by_remaining[remaining]=[i for i,s in self.safe.items() if len(s)<=remaining]
      allowed=list(self.safe_by_remaining[remaining]) if count<self.max_prose_tokens else []
      if count:allowed.append(quote[0])
      self.cache[prefix]=allowed;return allowed
     token=prefix[pos];pos+=1
     if token==quote[0]:
      assert count;break
     assert count<self.max_prose_tokens and token in self.safe and len(self.safe[token])<=remaining
     text+=self.safe[token];count+=1
    value=text
    try:node=gen.send(value);continue
    except StopIteration:break
   ok,result=consume(paths)
   if not ok:self.cache[prefix]=result;return result
   try:node=gen.send(result)
   except StopIteration:break
  assert pos==len(prefix),'Tokens beyond complete object'
  self.cache[prefix]=[self.eos];return [self.eos]
 def constraint(self,prompt_length):
  def allowed(batch_id,input_ids):assert batch_id==0;return self.allowed(input_ids[prompt_length:].tolist())
  return allowed
 def validate(self,tokens):
  assert tokens[-1]==self.eos and len(tokens)<=self.max_tokens
  for i,t in enumerate(tokens):assert int(t) in self.allowed(tokens[:i])
  text=self.tok.decode(tokens,skip_special_tokens=True)
  from interface import parse_analysis
  assert parse_analysis(text,self.arm,self.ledger,self.legal,self.sensors) is not None
  return text
