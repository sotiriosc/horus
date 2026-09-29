"""R1 real launch entry; qualified transport only, no gold/scorer access."""
import argparse,json,os,socket,subprocess
from pathlib import Path
from guard import P,B,PRIVATE,inheritance,runtime_identity,frozen_transport
from transport import execute,load_requests,write_new
class RealRuntime:
 def __init__(self):
  self.launch=json.loads((B/'campaign/launch.json').read_bytes());self.host='127.0.0.1';self.port=18085;self.process=None;self.log=None
 def start(self,private):
  with socket.socket() as sock:
   if sock.connect_ex((self.host,self.port))==0:raise RuntimeError('Dedicated port occupied')
  self.log=(private/'server.log').open('xb')
  env={k:v for k,v in os.environ.items() if not k.startswith(('LLAMA_ARG_','LLAMA_LOG_'))}
  self.process=subprocess.Popen(self.launch['command'],cwd=self.launch['cwd'],env=env,stdout=self.log,stderr=subprocess.STDOUT)
 def alive(self):return self.process is not None and self.process.poll() is None
 def stop(self):
  if self.alive():
   self.process.terminate()
   try:self.process.wait(timeout=30)
   except subprocess.TimeoutExpired:self.process.kill();self.process.wait()
  if self.log:self.log.close()
def main():
 a=argparse.ArgumentParser();a.add_argument('--transport-freeze',required=True);args=a.parse_args()
 qualified=json.loads((P/'qualification.json').read_bytes());assert qualified['status']=='PASS' and qualified['real_model_calls']==0
 checks=dict(transport=frozen_transport(args.transport_freeze),inheritance=inheritance(),runtime=runtime_identity())
 assert not (P/'raw').exists() and not PRIVATE.exists(),'Refuse repeat execution'
 write_new(P/'launch-preflight.json',dict(status='PASS',replacement_id='R1',checks=checks,prior_scientific_outputs=False))
 schedule,payloads=load_requests(B)
 result=execute(schedule,payloads,P,PRIVATE,RealRuntime(),'SCIENTIFIC_R1')
 print(json.dumps(dict(attempted=result['attempted_calls'],completed=result['completed_calls'],stop=result['stop'],raw_frozen=True)),flush=True)
if __name__=='__main__':main()
