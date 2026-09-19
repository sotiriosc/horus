"""Run/replay the feasibility diagnostic; never loads or calls a model."""

import argparse
import hashlib
import json
from pathlib import Path
import tempfile

from experiments.model_explorer_integration_v0.campaign import verify_frozen
from .preflight import run_preflight


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path)
    parser.add_argument("--replay",type=Path,help="retained preflight evidence directory, not model transcript")
    args=parser.parse_args();root=Path(__file__).resolve().parents[2];pkg=Path(__file__).parent
    frozen=verify_frozen(root)
    assert frozen==json.loads((pkg/"frozen-framework.json").read_text())
    paths=list(pkg.glob("*.py"))+[pkg/"frozen-framework.json",root/"research/model-explorer-contradiction-revision-v0-preregistration.md",
        root/"experiments/model_explorer_integration_v0/campaign.py"]
    sources={str(p.relative_to(root)):digest(p) for p in sorted(paths)}
    output=args.output or Path(tempfile.mkdtemp(prefix="horus-contradiction-preflight-"))
    if output.resolve().is_relative_to(root):raise ValueError("raw evidence must remain outside the public tree")
    if args.output:output.mkdir(parents=True,exist_ok=False)
    data=run_preflight()
    (output/"preflight.json").write_text(json.dumps(data,indent=2)+"\n")
    verify_frozen(root)
    assert sources=={str(p.relative_to(root)):digest(p) for p in sorted(paths)}
    result=dict(summary=data["summary"],frozen=frozen,source_sha256=sources,evidence_sha256={"preflight.json":digest(output/"preflight.json")})
    (output/"results.json").write_text(json.dumps(result,indent=2)+"\n")
    if args.replay:
        for name in ("preflight.json","results.json"):
            assert (args.replay/name).read_bytes()==(output/name).read_bytes(),name
        print("Exact preflight replay: diagnostic evidence and compact results byte-identical; zero inference.")
    print(json.dumps(data["summary"],indent=2))
    print("Evidence:",output)
    if not args.replay and data["summary"]["feasibility"]!="FEASIBLE":raise SystemExit(2)


if __name__=="__main__":main()
