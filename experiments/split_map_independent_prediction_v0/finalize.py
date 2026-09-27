"""Verify live/replay archives and publish compact Split Map evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from experiments.model_proposal_role_composition_v2_replacement_r1.durable import atomic_write, file_digest, inspect
from .protocol import (ROOT, PACKAGE, PARENT, CAMPAIGN, CALL_LIMIT, CONTEXT_LIMIT,
    OPTIONS, ROLES, contexts, summarize, frozen, matched)
from .run import FILES


def lines(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def git(*args):
    return subprocess.check_output(("git", *args), cwd=ROOT, text=True).strip()


def run(live, replay, preflight):
    registration = frozen()
    pre = json.loads(preflight.read_text())
    assert pre["passed"] and pre["actual_model_calls"] == 0
    assert pre["frozen_inputs_sha256"] == file_digest(PACKAGE / "frozen-inputs.json")
    assert pre["consequence_request_invariant_to_synthetic_next_state"]
    assert pre["reconciliation_after_both_durable_parses"]
    live_check = inspect(live)
    replay_check = inspect(replay)
    assert live_check["journal_valid"] and replay_check["journal_valid"]
    assert not live_check["ambiguous_calls"] and not replay_check["ambiguous_calls"]
    for name in FILES:
        assert (live / name).read_bytes() == (replay / name).read_bytes(), name
    live_snapshots = sorted((live / "memory-snapshots").glob("*.json"))
    replay_snapshots = sorted((replay / "memory-snapshots").glob("*.json"))
    assert live_snapshots and len(live_snapshots) == len(replay_snapshots)
    for original, copy in zip(live_snapshots, replay_snapshots):
        assert original.name == copy.name and original.read_bytes() == copy.read_bytes()

    calls = lines(live / "model-calls.jsonl")
    steps = lines(live / "steps.jsonl")
    context_rows = lines(live / "contexts.jsonl")
    registered = json.loads((PACKAGE / "schedule.json").read_text())
    assert len(calls) == len(registered) == CALL_LIMIT
    assert len(steps) == len(context_rows) == CONTEXT_LIMIT
    metadata = json.loads((live / "metadata.json").read_text())
    assert metadata["campaign_id"] == CAMPAIGN and metadata["maximum_calls"] == CALL_LIMIT
    assert metadata["registered_contexts"] == CONTEXT_LIMIT
    by_context = {descriptor["index"]: {} for descriptor in contexts()}
    compact_calls = []
    for index, (call, expected) in enumerate(zip(calls, registered)):
        assert index == call["index"] == expected["call_index"]
        intent = call["intent"]
        assert intent["context_index"] == expected["context_index"]
        assert intent["role"] == expected["role"]
        assert hashlib.sha256(intent["exact_request_json"].encode()).hexdigest() == expected["request_sha256"]
        by_context[expected["context_index"]][expected["role"]] = json.loads(intent["exact_request_json"])
        compact_calls.append(dict(index=index, call_id=call["call_id"],
            historical_context_number=expected["historical_context_number"], role=expected["role"],
            request_sha256=expected["request_sha256"], parsed=call["parsed"],
            parse_error=call["parse_error"],
            source_call_sha256=hashlib.sha256(json.dumps(call, sort_keys=True).encode()).hexdigest()))
    request_checks = []
    for descriptor in contexts():
        check = matched(by_context[descriptor["index"]], descriptor)
        request_checks.append(dict(historical_context_number=descriptor["historical_context_number"], **check))
    for expected, context_record, step in zip(contexts(), context_rows, steps):
        assert expected == context_record["descriptor"] == step["descriptor"]
        assert step["reconciliation"]["both_component_outputs_durable_and_parsed"]
        assert step["reconciliation"]["mechanical"] and not step["reconciliation"]["model_inference"]
        assert step["probe_detached"] and not step["probe_publication"]

    result = summarize(steps, CALL_LIMIT, integrity=True, replay=True,
                       independence=pre["passed"], reconciliation=True)
    result["registration_commit"] = git("rev-parse", "HEAD")
    result["registration_parent"] = PARENT
    result["calls"] = compact_calls
    result["request_checks"] = request_checks
    result["model"] = metadata.get("model")
    result["model_digest"] = metadata["installed_model"]["digest"]
    result["sampler"] = OPTIONS["Map"]
    result["retries"] = 0
    result["replacement_calls"] = 0

    changed = git("diff", "--name-only", PARENT, "--").splitlines()
    assert all(name.startswith("experiments/split_map_independent_prediction_v0/") or
               name == "research/split-map-independent-prediction-v0-preregistration.md"
               for name in changed)
    verification = dict(
        passed=True, parent=PARENT, registration_commit=result["registration_commit"],
        parent_files_preserved=registration["parent_files"],
        historical_context_numbers=registration["historical_context_numbers"],
        registered_request_hashes=CALL_LIMIT,
        historical_joint_request_hashes_reproduced=CONTEXT_LIMIT,
        preflight=pre, exact_replay_files=len(FILES),
        exact_replay_snapshots=len(live_snapshots),
        live_archive_sha256={name: file_digest(live / name) for name in FILES},
        replay_archive_sha256={name: file_digest(replay / name) for name in FILES},
        archive_paths_published=False, raw_requests_published=False,
        raw_outputs_published=False, real_model_calls=CALL_LIMIT,
        retries=0, replacement_calls=0, Explorer_model_calls=0, Recovery_model_calls=0,
        consequence_request_independent_of_next_state_output=True,
        reconciliation_mechanical_and_post_freeze=True,
        no_probe_execution_or_publication_authority=True)
    atomic_write(PACKAGE / "results.json", result)
    atomic_write(PACKAGE / "verification.json", verification)
    write_report(ROOT / "research/split-map-independent-prediction-v0-results.md", result)
    print(json.dumps({key: result[key] for key in (
        "status", "assessment", "historical_joint_failures_reproduced",
        "reproduced_failures_repaired_by_independent_consequence", "accuracy",
        "ranking_effect", "regressions", "reconciliation_new_errors")}, sort_keys=True))


def fmt(value):
    if value is None:
        return "invalid"
    if isinstance(value, dict) and set(value) == {"next_state", "consequence"}:
        return f"({value['next_state']},{value['consequence']:+d})"
    if isinstance(value, dict) and set(value) == {"next_state"}:
        return str(value["next_state"])
    if isinstance(value, dict) and set(value) == {"consequence"}:
        return f"{value['consequence']:+d}"
    return str(value)


def write_report(path, result):
    rows = [
        "# Split Map independent prediction v0 — results", "",
        f"**{result['assessment']}**", "",
        "| Ctx | World | Family | Map | Alias | Seed | Historical Map | New J | N | C | Reconciled | Receipt | J next | J cons | Split next | Split cons | J exact | Split exact | J failure reproduced | C repaired | J rank repaired | Split rank repaired |",
        "|---:|---|---|---:|---|---:|---|---|---:|---:|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in result["rows"]:
        rows.append("| {ctx} | {world} | {family} | {mapping} | {alias} | {seed} | {historical} | {joint} | {next_value} | {cons_value} | {split} | {receipt} | {jn} | {jc} | {sn} | {sc} | {je} | {se} | {reproduced} | {repaired} | {jr} | {sr} |".format(
            ctx=row["historical_context_number"], world=row["world"], family=row["family"],
            mapping=row["mapping_index"], alias=row["alias"], seed=row["seed"],
            historical=fmt(row["historical_map_prediction"]), joint=fmt(row["new_joint_prediction"]),
            next_value=fmt(row["independent_next_state_prediction"]),
            cons_value=fmt(row["independent_consequence_prediction"]),
            split=fmt(row["reconciled_prediction"]), receipt=fmt(row["realized_receipt_prediction"]),
            jn=row["joint_next_state_correct"], jc=row["joint_consequence_correct"],
            sn=row["split_next_state_correct"], sc=row["split_consequence_correct"],
            je=row["joint_exact_correct"], se=row["split_exact_correct"],
            reproduced=row["historical_joint_consequence_failure_reproduced"],
            repaired=row["independent_consequence_repaired_reproduced_failure"],
            jr=row["joint_ranking_failure_repaired"], sr=row["split_ranking_failure_repaired"]))
    accuracy = result["accuracy"]
    ranking = result["ranking_effect"]
    rows.extend(["",
        f"- Historical joint consequence failures reproduced: **{result['historical_joint_failures_reproduced']}/11**.",
        f"- Reproduced failures repaired by independent consequence: **{result['reproduced_failures_repaired_by_independent_consequence']}/{result['historical_joint_failures_reproduced']}**.",
        f"- Consequence accuracy: joint **{accuracy['joint_consequence']}/11**; split **{accuracy['split_consequence']}/11**.",
        f"- Next-state accuracy: joint **{accuracy['joint_next_state']}/11**; independent **{accuracy['split_next_state']}/11**.",
        f"- Exact accuracy: joint **{accuracy['joint_exact']}/11**; split **{accuracy['split_exact']}/11**.",
        f"- Original ranking failure repaired: joint **{ranking['joint_repaired']}/11**; split **{ranking['split_repaired']}/11**.",
        f"- Regressions: consequence **{result['regressions']['consequence']}**; exact **{result['regressions']['exact']}**.",
        f"- Mechanical reconciliation errors: **{result['reconciliation_new_errors']}**.", "",
        "All 33 registered attempts completed without retry or replacement. Zero-inference controls established that the consequence request bytes are invariant to synthetic next-state outputs, both component parses precede reconciliation, invalid components abstain, and no probe gains execution or publication authority. Exact replay passed. This remains a detached research implementation; production Map and Explorer were not modified.", ""])
    path.write_text("\n".join(rows))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", type=Path, required=True)
    parser.add_argument("--replay", type=Path, required=True)
    parser.add_argument("--preflight", type=Path, required=True)
    args = parser.parse_args()
    run(args.live, args.replay, args.preflight)
