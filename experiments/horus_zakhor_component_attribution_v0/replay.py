from argparse import ArgumentParser
import json
from pathlib import Path
from .study import replay

p = ArgumentParser()
p.add_argument("--output", type=Path, required=True)
args = p.parse_args()
result = replay(args.output)
(args.output / "replay.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps(result, sort_keys=True))

