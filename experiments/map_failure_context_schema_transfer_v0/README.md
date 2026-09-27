# Map failure-context schema transfer v0

This descriptive diagnostic reissues the exact retained J request for each of
the seven W0 ADVANCE and four W3 RETREAT Map ranking-failure contexts, then
issues a matched consequence-only S request. The existing instructions,
parsers, model and sampler are reused. Inside each pair only the required
response schema differs.

The source descriptors are derived in code from the public forensic and
retained-evidence artifacts. Each J request must reproduce its historical
SHA-256. `schedule.json` freezes all 22 request hashes before inference, and
`frozen-inputs.json` binds the complete inherited tree plus the preregistered
implementation.

Every context reconstructs the original five-event authenticated history. The
target row is transaction 2, as in the retained evidence. After durable response
and parse, a non-model control is latched; only then does ordinary execution
produce transaction 6's new original receipt. Measure, authorization and Memory
publication proceed normally. J and S are detached probes and never control
execution or publication.

See [the preregistration](../../research/map-failure-context-schema-transfer-v0-preregistration.md).
The public result is a compact record, not the full private transport archive.
Zero-inference verification:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m experiments.map_failure_context_schema_transfer_v0.preflight --out "$NEW_PREFLIGHT_DIRECTORY"
PYTHONDONTWRITEBYTECODE=1 python -m experiments.map_failure_context_schema_transfer_v0.run --replay "$RETAINED_LIVE_ARCHIVE" --output "$NEW_REPLAY_DIRECTORY"
```

Both output directories must be new, durable and outside the repository. Replay
blocks network access and must reproduce seven files and 22 Memory snapshots
byte-for-byte. The live command is reserved for the single registered campaign,
issues exactly 22 attempts and never retries. These reproduction instructions
do not authorize another live campaign.
