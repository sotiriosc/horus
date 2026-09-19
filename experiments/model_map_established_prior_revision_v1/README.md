# Established-prior Map revision v1

A bounded follow-up to unchanged Map proposal v0 (`f7b16c4`). Direct authenticated HOLD-only history supplies two old observations before an external consequence-law change. The model proposes Map predictions only; the Map adapter, parser, deterministic Explorer, latch, Measure, Memory, Recovery, receipt authority and bounds are imported unchanged.

Result: **ESTABLISHED-PRIOR MAP REVISION REPLICATED**. Exactly 144 calls; 144 valid, 0 safe rejections; zero protected false accepts. O1: SHIFT P0 exact old 12/12, SHIFT P2 exact new 12/12, favorable P2 pairs 12/12; O2: SHIFT P0 exact old 12/12, SHIFT P2 exact new 12/12, favorable P2 pairs 12/12. Exact replay and all 23 regression commands returned expected statuses.

Read the [frozen protocol](../../research/model-map-established-prior-revision-v1-preregistration.md), [35-section report](../../research/model-map-established-prior-revision-v1-results.md), `results.json` and `verification.json`. The [representation-prior checkpoint](../../research/representation-priors-and-neutrality-checkpoint.md) remains in force. Map-v0 remains NOT ESTABLISHED; its prior evidence is never overwritten or pooled with this run.

Protocol commit `ca05bf4`; passing preflight, implementation and prospective annex commit `5e4283e`, all before inference. Standard-library synthetic checks, from repository root:

```sh
python3 -m unittest experiments.model_map_established_prior_revision_v1.test_study -v
python3 -m experiments.model_map_established_prior_revision_v1.preflight --output "$HORUS_MAP_PRIOR_PREFLIGHT_OUTPUT"
```

Use fresh external output directories. Preflight constructs all six authenticated histories and the full 144-prompt annex, plus twelve synthetic probes checking prediction/receipt separation. It makes zero model calls. The summary/digests are in `preflight-results.json`; unit tests are not model behavior.

The full raw audit archive is retained privately. Set `HORUS_MAP_PRIOR_EVIDENCE` to its `real` directory, and choose a fresh `HORUS_MAP_PRIOR_REPLAY_OUTPUT` outside the checkout:

```sh
python3 -m experiments.model_map_established_prior_revision_v1.run --replay "$HORUS_MAP_PRIOR_EVIDENCE/model-calls.jsonl" --output "$HORUS_MAP_PRIOR_REPLAY_OUTPUT"
```

This reconstructs authenticated stage histories and reuses every recorded response, with zero new inference. All prompts, calls, steps, setup, controls, metadata and compact results must reproduce byte-for-byte. Compact public evidence alone cannot replace the private transcript archive.

Prospective reconstruction: `python3 -m experiments.model_map_established_prior_revision_v1.run --register --output "$HORUS_MAP_PRIOR_REGISTRATION_OUTPUT"`. This writes the deterministic public prompt-digest file; use an isolated reproduction checkout. The full annex has 144 matched calls, seeds 60001–60012, mappings j mod 6.

Original execution command, recorded for reproducibility: `python3 -m experiments.model_map_established_prior_revision_v1.run --model-bytes "$HORUS_MODEL_BYTE_PROOF" --output "$HORUS_MAP_PRIOR_RUN_OUTPUT"`. It requires passing preflight, the frozen annex, pinned local Ollama 0.1.16 and complete verified model bytes. Exactly 144 calls, no retries or extensions, then the same 18 synthetic admission controls as v0. This checkpoint is closed; do not start inference for replay.

`frozen-inputs.json` protects inherited sources/results including the complete v0 package. Actual regression commands, expected/actual exit codes, timestamps and log hashes are in verification. Historical negative controls, including the old contradiction diagnostic and trusted-root compromise, remain intact. This trusted-process prototype is not a sandbox for hostile Python or a proof of physical truth. No model training, weight changes, persistent learning, role combination or Recovery promotion occurs.
