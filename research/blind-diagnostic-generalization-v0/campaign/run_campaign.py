"""One-shot transport. No gold/scorer imports, retries, answer parsing or feedback."""
import datetime,hashlib,http.client,json,os,socket,subprocess,time
from pathlib import Path
P=Path(__file__).resolve().parent;B=P.parent
PRIVATE=Path('/tmp/horus-blind-diagnostic-generalization-v0-inference-private')
ASSETS=Path('/tmp/horus-development-runtime-assets')
PORT=18085

def sha(raw):return hashlib.sha256(raw).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(path,value):
 raw=(json.dumps(value,indent=2,ensure_ascii=True)+'\n').encode()
 with path.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
 return sha(raw)
def http(method,path,body=None,timeout=600):
 conn=http.client.HTTPConnection('127.0.0.1',PORT,timeout=timeout)
 try:
  conn.request(method,path,body=body,headers={'Content-Type':'application/json'} if body is not None else {})
  response=conn.getresponse();return response.status,response.read()
 finally:conn.close()
def main():
 pre=json.loads((P/'preflight.json').read_text());assert pre['status']=='PASS'
 manifest=json.loads((B/'materialized/render-manifest.json').read_text());schedule=manifest['schedule'];entries={e['render_id']:e for e in manifest['entries']}
 assert len(schedule)==len(set(schedule))==len(entries)==80
 raw_dir=P/'raw';assert not raw_dir.exists() and not PRIVATE.exists(),'Refuse resume or any previous outputs'
 payloads={rid:(B/'materialized'/entries[rid]['request_path']).read_bytes() for rid in schedule}
 assert all(sha(payloads[rid])==entries[rid]['request_sha256'] for rid in schedule)
 # Exclusive intent directory and ledger guarantee that rerunning cannot retry a call.
 PRIVATE.mkdir(mode=0o700);raw_dir.mkdir();(raw_dir/'finals').mkdir();(raw_dir/'metadata').mkdir()
 write(PRIVATE/'intent.json',dict(started=now(),schedule=schedule,preflight_sha256=sha((P/'preflight.json').read_bytes())))
 config=json.loads((B/'model-runtime.json').read_text())['configuration'];engine=ASSETS/'engine/llama-b11242';compat=ASSETS/'compat/root/usr/lib/x86_64-linux-gnu';cuda=ASSETS/'engine/cudart-llama-b11242-bin-ubuntu-cuda-12.8-x64'
 command=[str(compat/'ld-linux-x86-64.so.2'),'--library-path',':'.join(map(str,(compat,engine,cuda))),str(engine/'llama-server'),'--model',str(ASSETS/'model/Qwen3-14B-Q4_K_M.gguf'),'--host','127.0.0.1','--port',str(PORT),*config['planned_runtime_flags'],'--no-cache-prompt','--cache-ram','0','--no-cache-idle-slots','--no-warmup','--offline','--log-verbosity','4']
 # Strip runtime environment overrides, not system loader/GPU defaults.
 env={k:v for k,v in os.environ.items() if not k.startswith(('LLAMA_ARG_','LLAMA_LOG_'))}
 write(P/'launch.json',dict(command=command,cwd=str(engine),runtime_environment_overrides_removed=True,cache_isolation='Disabled prompt and RAM caches; erase slot before every request',model_access='Text-only exact messages; no tool loop, media path, filesystem/web tools or prior conversation'))
 server=None;log=None;completed=[];attempts=[];stop=None;pending=None
 try:
  with socket.socket() as sock:assert sock.connect_ex(('127.0.0.1',PORT))!=0,'Dedicated port already occupied'
  log=(PRIVATE/'server.log').open('xb');server=subprocess.Popen(command,cwd=engine,env=env,stdout=log,stderr=subprocess.STDOUT)
  deadline=time.monotonic()+180
  while True:
   if server.poll() is not None:raise RuntimeError('Server exited during startup: '+str(server.returncode))
   try:
    status,body=http('GET','/health',timeout=2)
    if status==200:break
   except (OSError,http.client.HTTPException):pass
   if time.monotonic()>deadline:raise RuntimeError('Server readiness timeout')
   time.sleep(.5)
  status,body=http('GET','/props');assert status==200
  (PRIVATE/'initial-props.json').write_bytes(body)
  props=json.loads(body);write(P/'server-identity.json',dict(build_info=props.get('build_info'),model_path=props.get('model_path'),total_slots=props.get('total_slots'),default_generation_settings=props.get('default_generation_settings'),props_sha256=sha(body)))
  assert props.get('total_slots')==1,'Expected one slot'
  for order,rid in enumerate(schedule,1):
   if server.poll() is not None:raise RuntimeError('Server exited before scheduled request')
   status,erase=http('POST','/slots/0?action=erase',b'{}',timeout=30)
   if status!=200:raise RuntimeError('Slot erase failed HTTP '+str(status))
   status,slot_raw=http('GET','/slots',timeout=30)
   if status!=200:raise RuntimeError('Slot inspection failed HTTP '+str(status))
   slots=json.loads(slot_raw)
   if len(slots)!=1 or slots[0].get('is_processing'):raise RuntimeError('Slot not isolated and idle')
   # Save controls privately, retaining their hashes as public audit evidence.
   (PRIVATE/(rid+'-erase.json')).write_bytes(erase);(PRIVATE/(rid+'-slot.json')).write_bytes(slot_raw)
   pending=dict(render_id=rid,call_order=order,request_sha256=sha(payloads[rid]),start_utc=now(),slot_erase_sha256=sha(erase),slot_before_sha256=sha(slot_raw),transport_status='ATTEMPTED')
   write(PRIVATE/(rid+'-intent.json'),pending);attempts.append(rid)
   start=time.monotonic()
   status,response=http('POST','/v1/chat/completions',payloads[rid])
   pending.update(end_utc=now(),wall_seconds=time.monotonic()-start,http_status=status,response_sha256=sha(response))
   (PRIVATE/(rid+'-response.json')).write_bytes(response)
   if status!=200:raise RuntimeError('Completion transport HTTP '+str(status))
   envelope=json.loads(response)
   if 'error' in envelope:raise RuntimeError('Server returned error envelope')
   choices=envelope.get('choices')
   if not isinstance(choices,list) or len(choices)!=1:raise RuntimeError('Invalid completion transport envelope')
   choice=choices[0];message=choice.get('message',{});final=message.get('content')
   if not isinstance(final,str):raise RuntimeError('Missing final-channel string')
   # Do not inspect the text, parse JSON, score, strip, repair or condition the schedule on it.
   final_bytes=final.encode('utf-8');target=raw_dir/'finals'/(rid+'.txt')
   with target.open('xb') as f:f.write(final_bytes);f.flush();os.fsync(f.fileno())
   usage=envelope.get('usage',{});reason=message.get('reasoning_content')
   pending.update(transport_status='COMPLETED',finish_reason=choice.get('finish_reason'),usage=usage,prompt_tokens=usage.get('prompt_tokens'),completion_tokens=usage.get('completion_tokens'),final_sha256=sha(final_bytes),reasoning_sha256=sha(reason.encode()) if isinstance(reason,str) else None,reasoning_separated=isinstance(reason,str),timings=envelope.get('timings'))
   write(raw_dir/'metadata'/(rid+'.json'),pending);completed.append(rid);pending=None
   print(json.dumps(dict(completed=len(completed),scheduled=80,last_render_id=rid)),flush=True)
 except Exception as exc:
  stop=dict(classification='INVALID_STUDY',reason=str(exc),utc=now(),attempted_calls=len(attempts),completed_calls=len(completed),render_id=pending['render_id'] if pending else (schedule[len(completed)] if len(completed)<80 else None))
  if pending:
   pending.update(transport_status='FAILED',error=str(exc),end_utc=pending.get('end_utc',now()))
   if not (raw_dir/'metadata'/(pending['render_id']+'.json')).exists():write(raw_dir/'metadata'/(pending['render_id']+'.json'),pending)
 finally:
  if server is not None and server.poll() is None:
   server.terminate()
   try:server.wait(timeout=30)
   except subprocess.TimeoutExpired:server.kill();server.wait()
  if log:log.close()
  statuses={rid:('COMPLETED' if rid in completed else 'FAILED' if rid in attempts else 'NOT_RUN') for rid in schedule}
  write(raw_dir/'execution.json',dict(finished_utc=now(),intended_calls=80,attempted_calls=len(attempts),completed_calls=len(completed),statuses=statuses,stop=stop,retries=0,answer_repairs=0,critic_calls=0,scoring_during_execution=False,server_terminated=server is None or server.poll() is not None))
  hashes={str(f.relative_to(raw_dir)):sha(f.read_bytes()) for f in sorted(raw_dir.rglob('*')) if f.is_file()}
  write(P/'raw-freeze.json',dict(frozen_utc=now(),sha256=hashes,scoring_has_occurred=False,method='Raw final bytes and metadata preserved and hashed before any campaign scoring'))
  for f in raw_dir.rglob('*'):
   if f.is_file():f.chmod(0o444)
  print(json.dumps(dict(completed=len(completed),attempted=len(attempts),stop=stop,raw_frozen=True)),flush=True)
if __name__=='__main__':main()
