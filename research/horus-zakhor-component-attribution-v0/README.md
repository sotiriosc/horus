# Horus/Zakhor component attribution v0

Read `results.md` together with `validity-audit.md`. The campaign is complete,
but its custom neutral harness did not use the current protected Horus receipt
and authorization objects; claims for that boundary are explicitly not
established.

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
