"""Final zero-inference analysis with preregistered prior-evidence denominator.

Raw scoring counted the newly published event as relevant-available even though
retrieval preceded publication. Selected identities/positions were correct. This
module recomputes availability and error labels from the frozen traces.
"""
from __future__ import annotations

import json
from pathlib import Path

from horus.live import SessionStore

from .analyze import condition_summary
from .harness import CONDITIONS, classify_error


PHASE_START = {"STABLE": 1, "CHANGE": 7, "RESTORATION": 17}
PHASE_VALUE = {"STABLE": 1, "CHANGE": -1, "RESTORATION": 1}


def corrected_row(event: dict, condition: str) -> dict:
    row = {**event["conditions"][condition], "phase": event["phase"]}
    start, number = PHASE_START[event["phase"]], event["event_number"]
    positions = row["retrieval"]["chronological_positions"]
    values = row["retrieval"]["selected_consequences"]
    row["relevant_available"] = max(0, number - start)
    row["relevant_selected"] = sum(start <= position < number for position in positions)
    row["stale_selected"] = sum(value != PHASE_VALUE[event["phase"]] for value in values)
    row["stale_available"] = sum(value != PHASE_VALUE[event["phase"]]
                                 for value in row["retrieval"]["candidate_consequences"])
    row["error_cause"] = (None if row["correct"] else classify_error(row,
        row["relevant_selected"], row["stale_selected"], row["relevant_available"]))
    return row


def analyze_completed_v2(output: Path) -> dict:
    with SessionStore(output / "protected-session", True) as store:
        scored = [row["record"] for row in store.records["training"]
                  if row["kind"] == "MEMORY_TRIAL_SCORED_EVENT"]
    rows = {name: [corrected_row(event, name) for event in scored]
            for name in CONDITIONS}
    summaries = {name: condition_summary(rows[name]) for name in CONDITIONS}
    before = json.loads((output / "before-restart.json").read_text())
    after = json.loads((output / "after-restart.json").read_text())
    result = dict(status="COMPLETE", event_count=len(scored), model_calls=48,
        reporting_recovery=("v2: duplicate-keyword repair plus prior-evidence "
                            "availability denominator; zero inference"),
        conditions=summaries,
        restart=dict(pre_restart=before["checkpoint"],
            restore_verification=after["restore_verification"],
            first_post_restart=after["first_post_restart"]),
        paired_differences=dict(
            accuracy=summaries["Z"]["consequence_accuracy"] -
                     summaries["M"]["consequence_accuracy"],
            adaptation_latency=None if None in (summaries["M"]["adaptation_latency"],
                summaries["Z"]["adaptation_latency"]) else
                summaries["Z"]["adaptation_latency"] - summaries["M"]["adaptation_latency"],
            restoration_latency=None if None in (summaries["M"]["restoration_latency"],
                summaries["Z"]["restoration_latency"]) else
                summaries["Z"]["restoration_latency"] - summaries["M"]["restoration_latency"],
            context_tokens=summaries["Z"]["context_tokens"]["total"] -
                           summaries["M"]["context_tokens"]["total"],
            measured_seconds=summaries["Z"]["total_measured_seconds"] -
                             summaries["M"]["total_measured_seconds"]))
    (output / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    from argparse import ArgumentParser
    p = ArgumentParser(); p.add_argument("--output", type=Path, required=True)
    print(json.dumps(analyze_completed_v2(p.parse_args().output), sort_keys=True))
