import json,hashlib,os,subprocess,time,http.client,re
from pathlib import Path
import jsonschema
R=Path('/tmp/horus-epistemic-primitive-gpt-oss-comparator-v0');P=R/'research/epistemic-primitive-gpt-oss-comparator-v0';S=R/'research/qwen-epistemic-primitive-factorization-v0';Q=Path('/tmp/horus-gpt-oss-qualification-v1');Q.mkdir(mode=0o700,exist_ok=True)
def sha(b):return hashlib.sha256(b).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def request(path,obj=None):
 conn=http.client.HTTPConnection('127.0.0.1',18085,timeout=600)
 try:
  conn.request('POST' if obj is not None else 'GET',path,body=json.dumps(obj).encode() if obj is not None else None,headers={'Content-Type':'application/json'});r=conn.getresponse();body=r.read();assert r.status==200,(path,r.status);return json.loads(body)
 finally:conn.close()
plan=json.loads((P/'original-launch.json').read_bytes());slot=Q/'slots';slot.mkdir(mode=0o700,exist_ok=True)
with (Q/'server.log').open('xb') as log:
 proc=subprocess.Popen(plan['command']+['--slot-save-path',str(slot)],cwd=plan['cwd'],env={k:v for k,v in os.environ.items() if not k.startswith(('LLAMA_ARG_','LLAMA_LOG_'))},stdout=log,stderr=subprocess.STDOUT)
 try:
  start=time.monotonic()
  while b'listening on http://127.0.0.1:18085' not in (Q/'server.log').read_bytes():
   assert proc.poll() is None,'Server failed startup; private log preserved';assert time.monotonic()-start<240;time.sleep(.2)
  props=request('/props');write(Q/'props.json',props);gpu=subprocess.check_output(['nvidia-smi','--query-gpu=name,driver_version,memory.total,memory.used,memory.free','--format=csv']).decode();logs=(Q/'server.log').read_text(errors='replace');residency=[x for x in logs.splitlines() if any(s in x for s in ('offloaded','model buffer size','KV buffer size','compute buffer size','n_ctx','type_k','type_v','type  f32','type  f16','type mxfp4','type bf16','type  bf16','type q8_0'))]
  layers=re.search(r'offloaded (\d+)/(\d+) layers to GPU',logs);assert layers and layers[1]==layers[2];assert not re.search(r'CPU(?:_Mapped)? model buffer size\s*=\s*[1-9]',logs)
  write(P/'gpu-residency.json',dict(status='PASS',gpu=gpu,loader_evidence=residency));print(json.dumps(dict(ready=True,gpu=gpu,residency=residency)),flush=True)
  template=(P/'runtime-chat-template.jinja').read_text()
  original_guard='{%- if "<|channel|>analysis<|message|>" in message.content or "<|channel|>final<|message|>" in message.content %}'
  applied=template.replace(original_guard,'{%- if false %}');assert props['chat_template']==applied
  (P/'runtime-applied-chat-template.jinja').write_text(applied)
  write(P/'runtime-template-normalization.json',dict(supplied_sha256=sha(template.encode()),applied_sha256=sha(applied.encode()),transformation='Pinned llama.cpp disables assistant content channel-tag validation guard; no assistant history exists in these requests; semantic system/user content unchanged',expected_replacements=template.count(original_guard)))
  audit=[]
  for path in sorted((S/'materialized/neutral').glob('*.json')):
   neutral=json.loads(path.read_bytes());ap=request('/apply-template',dict(messages=neutral['messages'],add_generation_prompt=True,chat_template_kwargs={'reasoning_effort':'high'}));prompt=ap['prompt'];assert all(m['content'] in prompt for m in neutral['messages']),path.name;assert 'Reasoning: high' in prompt and '2026-09-29' in prompt;assert '<|start|>developer' in prompt
   n=len(request('/tokenize',dict(content=prompt,add_special=True,parse_special=True))['tokens']);assert n+8192<=16384
   audit.append(dict(render_id=path.stem,neutral_sha256=sha(path.read_bytes()),messages_exact=True,template_prompt_sha256=sha(prompt.encode()),prompt_tokens=n))
  write(P/'interface-equivalence.json',dict(status='PASS',scientific_inference_calls=0,files=112,mechanism='Native Harmony: semantic system instruction maps to developer; user text unchanged; high reasoning/date are transport metadata; no task hints, tools or history',context=16384,reserved_generation=8192,max_prompt_tokens=max(x['prompt_tokens'] for x in audit),template_sha256=sha(template.encode()),entries=audit));print(json.dumps(dict(interface='PASS',files=len(audit),max_tokens=max(x['prompt_tokens'] for x in audit))),flush=True)
  results=[]
  for f in json.loads((P/'synthetic-fixtures.json').read_bytes()):
   req=f['request'];prompt=request('/apply-template',dict(messages=req['messages'],add_generation_prompt=True,chat_template_kwargs=req['chat_template_kwargs']))['prompt'];n=len(request('/tokenize',dict(content=prompt,add_special=True,parse_special=True))['tokens']);assert n+8192<=16384 and 'Reasoning: high' in prompt
   request('/slots/0?action=erase',{});slots=request('/slots');assert len(slots)==1 and not slots[0]['is_processing'];start=time.monotonic();result=request('/v1/chat/completions',req);write(Q/(f['id']+'-envelope.json'),result)
   choice=result['choices'][0];msg=choice['message'];text=msg['content'];obj=json.loads(text);jsonschema.Draft7Validator(req['response_format']['schema']).validate(obj);reason=msg.get('reasoning_content');assert isinstance(reason,str) and reason.strip(),'Task-shaped reasoning channel absent';assert choice['finish_reason']=='stop';assert result['usage']['completion_tokens']<4096,'Output allowance lacks headroom'
   entry=dict(id=f['id'],schema=f['schema_name'],schema_valid=True,reasoning_engaged=True,finish_reason=choice['finish_reason'],usage=result.get('usage'),wall_seconds=time.monotonic()-start,request_sha256=sha(json.dumps(req).encode()),final_sha256=sha(text.encode()),reasoning_sha256=sha(reason.encode()),synthetic_target_exact_descriptive_only=obj==f['target']);results.append(entry);write(P/'synthetic-qualification-results.json',dict(status='IN_PROGRESS',results=results));print(json.dumps(entry),flush=True)
  write(P/'synthetic-qualification-results.json',dict(status='PASS',scientific_calls=0,synthetic_calls=len(results),native_analysis_engaged=len(results),semantic_accuracy_not_used_for_selection=True,results=results))
 finally:
  proc.terminate()
  try:proc.wait(timeout=30)
  except subprocess.TimeoutExpired:proc.kill();proc.wait()
