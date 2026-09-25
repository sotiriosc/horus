"""Deterministic zero-inference campaign or exact replay; no live mode exists."""
import argparse,json
from pathlib import Path
from .campaign import run
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import atomic_write,require_durable
from .campaign import ROOT

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--replay',type=Path);a=p.parse_args();out=require_durable(a.output,ROOT)
 if out.exists():raise RuntimeError('existing evidence directory')
 out.mkdir();result,details=run();atomic_write(out/'results.json',result);atomic_write(out/'details.json',details)
 if a.replay:
  for n in ('results.json','details.json'):assert (out/n).read_bytes()==(a.replay/n).read_bytes(),n
  print('PASS: two deterministic files byte-identical; ZERO MODEL CALLS.')
 print(result['classification'],result['synthetic_cases'],'synthetic cases, ZERO MODEL CALLS.')
if __name__=='__main__':main()
