# Cross-episode authenticated Memory boundary v0

**C — NOT ESTABLISHED. Zero model calls.** Existing start_epoch retains complete
history and restarts transaction IDs, but preserves external/current state. Fresh
construction initializes at zero but loses history. No supported operation combines
a fresh registered start with retained authenticated provenance. Core unchanged.

Read the [32-section report](../../research/cross-episode-authenticated-memory-boundary-v0-results.md),
[preregistration](../../research/cross-episode-authenticated-memory-boundary-v0-preregistration.md),
[compact results](results.json) and [actual verification](verification.json).

The limited same-source 1001→1002 fixture completes four plus four authenticated
commits, then a ninth with unchanged FIFO eviction. It naturally returns to zero;
that is explicitly insufficient evidence of an independent state reset. Nonzero
state persists through the epoch transition. Four invalid boundary requests and
four receipt/provenance attacks reject safely. A separate fresh-source diagnostic
shows why partial keys cannot be naively merged across restarted lifetimes.

All new executed fixtures use the stationary world. A read-only contradiction
control uses preserved authenticated Map-prior setup records; it does not relabel
epochs or create a new cross-epoch contradiction. Detailed evidence stays private.

Zero-inference reproduction with retained historical setup evidence:

```sh
python3 -m experiments.cross_episode_authenticated_memory_boundary_v0.run --contradiction-source "$PRIOR_MAP_SETUP" --output "$BOUNDARY_DIAGNOSTIC"
python3 -m experiments.cross_episode_authenticated_memory_boundary_v0.run --contradiction-source "$PRIOR_MAP_SETUP" --replay "$BOUNDARY_DIAGNOSTIC" --output "$BOUNDARY_REPLAY"
python3 -m unittest experiments.cross_episode_authenticated_memory_boundary_v0.test_boundary -v
```

The setup source is the preserved Map established-prior v1 `setup.jsonl`; its full
hash is frozen in frozen-inputs.json. The diagnostic imports no model transport
and blocks socket creation. Exact replay requires results.json and details.json
byte-identical. Final public results keep C and mark replay/historical gates only
after the actual checks in verification.json. Frozen raw provisional evidence stays
unchanged. Inherited core/results and R1/ablation archives remain intact.

No Ollama, new model requests, conversational persistence, core repair, push or
automatic follow-up campaign. A separate boundary-design decision is required.
