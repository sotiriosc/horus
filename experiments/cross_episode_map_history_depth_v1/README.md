# Cross-episode Map history depth v1

A single 36-call Map-only matched study of actual empty, one-row and two-row authenticated exact-pair history after trusted episode initialization. Architecture, Map instruction, strict parser and epoch-visible projection are imported unchanged. Read the [frozen preregistration](../../research/cross-episode-map-history-depth-v1-preregistration.md).

Zero-inference tests:

```sh
python3 -m unittest experiments.cross_episode_map_history_depth_v1.test_study -v
```

For exact replay, set DEPTH_ARCHIVE to the retained private archive and REPLAY_OUTPUT to a new durable directory outside the public tree:

```sh
python3 -m experiments.cross_episode_map_history_depth_v1.run --replay "$DEPTH_ARCHIVE/live" --output "$REPLAY_OUTPUT"
```

Replay reconstructs genuine fresh and carried systems with network forbidden. The compact public result supplies all triple scores, contrasts and criteria; reproducing raw calls requires the private archive. The original campaign has a fixed reservation: never delete it or repeat live calls. Any later independent replication requires separate authorization and a new campaign identity. Explorer and Recovery are not called.
