# State Recovery proposal interface v1

**C — NOT ESTABLISHED. ZERO model calls.** The operational value-only hook passed its bounded checks, but the unchanged authorizer accepts forged status in direct low-level controls, historically and on the new path. See the [33-section results](../../research/state-recovery-proposal-interface-v1-results.md), [frozen protocol](../../research/state-recovery-proposal-interface-v1-preregistration.md), compact `results.json` and actual execution records in `verification.json`.

`StateRecoveryFramework(..., proposal_source=source)` exposes `source.propose(DecisionContext) -> int`. Only an exact built-in int 0–3 is admitted. Native Recovery owns the attempt and candidate identity/status. The unchanged authorizer and realized-event staged wrapper retain publication authority. Omitting the source preserves native behavior. This is a software API in a trusted process, not an arbitrary-Python sandbox.

From repository root, use fresh external evidence directories:

```sh
python3 -m unittest experiments.state_recovery_proposal_interface_v1.test_interface -v
python3 -m experiments.state_recovery_proposal_interface_v1.run --output "$HORUS_INTERFACE_OUTPUT"
python3 -m experiments.state_recovery_proposal_interface_v1.run --replay "$HORUS_INTERFACE_OUTPUT" --output "$HORUS_INTERFACE_REPLAY_OUTPUT"
```

Unit tests pass; campaign and replay intentionally exit **2** for classification C. With retained private Recovery-v0 evidence, add `--historical-evidence "$HORUS_RECOVERY_DIAGNOSTIC"` to compare its `diagnostic.json` byte-for-byte. Without that argument, the two paths still execute and compare the same 32 historical cases directly.

Detailed campaign evidence stays outside public source. `run` verifies inherited hashes, compares the source-level single-expression change and inherited authority methods, runs instrumented/uninstrumented duplicates and optionally exact replay. Public results record evidence/source digests. No inference mode, model parser, prompt, model transport, retry or automatic follow-up campaign exists.

Normal injected path: 52 synthetic transactions, 38 callbacks, 23 commits and 29 atomic rejections. Separate controls: 32 paired historical/default cases, eight budget cases and 32 identity/status cases against each unchanged authorizer. Wrong-status acceptance (8/8 per path) is explicitly separate from zero protected false accepts in normal transactions. The old Recovery-v0 checkpoint remains blocked and unmodified.
