"""Telemetry middleware — zero-entropy / token-sink flags for inference logs."""

from __future__ import annotations

from typing import Any, Dict, List, Sequence

from .epistemic import FeelingReport


# Collapse / runaway_repetition requires BOTH (avoids false positives when a
# few peaky tokens appear inside an otherwise diverse sequence, e.g. Qwen
# mean_entropy≈2 with honest replies still getting flagged).
SINK_ENTROPY = 1.5
SINK_TOP1 = 0.8


def detect_token_sink(
    entropies: Sequence[float], top1s: Sequence[float]
) -> Dict[str, Any]:
    """Flag runaway repetition collapse only when entropy and top-1 agree.

    Trigger: mean entropy < 1.5 **and** mean top-1 > 0.8, with at least two
    supporting tokens that individually meet the same pair of thresholds.
    """
    sink_steps = 0
    for e, p in zip(entropies, top1s):
        if e < SINK_ENTROPY and p > SINK_TOP1:
            sink_steps += 1
    mean_e = sum(entropies) / len(entropies) if entropies else 0.0
    mean_p = sum(top1s) / len(top1s) if top1s else 0.0
    min_e = min(entropies) if entropies else 0.0
    detected = (
        bool(entropies)
        and mean_e < SINK_ENTROPY
        and mean_p > SINK_TOP1
        and sink_steps >= 2
    )
    return {
        "token_sink_detected": detected,
        "sink_steps": sink_steps,
        "min_entropy": float(min_e),
        "mean_entropy": float(mean_e),
        "mean_top1": float(mean_p),
        "flags": (
            ["TOKEN_SINK_DETECTED", "UNCONSTRAINED_SAMPLING"]
            if detected
            else []
        ),
    }


def enrich_feeling(
    feeling: FeelingReport, entropies: Sequence[float], top1s: Sequence[float]
) -> FeelingReport:
    sink = detect_token_sink(entropies, top1s)
    feeling.token_sink_detected = bool(sink["token_sink_detected"])
    feeling.min_entropy = float(sink["min_entropy"])
    # Sink is a failure of diversity, not "high confidence knowledge"
    if feeling.token_sink_detected:
        feeling.low_confidence = True
        feeling.note = (
            "feeling = logit telemetry; token_sink_detected "
            "(entropy<1.5 and top1>0.8 collapse — not knowing)"
        )
    return feeling


def sink_knowing_stance(flags: List[str], docstring_drift: bool = False) -> Dict[str, Any]:
    out_flags = list(flags)
    if docstring_drift:
        out_flags.append("DOCSTRING_DRIFT")
    stance = (
        "runaway_repetition_collapse"
        if "TOKEN_SINK_DETECTED" in out_flags
        else "claims_unchecked_external_verify"
    )
    return {
        "stance": stance,
        "flags": out_flags,
        "verified": False,
        "requires_external_evidence": True,
    }
