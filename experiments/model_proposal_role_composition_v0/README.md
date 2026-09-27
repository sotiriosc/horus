# Model proposal role composition v0: blocked zero-call gate

**C — NOT ESTABLISHED.** The unchanged Map adapter accepts only state 1 / HOLD,
so every required state-0 first action rejects before execution. Existing opaque
Explorer projections also require prior experience. No interfaces changed and no
model inference occurred. This does not establish that the general framework is
incapable of a separately reviewed, more general binding.

Read the [38-section report](../../research/model-proposal-role-composition-v0-results.md),
[prospective protocol](../../research/model-proposal-role-composition-v0-preregistration.md),
`results.json` and `verification.json`.

Reproduce from repository root, with fresh external output directories:

```sh
python3 -m experiments.model_proposal_role_composition_v0.gate --output "$HORUS_COMPOSITION_GATE"
python3 -m experiments.model_proposal_role_composition_v0.gate --replay "$HORUS_COMPOSITION_GATE" --output "$HORUS_COMPOSITION_REPLAY"
```

Both commands use deterministic sources only. Exit 0 means the diagnostic matched
the expected **blocked** result; it does not mean composition passed. Replay checks
both generated evidence files byte-for-byte. Full diagnostic snapshots stay outside
the public tree; the compact result contains no raw prompt/call archive. The
canonical Explorer transaction probes isolate the Map guard and are not the
proposed opaque episodes. No live runner or general adapter was added.

`verification.json` records the 33 actually executed historical regression commands
with their expected outcomes (including historical exit-2 negative checkpoints).
Their evidence environment variables refer to the existing private archives as
documented in the corresponding experiment READMEs. This checkpoint authorizes no
additional model inference, repair, or extension.
