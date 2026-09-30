import json,hashlib,os,subprocess,time,http.client,re
from pathlib import Path
import jsonschema
R=Path('/tmp/horus-epistemic-primitive-cross-model-comparator-v0');P=R/'research/epistemic-primitive-cross-model-comparator-v0';S=R/'research/qwen-epistemic-primitive-factorization-v0';Q=Path('/tmp/horus-ministral-qualification-v0')
def sha(b):return hashlib.sha256(b).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def request(path,obj=None):
 conn=http.client.HTTPConnection('127.0.0.1',18085,timeout=600)
 try:
  conn.request('POST' if obj is not None else 'GET',path,body=json.dumps(obj).encode() if obj is not None else None,headers={'Content-Type':'application/json'});r=conn.getresponse();body=r.read();assert r.status==200,(path,r.status,body[:250]);return json.loads(body)
 finally:conn.close()
plan=json.loads((P/'original-launch.json').read_bytes());slot=Q/'slots';slot.mkdir(mode=0o700,exist_ok=True)
with (Q/'server.log').open('xb') as log:
 proc=subprocess.Popen(plan['command']+['--slot-save-path',str(slot)],cwd=plan['cwd'],env={k:v for k,v in os.environ.items() if not k.startswith(('LLAMA_ARG_','LLAMA_LOG_'))},stdout=log,stderr=subprocess.STDOUT)
 try:
  start=time.monotonic()
  while b'listening on http://127.0.0.1:18085' not in (Q/'server.log').read_bytes():
   assert proc.poll() is None,'Server failed startup; private log preserved'
   assert time.monotonic()-start<240,'Readiness timeout'
   time.sleep(.2)
  props=request('/props');write(Q/'props.json',props)
  gpu=subprocess.check_output(['nvidia-smi','--query-gpu=name,driver_version,memory.total,memory.used,memory.free','--format=csv']).decode();print(json.dumps(dict(ready=True,gpu=gpu)),flush=True)
  logs=(Q/'server.log').read_text(errors='replace');residency=[x for x in logs.splitlines() if any(s in x for s in ('offloaded','model buffer size','KV buffer size','compute buffer size','n_ctx','type_k','type_v'))];print(json.dumps(dict(residency=residency)),flush=True)
  write(P/'gpu-residency.json',dict(gpu=gpu,loader_evidence=residency))
  layers=re.search(r'offloaded (\d+)/(\d+) layers to GPU',logs);assert layers and layers[1]==layers[2],'Incomplete GPU layers';assert not re.search(r'CPU(?:_Mapped)? model buffer size\s*=\s*[1-9]',logs),'CPU model weights detected'
  # Every original message remains an exact substring in the model-native rendered prompt.
  audit=[]
  for path in sorted((S/'materialized/neutral').glob('*.json')):
   neutral=json.loads(path.read_bytes());ap=request('/apply-template',dict(messages=neutral['messages'],add_generation_prompt=True,chat_template_kwargs={'enable_thinking':True}));prompt=ap['prompt'];assert all(m['content'] in prompt for m in neutral['messages']),path.name
   tok=request('/tokenize',dict(content=prompt,add_special=True,parse_special=True));n=len(tok['tokens']);assert n+2048<=16384
   audit.append(dict(render_id=path.stem,neutral_sha256=sha(path.read_bytes()),messages_exact=True,template_prompt_sha256=sha(prompt.encode()),prompt_tokens=n))
  write(P/'interface-equivalence.json',dict(status='PASS',scientific_inference_calls=0,files=112,mechanism='Native GGUF chat template; original messages occur verbatim; native tokenizer only, no inference',context=16384,reserved_generation=2048,max_prompt_tokens=max(x['prompt_tokens'] for x in audit),template_sha256=sha(props.get('chat_template','').encode()),entries=audit))
  print(json.dumps(dict(interface='PASS',files=len(audit),max_tokens=max(x['prompt_tokens'] for x in audit))),flush=True)
  results=[]
  for f in json.loads((Q/'fixtures.json').read_bytes()):
   request('/slots/0?action=erase',{});slots=request('/slots');assert len(slots)==1 and not slots[0]['is_processing']
   result=request('/v1/chat/completions',f['request']);write(Q/(f['id']+'-envelope.json'),result)
   choice=result['choices'][0];msg=choice['message'];text=msg['content'];obj=json.loads(text);schema=f['request']['response_format']['schema'];jsonschema.Draft7Validator(schema).validate(obj);assert obj==f['target'],'Synthetic serialization transport failure'
   reason=msg.get('reasoning_content');entry=dict(id=f['id'],schema=f['schema_name'],schema_valid=True,synthetic_target_exact=True,finish_reason=choice['finish_reason'],usage=result.get('usage'),final_sha256=sha(text.encode()),reasoning_sha256=sha(reason.encode()) if isinstance(reason,str) else None);results.append(entry);write(P/'synthetic-qualification-results.json',dict(status='IN_PROGRESS',results=results));print(json.dumps(entry),flush=True)
  write(P/'synthetic-qualification-results.json',dict(status='PASS',scientific_calls=0,synthetic_calls=len(results),results=results))
 finally:
  proc.terminate()
  try:proc.wait(timeout=30)
  except subprocess.TimeoutExpired:proc.kill();proc.wait()
