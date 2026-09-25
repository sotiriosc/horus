# Composition Map Memory ablation v0 — results

**AUTHENTIC-HISTORY MAP EFFECT SUPPORTED**

One fixed 84-call Map-only paired input intervention. All results below come only from this study; original R1 responses were not reused as new H responses.

## 1. Parent R1 identity

Parent `bffc9c5aa2408770038ecaf7fb076757e991cd01`, branch `research/model-proposal-role-composition-v2-replacement-r1`; **A — MULTI-ROLE PROPOSAL COMPOSITION INTEGRITY PASS** remains unchanged. New branch: `research/composition-map-memory-ablation-v0`. Campaign: `HORUS_COMPOSITION_MAP_MEMORY_ABLATION_V0`. Original interrupted v2 remains C / live evidence unavailable.

## 2. Exact research question

When everything else is held fixed, does giving Map access to authenticated experience actually change and improve its prediction? The causal variable is **information visibility in the model input**.

## 3. Why this follows composition

R1 observed exact accuracy 3/26 at depth 0, 12/19 at depth 1 and 23/23 at depth 2+, with later wrong→exact changes. Those were sequential associations. This study prospectively varies history visibility on matched preserved contexts. It does not execute or rerun composition.

## 4. 42 frozen contexts

The complete [context list](../experiments/composition_map_memory_ablation_v0/contexts.json) was committed before inference in `95f03ac65012ba847e65c99396bbfd5d86f5d706` with the [preregistration](composition-map-memory-ablation-v0-preregistration.md). Selection: every R1 Map call whose actual same-pair history was nonempty, once each, ordered by original call order. No selection on prediction correctness. Exactly 42 unique contexts; 19 at depth 1, six at depth 2, 17 at depth 3+.

| Stratum | Pairs | H valid | W valid | H exact | W exact | Favorable | Reverse | Net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| O1 | 19 | 19 | 19 | 14 | 3 | 11 | 0 | 11 |
| O2 | 23 | 23 | 23 | 19 | 8 | 11 | 0 | 11 |


## 5. Preserved Memory and receipt evidence

Each exact pre-execution snapshot matches the original call, step and hashed source snapshot. Each authorized prior observation links to an earlier committed authenticated receipt in the same episode. Each evaluator receipt matches the subsequent R1 step, durable receipt journal and verified full-binding provenance. Source IDs, snapshots, full histories and evaluator receipts are retained privately. Public context descriptors retain hashes and source identities. This relies on preserved R1 authentication and its original external-source trust boundary; it does not independently observe a new world event.

## 6. H/W intervention

H reconstructs the exact original history-visible Map request. W replaces only `VERIFIED_CHRONOLOGICAL_HISTORY` with `[]`. Both receive the same state, target alias, system instruction, original seed, model and sampler. The underlying mapping is held fixed. Neither prompt receives the scoring receipt.

## 7. WITHHELD != UNKNOWN

W is an experimental omission of real existing authenticated history from the model input. It is not untried, empty system Memory, forgetting or an absence event. R1 Memory remains intact. No `[]` or UNTRIED marker was written to protected state. UNKNOWN IS NOT MEMORY remains unchanged.

## 8. Exact Map instruction and parser

The exact R1 explicit Map instruction, also frozen in the preregistration, is:

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object with exactly two fields: next_state must be an integer in {0,1,2,3}, and consequence must be an integer in {-1,0,1}. Do not include any other fields or explanation.

The unchanged strict parser requires precisely integer `next_state` in {0,1,2,3} and integer `consequence` in {-1,0,1}, rejects extra/duplicate fields and malformed text, and does not repair responses. Formatting validity and outcome accuracy are scored separately.

## 9. Model and configuration

dolphin-mixtral:latest; Ollama 0.1.16; GGUF 47B Q4_0. Complete manifest and all five model blobs were rehashed before inference and match R1, including the 26,441,544,128-byte weight file. Manifest SHA256 `4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`; weights SHA256 `bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3`. Temperature .2, top_p .9, top_k 40, num_predict 32, num_ctx 2048, repeat_penalty 1.1. Runtime version, model digest, template, parameter size and quantization were checked before generation. Requests were stateless; weights unchanged.

## 10. 84-call schedule

42 contexts × two requests, exactly 84 complete real calls. Original R1 Map seed reused within each H/W pair. Even context index: H then W; odd: W then H. Exactly 21 H-first and 21 W-first pairs. No new seeds, retries, replacements or additional contexts. No Explorer/Recovery calls.

| Stratum | Pairs | H valid | W valid | H exact | W exact | Favorable | Reverse | Net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| H_first | 21 | 21 | 21 | 17 | 4 | 13 | 0 | 13 |
| W_first | 21 | 21 | 21 | 16 | 7 | 9 | 0 | 9 |


## 11. H request identity

42/42 H user payloads and full serialized request JSON reconstruct byte-for-byte against R1 request-intent records. New H responses are new draws; they need not match old R1 responses. Context reconstruction was rerun in exact recorded-response replay.

## 12. W-only history difference

42/42 paired user payloads differ only in `VERIFIED_CHRONOLOGICAL_HISTORY`; the complete requests differ only in prompt bytes corresponding to that field. All paired request hashes were committed before inference. No condition label, hidden outcome, changed system text or extra instruction was inserted.

## 13. Validity

H: **42/42 valid**. W: **42/42 valid**. Invalid predictions, if any, count as wrong for every accuracy endpoint. There were 0 invalid H and 0 invalid W outputs; no retries or parser relaxation.

## 14. H exact accuracy

**33/42 (78.6%)** exactly matched both next_state and consequence from the original authentic scoring receipt.

## 15. W exact accuracy

**11/42 (26.2%)** exactly matched both fields. H minus W: **22 pairs / 52.4 percentage points**.

## 16. Favorable and reverse discordances

Exact outcome: favorable (H exact/W wrong) **22**; reverse (H wrong/W exact) **0**; both exact **11**; both wrong **9**. Net favorable minus reverse **22**; frozen minimum **10**.

| Stratum | Pairs | H valid | W valid | H exact | W exact | Favorable | Reverse | Net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Overall | 42 | 42 | 42 | 33 | 11 | 22 | 0 | 22 |


## 17. O1 matched result

| Stratum | Pairs | H valid | W valid | H exact | W exact | Favorable | Reverse | Net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| O1 | 19 | 19 | 19 | 14 | 3 | 11 | 0 | 11 |


## 18. O2 matched result

| Stratum | Pairs | H valid | W valid | H exact | W exact | Favorable | Reverse | Net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| O2 | 23 | 23 | 23 | 19 | 8 | 11 | 0 | 11 |


## 19. Original history-depth breakdown

Strata use the original H history depth even for W. No depth-specific success threshold.

| Stratum | Pairs | H valid | W valid | H exact | W exact | Favorable | Reverse | Net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 19 | 19 | 19 | 10 | 3 | 7 | 0 | 7 |
| 2 | 6 | 6 | 6 | 6 | 1 | 5 | 0 | 5 |
| 3+ | 17 | 17 | 17 | 17 | 7 | 10 | 0 | 10 |


## 20. Next-state effect

H correct **37/42**; W correct **20/42**. Favorable **18**, reverse **1**, both correct **19**, both wrong **4**, net **17**. Compact results also provide this endpoint within every family/depth/state/action/token stratum.

## 21. Consequence effect

H correct **36/42**; W correct **21/42**. Favorable **15**, reverse **0**, both correct **21**, both wrong **6**, net **15**. Compact results also provide this endpoint within every family/depth/state/action/token stratum.

## 22. Output-change classes

| H/W prediction difference | Pairs |
|---|---:|
| identical | 15 |
| state_changed_only | 9 |
| consequence_changed_only | 6 |
| both_changed | 12 |
| invalid_prediction_present | 0 |

Direction below means **withheld W → visible H**, not a chronological learning event.

| Direction | Pairs |
|---|---:|
| wrong_to_exact | 22 |
| exact_to_wrong | 0 |
| wrong_to_different_wrong | 5 |
| exact_to_same_exact | 11 |
| wrong_to_same_wrong | 4 |


## 23. State, action and token breakdown

Descriptive only; these selected contexts are not balanced across states/actions/tokens. No intrinsic token-causality claim. The selected R1 contexts contain K1, M4 and Q7; K2, K3 and Z2 have no eligible contexts and are not tested here.

| Stratum | Pairs | H valid | W valid | H exact | W exact | Favorable | Reverse | Net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 27 | 27 | 27 | 24 | 9 | 15 | 0 | 15 |
| 1 | 8 | 8 | 8 | 6 | 0 | 6 | 0 | 6 |
| 2 | 4 | 4 | 4 | 1 | 0 | 1 | 0 | 1 |
| 3 | 3 | 3 | 3 | 2 | 2 | 0 | 0 | 0 |

| Stratum | Pairs | H valid | W valid | H exact | W exact | Favorable | Reverse | Net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ADVANCE | 13 | 13 | 13 | 9 | 2 | 7 | 0 | 7 |
| HOLD | 21 | 21 | 21 | 20 | 9 | 11 | 0 | 11 |
| RETREAT | 8 | 8 | 8 | 4 | 0 | 4 | 0 | 4 |

| Stratum | Pairs | H valid | W valid | H exact | W exact | Favorable | Reverse | Net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| K1 | 19 | 19 | 19 | 14 | 3 | 11 | 0 | 11 |
| M4 | 19 | 19 | 19 | 17 | 8 | 9 | 0 | 9 |
| Q7 | 4 | 4 | 4 | 2 | 0 | 2 | 0 | 2 |


## 24. Primary criterion

| Frozen criterion | Result |
|---|---|
| H_exact_exceeds_W | PASS |
| H_valid_at_least_40 | PASS |
| O1_favorable_exceeds_reverse | PASS |
| O2_favorable_exceeds_reverse | PASS |
| W_valid_at_least_40 | PASS |
| all_84_complete | PASS |
| exact_recorded_response_replay | PASS |
| favorable_minus_reverse_at_least_10 | PASS |
| historical_memory_receipts_unchanged | PASS |
| parser_model_sampler_integrity | PASS |

**AUTHENTIC-HISTORY MAP EFFECT SUPPORTED**. All ten frozen conditions are reported, including any failed condition. No threshold changed after inference.

## 25. Memory preservation

Zero experimental world executions, zero new receipts, zero Memory events, zero Explorer calls and zero Recovery calls. All source evidence files match their frozen hashes. The complete original R1 private archive passed **288** saved checksum comparisons. Model requests had no execution/authorization capability. Private scoring read preserved receipts only.

## 26. Exact replay

All 84 recorded responses replayed with **zero inference**. All eight registered files reconstructed byte-identically: context snapshots, exact requests, model calls, paired scores, raw metrics, journal, atomic campaign state and model metadata. Final compact results regenerated identically from both live and replay files using the same actual assurance. Journal: **336 records**, 84 unique completed call IDs, zero ambiguous calls. Request intent was fsynced before generation; response before parsing. Raw provisional metrics remain unchanged; final classification adds the actual replay gate. A separate raw-record audit independently recomputed every score and endpoint stratum and confirmed exactly 84 successful server generation records, matching the 84 journal call IDs.

## 27. Historical preservation

Five actual post-study commands passed: this ablation replay, R1 exact replay, schema-contract exact replay, five unchanged v2 UNKNOWN/framework tests and five ablation preflight tests. No unrelated live historical campaign was rerun. **488 inherited substantive public files** remain byte-identical. R1 stays A; interrupted v2 stays C; schema-contract support, Map established-prior v1, all earlier Explorer/Map/Recovery results and UNKNOWN evidence remain unchanged. Main, tags and all prior branch refs unchanged. Nothing pushed.

Two pre-inference utility attempts failed before any model call: a newer Python hashing helper was unavailable, and a first blob-path assumption used hyphens rather than this Ollama version’s colons. Both were corrected before the passing complete hash/preflight check and preregistration commit. Their record is retained privately. They changed no science. No live retries or replacements occurred.

## 28. Limitations

One model/runtime, one seed per preserved context, one stationary bounded world and the R1-selected trajectories. Pairs are clustered within episodes and reuse some state/action problems; 42 is not a count of independent worlds or independent participants. Descriptive subgroup counts are small and uneven. Same seeds and stateless requests hold the registered request parameters fixed but do not prove deterministic execution or internal independence. Counterbalancing addresses order prospectively; order strata are descriptive. Correct prior outcomes directly reveal useful information about repeated stationary problems. This does not show an internal belief-update mechanism, weight learning, persistent model learning, causal world-model learning, RL, AGI or RSI. Evaluator authenticity inherits R1’s external realized-event source trust boundary. Raw source/response archives are private, so public compact evidence alone cannot perform full replay.

## 29. Narrowest defensible conclusion

Visible authenticated prior experience causally altered Map proposals under this paired prompt intervention, and exact accuracy was higher with visible history (33/42 vs 11/42). This supports the frozen authenticated-history Map effect in these contexts; it does not identify how the model computes the difference.

## 30. Recommendation

Stop at this checkpoint. A separate research decision may consider whether verified Memory can usefully persist across episode boundaries, with explicit context/provenance and forgetting/contradiction semantics. No cross-episode persistence, new model role, world enlargement, weight changes or additional campaign was started.
