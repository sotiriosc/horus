# Map positive-evidence depth v0

Eight registered real Map calls, with one or two independently executed,
receipt-authenticated positive HOLD observations. All runtime, parser, projection
and authority mechanisms are inherited unchanged. See the
[preregistration](../../research/map-positive-evidence-depth-v0-preregistration.md).

`schedule.json` freezes descriptors and exact request SHA-256 hashes, generated
from genuine setup executions. `frozen-inputs.json` binds all parent tracked files
and the new protocol/code/registration. `preflight.py` runs zero-model-call
canary, parser, classification and durable-journal controls. Synthetic responses
are explicitly labeled and cannot be reported as model observations.

Raw prompts, responses, source receipts, snapshots and hash-chained journal are
retained in the private durable campaign archive. Public results contain compact
finite evidence; original object identity and full raw record verification
require the original archive. No archive may be placed in ephemeral storage or
inside the public worktree.

With access to the retained archive, zero-inference replay (Python 3.10+;
assertions enabled) is:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m experiments.map_positive_evidence_depth_v0.run --replay "$RETAINED_ARCHIVE" --output "$NEW_DURABLE_REPLAY_DIRECTORY"
```

Both variables must identify persistent directories; the output must not exist.
Replay reconstructs actual simulator executions and authentic receipts, and
compares seven deterministic files plus eight snapshots byte-for-byte. It blocks
network access and never runs inference. Never use `-O`. The live mode is guarded
by a durable one-campaign reservation; it is not permission for another campaign.
Model inference is limited to the single authorized campaign.
