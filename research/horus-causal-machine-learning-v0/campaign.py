"""Only the registered stages, with conditional second cycle and durable progress."""
import fcntl,json,subprocess,sys,time
from pathlib import Path
P=Path(__file__).resolve().parent;ASSETS=Path('/mnt/d/horus-research-assets/causal-machine-v0');LOG=ASSETS/'campaign-logs'
if __name__=='__main__':
 LOG.mkdir(exist_ok=True);lock=(ASSETS/'campaign.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);start=time.monotonic()
 for cycle in [1,2]:
  resultfile=P/f'cycle{cycle}-results.json'
  if cycle==2 and not json.loads((P/'cycle1-results.json').read_bytes())['gate']['cycle2_authorized']:break
  if resultfile.exists():continue
  for stage in ['harvest','train','evaluate']:
   marker=P/(f'D{cycle}-composition.json' if stage=='harvest' else f'C{cycle}-artifact-freeze.json' if stage=='train' else f'cycle{cycle}-results.json')
   if marker.exists():
    tracked=subprocess.run(['git','diff','--exit-code','HEAD','--',str(marker)],cwd=P.parents[1],stdout=subprocess.DEVNULL).returncode==0
    assert tracked and subprocess.run(['git','ls-files','--error-unmatch',str(marker)],cwd=P.parents[1],stdout=subprocess.DEVNULL).returncode==0
    continue
   label=f'cycle{cycle}-{stage}';event=dict(stage=label,status='starting',elapsed_seconds=round(time.monotonic()-start,1));print(json.dumps(event),flush=True)
   attempt=len(list(LOG.glob(label+'-attempt-*.log')))+1;logpath=LOG/f'{label}-attempt-{attempt}.log'
   with logpath.open('x') as log:result=subprocess.run([sys.executable,str(P/'watchdog.py'),label,sys.executable,'-u',str(P/'run.py'),stage,str(cycle)],stdout=log,stderr=subprocess.STDOUT)
   if result.returncode:
    print(json.dumps(dict(stage=label,status='infrastructure_or_integrity_stop',exit_code=result.returncode,log=logpath.name)),flush=True);sys.exit(result.returncode)
   print(json.dumps(dict(stage=label,status='complete',elapsed_seconds=round(time.monotonic()-start,1))),flush=True)
   if resultfile.exists() and 'admission_stop' in json.loads(resultfile.read_bytes()):break
 print(json.dumps(dict(status='registered_campaign_complete',elapsed_seconds=round(time.monotonic()-start,1))),flush=True)
