# Cross-episode model transfer v0

Two independent stateless proposal probes compare actual retained authenticated history after trusted initialization with a genuinely empty fresh system. Existing architecture, parsers and projections are imported unchanged. Read the [preregistration](../../research/cross-episode-model-transfer-v0-preregistration.md) before interpreting results.

Zero-inference tests:

```sh
python3 -m unittest experiments.cross_episode_model_transfer_v0.test_study -v
```

Exact replay requires the retained private raw campaign archive. Set `TRANSFER_ARCHIVE` to its durable location and `REPLAY_OUTPUT` to a new durable directory outside this checkout:

```sh
python3 -m experiments.cross_episode_model_transfer_v0.run --replay "$TRANSFER_ARCHIVE/live" --output "$REPLAY_OUTPUT"
```

Replay forbids network access and reconstructs the ordinary authentic setup and fresh systems. Compact public results alone cannot reproduce raw model responses. They do permit inspecting every paired classification and every frozen support gate. No inference is required for replay. The original single live campaign has a fixed exclusive reservation; do not delete it or repeat calls. A future independent replication requires separate authorization and campaign identity.
