# Composition Map Memory ablation v0 — frozen preregistration

Parent: `bffc9c5aa2408770038ecaf7fb076757e991cd01`, R1 **A — MULTI-ROLE PROPOSAL COMPOSITION INTEGRITY PASS**.
Campaign: `HORUS_COMPOSITION_MAP_MEMORY_ABLATION_V0`. One separately recorded study.
R1 remains unchanged; original interrupted v2 remains C. No pooled responses.

## Question and selection

When everything else is held fixed, does giving Map access to authenticated
experience change and improve its prediction? R1 depth-associated accuracy and
wrong→exact sequential changes motivate a prospective input intervention.

Use all 42 unique R1 Map calls with nonempty same-state/action chronological history,
in original call order (episode then decision). Select solely by role and nonempty
history, never original prediction correctness. The complete public context identities,
seeds, original depths, source/receipt/request hashes and order are frozen in
`experiments/composition_map_memory_ablation_v0/contexts.json` before inference.
Raw original snapshots, authenticated records, receipts and exact paired requests
remain in the private durable archive. Depths: 19 at 1, six at 2, 17 at 3+.

Every source snapshot must equal the call's pre-execution Memory and step snapshot;
every record must link to an earlier committed authenticated receipt in that episode.
The original subsequent receipt must agree between the original journal, step and
verified provenance record. Use that stationary-world realized outcome for scoring.
No hidden oracle is queried; the evaluator receipt is never added to the prompt.

## Sole intervention

H uses the byte-identical original R1 Map user payload, mechanically reconstructed
from authenticated Memory through the unchanged binding. W changes only
`VERIFIED_CHRONOLOGICAL_HISTORY` to `[]`. Within-pair state, target opaque alias,
mapping, system, model, seed, sampler and serialization match. Verify every H
payload and complete serialized request against R1; failure stops before inference.
Retain exact request hashes and privately retain both request byte strings.

**WITHHELD != UNKNOWN.** W deliberately hides existing evidence from Map. It does
not represent an untried pair, empty system Memory or forgetting. No observation,
absence marker, receipt or protected record is written or deleted. UNKNOWN IS NOT
MEMORY and all historical authority boundaries remain unchanged. The common system
instruction refers to “outcomes shown”; it does not assert that omitted outcomes do
not exist. No extra condition label is inserted in either prompt.

## Exact instruction, parser and runtime

Use the frozen R1 Map instruction:

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object with exactly two fields: next_state must be an integer in {0,1,2,3}, and consequence must be an integer in {-1,0,1}. Do not include any other fields or explanation.

Import the unchanged strict Map parser. Duplicate/extra/missing fields, booleans,
nonintegral numbers, out-of-domain values and extraneous text are invalid. No repair,
constrained decoding, retries or fallback. Invalid responses count as wrong on all
accuracy measures, with validity separately reported.

Pinned dolphin-mixtral:latest, Ollama 0.1.16, GGUF 47B Q4_0; verify the full manifest
and all five blobs before inference. Manifest SHA256:
`4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`.
Weights SHA256: `bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3`.
Sampler: temperature .2, top_p .9, top_k 40, num_predict 32, num_ctx 2048,
repeat_penalty 1.1. Reuse the original R1 Map seed for both requests of each pair.
Requests are stateless; no response or previous context is sent with another request.

## Frozen schedule and durable evidence

Exactly 84 real calls = 42 contexts × H/W. Even zero-based context indices: H then W;
odd: W then H. No adaptation, new seeds, extra contexts, replacement calls or extension.
No Explorer, Recovery, world execution, new receipts, Memory commits or weight changes.

Create the durable private campaign reservation before live activity. Refuse an
existing reservation/output; no automatic restart. Fsync a hash-chained request
intent before HTTP, response before parsing, parsed/scored result before progression,
and atomically save call counts/journal head. Call identity includes campaign,
context index, condition and Map role. A transport failure is possibly issued and
stops without reissue. Invalid text is retained/scored; it is not retried. Durability
and interruption tests make zero model calls. R1 source hashes are checked before
and after. This journal has request boundaries only: no new protected transactions.

## Frozen scoring and primary criterion

Score valid response, exact pair, next_state and consequence independently against
the preserved original authentic receipt. For each endpoint report favorable
(H correct/W wrong), reverse (H wrong/W correct), both correct, both wrong.

**AUTHENTIC-HISTORY MAP EFFECT SUPPORTED iff all ten conditions hold:**

1. All 84 registered calls complete.
2. H valid >= 40/42.
3. W valid >= 40/42.
4. Exact favorable minus reverse discordances >= 10 pairs.
5. Exact favorable > reverse separately in O1.
6. Exact favorable > reverse separately in O2.
7. Overall H exact accuracy > W exact accuracy.
8. No historical R1 Memory/receipt data is modified.
9. Parser/model/sampler integrity passes.
10. Exact recorded-response replay passes.

Otherwise **AUTHENTIC-HISTORY MAP EFFECT NOT ESTABLISHED**. Raw results remain
provisional until the actual replay gate passes. Finalization cannot change thresholds.
No significance or depth-specific success threshold is introduced.

## Descriptive breakdowns

Report original H depths 1, 2, 3+; O1/O2; state, underlying action, opaque token.
Report state, consequence and exact-pair discordance separately. Also report order
strata to expose possible order sensitivity without an additional success criterion.
Classify paired valid predictions as identical, state-only change, consequence-only
change or both changed. Invalid prediction cases are reported separately, never
silently treated as valid comparisons. Direction is explicitly **W→H visibility**:
wrong→exact, exact→wrong, wrong→different wrong, exact→same exact, and unchanged
wrong predictions as a separate exhaustive residual category.

## Replay, preservation and stopping

Replay every recorded response with zero inference; reconstruct source contexts and
request identities, parse, receipt linkage and score. Require eight registered files
byte-identical: contexts.json, requests.json, model-calls.jsonl, pairs.json,
metrics.json, journal.jsonl, campaign-state.json, metadata.json. Final compact
classification must regenerate identically from the same actual verification evidence.

Run R1's exact archived-response replay, schema-contract replay and unchanged v2
UNKNOWN tests. Verify original interrupted C, Map established-prior v1 and every
other inherited substantive file remain byte-identical. Do not rerun unrelated
live campaigns. Preserve main, tags and prior branches; do not push.

The 42 pairs are clustered within the R1 episode trajectories, not independent
world samples; they cover the pairs actually selected in R1. Same seeds do not
make the different prompts deterministically equivalent or reproduce R1 responses.
The fixed stationary evaluator and single model/representation constrain scope.
A positive result supports an effect of authenticated-information visibility on
Map proposals under this paired prompt intervention. It does not identify an
internal belief mechanism, weight/persistent learning, causal world-model learning,
RL, AGI or RSI. Do not infer intrinsic opaque-token causality.

Stop after this study, replay, preservation and report. Persistent cross-episode
Memory would require a separate research decision; do not start it automatically.
