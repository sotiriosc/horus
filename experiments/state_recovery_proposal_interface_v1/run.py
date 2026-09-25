"""Deterministic campaign and byte-exact replay; ZERO model calls."""
import argparse
import hashlib
import json
from pathlib import Path
from .campaign import run, serialized, protected_projection


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--replay', type=Path)
    parser.add_argument('--historical-evidence', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    package = Path(__file__).parent
    frozen = json.loads((package / 'frozen-inputs.json').read_text())
    for name, digest in frozen['inherited_sha256'].items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest, name
    if args.output.resolve().is_relative_to(root):
        raise ValueError('Detailed evidence belongs outside public source')
    data = run()
    uninstrumented = run(False)
    assert serialized(protected_projection(data)) == serialized(protected_projection(uninstrumented))
    if args.historical_evidence:
        assert serialized(data['default_equivalence']['historical']) == (args.historical_evidence / 'diagnostic.json').read_bytes()
    content = serialized(data)
    paths = sorted(list(package.glob('*.py')) + [package / 'frozen-inputs.json',
        root / 'research/state-recovery-proposal-interface-v1-preregistration.md'])
    result = dict(summary=data['summary'], observer_noninterference=True,
        source_sha256={str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        campaign_sha256=hashlib.sha256(content).hexdigest())
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / 'campaign.json').write_bytes(content)
    (args.output / 'results.json').write_bytes(serialized(result))
    if args.replay:
        for name in ('campaign.json', 'results.json'):
            assert (args.output / name).read_bytes() == (args.replay / name).read_bytes(), name
        print('Exact campaign replay: both files byte-identical; zero inference.')
    print(json.dumps(data['summary'], indent=2))
    # Expected exit 2: classification C, a disclosed pre-existing requirement gap.
    raise SystemExit(2 if data['summary']['classification'].startswith('C') else 0)


if __name__ == '__main__':
    main()
