"""Exact replay against the authoritative zero-inference v3 report."""
from argparse import ArgumentParser
import json
from pathlib import Path

from . import replay as frozen_replay
from .postrun_v3 import analyze_completed_v3


def replay_completed_v3(output: Path) -> dict:
    frozen_replay.analyze = analyze_completed_v3
    result = frozen_replay.replay(output)
    result["reporting_recovery"] = "v3 authoritative zero-inference reporting recovery"
    (output / "replay.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    p = ArgumentParser(); p.add_argument("--output", type=Path, required=True)
    print(json.dumps(replay_completed_v3(p.parse_args().output), sort_keys=True))
