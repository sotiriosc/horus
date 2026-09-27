from argparse import ArgumentParser
import json
from pathlib import Path

from .harness import run_segment

p = ArgumentParser()
p.add_argument("--output", type=Path, required=True)
p.add_argument("--start", type=int, required=True)
p.add_argument("--stop", type=int, required=True)
p.add_argument("--initialize", action="store_true")
args = p.parse_args()
print(json.dumps(run_segment(args.output, args.start, args.stop, args.initialize),
                 sort_keys=True))

