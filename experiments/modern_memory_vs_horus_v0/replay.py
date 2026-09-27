from argparse import ArgumentParser
import json
from pathlib import Path

from horus.live import SessionStore
from horus.relation_routing import RelationEvidenceStore

from .analyze import analyze
from .protocol import CONDITIONS, ISSUED_REQUEST_BUDGET
from .storage import ModernMemory


def replay(output: Path) -> dict:
    saved = json.loads((output / "results.json").read_text())
    details = {}
    total_calls = total_events = 0
    for condition in CONDITIONS:
        root = output / condition
        with SessionStore(root / "session", True) as store, \
                ModernMemory(root / "memory.sqlite3", False) as memory:
            reconciliation = memory.reconcile(store)
            intents = [row for row in store.records["calls"] if row["kind"] == "REQUEST_INTENT"]
            responses = [row for row in store.records["calls"] if row["kind"] == "RESPONSE"]
            parsed = [row for row in store.records["calls"] if row["kind"] == "PARSED"]
            if not (len(intents) == len(responses) == len(parsed)):
                raise RuntimeError("call chain incomplete")
            ids = [row["record"]["call_id"] for row in intents]
            if len(ids) != len(set(ids)):
                raise RuntimeError("retry/duplicate call identity")
            expected = 102 if condition == "M" else 153
            if len(intents) != expected or len(store.records["events"]) != 16:
                raise RuntimeError("frozen call/event count mismatch")
            total_calls += len(intents); total_events += len(store.records["events"])
            details[condition] = dict(calls=len(intents), events=len(store.records["events"]),
                                      reconciliation=reconciliation)
        if condition == "MH":
            with RelationEvidenceStore(root / "registry") as routing:
                if len(routing.records) != 16:
                    raise RuntimeError("routing evidence count mismatch")
                details[condition]["routing_records"] = len(routing.records)
    recomputed = analyze(output)
    if recomputed != saved:
        raise RuntimeError("analysis does not exactly replay")
    result = dict(status="PASS", issued_requests=total_calls,
        issued_request_budget=ISSUED_REQUEST_BUDGET, protected_events=total_events,
        no_retries=True, exact_analysis_replay=True, conditions=details)
    (output / "replay.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    p = ArgumentParser(); p.add_argument("--output", type=Path, required=True)
    print(json.dumps(replay(p.parse_args().output), sort_keys=True))
