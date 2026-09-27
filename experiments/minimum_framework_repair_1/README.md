# Minimum-framework repair 1 validation

Run from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.minimum_framework_repair_1.run
make test
make independent-commit
make independent-commit-followup
make base-framework-v0
make base-framework-v1
make base-framework-v2
```

The repair runner creates an external evidence directory; optional `--output`
must name a new directory outside the source tree. Full `results.json` contains
177 frozen scenario runs, 109 direct repair probes, and source hashes.
`compact.json` groups the frozen scenarios. The committed `results.json` is
that public-safe compact evidence. Exit 0 means protected/direct checks pass,
2 means a covered failure, and 3 means a frozen-harness execution error.
Historical campaign files are preserved byte-for-byte.

The frozen audit module is imported, never edited. The adapters in `run.py` are:

* `old_prediction`: supply the same stale Prediction through `Map.predict`
  before the latch, rather than replacing the reference after `begin_step`.
* F9 observation: compare the latched prediction actually used for scoring
  against the pre-outcome snapshot. Separately record replacement of the exposed
  reference. Keep the independent truth-to-confirmation comparison unchanged.
* Early-continuation weakening: explicitly bypass the package-required ingress
  in test-local code; retain the A/B pair, state and Measure checks. This
  reproduces the old package-less commit after normal legacy ingress is blocked.

All other frozen scenarios and six other ablation implementations run unchanged.
Legacy ingress now returns a fail-closed result, so its existing adapter still
works. The two independently blocked ablations remain safe; no outcome is forced.

Direct checks add mutation snapshots, all 12 legitimate transitions, all 36
alias attempts, small invalid-domain boundaries, both facade/inner receipt
routes, method inventory, final-validation failures before publication (empty
and full rings), chronological recovery, prediction ownership, and measured
three-subsystem recovery. This is deterministic finite coverage, not fuzzing.

See the [frozen repair preregistration](../../research/minimum-framework-repair-1-preregistration.md)
and [repair report](../../research/minimum-framework-repair-1-results.md).
