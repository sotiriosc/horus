from argparse import ArgumentParser
import json
from pathlib import Path
import subprocess
import sys

from horus.grounded_exploration import initialize_grounded_exploration_registry
from horus.live import SessionStore

from .protocol import CONDITIONS, ISSUED_REQUEST_BUDGET, REAL_MODEL_CALL_BUDGET
from .storage import ModernMemory


def main(output: Path) -> dict:
    if output.exists():
        raise RuntimeError("output already exists; campaign is single-use")
    output.mkdir(parents=True)
    for condition in CONDITIONS:
        root = output / condition; root.mkdir()
        with SessionStore(root / "session", False): pass
        with ModernMemory(root / "memory.sqlite3", True): pass
        if condition == "MH":
            initialize_grounded_exploration_registry(root / "registry")
    for stage in ("A1", "A2", "B"):
        subprocess.run([sys.executable, "-m",
            "experiments.modern_memory_vs_horus_v0.worker", stage,
            "--output", str(output)], check=True)
    result = dict(status="CAMPAIGN_COMPLETE", conditions=list(CONDITIONS),
        issued_request_budget=ISSUED_REQUEST_BUDGET,
        real_model_call_budget=REAL_MODEL_CALL_BUDGET,
        stages=["A1", "A2", "B"])
    (output / "campaign-complete.json").write_text(json.dumps(
        result, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    p = ArgumentParser(); p.add_argument("--output", type=Path, required=True)
    print(json.dumps(main(p.parse_args().output), sort_keys=True))
