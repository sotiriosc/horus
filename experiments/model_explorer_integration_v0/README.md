# Model Explorer integration v0

This experiment replaces only the existing Explorer action-selection object.
The completed minimum framework at `8ec32c8` remains byte-identical.

Read the [preregistration](../../research/model-explorer-integration-v0-preregistration.md)
before the [result report](../../research/model-explorer-integration-v0-results.md).
`frozen-framework.json` pins framework source hashes and the local model digest.

## Reproduce without inference

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest experiments.model_explorer_integration_v0.test_adapter -v
PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.model_explorer_integration_v0.run \
  --replay experiments/model_explorer_integration_v0/model-calls.jsonl
PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.minimum_framework_repair_1.run
make base-framework-v0
make base-framework-v1
make base-framework-v2
```

Replay verifies every exact prompt, system instruction, generation seed/options,
and raw output against the retained real-call transcript, then runs the unchanged
world/evidence/authorization path again. It does not claim that fresh inference
will reproduce every token. Replay and real-inference evidence are labeled.

## Repeat real inference

Use the preregistered `dolphin-mixtral:latest` digest with the recorded Ollama
version/template. Start the local server, then run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.model_explorer_integration_v0.run
```

The runner refuses a different installed model digest. It writes full step
evidence, exact model calls, metadata, and results to a fresh external directory.
An optional `--output` must name a new directory outside the source tree.
The [Ollama generate API](https://docs.ollama.com/api/generate) is the string-only
inference transport. No model tools or framework object access are provided.
The published transcript retains the actual recorded old-server metadata;
current API documentation is not a claim of version equivalence.

`results.json` is compact measured evidence. `model-calls.jsonl` contains exact
inputs, system instructions, raw outputs, parsed actions, and generation metadata.
`proposal-outcomes.json` links real calls to authorization, consequence, prediction,
Memory state, and next proposal; deterministic and forced-output controls are
distinguished. Full step snapshots and raw server/execution logs stay external.
No weights, private predecessor files, credentials, or local absolute paths are
part of the public evidence.

## Insertion boundary

`ModelExplorerAdapter.choose` is invoked by the frozen coordinator after its
existing Memory audit. It serializes the current state and relevant audited
records plus copied epoch/transaction/version metadata. Its only returned
framework value is one action proposal. Parsing failures become an invalid
proposal and are rejected by the existing action gate before world execution.
No deterministic fallback, model self-check, or response cleanup is used.

The adapter survives the coordinator's bounded staging copies by retaining its
per-step I/O object; this object contains scalar metadata and its transcript,
not a reference to protected framework state. The local model sees only text.
The test harness, separately, owns world execution and evidence delivery.
