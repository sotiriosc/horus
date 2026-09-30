"""Execute only the prospectively authorized stages; Cycle 2 requires all first gates."""
import json,subprocess,sys,time
from pathlib import Path
P=Path(__file__).resolve().parent;LOG=Path('/mnt/d/horus-research-assets/qwen3-14b-qlora-v0/campaign-logs')
if __name__=='__main__':
 LOG.mkdir(exist_ok=True);start=time.monotonic()
 for cycle in [1,2]:
  if cycle==2:
   result=json.loads((P/'cycle1-results.json').read_bytes())
   if not result['gate']['cycle2_authorized']:break
  for stage in ['harvest','train','evaluate']:
   label=f'cycle{cycle}-{stage}'
   print(json.dumps(dict(stage=label,status='starting',elapsed_seconds=round(time.monotonic()-start,1))),flush=True)
   with (LOG/(label+'.log')).open('x') as log:
    result=subprocess.run([sys.executable,str(P/'watchdog.py'),label,sys.executable,'-u',str(P/'run.py'),stage,str(cycle)],stdout=log,stderr=subprocess.STDOUT)
   if result.returncode:
    print(json.dumps(dict(stage=label,status='stopped',exit_code=result.returncode,elapsed_seconds=round(time.monotonic()-start,1))),flush=True);sys.exit(0 if result.returncode==42 else result.returncode)
   print(json.dumps(dict(stage=label,status='complete',elapsed_seconds=round(time.monotonic()-start,1))),flush=True)
 print(json.dumps(dict(status='registered_campaign_complete',elapsed_seconds=round(time.monotonic()-start,1))),flush=True)
