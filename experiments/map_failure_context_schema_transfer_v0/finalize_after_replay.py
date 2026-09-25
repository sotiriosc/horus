"""Post-replay reporting correction; the registered experiment remains frozen."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from experiments.model_proposal_role_composition_v2_replacement_r1.durable import atomic_write, file_digest, inspect
from .protocol import (ROOT, PACKAGE, PARENT, CAMPAIGN, CALL_LIMIT, PAIR_LIMIT,
    OPTIONS, schedule, summarize, frozen, matched)
from .run import FILES


def lines(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def git(*args):
    return subprocess.check_output(("git", *args), cwd=ROOT, text=True).strip()


def assessment(result):
    reproduced = result["historical_joint_failures_reproduced"]
    repaired = result["reproduced_failures_repaired_by_S"]
    regressions = result["S_regressions_from_correct_J"]
    if reproduced <= PAIR_LIMIT // 2:
        return "FAILURE REPRODUCIBILITY / CONTEXT SENSITIVITY IS THE NEXT PROBLEM"
    if repaired == reproduced and regressions == 0:
        return "SCHEMA COUPLING APPEARS IN EVERY REPRODUCED FAILURE"
    return "MIXED SCHEMA-COUPLING AND REPRODUCIBILITY EVIDENCE"


def run(live, replay, preflight):
    registration = frozen()
    pre = json.loads(preflight.read_text())
    assert pre["passed"] and pre["actual_model_calls"] == 0
    assert pre["frozen_inputs_sha256"] == file_digest(PACKAGE / "frozen-inputs.json")
    live_check = inspect(live)
    replay_check = inspect(replay)
    assert live_check["journal_valid"] and replay_check["journal_valid"]
    assert not live_check["ambiguous_calls"] and not replay_check["ambiguous_calls"]
    for name in FILES:
        assert (live / name).read_bytes() == (replay / name).read_bytes(), name
    live_snapshots = sorted((live / "memory-snapshots").glob("*.json"))
    replay_snapshots = sorted((replay / "memory-snapshots").glob("*.json"))
    assert len(live_snapshots) == len(replay_snapshots) == CALL_LIMIT
    for original, copy in zip(live_snapshots, replay_snapshots):
        assert original.name == copy.name and original.read_bytes() == copy.read_bytes()
    calls = lines(live / "model-calls.jsonl")
    steps = lines(live / "steps.jsonl")
    contexts = lines(live / "contexts.jsonl")
    assert len(calls) == len(steps) == len(contexts) == CALL_LIMIT
    metadata = json.loads((live / "metadata.json").read_text())
    assert metadata["campaign_id"] == CAMPAIGN and metadata["maximum_calls"] == CALL_LIMIT
    assert metadata["registered_pairs"] == PAIR_LIMIT
    registered = json.loads((PACKAGE / "schedule.json").read_text())
    compact_calls = []
    requests = {}
    for index, (call, step, context, expected) in enumerate(zip(calls, steps, contexts, registered)):
        descriptor = step["descriptor"]
        assert index == descriptor["index"] == call["index"]
        assert descriptor == expected["descriptor"] == context["descriptor"]
        # JSONL is deliberately written with sorted object keys. Hash the exact
        # preregistered request bytes retained before that serialization layer.
        assert hashlib.sha256(call["intent"]["exact_request_json"].encode()).hexdigest() == expected["request_sha256"]
        requests[descriptor["pair_index"], descriptor["condition"]] = json.loads(
            call["intent"]["exact_request_json"])
        compact_calls.append(dict(
            index=index,
            historical_context_number=descriptor["historical_context_number"],
            condition=descriptor["condition"],
            request_sha256=expected["request_sha256"],
            raw_output=call["response"]["raw_output"],
            parsed=call["parsed"], parse_error=call["parse_error"],
            score=step["score"], valid=step["valid"],
            authenticated_target_history=descriptor["authenticated_target_history"],
            actual=step["actual"], receipt=step["receipt"],
            control_prediction=step["control_prediction"],
            control_measurement_matches=step["control_measurement_matches"],
            authorization=step["authorization"], effects=step["effects"],
            probe_detached=step["probe_detached"], probe_publication=step["probe_publication"],
            source_call_sha256=hashlib.sha256(json.dumps(call, sort_keys=True).encode()).hexdigest(),
            source_step_sha256=hashlib.sha256(json.dumps(step, sort_keys=True).encode()).hexdigest()))
    matching = []
    for pair_index in range(PAIR_LIMIT):
        descriptor = next(d for d in schedule() if d["pair_index"] == pair_index)
        matching.append(dict(pair_index=pair_index,
            historical_context_number=descriptor["historical_context_number"],
            **matched(requests[pair_index, "J"], requests[pair_index, "S"], descriptor)))
    result = summarize(steps, CALL_LIMIT, integrity=True, replay=True,
                       matched_requests=all(row["passed"] for row in matching),
                       leak_controls=pre["canaries"] == CALL_LIMIT)
    result["assessment"] = assessment(result)
    result["registration_commit"] = git("rev-parse", "HEAD")
    result["registration_parent"] = PARENT
    result["calls"] = compact_calls
    result["matched_pairs"] = matching
    result["model"] = metadata.get("model")
    result["model_digest"] = metadata["installed_model"]["digest"]
    result["sampler"] = OPTIONS["Map"]
    result["finalization_correction"] = (
        "The frozen finalizer incorrectly reserialized sorted-key JSONL request objects for a byte-order-sensitive hash. "
        "This post-replay reporter hashes the recorder's preserved exact_request_json bytes. No request, response, score, or decision changed."
    )
    result["replacement_calls"] = 0
    result["retries"] = 0

    changed = git("diff", "--name-only", PARENT, "--").splitlines()
    assert all(name.startswith("experiments/map_failure_context_schema_transfer_v0/") or
               name == "research/map-failure-context-schema-transfer-v0-preregistration.md"
               for name in changed)
    verification = dict(
        passed=True, parent=PARENT, registration_commit=result["registration_commit"],
        parent_files_preserved=registration["parent_files"],
        historical_context_numbers=registration["historical_context_numbers"],
        registered_request_hashes=CALL_LIMIT,
        historical_joint_request_hashes_reproduced=PAIR_LIMIT,
        preflight=pre, exact_replay_files=len(FILES), exact_replay_snapshots=CALL_LIMIT,
        live_archive_sha256={name: file_digest(live / name) for name in FILES},
        replay_archive_sha256={name: file_digest(replay / name) for name in FILES},
        archive_paths_published=False, raw_requests_published=False,
        real_model_calls=CALL_LIMIT, retries=0, replacement_calls=0,
        Explorer_model_calls=0, Recovery_model_calls=0,
        post_inference_reporting_correction=True,
        correction_scope="request-hash byte source only: intent.exact_request_json",
        frozen_finalizer_preserved=True,
        supplemental_unit_tests=[
            dict(command=("python3 -m unittest experiments.map_explorer_oracle_decomposition_v0.test_study "
                          "experiments.map_output_schema_isolation_v0.test_study"),
                 result="COMMAND ERROR: second named module does not exist; seven decomposition tests passed before loader error"),
            dict(command="python3 -m unittest experiments.map_explorer_oracle_decomposition_v0.test_study",
                 result="PASS", tests=7),
        ],
        no_probe_execution_or_publication_authority=all(
            row["probe_detached"] and not row["probe_publication"] for row in steps))
    atomic_write(PACKAGE / "results.json", result)
    atomic_write(PACKAGE / "verification.json", verification)
    write_report(ROOT / "research/map-failure-context-schema-transfer-v0-results.md", result)
    print(json.dumps({key: result[key] for key in (
        "status", "historical_joint_failures_reproduced",
        "reproduced_failures_repaired_by_S", "S_regressions_from_correct_J",
        "assessment")}, sort_keys=True))


def write_report(path, result):
    rows = [
        "# Map failure-context schema transfer v0 — results",
        "",
        "**DESCRIPTIVE DIAGNOSTIC COMPLETE — no A/B/C classification.**",
        "",
        "| Historical context | World | Family | Mapping | Alias | Seed | Historical J consequence | New J consequence | S consequence | Realized receipt | Historical J failure reproduced | S repaired it |",
        "|---:|---|---|---:|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for pair in result["pairs"]:
        rows.append("| {historical_context_number} | {world} | {family} | {mapping_index} | {alias} | {seed} | {historical_joint_consequence} | {new_J_consequence} | {S_consequence} | {realized_receipt_consequence} | {historical_J_failure_reproduced} | {S_repaired_reproduced_failure} |".format(**pair))
    rows.extend([
        "",
        f"1. Historical joint failures reproduced: **{result['historical_joint_failures_reproduced']}/11**.",
        f"2. Reproduced failures repaired by consequence-only: **{result['reproduced_failures_repaired_by_S']}/{result['historical_joint_failures_reproduced']}**.",
        f"3. Cases where S made a correct J prediction worse: **{result['S_regressions_from_correct_J']}**.",
        f"4. Assessment: **{result['assessment']}**. The other **{PAIR_LIMIT - result['historical_joint_failures_reproduced']}/11** historical failures did not reproduce, so context sensitivity remains a limit on the scope of that result.",
        "",
        "The 22 registered calls completed with no retries or replacements. J and S were matched within each pair; all J requests reproduced the retained historical request hash. Probes remained detached and were scored only after new original receipts. Exact replay passed. See `experiments/map_failure_context_schema_transfer_v0/results.json` and `verification.json` for compact evidence.",
        "",
        "Reporting note: the frozen finalizer stopped because it reserialized sorted-key JSONL objects for a byte-order-sensitive request hash. The preserved frozen finalizer is unchanged. The post-replay reporter uses each recorder intent's already-preserved `exact_request_json` bytes; no request, response, score or decision changed.",
        "",
    ])
    path.write_text("\n".join(rows))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", type=Path, required=True)
    parser.add_argument("--replay", type=Path, required=True)
    parser.add_argument("--preflight", type=Path, required=True)
    args = parser.parse_args()
    run(args.live, args.replay, args.preflight)
