"""Zero-call campaign and exact replay; final classification needs regressions."""
import argparse
import hashlib
import json
from pathlib import Path
from .campaign import run, serialized, protected_projection


def main():
    p = argparse.ArgumentParser(); p.add_argument('--output', type=Path, required=True)
    p.add_argument('--replay', type=Path)
    args = p.parse_args(); package = Path(__file__).parent; root = package.parents[1]
    frozen = json.loads((package / 'frozen-inputs.json').read_text())
    for name, digest in frozen['inherited_sha256'].items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest, name
    if args.output.resolve().is_relative_to(root.resolve()): raise ValueError('private evidence must be external')
    data = run(); duplicate = run(False)
    assert serialized(protected_projection(data)) == serialized(protected_projection(duplicate))
    content = serialized(data)
    paths = sorted(list(package.glob('*.py')) + [package / 'frozen-inputs.json', package / 'preflight-results.json',
                   root / 'research/state-recovery-authorizer-status-binding-v1-preregistration.md'])
    result = dict(summary=data['summary'], observer_noninterference=True,
        campaign_sha256=hashlib.sha256(content).hexdigest(),
        source_sha256={str(f.relative_to(root)): hashlib.sha256(f.read_bytes()).hexdigest() for f in paths})
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / 'campaign.json').write_bytes(content)
    (args.output / 'results.json').write_bytes(serialized(result))
    if args.replay:
        for name in ('campaign.json', 'results.json'):
            assert (args.output / name).read_bytes() == (args.replay / name).read_bytes(), name
        print('Exact replay: both files byte-identical; zero inference.')
    print(json.dumps(result['summary'], indent=2))


if __name__ == '__main__': main()
