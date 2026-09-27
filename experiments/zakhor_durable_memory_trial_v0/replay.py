from argparse import ArgumentParser
import json
from pathlib import Path

from horus.core import digest
from horus.live import SessionStore

from .analyze import analyze
from .harness import ADAPTER, EVENTS
from .storage import DurableMemory, file_hash


def replay(output: Path) -> dict:
    saved = json.loads((output / "results.json").read_text())
    with SessionStore(output / "protected-session", True) as store, \
            DurableMemory(output / "memory.sqlite3", False) as memory:
        reconciliation = memory.reconcile(store)
        events = [row["record"] for row in store.records["events"]]
        calls = store.records["calls"]
        scoring = [row["record"] for row in store.records["training"]]
        if len(events) != 24 or len(calls) != 144 or len(scoring) != 24:
            raise RuntimeError("frozen schedule/call evidence count mismatch")
        if [row["schedule_event"] for row in events] != list(range(1, 25)):
            raise RuntimeError("event schedule order mismatch")
        if [row["schedule_phase"] for row in events] != [x["phase"] for x in EVENTS]:
            raise RuntimeError("event phase schedule mismatch")
        grouped = {}
        for envelope in calls:
            row = envelope["record"]
            grouped.setdefault(row["call_id"], {})[envelope["kind"]] = row
        expected_ids = {f"event-{event:02d}:{condition}"
                        for event in range(1, 25) for condition in ("M", "Z")}
        if set(grouped) != expected_ids or any(set(parts) != {
                "MEMORY_MODEL_REQUEST", "MEMORY_MODEL_RESPONSE", "MEMORY_MODEL_PARSED"}
                for parts in grouped.values()):
            raise RuntimeError("call identity/retry mismatch")
        rows_by_identity = {row["event_identity"]: row for row in memory.history("1:HOLD")}
        for call_id, parts in grouped.items():
            request = parts["MEMORY_MODEL_REQUEST"]
            response = parts["MEMORY_MODEL_RESPONSE"]
            if request["request_sha256"] != digest(request["request"]) or \
                    response["response_sha256"] != digest(response["response"]):
                raise RuntimeError("call request/response hash mismatch")
            prompt = json.loads(request["request"]["prompt"])
            identities = request["retrieval"]["selected_memory_identities"]
            expected_history = []
            for identity in identities:
                row = rows_by_identity[identity]
                expected_history.append(dict(epoch=row["epoch"],
                    transaction_id=row["transaction_id"], surface_action="K2",
                    next_state=row["realized_next_state"],
                    consequence=row["realized_consequence"]))
            if prompt["VERIFIED_CHRONOLOGICAL_HISTORY"] != expected_history:
                raise RuntimeError("model prompt differs from transparent retrieval trace")
        for event, score in zip(events, scoring):
            if score["event_stream_sequence"] != event["schedule_event"] or \
                    score["receipt_identity"] != event["receipt_identity"] or \
                    score["receipt_provenance_sha256"] != event["receipt_provenance_sha256"]:
                raise RuntimeError("scoring record is not bound to protected publication")
        before = json.loads((output / "before-restart.json").read_text())
        after = json.loads((output / "after-restart.json").read_text())
        if not after["restore_verification"]["exact_hash_match"] or \
                after["restore_verification"]["expected"] != before["checkpoint"]:
            raise RuntimeError("restart proof mismatch")
        if file_hash(ADAPTER) != before["model_artifact_sha256"] or \
                file_hash(ADAPTER) != after["model_artifact_sha256"]:
            raise RuntimeError("model artifact identity mismatch")
    recomputed = analyze(output)
    if recomputed != saved:
        raise RuntimeError("analysis does not exactly replay")
    result = dict(status="PASS", protected_event_replay=reconciliation,
        event_count=24, model_calls=48, call_records=144, scoring_records=24,
        no_retries=True, exact_analysis_replay=True,
        fresh_process_restart_hash_match=True)
    (output / "replay.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    p = ArgumentParser(); p.add_argument("--output", type=Path, required=True)
    print(json.dumps(replay(p.parse_args().output), sort_keys=True))

