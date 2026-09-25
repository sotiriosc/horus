# Cross-episode stale-Memory Explorer revision v1

Read the [frozen preregistration](../../research/cross-episode-stale-memory-explorer-revision-v1-preregistration.md). One 144-call Explorer-only study; independently reconstructed authenticated histories, strict inherited parser and no measured action execution.

Zero-inference checks:

```sh
python3 -m unittest experiments.cross_episode_stale_memory_explorer_revision_v1.test_study -v
```

Set EXPLORER_ARCHIVE to the retained private archive and EXPLORER_REPLAY to a new durable directory outside the public checkout:

```sh
python3 -m experiments.cross_episode_stale_memory_explorer_revision_v1.run --replay "$EXPLORER_ARCHIVE/live" --output "$EXPLORER_REPLAY"
```

Replay forbids sockets and reconstructs all authentic fixtures. Eight files and 144 snapshots must match. Compact public results contain all per-schedule parsed outcomes, paths, pairs, latency and frozen gates. Original private raw outputs are required for replay. Preserve the live archive and fixed campaign reservation; never automatically reissue. A separate replication requires explicit authorization and a new campaign identity.
