"""Run the deterministic boundary campaign or exact reconstruction replay."""
import argparse,json
from pathlib import Path
from .campaign import run,encoded,frozen,ROOT
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import require_durable,fsync_dir

FILES=('results.json','details.json')

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);p.add_argument('--replay',type=Path)
    a=p.parse_args();require_durable(a.output,ROOT);before=frozen();result,details=run();assert frozen()==before
    a.output.mkdir(parents=True,exist_ok=False)
    import os
    for name,value in [('results.json',result),('details.json',details)]:
        with (a.output/name).open('x') as s:s.write(encoded(value));s.flush();os.fsync(s.fileno())
        if a.replay:assert (a.output/name).read_bytes()==(a.replay/name).read_bytes(),name
    fsync_dir(a.output);fsync_dir(a.output.parent)
    print(result['eligible_classification']);print('Final classification awaits actual replay and regressions.')
    print('ZERO MODEL CALLS; '+str(result['failure_cases_atomic'])+' atomic failure cases.')
    if a.replay:print('PASS: both registered files byte-identical.')

if __name__=='__main__':main()
