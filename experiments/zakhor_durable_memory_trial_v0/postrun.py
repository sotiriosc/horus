"""Zero-inference reporting recovery for the completed campaign.

The frozen analyzer passed event_number both explicitly and through the stored
condition record. This module changes only dictionary assembly; metric functions,
thresholds, evidence, and calls remain frozen.
"""
from __future__ import annotations

import json
from pathlib import Path

from horus.live import SessionStore

from .analyze import condition_summary
from .harness import CONDITIONS


def analyze_completed(output: Path) -> dict:
    with SessionStore(output / "protected-session", True) as store:
        scored = [row["record"] for row in store.records["training"]
                  if row["kind"] == "MEMORY_TRIAL_SCORED_EVENT"]
    rows = {name: [] for name in CONDITIONS}
    for event in scored:
        for name in CONDITIONS:
            rows[name].append({**event["conditions"][name], "phase": event["phase"]})
    summaries = {name: condition_summary(rows[name]) for name in CONDITIONS}
    before = json.loads((output / "before-restart.json").read_text())
    after = json.loads((output / "after-restart.json").read_text())
    result = dict(status="COMPLETE", event_count=len(scored), model_calls=48,
        reporting_recovery="duplicate event_number keyword only; zero inference",
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
    print(json.dumps(analyze_completed(p.parse_args().output), sort_keys=True))
