"""Single HF/NF4 stack for engineering qualification and all scientific arms."""
import contextlib,hashlib,json,os,random,time
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModelForCausalLM,AutoTokenizer,BitsAndBytesConfig
from peft import LoraConfig,get_peft_model,prepare_model_for_kbit_training,get_peft_model_state_dict,set_peft_model_state_dict
BASE=Path('/mnt/d/horus-research-assets/qwen3-14b-qlora-v0/231c69a380487f6c0e52d02dcf0d5456d1918201')
SEED=20260930
CONTEXT=1536
MAX_NEW=96
RANK=16
INFERENCE_BATCH=4

def seed():
 torch.set_num_threads(4);torch.cuda.set_per_process_memory_fraction(.75,0)
 random.seed(SEED);np.random.seed(SEED);torch.manual_seed(SEED);torch.cuda.manual_seed_all(SEED)
 torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False

def load():
 seed();tokenizer=AutoTokenizer.from_pretrained(BASE,local_files_only=True,padding_side='left');tokenizer.pad_token=tokenizer.eos_token
 model=AutoModelForCausalLM.from_pretrained(BASE,local_files_only=True,torch_dtype=torch.bfloat16,device_map={'':'cuda:0'},attn_implementation='sdpa',quantization_config=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type='nf4',bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=torch.bfloat16))
 model=prepare_model_for_kbit_training(model,use_gradient_checkpointing=True,gradient_checkpointing_kwargs={'use_reentrant':False})
 model=get_peft_model(model,LoraConfig(r=RANK,lora_alpha=2*RANK,lora_dropout=0.,bias='none',target_modules='all-linear',task_type='CAUSAL_LM'))
 model.config.use_cache=False
 assert all(p.device.type=='cuda' for p in model.parameters())
 assert all('lora_' in n for n,p in model.named_parameters() if p.requires_grad)
 expected={f'base_model.model.model.layers.{i}.{part}.{proj}' for i in range(40) for part,projs in [('self_attn',['q_proj','k_proj','v_proj','o_proj']),('mlp',['gate_proj','up_proj','down_proj'])] for proj in projs}
 actual={n for n,m in model.named_modules() if hasattr(m,'lora_A')};assert actual==expected,(actual^expected)
 model.eval();return model,tokenizer

def prompt(tokenizer,messages):
 return tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,enable_thinking=False)

def tensor_hash(t):
 b=t.detach().contiguous().cpu().reshape(-1).view(torch.uint8).numpy().tobytes();return hashlib.sha256(b).hexdigest()

def fingerprints(model,adapter):
 out={}
 for n,p in model.named_parameters():
  if ('lora_' in n)!=adapter:continue
  out[n]={'sha256':tensor_hash(p),'shape':list(p.shape),'dtype':str(p.dtype)}
  if not adapter and getattr(p,'quant_state',None) is not None:
   for k,v in p.quant_state.as_dict(packed=True).items():out[n+'::quant_state::'+k]={'sha256':tensor_hash(v),'shape':list(v.shape),'dtype':str(v.dtype)}
 if not adapter:
  for n,p in model.named_buffers():
   if 'lora_' not in n:out['buffer::'+n]={'sha256':tensor_hash(p),'shape':list(p.shape),'dtype':str(p.dtype)}
 return out

def loss(model,tokenizer,messages,target,synthetic_length=None):
 prefix=tokenizer.encode(prompt(tokenizer,messages),add_special_tokens=False);answer=tokenizer.encode(target+tokenizer.eos_token,add_special_tokens=False)
 if synthetic_length:prefix=(prefix*((synthetic_length//len(prefix))+1))[:synthetic_length-len(answer)]
 ids=prefix+answer;assert len(ids)<=CONTEXT
 # Only target prediction positions materialize vocabulary logits. All prompt positions have zero supervised loss.
 output=model(input_ids=torch.tensor([ids],device='cuda'),use_cache=False,logits_to_keep=len(answer)+1)
 return torch.nn.functional.cross_entropy(output.logits[0,:-1].float(),torch.tensor(answer,device='cuda'))

@torch.inference_mode()
def infer(model,tokenizer,messages,enabled=True):
 rendered=[prompt(tokenizer,m) for m in messages]
 batch=tokenizer(rendered,return_tensors='pt',padding=True,add_special_tokens=False).to('cuda');assert batch.input_ids.shape[1]+MAX_NEW<=CONTEXT
 model.eval()
 with contextlib.nullcontext() if enabled else model.disable_adapter():
  output=model.generate(**batch,do_sample=False,max_new_tokens=MAX_NEW,use_cache=True,pad_token_id=tokenizer.pad_token_id,eos_token_id=tokenizer.eos_token_id,temperature=None,top_p=None,top_k=None)
 gen=output[:,batch.input_ids.shape[1]:].cpu().tolist()
 return [{'text':tokenizer.decode(x,skip_special_tokens=True),'generated_token_ids':x,'prompt_sha256':hashlib.sha256(p.encode()).hexdigest(),'prompt_tokens':int(mask.sum()),'generation_token_count':next((i+1 for i,v in enumerate(x) if v==tokenizer.eos_token_id),len(x))} for x,p,mask in zip(gen,rendered,batch.attention_mask)]
