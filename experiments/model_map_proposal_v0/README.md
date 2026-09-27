# Model Map proposal v0

The model proposes one finite next-state/consequence prediction for deterministic state-1 HOLD. The existing pre-execution latch, external realized receipt, Measure, Recovery, authorization and Memory remain unchanged. Wrong predictions are permitted; wrong realized publication is not.

Result: **CONTRADICTION-DRIVEN MAP REVISION NOT ESTABLISHED**. Exactly 144 calls: 142 valid, two safe rejections, zero protected false accepts. Both families had 0/12 exact old predictions at SHIFT H0 despite 12/12 favorable matched H2 pairs. The old-Map prerequisite and all-valid gate failed. Exact replay and 20 regression commands returned their expected outcomes.

Read the [frozen protocol](../../research/model-map-proposal-v0-preregistration.md), [representation checkpoint](../../research/representation-priors-and-neutrality-checkpoint.md), [report](../../research/model-map-proposal-v0-results.md), compact `results.json` and `verification.json` together. The historical parent is `492d257`; Part A was committed at `c4fcbfc`, protocol at `2091199`, zero-call gate at `80643ad`, and implementation/prompt annex at `a131b38`, all before inference.

From repository root, synthetic gate and tests need only the Python standard library:

```sh
python3 -m unittest experiments.model_map_proposal_v0.test_study -v
python3 -m experiments.model_map_proposal_v0.gate --output "$HORUS_MAP_GATE_OUTPUT"
```

Use fresh output directories outside the public tree. Gate is 16 synthetic cases, zero model calls. `gate-results.json` retains the original digest. Unit tests include parser domains, staging isolation, wrong predictions, authenticated projections and frozen criterion checks; they are not model observations.

The full raw audit archive is privately retained, not embedded in this public tree. Set `HORUS_MAP_EVIDENCE` to its `real` directory and `HORUS_MAP_REPLAY_OUTPUT` to a new external directory, then:

```sh
python3 -m experiments.model_map_proposal_v0.run --replay "$HORUS_MAP_EVIDENCE/model-calls.jsonl" --output "$HORUS_MAP_REPLAY_OUTPUT"
```

Replay verifies every prompt/configuration/response, setup, latch, receipt, protected publication, parser control, metric and compact result byte-for-byte without inference. Compact public evidence alone cannot substitute for that archive. Reconstruct the prospective prompt annex without inference using `--register --output "$HORUS_MAP_REGISTRATION_OUTPUT"`; it writes deterministic `registration-digests.json`, so use an isolated checkout for reproduction.

Original execution command, recorded for reproducibility, is `python3 -m experiments.model_map_proposal_v0.run --model-bytes "$HORUS_MODEL_BYTE_PROOF" --output "$HORUS_MAP_RUN_OUTPUT"`. It requires the passing gate, matching prospective annex, pinned Ollama 0.1.16 local server and complete verified manifest/weight bytes. It makes exactly 144 scheduled calls, no retries, then 18 separate synthetic controls. This checkpoint is closed: do not launch another inference run as part of replay.

Historical regressions and their actual exit codes/log hashes are in `verification.json`. `frozen-inputs.json` binds inherited implementations and evidence. Legacy contradiction-v0 remains an expected failing diagnostic; trust-root compromise remains out of model. The adapter is a component seam in a trusted Python process, not a sandbox for arbitrary untrusted Python. Only model text receives proposal authority. No architecture, weight, world or authority changes are part of this study.
