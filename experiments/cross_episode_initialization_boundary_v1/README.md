# Cross-episode initialization boundary v1

**A — CROSS-EPISODE INITIALIZATION BOUNDARY COMPLETE. Zero model calls.**

The new driver-only EpisodeController stages current world/framework initialization
and publishes both through one reference. Same source/event counter, epochs
1001→1002, preserved authenticated rings, no fake reset event. Primary state 3→0;
four old plus four new ordinary commits, then unchanged ninth-event FIFO eviction.
24 reset-failure controls preserve the old publication. Old v0 remains C.

Read the [36-section report](../../research/cross-episode-initialization-boundary-v1-results.md),
[preregistration](../../research/cross-episode-initialization-boundary-v1-preregistration.md),
[compact results](results.json), and [verification](verification.json).

Only the separate cross-episode Map projection adds epoch. Historical Map/Explorer
adapters, authority modules and prior result files remain unchanged. Models receive
plain projection values, never the controller/reset/source capability. No model is
invoked here. Existing bounds and two-epoch limit remain in force.

Zero-inference reproduction into persistent private directories outside Git:

```sh
python3 -m experiments.cross_episode_initialization_boundary_v1.run --output "$BOUNDARY_CAMPAIGN"
python3 -m experiments.cross_episode_initialization_boundary_v1.run --replay "$BOUNDARY_CAMPAIGN" --output "$BOUNDARY_REPLAY"
python3 -m unittest experiments.cross_episode_initialization_boundary_v1.test_boundary -v
```

Raw campaign results stay provisional until the actual historical checks in
verification.json pass; final results mark the replay/regression gates and preserve
all original metrics. Both deterministic files replay byte-identically. Six new
and 49 inherited tests passed; prior v0, ablation and R1 replays are unchanged.

Primary world is stationary. A separate representation control reuses the existing
Map-prior-v1 HoldWorld switch before the boundary; it proves old/different outcomes
retain their epochs and provenance, not nonstationary transfer.

Atomicity applies to this copy-stageable in-process simulator with trusted APIs.
It provides no physical-device/distributed reset, hostile-process isolation or
crash-durable rollback. No live cross-episode model campaign is authorized here.
