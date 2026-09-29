# Grounded action sensitivity v0 — GROUNDING_INSENSITIVE

The preregistered 36-call matched diagnostic completed with 36 valid one-field actions, 36 signed transport attempts, and **zero diagnostic world executions**. Six grounded context fixtures were derived from 35 original protected seed receipts and replayed exactly from durable Memory. Within each matched pair, the prompt, seed, model, goal, state, action names and order, bounded history, and generation settings were identical; only the derived grounded assessments changed. The completed autonomous v0.2 campaign remains untouched and behaviorally `VALID`; v0 and v0.1 remain `INVALID`.

| Measure | Neutral N | Grounding directive G |
| --- | ---: | ---: |
| Valid action outputs | 18/18 | 18/18 |
| Choices matching the preregistered grounded preference | 9/18 | 9/18 |
| Matched swaps where **both** choices followed the changed grounded value | 0/9 | 0/9 |
| Core A/B matched swaps following value | 0/6 | 0/6 |
| Action changes when grounded values/status swapped | 0/9 | 0/9 |
| Established negative actions chosen | 6 | 6 |
| Established positive actions chosen | 3 | 3 |
| Unresolved actions chosen | 3 | 3 |
| Unseen actions chosen | 0 | 0 |
| Same action name across the three display orders | 6/6 context groups | 6/6 |
| Same display position across orders | 0/6 groups | 0/6 |

Every call selected `ADVANCE`. The 9/18 individual preference matches in each condition are the variants where `ADVANCE` happened to be the preregistered preferred action; **none** of the nine matched swaps produced a value-following change. In Pair A the model chose `ADVANCE` both when its established consequence was +1 and when it was -1 while `HOLD` became +1. In Pair B it chose `ADVANCE` both when it was established -1 and when it was 0. In Pair C it chose `ADVANCE` both when that relation was unresolved (+1→-1) and when it was established 0. The choice persisted as `ADVANCE` moved through all three positions in the available-action list. The minimal grounding-authority directive produced no observed change.

Under the frozen thresholds, the classification is **`GROUNDING_INSENSITIVE`**. This is a causal finding for the **presented matched assessments in these fixed contexts**, with the specified model, prompts, seeds, and generation settings. It does not claim the model can never use grounded evidence, nor does it rerun or reinterpret the v0.2 trajectories. The neutral and directive conditions both failed the narrower test: changing only reality-backed grounded assessments did not change the decision. No further autonomous campaign, model change, training, or mechanical policy was selected or run.

[`contexts.json`](contexts.json) contains the derived public-safe assessments and seed receipt provenance; [`contexts-manifest.json`](contexts-manifest.json) pins them before inference. [`result.json`](result.json) contains every sanitized choice, matched metric, strict parse verdict, request/output hashes, and private-artifact SHA-256 digest. [`publication-manifest.json`](publication-manifest.json) records source and archive provenance. Complete private keys, raw model calls, seed streams, and Memory databases remain locally archived at `92b7cac34e1c4d9f6c414e9d6be4a4fb577ed330`, outside the publication ancestry.
