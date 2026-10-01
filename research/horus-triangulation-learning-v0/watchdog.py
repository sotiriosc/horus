"""Bounded local resource monitor; may terminate only its own child process group."""
import json,os,signal,subprocess,sys,time
from pathlib import Path
P=Path(__file__).resolve().parent
PS='/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe'
def memory():
 m={l.split(':')[0]:int(l.split()[1])*1024 for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith(('MemAvailable:','SwapFree:'))};return m['MemAvailable']/2**30

def gpu():
 s=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,temperature.gpu','--format=csv,noheader,nounits'],text=True,timeout=5);free,temp=s.strip().split(',');return float(free)/1024,float(temp)
def windows_free():
 s=subprocess.check_output([PS,'-NoProfile','-NonInteractive','-Command','(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory'],text=True,timeout=12);return int(s.strip())/1024**2
if __name__=='__main__':
 label=sys.argv[1];command=sys.argv[2:];assert command and label.replace('-','').isalnum()
 out=Path('/mnt/d/horus-research-assets/triangulation-learning-v0/monitor');out.mkdir(exist_ok=True,parents=True)
 host=windows_free();free,temp=gpu();avail=memory();print(json.dumps(dict(stage='resource_preflight',gpu_free_GiB=free,linux_available_GiB=avail,windows_free_GiB=host)),flush=True)
 assert free>=20 and avail>=32 and host>=20,'Insufficient headroom; no model launched'
 env=dict(os.environ,TOKENIZERS_PARALLELISM='false',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4')
 child=subprocess.Popen(command,start_new_session=True,env=env);start=time.monotonic();last_host=0;last_log=0;reason=None
 try:
  while child.poll() is None:
   time.sleep(3);elapsed=time.monotonic()-start
   free,temp=gpu();avail=memory()
   if elapsed-last_host>=30:host=windows_free();last_host=elapsed
   if free<2 or avail<12 or host<8 or temp>=85:reason='Resource boundary reached'
   row=dict(elapsed_seconds=round(elapsed,1),gpu_free_GiB=free,gpu_temperature_C=temp,linux_available_GiB=avail,windows_free_GiB=host,stop_reason=reason)
   if elapsed-last_log>=30 or reason:
    with (out/(label+'.jsonl')).open('a') as f:f.write(json.dumps(row)+'\n')
    last_log=elapsed
   if reason:raise RuntimeError(reason)
 except BaseException as e:
  if child.poll() is None:
   os.killpg(child.pid,signal.SIGTERM)
   try:child.wait(timeout=15)
   except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
  (out/(label+'-interruption.json')).write_text(json.dumps(dict(reason=str(e),child_exit=child.returncode,elapsed_seconds=time.monotonic()-start),indent=2)+'\n');raise
 print(json.dumps(dict(stage='resource_monitor_complete',child_exit=child.returncode,elapsed_seconds=round(time.monotonic()-start,1))),flush=True);sys.exit(child.returncode)
