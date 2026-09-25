"""Zero-inference controls for the 11 registered matched historical contexts."""
from copy import deepcopy
import argparse
import json
from pathlib import Path
from unittest.mock import patch

from experiments.model_map_proposal_v0.adapter import INVALID
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import (
    Journal, inspect, atomic_write, file_digest)
from .protocol import (PACKAGE, CAMPAIGN, WORLDS, SYSTEMS, CALL_LIMIT, PAIR_LIMIT,
    schedule, frozen, summarize, matched, request_hash, parse)
from .fixture import Context
from .run import campaign, FILES


def fake_call(raw, descriptor):
    try:
        value = parse(raw, descriptor["condition"])
        error = None
    except (ValueError, TypeError) as exc:
        value = None
        error = str(exc)
    return dict(call_id=f'preflight:{descriptor["index"]}', parsed=value,
                parse_error=error, response=dict(raw_output=raw,
                transport_error=None, response_metadata={"synthetic_control": True}))


class Synthetic:
    def __init__(self):
        self.requests = 0

    def generate(self, call):
        self.requests += 1
        assert self.requests <= CALL_LIMIT
        value = dict(consequence=1)
        if call["system"] == SYSTEMS["J"]:
            payload = json.loads(call["exact_prompt"])
            value["next_state"] = payload["VERIFIED_CHRONOLOGICAL_HISTORY"][0]["next_state"]
        else:
            assert call["system"] == SYSTEMS["S"]
        return dict(raw_output=json.dumps(value), transport_error=None,
                    response_metadata={"synthetic_control": True})


def _synthetic_rows(joint_values, schema_values):
    rows = []
    for descriptor in schedule():
        value = (joint_values if descriptor["condition"] == "J" else schema_values)[descriptor["pair_index"]]
        parsed = dict(consequence=value)
        if descriptor["condition"] == "J":
            parsed["next_state"] = WORLDS[descriptor["world"]]["next_state"]
        rows.append(dict(descriptor=descriptor, valid=True, parsed=parsed,
            score=dict(consequence=value == 1,
                next_state=True if descriptor["condition"] == "J" else None,
                exact=(value == 1) if descriptor["condition"] == "J" else None),
            receipt=dict(realized_consequence=1), authentic_post_response_score=True,
            authentic_history=True, probe_detached=True))
    return rows


def run(out):
    registration = frozen()
    out.mkdir(exist_ok=False)
    canaries = []
    requests = {}
    detached = []
    baselines = {}
    descriptors = schedule()
    with patch("socket.socket", side_effect=AssertionError("no inference in preflight")):
        for descriptor in descriptors:
            context = Context(descriptor)
            before = deepcopy(context.before)
            exact_request = json.dumps(context.request)
            requests[descriptor["pair_index"], descriptor["condition"]] = deepcopy(context.request)
            if descriptor["condition"] == "J":
                assert request_hash(context.request) == descriptor["historical_request_sha256"]
            oracle = context.c._active.world.fixture.oracle
            law = list(oracle._CONSEQUENCE)
            law[WORLDS[descriptor["world"]]["law_index"]] = -1
            oracle._CONSEQUENCE = tuple(law)
            assert context.before == before and json.dumps(context.request) == exact_request
            context.audit_before()
            value = dict(consequence=1)
            if descriptor["condition"] == "J":
                value["next_state"] = WORLDS[descriptor["world"]]["next_state"]
            row = context.finish(fake_call(json.dumps(value), descriptor))
            assert row["receipt"]["realized_consequence"] == row["actual"]["consequence"] == -1
            assert row["after"]["protected"]["memory"][-1]["consequence"] == -1
            assert row["score"]["consequence"] is False
            assert not row["control_measurement_matches"]
            assert row["after"]["protected"]["memory"][:-1] == before["protected"]["memory"]
            canaries.append(dict(descriptor=descriptor, request_bytes_unchanged=True,
                scored_future_not_executed_at_request=True,
                authenticated_target_history=context.payload["VERIFIED_CHRONOLOGICAL_HISTORY"],
                receipt=row["receipt"], actual=row["actual"],
                published_last=row["after"]["protected"]["memory"][-1],
                control_prediction=row["control_prediction"], probe_score=row["score"]))

        matching = []
        for pair_index in range(PAIR_LIMIT):
            descriptor = next(d for d in descriptors if d["pair_index"] == pair_index)
            matching.append(dict(pair_index=pair_index,
                historical_context_number=descriptor["historical_context_number"],
                **matched(requests[pair_index, "J"], requests[pair_index, "S"], descriptor)))

        broken = deepcopy(requests[0, "S"])
        payload = json.loads(broken["prompt"])
        payload["VERIFIED_CHRONOLOGICAL_HISTORY"][0]["transaction_id"] = 3
        from experiments.cross_episode_initialization_boundary_v1.projection import serialize
        broken["prompt"] = serialize(payload)
        try:
            matched(requests[0, "J"], broken, descriptors[0])
        except AssertionError:
            pass
        else:
            raise AssertionError("additional visible mismatch admitted")
        broken = deepcopy(requests[0, "S"])
        broken["system"] = broken["system"].replace("realized outcome", "realized consequence")
        try:
            matched(requests[0, "J"], broken, descriptors[0])
        except AssertionError:
            pass
        else:
            raise AssertionError("changed task wording admitted")

        for world in WORLDS:
            baseline = None
            source = deepcopy(next(d for d in descriptors if d["world"] == world))
            for condition in ("J", "S"):
                for value in (-1, 0, 1, None):
                    descriptor = deepcopy(source)
                    descriptor["condition"] = condition
                    context = Context(descriptor)
                    raw = "{" if value is None else json.dumps(dict(
                        consequence=value,
                        **({"next_state": 3} if condition == "J" else {})))
                    row = context.finish(fake_call(raw, descriptor))
                    grounded = {key: row[key] for key in (
                        "control_prediction", "latch", "actual", "receipt", "authorization",
                        "effects", "provenance", "control_measurement_matches", "before", "after")}
                    if baseline is None:
                        baseline = grounded
                    assert grounded == baseline
                    assert row["probe_detached"] and not row["probe_publication"]
                    assert row["control_measurement_matches"]
                    assert row["score"]["consequence"] == (value == 1 if value is not None else None)
                    detached.append(dict(world=world, condition=condition, raw=raw,
                        parsed=row["parsed"], probe_score=row["score"],
                        identical_grounded_record=True))
            baselines[world] = baseline

        client = Synthetic()
        meta = dict(campaign_id=CAMPAIGN, synthetic_control=True, probe_only=True)
        campaign(out / "synthetic", client, meta)
        prior = [json.loads(line) for line in
                 (out / "synthetic/model-calls.jsonl").read_text().splitlines()]
        campaign(out / "synthetic-replay", None, meta, prior)
        for name in FILES:
            assert (out / "synthetic" / name).read_bytes() == (
                out / "synthetic-replay" / name).read_bytes()
        for path in (out / "synthetic/memory-snapshots").glob("*.json"):
            assert path.read_bytes() == (out / "synthetic-replay/memory-snapshots" / path.name).read_bytes()

        bad_joint = list(INVALID) + [
            '{"next_state":1,"next_state":1,"consequence":1}',
            '{"next_state":NaN,"consequence":1}']
        bad_schema = ["{", '{"consequence":1} because', 'because {"consequence":1}',
            '{"consequence":1,"next_state":1}', '{"consequence":true}',
            '{"consequence":1.0}', '{"consequence":"1"}', '{"consequence":null}',
            '{"consequence":2}', '{"consequence":-2}', '{"consequence":NaN}',
            '{"consequence":Infinity}', '{"consequence":1,"consequence":1}',
            '{"consequence":1}{"consequence":1}', "{}", "[]", "1", "null", None,
            '```json\n{"consequence":1}\n```']
        for condition, bad_values in (("J", bad_joint), ("S", bad_schema)):
            for raw in bad_values:
                try:
                    parse(raw, condition)
                except (ValueError, TypeError):
                    pass
                else:
                    raise AssertionError("invalid response repaired")
        for value in (-1, 0, 1):
            assert parse(json.dumps(dict(consequence=value)), "S") == dict(consequence=value)

        all_repaired = summarize(_synthetic_rows([0] * 11, [1] * 11), CALL_LIMIT, True, True)
        assert all_repaired["historical_joint_failures_reproduced"] == 11
        assert all_repaired["reproduced_failures_repaired_by_S"] == 11
        assert all_repaired["S_regressions_from_correct_J"] == 0
        all_regressed = summarize(_synthetic_rows([1] * 11, [0] * 11), CALL_LIMIT, True, True)
        assert all_regressed["historical_joint_failures_reproduced"] == 0
        assert all_regressed["S_regressions_from_correct_J"] == 11
        mixed = summarize(_synthetic_rows([0] * 5 + [1] * 6, [1] * 11), CALL_LIMIT, True, True)
        assert mixed["historical_joint_failures_reproduced"] == 5
        assert mixed["reproduced_failures_repaired_by_S"] == 5

        journal = Journal(out / "ambiguous", campaign="PREFLIGHT_ONLY")
        journal.append("REQUEST_INTENT_RECORDED", {}, "one")
        journal.close()
        check = inspect(out / "ambiguous")
        assert check["ambiguous_calls"] == ["one"] and not check["automatic_reissue_allowed"]
        partial = out / "ambiguous/journal.jsonl"
        partial.write_bytes(partial.read_bytes() + b"{")
        assert not inspect(out / "ambiguous")["journal_valid"]

    atomic_write(out / "canaries.json", canaries)
    atomic_write(out / "matched-requests.json", matching)
    atomic_write(out / "detachment-controls.json", dict(
        variants=detached, identical_grounded_records=baselines))
    result = dict(passed=True, actual_model_calls=0, canaries=CALL_LIMIT,
        historical_joint_request_hashes_reproduced=PAIR_LIMIT,
        matched_request_pairs=PAIR_LIMIT, task_field_mismatch_rejected=True,
        changed_instruction_rejected=True, exact_historical_contexts=PAIR_LIMIT,
        detached_output_variants=len(detached), synthetic_campaign_responses=CALL_LIMIT,
        synthetic_replay_responses=CALL_LIMIT, strict_J_parser_rejections=len(bad_joint),
        strict_S_parser_rejections=len(bad_schema), invalid_probes_no_authority=True,
        descriptive_summary_controls=3, durability_controls=2,
        byte_identical_replay=True, frozen_inputs_sha256=file_digest(PACKAGE / "frozen-inputs.json"),
        parent=registration["parent"], world_executions=dict(canaries=132,
            detachment_controls=96, synthetic_campaign=132, synthetic_replay=132,
            total=492))
    atomic_write(out / "preflight.json", result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    run(parser.parse_args().out)
