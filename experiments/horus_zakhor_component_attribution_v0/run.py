from argparse import ArgumentParser
import json
from pathlib import Path
from .study import run

p = ArgumentParser()
p.add_argument("--output", type=Path, required=True)
args = p.parse_args()
print(json.dumps(run(args.output), sort_keys=True))

