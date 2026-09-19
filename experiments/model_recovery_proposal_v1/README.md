# Model Recovery proposal v1

The model occupies only the replacement-state proposal slot after verified failure. Explorer/Map are deterministic; receipt authority, Measure, Memory, native attempt, trusted envelope/scope, independent status/value authorizer and atomic publication are inherited unchanged.

Read the [40-section report](../../research/model-recovery-proposal-v1-results.md), [frozen preregistration](../../research/model-recovery-proposal-v1-preregistration.md), compact `results.json` and `verification.json`. The fixed design has eight genuine Recovery fixtures, two opaque families and six paired mappings/seeds: exactly 96 real calls, 48 per family. No retries, replacement calls or extensions. Public evidence contains compact per-call outcomes; exact raw responses, prompts and full steps remain private.

From repository root, using fresh external directories:

```sh
python3 -m experiments.model_recovery_proposal_v1.preflight --output "$HORUS_RECOVERY_PREFLIGHT"
python3 -m unittest experiments.model_recovery_proposal_v1.test_study -v
python3 -m experiments.model_recovery_proposal_v1.run --replay "$HORUS_RECOVERY_EVIDENCE/model-calls.jsonl" --output "$HORUS_RECOVERY_REPLAY"
```

Preflight uses synthetic responses only. Recorded-response replay uses zero new inference and requires identical registration, calls, steps, controls, metadata and compact results. The unit tests also use synthetic responses. The preflight covers 192 correct/wrong transactions and 12 no-Recovery controls. The 20 self-certification/parser controls are synthetic and separate from model behavior.

The following is the archived live-run interface, **not authorization for another campaign**:

```sh
python3 -m experiments.model_recovery_proposal_v1.run --output "$HORUS_RECOVERY_LIVE_OUTPUT" --model-bytes "$HORUS_MODEL_BYTE_PROOF"
```

It requires the frozen model bytes/server, committed passing preflight and unchanged source hashes. It makes exactly the registered 96 requests unless a failure stops it, and never retries. Review the report before considering any separately authorized follow-up. This checkpoint is closed after its recorded campaign.

The model sees the verified realized next state; this tests bounded proposal generation from visible evidence, not hidden-state inference. Usefulness and authorization integrity are separate results. The trusted Python process, receipt emitter and coordinator scope remain explicit trust boundaries. No general Recovery reasoning, autonomous repair or learning claim is made.
