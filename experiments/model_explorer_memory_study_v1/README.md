# Model Explorer Memory study v1

This study separates verified negative avoidance (A) from preference for a
verified positive alternative (B). It does not reinterpret the previous v0
result or modify the completed framework.

The [preregistration](../../research/model-explorer-memory-study-v1-preregistration.md)
and `fixtures-and-prompts.json` freeze every exact prompt, fixture, seed,
sample count, and support threshold before inference. Study A uses five real
authorized setup transactions; B uses six, including the verified positive
HOLD outcome. No Memory record is manufactured.

## Reproduction

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest experiments.model_explorer_memory_study_v1.test_study -v
PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.model_explorer_memory_study_v1.run \
  --replay experiments/model_explorer_memory_study_v1/model-calls.jsonl
```

Replay checks all exact prompts, seeds, model configuration, and raw responses,
then reconstructs the authorized setup and runs the same framework gates. It
requires no inference server and does not claim deterministic fresh generation.

For new real inference, use the pinned local model and Ollama version, start
the local server, and omit `--replay`. The runner checks model/version first,
then executes 32 no-history bias calls followed by 192 paired-arm calls. Each
cell has 24 seed pairs and balanced arm order. An optional `--output` must be
a new directory outside the repository. There is no retry-until-success or
automatic prompt tuning. The optional exploration condition is not run.

## Evidence

* `results.json`: compact distributions, pair outcomes, fixed-threshold verdicts,
  framework checks, and evidence/source hashes.
* `model-calls.jsonl`: each call's condition/seed/order; exact prompt/system/options;
  raw authorized Memory even when withheld; displayed form; response; parsed
  action; prediction; authorization; consequence; and resulting Memory identities.
* `fixtures-and-prompts.json`: eight preregistered prompt templates and the
  authorized outcomes from which they were constructed.
* `frozen-framework.json`: exact unchanged source hashes and model digests.

Full setup and protected-state snapshots are retained outside the public tree.
The [report](../../research/model-explorer-memory-study-v1-results.md) distinguishes
model behavior from framework integrity and explains floor/ceiling limitations.

The transcript's `model_call.input` is the canonical raw projection retained
for compatibility with the previous integrity observer. The actual text sent
to the model is **only** `model_call.exact_prompt`, the serialization of
`model_call.model_visible_input`, plus the recorded system instruction.
`authorized_relevant_records` is audit evidence, never an additional hidden
model input. Without-history prompts contain no outcomes.

UNTRIED means no observation in the displayed audited projection. It is never
imputed as observed consequence zero. Semantic grouping preserves every shown
consequence and adds no authority, prediction, or evaluator-selected answer.

## Frozen regression checks

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.minimum_framework_repair_1.run
PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.model_explorer_integration_v0.run \
  --replay experiments/model_explorer_integration_v0/model-calls.jsonl
make base-framework-v0
make base-framework-v1
make base-framework-v2
```

The previous integration harness is reused without editing it. A test-local
adapter factory selects the new presentation at the same Explorer boundary;
all its existing world/evidence/prediction/provenance observers still run.
Presentation equality and exact registered prompts are additional test-side
checks, not a new framework authority layer. The model can propose an action,
cannot directly mutate protected state, and can authorize nothing.
