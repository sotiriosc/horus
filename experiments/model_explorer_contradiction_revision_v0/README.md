# Contradiction-revision v0 — mandatory feasibility gate

**Preflight result: INFEASIBLE. Zero model calls.** At the first changed event,
state-1 HOLD realized −1 while frozen A/B/C reported +1; the framework committed
+1. SHIFT stopped at transaction 4. This was an externally detected false accept,
not a safe rejection. Model revision remains untested.
See the [results report](../../research/model-explorer-contradiction-revision-v0-results.md),
[compact results](results.json), and [verification](verification.json).

The [protocol](../../research/model-explorer-contradiction-revision-v0-preregistration.md)
requires safe authorization of a changed external consequence before any model
inference. Only the experiment-side overlay, ordinary-path diagnostic and pure
chronological projection are implemented here. There is no model transport or
behavioral campaign implementation. The 144-call design is conditional on feasibility.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest experiments.model_explorer_contradiction_revision_v0.test_preflight -v
PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.model_explorer_contradiction_revision_v0.run
```

The diagnostic writes detailed evidence to a new temporary directory outside the
repository, or to a new explicit `--output` directory. It returns exit code 2 if
the world-change feasibility requirement fails. This is not a successful safety
result merely because the diagnostic ran. Inspect `results.json` and `preflight.json`.
It never loads or calls a model. No receipt, witness, registry or Memory is patched.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.model_explorer_contradiction_revision_v0.run \
  --replay "$HORUS_CONTRADICTION_EVIDENCE"
```

Set `HORUS_CONTRADICTION_EVIDENCE` to the retained preflight directory. Replay must
reproduce both diagnostic evidence and compact results byte-for-byte. Exit code 0
on replay means the recorded result was reproduced, not that feasibility passed.
This is not the blocked 144-model-call replay. No inference is made in either mode.

The externally audited failure, if present, must stop SHIFT immediately. No false
Memory is supplied to a model. Existing prior-model replay and framework regressions
may still verify preservation without enabling the blocked study. Preserve their
historical negative controls; do not interpret them as support for new nonstationarity.
