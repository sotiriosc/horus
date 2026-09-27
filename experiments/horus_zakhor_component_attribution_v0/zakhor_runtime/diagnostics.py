"""Training / living-memory diagnostic analysis.

Parses train logs, checkpoint ``keeper_train_meta.json``, and optional
``diagnostic_history.jsonl`` written by ``train.py``.

Tracks:
  - loss stability across steps/epochs
  - regime-change rates and guard-band (G) fluctuation per layer
  - stranger / clamp pressure (proxy for activation degradation vectors)
  - flags for unstable layers and overfitting / degradation zones
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Parsed records
# ---------------------------------------------------------------------------

_STEP_RE = re.compile(
    r"\[train\]\s+epoch\s+(?P<epoch>\d+)\s+step\s+(?P<step>\d+)/(?P<total>\d+)\s+"
    r"loss=(?P<loss>[-+eE0-9.]+)\s+lr=(?P<lr>[-+eE0-9.]+)\s+"
    r"mean_G=(?P<mean_G>[-+eE0-9.]+)\s+strangers=(?P<strangers>\d+)"
)
_EPOCH_RE = re.compile(
    r"\[train\]\s+epoch\s+(?P<epoch>\d+)\s+done\s+mean_loss=(?P<mean_loss>[-+eE0-9.]+)\s+"
    r"steps_this_epoch=(?P<steps>\d+)"
)
_DIAG_RE = re.compile(r"\[diag\]\s+(\{.*\})\s*$")


@dataclass
class StepRecord:
    epoch: int
    step: int
    total_steps: int
    loss: float
    lr: float
    mean_G: float
    strangers: int


@dataclass
class EpochRecord:
    epoch: int
    mean_loss: float
    steps: int
    layers: List[Dict[str, Any]] = field(default_factory=list)
    mean_G: Optional[float] = None
    total_strangers: Optional[int] = None
    total_regime_events: Optional[int] = None


@dataclass
class Flag:
    severity: str  # info | warn | critical
    code: str
    message: str
    layer: Optional[int] = None
    value: Optional[float] = None


@dataclass
class DiagnosticReport:
    source: str
    n_steps: int
    n_epochs: int
    loss_first: Optional[float]
    loss_last: Optional[float]
    loss_min: Optional[float]
    loss_max: Optional[float]
    loss_delta: Optional[float]
    loss_volatility: Optional[float]
    regime_change_rate: Optional[float]
    mean_G_volatility: Optional[float]
    stranger_rate_trend: Optional[float]
    unstable_layers: List[int]
    flags: List[Flag]
    epoch_summaries: List[Dict[str, Any]]
    layer_summaries: List[Dict[str, Any]]
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def parse_train_log(text: str) -> Tuple[List[StepRecord], List[EpochRecord]]:
    """Parse ``[train]`` / ``[diag]`` lines from a training log string."""
    steps: List[StepRecord] = []
    epochs: Dict[int, EpochRecord] = {}

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        m = _DIAG_RE.search(line)
        if m:
            try:
                obj = json.loads(m.group(1))
            except json.JSONDecodeError:
                continue
            ep = int(obj.get("epoch", 0))
            rec = epochs.get(ep) or EpochRecord(
                epoch=ep,
                mean_loss=float(obj.get("mean_loss", float("nan"))),
                steps=int(obj.get("steps", 0)),
            )
            rec.mean_loss = float(obj.get("mean_loss", rec.mean_loss))
            rec.steps = int(obj.get("steps", rec.steps))
            rec.layers = list(obj.get("layers") or [])
            rec.mean_G = obj.get("mean_G", rec.mean_G)
            rec.total_strangers = obj.get("total_strangers", rec.total_strangers)
            rec.total_regime_events = obj.get(
                "total_regime_events", rec.total_regime_events
            )
            epochs[ep] = rec
            continue

        m = _STEP_RE.search(line)
        if m:
            steps.append(
                StepRecord(
                    epoch=int(m.group("epoch")),
                    step=int(m.group("step")),
                    total_steps=int(m.group("total")),
                    loss=float(m.group("loss")),
                    lr=float(m.group("lr")),
                    mean_G=float(m.group("mean_G")),
                    strangers=int(m.group("strangers")),
                )
            )
            continue

        m = _EPOCH_RE.search(line)
        if m:
            ep = int(m.group("epoch"))
            rec = epochs.get(ep) or EpochRecord(
                epoch=ep,
                mean_loss=float(m.group("mean_loss")),
                steps=int(m.group("steps")),
            )
            rec.mean_loss = float(m.group("mean_loss"))
            rec.steps = int(m.group("steps"))
            epochs[ep] = rec

    return steps, [epochs[k] for k in sorted(epochs)]


def load_diagnostic_history(path: Path) -> List[EpochRecord]:
    """Load ``diagnostic_history.jsonl`` written by train.py."""
    out: List[EpochRecord] = []
    if not path.is_file():
        return out
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            out.append(
                EpochRecord(
                    epoch=int(obj.get("epoch", len(out) + 1)),
                    mean_loss=float(obj.get("mean_loss", float("nan"))),
                    steps=int(obj.get("steps", 0)),
                    layers=list(obj.get("layers") or []),
                    mean_G=obj.get("mean_G"),
                    total_strangers=obj.get("total_strangers"),
                    total_regime_events=obj.get("total_regime_events"),
                )
            )
    return out


def load_keeper_meta(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


# ---------------------------------------------------------------------------
# Stats helpers
# ---------------------------------------------------------------------------

def _finite(xs: Iterable[float]) -> List[float]:
    return [float(x) for x in xs if x is not None and math.isfinite(float(x))]


def _mean(xs: Sequence[float]) -> Optional[float]:
    vals = _finite(xs)
    return sum(vals) / len(vals) if vals else None


def _stdev(xs: Sequence[float]) -> Optional[float]:
    vals = _finite(xs)
    if len(vals) < 2:
        return 0.0 if len(vals) == 1 else None
    m = sum(vals) / len(vals)
    var = sum((x - m) ** 2 for x in vals) / (len(vals) - 1)
    return math.sqrt(var)


def _delta(xs: Sequence[float]) -> Optional[float]:
    vals = _finite(xs)
    if len(vals) < 2:
        return None
    return vals[-1] - vals[0]


def _slope(xs: Sequence[float]) -> Optional[float]:
    """Simple least-squares slope vs index."""
    vals = _finite(xs)
    n = len(vals)
    if n < 2:
        return None
    xm = (n - 1) / 2.0
    ym = sum(vals) / n
    num = sum((i - xm) * (y - ym) for i, y in enumerate(vals))
    den = sum((i - xm) ** 2 for i in range(n))
    return num / den if den else 0.0


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def analyze(
    steps: Sequence[StepRecord],
    epochs: Sequence[EpochRecord],
    meta: Optional[Dict[str, Any]] = None,
    source: str = "",
    *,
    loss_rise_warn: float = 0.15,
    loss_vol_warn: float = 0.35,
    regime_rate_warn: float = 0.05,
    g_vol_warn: float = 0.25,
    stranger_slope_warn: float = 50.0,
) -> DiagnosticReport:
    """Build a diagnostic report and flag instability / degradation zones."""
    meta = meta or {}
    flags: List[Flag] = []

    step_losses = [s.loss for s in steps]
    epoch_losses = [e.mean_loss for e in epochs if math.isfinite(e.mean_loss)]
    loss_series = epoch_losses if len(epoch_losses) >= 2 else step_losses

    loss_first = loss_series[0] if loss_series else None
    loss_last = loss_series[-1] if loss_series else None
    loss_min = min(loss_series) if loss_series else None
    loss_max = max(loss_series) if loss_series else None
    loss_delta = _delta(loss_series)
    loss_vol = _stdev(loss_series)

    if loss_delta is not None and loss_first and loss_first > 0:
        rel_rise = loss_delta / loss_first
        if rel_rise > loss_rise_warn:
            flags.append(
                Flag(
                    "warn",
                    "loss_late_rise",
                    f"Loss rose {rel_rise:.1%} end-to-end — possible overfitting "
                    f"or degradation zone (Δ={loss_delta:.4f}).",
                    value=rel_rise,
                )
            )
        elif loss_delta < -1e-6:
            flags.append(
                Flag(
                    "info",
                    "loss_improving",
                    f"Loss improved by {-loss_delta:.4f} across the series.",
                    value=loss_delta,
                )
            )

    loss_mean = _mean(loss_series)
    if loss_vol is not None and loss_mean is not None:
        rel_vol = loss_vol / max(loss_mean, 1e-6)
        if rel_vol > loss_vol_warn:
            flags.append(
                Flag(
                    "warn",
                    "loss_volatility",
                    f"High loss volatility (σ/mean={rel_vol:.2f}). "
                    "Training may be unstable.",
                    value=rel_vol,
                )
            )

    # Late-window rebound: last third mean vs best earlier mean
    if len(loss_series) >= 6:
        cut = max(1, len(loss_series) // 3)
        early_best = min(loss_series[:-cut])
        late_mean = _mean(loss_series[-cut:]) or 0.0
        if early_best > 0 and (late_mean - early_best) / early_best > loss_rise_warn:
            flags.append(
                Flag(
                    "critical",
                    "overfit_rebound",
                    f"Late-window mean loss {late_mean:.4f} rebounded above early "
                    f"best {early_best:.4f} — overfitting / degradation zone.",
                    value=late_mean - early_best,
                )
            )

    mean_G_series = [s.mean_G for s in steps] + [
        e.mean_G for e in epochs if e.mean_G is not None
    ]
    mean_G_vol = _stdev(mean_G_series)
    if mean_G_vol is not None and mean_G_vol > g_vol_warn:
        flags.append(
            Flag(
                "warn",
                "guard_band_fluctuation",
                f"mean_G fluctuates strongly (σ={mean_G_vol:.3f}) — switch/keeper "
                "thresholds are shifting aggressively.",
                value=mean_G_vol,
            )
        )

    stranger_series = [float(s.strangers) for s in steps]
    if not stranger_series:
        stranger_series = [
            float(e.total_strangers)
            for e in epochs
            if e.total_strangers is not None
        ]
    stranger_slope = _slope(stranger_series)
    if stranger_slope is not None and stranger_slope > stranger_slope_warn:
        flags.append(
            Flag(
                "warn",
                "stranger_pressure_rising",
                f"Stranger/clamp counts trending up (slope≈{stranger_slope:.1f}/step) "
                "— potential token/activation degradation vector.",
                value=stranger_slope,
            )
        )

    # Per-layer regime / G analysis from epoch layer snapshots
    layer_hist: Dict[int, Dict[str, List[float]]] = {}
    for e in epochs:
        for li, snap in enumerate(e.layers):
            lid = int(snap.get("layer", li))
            bucket = layer_hist.setdefault(
                lid, {"G": [], "regime": [], "strangers": [], "s": [], "confidence": []}
            )
            if snap.get("G") is not None:
                bucket["G"].append(float(snap["G"]))
            if snap.get("regime_events") is not None:
                bucket["regime"].append(float(snap["regime_events"]))
            if snap.get("stranger_elems") is not None:
                bucket["strangers"].append(float(snap["stranger_elems"]))
            if snap.get("s") is not None and snap["s"] == snap["s"]:
                bucket["s"].append(float(snap["s"]))
            if snap.get("mean_confidence") is not None:
                bucket["confidence"].append(float(snap["mean_confidence"]))

    layer_summaries: List[Dict[str, Any]] = []
    unstable_layers: List[int] = []
    regime_rates: List[float] = []

    for lid in sorted(layer_hist):
        b = layer_hist[lid]
        g_vol = _stdev(b["G"]) or 0.0
        # regime change rate ≈ Δregime_events / epoch (last-first)/n
        regime_delta = _delta(b["regime"])
        n_ep = max(len(b["regime"]), 1)
        regime_rate = (regime_delta / n_ep) if regime_delta is not None else 0.0
        if regime_rate is not None:
            regime_rates.append(float(regime_rate))
        s_vol = _stdev(b["s"]) or 0.0
        stranger_slope_l = _slope(b["strangers"])
        conf_mean = _mean(b["confidence"])

        summary = {
            "layer": lid,
            "G_volatility": g_vol,
            "scale_s_volatility": s_vol,
            "regime_change_rate": regime_rate,
            "stranger_slope": stranger_slope_l,
            "mean_confidence": conf_mean,
            "n_epochs_observed": max(len(b["G"]), len(b["regime"])),
        }
        layer_summaries.append(summary)

        unstable = False
        if g_vol > g_vol_warn:
            unstable = True
            flags.append(
                Flag(
                    "warn",
                    "layer_G_unstable",
                    f"Layer {lid}: guard band G unstable (σ={g_vol:.3f}).",
                    layer=lid,
                    value=g_vol,
                )
            )
        if regime_rate is not None and regime_rate > regime_rate_warn:
            unstable = True
            flags.append(
                Flag(
                    "warn",
                    "layer_regime_churn",
                    f"Layer {lid}: high regime-change rate "
                    f"({regime_rate:.3f} events/epoch).",
                    layer=lid,
                    value=regime_rate,
                )
            )
        if s_vol > 1.0:
            unstable = True
            flags.append(
                Flag(
                    "warn",
                    "layer_scale_drift",
                    f"Layer {lid}: living scale s fluctuates (σ={s_vol:.3f}) — "
                    "switch dynamics may be thrashing.",
                    layer=lid,
                    value=s_vol,
                )
            )
        if stranger_slope_l is not None and stranger_slope_l > stranger_slope_warn:
            unstable = True
            flags.append(
                Flag(
                    "critical",
                    "layer_degradation_vector",
                    f"Layer {lid}: rising stranger pressure "
                    f"(slope≈{stranger_slope_l:.1f}) — token/activation "
                    "degradation vector candidate.",
                    layer=lid,
                    value=stranger_slope_l,
                )
            )
        if conf_mean is not None and conf_mean < 0.45:
            flags.append(
                Flag(
                    "info",
                    "layer_low_confidence",
                    f"Layer {lid}: low mean simulate-confidence ({conf_mean:.2f}).",
                    layer=lid,
                    value=conf_mean,
                )
            )
        if unstable:
            unstable_layers.append(lid)

    overall_regime_rate = _mean(regime_rates)

    # Meta sanity
    if meta.get("ceiling_scale") is not None and float(meta["ceiling_scale"]) < 0.5:
        flags.append(
            Flag(
                "info",
                "tight_ceiling",
                f"Checkpoint ceiling_scale={meta['ceiling_scale']} is tight — "
                "expect more stranger clamps.",
                value=float(meta["ceiling_scale"]),
            )
        )

    if not steps and not epochs and not meta:
        flags.append(
            Flag(
                "critical",
                "no_data",
                "No parseable train steps, epoch records, or checkpoint meta found.",
            )
        )
    elif not steps and not epochs and meta:
        flags.append(
            Flag(
                "info",
                "meta_only",
                "Only checkpoint metadata available — re-run training with "
                "diagnostic logging for epoch/layer trends.",
            )
        )

    epoch_summaries = [
        {
            "epoch": e.epoch,
            "mean_loss": e.mean_loss,
            "steps": e.steps,
            "mean_G": e.mean_G,
            "total_strangers": e.total_strangers,
            "total_regime_events": e.total_regime_events,
            "n_layers": len(e.layers),
        }
        for e in epochs
    ]

    return DiagnosticReport(
        source=source,
        n_steps=len(steps),
        n_epochs=len(epochs),
        loss_first=loss_first,
        loss_last=loss_last,
        loss_min=loss_min,
        loss_max=loss_max,
        loss_delta=loss_delta,
        loss_volatility=loss_vol,
        regime_change_rate=overall_regime_rate,
        mean_G_volatility=mean_G_vol,
        stranger_rate_trend=stranger_slope,
        unstable_layers=unstable_layers,
        flags=flags,
        epoch_summaries=epoch_summaries,
        layer_summaries=layer_summaries,
        meta=meta,
    )


def format_report(report: DiagnosticReport) -> str:
    """Human-readable diagnostic summary."""
    lines: List[str] = []
    lines.append("=" * 64)
    lines.append("Living Memory — Training Diagnostic Report")
    lines.append("=" * 64)
    lines.append(f"Source: {report.source or '(none)'}")
    lines.append(f"Parsed steps: {report.n_steps}   epochs: {report.n_epochs}")
    if report.meta:
        keys = (
            "base_model",
            "policy",
            "steps",
            "lr",
            "ceiling_scale",
            "g_floor",
            "data",
        )
        bits = [f"{k}={report.meta[k]}" for k in keys if k in report.meta]
        if bits:
            lines.append("Meta: " + ", ".join(bits))

    lines.append("")
    lines.append("--- Loss stability ---")
    lines.append(
        f"first={_fmt(report.loss_first)}  last={_fmt(report.loss_last)}  "
        f"min={_fmt(report.loss_min)}  max={_fmt(report.loss_max)}"
    )
    lines.append(
        f"Δ={_fmt(report.loss_delta)}  volatility(σ)={_fmt(report.loss_volatility)}"
    )

    lines.append("")
    lines.append("--- Switch / regime dynamics ---")
    lines.append(
        f"mean regime-change rate={_fmt(report.regime_change_rate)} events/epoch"
    )
    lines.append(f"mean_G volatility={_fmt(report.mean_G_volatility)}")
    lines.append(f"stranger trend (slope)={_fmt(report.stranger_rate_trend)}")

    if report.unstable_layers:
        lines.append(
            f"Unstable layers: {', '.join(str(i) for i in report.unstable_layers)}"
        )
    else:
        lines.append("Unstable layers: (none flagged)")

    if report.layer_summaries:
        lines.append("")
        lines.append("--- Per-layer summary ---")
        lines.append(
            f"{'L':>3}  {'Gσ':>8}  {'sσ':>8}  {'regime/ep':>10}  "
            f"{'strangerΔ':>10}  {'conf':>6}"
        )
        for ls in report.layer_summaries:
            lines.append(
                f"{ls['layer']:3d}  {_fmt(ls.get('G_volatility'), 8)}  "
                f"{_fmt(ls.get('scale_s_volatility'), 8)}  "
                f"{_fmt(ls.get('regime_change_rate'), 10)}  "
                f"{_fmt(ls.get('stranger_slope'), 10)}  "
                f"{_fmt(ls.get('mean_confidence'), 6)}"
            )

    if report.epoch_summaries:
        lines.append("")
        lines.append("--- Epoch trend ---")
        for es in report.epoch_summaries[-20:]:
            lines.append(
                f"epoch {es['epoch']:>3}: mean_loss={_fmt(es['mean_loss'])}  "
                f"G={_fmt(es.get('mean_G'))}  strangers={es.get('total_strangers')}  "
                f"regimes={es.get('total_regime_events')}"
            )

    lines.append("")
    lines.append("--- Flags ---")
    if not report.flags:
        lines.append("(none)")
    else:
        for fl in sorted(report.flags, key=lambda f: _sev_rank(f.severity)):
            loc = f" [L{fl.layer}]" if fl.layer is not None else ""
            lines.append(f"[{fl.severity.upper()}] {fl.code}{loc}: {fl.message}")

    lines.append("=" * 64)
    return "\n".join(lines)


def _fmt(x: Optional[float], width: int = 0) -> str:
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        s = "n/a"
    else:
        s = f"{x:.4f}"
    return f"{s:>{width}}" if width else s


def _sev_rank(sev: str) -> int:
    return {"critical": 0, "warn": 1, "info": 2}.get(sev, 9)


def collect_from_paths(
    log_paths: Sequence[Path],
    checkpoint: Optional[Path] = None,
) -> Tuple[List[StepRecord], List[EpochRecord], Dict[str, Any], str]:
    """Merge logs + optional checkpoint history/meta."""
    steps: List[StepRecord] = []
    epochs: List[EpochRecord] = []
    sources: List[str] = []
    meta: Dict[str, Any] = {}

    for lp in log_paths:
        if not lp.is_file():
            continue
        s, e = parse_train_log(lp.read_text(encoding="utf-8", errors="ignore"))
        steps.extend(s)
        epochs.extend(e)
        sources.append(str(lp))

    if checkpoint is not None:
        ck = Path(checkpoint)
        if ck.is_file() and ck.name.endswith(".json"):
            # treat as meta file; parent is checkpoint dir
            meta.update(load_keeper_meta(ck))
            hist = load_diagnostic_history(ck.parent / "diagnostic_history.jsonl")
            if hist:
                epochs.extend(hist)
            sources.append(str(ck))
        elif ck.is_dir():
            meta.update(load_keeper_meta(ck / "keeper_train_meta.json"))
            hist = load_diagnostic_history(ck / "diagnostic_history.jsonl")
            if hist:
                epochs.extend(hist)
            # also swallow any *.log / run_log* inside
            for pattern in ("*.log", "run_log*.txt", "train*.txt"):
                for lp in sorted(ck.glob(pattern)):
                    s, e = parse_train_log(
                        lp.read_text(encoding="utf-8", errors="ignore")
                    )
                    steps.extend(s)
                    epochs.extend(e)
                    sources.append(str(lp))
            sources.append(str(ck))

    # Deduplicate epochs by epoch id (prefer richer layer payloads)
    by_ep: Dict[int, EpochRecord] = {}
    for e in epochs:
        prev = by_ep.get(e.epoch)
        if prev is None or (len(e.layers) > len(prev.layers)):
            by_ep[e.epoch] = e
    epochs_sorted = [by_ep[k] for k in sorted(by_ep)]

    return steps, epochs_sorted, meta, " + ".join(sources) if sources else ""


def layer_snapshots_payload(snaps: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Normalize controller.tracker_snapshots() for diagnostic JSON."""
    out: List[Dict[str, Any]] = []
    for i, s in enumerate(snaps):
        out.append(
            {
                "layer": i,
                "s": s.get("s"),
                "G": s.get("G"),
                "ceiling": s.get("ceiling"),
                "regime_events": s.get("regime_events", 0),
                "stranger_elems": s.get("stranger_elems", 0),
                "stable_blocks": s.get("stable_blocks", 0),
                "unstable_blocks": s.get("unstable_blocks", 0),
                "mean_confidence": s.get("mean_confidence"),
            }
        )
    return out
