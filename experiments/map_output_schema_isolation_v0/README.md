# Map output-schema isolation v0

Eight registered detached Map probes: unchanged joint instruction J versus S,
which retains identical outcome-prediction wording and removes next_state only
from the required answer schema. Task data and settings match. S directly reuses
the previous diagnostic's strict consequence-only parser.

See [preregistration](../../research/map-output-schema-isolation-v0-preregistration.md).
Both probes lack framework authority. Ordinary unchanged MapModel uses fixed
non-model control (1,+1) to drive the scored HOLD. Each probe is scored against
a new original post-response execution receipt, separately from control
measurement_matches. S has no next_state or joint exactness score.

`schedule.json` binds exact authenticated request hashes; `frozen-inputs.json`
binds parent files and diagnostic code/registration. Preflight checks matching,
byte-identical first/last sentences, leak canaries, probe detachment, strict
parsers, frozen decision boundaries, durability and synthetic replay with zero
model inference.

Full requests/responses, authentic setup and new scored receipts, non-model
control latches, Measure, authorization, Memory, snapshots and journals remain
in the private durable archive. Compact public evidence is not the full archive.
With access to the archive, Python 3.10+ and assertions enabled:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m experiments.map_output_schema_isolation_v0.run --replay "$RETAINED_ARCHIVE" --output "$NEW_DURABLE_REPLAY_DIRECTORY"
```

Output must be new, persistent and outside the public worktree. Replay blocks
network access, reconstructs ordinary simulator execution and receipt paths, and
requires seven data files and eight snapshots to match exactly. Do not use `-O`.
Live mode reserves one campaign and never retries an attempt. These instructions
do not authorize another live campaign or a production split/prompt adoption.
