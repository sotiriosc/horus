# Grounded safe fallback v0

The [prospective registration](preregistration.md), [frozen scenarios](scenarios.json), and [source manifest](source-manifest.json) were committed at `3fb0f91` before live inference. The grounded-hybrid parent remains unchanged at `dbe9894abfcbfea107d6cc30cf4a1ccf3a3108b0`.

The completed four-arm protected campaign is in [evidence](evidence). Read the [report](report.md), [results](evidence/results.json), and [exact replay](evidence/replay.json). Seed histories match across arms before each first autonomous decision; later decisions follow arm-specific protected histories. P8 has a fresh-process unresolved restart. This single-use evidence is not rerun in place.

Validation:

```sh
python -m unittest experiments.grounded_safe_fallback_v0.test_study -v
python -m experiments.grounded_safe_fallback_v0.preflight
python -m experiments.grounded_safe_fallback_v0.replay --output research/grounded-safe-fallback-v0/evidence
```
