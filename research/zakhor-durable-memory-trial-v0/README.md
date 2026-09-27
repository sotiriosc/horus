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
python -m experiments.zakhor_durable_memory_trial_v0.postrun_replay_v3 \
  --output research/zakhor-durable-memory-trial-v0/evidence
```

The frozen campaign completed all inference and protected publication before a
reporting-only exception in the original analyzer. `reporting-amendment.md`
records the zero-inference recovery; `postrun_v3.py` and
`postrun_replay_v3.py` produce and verify the authoritative report without
changing raw evidence. The original `replay` command remains available for the
frozen pre-inference implementation, while the v3 command above verifies the
completed evidence package.
