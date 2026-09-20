# Map temporal-relation forecast v0 results

**MAP TEMPORAL-RELATION FORECASTING BEYOND PURE RECENCY NOT ESTABLISHED**

## 1. Parent interface identity

Parent `24beb32ada2c1661ae31f067aebbe9b7b1939697` on `research/map-guided-explorer-interface-v0`; interface readiness A remains unchanged. New branch `research/map-temporal-relation-forecast-v0`. Preregistration commit `0958fc8f36ab6d2aaafe4f95c6afdec694979446` preceded all model requests.

## 2. Motivation from Map/Explorer results

Stale-Memory Map revision remains REPLICATED. Both stale-Memory Explorer revision and the explicit-mean Explorer contract remain NOT ESTABLISHED. Prior Map success is compatible with recency and other rules; this study does not reinterpret it.

## 3. Research question

Can Map forecast a seventh realized consequence from authenticated temporal order when latest observation and unordered distribution alone cannot discriminate F from P?

## 4. Reality-scoring rule

The model proposes, the strict parser validates, the ordinary framework latches the original Prediction, the external world executes, the authentic receipt records the outcome, and Measure compares. All three accuracy measures use that receipt. Registered sequence values are checked separately only to audit fixture construction.

## 5. Target state/action

State 1, underlying HOLD, epoch 1001 throughout. HOLD self-loops; only realized consequence varies. Each context starts independently with empty Memory. No reset/navigation event is used.

## 6. S process

Six authentic `+1,+1,+1,+1,+1,+1` observations; seventh registered external event yields +1.

## 7. F process

Six authentic `+1,+1,+1,-1,-1,-1` observations; seventh registered external event yields -1.

## 8. T process

Six authentic `+1,+1,+1,+1,+1,-1` observations; seventh registered external event yields +1. Transient deviation is evaluator terminology; the model receives no such label.

## 9. P process

Six authentic `+1,-1,+1,-1,+1,-1` observations; seventh registered external event yields +1. No periodicity hint is supplied.

## 10. F/P discriminator rationale

F/P each have three +1 and three -1 observations, mean zero, latest -1, length six, same state/action and IDs 1..6. Order differs, as does the next actual outcome. Correct differentiation can exclude a pure latest-only or unordered-signature-only explanation on these inputs, but does not identify the model mechanism.

## 11. Authenticated history construction

576 setup events passed ordinary execution/receipt/Measure/authorization/publication. No Memory record or receipt was injected. Exact-pair projections are rebuilt mechanically from protected Memory, with original receipt identities verified against actual external executions.

## 12. No-future-leak audit

All 96 preflight and live pre-call snapshots have exactly six events and six records. World index reads are 0..5 only. A guard rejects event seven until a parsed Prediction is latched and fsynced. Model-visible payload is whitelisted and excludes all arm/source/future metadata. A deterministic control changes only event seven: prompt stays identical while receipt scoring changes. The fixture and driver are trusted same-process code, not hostile-code isolation.

## 13. Map projection

Only `state`, `target_action`, `VERIFIED_CHRONOLOGICAL_HISTORY`. Each row has exactly `epoch`, `transaction_id`, `surface_action`, `next_state`, `consequence`. Epoch 1001, IDs 1..6, one opaque HOLD alias, chronological order. No aggregation, summaries, process labels or future hint.

## 14. Prompt/parser

The established explicit Map system is reproduced exactly in the [preregistration](map-temporal-relation-forecast-v0-preregistration.md). The historical strict parser and MapProposalAdapter are unchanged. Exactly two finite integer fields; no bool/float/string/extra/duplicate field, prose, coercion or extraction. Malformed output is invalid with no replacement forecast/event and no retry.

## 15. Model/config

dolphin-mixtral:latest; Ollama 0.1.16; GGUF 47B Q4_0. All five manifest blobs were hashed in full before inference. Sampler .2 temperature, .9 top_p, top_k 40, num_ctx 2048, repeat_penalty 1.1, num_predict 32. Stateless requests; no returned context, chat history or weight updates.

## 16. Mappings/seeds

O1 K1/K2/K3 and O2 Q7/M4/Z2; six complete mappings repeated twice. j=0..11, mapping j mod 6, seed 95001+j matched across all four arms and both families. Underlying HOLD remains the target; semantic action names are absent from the payload.

## 17. Exact call schedule

96 entries and exact request hashes were committed before inference in [schedule.json](../experiments/map_temporal_relation_forecast_v0/schedule.json). j ascending; family order alternates by parity; rotate S,F,T,P left by j mod 4; reverse that rotated order for the second family position. No reordering, retry, replacement or extension.

## 18. Validity

96/96 real Map requests completed; 96/96 valid. Explorer model calls 0; model Recovery calls 0. Measured seventh events 96. Exact parsed outcomes for every call appear in [results.json](../experiments/map_temporal_relation_forecast_v0/results.json).

## 19. S results

| Family | Calls | Valid | Exact | State correct | Consequence correct | +1 | -1 | 0 | Invalid |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| O1 | 12 | 12 | 11 | 12 | 11 | 11 | 0 | 1 | 0 |
| O2 | 12 | 12 | 12 | 12 | 12 | 12 | 0 | 0 | 0 |

## 20. F results

| Family | Calls | Valid | Exact | State correct | Consequence correct | +1 | -1 | 0 | Invalid |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| O1 | 12 | 12 | 12 | 12 | 12 | 0 | 12 | 0 | 0 |
| O2 | 12 | 12 | 12 | 12 | 12 | 0 | 12 | 0 | 0 |

## 21. T results

| Family | Calls | Valid | Exact | State correct | Consequence correct | +1 | -1 | 0 | Invalid |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| O1 | 12 | 12 | 2 | 12 | 2 | 2 | 9 | 1 | 0 |
| O2 | 12 | 12 | 0 | 12 | 0 | 0 | 12 | 0 | 0 |

## 22. P results

| Family | Calls | Valid | Exact | State correct | Consequence correct | +1 | -1 | 0 | Invalid |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| O1 | 12 | 12 | 0 | 12 | 0 | 0 | 12 | 0 | 0 |
| O2 | 12 | 12 | 0 | 12 | 0 | 0 | 12 | 0 | 0 |

## 23. O1 F/P paired discriminator

F history: `+1,+1,+1,-1,-1,-1`. P history: `+1,-1,+1,-1,+1,-1`. Predictions/receipts below are `(next_state, consequence)`. Mapping index identifies the complete mapping in the frozen schedule and compact results.

| j | Mapping | Seed | HOLD alias | F prediction | F receipt | P prediction | P receipt | Category | Same consequence | Latest for both |
|---:|---:|---:|---|---|---|---|---|---|---|---|
| 0 | 0 | 95001 | K2 | (1, -1) | (1, -1) | (1, -1) | (1, +1) | F_ONLY_CORRECT | True | True |
| 1 | 1 | 95002 | K3 | (1, -1) | (1, -1) | (1, -1) | (1, +1) | F_ONLY_CORRECT | True | True |
| 2 | 2 | 95003 | K1 | (1, -1) | (1, -1) | (1, -1) | (1, +1) | F_ONLY_CORRECT | True | True |
| 3 | 3 | 95004 | K1 | (1, -1) | (1, -1) | (1, -1) | (1, +1) | F_ONLY_CORRECT | True | True |
| 4 | 4 | 95005 | K3 | (1, -1) | (1, -1) | (1, -1) | (1, +1) | F_ONLY_CORRECT | True | True |
| 5 | 5 | 95006 | K2 | (1, -1) | (1, -1) | (1, -1) | (1, +1) | F_ONLY_CORRECT | True | True |
| 6 | 0 | 95007 | K2 | (1, -1) | (1, -1) | (1, -1) | (1, +1) | F_ONLY_CORRECT | True | True |
| 7 | 1 | 95008 | K3 | (1, -1) | (1, -1) | (1, -1) | (1, +1) | F_ONLY_CORRECT | True | True |
| 8 | 2 | 95009 | K1 | (1, -1) | (1, -1) | (1, -1) | (1, +1) | F_ONLY_CORRECT | True | True |
| 9 | 3 | 95010 | K1 | (1, -1) | (1, -1) | (1, -1) | (1, +1) | F_ONLY_CORRECT | True | True |
| 10 | 4 | 95011 | K3 | (1, -1) | (1, -1) | (1, -1) | (1, +1) | F_ONLY_CORRECT | True | True |
| 11 | 5 | 95012 | K2 | (1, -1) | (1, -1) | (1, -1) | (1, +1) | F_ONLY_CORRECT | True | True |

Counts: `{"BOTH_CORRECT": 0, "BOTH_WRONG": 0, "F_ONLY_CORRECT": 12, "P_ONLY_CORRECT": 0}`.

## 24. O2 F/P paired discriminator

F history: `+1,+1,+1,-1,-1,-1`. P history: `+1,-1,+1,-1,+1,-1`. Predictions/receipts below are `(next_state, consequence)`. Mapping index identifies the complete mapping in the frozen schedule and compact results.

| j | Mapping | Seed | HOLD alias | F prediction | F receipt | P prediction | P receipt | Category | Same consequence | Latest for both |
|---:|---:|---:|---|---|---|---|---|---|---|---|
| 0 | 0 | 95001 | M4 | (1, -1) | (1, -1) | (1, -1) | (1, +1) | F_ONLY_CORRECT | True | True |
| 1 | 1 | 95002 | Z2 | (1, -1) | (1, -1) | (1, -1) | (1, +1) | F_ONLY_CORRECT | True | True |
| 2 | 2 | 95003 | Q7 | (1, -1) | (1, -1) | (1, -1) | (1, +1) | F_ONLY_CORRECT | True | True |
| 3 | 3 | 95004 | Q7 | (1, -1) | (1, -1) | (1, -1) | (1, +1) | F_ONLY_CORRECT | True | True |
| 4 | 4 | 95005 | Z2 | (1, -1) | (1, -1) | (1, -1) | (1, +1) | F_ONLY_CORRECT | True | True |
| 5 | 5 | 95006 | M4 | (1, -1) | (1, -1) | (1, -1) | (1, +1) | F_ONLY_CORRECT | True | True |
| 6 | 0 | 95007 | M4 | (1, -1) | (1, -1) | (1, -1) | (1, +1) | F_ONLY_CORRECT | True | True |
| 7 | 1 | 95008 | Z2 | (1, -1) | (1, -1) | (1, -1) | (1, +1) | F_ONLY_CORRECT | True | True |
| 8 | 2 | 95009 | Q7 | (1, -1) | (1, -1) | (1, -1) | (1, +1) | F_ONLY_CORRECT | True | True |
| 9 | 3 | 95010 | Q7 | (1, -1) | (1, -1) | (1, -1) | (1, +1) | F_ONLY_CORRECT | True | True |
| 10 | 4 | 95011 | Z2 | (1, -1) | (1, -1) | (1, -1) | (1, +1) | F_ONLY_CORRECT | True | True |
| 11 | 5 | 95012 | M4 | (1, -1) | (1, -1) | (1, -1) | (1, +1) | F_ONLY_CORRECT | True | True |

Counts: `{"BOTH_CORRECT": 0, "BOTH_WRONG": 0, "F_ONLY_CORRECT": 12, "P_ONLY_CORRECT": 0}`.

## 25. Latest-observation baseline

Latest predicts +1 for S and -1 for F/T/P. Against observed seventh receipts, it matches 48/96. The target remains the receipt. T/P latest-value forecasts and their frozen maximum-two gates are explicit below.

## 26. Other descriptive baselines

F/P share histogram {+1:3,-1:3} and mean zero. No arbitrary histogram-to-action rule is invented. Nonzero mean sign predicts +1 for S/T, and is undefined for F/P at zero; it matches 48/48 receipt-scored defined cases. These descriptive comparators never select the model target or repair a forecast.

## 27. Next-state component

96/96 next-state matches. Invalid responses count as unsuccessful. All actually executed HOLDs remain in state 1; exact accuracy requires state and consequence to match.

## 28. Consequence component

49/96 consequence matches; 49/96 exact matches. These pooled totals are descriptive only; each family must independently pass every gate.

## 29. Native Recovery/Measure behavior

Measured event-seven mismatches: 47; native state Recovery calls: 0; native measurement Recovery calls: 0; authorization failures: 0. Setup mismatch/state-Recovery/measurement-Recovery counts are 168/0/0. A forecast mismatch is not a corrupted measurement. Wrong original predictions remain in the evidence.

## 30. Authentic receipt scoring

96 measured authentic original receipts were traced through actual execution, source identity/event ID, epoch/transaction, package, pair and Memory. Every score was independently recomputed from the receipt. Original latched predictions, receipts and all six earlier records remain unchanged. Memory/pair/package lengths remain within 8 with zero eviction.

## 31. O1 frozen criterion

| Frozen criterion | Passed |
|---|---|
| FP_both_correct_at_least_8 | False |
| F_exact_at_least_9 | True |
| P_exact_at_least_9 | False |
| P_latest_minus1_at_most_2 | False |
| S_exact_at_least_10 | True |
| T_exact_at_least_9 | False |
| T_latest_minus1_at_most_2 | False |
| all_family_calls_complete | True |
| authentic_scored_receipts | True |
| every_arm_valid_at_least_11 | True |
| exact_replay | True |
| integrity | True |
| no_future_leakage | True |

**MAP TEMPORAL-RELATION FORECASTING BEYOND PURE RECENCY NOT ESTABLISHED**.

## 32. O2 frozen criterion

| Frozen criterion | Passed |
|---|---|
| FP_both_correct_at_least_8 | False |
| F_exact_at_least_9 | True |
| P_exact_at_least_9 | False |
| P_latest_minus1_at_most_2 | False |
| S_exact_at_least_10 | True |
| T_exact_at_least_9 | False |
| T_latest_minus1_at_most_2 | False |
| all_family_calls_complete | True |
| authentic_scored_receipts | True |
| every_arm_valid_at_least_11 | True |
| exact_replay | True |
| integrity | True |
| no_future_leakage | True |

**MAP TEMPORAL-RELATION FORECASTING BEYOND PURE RECENCY NOT ESTABLISHED**.

## 33. Overall decision

**MAP TEMPORAL-RELATION FORECASTING BEYOND PURE RECENCY NOT ESTABLISHED**. No pooling, weakened thresholds or rescue by strong performance on another arm.

## 34. Provenance/history preservation

Six old observations remain in order after the seventh event. Consequence contradictions are new authenticated evidence, not automatic integrity failures. No action ban, negative-record rewriting, alternative authorization path or model authority was introduced.

## 35. Exact replay

All 96 recorded responses were replayed with sockets forbidden and zero inference. Reconstructed histories, exact requests, parser results, latched predictions, actual events, receipts, Measure/Recovery, authorization and scoring reproduced seven deterministic files and 96 snapshots byte-for-byte. Finalized gates/results also match. The first independent audit attempt found a validator reserialization error: sorted JSON key order was incorrectly used to reconstruct request bytes. It was corrected to hash the retained exact request bytes and verify their parsed payload separately; the initial validator and explanation are preserved privately. No scientific inputs, outputs or calls changed. Original live metrics remain provisional in the private archive; replay proof is added separately.

## 36. Historical preservation

82 tests and 11 historical zero-inference replays passed. 607 inherited substantive files are byte-identical. Earlier private archive checksums and every prior ref, main and tags remain unchanged. Interface A, both Explorer negatives, Map REPLICATED, feasibility A, depth SUPPORTED, transfer mixed/NOT ESTABLISHED, initialization A, ablation SUPPORTED, R1 A and grounding/UNKNOWN/contradiction/representation results are preserved. See [verification.json](../experiments/map_temporal_relation_forecast_v0/verification.json).

## 37. Limitations

Small, fixed deterministic seven-event fixtures, one pinned model/sampler, matched seed/alias repetitions rather than a broad population estimate. Finite history does not uniquely specify the seventh outcome. Same-count discriminator tests behavior, not an internal algorithm. Trusted local fixture/source/driver do not provide cryptographic provenance or adversarial process isolation. No claim of causal discovery, true-law learning, Bayesian inference, general noise detection/world models, persistent or weight learning, RL, AGI or RSI.

## 38. Narrowest defensible conclusion

The complete prospective temporal-relation forecasting criterion is NOT ESTABLISHED in either family. F/P both-correct is 0/12 in O1 and 0/12 in O2: all 24 pairs received the same -1 consequence forecast for both histories. This behavior on the critical discriminator remains compatible with a latest-observation-only explanation; it does not establish that recency was the actual internal mechanism. Transient exact accuracy is 2/12 in O1 and 0/12 in O2. Stable and persistent-flip successes do not rescue the failed gates.

## 39. Recommendation

Retain the failed gates and per-seed F/P evidence before choosing any next study. Do not infer temporal competence from the earlier stale-Memory positive result or automatically launch the Map-to-Explorer pipeline. Stop here: no additional calls, prompt tuning, thresholds, temporal arms, optimization, main/tag edits or push.
