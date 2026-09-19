# Adaptive Explorer episode v0

Twelve matched seed pairs, two instruction conditions, twelve decisions per
episode. Every episode starts with empty Memory; all later displayed outcomes
come from that episode's authorized model actions. The model is Explorer only.

The [preregistration](../../research/model-explorer-adaptive-episode-v0-preregistration.md)
freezes prompts, seeds, ordering, metrics, support thresholds, and the prospective
clarification separating sparse/conflicting retests from repeated known-worse
choices. It never bans an action after a negative outcome. The existing eight
record Memory ring is preserved; full step evidence retains older observations.

## Reproduce without inference

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest experiments.model_explorer_adaptive_episode_v0.test_study -v
PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.model_explorer_adaptive_episode_v0.run \
  --replay experiments/model_explorer_adaptive_episode_v0/model-calls.jsonl
```

Replay verifies exact prompts, settings, seeds, responses, and the complete
reconstructed steps, episode analysis, source hashes, and summary. It uses the
unchanged framework gates and makes no model calls. Synthetic unit tests are
separate from measured evidence, including tests of contradiction handling.

The first completed-data replay exposed a tuple/list comparison mismatch in its
final summary assertion. The replay-only fix and added CLI regression test are
documented in `replay-compatibility.json`, which pins both original and corrected
source hashes. Original inference artifacts remain unchanged. Replay accepts only
these exact runner/test differences; behavioral sources and preregistration must
still match exactly. The full steps and episode analysis were already identical
before the assertion fix.

For fresh inference, run the registered local model and Ollama version and omit
`--replay`. The runner checks version, manifest digest, prompt template, and frozen
framework hashes. `--output` must name a new directory outside the repository.
No retries, fallback responses, or preparation lessons are used. A new generation
need not reproduce the original responses despite fixed seeds.

## Evidence

- `results.json`: compact per-arm and per-episode results and source/evidence hashes.
- `model-calls.jsonl`: exact model input/output, order, original prediction, actual
  consequence, and authorization for every real call.
- `steps.jsonl`: full protected-state snapshots, independent evidence packages,
  Memory before/after, ring bounds, and original integrity-observer results.
- `episode-analysis.json`: every step's descriptive metrics, discoveries, retests,
  contradictions, and all first-to-later repeated-state comparisons.
- `frozen-framework.json`: unchanged framework hashes and pinned model digests.

Only `model_call.exact_prompt` and the recorded condition system instruction reach
the model. `model_call.input` and `authorized_relevant_records` are audit fields,
not extra model inputs. Test observers and the hidden test world never recommend
actions. No model output directly mutates protected state or authorizes a commit.

## Fresh regressions

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.minimum_framework_repair_1.run
PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.model_explorer_integration_v0.run \
  --replay experiments/model_explorer_integration_v0/model-calls.jsonl
PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.model_explorer_memory_study_v1.run \
  --replay experiments/model_explorer_memory_study_v1/model-calls.jsonl
make base-framework-v0
make base-framework-v1
make base-framework-v2
```

The framework and all earlier experiment artifacts remain unchanged. This is a
bounded behavioral study, not training, a new framework, or evidence of inferred
causality. In the deterministic frozen world, revision after contradictory
verified outcomes may have no live opportunities.
