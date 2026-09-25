"""Zero-inference independence, authority, parser, durability, and replay controls."""
from copy import deepcopy
import argparse
import json
from pathlib import Path
from unittest.mock import patch

from experiments.model_map_proposal_v0.adapter import INVALID as INVALID_J
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import (
    Journal, atomic_write, file_digest, inspect)
from .protocol import (PACKAGE, CAMPAIGN, WORLDS, ROLES, CALL_LIMIT, CONTEXT_LIMIT,
    contexts, frozen, matched, body, request_hash, parse)
from .fixture import Context
from .run import campaign, FILES


def fake_call(role, parsed, index=0):
    return dict(call_id=f"preflight:{index}:{role}", parsed=deepcopy(parsed),
                parse_error=None if parsed is not None else "synthetic invalid")


class Synthetic:
    def __init__(self):
        self.requests = 0

    def generate(self, call):
        self.requests += 1
        assert self.requests <= CALL_LIMIT
        system = call["system"]
        if "exactly two fields" in system:
            value = {"next_state": 1, "consequence": 1}
        elif "next_state must" in system:
            value = {"next_state": 1}
        else:
            value = {"consequence": 1}
        return dict(raw_output=json.dumps(value), transport_error=None,
                    response_metadata={"synthetic_control": True})


def normalized_grounded(row):
    return {key: row[key] for key in ("control_prediction", "latch", "actual", "receipt",
        "authorization", "effects", "provenance", "control_measurement_matches",
        "before", "after")}


def run(out):
    registration = frozen()
    out.mkdir(exist_ok=False)
    descriptors = contexts()
    independence_rows = []
    canaries = []
    detachment = []
    with patch("socket.socket", side_effect=AssertionError("no inference in preflight")):
        for descriptor in descriptors:
            context = Context(descriptor)
            checks = matched(context.requests, descriptor)
            before = deepcopy(context.before)
            exact_c = json.dumps(context.requests["C"])
            exact_n = json.dumps(context.requests["N"])
            assert request_hash(context.requests["J"]) == descriptor["historical_request_sha256"]

            # Synthetic next-state values exist only after request construction.
            # Neither value, a shared mutable holder, nor reconciliation can alter C bytes.
            mutable = {"predicted_next_state": None, "reconciliation": None}
            c_hashes = []
            for synthetic_next in (0, 1, 2, 3, None):
                mutable["predicted_next_state"] = synthetic_next
                mutable["reconciliation"] = ({"next_state": synthetic_next, "consequence": 1}
                                               if synthetic_next is not None else None)
                rebuilt = body("C", descriptor, deepcopy(context.payload))
                assert json.dumps(rebuilt) == exact_c
                c_hashes.append(request_hash(rebuilt))
            assert len(set(c_hashes)) == 1
            assert json.dumps(context.requests["N"]) == exact_n
            assert context.before == before and context.audit_before()
            prompt = json.loads(context.requests["C"]["prompt"])
            assert set(prompt) == {"state", "target_action", "VERIFIED_CHRONOLOGICAL_HISTORY"}
            assert all(key not in prompt for key in ("predicted_next_state", "next_state_model_output",
                                                      "reconciliation", "execution_result"))
            independence_rows.append(dict(
                historical_context_number=descriptor["historical_context_number"],
                matched=checks, synthetic_next_state_variants=5,
                consequence_request_hashes=list(dict.fromkeys(c_hashes)),
                consequence_request_invariant=True, next_state_request_frozen=True,
                no_shared_mutable_state_path=True))

            # Change the hidden future after every request is frozen. Detached probes
            # must be scored against the new receipt and still cannot drive publication.
            oracle = context.c._active.world.fixture.oracle
            law = list(oracle._CONSEQUENCE)
            law[WORLDS[descriptor["world"]]["law_index"]] = -1
            oracle._CONSEQUENCE = tuple(law)
            calls = {
                "J": fake_call("J", {"next_state": WORLDS[descriptor["world"]]["next_state"],
                                      "consequence": 1}, descriptor["index"]),
                "N": fake_call("N", {"next_state": WORLDS[descriptor["world"]]["next_state"]},
                               descriptor["index"]),
                "C": fake_call("C", {"consequence": 1}, descriptor["index"]),
            }
            row = context.finish(calls)
            assert row["receipt"]["realized_consequence"] == row["actual"]["consequence"] == -1
            assert row["after"]["protected"]["memory"][-1]["consequence"] == -1
            assert row["scores"]["J"]["consequence"] is False
            assert row["scores"]["C"]["consequence"] is False
            assert row["after"]["protected"]["memory"][:-1] == before["protected"]["memory"]
            assert row["probe_detached"] and not row["probe_publication"]
            canaries.append(dict(historical_context_number=descriptor["historical_context_number"],
                request_bytes_unchanged=True, scored_future_not_executed_at_request=True,
                receipt=row["receipt"], published_last=row["after"]["protected"]["memory"][-1]))

        # Invalid N or C always abstains. Valid component outputs are copied before
        # reconciliation, and output variation cannot change grounded behavior.
        for world in WORLDS:
            descriptor = deepcopy(next(row for row in descriptors if row["world"] == world))
            baseline = None
            cases = (
                ({"next_state": WORLDS[world]["next_state"]}, {"consequence": 1}),
                ({"next_state": 0}, {"consequence": -1}),
                (None, {"consequence": 1}),
                ({"next_state": WORLDS[world]["next_state"]}, None),
            )
            for case_index, (next_value, consequence_value) in enumerate(cases):
                context = Context(descriptor)
                frozen_next = deepcopy(next_value)
                calls = {
                    "J": fake_call("J", {"next_state": WORLDS[world]["next_state"],
                                          "consequence": 1}, case_index),
                    "N": fake_call("N", next_value, case_index),
                    "C": fake_call("C", consequence_value, case_index),
                }
                row = context.finish(calls)
                grounded = normalized_grounded(row)
                if baseline is None:
                    baseline = grounded
                assert grounded == baseline
                assert calls["N"]["parsed"] == frozen_next
                assert (row["reconciled_prediction"] is None) == (
                    next_value is None or consequence_value is None)
                if row["reconciled_prediction"] is not None:
                    assert row["reconciled_prediction"] == {
                        "next_state": next_value["next_state"],
                        "consequence": consequence_value["consequence"]}
                detachment.append(dict(world=world, next_state=next_value,
                    consequence=consequence_value, reconciled=row["reconciled_prediction"],
                    identical_grounded_record=True))

        bad_n = ["{", '{"next_state":1} because', '{"next_state":true}',
            '{"next_state":1.0}', '{"next_state":"1"}', '{"next_state":4}',
            '{"next_state":-1}', '{"next_state":1,"consequence":1}',
            '{"next_state":1,"next_state":1}', "{}", "[]", "1", "null", None,
            '```json\n{"next_state":1}\n```']
        bad_c = ["{", '{"consequence":1} because', '{"consequence":true}',
            '{"consequence":1.0}', '{"consequence":"1"}', '{"consequence":2}',
            '{"consequence":-2}', '{"consequence":1,"next_state":1}',
            '{"consequence":1,"consequence":1}', "{}", "[]", "1", "null", None,
            '```json\n{"consequence":1}\n```']
        for role, values in (("J", INVALID_J), ("N", bad_n), ("C", bad_c)):
            for raw in values:
                try:
                    parse(raw, role)
                except (ValueError, TypeError, json.JSONDecodeError):
                    pass
                else:
                    raise AssertionError(f"invalid {role} response repaired")
        for value in range(4):
            assert parse(json.dumps({"next_state": value}), "N") == {"next_state": value}
        for value in (-1, 0, 1):
            assert parse(json.dumps({"consequence": value}), "C") == {"consequence": value}

        client = Synthetic()
        meta = dict(campaign_id=CAMPAIGN, synthetic_control=True, probe_only=True,
                    maximum_calls=CALL_LIMIT, registered_contexts=CONTEXT_LIMIT)
        campaign(out / "synthetic", client, meta)
        prior = [json.loads(line) for line in
                 (out / "synthetic/model-calls.jsonl").read_text().splitlines()]
        campaign(out / "synthetic-replay", None, meta, prior)
        for name in FILES:
            assert (out / "synthetic" / name).read_bytes() == (
                out / "synthetic-replay" / name).read_bytes(), name
        source_snapshots = sorted((out / "synthetic/memory-snapshots").glob("*.json"))
        replay_snapshots = sorted((out / "synthetic-replay/memory-snapshots").glob("*.json"))
        assert source_snapshots and len(source_snapshots) == len(replay_snapshots)
        for source, copy in zip(source_snapshots, replay_snapshots):
            assert source.name == copy.name and source.read_bytes() == copy.read_bytes()

        journal_rows = [json.loads(line) for line in
                        (out / "synthetic/journal.jsonl").read_text().splitlines()]
        for descriptor in descriptors:
            rows = [row for row in journal_rows if row["episode"] == descriptor["index"]]
            reconciliation_index = next(index for index, row in enumerate(rows)
                if row["status"] == "SPLIT_RECONCILIATION_FROZEN")
            for role in ("N", "C"):
                parse_index = next(index for index, row in enumerate(rows)
                    if row["call_id"] == f'{CAMPAIGN}:c{descriptor["index"]:02d}:{role}'
                    and row["status"] == "PARSED")
                assert parse_index < reconciliation_index
            execution_index = next(index for index, row in enumerate(rows)
                if row["status"] == "EXECUTION_INTENT_RECORDED")
            assert reconciliation_index < execution_index

        ambiguous = Journal(out / "ambiguous", campaign="PREFLIGHT_ONLY")
        ambiguous.append("REQUEST_INTENT_RECORDED", {}, "one")
        ambiguous.close()
        check = inspect(out / "ambiguous")
        assert check["ambiguous_calls"] == ["one"] and not check["automatic_reissue_allowed"]

    atomic_write(out / "independence-controls.json", independence_rows)
    atomic_write(out / "future-event-canaries.json", canaries)
    atomic_write(out / "detachment-controls.json", detachment)
    result = dict(
        passed=True, actual_model_calls=0, exact_historical_contexts=CONTEXT_LIMIT,
        historical_joint_request_hashes_reproduced=CONTEXT_LIMIT,
        registered_request_hashes=CALL_LIMIT, future_event_canaries=CONTEXT_LIMIT,
        synthetic_next_state_variants_per_context=5,
        consequence_request_invariant_to_synthetic_next_state=True,
        no_next_state_output_memory_or_mutable_state_path_to_consequence_request=True,
        consequence_cannot_alter_frozen_next_state=True,
        reconciliation_after_both_durable_parses=True,
        reconciliation_before_execution=True, invalid_component_abstains=True,
        mechanical_reconciliation_only=True, probe_execution_or_publication_authority=False,
        detached_output_variants=len(detachment), strict_J_parser_rejections=len(INVALID_J),
        strict_N_parser_rejections=len(bad_n), strict_C_parser_rejections=len(bad_c),
        synthetic_campaign_responses=CALL_LIMIT, synthetic_replay_responses=CALL_LIMIT,
        exact_replay_files=len(FILES), exact_replay_snapshots=len(source_snapshots),
        durability_ambiguous_call_stops=True, byte_identical_replay=True,
        frozen_inputs_sha256=file_digest(PACKAGE / "frozen-inputs.json"),
        parent=registration["parent"])
    atomic_write(out / "preflight.json", result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    run(parser.parse_args().out)
