"""Run local real inference or replay its exact public proposal transcript."""

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import urllib.request

from experiments.model_explorer_integration_v0.adapter import LocalModel, MODEL, OPTIONS, SYSTEM
from experiments.model_explorer_integration_v0.campaign import execute, summarize, verify_frozen


class Replay:
    def __init__(self, path):
        self.calls = [json.loads(line) for line in path.read_text().splitlines()]
        self.index = 0

    def generate(self, prompt, seed):
        call = self.calls[self.index]
        self.index += 1
        assert prompt == call["exact_prompt"], "replay input differs"
        assert call["options"] == {**OPTIONS, "seed": seed}, "replay generation configuration differs"
        assert call["system"] == SYSTEM and call["model"] == MODEL
        return call["raw_output"], call["response_metadata"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--replay", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    frozen = verify_frozen(root)
    output = args.output or Path(tempfile.mkdtemp(prefix="horus-model-explorer-"))
    if output.resolve().is_relative_to(root):
        raise ValueError("raw evidence must remain outside the public source tree")
    if args.output:
        output.mkdir(parents=True, exist_ok=False)
    metadata = {"model": MODEL, "options": OPTIONS, "system": SYSTEM, "frozen": frozen,
                "execution": "replay" if args.replay else "real_inference"}
    if args.replay:
        transport = Replay(args.replay)
    else:
        transport = LocalModel()
        def get(endpoint, data=None):
            req = urllib.request.Request(transport.endpoint + "/api/" + endpoint,
                  data=None if data is None else json.dumps(data).encode(),
                  headers={"Content-Type": "application/json"})
            return json.load(urllib.request.urlopen(req, timeout=30))
        metadata["server"] = get("version")
        model = next(row for row in get("tags")["models"] if row["name"] == MODEL)
        if model["digest"] != frozen["model"]["manifest_digest"]:
            raise RuntimeError("preregistered model digest changed")
        metadata["installed_model"] = model
        shown = get("show", {"name": MODEL})
        metadata["model_template"] = {key: shown[key] for key in ("template", "system", "parameters", "details") if key in shown}
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    rows = []
    with (output / "steps.jsonl").open("w") as steps, (output / "model-calls.jsonl").open("w") as calls:
        def emit(row):
            rows.append(row)
            steps.write(json.dumps(row, sort_keys=True) + "\n")
            steps.flush()
            call = row["model_call"]
            if call and not call["response_metadata"].get("synthetic"):
                calls.write(json.dumps(call, sort_keys=True) + "\n")
                calls.flush()
                print(f"{row['role']} {row['label']} seed={row['seed']} action={row['parsed_action']} "
                      f"commit={row['authorization']['committed']} violations={row['violations']}", flush=True)
        try:
            campaign = execute(transport, emit)
        except Exception as error:
            (output / "execution-error.json").write_text(json.dumps({
                "class": "INFRASTRUCTURE_OR_HARNESS_FAILURE", "type": type(error).__name__,
                "message": str(error), "completed_steps": len(rows)}, indent=2) + "\n")
            raise
    if args.replay:
        assert transport.index == len(transport.calls), "unused model calls"
    verify_frozen(root)
    result = dict(summary=summarize(campaign, rows),
                  pairs=[{k: v for k, v in p.items() if k != "arms"} for p in campaign["pairs"]],
                  model=metadata, source_sha256={str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in sorted((root / "experiments/model_explorer_integration_v0").glob("*.py"))},
                  transcript_sha256=hashlib.sha256((output / "model-calls.jsonl").read_bytes()).hexdigest())
    (output / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["summary"], indent=2), flush=True)
    print(f"Evidence: {output}")
    raise SystemExit(0 if result["summary"]["framework_integrity"] == "PASS" else 2)


if __name__ == "__main__":
    main()
