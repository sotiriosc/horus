"""Frozen 22-call historical-failure-context schema diagnostic."""
from copy import deepcopy
from pathlib import Path
import hashlib
import json

from experiments.map_output_schema_isolation_v0.protocol import MODEL, OPTIONS, SYSTEMS, parse
from experiments.cross_episode_initialization_boundary_v1.projection import serialize
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import file_digest


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).parent
PARENT = "9219d313f3fca720c99bf7af9876d35e52ed89b9"
CAMPAIGN = "HORUS_MAP_FAILURE_CONTEXT_SCHEMA_TRANSFER_V0"
PAIR_LIMIT = 11
CALL_LIMIT = 22
FORENSIC = ROOT / "experiments/map_ranking_failure_forensics_v0/results.json"
RETAINED = ROOT / "experiments/map_ranking_failure_forensics_v0/retained-evidence.json"
CONTEXT_NUMBERS = (2, 3, 5, 7, 8, 9, 10, 27, 30, 32, 33)

WORLDS = {
    "W0": dict(state=0, action="ADVANCE", next_state=1, law_index=0,
               setup_actions=["HOLD", "ADVANCE", "RETREAT", "RETREAT", "ADVANCE"]),
    "W3": dict(state=3, action="RETREAT", next_state=2, law_index=11,
               setup_actions=["HOLD", "RETREAT", "ADVANCE", "ADVANCE", "RETREAT"]),
}


def _source_rows():
    forensic = json.loads(FORENSIC.read_text())
    retained = json.loads(RETAINED.read_text())
    contexts = {row["context_index"]: row for row in forensic["contexts"]}
    retained_contexts = {row["context_index"]: row for row in retained}
    rows = []
    for number in CONTEXT_NUMBERS:
        context = contexts[number]
        source = retained_contexts[number]
        world = context["world"]
        action = WORLDS[world]["action"]
        forecast = next(row for row in forensic["forecasts"]
                        if row["context_index"] == number and row["action"] == action)
        retained_action = next(row for row in source["actions"] if row["action"] == action)
        assert context["classification"] in ("MAP_TIE", "MAP_WRONG_UNIQUE")
        assert not forecast["consequence_correct"]
        assert forecast["parsed_prediction"] == retained_action["parsed_prediction"]
        assert forecast["history"] == retained_action["history"]
        assert context["mapping"] == source["mapping"]
        ordered_mapping = {alias: source["mapping"][alias]
                           for alias in source["registered_alias_order"]}
        assert forecast["retained_detached_outcome"] == {
            "next_state": WORLDS[world]["next_state"], "consequence": 1}
        assert forecast["history"] == [{
            "epoch": 1001, "transaction_id": 2, "surface_action": forecast["alias"],
            "next_state": WORLDS[world]["next_state"], "consequence": 1}]
        rows.append(dict(
            historical_context_number=number, world=world, state=context["state"],
            family=context["family"], mapping_index=context["mapping_index"],
            mapping=ordered_mapping, target_alias=forecast["alias"], target_action=action,
            seed=forecast["seed"], historical_joint_prediction=forecast["parsed_prediction"],
            historical_joint_consequence=forecast["parsed_prediction"]["consequence"],
            historical_realized_outcome=forecast["retained_detached_outcome"],
            historical_request_sha256=forecast["request_sha256"],
            historical_record_sha256=forecast["record_sha256"],
            historical_history_provenance_sha256=forecast["history_provenance_sha256"],
            authenticated_target_history=forecast["history"],
            historical_retained_call_index=forecast["retained_call_index"],
            historical_failure_class=context["classification"],
            setup_actions=WORLDS[world]["setup_actions"], setup_count=5, history_depth=1))
    assert len(rows) == PAIR_LIMIT
    assert sum(row["world"] == "W0" for row in rows) == 7
    assert sum(row["world"] == "W3" for row in rows) == 4
    return rows


def control(descriptor):
    world = WORLDS[descriptor["world"]]
    return dict(next_state=world["next_state"], consequence=1)


def schedule():
    out = []
    for pair_index, source in enumerate(_source_rows()):
        conditions = ("J", "S") if pair_index % 2 == 0 else ("S", "J")
        for condition in conditions:
            out.append(dict(index=len(out), pair_index=pair_index, condition=condition,
                            **deepcopy(source)))
    assert len(out) == CALL_LIMIT
    return out


def body(descriptor, payload):
    assert OPTIONS["Map"]["num_predict"] == 32
    return dict(model=MODEL, system=SYSTEMS[descriptor["condition"]],
                prompt=serialize(payload), stream=False,
                options={**OPTIONS["Map"], "seed": descriptor["seed"]})


def request_hash(request):
    return hashlib.sha256(json.dumps(request).encode()).hexdigest()


def matched(joint, schema, descriptor):
    assert joint["system"] == SYSTEMS["J"] and schema["system"] == SYSTEMS["S"]
    joint_sentences = joint["system"].split(". ")
    schema_sentences = schema["system"].split(". ")
    assert len(joint_sentences) == len(schema_sentences) == 3
    assert joint_sentences[0].encode() == schema_sentences[0].encode()
    assert joint_sentences[2].encode() == schema_sentences[2].encode()
    assert joint_sentences[1] != schema_sentences[1]
    assert joint["prompt"] == schema["prompt"]
    payload = json.loads(joint["prompt"])
    assert payload["state"] == descriptor["state"]
    assert payload["target_action"] == descriptor["target_alias"]
    assert payload["VERIFIED_CHRONOLOGICAL_HISTORY"] == descriptor["authenticated_target_history"]
    normalized = deepcopy(schema)
    normalized["system"] = joint["system"]
    assert normalized == joint
    assert json.dumps(normalized).encode() == json.dumps(joint).encode()
    assert joint["options"]["num_predict"] == schema["options"]["num_predict"] == 32
    assert request_hash(joint) == descriptor["historical_request_sha256"]
    return dict(passed=True, only_request_path="system.response_format_sentence",
                historical_joint_request_reproduced=True,
                first_instruction_sentence_bytes_identical=True,
                last_instruction_sentence_bytes_identical=True,
                task_data_bytes_identical=True,
                normalized_envelope_bytes_identical=True, num_predict_both=32)


def frozen():
    registration = json.loads((PACKAGE / "frozen-inputs.json").read_text())
    for name, digest in registration["sha256"].items():
        assert file_digest(ROOT / name) == digest, name
    return registration


def summarize(rows, completed_calls, integrity=True, replay=False,
              matched_requests=True, leak_controls=True):
    pairs = []
    for pair_index in range(PAIR_LIMIT):
        pair_rows = [row for row in rows if row["descriptor"]["pair_index"] == pair_index]
        if len(pair_rows) != 2:
            continue
        joint = next(row for row in pair_rows if row["descriptor"]["condition"] == "J")
        schema = next(row for row in pair_rows if row["descriptor"]["condition"] == "S")
        descriptor = joint["descriptor"]
        realized = joint["receipt"]["realized_consequence"]
        assert schema["receipt"]["realized_consequence"] == realized
        joint_consequence = joint["parsed"]["consequence"] if joint["valid"] else None
        schema_consequence = schema["parsed"]["consequence"] if schema["valid"] else None
        reproduced = joint["valid"] and joint_consequence != realized
        repaired = reproduced and schema["valid"] and schema_consequence == realized
        regression = (joint["valid"] and joint_consequence == realized and
                      (not schema["valid"] or schema_consequence != realized))
        pairs.append(dict(
            historical_context_number=descriptor["historical_context_number"],
            world=descriptor["world"], family=descriptor["family"],
            mapping_index=descriptor["mapping_index"], alias=descriptor["target_alias"],
            seed=descriptor["seed"],
            historical_joint_consequence=descriptor["historical_joint_consequence"],
            new_J_consequence=joint_consequence, S_consequence=schema_consequence,
            realized_receipt_consequence=realized,
            historical_J_failure_reproduced=reproduced,
            S_repaired_reproduced_failure=repaired,
            S_made_correct_J_worse=regression,
            exact_historical_J_value_reproduced=(joint["valid"] and
                joint_consequence == descriptor["historical_joint_consequence"]),
            J_valid=joint["valid"], S_valid=schema["valid"]))
    complete = completed_calls == len(rows) == CALL_LIMIT and len(pairs) == PAIR_LIMIT
    receipts = len(rows) == CALL_LIMIT and all(
        row["authentic_post_response_score"] and row["authentic_history"] and row["probe_detached"]
        for row in rows)
    ready = complete and receipts and integrity and replay and matched_requests and leak_controls
    return dict(
        study="map-failure-context-schema-transfer-v0", parent=PARENT,
        design="DESCRIPTIVE_DIAGNOSTIC_NO_A_B_C_THRESHOLDS",
        status="COMPLETE" if ready else "AWAITING_EXACT_REPLAY_OR_INTEGRITY",
        real_model_calls=completed_calls, registered_call_limit=CALL_LIMIT,
        registered_pairs=PAIR_LIMIT, complete_trials=len(rows),
        valid_J=sum(row["valid"] for row in rows if row["descriptor"]["condition"] == "J"),
        valid_S=sum(row["valid"] for row in rows if row["descriptor"]["condition"] == "S"),
        pairs=pairs,
        historical_joint_failures_reproduced=sum(pair["historical_J_failure_reproduced"] for pair in pairs),
        reproduced_failures_repaired_by_S=sum(pair["S_repaired_reproduced_failure"] for pair in pairs),
        S_regressions_from_correct_J=sum(pair["S_made_correct_J_worse"] for pair in pairs),
        exact_historical_J_values_reproduced=sum(pair["exact_historical_J_value_reproduced"] for pair in pairs),
        matched_request_check=matched_requests, authentic_post_response_receipts=receipts,
        future_answer_leak_controls=leak_controls, integrity_passed=integrity,
        exact_replay_passed=replay, Explorer_model_calls=0, Recovery_model_calls=0,
        scoring_scope=("Detached J/S probes on the eleven retained W0/W3 failure configurations, "
            "scored against new original simulated receipts after durable response and parse; "
            "ordinary non-model controls drive framework execution."))
