"""Deterministic receipt campaign and exact replay; no model transport."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile

from experiments.model_explorer_integration_v0.campaign import verify_frozen
from .campaign import run_campaign


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--replay", type=Path, help="retained campaign directory")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    package = Path(__file__).parent
    frozen = verify_frozen(root)
    sources = list(package.glob("*.py")) + [
        root / "research/realized-event-grounding-v0-preregistration.md",
        root / "experiments/model_explorer_contradiction_revision_v0/overlay.py",
        root / "experiments/model_explorer_integration_v0/campaign.py"]
    hashes = {str(p.relative_to(root)): digest(p) for p in sorted(sources)}
    output = args.output or Path(tempfile.mkdtemp(prefix="horus-realized-event-"))
    if output.resolve().is_relative_to(root):
        raise ValueError("detailed evidence must remain outside the public tree")
    if args.output:
        output.mkdir(parents=True, exist_ok=False)
    data = run_campaign()
    (output / "campaign.json").write_text(json.dumps(data, indent=2) + "\n")
    assert frozen == verify_frozen(root)
    assert hashes == {str(p.relative_to(root)): digest(p) for p in sorted(sources)}
    result = dict(summary=data["summary"], frozen=frozen, source_sha256=hashes,
                  evidence_sha256={"campaign.json": digest(output / "campaign.json")})
    (output / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    if args.replay:
        for name in ("campaign.json", "results.json"):
            assert (args.replay / name).read_bytes() == (output / name).read_bytes(), name
        print("Exact replay: campaign and compact results byte-identical; zero inference.")
    print(json.dumps(data["summary"], indent=2))
    print("Evidence:", output)


if __name__ == "__main__":
    main()
