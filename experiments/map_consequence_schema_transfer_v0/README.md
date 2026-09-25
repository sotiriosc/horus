# Map consequence-schema transfer v0

Sixteen detached Map probes on WA (W0 ADVANCE 0→1,+1) and WR (W3 RETREAT
3→2,+1). J and S reuse the previous schema-isolation instructions and parsers.
Both retain identical outcome-prediction wording; only the response schema differs.

See [preregistration](../../research/map-consequence-schema-transfer-v0-preregistration.md).
Each genuine target setup execution is followed by ordinary authenticated return
navigation. The exact-pair target history contains only the target observation.
After durable response/parse, unchanged MapModel supplies a non-model control
(WA 1,+1; WR 2,+1). Each detached probe is scored against the new original target
receipt, separately from the framework's control measurement_matches. S has no
next_state or joint exactness score. No model output obtains framework authority.

`schedule.json` freezes exact request hashes; `frozen-inputs.json` binds the parent
tree and new diagnostic code/registration. Preflight uses zero inference to check
all 16 future-answer canaries, navigation exclusion, eight matched pairs, probe
detachment, parsers, thresholds/categories, durability and exact synthetic replay.

Private durable records retain complete requests/responses, authentic target and
navigation histories, post-response receipts, controls, Measure, authorizations,
Memory, snapshots and journals. Compact public evidence is not the full archive.
With access to that archive, Python 3.10+ and assertions enabled:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m experiments.map_consequence_schema_transfer_v0.run --replay "$RETAINED_ARCHIVE" --output "$NEW_DURABLE_REPLAY_DIRECTORY"
```

Output must be new, persistent and outside the public tree. Replay blocks network
access and reproduces seven data files and sixteen snapshots exactly through
ordinary execution/receipt paths. Do not use `-O`. Live mode reserves one campaign
and never retries an attempt. These instructions do not authorize more model calls.
