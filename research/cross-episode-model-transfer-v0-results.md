# Cross-episode model transfer v0 — results

**Overall: NOT ESTABLISHED.** Explorer passed all frozen criteria (CARRY ADVANCE 10/12; FRESH 5/12). Map exact accuracy was 3/12 versus 0/12, with three favorable pairs against the required four. All 48 calls completed once; exact replay and preservation passed.

## 1. Parent identity

Branch `research/cross-episode-model-transfer-v0` descends from initialization-v1 `9e2e70bcde58f8cfe5a76f0dd2d2a08c2ba617f8`. Prospective registration and scientific implementation were committed as `e083bef80159fbe150f19b658959207f38473839` before inference. No historical result was revised.

## 2. Initialization-boundary A

Initialization v1 remains **A — CROSS-EPISODE INITIALIZATION BOUNDARY COMPLETE**. Its actual deterministic replay matched both saved files; six boundary tests were rerun in preflight. This provides a trusted in-process initialization boundary, not crash-durable or physical reset guarantees.

## 3. Prior causal Map-memory finding

The earlier composition Map Memory ablation remains **AUTHENTIC-HISTORY MAP EFFECT SUPPORTED** and replayed exactly. That study varied visibility of existing history. Here FRESH actually starts without history; it is not the old WITHHELD condition.

## 4. Exact research question

Can a stateless model start a fresh present already informed by a verified past that lives outside the model? Test first Explorer choice and fixed-target Map prediction independently after genuine initialization.

## 5. CARRY/FRESH distinction

CARRY retains authenticated episode-1 experience across trusted initialization. FRESH is a separate ordinary new world/source/framework at epoch 1002, state 0 and empty Memory. FRESH never received the earlier history. Model calls in both conditions are stateless.

## 6. Deterministic episode-1 history

| Transaction | Action | Transition | Consequence |
| --- | --- | --- | --- |
| 1 | HOLD | 0 → 0 | 0 |
| 2 | ADVANCE | 0 → 1 | 1 |
| 3 | RETREAT | 1 → 0 | 0 |
| 4 | RETREAT | 0 → 3 | -1 |

Each of twelve CARRY systems used ordinary authenticated publication. Setup generated 48 deterministic realized events in total; these are separate from the 48 model calls.

## 7. Episode boundary

Each CARRY system invoked `start_episode(1002,0)` once. All twelve resets changed current state from 3 to 0 with zero external execution, Measure, Recovery or package-admission calls at the boundary. Source event count remained four.

## 8. Current state / retained history

Current external and authorized state is 0 in epoch 1002. Memory still ends with the epoch-1001 observation whose next_state is 3. All four old records, pairs, package objects and original receipt objects survive; current state is not inferred by rewriting the last historical record.

## 9. FRESH system

Twelve independent ordinary fresh systems begin directly in epoch 1002/state 0. Memory, pairs and packages are empty; world execution and source event counts are zero. CARRY Memory was never deleted or repurposed to create FRESH.

## 10. UNKNOWN semantics

All three CARRY state-0 actions have authentic observations: ADVANCE [1], HOLD [0], RETREAT [−1]. None renders UNTRIED. FRESH legitimately renders three UNTRIED values and an empty Map history. Unknown markers never enter Memory. All actions remain allowed; one negative observation is not a universal prohibition. This study contains no contradiction or action-retest campaign.

## 11. Opaque mappings

| Context | Family | Mapping index | Aliases → underlying actions |
| --- | --- | --- | --- |
| 0 | O1 | 0 | K1=ADVANCE, K2=HOLD, K3=RETREAT |
| 1 | O1 | 1 | K1=ADVANCE, K2=RETREAT, K3=HOLD |
| 2 | O1 | 2 | K1=HOLD, K2=ADVANCE, K3=RETREAT |
| 3 | O1 | 3 | K1=HOLD, K2=RETREAT, K3=ADVANCE |
| 4 | O1 | 4 | K1=RETREAT, K2=ADVANCE, K3=HOLD |
| 5 | O1 | 5 | K1=RETREAT, K2=HOLD, K3=ADVANCE |
| 6 | O2 | 0 | M4=HOLD, Q7=ADVANCE, Z2=RETREAT |
| 7 | O2 | 1 | M4=RETREAT, Q7=ADVANCE, Z2=HOLD |
| 8 | O2 | 2 | M4=ADVANCE, Q7=HOLD, Z2=RETREAT |
| 9 | O2 | 3 | M4=RETREAT, Q7=HOLD, Z2=ADVANCE |
| 10 | O2 | 4 | M4=ADVANCE, Q7=RETREAT, Z2=HOLD |
| 11 | O2 | 5 | M4=HOLD, Q7=RETREAT, Z2=ADVANCE |

All six permutations occur once in each family. The same mapping is used within each matched pair.

## 12. Explorer prompts

The exact unchanged exploration-aware system instruction and projection contract are frozen in the [preregistration](cross-episode-model-transfer-v0-preregistration.md). Each input contains state 0, all three opaque actions and their actual verified outcomes or truthful UNTRIED. Exact request texts are retained privately. No condition or transfer labels are shown.

## 13. Map prompts

The exact unchanged explicit R1 two-field JSON instruction is frozen in the preregistration. Target is always state-0 ADVANCE, independent of Explorer output. CARRY supplies one authenticated row: epoch 1001, transaction_id 2, ADVANCE alias, next_state 1, consequence 1. FRESH supplies `[]`. The evaluator designation and future events are absent.

## 14. Model/config

Pinned `dolphin-mixtral:latest`, Ollama 0.1.16, GGUF 47B Q4_0. All five complete manifest blobs were freshly hashed before inference. Temperature .2, top_p .9, top_k 40, num_ctx 2048, repeat_penalty 1.1; num_predict 16 Explorer / 32 Map. Manifest and weight identities are in the preregistration. No returned context, retry, repair or constrained decoding.

## 15. Exact 48-call schedule

| Call index | Context | Family | Role | Condition | Seed |
| --- | --- | --- | --- | --- | --- |
| 0 | 0 | O1 | Explorer | CARRY | 90001 |
| 1 | 0 | O1 | Explorer | FRESH | 90001 |
| 2 | 0 | O1 | Map | CARRY | 90101 |
| 3 | 0 | O1 | Map | FRESH | 90101 |
| 4 | 1 | O1 | Explorer | FRESH | 90002 |
| 5 | 1 | O1 | Explorer | CARRY | 90002 |
| 6 | 1 | O1 | Map | FRESH | 90102 |
| 7 | 1 | O1 | Map | CARRY | 90102 |
| 8 | 2 | O1 | Explorer | CARRY | 90003 |
| 9 | 2 | O1 | Explorer | FRESH | 90003 |
| 10 | 2 | O1 | Map | CARRY | 90103 |
| 11 | 2 | O1 | Map | FRESH | 90103 |
| 12 | 3 | O1 | Explorer | FRESH | 90004 |
| 13 | 3 | O1 | Explorer | CARRY | 90004 |
| 14 | 3 | O1 | Map | FRESH | 90104 |
| 15 | 3 | O1 | Map | CARRY | 90104 |
| 16 | 4 | O1 | Explorer | CARRY | 90005 |
| 17 | 4 | O1 | Explorer | FRESH | 90005 |
| 18 | 4 | O1 | Map | CARRY | 90105 |
| 19 | 4 | O1 | Map | FRESH | 90105 |
| 20 | 5 | O1 | Explorer | FRESH | 90006 |
| 21 | 5 | O1 | Explorer | CARRY | 90006 |
| 22 | 5 | O1 | Map | FRESH | 90106 |
| 23 | 5 | O1 | Map | CARRY | 90106 |
| 24 | 6 | O2 | Explorer | CARRY | 90001 |
| 25 | 6 | O2 | Explorer | FRESH | 90001 |
| 26 | 6 | O2 | Map | CARRY | 90101 |
| 27 | 6 | O2 | Map | FRESH | 90101 |
| 28 | 7 | O2 | Explorer | FRESH | 90002 |
| 29 | 7 | O2 | Explorer | CARRY | 90002 |
| 30 | 7 | O2 | Map | FRESH | 90102 |
| 31 | 7 | O2 | Map | CARRY | 90102 |
| 32 | 8 | O2 | Explorer | CARRY | 90003 |
| 33 | 8 | O2 | Explorer | FRESH | 90003 |
| 34 | 8 | O2 | Map | CARRY | 90103 |
| 35 | 8 | O2 | Map | FRESH | 90103 |
| 36 | 9 | O2 | Explorer | FRESH | 90004 |
| 37 | 9 | O2 | Explorer | CARRY | 90004 |
| 38 | 9 | O2 | Map | FRESH | 90104 |
| 39 | 9 | O2 | Map | CARRY | 90104 |
| 40 | 10 | O2 | Explorer | CARRY | 90005 |
| 41 | 10 | O2 | Explorer | FRESH | 90005 |
| 42 | 10 | O2 | Map | CARRY | 90105 |
| 43 | 10 | O2 | Map | FRESH | 90105 |
| 44 | 11 | O2 | Explorer | FRESH | 90006 |
| 45 | 11 | O2 | Explorer | CARRY | 90006 |
| 46 | 11 | O2 | Map | FRESH | 90106 |
| 47 | 11 | O2 | Map | CARRY | 90106 |

All 48 completed once: 24 Explorer, 24 Map, zero Recovery. Explorer pair precedes Map pair per context. Even contexts CARRY first; odd FRESH first. The independent server log contains exactly 48 successful generation requests.

## 16. Explorer validity

CARRY 12/12; FRESH 11/12. Strict historical parser, no repair. Invalid proposals count as non-ADVANCE in binary scoring and remain explicitly invalid in the paired evidence.

## 17. Explorer CARRY behavior

{'ADVANCE': 10, 'HOLD': 1, 'INVALID': 0, 'RETREAT': 1}. Verified-best ADVANCE selected 10/12. These are proposals only; no selected action was executed.

## 18. Explorer FRESH behavior

{'ADVANCE': 5, 'HOLD': 1, 'INVALID': 1, 'RETREAT': 5}. ADVANCE selected 5/12. FRESH has no verified action ranking; these choices are not labeled irrational or integrity failures.

## 19. Explorer matched pairs

| Family | Mapping | CARRY | FRESH | Classification |
| --- | --- | --- | --- | --- |
| O1 | 0 | ADVANCE | ADVANCE | both positive |
| O1 | 1 | ADVANCE | ADVANCE | both positive |
| O1 | 2 | ADVANCE | HOLD | favorable |
| O1 | 3 | ADVANCE | INVALID | favorable |
| O1 | 4 | ADVANCE | RETREAT | favorable |
| O1 | 5 | ADVANCE | RETREAT | favorable |
| O2 | 0 | ADVANCE | ADVANCE | both positive |
| O2 | 1 | ADVANCE | RETREAT | favorable |
| O2 | 2 | HOLD | ADVANCE | reverse |
| O2 | 3 | ADVANCE | RETREAT | favorable |
| O2 | 4 | ADVANCE | ADVANCE | both positive |
| O2 | 5 | RETREAT | RETREAT | both negative |

Favorable 6; reverse 1; both ADVANCE 4; both non-ADVANCE 1; identical valid choices 5/12.

## 20. Explorer primary decision

**CROSS-EPISODE EXPLORER MEMORY EFFECT SUPPORTED**

| Frozen criterion | Passed |
| --- | --- |
| O1_carry_advance_at_least_4 | yes |
| O2_carry_advance_at_least_4 | yes |
| all_24_complete | yes |
| carry_advance_at_least_9 | yes |
| carry_valid_at_least_11 | yes |
| favorable_at_least_5 | yes |
| fresh_valid_at_least_11 | yes |
| reverse_at_most_1 | yes |

## 21. Map validity

CARRY 12/12; FRESH 12/12. Strict exact schema rejects extra/duplicate fields, booleans, non-integers and out-of-domain values. Invalid means wrong on all accuracy measures.

## 22. Map CARRY accuracy

consequence 3/12, exact 3/12, next_state 12/12, valid 12/12. Scoring uses the retained original episode-1 ADVANCE receipt, never model output or a fabricated probe event.

## 23. Map FRESH accuracy

consequence 2/12, exact 0/12, next_state 9/12, valid 12/12. A correct empty-history guess is scored correct without implying authenticated knowledge.

## 24. Map matched discordances

| Family | Mapping | CARRY | FRESH | Classification |
| --- | --- | --- | --- | --- |
| O1 | 0 | {'consequence': 0, 'next_state': 1} | {'consequence': -1, 'next_state': 1} | both negative |
| O1 | 1 | {'consequence': 0, 'next_state': 1} | {'consequence': 0, 'next_state': 1} | both negative |
| O1 | 2 | {'consequence': 0, 'next_state': 1} | {'consequence': 1, 'next_state': 0} | both negative |
| O1 | 3 | {'consequence': 0, 'next_state': 1} | {'consequence': 0, 'next_state': 1} | both negative |
| O1 | 4 | {'consequence': 1, 'next_state': 1} | {'consequence': 0, 'next_state': 1} | favorable |
| O1 | 5 | {'consequence': 0, 'next_state': 1} | {'consequence': 0, 'next_state': 1} | both negative |
| O2 | 0 | {'consequence': 0, 'next_state': 1} | {'consequence': 0, 'next_state': 1} | both negative |
| O2 | 1 | {'consequence': 0, 'next_state': 1} | {'consequence': 0, 'next_state': 1} | both negative |
| O2 | 2 | {'consequence': 1, 'next_state': 1} | {'consequence': 1, 'next_state': 0} | favorable |
| O2 | 3 | {'consequence': 1, 'next_state': 1} | {'consequence': 0, 'next_state': 1} | favorable |
| O2 | 4 | {'consequence': 0, 'next_state': 1} | {'consequence': 0, 'next_state': 0} | both negative |
| O2 | 5 | {'consequence': 0, 'next_state': 1} | {'consequence': 0, 'next_state': 1} | both negative |

Favorable 3; reverse 0; both exact 0; both wrong 9.

## 25. Map primary decision

**CROSS-EPISODE MAP MEMORY EFFECT NOT ESTABLISHED**

The failed criterion is favorable exact discordances: **3 observed; at least 4 required**. CARRY next-state accuracy was 12/12, but consequence and exact-pair accuracy were only 3/12. No additional calls were made to cross the threshold.

| Frozen criterion | Passed |
| --- | --- |
| O1_favorable_exceeds_reverse | yes |
| O2_favorable_exceeds_reverse | yes |
| all_24_complete | yes |
| carry_exact_exceeds_fresh | yes |
| carry_valid_at_least_11 | yes |
| favorable_at_least_4 | NO |
| fresh_valid_at_least_11 | yes |
| reverse_at_most_1 | yes |

## 26. O1/O2 breakdown

| Role | Family | CARRY valid | FRESH valid | CARRY ADVANCE/exact | FRESH ADVANCE/exact | Favorable | Reverse |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Explorer | O1 | 6/6 | 5/6 | 6/6 | 2/6 | 4 | 0 |
| Explorer | O2 | 6/6 | 6/6 | 4/6 | 3/6 | 2 | 1 |
| Map | O1 | 6/6 | 6/6 | 1/6 | 0/6 | 1 | 0 |
| Map | O2 | 6/6 | 6/6 | 2/6 | 0/6 | 2 | 0 |

Family requirements were evaluated separately. Strong pooled results cannot rescue a failed family rule.

## 27. Overall cross-episode transfer decision

**CROSS-EPISODE AUTHENTICATED-MEMORY BEHAVIORAL TRANSFER NOT ESTABLISHED**

Overall support requires both role-specific decisions plus successful replay and preservation. No threshold was revised after observing output.

## 28. Provenance audit

All 24 CARRY pre-call audits verified current epoch 1002/state 0, four retained epoch-1001 records, original receipts by object identity, exact package bindings, unchanged source lifetime and zero fake reset events. Map retains epoch and transaction identity. Epoch 1002 starts its transaction counter at 1; probes create no transaction. Historical and future repeated transaction numbers must be distinguished by epoch.

## 29. No model/chat persistence audit

All 48 request bodies contain only model, system, prompt, stream=false and options. No prior response context is sent. Requests share the pinned local server and model weights, but no application-level chat history or weight update is used. The observed variable is authenticated SYSTEM history availability in the current input; this does not audit undocumented runtime internals.

## 30. Memory unchanged

All 48 before/after probe checks matched full system snapshots. No Explorer output executed, no Map output latched, no receipt minted and no Memory committed by any probe. Both CARRY and FRESH systems remained unchanged across their four calls. Source count four CARRY / zero FRESH remains fixed.

## 31. Exact replay

All 48 recorded responses replayed with socket creation forbidden. Actual episode-1 execution, receipts, initialization, fresh construction, projections, exact requests, parsing, scoring, pairs and decisions were reconstructed. Eight registered output files and twelve full system snapshots matched byte for byte. Separately finalized live/replay results are identical. Zero additional inference.

## 32. Historical preservation

All five requested historical replays passed. Preflight ran 18 tests (six new study, six initialization boundary, six inherited durability); the historical regression set ran 49 tests. All 525 inherited substantive public files are byte-identical to the parent. Four prior private archives passed their complete saved checksum inventories. Prior classifications, all older results, authority code, main, tags and prior branch references remain unchanged. See [verification.json](../experiments/cross_episode_model_transfer_v0/verification.json) for actual commands, outcomes and evidence hashes.

## 33. Limitations

Twelve paired contexts, two opaque vocabularies, one model, one stationary four-state fixture, four old observations and read-only first-decision proposals. Seeds are matched and reused across families; these are not independent model/population samples. There is no new episode-2 realized experience, contradiction, retention extension or full composed episode. A changed proposal does not establish that the model inferred causality. Trusted execution emitter, registry, audit and initialization code remain the authority boundary. No persistent/lifelong/weight learning, RL, self-improvement, AGI or RSI is established.

## 34. Narrowest defensible conclusion

The frozen overall transfer claim is not established. Explorer: CROSS-EPISODE EXPLORER MEMORY EFFECT SUPPORTED. Map: CROSS-EPISODE MAP MEMORY EFFECT NOT ESTABLISHED. The role-specific counts and failed gates above are retained without extending the campaign.

## 35. Recommendation

Stop here as authorized. Inspect the failed role-specific gates and paired outputs before deciding whether a separately authorized study is justified. Do not extend this campaign or revise its thresholds.
