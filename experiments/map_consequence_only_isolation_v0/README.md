# Map consequence-only isolation v0

Eight registered detached forecast probes: existing joint-output instruction J
versus the user's exact consequence-only instruction C. Authentic one-row
self-loop history and all settings match; only the system instruction differs.
Neither output enters protected framework prediction or authorization.

See [preregistration](../../research/map-consequence-only-isolation-v0-preregistration.md).
`protocol.py` contains the strict diagnostic C parser and frozen consequence
thresholds. The production J parser and framework remain unchanged. Ordinary
MapModel supplies the fixed non-model (1,+1) control for both arms. Each detached
probe is scored against a new original post-response execution receipt, separately
from the control's framework measurement match. C has no next_state score.

`schedule.json` binds exact authenticated request hashes; `frozen-inputs.json`
binds the parent tree and diagnostic code/registration. `preflight.py` checks
matching, future-answer canaries, probe detachment, parser rejection, decision
boundaries, durability and synthetic replay, with zero model inference.

Full requests/responses, setup and scored receipts, ordinary control predictions,
Measure, authorizations, Memory, snapshots and journals remain in the private
durable archive. Public compact evidence is not the complete raw replay archive.
With that archive, Python 3.10+ and assertions enabled:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m experiments.map_consequence_only_isolation_v0.run --replay "$RETAINED_ARCHIVE" --output "$NEW_DURABLE_REPLAY_DIRECTORY"
```

Use a new persistent output directory outside the public worktree. Replay blocks
network access, re-executes the genuine simulator boundary, and requires seven
deterministic data files and eight snapshots to match byte for byte. Do not use
`-O`. Live mode reserves one campaign and never retries an attempt. This
reproduction description does not authorize another live campaign.
