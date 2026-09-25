# Map ranking failure forensics v0

Retained evidence only, from parent `004ec5a` (mechanical), grounded root
`79921b1`, and decomposition `2679cff`. No model calls, world executions,
prompt modifications or runtime/chooser changes. This package imports no
historical experiment runtime and does not rerun mechanical argmax.

From the repository root, with Python 3.10+ and assertions enabled:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m experiments.map_ranking_failure_forensics_v0.analyze --out /tmp/map-forensics-1
PYTHONDONTWRITEBYTECODE=1 python -m experiments.map_ranking_failure_forensics_v0.verify --out /tmp/map-forensics-1
PYTHONDONTWRITEBYTECODE=1 python -m experiments.map_ranking_failure_forensics_v0.analyze --out /tmp/map-forensics-2
PYTHONDONTWRITEBYTECODE=1 python -m experiments.map_ranking_failure_forensics_v0.verify --out /tmp/map-forensics-2
cmp /tmp/map-forensics-1/results.json /tmp/map-forensics-2/results.json
cmp /tmp/map-forensics-1/verification.json /tmp/map-forensics-2/verification.json
cmp /tmp/map-forensics-1/results.json experiments/map_ranking_failure_forensics_v0/results.json
cmp /tmp/map-forensics-1/verification.json experiments/map_ranking_failure_forensics_v0/verification.json
```

Git history through the parent is required for byte/mode preservation checks.
Do not use Python `-O` or historical runners; historical runners execute worlds.

- `retained-evidence.json`: all 48 contexts / 144 action forecasts, complete
  model-visible exact-pair histories with chronological identity, finite parsed
  predictions, detached evaluator outcomes, seeds and original record hashes.
- `source-manifest.json`: archive seal, source hashes and reconstruction scope.
- `results.json`: reconstructed per-action/per-context scores, all requested
  groupings, simple-rule compatibility, seed pairs and ranking counterfactuals.
- `verification.json`: independent arithmetic/reconciliation/preservation checks.

Canonical record/provenance hashes use UTF-8 JSON with sorted keys and compact
comma/colon separators; file hashes cover exact bytes. Public replay validates
this finite export and its scores. Verifying the export against original
requests, receipt/Memory records and raw responses requires the privately
retained source archive. Those raw archives and extraction paths are not
published. “Actual” means retained detached evaluator output, not a newly
executed outcome or a new receipt-grounded forecast claim.

The study is retrospective and descriptive. Fixed-alias/action constants are
explicitly fitted modal baselines on the same data; zero-output counts cannot
establish uncertainty. The next-study suggestion is not implemented or frozen
as a preregistration. See [the full report](../../research/map-ranking-failure-forensics-v0-results.md).
