from argparse import ArgumentParser
import json
from pathlib import Path
import subprocess
import sys
from horus.live import SessionStore, _atomic_write
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory
from .protocol import ARMS,SCHEDULES,MODEL_LOGICAL_CEILING,MODEL_PHYSICAL_CEILING


def main(output):
    from .preflight import main as preflight
    preflight()
    if output.exists():raise RuntimeError('single-use campaign output already exists')
    output.mkdir(parents=True)
    for schedule in SCHEDULES:
        root=output/'schedules'/schedule
        for arm in ARMS:
            armroot=root/'work'/arm;armroot.mkdir(parents=True)
            with SessionStore(armroot/'session',False):pass
            with ModernMemory(armroot/'memory.sqlite3',True):pass
            (root/arm).symlink_to(Path('current')/arm,target_is_directory=True)
    for stage in ('SUSTAINED1','SUSTAINED2','ANOMALY','EXCURSION','NOISE_THEN_CHANGE'):
        subprocess.run([sys.executable,'-m',
            'experiments.grounded_uncertainty_state_v0.worker',stage,
            '--output',str(output)],check=True)
    result=dict(status='CAMPAIGN_COMPLETE',schedules=list(SCHEDULES),
        conditions=list(ARMS),events_per_arm=sum(map(len,SCHEDULES.values())),
        model_logical_ceiling=MODEL_LOGICAL_CEILING,
        model_physical_ceiling=MODEL_PHYSICAL_CEILING)
    _atomic_write(output/'campaign-complete.json',result)
    return result

if __name__=='__main__':
    parser=ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    print(json.dumps(main(parser.parse_args().output),sort_keys=True))
