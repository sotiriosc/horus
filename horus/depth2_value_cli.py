import argparse,json
from pathlib import Path
from .depth2_value import run
from .grounded_learning import atomic_json

def main(argv=None):
    parser=argparse.ArgumentParser(); parser.add_argument("--session",type=Path,required=True)
    parser.add_argument("--registry",type=Path,required=True); parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args(argv)
    if args.output.exists(): raise FileExistsError(args.output)
    result=run(args.session,args.registry); atomic_json(args.output,result)
    print(json.dumps({k:result.get(k) for k in ("status","model_calls","selected_action")},indent=2))

if __name__=="__main__": main()
