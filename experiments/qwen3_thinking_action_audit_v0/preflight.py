"""Three preregistered strict-schema native-thinking interface probes."""
from argparse import ArgumentParser
from pathlib import Path
import json
from horus.live import _atomic_write
from .shared import STUDY,direct_action,verify_model,verify_sources

SEEDS=(88101,88102,88103)


def run(private):
    verify_sources();verify_model()
    fixtures=json.loads((STUDY.parent/'qwen3-grounded-agent-substitution-v0/stage-a-fixtures.json').read_text())['fixtures']
    fixture=fixtures['D'];projection=fixture['projection'];allowed=fixture['route']['candidates']
    public=[]
    for n,seed in enumerate(SEEDS,1):
        result=direct_action(projection,allowed,seed,private/f'probe-{n}')
        public.append(dict(probe=n,seed=seed,**result))
        _atomic_write(STUDY/'preflight-result.json',dict(probes=public,
            status='RUNNING' if result['status']=='VALID' else 'INTERFACE_INCOMPATIBLE'))
        print(json.dumps(dict(probe=n,status=result['status'],action=result.get('action'),
            wall_seconds=result['wall_seconds'])),flush=True)
        if result['status']!='VALID':return 'INTERFACE_INCOMPATIBLE'
    _atomic_write(STUDY/'preflight-result.json',dict(probes=public,status='PASS'))
    return 'PASS'

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--private-root',required=True,type=Path)
    a=p.parse_args();status=run(a.private_root)
    if status!='PASS':raise SystemExit(2)
