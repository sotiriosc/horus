"""Prospective registration, one bounded live run, and exact recorded-response replay."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

from experiments.model_explorer_integration_v0.campaign import verify_frozen
from experiments.model_map_proposal_v0.adapter import MODEL, OPTIONS, SYSTEM
from experiments.model_map_proposal_v0.transport import LocalModel
from .campaign import registration, probe, controls
from .analysis import summarize

FILES=("registered-prompts.json","model-calls.jsonl","steps.jsonl","setup.jsonl","controls.jsonl")


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def frozen_check(root):
    frozen=json.loads((Path(__file__).parent/"frozen-inputs.json").read_text())
    original=verify_frozen(root)
    assert all(frozen[k]==original[k] for k in original)
    assert all(digest(root/p)==h for p,h in frozen["additional_source_sha256"].items())
    return frozen


def sources(root):
    package=Path(__file__).parent
    paths=list(package.glob("*.py"))+[package/"frozen-inputs.json",package/"registration-digests.json",package/"preflight-results.json",
        root/"research/model-map-established-prior-revision-v1-preregistration.md"]
    return {str(p.relative_to(root)):digest(p) for p in sorted(paths)}


class Replay:
    def __init__(self,path):
        self.calls=[json.loads(line) for line in path.read_text().splitlines()];self.index=0
    def generate(self,prompt,seed):
        call=self.calls[self.index]["model_call"];self.index+=1
        assert call["exact_prompt"]==prompt and call["options"]=={**OPTIONS,"seed":seed}
        assert call["model"]==MODEL and call["system"]==SYSTEM
        return call["raw_output"],call["response_metadata"]


def server_metadata(transport,frozen,proof):
    assert proof["manifest_sha256"]==frozen["model"]["manifest_digest"]
    assert proof["weights_sha256"]==frozen["model"]["weights_digest"]
    def get(name,payload=None):
        req=urllib.request.Request(transport.endpoint+"/api/"+name,
            data=None if payload is None else json.dumps(payload).encode(),headers={"Content-Type":"application/json"})
        with urllib.request.urlopen(req,timeout=30) as response:return json.load(response)
    version=get("version");assert version["version"]=="0.1.16"
    model=next(m for m in get("tags")["models"] if m["name"]==MODEL)
    assert model["digest"]==frozen["model"]["manifest_digest"]
    shown=get("show",dict(name=MODEL))
    assert shown["template"]=="<|im_start|>system\n{{ .System }}<|im_end|>\n<|im_start|>user\n{{ .Prompt }}<|im_end|>\n<|im_start|>assistant\n"
    assert model["details"]["parameter_size"]=="47B" and model["details"]["quantization_level"]=="Q4_0"
    return dict(model=MODEL,system=SYSTEM,options=OPTIONS,server=version,installed_model=model,
        template={k:shown[k] for k in ("template","system","parameters","details") if k in shown},
        verified_model_bytes=proof)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--register",action="store_true")
    parser.add_argument("--replay",type=Path)
    parser.add_argument("--model-bytes",type=Path)
    args=parser.parse_args();root=Path(__file__).resolve().parents[2];package=Path(__file__).parent
    frozen=frozen_check(root)
    gate=json.loads((package/"preflight-results.json").read_text())
    assert gate["preflight"]=="PASS" and gate["actual_model_calls"]==0 and gate["exact_replay"]
    if args.output.resolve().is_relative_to(root):raise ValueError("private detailed evidence must stay outside public tree")
    args.output.mkdir(parents=True,exist_ok=False)
    plan,data=registration()
    registration_hash=hashlib.sha256(data).hexdigest()
    assert registration_hash==gate["annex_sha256"]
    if args.register:
        (args.output/"registered-prompts.json").write_bytes(data)
        digests=dict(parent="f7b16c4997625e902b59800ec1110806342a1069",calls=144,
            annex_sha256=registration_hash,prompts=[dict(index=d["index"],family=d["family"],arm=d["arm"],
                stage=d["stage"],schedule_id=d["schedule_id"],seed=d["seed"],sha256=d["prompt_sha256"]) for d in plan])
        (package/"registration-digests.json").write_text(json.dumps(digests,indent=2)+"\n")
        print("Registered 144 exact prompts, matched histories/order/seeds, zero inference. Annex:",registration_hash)
        return
    registered=json.loads((package/"registration-digests.json").read_text())
    assert registration_hash==registered["annex_sha256"] and registered["calls"]==len(plan)==144
    source_hashes=sources(root)
    if args.replay:
        transport=Replay(args.replay)
        metadata=json.loads((args.replay.parent/"metadata.json").read_text())
    else:
        if args.model_bytes is None:raise ValueError("verified model-byte proof required before inference")
        transport=LocalModel();metadata=server_metadata(transport,frozen,json.loads(args.model_bytes.read_text()))
    (args.output/"metadata.json").write_text(json.dumps(metadata,indent=2)+"\n")
    (args.output/"registered-prompts.json").write_bytes(data)
    rows=[];synthetic=[];setup_count=0
    try:
        with (args.output/"model-calls.jsonl").open("w") as calls,(args.output/"steps.jsonl").open("w") as steps,\
             (args.output/"setup.jsonl").open("w") as setups,(args.output/"controls.jsonl").open("w") as control_file:
            def emit_call(row):calls.write(json.dumps(row,sort_keys=True)+"\n");calls.flush()
            def emit_setup(row):
                nonlocal setup_count
                setup_count+=1;setups.write(json.dumps(row,sort_keys=True)+"\n");setups.flush()
            for d in plan:
                assert sources(root)==source_hashes
                row=probe(transport,d,emit_setup,emit_call)
                steps.write(json.dumps(row,sort_keys=True)+"\n");steps.flush();rows.append(row)
                print(f"{len(rows)}/144 {d['family']} {d['arm']} {d['stage']} j={d['schedule_id']} raw={row['model_call']['raw_output']!r} prediction={row['model_call']['parsed_prediction']} commit={row['probe']['authorization']['committed']} errors={row['probe']['errors']}",flush=True)
                if row["probe"]["errors"] or not row["history_retained"]:
                    raise RuntimeError("protected failure; stop immediately, no patch")
            synthetic=controls(plan)
            for row in synthetic:control_file.write(json.dumps(row,sort_keys=True)+"\n")
    except Exception as exc:
        (args.output/"STOP.json").write_text(json.dumps(dict(error_type=type(exc).__name__,reason=str(exc),
            completed_probe_rows=len(rows),summary=summarize(rows,synthetic)),indent=2)+"\n")
        raise
    assert frozen_check(root)==frozen and source_hashes==sources(root)
    summary=summarize(rows,synthetic);summary["measured_setup_transactions"]=setup_count
    result=dict(summary=summary,model=metadata,source_sha256=source_hashes,
        evidence_sha256={name:digest(args.output/name) for name in FILES})
    (args.output/"results.json").write_text(json.dumps(result,indent=2)+"\n")
    if args.replay:
        assert transport.index==len(transport.calls)==144
        for name in FILES+("metadata.json","results.json"):
            assert (args.output/name).read_bytes()==(args.replay.parent/name).read_bytes(),name
        print("Exact recorded-response replay: all evidence and compact results byte-identical; zero inference.")
    print(summary["overall"])
    for family,f in summary["families"].items():print(family,f["cells"],f["criteria"],f["revision"])


if __name__=="__main__":main()
