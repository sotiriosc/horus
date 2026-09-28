"""Allowlisted sanitized result export from locally signed private archive."""
from argparse import ArgumentParser
from pathlib import Path
import json
from horus.live import _atomic_write
from .analyze import analyze

def export(private_root,output):
    result=analyze(private_root)
    # Analyzer exposes only derived decision values, safe receipt identities,
    # replay verdicts and private-file digests; raw call streams and keys stay local.
    _atomic_write(output,result)
    return result

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--private-root',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();result=export(a.private_root,a.output)
    print(json.dumps(dict(status=result['campaign_status'],classification=result['classification'],
        relative_acquisition_ABCD_cases=result['relative_acquisition_ABCD_cases']),sort_keys=True))
