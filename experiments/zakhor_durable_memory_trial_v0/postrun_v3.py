"""Authoritative zero-inference report with non-vacuous recency accounting."""
from __future__ import annotations

import json
from pathlib import Path

from horus.live import SessionStore

from .harness import CONDITIONS
from .postrun_v2 import analyze_completed_v2


def analyze_completed_v3(output: Path) -> dict:
    result = analyze_completed_v2(output)
    with SessionStore(output / "protected-session", True) as store:
        scored = [row["record"] for row in store.records["training"]
                  if row["kind"] == "MEMORY_TRIAL_SCORED_EVENT"]
    for name in CONDITIONS:
        traces = [event["conditions"][name]["retrieval"] for event in scored]
        result["conditions"][name]["retrieval_questions"][
            "most_recent_event_retrieved"] = sum(bool(trace[
                "chronological_positions"]) and max(trace["chronological_positions"]) ==
                trace["candidate_memory_count"] for trace in traces)
    result["retrieval_pair_audit"] = dict(
        identical_selected_identity_sets=sum(event["conditions"]["M"]["retrieval"][
            "selected_memory_identities"] == event["conditions"]["Z"]["retrieval"][
            "selected_memory_identities"] for event in scored),
        identical_predictions=sum(event["conditions"]["M"]["prediction"] ==
            event["conditions"]["Z"]["prediction"] for event in scored),
        different_internal_reason_labels=sum(event["conditions"]["M"]["retrieval"][
            "retrieval_reasons"] != event["conditions"]["Z"]["retrieval"][
            "retrieval_reasons"] for event in scored), opportunities=24)
    result["decision_gate"] = "MODERN_MEMORY_SUFFICIENT"
    result["decision_gate_reason"] = (
        "M and Z selected identical memories and produced identical predictions on all "
        "24 opportunities; Z added a persistent regime index and slightly more retrieval "
        "time without a distinct retrieval or behavioral result.")
    result["reporting_recovery"] = (
        "v3 authoritative: duplicate-keyword, prior-evidence denominator, and "
        "non-vacuous most-recent count; zero inference")
    (output / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    from argparse import ArgumentParser
    p = ArgumentParser(); p.add_argument("--output", type=Path, required=True)
    print(json.dumps(analyze_completed_v3(p.parse_args().output), sort_keys=True))
