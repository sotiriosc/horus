"""Exact replay using the separately recorded reporting-only recovery."""
from argparse import ArgumentParser
import json
from pathlib import Path

from . import replay as frozen_replay
from .postrun import analyze_completed


def replay_completed(output: Path) -> dict:
    frozen_replay.analyze = analyze_completed
    result = frozen_replay.replay(output)
    result["reporting_recovery"] = "duplicate event_number keyword only; zero inference"
    (output / "replay.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    p = ArgumentParser(); p.add_argument("--output", type=Path, required=True)
    print(json.dumps(replay_completed(p.parse_args().output), sort_keys=True))
