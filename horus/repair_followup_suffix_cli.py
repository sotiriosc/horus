import argparse,json
from pathlib import Path

from .grounded_learning import atomic_json
from .repair_followup_suffix import run


def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("--session",type=Path,required=True)
    parser.add_argument("--registry",type=Path,required=True)
    parser.add_argument("--repair-root",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args(argv)
    if args.output.exists(): raise FileExistsError(args.output)
    result=run(args.session,args.registry,args.repair_root)
    atomic_json(args.output,result)
    print(json.dumps({k:result.get(k) for k in (
        "status","total_live_model_calls","new_authenticated_receipts",
        "pr0002_unchanged","training_runs")},indent=2))


if __name__=="__main__": main()
