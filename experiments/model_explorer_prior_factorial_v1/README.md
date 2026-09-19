# Prior factorial v1

Three targeted, authorized two-option fixtures compare canonical names, K1/K2/K3,
and Q7/M4/Z2. Six opaque mappings are independently crossed with both option and
evidence orders. The framework and semantic-prior v0 system instruction remain
unchanged. The model only proposes; existing external authorization still governs
execution and Memory. No surface family is assumed neutral.

[Preregistration](../../research/model-explorer-prior-factorial-v1-preregistration.md)
freezes exactly 216 real calls and 14 synthetic rejection controls. There is no
automatic sample extension. Six observations per order cell support only narrow
descriptive claims. Seeds are matched across surfaces, but mapping and seed are
not independently crossed.

## Reproduce without new inference

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest experiments.model_explorer_prior_factorial_v1.test_study -v
PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.model_explorer_prior_factorial_v1.run \
  --replay "$HORUS_FACTORIAL_EVIDENCE/model-calls.jsonl"
```

Set `HORUS_FACTORIAL_EVIDENCE` to the retained detailed archive outside this public
tree. It contains model-calls.jsonl, steps.jsonl, setup.jsonl, controls.jsonl,
registered-fixtures-and-prompts.json, and results.json. Replay reconstructs normal
authorized fixtures and requires byte-identical detailed evidence, JSON-equal
summary, and identical source hashes. It makes no inference calls. Synthetic unit
tests do not require that archive and do not count as measured model behavior.

For a separately authorized fresh generation, start the pinned installed local
model and engine, then omit `--replay`. `--output` may name a new directory outside
the repository. The runner reconstructs the prospective annex and checks its hash,
framework sources, engine/model/template identity before calls. It permits no
inference retry or fallback; an integrity/transport mismatch stops execution.

Detailed per-call mappings, protected snapshots, exact prompts, and raw transcripts
remain outside the public repository. Public compact evidence contains aggregate
tables, matched canonical-action comparisons, and hashes. The prospective schedule
is public so another researcher can reconstruct it. The model itself receives
only the registered surface-rendered prompt and unchanged system instruction.

## Required fresh regressions

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.model_explorer_semantic_prior_study_v0.run \
  --replay "$HORUS_SEMANTIC_EVIDENCE/model-calls.jsonl"
PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.model_explorer_adaptive_episode_v0.run \
  --replay experiments/model_explorer_adaptive_episode_v0/model-calls.jsonl
PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.model_explorer_memory_study_v1.run \
  --replay experiments/model_explorer_memory_study_v1/model-calls.jsonl
PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.model_explorer_integration_v0.run \
  --replay experiments/model_explorer_integration_v0/model-calls.jsonl
PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.minimum_framework_repair_1.run
make base-framework-v0
make base-framework-v1
make base-framework-v2
```

Set `HORUS_SEMANTIC_EVIDENCE` to the earlier semantic-prior v0 detailed archive.
Run the new suite and this study's replay as well. Preserve expected historical
negative controls and all earlier results. Stop at this experiment: no new model
role, architecture development, training, or nonstationarity.
