"""Protected real-process measurement. No policy, scoring or Memory access."""
import hashlib,json,os,subprocess,threading,time,urllib.request
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PUBLIC=ROOT/'research/horus-real-task-runtime-optimization-v0'
ASSETS=Path('/tmp/horus-development-runtime-assets')
PRIVATE=Path('/tmp/horus-real-task-runtime-optimization-v0-private')
MODEL=ASSETS/'model/Qwen3-14B-Q4_K_M.gguf'
ENGINE=ASSETS/'engine/llama-b11242'
EXE=ENGINE/'llama-server'
COMPAT=ASSETS/'compat/root/usr/lib/x86_64-linux-gnu'
CUDA=ASSETS/'engine/cudart-llama-b11242-bin-ubuntu-cuda-12.8-x64'
MODEL_SHA='500a8806e85ee9c83f3ae08420295592451379b4f8cf2d0f41c15dffeb6b81f0'
EXE_SHA='778f1b3fbbb76e921af1d7f25a5b61d82859962dcd18c71ce86ab84d7f4884e5'
URL='http://127.0.0.1:18086'
CANDIDATES={'HOLD':{'batch':512,'ubatch':128,'threads':8,'threads_batch':8},'ADVANCE':{'batch':2048,'ubatch':512,'threads':16,'threads_batch':16},'RETREAT':{'batch':128,'ubatch':64,'threads':4,'threads_batch':4}}
CEILING=22000
class InfrastructureError(RuntimeError):pass
def sha(data):return hashlib.sha256(data).hexdigest()
def file_sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def write(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def now():return datetime.now(timezone.utc).isoformat()
def http(path,payload=None,timeout=180,base=URL):
 data=None if payload is None else json.dumps(payload,separators=(',',':')).encode()
 req=urllib.request.Request(base+path,data=data,headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=timeout) as r:return json.load(r)
def gpu():
 raw=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,name,driver_version,memory.total,memory.used,utilization.gpu,temperature.gpu','--format=csv,noheader,nounits'],text=True,timeout=5).strip().split(', ')
 return dict(uuid=raw[0],name=raw[1],driver=raw[2],total_mib=int(raw[3]),used_mib=int(raw[4]),utilization=int(raw[5]),temperature_c=int(raw[6]))
def compute_processes():
 raw=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader,nounits'],text=True,timeout=5)
 return sorted(x.strip() for x in raw.splitlines() if x.strip())
def idle():
 samples=[]
 for _ in range(30):
  s=gpu();samples.append(s)
  if s['utilization']<=25 and s['used_mib']<5000 and not compute_processes():return samples
  time.sleep(1)
 raise InfrastructureError('GPU not idle/free before isolated target launch')
def pins():
 observed={'model_sha256':file_sha(MODEL),'executable_sha256':file_sha(EXE)}
 if observed!={'model_sha256':MODEL_SHA,'executable_sha256':EXE_SHA}:raise InfrastructureError('artifact hash mismatch')
 return observed
def command(action,slots):
 c=CANDIDATES[action]
 return [str(COMPAT/'ld-linux-x86-64.so.2'),'--library-path',':'.join(map(str,[COMPAT,ENGINE,CUDA])),str(EXE),'--model',str(MODEL),'--host','127.0.0.1','--port','18086','--ctx-size','8192','--parallel','1','--jinja','--n-gpu-layers','999','--override-tensor','.*=CUDA0','--fit','off','--flash-attn','on','--reasoning','off','--no-cache-prompt','--cache-ram','0','--no-cache-idle-slots','--no-warmup','--no-context-shift','--offline','--log-verbosity','4','--cache-type-k','f16','--cache-type-v','f16','--batch-size',str(c['batch']),'--ubatch-size',str(c['ubatch']),'--threads',str(c['threads']),'--threads-batch',str(c['threads_batch']),'--slot-save-path',str(slots)]
def request(system,prompt,cap=512,schema=None):
 r=dict(messages=[{'role':'system','content':system},{'role':'user','content':prompt}],temperature=0.0,top_p=1.0,top_k=1,min_p=0.0,seed=917223,max_tokens=cap,stream=False,cache_prompt=False,chat_template_kwargs={'enable_thinking':False})
 if schema is not None:r['response_format']={'type':'json_object','schema':schema}
 return r
READY_SCHEMA={'type':'object','properties':{'ready':{'type':'boolean'}},'required':['ready'],'additionalProperties':False}
WARM=request('Return the requested JSON object.','Return {"ready":true}.',32,READY_SCHEMA)
class Server:
 def __init__(self,action,directory):
  self.action=action;self.directory=Path(directory);self.process=None;self.samples=[];self.stop=threading.Event()
 def __enter__(self):
  self.directory.mkdir(parents=True,exist_ok=False);self.pin=pins();self.pre_idle=idle()
  self.slots=self.directory/'slots';self.slots.mkdir(mode=0o700)
  self.cmd=command(self.action,self.slots);self.log=(self.directory/'server.log').open('w');self.launch_start=time.perf_counter()
  write(self.directory/'launch.json',dict(command=self.cmd,pins=self.pin,started_at=now(),gpu_before=self.pre_idle))
  self.process=subprocess.Popen(self.cmd,cwd=ENGINE,stdout=self.log,stderr=subprocess.STDOUT)
  try:
   deadline=time.monotonic()+120
   while time.monotonic()<deadline:
    if self.process.poll() is not None:raise RuntimeError('server launch failed')
    try:
     if http('/health',timeout=2).get('status')=='ok':break
    except Exception:time.sleep(.2)
   else:raise RuntimeError('server startup deadline')
   self.launch_seconds=time.perf_counter()-self.launch_start
   self.properties=http('/props');write(self.directory/'properties.json',self.properties)
   self.log.flush();txt=(self.directory/'server.log').read_text()
   if 'offloaded 41/41 layers to GPU' not in txt or 'CPU_Mapped model buffer size' in txt:raise InfrastructureError('model not completely GPU resident')
   self.own_compute=compute_processes()
   for _ in range(2):
    self.erase();x=http('/v1/chat/completions',WARM);assert x['choices'][0]['finish_reason']=='stop'
   self.thread=threading.Thread(target=self.monitor,daemon=True);self.thread.start()
   return self
  except BaseException:self.__exit__(None,None,None);raise
 def monitor(self):
  while not self.stop.is_set():
   try:self.samples.append(gpu())
   except Exception:self.samples.append({'monitor_error':True})
   self.stop.wait(.5)
 def erase(self):
  http('/slots/0?action=erase',{});slots=http('/slots');assert len(slots)==1 and not slots[0]['is_processing']
 def measure(self,r,name,validator='json',reference=None):
  if compute_processes()!=self.own_compute:raise InfrastructureError('competing compute process before measurement')
  self.erase();time.sleep(1);start_index=len(self.samples);before=gpu();start=now();t=time.perf_counter();error=None;response=None
  try:response=http('/v1/chat/completions',r,timeout=180)
  except Exception as e:error=type(e).__name__+': '+str(e)
  wall=time.perf_counter()-t;end=now();after=gpu();samples=self.samples[start_index:]+[before,after]
  if compute_processes()!=self.own_compute and self.process.poll() is None:raise InfrastructureError('competing compute process during measurement')
  valid_samples=[s for s in samples if 'used_mib' in s]
  peak=max(s['used_mib'] for s in valid_samples);body='';finish=None;timings={};usage={};structural=False
  if response:
   write(self.directory/(name+'-envelope.json'),response)
   body=response['choices'][0]['message'].get('content') or '';finish=response['choices'][0].get('finish_reason');timings=response.get('timings',{});usage=response.get('usage',{})
   try:
    if validator=='action':obj=json.loads(body);structural=set(obj)=={'selected_action'} and obj['selected_action'] in CANDIDATES
    elif validator=='json':structural=isinstance(json.loads(body),dict)
    elif validator=='review':structural=all(body.count(h)==1 for h in ['DIAGNOSIS:','PROPOSED_CHANGE:','EVIDENCE:']) and body.index('DIAGNOSIS:')<body.index('PROPOSED_CHANGE:')<body.index('EVIDENCE:')
    else:raise ValueError('unregistered validator')
   except (ValueError,TypeError,KeyError):structural=False
  valid=error is None and finish=='stop' and structural and (reference is None or sha(body.encode())==reference) and peak<=CEILING
  result=dict(action=self.action,request_sha256=sha(json.dumps(r,sort_keys=True).encode()),start_utc=start,end_utc=end,wall_seconds=wall,prompt_tokens=usage.get('prompt_tokens'),completion_tokens=usage.get('completion_tokens'),timings=timings,output_sha256=sha(body.encode()),output_bytes=len(body.encode()),structural_valid=structural,reference_match=None if reference is None else sha(body.encode())==reference,valid=valid,finish_reason=finish,error=error,resource_violation=peak>CEILING,peak_vram_mib=peak,gpu_before=before,gpu_after=after,monitor_samples=len(valid_samples),monitor_errors=sum('monitor_error' in s for s in samples),server_exit_status=self.process.poll(),launch_seconds=self.launch_seconds,full_gpu_residency=True,cache_erased=True)
  write(self.directory/(name+'-measurement.json'),result);(self.directory/(name+'-final.txt')).write_text(body)
  return result
 def __exit__(self,*_):
  self.stop.set()
  if hasattr(self,'thread'):self.thread.join(timeout=6)
  if self.process and self.process.poll() is None:
   self.process.terminate()
   try:self.process.wait(timeout=15)
   except subprocess.TimeoutExpired:self.process.kill();self.process.wait(timeout=5)
  if hasattr(self,'log'):self.log.close()
  if self.process:write(self.directory/'termination.json',dict(exit_status=self.process.returncode,ended_at=now()))
  return False
