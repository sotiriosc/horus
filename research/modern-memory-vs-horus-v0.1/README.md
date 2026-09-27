# Modern memory versus Horus v0.1

Read preregistration.md and source-manifest.json before interpreting evidence.
The v0 INVALID study is preserved at its original commit and directory.

Run once, from fresh isolated state:

```sh
python -m experiments.modern_memory_vs_horus_v0_1.preflight
python -m experiments.modern_memory_vs_horus_v0_1.run --output research/modern-memory-vs-horus-v0.1/evidence
python -m experiments.modern_memory_vs_horus_v0_1.analyze --output research/modern-memory-vs-horus-v0.1/evidence
python -m experiments.modern_memory_vs_horus_v0_1.replay --output research/modern-memory-vs-horus-v0.1/evidence
```

`evidence/current` is the atomic committed pair. Resolve this pointer once when
reading both arms. `evidence/work` is private transaction state and is not a
published experience. `evidence/pairs` preserves matched checkpoints.
Never resume or rerun a stopped live campaign automatically.

Zero-inference infrastructure tests:

```sh
python -m unittest experiments.modern_memory_vs_horus_v0_1.test_protocol -v
```
