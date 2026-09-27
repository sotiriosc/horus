"""Inspect the Horus v0.13 canonical problem graph."""
import argparse,json
from pathlib import Path
from .problem_manager import ProblemManager

def main(argv=None):
    parser=argparse.ArgumentParser(); parser.add_argument("command",choices=("list","show","rebuild"))
    parser.add_argument("--registry",type=Path,required=True); parser.add_argument("--problem-id")
    args=parser.parse_args(argv)
    with ProblemManager(args.registry) as manager:
        if args.command=="rebuild": manager.rebuild_index(); result={"rebuilt":True,"stream_count":manager.state["stream_count"]}
        elif args.command=="show":
            if not args.problem_id or args.problem_id not in manager.state["problems"]: raise ValueError("known --problem-id required")
            result=manager.state["problems"][args.problem_id]
        else:
            result=[{k:p[k] for k in ("problem_id","problem_type","scope","owner","lifecycle_state","capability_assessment","requested_capability")}
                    for p in manager.state["problems"].values()]
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__": main()
