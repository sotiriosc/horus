import argparse,json
from pathlib import Path
from .grounded_learning import atomic_json
from .problem_ownership_run import run

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--session",type=Path,required=True)
    p.add_argument("--registry",type=Path,required=True); p.add_argument("--output",type=Path,required=True)
    a=p.parse_args(argv)
    if a.output.exists(): raise FileExistsError(a.output)
    result=run(a.session,a.registry); atomic_json(a.output,result)
    print(json.dumps({k:result[k] for k in ("status","fresh_decisions","model_calls","route_exercised")},indent=2))
if __name__=="__main__": main()
