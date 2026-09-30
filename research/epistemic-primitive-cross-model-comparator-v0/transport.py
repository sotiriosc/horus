"""Exact-byte one-shot HTTP transport. No gold, scoring, inference retry or text repair."""
import datetime
import hashlib
import http.client as http_client
import json
import os
import time
from pathlib import Path

class TransportFailure(RuntimeError):pass

def sha(raw):return hashlib.sha256(raw).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write_new(path,value):
 raw=(json.dumps(value,indent=2,ensure_ascii=True)+'\n').encode()
 with Path(path).open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
 return sha(raw)

def http_request(host,port,method,path,body=None,timeout=600):
 connection=http_client.HTTPConnection(host,port,timeout=timeout)
 try:
  connection.request(method,path,body=body,headers={'Content-Type':'application/json'} if body is not None else {})
  response=connection.getresponse()
  return response.status,response.getheaders(),response.read()
 finally:connection.close()

def load_requests(benchmark):
 manifest=json.loads((benchmark/'materialized/render-manifest.json').read_bytes())
 schedule=manifest['schedule'];entries={x['render_id']:x for x in manifest['entries']}
 if len(schedule)!=112 or len(set(schedule))!=112 or set(schedule)!=set(entries):raise TransportFailure('Invalid frozen schedule')
 payloads={rid:(benchmark/'materialized'/entries[rid]['request_path']).read_bytes() for rid in schedule}
 for rid in schedule:
  if sha(payloads[rid])!=entries[rid]['request_sha256']:raise TransportFailure('Frozen request hash mismatch: '+rid)
 return schedule,payloads

def execute(schedule,payloads,output,private,runtime,purpose,timeout=600,readiness_seconds=180):
 """Same real HTTP orchestration in qualification and science; output domains cannot overlap."""
 if purpose not in ('QUALIFICATION_ONLY','SCIENTIFIC_CROSS_MODEL_COMPARATOR_V0'):raise ValueError('Explicit evidence purpose required')
 if purpose=='QUALIFICATION_ONLY' and 'epistemic-qualification-' not in str(output):raise ValueError('Mock output requires dedicated temporary namespace')
 if purpose=='SCIENTIFIC_CROSS_MODEL_COMPARATOR_V0' and (output.name!='epistemic-primitive-cross-model-comparator-v0' or len(schedule)!=112):raise ValueError('Science requires primitive-study location and complete frozen schedule')
 if len(schedule)!=len(set(schedule)) or set(schedule)!=set(payloads):raise ValueError('Duplicate or incomplete dispatch inventory')
 raw_dir=output/'raw'
 if raw_dir.exists() or (private/'intent.json').exists():raise FileExistsError('Refuse overwrite/resume/retry of an existing execution')
 private.mkdir(mode=0o700,exist_ok=True);raw_dir.mkdir();(raw_dir/'finals').mkdir();(raw_dir/'metadata').mkdir()
 write_new(private/'intent.json',dict(purpose=purpose,start_utc=now(),schedule=schedule))
 completed=[];attempted=[];stop=None;pending=None;started=None
 wire_index=0;controls=[]
 def request(method,path,body=None,limit=timeout):
  nonlocal wire_index
  wire_index+=1;start_utc=now();prefix=f'http-{wire_index:04d}'
  status,headers,response=http_request(runtime.host,runtime.port,method,path,body,limit)
  response_path=private/(prefix+'-body.bin');response_path.write_bytes(response)
  meta=dict(method=method,path=path,start_utc=start_utc,end_utc=now(),http_status=status,response_headers=headers,response_sha256=sha(response),private_body_file=response_path.name,response_bytes=len(response))
  write_new(private/(prefix+'-metadata.json'),meta)
  if path!='/v1/chat/completions':controls.append(meta)
  return status,response
 def require(status,label):
  if status!=200:raise TransportFailure(label+' HTTP '+str(status))
 try:
  runtime.start(private)
  deadline=time.monotonic()+readiness_seconds
  while not runtime.ready():
   if not runtime.alive():raise TransportFailure('Server exited during readiness')
   if time.monotonic()>deadline:raise TransportFailure('Server readiness timeout')
   time.sleep(.05)
  status,body=request('GET','/health',limit=30);require(status,'Readiness')
  if json.loads(body).get('status')!='ok':raise TransportFailure('Unexpected health envelope')
  status,body=request('GET','/props');require(status,'Properties')
  (private/'initial-props.json').write_bytes(body);props=json.loads(body)
  if props.get('total_slots')!=1:raise TransportFailure('Expected exactly one isolated slot')
  write_new(output/'server-properties.json',dict(purpose=purpose,props_sha256=sha(body),build_info=props.get('build_info'),model_path=props.get('model_path'),total_slots=props.get('total_slots'),default_generation_settings=props.get('default_generation_settings')))
  status,initial_slots=request('GET','/slots',limit=30);require(status,'Initial slot inspection')
  initial=json.loads(initial_slots)
  if len(initial)!=1 or initial[0].get('is_processing'):raise TransportFailure('Initial slot not isolated and idle')
  for order,rid in enumerate(schedule,1):
   if not runtime.alive():raise TransportFailure('Server exited before request')
   status,erase=request('POST','/slots/0?action=erase',b'{}',limit=30);require(status,'Slot erase')
   erased=json.loads(erase)
   if erased.get('id_slot')!=0 or type(erased.get('n_erased')) is not int or erased['n_erased']<0:raise TransportFailure('Invalid erase envelope')
   status,slot_bytes=request('GET','/slots',limit=30);require(status,'Slot inspection')
   slots=json.loads(slot_bytes)
   if len(slots)!=1 or slots[0].get('is_processing'):raise TransportFailure('Slot not isolated and idle')
   (private/(rid+'-erase.json')).write_bytes(erase);(private/(rid+'-slot.json')).write_bytes(slot_bytes)
   presentation=json.loads((output/'materialized/render-manifest.json').read_bytes()) if purpose=='SCIENTIFIC_CROSS_MODEL_COMPARATOR_V0' else None
   entry=next(e for e in presentation['entries'] if e['render_id']==rid) if presentation else {}
   pending=dict(world_id=entry.get('world_id'),arm=entry.get('arm'),presentation=entry,purpose=purpose,render_id=rid,call_order=order,start_utc=now(),request_sha256=sha(payloads[rid]),transport_status='ATTEMPTED',slot_erase_sha256=sha(erase),slot_before_sha256=sha(slot_bytes),n_erased=erased['n_erased'])
   write_new(private/(rid+'-intent.json'),pending)
   # Append before the sole completion dispatch: even a dropped response is never retried.
   attempted.append(rid);started=time.monotonic()
   status,response=request('POST','/v1/chat/completions',payloads[rid])
   pending.update(end_utc=now(),wall_seconds=time.monotonic()-started,http_status=status,response_sha256=sha(response))
   (private/(rid+'-response.json')).write_bytes(response);require(status,'Completion')
   envelope=json.loads(response)
   if 'error' in envelope:raise TransportFailure('Server error envelope')
   choices=envelope.get('choices')
   if not isinstance(choices,list) or len(choices)!=1:raise TransportFailure('Invalid completion envelope')
   choice=choices[0];message=choice.get('message',{});final=message.get('content')
   if not isinstance(final,str):raise TransportFailure('Missing final-channel string')
   # Preserve without inspecting class/schema/text quality or feeding any answer into later requests.
   final_bytes=final.encode('utf-8')
   with (raw_dir/'finals'/(rid+'.txt')).open('xb') as f:f.write(final_bytes);f.flush();os.fsync(f.fileno())
   reason=message.get('reasoning_content');usage=envelope.get('usage',{})
   pending.update(transport_status='COMPLETED',finish_reason=choice.get('finish_reason'),usage=usage,prompt_tokens=usage.get('prompt_tokens'),completion_tokens=usage.get('completion_tokens'),final_sha256=sha(final_bytes),reasoning_sha256=sha(reason.encode()) if isinstance(reason,str) else None,reasoning_separated=isinstance(reason,str),timings=envelope.get('timings'))
   write_new(raw_dir/'metadata'/(rid+'.json'),pending);completed.append(rid);pending=None
   if purpose=='SCIENTIFIC_CROSS_MODEL_COMPARATOR_V0':print(json.dumps(dict(completed=len(completed),scheduled=len(schedule),last_render_id=rid)),flush=True)
 except Exception as exc:
  stop=dict(classification='INVALID_STUDY',study_id='CROSS_MODEL_COMPARATOR_V0',reason=type(exc).__name__+': '+str(exc),utc=now(),attempted_calls=len(attempted),completed_calls=len(completed),render_id=pending['render_id'] if pending else (schedule[len(completed)] if len(completed)<len(schedule) else None))
  if pending:
   pending.update(transport_status='FAILED',error=stop['reason'],end_utc=pending.get('end_utc',now()),wall_seconds=pending.get('wall_seconds',time.monotonic()-started))
   target=raw_dir/'metadata'/(pending['render_id']+'.json')
   if not target.exists():write_new(target,pending)
 finally:
  try:runtime.stop()
  except Exception as exc:stop=stop or dict(classification='INVALID_STUDY',study_id='CROSS_MODEL_COMPARATOR_V0',reason='Cleanup failure: '+str(exc),utc=now())
  execution=dict(purpose=purpose,study_id='CROSS_MODEL_COMPARATOR_V0',finished_utc=now(),intended_calls=len(schedule),attempted_calls=len(attempted),completed_calls=len(completed),statuses={rid:('COMPLETED' if rid in completed else 'FAILED' if rid in attempted else 'NOT_RUN') for rid in schedule},stop=stop,retries=0,answer_repairs=0,critic_calls=0,scoring_during_execution=False,server_terminated=not runtime.alive())
  write_new(raw_dir/'execution.json',execution)
  write_new(raw_dir/'control-metadata.json',controls)
  hashes={str(f.relative_to(raw_dir)):sha(f.read_bytes()) for f in sorted(raw_dir.rglob('*')) if f.is_file()}
  write_new(output/'raw-freeze.json',dict(purpose=purpose,study_id='CROSS_MODEL_COMPARATOR_V0',frozen_utc=now(),sha256=hashes,scoring_has_occurred=False))
  for f in raw_dir.rglob('*'):
   if f.is_file():f.chmod(0o444)
 return execution
