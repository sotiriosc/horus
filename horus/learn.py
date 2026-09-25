"""CLI for the bounded Horus v0.2 grounded consequence-learning path."""
import argparse
import json
from pathlib import Path

from .grounded_learning import (collect, compare, compare_context, evaluate,
                                freeze_dataset, summarize_session, train)


def main(argv=None):
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("collect")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--target", type=int, default=60)
    p.add_argument("--max-sessions", type=int, default=20)
    p.add_argument("--steps-per-session", type=int, default=6)
    p = commands.add_parser("freeze")
    p.add_argument("--collection", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p = commands.add_parser("evaluate")
    p.add_argument("--dataset", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--adapter", type=Path)
    p = commands.add_parser("train")
    p.add_argument("--dataset", type=Path, required=True)
    p.add_argument("--pre-evaluation", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p = commands.add_parser("compare")
    p.add_argument("--before", type=Path, required=True)
    p.add_argument("--after", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p = commands.add_parser("context-compare")
    p.add_argument("--adapter", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--state", type=int, default=1)
    p = commands.add_parser("session-summary")
    p.add_argument("--session", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "collect":
        result = collect(args.output, args.target, args.max_sessions,
                         args.steps_per_session)
    elif args.command == "freeze":
        result = freeze_dataset(args.collection, args.output)
    elif args.command == "evaluate":
        result = evaluate(args.dataset, args.output, args.adapter)
    elif args.command == "train":
        result = train(args.dataset, args.pre_evaluation, args.output)
    elif args.command == "compare":
        result = compare(args.before, args.after, args.output)
    elif args.command == "context-compare":
        result = compare_context(args.adapter, args.output, args.state)
    else:
        result = summarize_session(args.session, args.output)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
