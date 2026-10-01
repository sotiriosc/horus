# Qwen Error-Driven QLoRA Learning v0

Cycle 1: **ERROR_DRIVEN_PARAMETER_LEARNING_SUPPORTED**. Sealed T1 joint accuracy improved from 208/540 to 540/540 after supervised adapter training on verified mistakes.

Cycle 2: **SECOND_LEARNING_CYCLE_NOT_ESTABLISHED**. M1 and M2 both scored 540/540 on sealed T2; M2 retained T1 and passed regression checks. The registered improvement gates failed without modification.

Read the [complete report and ten completion answers](report.md) or the [structured handoff](handoff.json).

## Evidence map

- [Frozen method](method.md), [data/split freeze](data-freeze.json), and [materialized manifest](materialized/manifest.json).
- [Upstream identity](upstream-provenance.json), [runtime settings](runtime-settings.json), [synthetic qualification and package lock](engineering-qualification.json), and [historical LoRA precedent](historical-learning-precedent.json).
- [M1 artifact freeze](M1-artifact-freeze.json), [M2 artifact freeze](M2-artifact-freeze.json), [Cycle 1 results](cycle1-results.json), and [Cycle 2 results](cycle2-results.json).
- [Exact replay audit](replay-audit.json), [private evidence hash audit](private-evidence-audit.json), [preservation audit](preservation-audit.json), [training recovery accounting](training-recovery-audit.json), and [resource accounting](resource-accounting.json).
- [Posthoc descriptive breakdown](descriptive-error-analysis.json) separates semantic changes from schema validity and does not modify any registered gate.

## Reproduction boundary

Scientific source, recipe, datasets and gates remain byte-for-byte identical to the 33-file Data Freeze manifest. The `posthoc/` scripts were added after both cycles completed; they replay arithmetic, audit retained evidence and render the report without scientific inference or candidate selection.

The frozen unit tests can be run from this directory with `python -m unittest test_study`. The `posthoc/` evidence audits require the pinned environment and original private raw outputs, local model assets, adapters and recovery states at the paths recorded by the frozen runtime. Those private binaries and raw outputs are deliberately not Git objects; hashes and strict parsed two-field scientific answers are published. A public checkout supports code/data/scoring inspection, but cannot independently regenerate missing private model artifacts from hashes alone.

No merge, promotion, deployment, active-model replacement or subsequent study is part of this publication. Memory remains evidence; only the trained adapters carry the parameter changes measured here.
