# State Recovery authorizer status binding v1

**A — STATE RECOVERY STATUS BINDING COMPLETE; ZERO model calls.** See the [30-section report](../../research/state-recovery-authorizer-status-binding-v1-results.md), [frozen protocol](../../research/state-recovery-authorizer-status-binding-v1-preregistration.md), `preflight-results.json`, compact campaign `results.json` and final `verification.json`.

The sole new authorization predicate rejects non-RECOVERING status **in state-Recovery scope**. The existing trusted coordinator branch flag supplies that scope; the source cannot supply it and it is not inferred from candidate status. Ordinary PROPOSED transactions retain historical behavior. Value/identity/duplicate/capacity checks are inherited. Epoch reset retains the repaired authorizer. The normal source still proposes only an exact state int; no prompt, model parser, transport or retry is added.

From repository root, using fresh directories outside public source:

```sh
python3 -m experiments.state_recovery_authorizer_status_binding_v1.preflight --output "$HORUS_STATUS_PREFLIGHT"
python3 -m unittest experiments.state_recovery_authorizer_status_binding_v1.test_status -v
python3 -m experiments.state_recovery_authorizer_status_binding_v1.run --output "$HORUS_STATUS_OUTPUT"
python3 -m experiments.state_recovery_authorizer_status_binding_v1.run --replay "$HORUS_STATUS_OUTPUT" --output "$HORUS_STATUS_REPLAY_OUTPUT"
```

All four commands exit 0 on the recorded passing checks. Preflight optionally accepts `--historical-evidence "$HORUS_INTERFACE_CAMPAIGN"` to compare the old interface campaign file to retained evidence. The old interface CLI remains unchanged and intentionally exits 2 for C. Recovery-v0 remains blocked separately.

Campaign results capture operational measurements; **final classification is in verification.json**, after exact replay and all historical regression statuses have been verified. `run` checks inherited source hashes and compares instrumented/uninstrumented outputs. Detailed local evidence remains private; compact results include its hash. No inference mode exists.

Frozen matrix: 17 typed enum entries × eight decisions = 136 direct cells; 16 RECOVERING accepts, 120 other-status rejects. Preserved old-authorizer acceptance remains visible. Separate controls include 40 invalid identity/value combinations, 25 wrong-status atomic transaction rejections, complete prior interface compatibility, duplicate/capacity and epoch reset. This is a trusted-process software boundary, not a sandbox against arbitrary Python.
