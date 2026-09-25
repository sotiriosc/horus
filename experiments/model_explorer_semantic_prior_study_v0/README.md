# Semantic-prior study v0

Isolated authorized fixtures test verified value following under original action
names and six rotated K1/K2/K3 alias mappings. The same underlying options occupy
matched positions in S/O calls. No opaque token is assumed neutral.

The [preregistration](../../research/model-explorer-semantic-prior-study-v0-preregistration.md)
freezes 216 pairwise and 72 three-way calls, exact fixtures/prompts, seeds,
mapping/order schedules, and descriptive thresholds. Normal setup takes five
authorized transactions per fixture. All offered actions have verified outcomes.
The sixth decision remains under the unchanged framework's authority.

The completed [report](../../research/model-explorer-semantic-prior-study-v0-results.md)
and [compact results](results.json) record 288 real calls, integrity PASS, and
preregistered surface effects favoring opaque labels for +1>0 and +1>−1.
The 0>−1 effect was not established; opaque responses selected the first option
in all 36 of those calls. Detailed mappings and transcripts remain outside the
public repository. [Verification](verification.json) records exact replay and
fresh regressions, plus explicitly null unexposed joint strata.

## Reproduction

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest experiments.model_explorer_semantic_prior_study_v0.test_study -v
PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.model_explorer_semantic_prior_study_v0.run \
  --replay "$HORUS_SEMANTIC_EVIDENCE/model-calls.jsonl"
```

Set `HORUS_SEMANTIC_EVIDENCE` to the retained detailed evidence directory outside the public
repository. It must contain model-calls.jsonl, steps.jsonl, setup.jsonl,
controls.jsonl, registered-fixtures-and-prompts.json, and results.json.
Replay regenerates every authorized fixture and requires byte-identical raw
evidence plus equal serialized summaries and source hashes. It makes no inference
calls. The CLI is exercised end to end with explicitly synthetic unit-test responses.

For fresh inference, start the pinned installed local model/engine and omit
`--replay`. Optionally provide `--output` with a new directory outside the repository.
The runner reconstructs and verifies the exact prospective annex SHA-256 before
calling the model, checks engine/version/model/template and frozen framework hashes,
then runs 288 real calls followed by 48 separate synthetic rejection controls.
There are no inference retries or fallback responses.

The detailed alias mappings, raw model responses, and full step/setup evidence
are kept outside the public tree, as requested. Public compact results contain
aggregate counts, matched underlying-action comparisons, and evidence/source hashes.
No per-call private archive is required to run the synthetic tests.

The model receives only exact_prompt and the common system instruction. Audit
fields such as canonical input, surface_to_underlying, and protected state never
reach it. The adapter translates one offered label before admission; it cannot
grant authorization or change action semantics. Excluding the third option in
a pairwise call is fixed experimental formatting, not learned invalidity.

## Fresh post-study regressions

```bash
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

Run the new suite and this study's exact replay as well. Preserve all prior
findings and expected negative controls. Stop at Explorer: no architecture,
contradiction manipulation, training, or other model roles.
