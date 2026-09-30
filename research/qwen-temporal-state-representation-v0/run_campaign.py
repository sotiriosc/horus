"""R2 real launch entry; qualified transport only, no gold/scorer access."""
import argparse,json,os,socket,subprocess,shutil
from pathlib import Path
from guard import P,PRIVATE,inheritance,runtime_identity,frozen_transport
from transport import execute,load_requests,write_new
class RealRuntime:
 def __init__(self):
  self.launch=json.loads((P/'launch-plan.json').read_bytes());self.host='127.0.0.1';self.port=18085;self.process=None;self.log=None
 def start(self,private):
  with socket.socket() as sock:
   if sock.connect_ex((self.host,self.port))==0:raise RuntimeError('Dedicated port occupied')
  self.log=(private/'server.log').open('xb')
  env={k:v for k,v in os.environ.items() if not k.startswith(('LLAMA_ARG_','LLAMA_LOG_'))}
  self.process=subprocess.Popen(self.launch['command'],cwd=self.launch['cwd'],env=env,stdout=self.log,stderr=subprocess.STDOUT)
 def ready(self):return self.log is not None and b'listening on http://127.0.0.1:18085' in Path(self.log.name).read_bytes()
 def alive(self):return self.process is not None and self.process.poll() is None
 def stop(self):
  if self.alive():
   self.process.terminate()
   try:self.process.wait(timeout=30)
   except subprocess.TimeoutExpired:self.process.kill();self.process.wait()
  if self.log:self.log.close()
  slot=Path(self.launch['slot_directory'])
  if slot.exists():
   if list(slot.iterdir()):shutil.move(str(slot),str(PRIVATE/'slot-directory-archive'))
   else:slot.rmdir()
def main():
 a=argparse.ArgumentParser();a.add_argument('--case-freeze',required=True);args=a.parse_args()
 qualified=json.loads((P/'qualification.json').read_bytes());assert qualified['status']=='PASS' and qualified['real_model_calls']==0
 checks=dict(frozen=frozen_transport(args.case_freeze),inheritance=inheritance(),runtime=runtime_identity())
 assert not (P/'raw').exists() and not (PRIVATE/'intent.json').exists(),'Refuse repeat execution'
 plan=json.loads((P/'launch-plan.json').read_bytes());original=json.loads((P/'original-launch.json').read_bytes())
 slot=Path(plan['slot_directory']);assert slot.is_dir() and not list(slot.iterdir()) and slot.stat().st_mode&0o777==0o700
 assert plan['command'][:-1]==original['command'][:-1] and plan['cwd']==original['cwd']
 write_new(P/'launch-preflight.json',dict(status='PASS',case_freeze=args.case_freeze,checks=checks,prior_scientific_outputs=False))
 schedule,payloads=load_requests(P)
 result=execute(schedule,payloads,P,PRIVATE,RealRuntime(),'SCIENTIFIC_TEMPORAL_STATE_V0')
 print(json.dumps(dict(attempted=result['attempted_calls'],completed=result['completed_calls'],stop=result['stop'],raw_frozen=True)),flush=True)
if __name__=='__main__':main()
