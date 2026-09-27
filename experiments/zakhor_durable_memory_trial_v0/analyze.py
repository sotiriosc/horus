from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from statistics import mean

from horus.live import SessionStore

from .harness import CONDITIONS


def accuracy(rows: list[dict]) -> float:
    return sum(bool(row["correct"]) for row in rows) / len(rows)


def window(rows: list[dict]) -> dict:
    selected = sum(len(row["retrieval"]["selected_memory_identities"]) for row in rows)
    return dict(events=len(rows), accuracy=accuracy(rows),
        invalid=sum(row["prediction"] is None for row in rows),
        relevant_retrieval_rate=(sum(row["relevant_selected"] for row in rows) /
            sum(min(row["relevant_available"], 6) for row in rows)
            if sum(min(row["relevant_available"], 6) for row in rows) else None),
        stale_selection_rate=(sum(row["stale_selected"] for row in rows) / selected
                              if selected else 0.0),
        mean_context_tokens=mean(row["context_tokens"] for row in rows))


def first_correct(rows: list[dict], phase: str) -> int | None:
    candidates = [row for row in rows if row["phase"] == phase]
    return next((offset for offset, row in enumerate(candidates) if row["correct"]), None)


def condition_summary(rows: list[dict]) -> dict:
    rolling = [(i + 1, window(rows[i:i + 6])) for i in range(len(rows) - 5)]
    worst = min(rolling, key=lambda item: item[1]["accuracy"])
    contradiction_opportunities = [row for row in rows
        if row["retrieval"]["contradictions_in_candidates"]]
    selected = sum(len(row["retrieval"]["selected_memory_identities"]) for row in rows)
    relevant_denom = sum(min(row["relevant_available"], 6) for row in rows)
    return dict(events=len(rows), correct=sum(row["correct"] for row in rows),
        consequence_accuracy=accuracy(rows), invalid_outputs=sum(
            row["prediction"] is None for row in rows),
        adaptation_latency=first_correct(rows, "CHANGE"),
        restoration_latency=first_correct(rows, "RESTORATION"),
        false_persistence_old_regime=sum(row["phase"] == "CHANGE" and
            row["prediction"] == 1 and not row["correct"] for row in rows),
        false_persistence_changed_regime=sum(row["phase"] == "RESTORATION" and
            row["prediction"] == -1 and not row["correct"] for row in rows),
        contradiction_opportunities=len(contradiction_opportunities),
        contradictions_preserved=sum(row["retrieval"]["contradictions_included"]
                                     for row in contradiction_opportunities),
        contradiction_preservation_rate=(sum(row["retrieval"][
            "contradictions_included"] for row in contradiction_opportunities) /
            len(contradiction_opportunities) if contradiction_opportunities else None),
        relevant_history_retrieval_rate=(sum(row["relevant_selected"] for row in rows) /
            relevant_denom if relevant_denom else None),
        stale_history_retrieval_rate=(sum(row["stale_selected"] for row in rows) /
            selected if selected else 0.0),
        context_tokens=dict(total=sum(row["context_tokens"] for row in rows),
            mean=mean(row["context_tokens"] for row in rows),
            maximum=max(row["context_tokens"] for row in rows)),
        retrieval_seconds=dict(total=sum(row["retrieval_seconds"] for row in rows),
            mean=mean(row["retrieval_seconds"] for row in rows),
            maximum=max(row["retrieval_seconds"] for row in rows)),
        model_seconds=dict(total=sum(row["model_seconds"] for row in rows),
            mean=mean(row["model_seconds"] for row in rows),
            maximum=max(row["model_seconds"] for row in rows)),
        total_measured_seconds=sum(row["retrieval_seconds"] + row["model_seconds"]
                                   for row in rows),
        error_causes=dict(Counter(row["error_cause"] for row in rows if not row["correct"])),
        windows=dict(early=window(rows[:8]), middle=window(rows[8:16]),
            late=window(rows[16:24]),
            worst_rolling=dict(starts_at=worst[0], **worst[1])),
        retrieval_questions=dict(
            recent_event_available=sum(bool(row["retrieval"][
                "candidate_memory_count"]) for row in rows),
            most_recent_event_retrieved=sum((not row["retrieval"][
                "chronological_positions"] or max(row["retrieval"][
                    "chronological_positions"]) == row["retrieval"][
                    "candidate_memory_count"]) for row in rows),
            contradictions_visible=sum(row["retrieval"]["contradictions_included"]
                                       for row in rows),
            relevant_current_phase_visible=sum(row["relevant_selected"] > 0 for row in rows)))


def analyze(output: Path) -> dict:
    with SessionStore(output / "protected-session", True) as store:
        scored = [row["record"] for row in store.records["training"]
                  if row["kind"] == "MEMORY_TRIAL_SCORED_EVENT"]
    rows = {name: [] for name in CONDITIONS}
    for event in scored:
        for name in CONDITIONS:
            rows[name].append(dict(phase=event["phase"], event_number=event["event_number"],
                                   **event["conditions"][name]))
    summaries = {name: condition_summary(rows[name]) for name in CONDITIONS}
    before = json.loads((output / "before-restart.json").read_text())
    after = json.loads((output / "after-restart.json").read_text())
    result = dict(status="COMPLETE", event_count=len(scored), model_calls=48,
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

