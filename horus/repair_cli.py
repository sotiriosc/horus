"""Command line entry points for the one-shot Horus v0.10 repair."""
import argparse
import json
from pathlib import Path

from .grounded_learning import atomic_json
from .repair_resume import (RepairStore, analyze_repair_resume,
                            run_authorized_repair_resume)


def main(argv=None):
    parser=argparse.ArgumentParser()
    commands=parser.add_subparsers(dest="command",required=True)
    p=commands.add_parser("init")
    p.add_argument("--session",type=Path,required=True)
    p.add_argument("--registry",type=Path,required=True)
    p.add_argument("--source-report",type=Path,required=True)
    p=commands.add_parser("run")
    p.add_argument("--session",type=Path,required=True)
    p.add_argument("--registry",type=Path,required=True)
    p.add_argument("--authorization",type=Path,required=True)
    p.add_argument("--process-config",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p=commands.add_parser("report")
    p.add_argument("--session",type=Path,required=True)
    p.add_argument("--registry",type=Path,required=True)
    p.add_argument("--run-result",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=parser.parse_args(argv)
    if args.command=="init":
        result=RepairStore.initialize(args.registry,args.session,args.source_report)
    elif args.command=="run":
        if args.output.exists(): raise FileExistsError(args.output)
        result=run_authorized_repair_resume(args.session,args.registry,
                                            args.authorization,args.process_config)
        atomic_json(args.output,result)
    else:
        result=analyze_repair_resume(args.session,args.registry,
            json.loads(args.run_result.read_text()),args.output)
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__": main()
