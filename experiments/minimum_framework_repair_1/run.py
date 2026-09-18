"""Run the frozen audit with explicit repair-interface adapters and direct checks."""

from __future__ import annotations

import argparse
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

from experiments.minimum_framework_audit import run as frozen


class Driver(frozen.Driver):
    def begin(self, action=None, old_prediction=None):
        if old_prediction is None:
            return super().begin(action)
        # Same stale pre-outcome model output, now injected before the latch.
        with patch.object(self.system.map, "predict", lambda *args: old_prediction):
            return super().begin(action)

    def audit_after(self, pending, evidence, committed):
        reference = self.pending_reference
        if reference is not None:
            # F9 concerns the prediction USED for scoring. An exposed reference
            # may now change harmlessly; retain the original truth comparison.
            self.row["observations"]["exposed_prediction_replaced"] = (
                asdict(reference.prediction) != self.prediction
            )
            self.pending_reference = replace(
                reference, prediction=self.system.inner._prediction_at_begin
            )
        try:
            super().audit_after(pending, evidence, committed)
        finally:
            self.pending_reference = reference


_original_ablation = frozen.ablation_case


def ablation_case(row, name, weakened):
    if name != "early_continuation" or not weakened:
        return _original_ablation(row, name, weakened)
    d = Driver(row)
    row["_driver"] = d
    s = d.system

    def unchecked_receipt(port, receipt, **kwargs):
        # Explicitly remove precisely v2's mandatory-package ingress invariant.
        # All inner pair/state/Measure/Recovery checks remain active.
        s.inner._requires_package = False
        return s.inner.submit_receipt(port, receipt, **kwargs)

    with patch.object(s, "submit_receipt", unchecked_receipt):
        d.step(("c_bad", "c_bad"), legacy=True)
    row["observations"]["adapter"] = "test-local removal of mandatory package ingress"
    return d


def execute():
    with patch.object(frozen, "Driver", Driver), patch.object(frozen, "ablation_case", ablation_case):
        result = frozen.execute()
    result["baseline_commit"] = "412de7bb02a4cedfab5d648debffe54b8b5a94bb"
    from experiments.minimum_framework_repair_1.checks import run_checks
    result["direct_checks"] = run_checks()
    result["counts"]["protected_passes"] = sum(
        r["category"] == "protected" and r["outcome"] == "PASS" for r in result["rows"]
    )
    if result["direct_checks"]["failed"]:
        result["recommendation"] = "B"
        result["protected_status"] = "FAIL"
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    output = args.output or Path(tempfile.mkdtemp(prefix="horus-repair-1-"))
    if output.resolve().is_relative_to(root):
        raise ValueError("raw evidence must be outside the source tree")
    if args.output:
        output.mkdir(parents=True, exist_ok=False)
    result = execute()
    paths = [p for version in ("base_framework_v0", "base_framework_v1", "base_framework_v2",
                                "minimum_framework_audit", "minimum_framework_repair_1")
             for p in (root / "experiments" / version).glob("*.py")]
    paths += [root / "research" / name for name in (
        "minimum-framework-completion-definition.md", "minimum-framework-stress-preregistration.md",
        "minimum-framework-repair-1-preregistration.md")]
    result["source_sha256"] = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in sorted(paths)}
    (output / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    (output / "compact.json").write_text(json.dumps(frozen.compact(result), indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("recommendation", "protected_status", "counts")}, indent=2))
    print(f"Evidence: {output}")
    for row in result["rows"]:
        if row["harness_error"]:
            print("HARNESS ERROR", row["name"], row["seed"], row["harness_error"]["message"])
    print("Direct checks:", {k: v for k, v in result["direct_checks"].items() if k != "rows"})
    raise SystemExit(3 if result["counts"]["harness_errors"] else 2 if result["protected_status"] == "FAIL" else 0)


if __name__ == "__main__":
    main()
