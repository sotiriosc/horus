"""Isolated A0 model process. Public messages/IDs/schema only; no world loading."""
import sys
from common import *
from runtime import load,infer

def main():
 model,tok=load();print(canon(dict(ready=True,adapter_sha256=ADAPTER_SHA)),flush=True)
 for line in sys.stdin:
  request=json.loads(line);assert set(request)<= {'id','messages','mode','legal_ids','prediction_shape'}
  assert set(request)>={'id','messages','mode'}
  msgs=request['messages'];assert len(msgs)==2 and [m['role'] for m in msgs]==['system','user']
  assert all(set(m)=={'role','content'} and type(m['content']) is str for m in msgs)
  mode=request['mode'];assert mode in ['analysis','choice','prediction']
  if mode=='choice':assert 'legal_ids' in request and 'prediction_shape' not in request
  elif mode=='prediction':assert 'prediction_shape' in request and 'legal_ids' not in request
  else:assert 'legal_ids' not in request and 'prediction_shape' not in request
  result=infer(model,tok,msgs,legal_ids=request.get('legal_ids'),prediction_shape=request.get('prediction_shape'))
  print(canon(dict(id=request['id'],mode=mode,**result)),flush=True)
if __name__=='__main__':main()
