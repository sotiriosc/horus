"""Frozen 33-call Split Map diagnostic on eleven retained failure contexts."""
from copy import deepcopy
from pathlib import Path
import hashlib
import json

from experiments.map_output_schema_isolation_v0.protocol import MODEL, OPTIONS, SYSTEMS as OLD_SYSTEMS
from experiments.model_map_proposal_v0.adapter import parse as parse_joint
from experiments.map_consequence_only_isolation_v0.protocol import parse as parse_consequence_old
from experiments.cross_episode_initialization_boundary_v1.projection import serialize
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import file_digest


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).parent
PARENT = "06748b2c085839786daf32f058bb24b57291c8f3"
CAMPAIGN = "HORUS_SPLIT_MAP_INDEPENDENT_PREDICTION_V0"
CONTEXT_LIMIT = 11
CALL_LIMIT = 33
ROLES = ("J", "N", "C")
CONTEXT_NUMBERS = (2, 3, 5, 7, 8, 9, 10, 27, 30, 32, 33)
FORENSIC = ROOT / "experiments/map_ranking_failure_forensics_v0/results.json"
RETAINED = ROOT / "experiments/map_ranking_failure_forensics_v0/retained-evidence.json"

SYSTEMS = {
    "J": OLD_SYSTEMS["J"],
    "N": ("Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. "
          "Reply with exactly one JSON object with exactly one field: next_state must be an integer in {0,1,2,3}. "
          "Do not include any other fields or explanation."),
    "C": OLD_SYSTEMS["S"],
}

WORLDS = {
    "W0": dict(state=0, action="ADVANCE", next_state=1, law_index=0,
               setup_actions=["HOLD", "ADVANCE", "RETREAT", "RETREAT", "ADVANCE"]),
    "W3": dict(state=3, action="RETREAT", next_state=2, law_index=11,
               setup_actions=["HOLD", "RETREAT", "ADVANCE", "ADVANCE", "RETREAT"]),
}

ORDERS = (
    ("J", "N", "C"), ("N", "C", "J"), ("C", "J", "N"),
    ("J", "C", "N"), ("N", "J", "C"), ("C", "N", "J"),
    ("J", "N", "C"), ("N", "C", "J"), ("C", "J", "N"),
    ("J", "C", "N"), ("N", "J", "C"),
)


def _source_rows():
    forensic = json.loads(FORENSIC.read_text())
    retained = json.loads(RETAINED.read_text())
    source_contexts = {row["context_index"]: row for row in forensic["contexts"]}
    retained_contexts = {row["context_index"]: row for row in retained}
    rows = []
    for context_index, number in enumerate(CONTEXT_NUMBERS):
        context = source_contexts[number]
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
            index=context_index, historical_context_number=number,
            call_order=list(ORDERS[context_index]), world=world, state=context["state"],
            family=context["family"], mapping_index=context["mapping_index"],
            mapping=ordered_mapping, target_alias=forecast["alias"], target_action=action,
            seed=forecast["seed"], historical_joint_prediction=forecast["parsed_prediction"],
            historical_realized_outcome=forecast["retained_detached_outcome"],
            historical_request_sha256=forecast["request_sha256"],
            historical_record_sha256=forecast["record_sha256"],
            historical_history_provenance_sha256=forecast["history_provenance_sha256"],
            authenticated_target_history=forecast["history"],
            historical_retained_call_index=forecast["retained_call_index"],
            historical_failure_class=context["classification"],
            historical_predicted_triple=context["predicted_triple"],
            historical_actual_triple=context["actual_triple"],
            historical_predicted_ranking=context["predicted_ranking"],
            historical_actual_ranking=context["actual_ranking"],
            setup_actions=WORLDS[world]["setup_actions"], setup_count=5, history_depth=1))
    assert len(rows) == CONTEXT_LIMIT
    assert sum(row["world"] == "W0" for row in rows) == 7
    assert sum(row["world"] == "W3" for row in rows) == 4
    return rows


def contexts():
    return deepcopy(_source_rows())


def control(descriptor):
    world = WORLDS[descriptor["world"]]
    return dict(next_state=world["next_state"], consequence=1)


def body(role, descriptor, payload):
    assert role in ROLES and OPTIONS["Map"]["num_predict"] == 32
    return dict(model=MODEL, system=SYSTEMS[role], prompt=serialize(payload), stream=False,
                options={**OPTIONS["Map"], "seed": descriptor["seed"]})


def request_hash(request):
    return hashlib.sha256(json.dumps(request).encode()).hexdigest()


def schedule():
    rows = []
    for descriptor in contexts():
        for role in descriptor["call_order"]:
            rows.append(dict(call_index=len(rows), context_index=descriptor["index"],
                             historical_context_number=descriptor["historical_context_number"],
                             role=role, seed=descriptor["seed"]))
    assert len(rows) == CALL_LIMIT
    return rows


def _unique(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("duplicate key")
        out[key] = value
    return out


def parse(raw, role):
    if role == "J":
        return parse_joint(raw)
    if role == "C":
        return parse_consequence_old(raw, "C")
    assert role == "N"
    if type(raw) is not str:
        raise ValueError("response is not text")
    value = json.loads(raw, object_pairs_hook=_unique)
    if type(value) is not dict or set(value) != {"next_state"}:
        raise ValueError("exact next-state-only schema required")
    if type(value["next_state"]) is not int:
        raise ValueError("exact integer required")
    if value["next_state"] not in range(4):
        raise ValueError("next_state outside finite domain")
    return value


def matched(requests, descriptor):
    assert set(requests) == set(ROLES)
    assert all(requests[role]["system"] == SYSTEMS[role] for role in ROLES)
    assert len({requests[role]["prompt"] for role in ROLES}) == 1
    assert len({json.dumps(requests[role]["options"], sort_keys=True) for role in ROLES}) == 1
    payload = json.loads(requests["J"]["prompt"])
    assert set(payload) == {"state", "target_action", "VERIFIED_CHRONOLOGICAL_HISTORY"}
    assert payload["state"] == descriptor["state"]
    assert payload["target_action"] == descriptor["target_alias"]
    assert payload["VERIFIED_CHRONOLOGICAL_HISTORY"] == descriptor["authenticated_target_history"]
    assert request_hash(requests["J"]) == descriptor["historical_request_sha256"]
    for role in ("N", "C"):
        normalized = deepcopy(requests[role])
        normalized["system"] = requests["J"]["system"]
        assert normalized == requests["J"]
    return dict(passed=True, historical_joint_request_reproduced=True,
                task_data_bytes_identical=True, model_sampler_seed_identical=True,
                predicted_next_state_absent_from_C_request=True,
                normalized_envelopes_identical=True)


def ranking(values):
    actions = ("ADVANCE", "HOLD", "RETREAT")
    return [[action for action in actions if values[action] == value]
            for value in sorted(set(values.values()), reverse=True)]


def ranking_effect(descriptor, consequence):
    actions = ("ADVANCE", "HOLD", "RETREAT")
    values = dict(zip(actions, descriptor["historical_predicted_triple"]))
    if consequence is not None:
        values[descriptor["target_action"]] = consequence
    ranked = ranking(values) if consequence is not None else None
    correct = bool(ranked and ranked[0] == descriptor["historical_actual_ranking"][0])
    return dict(consequence_by_action=values if consequence is not None else None,
                ranking=ranked, true_best_unique=correct)


def frozen():
    registration = json.loads((PACKAGE / "frozen-inputs.json").read_text())
    for name, digest in registration["sha256"].items():
        assert file_digest(ROOT / name) == digest, name
    return registration


def summarize(rows, completed_calls, integrity=True, replay=False,
              independence=True, reconciliation=True):
    details = []
    for row in rows:
        d = row["descriptor"]
        receipt = row["receipt"]
        actual = dict(next_state=receipt["next_state"], consequence=receipt["realized_consequence"])
        j = row["predictions"]["J"]
        n = row["predictions"]["N"]
        c = row["predictions"]["C"]
        split = row["reconciled_prediction"]
        j_next = bool(j and j["next_state"] == actual["next_state"])
        j_cons = bool(j and j["consequence"] == actual["consequence"])
        n_next = bool(n and n["next_state"] == actual["next_state"])
        c_cons = bool(c and c["consequence"] == actual["consequence"])
        j_exact = bool(j_next and j_cons)
        split_exact = bool(split and n_next and c_cons)
        reproduced = bool(j and not j_cons)
        repaired = bool(reproduced and c_cons)
        joint_rank = ranking_effect(d, j["consequence"] if j else None)
        split_rank = ranking_effect(d, c["consequence"] if c else None)
        details.append(dict(
            historical_context_number=d["historical_context_number"], world=d["world"],
            family=d["family"], mapping_index=d["mapping_index"], alias=d["target_alias"],
            seed=d["seed"], historical_map_prediction=d["historical_joint_prediction"],
            new_joint_prediction=j, independent_next_state_prediction=n,
            independent_consequence_prediction=c, reconciled_prediction=split,
            realized_receipt_prediction=actual, joint_next_state_correct=j_next,
            joint_consequence_correct=j_cons, split_next_state_correct=n_next,
            split_consequence_correct=c_cons, joint_exact_correct=j_exact,
            split_exact_correct=split_exact, historical_joint_consequence_failure_reproduced=reproduced,
            independent_consequence_repaired_reproduced_failure=repaired,
            reconciliation_exactly_combined=(split == ({"next_state": n["next_state"],
                "consequence": c["consequence"]} if n and c else None)),
            joint_ranking=joint_rank, split_ranking=split_rank,
            joint_ranking_failure_repaired=joint_rank["true_best_unique"],
            split_ranking_failure_repaired=split_rank["true_best_unique"],
            consequence_regression=(j_cons and not c_cons),
            exact_regression=(j_exact and not split_exact), call_order=d["call_order"]))
    complete = completed_calls == CALL_LIMIT and len(rows) == CONTEXT_LIMIT
    receipts = complete and all(row["authentic_post_response_score"] and
        row["authentic_history"] and row["probe_detached"] for row in rows)
    ready = complete and receipts and integrity and replay and independence and reconciliation
    reproduced = sum(row["historical_joint_consequence_failure_reproduced"] for row in details)
    repairs = sum(row["independent_consequence_repaired_reproduced_failure"] for row in details)
    exact_regressions = sum(row["exact_regression"] for row in details)
    if not ready:
        assessment = "AWAITING EXACT REPLAY OR INTEGRITY"
    elif reproduced <= CONTEXT_LIMIT // 2:
        assessment = "FAILURE REPRODUCIBILITY TOO WEAK TO EVALUATE SPLIT MAP"
    elif repairs == reproduced and not exact_regressions and all(
            row["reconciliation_exactly_combined"] for row in details):
        assessment = "SPLIT MAP POSITIVE ON EVERY REPRODUCED CONSEQUENCE FAILURE"
    else:
        assessment = "MIXED SPLIT MAP EVIDENCE"
    return dict(
        study="split-map-independent-prediction-v0", parent=PARENT,
        status="COMPLETE" if ready else "AWAITING_EXACT_REPLAY_OR_INTEGRITY",
        assessment=assessment, real_model_calls=completed_calls,
        registered_call_limit=CALL_LIMIT, contexts=CONTEXT_LIMIT, rows=details,
        historical_joint_failures_reproduced=reproduced,
        reproduced_failures_repaired_by_independent_consequence=repairs,
        accuracy=dict(
            joint_consequence=sum(row["joint_consequence_correct"] for row in details),
            split_consequence=sum(row["split_consequence_correct"] for row in details),
            joint_next_state=sum(row["joint_next_state_correct"] for row in details),
            split_next_state=sum(row["split_next_state_correct"] for row in details),
            joint_exact=sum(row["joint_exact_correct"] for row in details),
            split_exact=sum(row["split_exact_correct"] for row in details), denominator=CONTEXT_LIMIT),
        ranking_effect=dict(
            joint_repaired=sum(row["joint_ranking_failure_repaired"] for row in details),
            split_repaired=sum(row["split_ranking_failure_repaired"] for row in details),
            denominator=CONTEXT_LIMIT),
        regressions=dict(consequence=sum(row["consequence_regression"] for row in details),
                         exact=exact_regressions),
        reconciliation_new_errors=sum(not row["reconciliation_exactly_combined"] for row in details),
        independent_next_state_valid=sum(row["independent_next_state_prediction"] is not None for row in details),
        independent_consequence_valid=sum(row["independent_consequence_prediction"] is not None for row in details),
        joint_valid=sum(row["new_joint_prediction"] is not None for row in details),
        independence_controls_passed=independence,
        reconciliation_controls_passed=reconciliation,
        authentic_post_response_receipts=receipts, integrity_passed=integrity,
        exact_replay_passed=replay, Explorer_model_calls=0, Recovery_model_calls=0,
        scoring_scope=("Detached J/N/C predictions on eleven retained W0/W3 contexts, "
            "scored against one new original receipt per context after all three outputs "
            "were durably parsed and the N/C outputs mechanically reconciled."))
