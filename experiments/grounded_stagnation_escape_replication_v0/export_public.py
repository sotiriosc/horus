"""Export allowlisted replay result; raw model calls and keys remain local."""
from argparse import ArgumentParser
from pathlib import Path
import json
from horus.live import _atomic_write
from .analyze import audit

def export(private_root,output):
    result=audit(private_root)
    _atomic_write(output,result)
    return result

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--private-root',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();r=export(a.private_root,a.output)
    print(json.dumps(dict(status=r['campaign_status'],classification=r['classification'],
        recommendation=r['promotion_recommendation']),sort_keys=True))
