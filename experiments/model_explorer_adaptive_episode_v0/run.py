"""Run real bounded episodes, or replay all gates from the public transcript."""

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import urllib.request

from experiments.model_explorer_integration_v0.campaign import verify_frozen
from .adapter import MODEL, OPTIONS, SYSTEMS, LocalModel
from .campaign import execute, summarize


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Replay:
    def __init__(self, path):
        self.calls = [json.loads(line) for line in path.read_text().splitlines()]
        self.index = 0

    def generate(self, prompt, seed, condition):
        call = self.calls[self.index]["model_call"]
        self.index += 1
        assert call["exact_prompt"] == prompt
        assert call["system"] == SYSTEMS[condition]
        assert call["model"] == MODEL and call["options"] == {**OPTIONS,"seed":seed}
        return call["raw_output"], call["response_metadata"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output",type=Path)
    parser.add_argument("--replay",type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    frozen = verify_frozen(root)
    assert json.loads((Path(__file__).parent/"frozen-framework.json").read_text()) == frozen
    output = args.output or Path(tempfile.mkdtemp(prefix="horus-adaptive-v0-"))
    if output.resolve().is_relative_to(root):
        raise ValueError("execution evidence must be outside source")
    if args.output:
        output.mkdir(parents=True,exist_ok=False)
    metadata = dict(model=MODEL,systems=SYSTEMS,options=OPTIONS,frozen=frozen,
        execution="replay" if args.replay else "real_inference")
    if args.replay:
        transport=Replay(args.replay)
    else:
        transport=LocalModel()
        def get(endpoint,payload=None):
            request=urllib.request.Request(transport.endpoint+"/api/"+endpoint,
                data=None if payload is None else json.dumps(payload).encode(),
                headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(request,timeout=30) as response:
                return json.load(response)
        metadata["server"]=get("version")
        assert metadata["server"]["version"]=="0.1.16"
        installed=next(m for m in get("tags")["models"] if m["name"]==MODEL)
        assert installed["digest"]==frozen["model"]["manifest_digest"]
        metadata["installed_model"]=installed
        shown=get("show",dict(name=MODEL))
        metadata["template"]={k:shown[k] for k in ("template","system","parameters","details") if k in shown}
        assert shown["template"] == "<|im_start|>system\n{{ .System }}<|im_end|>\n<|im_start|>user\n{{ .Prompt }}<|im_end|>\n<|im_start|>assistant\n"
    (output/"metadata.json").write_text(json.dumps(metadata,indent=2)+"\n")
    with (output/"steps.jsonl").open("w") as full,(output/"model-calls.jsonl").open("w") as calls:
        def emit(row):
            full.write(json.dumps(row,sort_keys=True)+"\n");full.flush()
            public={k:row[k] for k in ("descriptor","model_call","authorization","world_event",
                "original_prediction","violations","projection_verified","bounds","matched_initial_state_verified")}
            calls.write(json.dumps(public,sort_keys=True)+"\n");calls.flush()
            d=row["descriptor"]
            print(f"{d['index']+1}/288 pair={d['pair']} arm={d['condition']} t={d['decision']} "
                f"action={row['parsed_action']} commit={row['authorization']['committed']} violations={row['violations']}",flush=True)
        try:
            rows=execute(transport,emit)
        except Exception as error:
            (output/"execution-error.json").write_text(json.dumps(dict(type=type(error).__name__,message=str(error)),indent=2)+"\n")
            raise
    if args.replay:
        assert transport.index==len(transport.calls)
    verify_frozen(root)
    summary=summarize(rows)
    (output/"episode-analysis.json").write_text(json.dumps(summary["episodes"],indent=2)+"\n")
    summary["episodes"]=[{k:v for k,v in e.items() if k not in ("repeated_visits","decisions_detail")}
                         for e in summary["episodes"]]
    source_paths=list(Path(__file__).parent.glob("*.py"))+[
        root/"research/model-explorer-adaptive-episode-v0-preregistration.md",Path(__file__).parent/"frozen-framework.json"]
    result=dict(summary=summary, model=metadata,
        source_sha256={str(p.relative_to(root)):digest(p) for p in sorted(source_paths)},
        evidence_sha256={name:digest(output/name) for name in ("model-calls.jsonl","steps.jsonl","episode-analysis.json")})
    (output/"results.json").write_text(json.dumps(result,indent=2)+"\n")
    if args.replay:
        for name in ("model-calls.jsonl","steps.jsonl","episode-analysis.json"):
            expected=args.replay.parent/name
            if not expected.exists():
                raise RuntimeError("complete replay evidence missing: "+name)
            assert expected.read_bytes()==(output/name).read_bytes(), "replay differs: "+name
        original=json.loads((args.replay.parent/"results.json").read_text())
        assert original["summary"]==summary, "replayed metric summary differs"
        assert original["source_sha256"]==result["source_sha256"], "registered source differs"
        print("Exact replay: calls, full steps, episode analysis, and summary identical.")
    print(json.dumps({k:v for k,v in summary.items() if k not in ("episodes","arms")},indent=2))
    print("Evidence:",output)
    raise SystemExit(0 if summary["framework_integrity"]=="PASS" else 2)


if __name__=="__main__":
    main()
