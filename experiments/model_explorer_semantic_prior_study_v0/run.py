"""Execute or exactly replay the registered isolated-fixture study."""

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import urllib.request

from experiments.model_explorer_integration_v0.campaign import verify_frozen
from .adapter import MODEL,OPTIONS,SYSTEM,LocalModel
from .campaign import registration,execute
from .analysis import summarize

EVIDENCE=("model-calls.jsonl","steps.jsonl","setup.jsonl","controls.jsonl","registered-fixtures-and-prompts.json")


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hashes(root):
    pkg=Path(__file__).parent
    paths=list(pkg.glob("*.py"))+[pkg/"frozen-framework.json",pkg/"registration-digests.json",
        root/"research/model-explorer-semantic-prior-study-v0-preregistration.md"]
    return {str(p.relative_to(root)):sha(p) for p in sorted(paths)}


class Replay:
    def __init__(self,path):
        self.calls=[json.loads(line) for line in path.read_text().splitlines()];self.index=0

    def generate(self,prompt,seed):
        call=self.calls[self.index]["model_call"];self.index+=1
        assert call["model"]==MODEL and call["system"]==SYSTEM
        assert call["exact_prompt"]==prompt and call["options"]=={**OPTIONS,"seed":seed}
        return call["raw_output"],call["response_metadata"]


def run_campaign(transport,output,registered,data,progress=True):
    (output/"registered-fixtures-and-prompts.json").write_bytes(data)
    setup_count=0
    with (output/"steps.jsonl").open("w") as steps,(output/"model-calls.jsonl").open("w") as calls,\
         (output/"setup.jsonl").open("w") as setups,(output/"controls.jsonl").open("w") as controls:
        def emit_setup(row):
            nonlocal setup_count
            setup_count+=1;setups.write(json.dumps(row,sort_keys=True)+"\n")
        def emit(row):
            if row["role"]=="control":controls.write(json.dumps(row,sort_keys=True)+"\n");return
            steps.write(json.dumps(row,sort_keys=True)+"\n");steps.flush()
            fields=("descriptor","model_call","authorization","world_event","original_prediction","violations","projection_verified","pair_verified","bounds")
            calls.write(json.dumps({k:row[k] for k in fields},sort_keys=True)+"\n");calls.flush()
            d=row["descriptor"]
            if progress:print(f"{d['index']+1}/288 {d['condition']} state={d['state']} {d['relation']} "
                f"seed={d['seed']} surface={row['model_call']['parsed_surface_proposal']} action={row['parsed_action']} "
                f"commit={row['authorization']['committed']} violations={row['violations']}",flush=True)
        rows=execute(transport,emit,emit_setup,registered)
    return summarize(rows,setup_count)


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--output",type=Path);parser.add_argument("--replay",type=Path)
    args=parser.parse_args();root=Path(__file__).resolve().parents[2]
    frozen=verify_frozen(root)
    assert frozen==json.loads((Path(__file__).parent/"frozen-framework.json").read_text())
    registered,data=registration()
    output=args.output or Path(tempfile.mkdtemp(prefix="horus-semantic-prior-v0-"))
    if output.resolve().is_relative_to(root):raise ValueError("detailed mapping/evidence archive must remain outside public source")
    if args.output:output.mkdir(parents=True,exist_ok=False)
    before_hashes=source_hashes(root)
    metadata=dict(model=MODEL,system=SYSTEM,options=OPTIONS,frozen=frozen,execution="replay" if args.replay else "real_inference")
    if args.replay:transport=Replay(args.replay)
    else:
        transport=LocalModel()
        def get(endpoint,payload=None):
            request=urllib.request.Request(transport.endpoint+"/api/"+endpoint,
                data=None if payload is None else json.dumps(payload).encode(),headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(request,timeout=30) as response:return json.load(response)
        metadata["server"]=get("version");assert metadata["server"]["version"]=="0.1.16"
        model=next(m for m in get("tags")["models"] if m["name"]==MODEL)
        assert model["digest"]==frozen["model"]["manifest_digest"];metadata["installed_model"]=model
        shown=get("show",dict(name=MODEL));metadata["template"]={k:shown[k] for k in ("template","system","parameters","details") if k in shown}
        assert shown["template"]=="<|im_start|>system\n{{ .System }}<|im_end|>\n<|im_start|>user\n{{ .Prompt }}<|im_end|>\n<|im_start|>assistant\n"
    (output/"metadata.json").write_text(json.dumps(metadata,indent=2)+"\n")
    try:summary=run_campaign(transport,output,registered,data)
    except Exception as error:
        (output/"execution-error.json").write_text(json.dumps(dict(type=type(error).__name__,message=str(error)),indent=2)+"\n")
        raise
    if args.replay:assert transport.index==len(transport.calls)==288
    verify_frozen(root);assert before_hashes==source_hashes(root)
    result=dict(summary=summary,model=metadata,source_sha256=before_hashes,evidence_sha256={n:sha(output/n) for n in EVIDENCE})
    (output/"results.json").write_text(json.dumps(result,indent=2)+"\n")
    if args.replay:
        for n in EVIDENCE:assert (args.replay.parent/n).read_bytes()==(output/n).read_bytes(),"replay differs: "+n
        original=json.loads((args.replay.parent/"results.json").read_text())
        assert original["summary"]==json.loads(json.dumps(summary)),"JSON summary differs"
        assert original["source_sha256"]==before_hashes,"registered source differs"
        print("Exact replay: calls, full measured steps, setup, controls, registered prompts, and JSON summary identical.")
    print(json.dumps({k:v for k,v in summary.items() if k in ("framework_integrity","real_model_calls","valid_proposals","controls","control_commits","setup_transactions","matched_state_checks","complete")},indent=2))
    for name,c in summary["relations"].items():print(name,c["arms"]["S"]["value_following"],c["arms"]["O"]["value_following"],c["semantic_prior_effect"])
    print("Evidence:",output)
    raise SystemExit(0 if summary["framework_integrity"]=="PASS" else 2)


if __name__=="__main__":main()
