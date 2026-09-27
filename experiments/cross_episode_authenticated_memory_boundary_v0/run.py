"""Deterministic zero-inference diagnostic and exact reconstruction replay."""
import argparse,json
from pathlib import Path
from .campaign import run,encoded,frozen,ROOT
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import require_durable,atomic_write

FILES=('results.json','details.json')


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path)
    p.add_argument('--contradiction-source',required=True,type=Path);p.add_argument('--replay',type=Path)
    a=p.parse_args();require_durable(a.output,ROOT)
    if a.output.exists():raise ValueError('use a fresh evidence directory')
    before=frozen();result,details=run(a.contradiction_source);assert frozen()==before
    a.output.mkdir(parents=True,exist_ok=False)
    for name,value in [('results.json',result),('details.json',details)]:
        atomic_write(a.output/name,value)
        if a.replay:assert (a.output/name).read_bytes()==(a.replay/name).read_bytes(),name
    print(result['classification']);print(result['missing_property'])
    print('ZERO MODEL CALLS. '+('Both registered files byte-identical.' if a.replay else 'Diagnostic saved; final replay/regression assurance pending.'))


if __name__=='__main__':main()
