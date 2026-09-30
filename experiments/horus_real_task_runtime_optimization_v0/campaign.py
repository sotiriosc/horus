"""Run both frozen halves, then commit raw evidence before any scoring."""
import json,subprocess,sys
from .runtime import ROOT,PUBLIC,write

def main(freeze):
 for phase in ('half0','half1'):
  subprocess.run([sys.executable,'-m','experiments.horus_real_task_runtime_optimization_v0.worker',phase,'--freeze',freeze],cwd=ROOT,check=True)
 subprocess.run([sys.executable,'-m','experiments.horus_real_task_runtime_optimization_v0.postflight',freeze],cwd=ROOT,check=True)
 names=['raw','raw-freeze.json','postflight.json','private-evidence-manifest.json','restart.json']
 subprocess.run(['git','add',*[str((PUBLIC/n).relative_to(ROOT)) for n in names]],cwd=ROOT,check=True)
 subprocess.run(['git','commit','-q','-m','Freeze real runtime campaign raw evidence before scientific analysis'],cwd=ROOT,check=True)
 sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()
 print(json.dumps(dict(stage='RAW_PRE_ANALYSIS_COMMITTED',commit=sha,scoring_performed=False)),flush=True)
if __name__=='__main__':main(sys.argv[1])
