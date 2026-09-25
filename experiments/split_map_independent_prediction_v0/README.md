# Split Map independent prediction v0

This bounded diagnostic compares the existing joint Map response with two
independent one-field predictions on the eleven retained W0/W3 ranking-failure
contexts. Next state and consequence requests use identical authenticated task
data but separate strict schemas. The consequence request is constructed and
frozen without the next-state model output. A non-model reconciler combines the
two parsed values only after both records are durable, or abstains if either is
invalid.

Each context uses three real calls and one grounded execution. All predictions
remain detached probes; ordinary Horus controls execution, receipt creation,
Measure, authorization and Memory publication. The campaign has exactly 33
attempts with no retry, replacement or adaptive calls.

See [the preregistration](../../research/split-map-independent-prediction-v0-preregistration.md).
The full transport journal remains in a private durable archive. Public files
contain compact evidence and hashes only.

Zero-inference checks and replay:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m experiments.split_map_independent_prediction_v0.preflight --out "$NEW_PREFLIGHT_DIRECTORY"
PYTHONDONTWRITEBYTECODE=1 python -m experiments.split_map_independent_prediction_v0.run --replay "$RETAINED_LIVE_ARCHIVE" --output "$NEW_REPLAY_DIRECTORY"
```

The live command is reserved for the single registered campaign. These replay
instructions do not authorize another live campaign.
