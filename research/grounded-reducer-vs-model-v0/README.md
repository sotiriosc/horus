# Grounded reducer versus model v0

The [prospective registration](preregistration.md) freezes four independent
matched observation schedules and the exact M, L and R3 rules. The completed
Modern Memory versus Horus v0.1 study remains unchanged on its own branch.

Zero-inference checks:

```sh
python -m unittest experiments.grounded_reducer_vs_model_v0.test_study -v
python -m experiments.grounded_reducer_vs_model_v0.preflight
```

Single-use live campaign:

```sh
python -m experiments.grounded_reducer_vs_model_v0.run \
  --output research/grounded-reducer-vs-model-v0/evidence
python -m experiments.grounded_reducer_vs_model_v0.analyze \
  --output research/grounded-reducer-vs-model-v0/evidence
python -m experiments.grounded_reducer_vs_model_v0.replay \
  --output research/grounded-reducer-vs-model-v0/evidence
```

Each `evidence/schedules/<name>/current` points to one committed triple.
Resolve it once when reading all arms. `work` is private transaction state.
A stopped live campaign is never automatically rerun.
