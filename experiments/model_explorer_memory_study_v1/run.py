"""Execute the frozen 224-call study or replay its exact model transcript."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import tempfile
import urllib.request

from experiments.model_explorer_memory_study_v1.adapter import LocalModel, MODEL, OPTIONS, SYSTEM
from experiments.model_explorer_memory_study_v1.campaign import execute, summarize
from experiments.model_explorer_integration_v0.campaign import verify_frozen


class Replay:
    def __init__(self, path):
        self.calls = [json.loads(line) for line in path.read_text().splitlines()]
        self.index = 0

    def generate(self, prompt, seed):
        call = self.calls[self.index]["model_call"]
        self.index += 1
        assert call["exact_prompt"] == prompt
        assert call["options"] == {**OPTIONS, "seed": seed}
        assert call["model"] == MODEL and call["system"] == SYSTEM
        return call["raw_output"], call["response_metadata"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--replay", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    frozen = verify_frozen(root)
    output = args.output or Path(tempfile.mkdtemp(prefix="horus-memory-study-v1-"))
    if output.resolve().is_relative_to(root):
        raise ValueError("raw evidence must be outside source")
    if args.output:
        output.mkdir(parents=True, exist_ok=False)
    metadata = dict(model=MODEL, system=SYSTEM, options=OPTIONS, frozen=frozen,
                    execution="replay" if args.replay else "real_inference")
    if args.replay:
        transport = Replay(args.replay)
    else:
        transport = LocalModel()
        def get(endpoint, payload=None):
            request = urllib.request.Request(transport.endpoint + "/api/" + endpoint,
                data=None if payload is None else json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"})
            return json.load(urllib.request.urlopen(request, timeout=30))
        metadata["server"] = get("version")
        assert metadata["server"]["version"] == "0.1.16", "registered inference engine changed"
        model = next(m for m in get("tags")["models"] if m["name"] == MODEL)
        assert model["digest"] == frozen["model"]["manifest_digest"], "registered model changed"
        metadata["installed_model"] = model
        shown = get("show", dict(name=MODEL))
        metadata["template"] = {k:shown[k] for k in ("template","system","parameters","details") if k in shown}
    (output / "metadata.json").write_text(json.dumps(metadata,indent=2)+'\n')
    setup_count = 0
    setup_violations = Counter()
    with (output/'steps.jsonl').open('w') as full, (output/'model-calls.jsonl').open('w') as transcript, (output/'setup.jsonl').open('w') as setups:
        def emit_setup(row):
            nonlocal setup_count
            if row["role"] != "setup":
                return
            setup_count += 1
            setup_violations.update(row["violations"])
            setups.write(json.dumps(row,sort_keys=True)+'\n')
        def emit(row):
            full.write(json.dumps(row,sort_keys=True)+'\n')
            full.flush()
            public = {k:row[k] for k in ("descriptor","model_call","authorization","world_event",
                       "original_prediction","violations","projection_verified","bounds")}
            public["paired_state_verified"] = row.get("pair_verified",False)
            public["memory_after"] = row["after"]["memory"]
            public["ring_identities_after"] = {name:[[r["epoch"],r["transaction_id"]] for r in row["after"][name]]
                                               for name in ("memory","pairs","packages")}
            transcript.write(json.dumps(public,sort_keys=True)+'\n')
            transcript.flush()
            d=row['descriptor']
            print(f"{d['index']+1}/224 {d['phase']} {d['study']}/{d['form']} seed={d['seed']} "
                  f"history={d['history']} action={row['parsed_action']} commit={row['authorization']['committed']} "
                  f"violations={row['violations']}",flush=True)
        try:
            rows=execute(transport,emit,emit_setup)
        except Exception as error:
            (output/'execution-error.json').write_text(json.dumps(dict(type=type(error).__name__,message=str(error)),indent=2)+'\n')
            raise
    if args.replay:
        assert transport.index == len(transport.calls)
    verify_frozen(root)
    source_paths=list((root/'experiments/model_explorer_memory_study_v1').glob('*.py'))
    source_paths += [root/'research/model-explorer-memory-study-v1-preregistration.md',
                     root/'experiments/model_explorer_memory_study_v1/fixtures-and-prompts.json']
    result=dict(summary=summarize(rows,setup_violations),setup_transactions=setup_count,model=metadata,
        source_sha256={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source_paths)},
        transcript_sha256=hashlib.sha256((output/'model-calls.jsonl').read_bytes()).hexdigest())
    (output/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result['summary'].items() if k!='cells'},indent=2))
    for c in result['summary']['cells']:
        print(c['study'],c['form'],'delta=',c['delta'],'supported=',c['supported'])
    print('Evidence:',output)
    raise SystemExit(0 if result['summary']['framework_integrity']=='PASS' else 2)


if __name__ == '__main__':
    main()
