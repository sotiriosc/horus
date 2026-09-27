from argparse import ArgumentParser
import json
from pathlib import Path

from hashlib import sha256
from hmac import compare_digest, new as new_hmac

from horus.live import _canonical
from horus.relation_routing import RelationGroundedRouter, relation_key

from .invalid_report import build, read_partial_session
from .storage import ModernMemory, canonical


def replay_routing(root: Path) -> int:
    key = bytes.fromhex((root / "routing-authority.key").read_text().strip())
    document = json.loads((root / "router-state.json").read_text())
    if not compare_digest(new_hmac(key, _canonical(document["payload"]).encode(),
                                   "sha256").hexdigest(),
                          document["hmac_sha256"]):
        raise RuntimeError("routing checkpoint authentication failed")
    rows, previous, selected, replay_rows = [], None, {}, []
    router = RelationGroundedRouter()
    for sequence, line in enumerate((root / "routing-evidence.jsonl").read_text().splitlines(), 1):
        envelope = json.loads(line)
        signed = {name: envelope[name] for name in
                  ("sequence", "previous_sha256", "kind", "record")}
        if envelope["sequence"] != sequence or envelope["previous_sha256"] != previous or \
                not compare_digest(new_hmac(key, _canonical(signed).encode(),
                                            "sha256").hexdigest(), envelope["hmac_sha256"]):
            raise RuntimeError("routing evidence authentication failed")
        row, relation = envelope["record"], envelope["record"]["relation"]
        before = selected.get(relation_key(relation), "G2")
        if row["selected_specialist"] != before or \
                row["router_score_before"] != router.scores(replay_rows, relation):
            raise RuntimeError("routing before-state mismatch")
        replay_rows.append(row); transition = router.update(replay_rows, relation, before)
        if row["router_score_after"] != transition["scores"] or \
                row["selected_specialist_after"] != transition["selected_after"] or \
                row["switch_occurred"] != transition["switched"]:
            raise RuntimeError("routing transition mismatch")
        selected[relation_key(relation)] = transition["selected_after"]
        previous = sha256(_canonical(envelope).encode()).hexdigest(); rows.append(envelope)
    state = document["payload"]
    if state["evidence_count"] != len(rows) or state["evidence_head_sha256"] != previous:
        raise RuntimeError("routing checkpoint/stream mismatch")
    return len(rows)


def replay(output: Path) -> dict:
    saved = json.loads((output / "results.json").read_text())
    details = {}
    for condition, expected_calls, expected_events in (("M", 30, 5), ("MH", 45, 4)):
        root = output / condition
        session = read_partial_session(root / "session"); records = session["records"]
        with ModernMemory(root / "memory.sqlite3", False) as memory:
            intents = [row for row in records["calls"] if row["kind"] == "REQUEST_INTENT"]
            responses = [row for row in records["calls"] if row["kind"] == "RESPONSE"]
            parsed = [row for row in records["calls"] if row["kind"] == "PARSED"]
            if not (len(intents) == len(responses) == len(parsed) == expected_calls):
                raise RuntimeError("partial call-chain accounting mismatch")
            if len(records["events"]) != expected_events:
                raise RuntimeError("partial protected-event count mismatch")
            memory_rows = memory.rows()
            if len(memory_rows) != expected_events or any(
                    row["event_identity"] != canonical(event["record"]["receipt_identity"])
                    for row, event in zip(memory_rows, records["events"])):
                raise RuntimeError("partial durable memory/event mismatch")
            details[condition] = dict(calls=expected_calls, events=expected_events,
                reconciliation={"status":"PASS","authenticated_events":expected_events},
                registered_call_records=session["checkpoint"]["streams"]["calls"]["count"],
                physical_call_records=len(records["calls"]))
        if condition == "MH":
            routing_records = replay_routing(root / "registry")
            if routing_records != 4:
                raise RuntimeError("partial routing evidence mismatch")
            details[condition]["routing_records"] = routing_records
    session = read_partial_session(output / "MH/session")
    failure = [row for row in session["records"]["calls"] if row["kind"] == "PARSED" and
                   row["record"].get("call_id") == "A:05:MH:ADVANCE:J"]
    if len(failure) != 1 or failure[0]["record"].get("parse_error") != "TimeoutError":
        raise RuntimeError("stopping failure does not replay")
    if build(output) != saved:
        raise RuntimeError("invalid-result analysis does not exactly replay")
    result = dict(status="PASS", exact_invalid_analysis_replay=True,
        protected_partial_evidence_replay=True, no_retries=True,
        issued_model_calls=75, conditions=details)
    (output / "replay.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    p = ArgumentParser(); p.add_argument("--output", type=Path, required=True)
    print(json.dumps(replay(p.parse_args().output), sort_keys=True))
