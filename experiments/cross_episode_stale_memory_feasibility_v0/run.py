"""Deterministic feasibility generation/replay; socket access prohibited."""
import argparse,json
from pathlib import Path
from .campaign import run,frozen,ROOT,A,B,C,HistoryFailure
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import atomic_write,require_durable
FILES=('results.json','details.json')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);p.add_argument('--replay',type=Path)
    args=p.parse_args();out=require_durable(args.output,ROOT)
    if out.exists():raise ValueError('fresh evidence directory required')
    out.mkdir(parents=True);before=frozen()
    try:
        result,details=run();assert frozen()==before
        atomic_write(out/'results.json',result);atomic_write(out/'details.json',details)
        if args.replay:
            for name in FILES:assert (out/name).read_bytes()==(args.replay/name).read_bytes(),name
    except Exception as exc:
        atomic_write(out/'STOP.json',dict(classification=B if isinstance(exc,HistoryFailure) else C,reason=str(exc),
            error_type=type(exc).__name__,actual_model_calls=0,no_model_followup_authorized=True))
        raise
    print(result['eligible_classification']+' (pending replay/preservation gates).')
    print('ZERO MODEL CALLS; native state Recovery:',result['native_state_Recovery_calls'])
    if args.replay:print('PASS: both registered files byte-identical; zero inference.')
if __name__=='__main__':main()
