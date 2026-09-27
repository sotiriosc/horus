"""Epistemic manifesto — feeling ≠ knowing; prediction ≠ fact.

Five directives:
  1. Feeling (logits/entropy) is logged separately from Knowing (claims)
  2. Layer flow A→B→C→D→E→F — one relational transform per step
  3. Strict ≠ boundaries — flag when text asserts fact/cause without warrant
  4. Direct state observation — prefer tracker hooks over text feedback loops
  5. Ban truth-by-repetition — structural metrics, not phrase loops
"""

from __future__ import annotations

import math
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Sequence


# --- 1. Feeling (model) vs Knowing (system) ---------------------------------

@dataclass
class FeelingReport:
    """Raw sampling state — honesty about uncertainty, not authority."""

    mean_entropy: float = 0.0
    mean_top1_prob: float = 0.0
    min_top1_prob: float = 1.0
    min_entropy: float = 0.0
    max_entropy: float = 0.0
    n_tokens: int = 0
    low_confidence: bool = False
    token_sink_detected: bool = False
    note: str = (
        "feeling = logit distribution telemetry; not a claim about the world"
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BeliefReport:
    """What the model *predicts* and how strongly — not yet knowing."""

    prediction_strength: float = 0.0
    alternative_hypotheses: int = 0
    mean_entropy: float = 0.0
    note: str = (
        "belief = prediction strength from logits; prediction ≠ truth"
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class KnowingReport:
    """System stance — what is asserted vs what remains unknown."""

    text_is_not_ground_truth: bool = True
    claims_flagged: List[str] = field(default_factory=list)
    prediction_asserted_as_fact: bool = False
    causal_asserted_without_mechanism: bool = False
    invented_authority: bool = False
    repetition_loop_suspected: bool = False
    token_sink_detected: bool = False
    verified: bool = False
    requires_external_evidence: bool = True
    honest_stance: str = "insufficient_evidence"
    note: str = (
        "knowing requires external verification; generated text ≠ fact"
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def belief_from_feeling(feeling: FeelingReport) -> BeliefReport:
    """Map feeling → belief: strength of prediction, not verified knowledge."""
    # Rough effective support count from entropy (higher entropy → more alts)
    if feeling.mean_entropy <= 0.05:
        alts = 1
    else:
        alts = max(1, min(32, int(round(math.exp(feeling.mean_entropy)))))
    return BeliefReport(
        prediction_strength=float(feeling.mean_top1_prob),
        alternative_hypotheses=alts,
        mean_entropy=float(feeling.mean_entropy),
    )


# --- 3. Strict ≠ boundaries ------------------------------------------------

_CAUSAL_AS_FACT = re.compile(
    r"\b(proves?|proven|definitely causes?|always causes?|"
    r"the (only )?cause is|therefore it is (a )?fact|"
    r"this (is|means) (because|why) .{0,40} (always|never))\b",
    re.I,
)
_PREDICTION_AS_REALITY = re.compile(
    r"\b(will (definitely|certainly|always)|guaranteed to|"
    r"prediction (is|=) (reality|fact)|future is certain)\b",
    re.I,
)
_INVENTED_AUTHORITY = re.compile(
    r"(https?://|www\.[a-z0-9.-]+\.[a-z]{2,}|"
    r"\bcitation\.org\b|\bdoi:\s*\d|"
    r"according to (a )?(study|paper) that does not|"
    r"see proof online)\b",
    re.I,
)
_FICTION_AS_SCIENCE = re.compile(
    r"\b(fantasy is (science|fact)|fiction (equals|is) (truth|reality)|"
    r"vibes (prove|confirm))\b",
    re.I,
)


def validate_epistemic(text: str, feeling: Optional[FeelingReport] = None) -> KnowingReport:
    """Flag outputs that blur ≠ boundaries. Does not rewrite the text."""
    claims: List[str] = []
    report = KnowingReport()

    if _CAUSAL_AS_FACT.search(text):
        report.causal_asserted_without_mechanism = True
        claims.append("explanation/description ≠ causal mechanism (flagged causal-as-fact phrasing)")
    if _PREDICTION_AS_REALITY.search(text):
        report.prediction_asserted_as_fact = True
        claims.append("prediction ≠ reality")
    if _INVENTED_AUTHORITY.search(text):
        report.invented_authority = True
        claims.append("do not invent authority stamps / URLs from story pressure")
    if _FICTION_AS_SCIENCE.search(text):
        claims.append("fantasy/fiction ≠ science/fact")

    # Low feeling confidence + authoritative tone
    if feeling is not None and feeling.low_confidence:
        if re.search(r"\b(certainly|definitely|always|never|proven)\b", text, re.I):
            claims.append("feeling(low confidence) ≠ knowing(forced certainty in text)")

    if feeling is not None and feeling.token_sink_detected:
        report.token_sink_detected = True
        report.repetition_loop_suspected = True
        claims.append("TOKEN_SINK_DETECTED | token_entropy≈0  repetition≠meaning")
        report.honest_stance = "runaway_repetition_collapse"

    report.claims_flagged = claims
    if report.honest_stance == "runaway_repetition_collapse":
        pass
    elif (
        report.causal_asserted_without_mechanism
        or report.prediction_asserted_as_fact
        or report.invented_authority
        or feeling is not None
        and feeling.low_confidence
    ):
        report.honest_stance = "uncertain_or_flagged"
    elif not claims:
        report.honest_stance = "claims_unchecked_external_verify"
    return report


# --- 2 + 4. Layer flow + direct observation --------------------------------
# Conceptual stack: FEELING → BELIEF → KNOWING (prediction ≠ truth)

STAGE_ORDER = ("A", "B", "C", "D", "E", "F")
STAGE_NAMES = {
    "A": "observe",       # prompt + direct tracker snapshot
    "B": "feel",          # logit entropy / top-1 (feeling)
    "C": "believe",       # prediction strength / alternatives (belief)
    "D": "form",          # token text forming
    "E": "know",          # ≠ filter + knowing stance
    "F": "render",        # graphics / structured display payload
}


@dataclass
class LayerFlow:
    """Strict sequential transforms — one relation per stage, no skips."""

    stages: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def set(self, stage: str, payload: Dict[str, Any]) -> None:
        if stage not in STAGE_ORDER:
            raise ValueError(f"unknown stage {stage!r}")
        # Enforce order: prior stages must exist
        idx = STAGE_ORDER.index(stage)
        for prev in STAGE_ORDER[:idx]:
            if prev not in self.stages:
                raise RuntimeError(
                    f"layer flow skip: {stage} before {prev} "
                    f"({STAGE_NAMES[prev]})"
                )
        self.stages[stage] = {
            "name": STAGE_NAMES[stage],
            "relation": f"{STAGE_ORDER[idx - 1] if idx else '∅'}→{stage}",
            **payload,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "order": list(STAGE_ORDER),
            "names": dict(STAGE_NAMES),
            "stages": self.stages,
            "note": "each step = one relational transform across layers; no blend/skip",
        }


def observe_controller(controller) -> Dict[str, Any]:
    """Direct state observation via living-memory trackers (not text feedback)."""
    if controller is None:
        return {"available": False, "layers": []}
    try:
        snaps = controller.tracker_snapshots()
    except Exception as e:  # noqa: BLE001
        return {"available": False, "error": f"{type(e).__name__}: {e}", "layers": []}
    layers = []
    for i, s in enumerate(snaps):
        layers.append(
            {
                "layer": i,
                "s": s.get("s"),
                "G": s.get("G"),
                "ceiling": s.get("ceiling"),
                "stranger_elems": s.get("stranger_elems"),
                "regime_events": s.get("regime_events"),
            }
        )
    return {
        "available": True,
        "n_layers": len(layers),
        "layers": layers,
        "source": "register_forward_hook / LivingMemoryTracker (direct)",
    }


def render_graphics(
    flow: LayerFlow,
    feeling: FeelingReport,
    belief: BeliefReport,
    knowing: KnowingReport,
) -> Dict[str, Any]:
    """Stage F — structured visual payload (not decorative fluff)."""
    bar = lambda x, w=20: "█" * int(max(0, min(1, x)) * w) + "░" * (
        w - int(max(0, min(1, x)) * w)
    )
    ent_norm = min(1.0, feeling.mean_entropy / 8.0) if feeling.n_tokens else 0.0
    conf = feeling.mean_top1_prob
    sink_note = " (token_sink_detected)" if feeling.token_sink_detected else ""
    ascii_panel = (
        f"feeling.entropy  [{bar(ent_norm)}] {feeling.mean_entropy:.3f}{sink_note}\n"
        f"feeling.top1     [{bar(conf)}] {feeling.mean_top1_prob:.3f}\n"
        f"belief.strength  [{bar(belief.prediction_strength)}] "
        f"{belief.prediction_strength:.3f}  alts={belief.alternative_hypotheses}\n"
        f"knowing.stance   {knowing.honest_stance}\n"
        f"knowing.verified {knowing.verified}  "
        f"requires_external_evidence={knowing.requires_external_evidence}\n"
        f"flags            {len(knowing.claims_flagged)}\n"
        f"≠                feeling≠belief≠knowing  "
        f"prediction≠truth  token_entropy=0≠meaning"
    )
    return {
        "ascii": ascii_panel,
        "feeling_low": feeling.low_confidence,
        "token_sink_detected": feeling.token_sink_detected,
        "flags": list(knowing.claims_flagged),
        "pipeline": "FEELING→BELIEF→KNOWING | "
        + "→".join(f"{s}:{STAGE_NAMES[s]}" for s in STAGE_ORDER),
    }


def run_epistemic_pipeline(
    *,
    prompt: str,
    text: str,
    feeling: FeelingReport,
    controller=None,
    completion: str = "",
    docstring_drift: bool = False,
) -> Dict[str, Any]:
    """A→F sequential epistemic pipeline. Returns full telemetry bundle."""
    belief = belief_from_feeling(feeling)

    flow = LayerFlow()
    flow.set(
        "A",
        {
            "prompt_chars": len(prompt),
            "direct_observation": observe_controller(controller),
        },
    )
    flow.set("B", {"feeling": feeling.to_dict()})
    flow.set("C", {"belief": belief.to_dict()})
    flow.set(
        "D",
        {
            "text_chars": len(text),
            "completion_chars": len(completion),
            "text_is_forming_only": True,
        },
    )
    knowing = validate_epistemic(completion or text, feeling)
    words = re.findall(r"[A-Za-z']+", completion or text)
    if len(words) >= 20:
        uniq = len(set(w.lower() for w in words))
        if uniq / len(words) < 0.35:
            knowing.repetition_loop_suspected = True
            knowing.claims_flagged.append(
                "truth-by-repetition banned — low type/token diversity"
            )
            if knowing.honest_stance != "runaway_repetition_collapse":
                knowing.honest_stance = "uncertain_or_flagged"
    if docstring_drift:
        knowing.claims_flagged.append("DOCSTRING_DRIFT | unconstrained template attractor")
        if knowing.honest_stance != "runaway_repetition_collapse":
            knowing.honest_stance = "uncertain_or_flagged"
    flow.set(
        "E",
        {
            "boundaries": [
                "feeling ≠ belief ≠ knowing",
                "prediction ≠ truth",
                "explanation ≠ causal mechanism",
                "text ≠ ground truth",
            ],
            "knowing": knowing.to_dict(),
        },
    )
    graphics = render_graphics(flow, feeling, belief, knowing)
    flow.set("F", {"graphics": graphics})

    return {
        "feeling": feeling.to_dict(),
        "belief": belief.to_dict(),
        "knowing": knowing.to_dict(),
        "layer_flow": flow.to_dict(),
        "graphics": graphics,
        "manifesto": {
            "stack": "FEELING → BELIEF → KNOWING",
            "feeling": "logits/entropy (not authority)",
            "belief": "prediction_strength + alternatives (not verified)",
            "knowing": "verified=False unless external evidence",
            "anti_sink": "dynamic temp/penalty + ngram ban + abort",
        },
    }


def feeling_from_token_stats(entropies: Sequence[float], top1s: Sequence[float]) -> FeelingReport:
    from living_memory.telemetry import enrich_feeling

    if not entropies:
        return FeelingReport()
    mean_e = sum(entropies) / len(entropies)
    mean_p = sum(top1s) / len(top1s) if top1s else 0.0
    min_p = min(top1s) if top1s else 0.0
    max_e = max(entropies)
    min_e = min(entropies)
    low = mean_p < 0.25 or mean_e > 5.0
    feeling = FeelingReport(
        mean_entropy=float(mean_e),
        mean_top1_prob=float(mean_p),
        min_top1_prob=float(min_p),
        min_entropy=float(min_e),
        max_entropy=float(max_e),
        n_tokens=len(entropies),
        low_confidence=low,
    )
    return enrich_feeling(feeling, entropies, top1s)


def token_feeling(probs) -> tuple:
    """Return (entropy, top1_prob) from a 1-D probability vector (torch or list)."""
    import torch

    if not isinstance(probs, torch.Tensor):
        # list/tuple fallback
        ps = [float(p) for p in probs if float(p) > 0.0]
        if not ps:
            return 0.0, 0.0
        ent = -sum(p * math.log(p + 1e-12) for p in ps)
        return float(ent), float(max(ps))
    p = probs.detach().float().clamp(min=0)
    s = p.sum()
    if not torch.isfinite(s) or float(s.item()) <= 0:
        return 0.0, 0.0
    p = p / s
    # entropy in nats
    ent = float(-(p * (p + 1e-12).log()).sum().item())
    top1 = float(p.max().item())
    return ent, top1
