# Horus/Zakhor component attribution v0

Run zero-inference checks:

```bash
python -m experiments.horus_zakhor_component_attribution_v0.preflight
python -m unittest experiments.horus_zakhor_component_attribution_v0.test_study
```

Run the single frozen campaign once:

```bash
python -m experiments.horus_zakhor_component_attribution_v0.run \
  --output research/horus-zakhor-component-attribution-v0/evidence
```

Replay without inference:

```bash
python -m experiments.horus_zakhor_component_attribution_v0.replay \
  --output research/horus-zakhor-component-attribution-v0/evidence
```
