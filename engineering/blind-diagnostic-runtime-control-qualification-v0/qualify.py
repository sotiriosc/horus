"""One real launch, four allowlisted control requests, absolutely no generation."""
import datetime,hashlib,http.client as http_client,json,os,shutil,socket,subprocess,time
from pathlib import Path
from verify import P,B,preservation,runtime_hashes,source_integrity
ALLOWED=(('GET','/health'),('GET','/props'),('GET','/slots'),('POST','/slots/0?action=erase'))
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def write_new(path,value):
 with path.open('x') as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def control_request(host,port,method,path,body=None,timeout=30):
 if (method,path) not in ALLOWED:raise ValueError('Endpoint outside control-only allowlist')
 if body!=(b'{}' if method=='POST' else None):raise ValueError('Unapproved request body')
 if host!='127.0.0.1':raise ValueError('Only isolated localhost')
 connection=http_client.HTTPConnection(host,port,timeout=timeout)
 try:
  connection.request(method,path,body=body,headers={'Content-Type':'application/json'} if body is not None else {})
  response=connection.getresponse();return response.status,response.getheaders(),response.read()
 finally:connection.close()
def observe(output,ordinal,method,path,port=18085):
 meta=dict(order=ordinal,method=method,path=path,start_utc=now(),request_body_sha256=sha(b'{}') if method=='POST' else None)
 try:status,headers,body=control_request('127.0.0.1',port,method,path,b'{}' if method=='POST' else None)
 except Exception as exc:
  meta.update(end_utc=now(),http_status=None,error=repr(exc),response_received=False);write_new(output/(str(ordinal)+'-metadata.json'),meta);raise
 # Entire wire body persisted BEFORE status or JSON acceptance is evaluated.
 body_name=str(ordinal)+'-response.txt'
 with (output/body_name).open('xb') as f:f.write(body);f.flush();os.fsync(f.fileno())
 meta.update(end_utc=now(),http_status=status,response_headers=headers,response_body_file=body_name,response_body_sha256=sha(body),response_bytes=len(body),response_received=True)
 write_new(output/(str(ordinal)+'-metadata.json'),meta)
 if status!=200:raise RuntimeError('Control endpoint HTTP '+str(status)+': '+path)
 value=json.loads(body)
 if path=='/health':assert value['status']=='ok'
 elif path=='/props':assert value['total_slots']==1 and value['build_info']=='b11242-526c43b8f'
 elif path=='/slots':assert isinstance(value,list) and len(value)==1 and not value[0]['is_processing']
 else:assert value['id_slot']==0 and type(value['n_erased']) is int and value['n_erased']==0
 return meta

def main():
 plan=json.loads((P/'plan.json').read_bytes());private=Path(plan['private_evidence_directory']);slots=Path(plan['slot_directory']);original=json.loads((B/'campaign/launch.json').read_bytes())
 assert plan['runtime_command']==original['command']+['--slot-save-path',str(slots)]
 assert plan['cwd']==original['cwd']
 assert [(r['method'],r['path']) for r in plan['requests']]==list(ALLOWED)
 assert slots.is_dir() and not list(slots.iterdir()) and slots.stat().st_mode&0o777==0o700
 assert not (P/'observations').exists() and not (private/'launch-intent.json').exists(),'Never relaunch this qualification'
 checks=dict(preservation=preservation(),runtime=runtime_hashes(),source=source_integrity())
 launch=dict(start_utc=now(),command=plan['runtime_command'],cwd=plan['cwd'],command_delta=plan['command_delta'],slot_directory_empty=True,slot_directory_mode='0700',checks=checks,completion_calls_allowed=0,request_allowlist=list(ALLOWED))
 write_new(P/'launch-preflight.json',launch);write_new(private/'launch-intent.json',launch)
 output=P/'observations';output.mkdir();process=None;log=None;accepted=[];failure=None;directory_action=None
 try:
  with socket.socket() as sock:assert sock.connect_ex(('127.0.0.1',18085))!=0,'Port occupied'
  log_path=private/'server.log';log=log_path.open('xb')
  env={k:v for k,v in os.environ.items() if not k.startswith(('LLAMA_ARG_','LLAMA_LOG_'))}
  process=subprocess.Popen(plan['runtime_command'],cwd=plan['cwd'],env=env,stdout=log,stderr=subprocess.STDOUT)
  deadline=time.monotonic()+plan['startup_timeout_seconds']
  # Non-HTTP startup wait avoids sending any request while the server is loading.
  while b'listening on http://127.0.0.1:18085' not in log_path.read_bytes():
   if process.poll() is not None:raise RuntimeError('Server exited before listening: '+str(process.returncode))
   if time.monotonic()>deadline:raise RuntimeError('Startup log readiness timeout')
   time.sleep(.05)
  for ordinal,(method,path) in enumerate(ALLOWED,1):accepted.append(observe(output,ordinal,method,path))
 except Exception as exc:failure=dict(error=repr(exc),utc=now(),accepted_checks=len(accepted))
 finally:
  if process is not None and process.poll() is None:
   process.terminate()
   try:process.wait(timeout=30)
   except subprocess.TimeoutExpired:process.kill();process.wait()
  if log:log.close()
  if list(slots.iterdir()):
   shutil.move(str(slots),str(private/'slot-directory-archive'));directory_action='Archived unexpected contents privately; never restored'
  else:slots.rmdir();directory_action='Empty private slot directory removed'
  observations=[json.loads(f.read_bytes()) for f in sorted(output.glob('*-metadata.json'))]
  result=dict(classification='REAL_RUNTIME_CONTROL_PATH_QUALIFIED' if failure is None and len(accepted)==4 else 'REAL_RUNTIME_CONTROL_PATH_NOT_QUALIFIED',accepted_checks=len(accepted),observed_requests=len(observations),observations=observations,failure=failure,model_completion_calls=0,benchmark_requests=0,prompts_submitted=0,retries=0,second_erase=False,server_starts=int(process is not None),server_terminated=process is None or process.poll() is not None,slot_directory_cleanup=directory_action,slot_directory_exists=slots.exists(),finished_utc=now())
  write_new(P/'result.json',result)
  write_new(P/'observation-manifest.json',dict(sha256={str(f.relative_to(P)):sha(f.read_bytes()) for f in sorted(output.iterdir()) if f.is_file()},model_completion_calls=0))
  print(json.dumps(result,indent=2))
if __name__=='__main__':main()
