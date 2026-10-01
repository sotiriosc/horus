"""Product grammar for exact trace shape; every sensor bit remains model-chosen.

No prediction labels are inputs. Verify tokenizer compositionality for all bit
positions and both neighbor settings before allowing the compact product form.
"""
import json
class PredictionFormat:
 def __init__(self,tok,sensors,length):
  assert length in range(1,7) and len(set(sensors))==len(sensors)==4
  self.sensors=sensors;self.length=length;self.eos=tok.eos_token_id;self.tok=tok
  def render(bits):return json.dumps({'predicted_observations':[{s:int(bits[t*len(sensors)+j]) for j,s in enumerate(sensors)} for t in range(length)]},separators=(',',':'))
  self.render=render;n=length*len(sensors)
  def encode(bits):return tuple(tok.encode(render(bits),add_special_tokens=False))+(self.eos,)
  zero=encode([0]*n);one=encode([1]*n);assert len(zero)==len(one)
  self.allowed_by_position=[sorted(set((a,b))) for a,b in zip(zero,one)]
  positions=[i for i,x in enumerate(self.allowed_by_position) if len(x)==2]
  assert len(positions)==n
  assert all({tok.decode([zero[i]],skip_special_tokens=False),tok.decode([one[i]],skip_special_tokens=False)}=={'0','1'} for i in positions)
  assert ''.join(tok.decode([v],skip_special_tokens=False) for v in zero[:-1])==render([0]*n)
  assert ''.join(tok.decode([v],skip_special_tokens=False) for v in one[:-1])==render([1]*n)
  # Single flips in both uniform contexts verify no token can span two bits or
  # change adjacent structural tokens. Legal field names are opaque letter-digit.
  for bit,pos in enumerate(positions):
   x=[0]*n;x[bit]=1;path=encode(x);expected=list(zero);expected[pos]=one[pos];assert path==tuple(expected)
   x=[1]*n;x[bit]=0;path=encode(x);expected=list(one);expected[pos]=zero[pos];assert path==tuple(expected)
  self.max_tokens=len(zero)
 def allowed(self,prefix):
  assert len(prefix)<self.max_tokens
  assert all(int(v) in self.allowed_by_position[i] for i,v in enumerate(prefix))
  return self.allowed_by_position[len(prefix)]
 def constraint(self,prompt_length):
  def allowed(batch_id,input_ids):
   assert batch_id==0;return self.allowed(input_ids[prompt_length:].tolist())
  return allowed
 def validate(self,tokens):
  assert len(tokens)==self.max_tokens
  assert all(int(v) in self.allowed_by_position[i] for i,v in enumerate(tokens))
  text=self.tok.decode(tokens,skip_special_tokens=True);x=json.loads(text)
  assert set(x)=={'predicted_observations'} and len(x['predicted_observations'])==self.length
  assert all(set(row)==set(self.sensors) and all(type(v) is int and v in (0,1) for v in row.values()) for row in x['predicted_observations'])
  return text
