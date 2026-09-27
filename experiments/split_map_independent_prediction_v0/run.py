"""Exactly 33 registered Map attempts or recorded replay; never retry."""
import argparse
import hashlib
import json
from pathlib import Path
from unittest.mock import patch

from experiments.model_proposal_role_composition_v2.transport import LocalModel
from experiments.model_recovery_proposal_v1.transport import metadata
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import (
    Journal, atomic_write, append_line, require_durable, fsync_dir, file_digest, inspect)
from .protocol import (ROOT, PACKAGE, CAMPAIGN, CALL_LIMIT, CONTEXT_LIMIT, ROLES,
    contexts, schedule, frozen, summarize, parse, request_hash)
from .fixture import Context, GUARD


FILES = ("metadata.json", "contexts.jsonl", "model-calls.jsonl", "steps.jsonl",
         "metrics.json", "journal.jsonl", "campaign-state.json")


class Recorder:
    def __init__(self, journal, client, stream, prior=None):
        self.journal = journal
        self.client = client
        self.stream = stream
        self.prior = prior
        self.calls = []
        self.registered = json.loads((PACKAGE / "schedule.json").read_text())

    def call(self, context, role):
        call_index = len(self.calls)
        descriptor = context.d
        assert call_index < CALL_LIMIT and role in ROLES
        expected = self.registered[call_index]
        assert expected["call_index"] == call_index
        assert expected["context_index"] == descriptor["index"]
        assert expected["historical_context_number"] == descriptor["historical_context_number"]
        assert expected["role"] == role and expected["seed"] == descriptor["seed"]
        call_id = f'{CAMPAIGN}:c{descriptor["index"]:02d}:{role}'
        assert call_id not in self.journal.calls
        self.journal.calls[call_id] = "INTENT"
        request = context.requests[role]
        exact_request_json = json.dumps(request)
        assert hashlib.sha256(exact_request_json.encode()).hexdigest() == expected["request_sha256"]
        intent = dict(call_index=call_index, context_index=descriptor["index"], role=role,
            descriptor=descriptor, request=request, exact_request_json=exact_request_json,
            snapshot=self.journal.snapshot(context.before))
        self.journal.append("REQUEST_INTENT_RECORDED", intent, call_id)
        atomic_write(self.journal.directory / "campaign-state.json", dict(
            campaign_id=CAMPAIGN, status="REQUEST_INTENT_RECORDED",
            attempted_calls=call_index + 1, completed_calls=call_index,
            completed_contexts=descriptor["index"], journal_head_sha256=self.journal.previous,
            journal_records=self.journal.sequence, automatic_reissue_allowed=False))
        with patch(GUARD, side_effect=AssertionError("scored event cannot execute during inference")):
            context.audit_before()
            if self.prior is None:
                assert self.client.requests == call_index
                response = self.client.generate(dict(model=request["model"], system=request["system"],
                    exact_prompt=request["prompt"], options=request["options"]))
                assert self.client.requests == call_index + 1
            else:
                old = self.prior[call_index]
                assert old["call_id"] == call_id and old["intent"] == intent
                response = old["response"]
            self.journal.append("RESPONSE_RECEIVED", response, call_id)
            if response["transport_error"]:
                raise RuntimeError("failed or ambiguous transport; STOP; no reissue")
            try:
                parsed = parse(response["raw_output"], role)
                error = None
            except (ValueError, TypeError) as exc:
                parsed = None
                error = str(exc)
            self.journal.append("PARSED", dict(parsed=parsed, error=error,
                component_output_frozen=True), call_id)
            self.journal.calls[call_id] = "PARSED"
            context.audit_before()
        row = dict(index=call_index, call_id=call_id, intent=intent, request=request,
                   response=response, parsed=parsed, parse_error=error)
        append_line(self.stream, row)
        self.calls.append(row)
        return row


def campaign(output, client, meta, prior=None):
    journal = Journal(output, campaign=CAMPAIGN)
    rows = []
    try:
        atomic_write(output / "metadata.json", meta)
        with (output / "contexts.jsonl").open("x") as context_stream, \
             (output / "model-calls.jsonl").open("x") as call_stream, \
             (output / "steps.jsonl").open("x") as step_stream:
            recorder = Recorder(journal, client, call_stream, prior)
            for descriptor in contexts():
                frozen()
                journal.episode = descriptor["index"]
                journal.decision = 0
                context = Context(descriptor)
                context_record = context.record()
                append_line(context_stream, context_record)
                journal.append("AUTHENTIC_HISTORY_AND_ALL_REQUESTS_READY", context_record)
                calls = {}
                for role in descriptor["call_order"]:
                    calls[role] = recorder.call(context, role)
                row = context.finish(calls, journal)
                append_line(step_stream, row)
                rows.append(row)
                journal.append("CONTEXT_FINALIZED", dict(index=descriptor["index"],
                    predictions=row["predictions"], reconciled=row["reconciled_prediction"],
                    scores=row["scores"]))
                atomic_write(output / "campaign-state.json", dict(
                    campaign_id=CAMPAIGN, status="CONTEXT_FINALIZED",
                    attempted_calls=len(recorder.calls), completed_calls=len(recorder.calls),
                    completed_contexts=len(rows), journal_head_sha256=journal.previous,
                    journal_records=journal.sequence, automatic_reissue_allowed=False))
                print(f"context {len(rows)}/{CONTEXT_LIMIT} historical={descriptor['historical_context_number']} "
                      f"order={','.join(descriptor['call_order'])} J={row['predictions']['J']} "
                      f"N={row['predictions']['N']} C={row['predictions']['C']} "
                      f"split={row['reconciled_prediction']} scores={row['scores']}", flush=True)
        assert len(recorder.calls) == CALL_LIMIT
        assert client.requests == CALL_LIMIT if prior is None else len(prior) == CALL_LIMIT
        result = summarize(rows, len(recorder.calls), integrity=True, replay=False,
                           independence=True, reconciliation=True)
        atomic_write(output / "metrics.json", result)
        state = json.loads((output / "campaign-state.json").read_text())
        state["status"] = "THIRTY_THREE_CALLS_COMPLETE_STOP"
        atomic_write(output / "campaign-state.json", state)
        check = inspect(output)
        assert check["journal_valid"] and not check["ambiguous_calls"]
        assert check["campaign_state_matches_journal"]
    except BaseException as exc:
        atomic_write(output / "STOP.json", dict(status="STOP_NO_REISSUE", reason=str(exc),
            completed_contexts=len(rows), inspection=inspect(output)))
        raise
    finally:
        journal.close()
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--live", action="store_true")
    mode.add_argument("--replay", type=Path)
    parser.add_argument("--model-bytes", type=Path)
    parser.add_argument("--preflight", type=Path)
    args = parser.parse_args()
    frozen()
    output = require_durable(args.output, ROOT)
    if output.exists():
        raise RuntimeError("existing evidence directory: no automatic rerun")
    if args.live:
        reservation = output.parent / "LIVE_CAMPAIGN_RESERVED.json"
        with reservation.open("x") as stream:
            append_line(stream, dict(campaign_id=CAMPAIGN, output=output.name,
                                     maximum_calls=CALL_LIMIT))
        fsync_dir(reservation.parent)
        preflight = json.loads(args.preflight.read_text())
        assert preflight["passed"] and preflight["actual_model_calls"] == 0
        assert preflight["frozen_inputs_sha256"] == file_digest(PACKAGE / "frozen-inputs.json")
        proof = json.loads(args.model_bytes.read_text())
        assert proof["complete_blobs_verified"]
        client = LocalModel()
        old = json.loads((ROOT / "experiments/model_recovery_proposal_v1/frozen-inputs.json").read_text())
        meta = metadata(client, old, proof)
        meta.pop("system", None)
        meta.pop("options", None)
        meta.update(campaign_id=CAMPAIGN, stateless=True, maximum_calls=CALL_LIMIT,
            registered_contexts=CONTEXT_LIMIT, model_roles=["MapJoint", "MapNextState", "MapConsequence"],
            probe_only=True, model_prediction_publication=False)
        result = campaign(output, client, meta)
    else:
        prior = [json.loads(line) for line in
                 (args.replay / "model-calls.jsonl").read_text().splitlines()]
        assert len(prior) == CALL_LIMIT
        meta = json.loads((args.replay / "metadata.json").read_text())
        assert meta["campaign_id"] == CAMPAIGN
        with patch("socket.socket", side_effect=AssertionError("ZERO INFERENCE in replay")):
            result = campaign(output, None, meta, prior)
        for name in FILES:
            assert (output / name).read_bytes() == (args.replay / name).read_bytes(), name
        source_snapshots = sorted((args.replay / "memory-snapshots").glob("*.json"))
        replay_snapshots = sorted((output / "memory-snapshots").glob("*.json"))
        assert source_snapshots and len(source_snapshots) == len(replay_snapshots)
        for source, copy in zip(source_snapshots, replay_snapshots):
            assert source.name == copy.name and source.read_bytes() == copy.read_bytes()
        print(f"PASS seven deterministic files and {len(source_snapshots)} snapshots byte-identical; ZERO INFERENCE.")
    print(result["status"])


if __name__ == "__main__":
    main()
