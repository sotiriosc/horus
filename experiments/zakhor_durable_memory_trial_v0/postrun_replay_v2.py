"""Exact replay against the final zero-inference v2 analysis."""
from argparse import ArgumentParser
import json
from pathlib import Path

from . import replay as frozen_replay
from .postrun_v2 import analyze_completed_v2


def replay_completed_v2(output: Path) -> dict:
    frozen_replay.analyze = analyze_completed_v2
    result = frozen_replay.replay(output)
    result["reporting_recovery"] = (
        "v2 duplicate-keyword and prior-evidence denominator repair; zero inference")
    (output / "replay.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    p = ArgumentParser(); p.add_argument("--output", type=Path, required=True)
    print(json.dumps(replay_completed_v2(p.parse_args().output), sort_keys=True))
