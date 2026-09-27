from __future__ import annotations

from argparse import ArgumentParser
import json
from pathlib import Path

from .study import CONDITIONS, effects


def decision_rows(root: Path, condition: str) -> list[dict]:
    rows = []
    for line in (root / condition / "records.jsonl").read_text().splitlines():
        envelope = json.loads(line)
        if envelope["kind"] in ("AUTHORIZED_RECEIPT", "ABSTENTION"):
            rows.append(envelope["record"])
    return rows


def stage_summary(rows: list[dict]) -> dict:
    scored = [row for row in rows if row["consequence_correct"] is not None]
    return dict(opportunities=len(rows),
        authorized_executions=sum(row["receipt"] is not None for row in rows),
        abstentions=sum(row["receipt"] is None for row in rows),
        correct=sum(bool(row["consequence_correct"]) for row in scored),
        consequence_accuracy=(None if not scored else
                              sum(bool(row["consequence_correct"]) for row in scored) / len(scored)),
        invalid_outputs=sum(bool(row["invalid"]) for row in rows),
        realized_consequence=sum(row["receipt"]["realized_consequence"]
                                 for row in rows if row["receipt"]),
        actions=[None if row["receipt"] is None else row["receipt"]["action"]
                 for row in rows])


def persistence(rows: list[dict]) -> dict:
    prior_truth = {"ADVANCE": -1, "HOLD": 1}
    changed_truth = {"ADVANCE": 1, "HOLD": -1}
    false_after_change = 0
    false_after_restoration = 0
    restoration_errors = 0
    for row in rows:
        receipt = row.get("receipt")
        if not receipt or receipt["pre_state"] != 1 or receipt["action"] not in prior_truth:
            continue
        action, predicted = receipt["action"], row["predicted_consequence"]
        if row["phase"] == "change" and predicted == prior_truth[action] and not row["consequence_correct"]:
            false_after_change += 1
        if row["phase"] == "restoration":
            restoration_errors += int(not row["consequence_correct"])
            if predicted == changed_truth[action] and not row["consequence_correct"]:
                false_after_restoration += 1
    return dict(false_persistence_after_change=false_after_change,
        false_persistence_after_restoration=false_after_restoration,
        restoration_errors=restoration_errors)


def analyze(root: Path) -> dict:
    original = json.loads((root / "results.json").read_text())
    conditions = {}
    for name in CONDITIONS:
        rows = decision_rows(root, name)
        stage_a = [row for row in rows if row["stage"] == "A"]
        stage_b = [row for row in rows if row["stage"] == "B"]
        conditions[name] = dict(stage_a=stage_summary(stage_a),
            stage_b=stage_summary(stage_b), **persistence(stage_a),
            route_switch_events=[dict(stage=row["stage"], opportunity=row["opportunity"],
                state=row["receipt"]["pre_state"], action=row["receipt"]["action"],
                selected_before=row["selected_specialist"])
                for row in rows if row["router_switch"]],
            autonomous_modes=[row["decision"]["mode"] for row in stage_b])
    stage_a_metric = {name: {"accuracy": value["stage_a"]["consequence_accuracy"]}
                      for name, value in conditions.items()}
    stage_b_metric = {name: {"accuracy": value["stage_b"]["consequence_accuracy"],
                             "realized": value["stage_b"]["realized_consequence"]}
                      for name, value in conditions.items()}
    output = dict(status="COMPLETE", conditions=conditions,
        stage_a_accuracy_effects=effects(stage_a_metric, "accuracy"),
        stage_b_accuracy_effects=effects(stage_b_metric, "accuracy"),
        stage_b_realized_effects=effects(stage_b_metric, "realized"),
        behavioral_equivalence=dict(F_equals_Z=(conditions["F"]["stage_a"] ==
            conditions["Z"]["stage_a"] and conditions["F"]["stage_b"] ==
            conditions["Z"]["stage_b"]), H_equals_HZ_aggregate=(conditions["H"][
            "stage_a"] == conditions["HZ"]["stage_a"] and conditions["H"][
            "stage_b"] == conditions["HZ"]["stage_b"])),
        source_results_sha256=__import__("hashlib").sha256(
            (root / "results.json").read_bytes()).hexdigest())
    (root / "analysis.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    return output


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(analyze(args.output), sort_keys=True))

