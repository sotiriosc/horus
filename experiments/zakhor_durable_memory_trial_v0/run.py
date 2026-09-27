from argparse import ArgumentParser
import json
from pathlib import Path
import subprocess
import sys

from .analyze import analyze
from .preflight import main as preflight


p = ArgumentParser()
p.add_argument("--output", type=Path, required=True)
args = p.parse_args()
if args.output.exists():
    raise RuntimeError("output already exists; campaign is single-run")
args.output.mkdir(parents=True)
check = preflight()
(args.output / "preflight.json").write_text(json.dumps(check, indent=2, sort_keys=True) + "\n")
for start, stop, initialize in ((1, 12, True), (13, 24, False)):
    command = [sys.executable, "-m", "experiments.zakhor_durable_memory_trial_v0.worker",
               "--output", str(args.output), "--start", str(start), "--stop", str(stop)]
    if initialize:
        command.append("--initialize")
    subprocess.run(command, cwd=Path(__file__).resolve().parents[2], check=True)
print(json.dumps(analyze(args.output), sort_keys=True))
