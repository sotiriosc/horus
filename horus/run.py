"""Command-line entrypoint for the bounded Horus v0 session."""
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


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run the bounded Horus v0 closed loop")
    parser.add_argument("--output", type=Path, default=Path("horus-v0-run.json"))
    args = parser.parse_args(argv)
    artifact = run_demo(args.output)
    render(artifact)
    print(f"Machine-readable artifact: {args.output}")


if __name__ == "__main__":
    main()
