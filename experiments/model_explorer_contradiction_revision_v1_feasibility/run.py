"""Full deterministic fixture/replay. No prompt, parser or model transport."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile

from experiments.model_explorer_integration_v0.campaign import verify_frozen
from .fixture import run_fixture


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--replay", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    package = Path(__file__).parent
    frozen = json.loads((package / "frozen-inputs.json").read_text())
    historical = verify_frozen(root)
    assert all(digest(root / p) == h for p, h in frozen.items())
    paths = list(package.glob("*.py")) + [package / "frozen-inputs.json",
        root / "research/model-explorer-contradiction-revision-v1-feasibility-preregistration.md"]
    sources = {str(p.relative_to(root)): digest(p) for p in sorted(paths)}
    output = args.output or Path(tempfile.mkdtemp(prefix="horus-contradiction-v1-"))
    if output.resolve().is_relative_to(root):
        raise ValueError("detailed evidence must stay outside the public tree")
    if args.output:
        output.mkdir(parents=True, exist_ok=False)
    data = run_fixture()
    if data["summary"]["campaign_gate"] == "PASS_PENDING_REPLAY_AND_REGRESSIONS":
        uninstrumented = run_fixture(instrument=False)
        normalized = deepcopy(data)
        for row in normalized["steps"]:
            row["observations"] = []
        same = normalized == uninstrumented
        data["summary"]["observer_noninterference_pass"] = same
        data["summary"]["uninstrumented_validation_transactions"] = len(uninstrumented["steps"])
        if not same:
            data["summary"]["campaign_gate"] = "C"
            data["summary"]["first_failure"] = {"boundary": "observer_noninterference"}
    assert historical == verify_frozen(root)
    assert all(digest(root / p) == h for p, h in frozen.items())
    assert sources == {str(p.relative_to(root)): digest(p) for p in sorted(paths)}
    (output / "fixture.json").write_text(json.dumps(data, indent=2) + "\n")
    result = dict(summary=data["summary"], frozen_framework=historical, frozen_inputs_sha256=frozen,
                  source_sha256=sources, evidence_sha256={"fixture.json": digest(output / "fixture.json")})
    (output / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    if args.replay:
        for name in ("fixture.json", "results.json"):
            assert (args.replay / name).read_bytes() == (output / name).read_bytes(), name
        print("Exact fixture and compact-results replay: byte-identical; zero inference.")
    print(json.dumps(data["summary"], indent=2))
    print("Evidence:", output)
    if data["summary"]["campaign_gate"] != "PASS_PENDING_REPLAY_AND_REGRESSIONS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
