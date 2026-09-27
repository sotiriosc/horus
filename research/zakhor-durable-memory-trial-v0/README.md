# Zakhor durable-memory trial v0

Zero-inference gate:

```bash
python -m experiments.zakhor_durable_memory_trial_v0.preflight
```

Single campaign:

```bash
python -m experiments.zakhor_durable_memory_trial_v0.run \
  --output research/zakhor-durable-memory-trial-v0/evidence
```

Exact replay:

```bash
python -m experiments.zakhor_durable_memory_trial_v0.replay \
  --output research/zakhor-durable-memory-trial-v0/evidence
```
