# Minimum-framework audit harness

This is test-only code around the unchanged public v0/v1/v2 implementations.
The [completion definition](../../research/minimum-framework-completion-definition.md)
and [stress preregistration](../../research/minimum-framework-stress-preregistration.md)
were committed before execution. No new runtime architecture is supplied.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.minimum_framework_audit.run
```

The command creates a new external evidence directory containing full per-case
traces and a compact summary. Exit **2** means the frozen protected criteria
failed; this is the observed research result, not a passing test suite. Exit 3
means an unexpected harness error; exit 0 means no covered failure or uncertainty.

There are 42 protected case types, seven pairs of normal/ablated cases, and three
boundary controls, each repeated for three identity seeds: 177 runs. The 12
alias cases exhaust the existing four-state/three-action world without changing
its transition semantics. All monkeypatches are confined to ablation instances.

The [audit report](../../research/minimum-framework-completeness-audit.md)
distinguishes covered failures from deliberate trust-root corruption and from
the mutable prediction-reference boundary probe. The original milestone result
files remain unchanged. `results.json` contains grouped public-safe observations
and source hashes; raw traces stay outside the repository.
