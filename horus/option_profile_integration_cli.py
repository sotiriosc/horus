import argparse,json
from pathlib import Path

from .grounded_learning import atomic_json
from .option_profile_integration import run


def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("--session",type=Path,required=True)
    parser.add_argument("--registry",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args(argv)
    if args.output.exists(): raise FileExistsError(args.output)
    result=run(args.session,args.registry); atomic_json(args.output,result)
    print(json.dumps({k:result[k] for k in ("status","fresh_decisions","model_calls",
        "frozen_selected_action","pr0003_unchanged")},indent=2))


if __name__=="__main__": main()
