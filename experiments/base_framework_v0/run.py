#!/usr/bin/env python3
"""Run tests and the frozen base-framework-v0 campaign."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile
import unittest

from experiments.base_framework_v0.campaign import execute_campaign, source_hashes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    suite = unittest.defaultTestLoader.loadTestsFromName(
        "experiments.base_framework_v0.test_framework"
    )
    test_result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not test_result.wasSuccessful():
        raise SystemExit(1)

    root = Path(__file__).resolve().parents[2]
    output = args.output or Path(tempfile.mkdtemp(prefix="horus-base-framework-v0-"))
    if args.output:
        output.mkdir(parents=True, exist_ok=False)
    if output.resolve().is_relative_to(root):
        raise ValueError("campaign evidence must remain outside the source tree")

    result = execute_campaign()
    result["verification"] = {
        "unit_tests_run": test_result.testsRun,
        "unit_test_failures": len(test_result.failures),
        "unit_test_errors": len(test_result.errors),
    }
    result["source_sha256"] = source_hashes(root)
    (output / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        "BASE FRAMEWORK V0 PASS: "
        f"tests={test_result.testsRun}; "
        f"scenarios={result['totals']['scenario_runs']}; "
        f"protected_false_accepts={result['totals']['protected_false_accepts']}; "
        f"false_rejects={result['totals']['false_rejects']}; "
        f"duplicate_authorizations={result['totals']['duplicate_authorizations']}; "
        f"evidence={output}"
    )


if __name__ == "__main__":
    main()
