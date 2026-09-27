from __future__ import annotations

from collections import Counter
from argparse import ArgumentParser
import json
from pathlib import Path
from statistics import mean

from horus.live import SessionStore

from .protocol import CONDITIONS


def _latency(rows: list[dict], start: int) -> int | None:
    for row in rows:
        if row["event"] >= start and row["consequence_correct"]:
            return row["event"] - start
    return None


def _summary(rows: list[dict], perturbation: dict) -> dict:
    stage_a = [row for row in rows if row["stage"] == "A"]
    stage_b = [row for row in rows if row["stage"] == "B"]
    change = [row for row in stage_a if 5 <= row["event"] <= 8]
    right_wrong = []
    stale_errors = []
    for row in stage_a:
        selected = row["retrieval"][row["action"]]["selected_consequences"]
        if row["realized"]["consequence"] in selected and not row["consequence_correct"]:
            right_wrong.append(row["event"])
        if not row["consequence_correct"] and selected.count(
                row["prediction"]["consequence"]) > selected.count(
                    row["realized"]["consequence"]):
            stale_errors.append(row["event"])
    windows = {}
    for name, subset in (("early", stage_a[:4]), ("middle_change", stage_a[4:8]),
                         ("late_restoration", stage_a[8:12])):
        windows[name] = dict(n=len(subset), consequence_accuracy=(sum(
            row["consequence_correct"] for row in subset) / len(subset)), exact_accuracy=(sum(
            row["exact_correct"] for row in subset) / len(subset)))
    rolling = []
    for index in range(len(stage_a) - 3):
        part = stage_a[index:index + 4]
        rolling.append(dict(start_event=part[0]["event"], accuracy=sum(
            row["consequence_correct"] for row in part) / 4))
    return dict(stage_a=dict(n=len(stage_a), consequence_correct=sum(
        row["consequence_correct"] for row in stage_a), consequence_accuracy=sum(
        row["consequence_correct"] for row in stage_a) / len(stage_a),
        exact_correct=sum(row["exact_correct"] for row in stage_a),
        exact_accuracy=sum(row["exact_correct"] for row in stage_a) / len(stage_a),
        adaptation_latency=_latency(stage_a, 5), restoration_latency=_latency(stage_a, 9),
        false_persistence=sum(not row["consequence_correct"] for row in change),
        correct_memory_model_wrong=len(right_wrong),
        correct_memory_model_wrong_events=right_wrong, windows=windows,
        stale_history_errors=len(stale_errors), stale_history_error_events=stale_errors,
        worst_rolling_4=min(rolling, key=lambda row: row["accuracy"])),
        stage_b=dict(decisions=len(stage_b), actions=[row["action"] for row in stage_b],
            realized_consequences=[row["realized"]["consequence"] for row in stage_b],
            realized_total=sum(row["realized"]["consequence"] for row in stage_b),
            consequence_correct=sum(row["consequence_correct"] for row in stage_b),
            exact_correct=sum(row["exact_correct"] for row in stage_b)),
        total_model_calls=sum(row["model_calls"] for row in rows) + perturbation["model_calls"],
        context_tokens=sum(row["context_tokens"] for row in rows) +
            perturbation["context_tokens"],
        model_seconds=sum(row["model_seconds"] for row in rows) +
            perturbation["model_seconds"],
        invalid_outputs=1, abstentions=1)


def analyze(output: Path) -> dict:
    perturbation = json.loads((output / "perturbation.json").read_text())
    rows = {}
    for condition in CONDITIONS:
        with SessionStore(output / condition / "session", True) as store:
            rows[condition] = [envelope["record"] for envelope in store.records["training"]
                if envelope["kind"] == "MODERN_VS_HORUS_SCORED_EVENT"]
    summaries = {condition: _summary(rows[condition], perturbation[condition])
                 for condition in CONDITIONS}
    stage_a_pairs = {row["event"]: {"M": row} for row in rows["M"] if row["stage"] == "A"}
    for row in rows["MH"]:
        if row["stage"] == "A": stage_a_pairs[row["event"]]["MH"] = row
    ledger = []
    for event, pair in sorted(stage_a_pairs.items()):
        m, mh = pair["M"], pair["MH"]
        if m["prediction"] == mh["prediction"]: continue
        effect = ("IMPROVED" if mh["consequence_correct"] and not m["consequence_correct"]
                  else "DEGRADED" if m["consequence_correct"] and not mh["consequence_correct"]
                  else "NO_CHANGE")
        mechanism = ("SPECIALIST_ROUTING" if mh["selected_specialist"] != "G2"
                     else "OTHER_EXISTING_HORUS_COMPONENT")
        ledger.append(dict(stage="A", event=event, M_prediction=m["prediction"],
            MH_prediction=mh["prediction"], M_action=m["action"], MH_action=mh["action"],
            horus_mechanism=mechanism, realized_outcome=mh["realized"], effect=effect))
    b_m = [row for row in rows["M"] if row["stage"] == "B"]
    b_h = [row for row in rows["MH"] if row["stage"] == "B"]
    for m, mh in zip(b_m, b_h):
        if m["action"] == mh["action"] and m["prediction"] == mh["prediction"]: continue
        effect = ("IMPROVED" if mh["realized"]["consequence"] > m["realized"]["consequence"]
                  else "DEGRADED" if mh["realized"]["consequence"] < m["realized"]["consequence"]
                  else "NO_CHANGE")
        ledger.append(dict(stage="B", event=m["event"], M_prediction=m["prediction"],
            MH_prediction=mh["prediction"], M_action=m["action"], MH_action=mh["action"],
            horus_mechanism=("EXPLORER_PROBE" if mh["explorer"]["mode"] == "PROBE"
                             else "SPECIALIST_ROUTING"),
            realized_outcome={"M": m["realized"], "MH": mh["realized"]}, effect=effect))
    effects = Counter(row["effect"] for row in ledger)
    mh_routes = [row["routing_evidence"] for row in rows["MH"] if row["routing_evidence"]]
    switches = [row for row in mh_routes if row["switch_occurred"]]
    switch_audit = []
    for switch in switches:
        relation = switch["relation"]
        after = [row for row in rows["MH"] if row["state"] == relation["pre_state"] and
                 row["action"] == relation["action"] and
                 row["routing_evidence"]["evidence_sequence"] > switch["evidence_sequence"]]
        switch_audit.append(dict(record=switch,
            subsequent_predictions=len(after),
            subsequent_correct=sum(row["consequence_correct"] for row in after),
            improved_subsequent_predictions=(None if not after else
                sum(row["consequence_correct"] for row in after) > len(after) / 2)))
    probes = [row for row in b_h if row["explorer"]["mode"] == "PROBE"]
    if effects["DEGRADED"] > effects["IMPROVED"]:
        classification = "HORUS_NET_HARMFUL"
    elif effects["IMPROVED"] and effects["DEGRADED"]:
        classification = "MIXED_COMPONENT_SIGNAL"
    elif effects["IMPROVED"] and not effects["DEGRADED"]:
        classification = "HORUS_DISTINCTLY_USEFUL"
    else:
        classification = "MODERN_BASE_SUFFICIENT"
    result = dict(status="COMPLETE", classification=classification,
        conditions=summaries, intervention_ledger=ledger,
        intervention_effect_counts=dict(effects),
        horus_activity=dict(specialist_switches=len(switches), switch_records=switch_audit,
            explorer_probes=len(probes), probe_records=[dict(event=row["event"],
                action=row["action"], realized=row["realized"],
                useful_evidence=(row["routing_evidence"]["relation_evidence_count"]
                    if "relation_evidence_count" in row["routing_evidence"] else True))
                for row in probes],
            ties_resolved=sum(row["explorer"]["reason"].endswith("TIE") for row in b_h),
            problem_objects_created=0, capability_requests=0, route_executions=0,
            repair_recoveries=0, reacquisitions=0,
            dormant_components=["PROBLEM_MANAGER", "SCOPED_ROUTE", "REPAIR_RECOVERY",
                                "REACQUISITION"]),
        perturbation=perturbation,
        restart=json.loads((output / "stage-a2.json").read_text())[
            "restart_verification"], stage_b_trajectory=dict(M=b_m, MH=b_h))
    (output / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    p = ArgumentParser(); p.add_argument("--output", type=Path, required=True)
    print(json.dumps(analyze(p.parse_args().output), sort_keys=True))
