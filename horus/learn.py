"""CLI for the bounded Horus v0.2 grounded consequence-learning path."""
import argparse
import json
from pathlib import Path

from .grounded_learning import (collect, compare, compare_context, evaluate,
                                freeze_dataset, summarize_session, train)
from .learning_cycle import STRATEGIES, collect_active, run_cycle
from .model_registry import history, initialize_registry


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
    p.add_argument("--phase", choices=("PRE_TRAINING", "POST_TRAINING"))
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
    p = commands.add_parser("init-registry")
    p.add_argument("--registry", type=Path, required=True)
    p = commands.add_parser("collect-active")
    p.add_argument("--session-root", type=Path, required=True)
    p.add_argument("--registry", type=Path, required=True)
    p.add_argument("--target", type=int, default=60)
    p.add_argument("--max-sessions", type=int, default=20)
    p.add_argument("--steps-per-session", type=int, default=6)
    p = commands.add_parser("cycle")
    p.add_argument("--session-root", type=Path, required=True)
    p.add_argument("--registry", type=Path, required=True)
    p.add_argument("--strategy", choices=STRATEGIES, default="continue-active")
    p = commands.add_parser("history")
    p.add_argument("--registry", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "collect":
        result = collect(args.output, args.target, args.max_sessions,
                         args.steps_per_session)
    elif args.command == "freeze":
        result = freeze_dataset(args.collection, args.output)
    elif args.command == "evaluate":
        result = evaluate(args.dataset, args.output, args.adapter, args.phase)
    elif args.command == "train":
        result = train(args.dataset, args.pre_evaluation, args.output)
    elif args.command == "compare":
        result = compare(args.before, args.after, args.output)
    elif args.command == "context-compare":
        result = compare_context(args.adapter, args.output, args.state)
    elif args.command == "session-summary":
        result = summarize_session(args.session, args.output)
    elif args.command == "init-registry":
        result = initialize_registry(args.registry)
    elif args.command == "collect-active":
        result = collect_active(args.session_root, args.registry, args.target,
                                args.max_sessions, args.steps_per_session)
    elif args.command == "cycle":
        result = run_cycle(args.session_root, args.registry, args.strategy)
    else:
        result = history(args.registry)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
