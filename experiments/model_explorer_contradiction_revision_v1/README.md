# Contradiction revision v1 — bounded behavioral study

Explorer-only model proposals after independently rebuilt CONTROL/SHIFT H0/H1/H2 histories. The realized-event grounding and feasibility packages are frozen, as are all earlier studies. Read the [protocol](../../research/model-explorer-contradiction-revision-v1-preregistration.md) and [results](../../research/model-explorer-contradiction-revision-v1-results.md).

The fixed design is two opaque families × two arms × three stages × twelve schedules = 144 real requests. Each reconstructs authentic authorized history, renders the exact registered chronology, obtains one raw response, admits only one displayed alias and executes that proposal through the unchanged receipt path. No history from one measured proposal enters another sample. Invalid responses remain in denominators and are never retried. Twelve synthetic parser controls execute only after all real calls finish.

The model sees only state, offered opaque aliases and authorized chronological transaction/action/consequence rows. It receives no regime, canonical name, evaluator answer, prediction, source identity or recommendation. The string transport has no framework or external-event capability. Actual source authenticity remains a declared software trust root; sharing receipt ancestry does not establish independent physical truth.

## Exact replay and deterministic tests

Retain the complete original private evidence directory, including `metadata.json`, `registered-prompts.json`, `model-calls.jsonl`, `steps.jsonl`, `setup.jsonl`, `controls.jsonl` and `results.json`. Choose a fresh replay output directory outside the public tree:

```sh
python3 -m experiments.model_explorer_contradiction_revision_v1.run --replay "$HORUS_CONTRADICTION_EVIDENCE/model-calls.jsonl" --output "$HORUS_CONTRADICTION_REPLAY"
python3 -m unittest experiments.model_explorer_contradiction_revision_v1.test_study -v
```

Replay makes zero inference requests. It checks exact prompts, seed/configuration, mapping, raw response identity, reconstructed fixtures and measured outcomes. All listed evidence and compact results must match byte-for-byte. The original response metadata is retained; this does not assert that fresh stochastic generation would produce identical text.

`registration-digests.json` contains the prospective annex hash and all 144 prompt hashes. Reconstructing the annex needs no model or private input. `frozen-inputs.json` contains all required historical/repair/feasibility source hashes and pinned model byte digests. The execution wrapper checks frozen inputs before/after and study source hashes throughout. Detailed archives and local paths remain outside public source; compact results/hashes and verification are public.

## Live-run reproducibility

A live run requires the preregistered Ollama version, local model and verified manifest/weight bytes, and a new output directory. The CLI requires a JSON byte-verification record (`manifest_sha256`, `weights_sha256`, weight size and verification time); actual bytes must be hashed against the frozen digests before creating it. Server version, installed model digest, GGUF/47B/Q4_0 metadata and ChatML template are checked before inference. The original sampler and seeds are in the protocol. A transport/protected failure stops without retry or automatic patch. Do not run again merely to improve an outcome; the completed study budget is fixed.

The framework retains at most eight Memory/pair/package records and one pending authentic receipt. A valid H2 measured probe fills the eighth slot without eviction. The prior feasibility observer records actual Recovery/quarantine returns without replacing framework functions. Historical preservation/regression commands and actual results are recorded in `verification.json`.
