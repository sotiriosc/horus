#!/usr/bin/env python3
"""Run v2 tests and frozen campaign, writing detailed evidence outside source."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile
import unittest

from experiments.base_framework_v2.campaign import execute_campaign, source_hashes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromName("experiments.base_framework_v2.test_framework")
    tests = unittest.TextTestRunner(verbosity=1).run(suite)
    if not tests.wasSuccessful():
        raise SystemExit(1)
    root = Path(__file__).resolve().parents[2]
    output = args.output or Path(tempfile.mkdtemp(prefix="horus-base-framework-v2-"))
    if args.output:
        output.mkdir(parents=True, exist_ok=False)
    if output.resolve().is_relative_to(root):
        raise ValueError("evidence must remain outside source tree")
    result = execute_campaign()
    result["verification"] = {
        "unit_tests_run": tests.testsRun,
        "unit_test_failures": len(tests.failures),
        "unit_test_errors": len(tests.errors),
    }
    result["source_sha256"] = source_hashes(root)
    (output / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    totals = result["totals"]
    print(
        "BASE FRAMEWORK V2 PASS: "
        f"tests={tests.testsRun}; scenarios={totals['scenario_runs']}; "
        f"protected_false_accepts={totals['protected_false_accepts']}; "
        f"ab_common_blocks={totals['ab_common_mode_blocks']}; "
        f"abc_false_accepts={totals['abc_common_mode_false_accepts']}; "
        f"registry_false_accepts={totals['registry_corruption_false_accepts']}; "
        f"evidence={output}"
    )


if __name__ == "__main__":
    main()
