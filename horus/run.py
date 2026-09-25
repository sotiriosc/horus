"""Command-line entrypoint for reference v0 and live v0.1 sessions."""
import argparse
from pathlib import Path

from .core import run_demo


def render(artifact):
    for row in artifact["episodes"]:
        print(f"Episode {row['episode']}")
        print(f"State: {row['state']}")
        used = {action: len(history) for action, history in row["memory_used"].items()}
        print(f"Memory used: {used}")
        print("Map forecasts:")
        for forecast in row["map_forecasts"]:
            print(f"  {forecast['action']} -> next_state={forecast['next_state']}, "
                  f"consequence={forecast['consequence']}, history={forecast['history_count']}")
        print(f"Explorer chose: {row['explorer']['action']} ({row['explorer']['reason']})")
        receipt = row["receipt"]
        print(f"Realized receipt: next_state={receipt['next_state']}, "
              f"consequence={receipt['realized_consequence']}, event_id={receipt['event_id']}")
        print(f"Prediction match: {row['prediction_match']}")
        memory = row["memory_published"]
        print(f"Memory published: epoch={memory['epoch']}, tx={memory['transaction_id']}, "
              f"action={memory['action']}, consequence={memory['consequence']}")
        print()
    causal = artifact["causal_moment"]
    print(f"Grounded behavior change: {causal['earlier_action']} -> {causal['later_action']}")


def render_live(artifact):
    print(f"Horus live session: {artifact['session_id']}")
    print(f"Runtime {artifact['runtime_index']} / epoch {artifact['epoch']}")
    for row in artifact["steps"]:
        print(f"\nStep {row['step']}")
        print("Prior authenticated observations used: " +
              ", ".join(f"{key}={value}" for key, value in
                        row["prior_authenticated_observations_used"].items()))
        print("Map:")
        for forecast in row["map_forecasts"]:
            print(f"  {forecast['action']} -> next_state={forecast['next_state']}, "
                  f"consequence={forecast['consequence']}, "
                  f"history={forecast['history_count']}, "
                  f"abstained={forecast['abstained']}")
        print(f"Explorer chose: {row['explorer']['action']} "
              f"({row['explorer']['reason']})")
        if row["status"] == "ABSTAINED":
            print("Executed: no (Map abstained)")
            continue
        receipt = row["receipt"]
        print(f"Executed: {receipt['action']}")
        print(f"Original receipt: source={receipt['source_identity']}, "
              f"event={receipt['event_id']}, next_state={receipt['next_state']}, "
              f"consequence={receipt['realized_consequence']}")
        print(f"Prediction vs realization: {row['prediction_match']}")
        print(f"Memory publication: {row['memory_publication']}")
        print("Behavioral change attributable to prior experience: not established; "
              "the authenticated-history counts above show request-level use only")
    print(f"\nActual model calls this process: {artifact['actual_model_calls']}")
    print(f"Checkpoint: {Path(artifact['session']) / 'checkpoint.json'}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run the bounded Horus v0 closed loop")
    parser.add_argument("--output", type=Path, default=Path("horus-v0-run.json"))
    parser.add_argument("--live", action="store_true",
                        help="use real model predictors and durable session state")
    parser.add_argument("--steps", type=int, default=1)
    parser.add_argument("--session", type=Path)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--consequence-model", choices=("mixtral", "base", "trained"),
                        default="mixtral")
    parser.add_argument("--trained-adapter", type=Path)
    parser.add_argument("--consequence-base-model", type=Path,
                        help="optional local directory for the pinned Qwen base snapshot")
    args = parser.parse_args(argv)
    if args.live:
        if args.session is None:
            parser.error("--live requires --session")
        if args.resume and not args.live:
            parser.error("--resume requires --live")
        from .live import run_live
        consequence_client = None
        if args.consequence_model != "mixtral":
            from .grounded_learning import QwenConsequenceClient, default_adapter_path
            adapter = None
            if args.consequence_model == "trained":
                adapter = args.trained_adapter or default_adapter_path()
                if not adapter.exists():
                    parser.error(f"trained adapter does not exist: {adapter}")
            consequence_client = QwenConsequenceClient(
                adapter_path=adapter, model_path=args.consequence_base_model)
        artifact = run_live(args.session, args.steps, args.resume,
                            consequence_client=consequence_client)
        render_live(artifact)
        return
    if args.resume or args.session is not None:
        parser.error("--resume/--session require --live")
    artifact = run_demo(args.output)
    render(artifact)
    print(f"Machine-readable artifact: {args.output}")


if __name__ == "__main__":
    main()
