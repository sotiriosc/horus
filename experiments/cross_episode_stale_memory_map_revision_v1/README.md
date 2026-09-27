# Cross-episode stale-Memory Map revision v1

One preregistered 144-call Map-only study using unchanged authenticated feasibility construction. Read the [frozen preregistration](../../research/cross-episode-stale-memory-map-revision-v1-preregistration.md) before the results.

Zero-inference tests:

```sh
python3 -m unittest experiments.cross_episode_stale_memory_map_revision_v1.test_study -v
```

Set REVISION_ARCHIVE to the retained private archive and REVISION_REPLAY to a new durable directory outside this public checkout:

```sh
python3 -m experiments.cross_episode_stale_memory_map_revision_v1.run --replay "$REVISION_ARCHIVE/live" --output "$REVISION_REPLAY"
```

Replay reconstructs each actual authenticated fixture and forbids sockets. Eight files and 144 system snapshots must match. Public results expose all schedules, scores, pairs, paths, latency and criteria; private raw responses are required to replay inference. Original live output and its fixed campaign reservation must never be overwritten/deleted or automatically rerun. Any separate replication requires new authorization and campaign identity. No model output executes or writes Memory.
