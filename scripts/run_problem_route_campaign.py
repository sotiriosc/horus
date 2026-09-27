#!/usr/bin/env python3
"""Run the preregistered Horus v0.8 campaign once with durable progress."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from horus.live import ModelClient, _now
from horus.problem_routing import (V08_SEGMENTS, initialize_problem_route_registry,
                                   run_problem_route_segment)
from horus.relation_routing import relation_routed_clients


def append(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as stream:
        stream.write(json.dumps(value, sort_keys=True) + "\n")
        stream.flush(); os.fsync(stream.fileno())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--source-registry", type=Path, required=True)
    parser.add_argument("--progress", type=Path, required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    args = parser.parse_args()
    if args.session.exists() or args.registry.exists() or args.progress.exists():
        raise SystemExit("v0.8 runner requires fresh session, registry, and progress paths")
    args.artifacts.mkdir(parents=True, exist_ok=False)
    append(args.progress, dict(started_at=_now(), campaign="HORUS_PROBLEM_ROUTE_REQUEST_V0"))
    initialize_problem_route_registry(args.registry, args.source_registry)
    specialists, relation_registry = relation_routed_clients(args.registry,
                                                              device="cuda")
    joint = ModelClient()
    try:
        for index, segment in enumerate(V08_SEGMENTS):
            artifact = run_problem_route_segment(args.session, args.registry,
                segment, index > 0, joint_client=joint,
                specialist_clients=specialists)
            destination = args.artifacts / f"{index + 1:02d}-{segment}.json"
            destination.write_text(json.dumps(artifact, indent=2,
                                              sort_keys=True) + "\n")
            append(args.progress, dict(at=_now(), segment=segment,
                decisions=artifact["checkpoint"]["attempted_decisions"],
                executions=artifact["checkpoint"]["completed_steps"],
                calls=sum(artifact["model_calls_by_role"].values()),
                artifact=destination.name))
    except Exception as exc:
        append(args.progress, dict(failed_at=_now(), error_type=type(exc).__name__,
                                   campaign_complete=False))
        raise
    append(args.progress, dict(finished_at=_now(), campaign_complete=True,
        decisions=54, model_calls=486))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
