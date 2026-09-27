"""Add actual replay and preservation assurance without changing raw study results."""
import argparse,json
from pathlib import Path
from .run import FILES
from .contexts import frozen,source_hashes
from .analysis import metrics,criteria
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import atomic_write,file_digest


def main():
    p=argparse.ArgumentParser();p.add_argument('--live',type=Path,required=True);p.add_argument('--replay',type=Path,required=True)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--assurance',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();reg=frozen()
    for name in FILES:assert (a.live/name).read_bytes()==(a.replay/name).read_bytes(),name
    assert source_hashes(a.source)==reg['r1_evidence_sha256']
    proof=json.loads(a.assurance.read_text());assert proof['passed'] and proof['new_inference']==0
    result=json.loads((a.live/'metrics.json').read_text())
    result['primary_criteria']=criteria(result,True,True,True,True)
    result['classification']='AUTHENTIC-HISTORY MAP EFFECT '+('SUPPORTED' if all(result['primary_criteria'].values()) else 'NOT ESTABLISHED')
    result['status']='FINAL';result['evidence_sha256']={name:file_digest(a.live/name) for name in FILES}
    result['historical_preservation']=proof
    result['pairs']=json.loads((a.live/'pairs.json').read_text())
    atomic_write(a.output,result)
    print(result['classification'])


if __name__=='__main__':main()
