# Modern memory versus Horus v0

Zero-inference preflight:

```bash
python -m experiments.modern_memory_vs_horus_v0.preflight
```

Single live campaign:

```bash
python -m experiments.modern_memory_vs_horus_v0.run \
  --output research/modern-memory-vs-horus-v0/evidence
```

Analysis and exact replay:

```bash
python -m experiments.modern_memory_vs_horus_v0.analyze \
  --output research/modern-memory-vs-horus-v0/evidence
python -m experiments.modern_memory_vs_horus_v0.replay \
  --output research/modern-memory-vs-horus-v0/evidence
```
