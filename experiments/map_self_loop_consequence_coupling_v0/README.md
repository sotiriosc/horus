# Map self-loop / consequence coupling v0

Eight preregistered real Map calls; one authenticated target observation in both
conditions. The moving external fixture changes only state-1 HOLD next_state to
2 and uses unchanged RETREAT to return to state 1. Framework architecture,
parser, projections, Map instruction and authority remain unchanged.

See [preregistration](../../research/map-self-loop-consequence-coupling-v0-preregistration.md).
`schedule.json` binds exact authenticated request hashes; `frozen-inputs.json`
binds all parent tracked files and the new protocol/code/registration. Paired
requests must differ by exactly the one historical next_state digit before any
model inference. Zero-model preflight also verifies relation scope, canaries,
parser rejection, decision boundaries, durability and synthetic exact replay.

Full raw requests/responses, setup/navigation events, prediction latches,
original receipts, Measure, authorization, Memory, snapshots and hash-chained
journals are retained in the private durable archive. Public results contain
compact finite evidence. Access to that archive permits exact zero-inference
replay with Python 3.10+ and assertions enabled:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m experiments.map_self_loop_consequence_coupling_v0.run --replay "$RETAINED_ARCHIVE" --output "$NEW_DURABLE_REPLAY_DIRECTORY"
```

The output must be new, persistent and outside the public worktree. Replay
blocks network access, reconstructs actual simulator execution/receipt paths and
requires seven deterministic files and eight snapshots to match exactly. Do not
use `-O`. Live mode has a one-campaign reservation; this documentation does not
authorize another campaign. Never retry or replace a recorded attempt.
