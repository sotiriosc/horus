"""Frozen-weight HF A0 with study-local finite legal-ID selection."""
import importlib.util,time
from common import *
from legal_choice import LegalChoiceTrie
from prediction_format import PredictionFormat
spec=importlib.util.spec_from_file_location('preserved_qlora_runtime',TEMPORAL/'runtime.py');hf=importlib.util.module_from_spec(spec);spec.loader.exec_module(hf)
CONTEXT=6144
TEXT_MAX_NEW=384

def load():
 from safetensors.torch import load_file
 from peft import set_peft_model_state_dict
 assert filehash(ADAPTER)==ADAPTER_SHA
 model,tok=hf.load()
 assert hf.fingerprints(model,False)==json.loads((TEMPORAL/'M0-base-fingerprints.json').read_bytes())
 set_peft_model_state_dict(model,load_file(str(ADAPTER)))
 assert hf.fingerprints(model,True)==json.loads((TEMPORAL/'M1-artifact-freeze.json').read_bytes())['adapter_parameter_fingerprints']
 for p in model.parameters():p.requires_grad_(False)
 return model,tok

def infer(model,tok,messages,legal_ids=None,prediction_shape=None):
 import torch
 rendered=hf.prompt(tok,messages);ids=tok.encode(rendered,add_special_tokens=False)
 assert legal_ids is None or prediction_shape is None
 trie=LegalChoiceTrie(tok,legal_ids) if legal_ids is not None else PredictionFormat(tok,**prediction_shape) if prediction_shape is not None else None
 maximum=trie.max_tokens if trie else TEXT_MAX_NEW
 assert len(ids)+maximum<=CONTEXT,'Full history must fit; truncation is prohibited'
 inputs=tok([rendered],return_tensors='pt',padding=True,add_special_tokens=False).to('cuda')
 options=dict(do_sample=False,max_new_tokens=maximum,use_cache=True,pad_token_id=tok.pad_token_id,eos_token_id=tok.eos_token_id,temperature=None,top_p=None,top_k=None)
 if trie:options.update(prefix_allowed_tokens_fn=trie.constraint(len(ids)),return_dict_in_generate=True,output_scores=True)
 started=time.monotonic()
 with torch.inference_mode():out=model.generate(**inputs,**options)
 generated=(out.sequences if trie else out)[0,len(ids):].cpu().tolist()
 result=dict(text=tok.decode(generated,skip_special_tokens=True),generated_token_ids=generated,prompt_sha256=hashlib.sha256(rendered.encode()).hexdigest(),semantic_messages_sha256=sha(messages),prompt_tokens=len(ids),generation_token_count=len(generated),seconds=round(time.monotonic()-started,6))
 if trie:
  ident=trie.identify(generated) if legal_ids is not None else None
  if prediction_shape is not None:assert trie.validate(generated)==result['text']
  branches=[]
  for step,scores in enumerate(out.scores):
   permitted=trie.allowed(generated[:step]);scores=scores[0]
   finite=torch.isfinite(scores);permitted_mask=torch.zeros_like(finite);permitted_mask[permitted]=True
   assert not torch.any(finite & ~permitted_mask),'Illegal token has nonzero generative support'
   assert torch.all(torch.isfinite(scores[permitted]))
   probabilities=torch.softmax(scores[permitted].float(),dim=-1).cpu().tolist()
   if len(permitted)>1:branches.append(dict(step=step,permitted_tokens=permitted,probabilities=probabilities))
  if legal_ids is not None:
   assert json.loads(result['text'])=={'probe_id':ident}
   result.update(probe_id=ident,finite_choice=dict(legal_ids=list(legal_ids),max_path_tokens=trie.max_tokens,all_generated_tokens_legal=True,illegal_support_zero=True,branch_probabilities=branches))
  else:result['structured_prediction']=dict(shape=prediction_shape,max_path_tokens=trie.max_tokens,all_generated_tokens_legal=True,illegal_support_zero=True)
 return result
