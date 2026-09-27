"""Zero-inference report for the stopped, unmatched Stage-A campaign."""
from argparse import ArgumentParser
from collections import Counter
from datetime import datetime
from hashlib import sha256
from hmac import compare_digest, new as new_hmac
import json
from pathlib import Path

from horus.live import _canonical


def _time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def read_partial_session(directory: Path) -> dict:
    """Authenticate registered prefixes and any physically durable call suffix."""
    key = bytes.fromhex((directory / "authority.key").read_text().strip())
    document = json.loads((directory / "checkpoint.json").read_text())
    if not compare_digest(new_hmac(key, _canonical(document["payload"]).encode(),
                                  "sha256").hexdigest(), document["hmac_sha256"]):
        raise RuntimeError("checkpoint authentication failed")
    checkpoint, streams = document["payload"], {}
    names = {"events": "events.jsonl", "calls": "model-calls.private.jsonl",
             "training": "training-records.jsonl"}
    for name, filename in names.items():
        rows, previous = [], None
        for sequence, line in enumerate((directory / filename).read_text().splitlines(), 1):
            envelope = json.loads(line)
            signed = {key_name: envelope[key_name] for key_name in
                      ("sequence", "previous_sha256", "kind", "record")}
            if sequence != envelope["sequence"] or envelope["previous_sha256"] != previous or \
                    not compare_digest(new_hmac(key, _canonical(signed).encode(),
                                                "sha256").hexdigest(),
                                       envelope["hmac_sha256"]):
                raise RuntimeError(f"{name} chain authentication failed")
            previous = sha256(_canonical(envelope).encode()).hexdigest(); rows.append(envelope)
        registered = checkpoint["streams"][name]
        if len(rows) < registered["count"]:
            raise RuntimeError("physical stream shorter than registered prefix")
        prefix_head = None if not registered["count"] else sha256(_canonical(
            rows[registered["count"] - 1]).encode()).hexdigest()
        if prefix_head != registered["head_sha256"]:
            raise RuntimeError("registered prefix head mismatch")
        streams[name] = rows
    return dict(checkpoint=checkpoint, records=streams)


def build(output: Path) -> dict:
    conditions, calls = {}, {}
    for condition in ("M", "MH"):
        session = read_partial_session(output / condition / "session")
        records = session["records"]
        scored = [row["record"] for row in records["training"]
                      if row["kind"] == "MODERN_VS_HORUS_SCORED_EVENT"]
        intents = [row for row in records["calls"]
                       if row["kind"] == "REQUEST_INTENT"]
        parsed = [row for row in records["calls"] if row["kind"] == "PARSED"]
        errors = Counter(row["record"].get("parse_error") for row in parsed
                             if row["record"].get("parse_error"))
        first = _time(records["calls"][0]["record"]["recorded_at"])
        last = _time(records["calls"][-1]["record"]["recorded_at"])
        conditions[condition] = dict(authenticated_events=len(records["events"]),
                completed_scored_events=len(scored), issued_model_calls=len(intents),
                complete_call_chains=(len(records["calls"]) == 3 * len(intents)),
                checkpoint_registered_call_records=session["checkpoint"]["streams"][
                    "calls"]["count"], physical_call_records=len(records["calls"]),
                call_errors=dict(errors), elapsed_recorded_seconds=(last-first).total_seconds(),
                consequence_correct=sum(row["consequence_correct"] for row in scored),
                exact_correct=sum(row["exact_correct"] for row in scored),
                actions=[row["action"] for row in scored],
                realized_consequences=[row["realized"]["consequence"] for row in scored])
        calls[condition] = {row["record"]["call_id"]: row["record"] for row in parsed}
    failure_id = "A:05:MH:ADVANCE:J"
    failure = calls["MH"][failure_id]
    result = dict(status="STOPPED", classification="INVALID",
        reason="MATCHED_STAGE_A_SEQUENCE_BROKEN_BY_UNPLANNED_JOINT_TRANSPORT_TIMEOUT",
        inference_retried=False, campaign_restarted=False,
        completed_scope=dict(stage_a_matched_events=4, stage_a_M_only_event=5,
            stage_a_target_events=12, registered_perturbation_reached=False,
            fresh_process_restart_reached=False, stage_b_reached=False),
        conditions=conditions,
        failure=dict(condition="MH", stage="A", event=5, call_id=failure_id,
            role="joint-next-state", action="ADVANCE",
            transport_error=failure["parse_error"], strict_parser_result="INVALID",
            policy_result="FAIL_CLOSED_NO_EXECUTION", receipt_created=False,
            memory_published=False, routing_evidence_created=False),
        protected_harness=dict(status="PASS_THROUGH_FAILURE_BOUNDARY",
            original_receipt_identity_retained=True,
            unauthorized_evidence_admitted=False,
            failed_MH_execution_created_receipt=False,
            authenticated_streams_replay=True),
        intervention_ledger=[],
        metrics_not_estimable=["adaptation_latency", "restoration_latency",
            "endurance_windows", "autonomous_trajectory", "full_component_attribution"],
        narrow_observation=("Current Horus failed closed on an incomplete Map batch. "
            "The planned Horus-versus-modern-memory capability comparison is not interpretable."))
    (output / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    p = ArgumentParser(); p.add_argument("--output", type=Path, required=True)
    print(json.dumps(build(p.parse_args().output), sort_keys=True))
