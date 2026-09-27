from argparse import ArgumentParser
import json
from pathlib import Path
import subprocess
import sys
from horus.live import SessionStore,_atomic_write
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory
from .protocol import ARMS,SCENARIOS,MODEL_LOGICAL_CEILING,TOTAL_LOGICAL_CEILING,TOTAL_PHYSICAL_CEILING

def main(output):
    from .preflight import main as preflight
    preflight()
    if output.exists():raise RuntimeError('single-use campaign output already exists')
    output.mkdir(parents=True)
    for scenario in SCENARIOS:
        for arm in ARMS:
            root=output/'scenarios'/scenario/'work'/arm;root.mkdir(parents=True)
            with SessionStore(root/'session',False):pass
            with ModernMemory(root/'memory.sqlite3',True):pass
    for scenario,spec in SCENARIOS.items():
        stages=('H1','H2') if spec.get('restart') else ('single',)
        for stage in stages:
            subprocess.run([sys.executable,'-m','experiments.grounded_hybrid_controller_v0.worker',
                scenario,'--stage',stage,'--output',str(output)],check=True)
    result=dict(status='CAMPAIGN_COMPLETE',scenarios=list(SCENARIOS),arms=list(ARMS),
        model_logical_ceiling=MODEL_LOGICAL_CEILING,
        total_logical_ceiling=TOTAL_LOGICAL_CEILING,total_physical_ceiling=TOTAL_PHYSICAL_CEILING)
    _atomic_write(output/'campaign-complete.json',result)
    return result
if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--output',type=Path,required=True)
    print(json.dumps(main(p.parse_args().output),sort_keys=True))
