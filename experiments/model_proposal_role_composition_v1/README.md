# Model proposal role composition v1

This is the single registered live composition study using the frozen input
bindings from `e10fbb8`. Read the [results](../../research/model-proposal-role-composition-v1-results.md),
[preregistration](../../research/model-proposal-role-composition-v1-preregistration.md),
`results.json` and `verification.json` before interpreting the outcome. No previous
adapter or authority component is edited. Live Recovery input is rendered only
from the existing genuine callback context; it uses no precomputed world answer.

The primary result concerns composition integrity. Safe malformed/wrong responses
remain data and are never repaired, retried or replaced. If a role or sequential
path is not reached, its live behavior is untested; historical and synthetic
boundary evidence is reported separately.

Deterministic checks and exact replay from repository root:

```sh
python3 -m unittest experiments.model_proposal_role_composition_v1.test_study -v
python3 -m experiments.model_proposal_role_composition_v1.run --replay "$HORUS_COMPOSITION_LIVE" --output "$HORUS_COMPOSITION_REPLAY"
```

Both commands use zero new inference. Replay requires the private live evidence
directory and a fresh external output directory. It recomputes all projections
from current authenticated Memory, runs the bounded post-campaign controls, and
requires all seven evidence files byte-identical. UNTRIED and [] are never historical
observations. All full prompts, responses, transaction traces, metadata and chains
remain in the private archive; only compact evidence is public.

The following is the archived live interface, **not authorization to repeat it**:

```sh
python3 -m experiments.model_proposal_role_composition_v1.run --output "$HORUS_COMPOSITION_OUTPUT" --model-bytes "$HORUS_MODEL_BYTE_PROOF"
```

It checks frozen scientific sources, the zero-call unknown-marker invariant,
verified pinned bytes/server and fixed model schedule. Every request is stateless.
There are at most 12 episodes × 8 decisions, 96 calls per role, 288 total. No retries
or replacements. Bounded role controls occur only after the live episodes.
The completed checkpoint authorizes no new live campaign or architecture change.
