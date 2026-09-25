# Recovery proposal v0 — blocked interface checkpoint

**Zero model calls. Model usefulness UNTESTED / NOT ESTABLISHED.** The frozen coordinator constructs `Recovery().state_candidate(...)` inline and exposes no Recovery proposer/component/factory. Native Recovery authorization passed bounded diagnostics, but no model adapter gate passed. Do not substitute the ordinary `candidate_value` fault input or native Recovery's own receipt-derived value for a model candidate.

Read the [32-section report](../../research/model-recovery-proposal-v0-results.md), [zero-call protocol](../../research/model-recovery-proposal-v0-preregistration.md), `results.json`, `verification.json` and `frozen-inputs.json`. Source history is unchanged except the root README append and inventory refresh. No live model prompt, parser, transport, schedule or usage result exists.

From repository root, with a fresh external evidence directory:

```sh
python3 -m unittest experiments.model_recovery_proposal_v0.test_interface -v
python3 -m experiments.model_recovery_proposal_v0.run --output "$HORUS_RECOVERY_DIAGNOSTIC_OUTPUT"
```

Tests pass; the diagnostic intentionally exits **2**, meaning the proposal-interface gate is blocked. It enumerates 12 unchanged world transitions through authentic receipts and runs 32 synthetic transactions (24 semantic matrix + four interface probes + four consequence-only HOLD controls), plus the native object-local budget check. It also compares an uninstrumented repeat. It never calls a model or changes core functions/module bindings.

Exact replay with the retained private `diagnostic-final` directory:

```sh
python3 -m experiments.model_recovery_proposal_v0.run --replay "$HORUS_RECOVERY_DIAGNOSTIC_EVIDENCE" --output "$HORUS_RECOVERY_REPLAY_OUTPUT"
```

Replay requires identical diagnostic and compact-result bytes and still exits **2** for the same missing interface. This is a synthetic checkpoint replay, not recorded model inference. Detailed diagnostic archives remain private; public compact evidence retains their digest. Historical regression commands and actual/expected statuses are in verification. There is no inference mode to run and no automatic architectural repair.
