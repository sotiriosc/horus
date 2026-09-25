# Cross-episode stale-Memory feasibility v0

Zero-model deterministic feasibility, preserving all old architecture. Read the [preregistration](../../research/cross-episode-stale-memory-feasibility-v0-preregistration.md).

Set STALE_OUTPUT to a new durable directory outside this public checkout, and STALE_REPLAY to another new durable directory. No server or model is needed:

```sh
python3 -m experiments.cross_episode_stale_memory_feasibility_v0.run --output "$STALE_OUTPUT"
python3 -m experiments.cross_episode_stale_memory_feasibility_v0.run --replay "$STALE_OUTPUT" --output "$STALE_REPLAY"
python3 -m unittest experiments.cross_episode_stale_memory_feasibility_v0.test_fixture -v
```

Generation and replay forbid socket access. The two raw files must match byte for byte. Raw output remains provisional C until replay and historical preservation pass; the public final result records all seventeen gates and the actual verification. New negative controls test receipt substitutions in isolated systems. Native deterministic state Recovery is observed without forcing or bypassing it. No behavioral model follow-up is authorized by this package.
