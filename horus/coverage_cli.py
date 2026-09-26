"""One-shot CLI for Horus v0.11 bounded evidence coverage."""
import argparse,json
from pathlib import Path
from .coverage_extension import analyze_coverage_extension,run_coverage_extension
from .grounded_learning import atomic_json

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("command",choices=("run","report"))
    p.add_argument("--session",type=Path,required=True); p.add_argument("--registry",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True); p.add_argument("--run-result",type=Path)
    a=p.parse_args(argv)
    if a.output.exists(): raise FileExistsError(a.output)
    if a.command=="run": result=run_coverage_extension(a.session,a.registry); atomic_json(a.output,result)
    else:
        if a.run_result is None: raise ValueError("report requires --run-result")
        result=analyze_coverage_extension(a.session,a.registry,json.loads(a.run_result.read_text()),a.output)
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=="__main__": main()
