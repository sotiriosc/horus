"""Finite legal JSON language. Token masking constrains syntax, never utility.

The only inputs are the public legal IDs and pinned tokenizer. No probe trace,
program, contribution score, candidate hypothesis or preferred action enters.
"""
import re,json
class LegalChoiceTrie:
 def __init__(self,tokenizer,legal_ids):
  assert legal_ids and len(set(legal_ids))==len(legal_ids)
  assert all(type(x) is str and re.fullmatch(r'P\d{3}',x) for x in legal_ids)
  self.root={};self.paths={};self.texts={};self.eos=tokenizer.eos_token_id
  assert type(self.eos) is int
  for ident in legal_ids:
   text=json.dumps({'probe_id':ident},separators=(',',':'))
   tokens=tuple(tokenizer.encode(text,add_special_tokens=False))
   assert tokenizer.decode(tokens,skip_special_tokens=False)==text
   assert self.eos not in tokens
   tokens=tokens+(self.eos,);self.paths[ident]=tokens;self.texts[ident]=text
   node=self.root
   for token in tokens:node=node.setdefault(token,{})
   assert not node
  self.max_tokens=max(map(len,self.paths.values()))
  assert len(set(self.paths.values()))==len(legal_ids)
 def allowed(self,prefix):
  node=self.root
  for token in prefix:
   assert int(token) in node,'Generated prefix is outside finite legal language'
   node=node[int(token)]
  assert node,'Generation continued past a complete legal JSON+EOS'
  return sorted(node)
 def constraint(self,prompt_length):
  def prefix_allowed_tokens_fn(batch_id,input_ids):
   assert batch_id==0,'Frozen batch size is one'
   return self.allowed(input_ids[prompt_length:].tolist())
  return prefix_allowed_tokens_fn
 def identify(self,tokens):
  tokens=tuple(tokens)
  matches=[ident for ident,path in self.paths.items() if path==tokens]
  assert len(matches)==1,'Output must exactly equal a legal JSON+EOS token path'
  return matches[0]
 def leaves(self):
  out=[]
  def walk(node,path):
   if not node:out.append(tuple(path));return
   for token,child in node.items():walk(child,path+[token])
  walk(self.root,[]);return out
