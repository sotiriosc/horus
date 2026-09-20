# Cross-episode Map history depth v1 — results

**TWO-OBSERVATION CROSS-EPISODE MAP EFFECT SUPPORTED.** Exact accuracy: D0 0/12, D1 7/12, D2 10/12. All 36 calls completed once; exact replay and preservation passed.

## 1. Parent transfer-v0 result

Parent branch `research/cross-episode-model-transfer-v0`, commit `148b760d7c97583142c7e7f6093aa0835f0d4a71`. Its overall NOT ESTABLISHED, Explorer SUPPORTED and Map NOT ESTABLISHED results remain unchanged. Prior CARRY exact 3/12, FRESH 0/12, favorable 3 against required 4. This new branch is `research/cross-episode-map-history-depth-v1`; preregistration commit `50730a208417e069b1f79f349a09be14ab9b492a` preceded all inference.

## 2. Why Explorer is not rerun

The unresolved question concerns Map and authenticated history depth. Explorer already met its separate parent criterion. Exactly zero new Explorer calls and zero Recovery calls were made. All model probes here are fixed-target Map proposals.

## 3. Prior Map history-depth motivation

[Map v0](model-map-proposal-v0-results.md) failed its one-row exact old-relation prerequisite. The separately preregistered [established-prior Map v1](model-map-established-prior-revision-v1-results.md) used two observations and obtained exact old predictions at P0 in both families. Those studies also differed in navigation, transaction IDs and seeds; they motivate this question without proving that row count alone caused the difference or that two is a general minimum.

## 4. Exact research question

When present state is genuinely fresh, does zero, one or two authenticated exact-pair observations retained from an earlier episode change the first Map prediction? Primary comparison is D2 versus D0. D1 is secondary; its new draws need not match the previous 3/12.

## 5. D0/D1/D2 distinction

D0 is an ordinary new epoch-1002/state-0 world/source/framework with empty Memory. D1 and D2 are independent ordinary systems that executed authentic episode-1 history and retained it through trusted initialization. D0 is never produced by deleting or withholding another system’s history. Only the exact-pair history differs in matched model input.

## 6. Authenticated episode-1 construction

| System | Transaction | Action | Transition | Consequence |
| --- | --- | --- | --- | --- |
| D1 | 1 | ADVANCE | 0 → 1 | 1 |
| D2 | 1 | ADVANCE | 0 → 1 | 1 |
| D2 | 2 | RETREAT | 1 → 0 | 0 |
| D2 | 3 | ADVANCE | 0 → 1 | 1 |

Each event followed ordinary action → external execution → authentic receipt → Measure → authorized publication. D1 needs no navigation; D2 uses one necessary return. All navigation stays in protected Memory. Twelve contexts created 48 ordinary setup events, separate from the model calls.

## 7. Fresh-state initialization

All 24 D1/D2 episode-1 systems ended at state 1. Each invoked trusted `start_episode(1002,0)`, resetting external and authorized state to 0 with zero realized reset events. Execution, Measure, Recovery and package-admission counts at each reset were zero. A natural return to zero was not substituted for the boundary.

## 8. Provenance

Every retained record preserves epoch 1001, original transaction ID, event identity, original receipt object and pair/package binding. Source lifetime stays unchanged within each D1/D2 system; separate systems never import one another’s records. Before/after audits of all systems passed for every probe. Full protected and external snapshots remained identical; model outputs created no execution, receipt, Map latch or Memory commit.

## 9. UNKNOWN semantics

D0 history [] is truthful because D0 never had an earlier episode. D1 and D2 display every retained matching row. No authenticated target observation is marked unknown, and no absence marker becomes an event. A negative observation never removes an allowed action. Contradiction and nonstationarity are outside this study.

## 10. Epoch-visible projection

The unchanged initialization-v1 Map projection emits state 0 and the ADVANCE alias. D1 history is one row with epoch 1001/transaction 1; D2 history has epoch 1001/transactions 1 and 3. All rows show next_state 1/consequence 1. D2’s transaction-2 RETREAT remains in protected Memory and is omitted solely by exact state/action filtering. Epoch is neither removed nor relabeled to current epoch 1002.

## 11. Representation mappings

| Context | Family | Mapping index | Aliases → actions |
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

All six permutations appear once per family. Within a triple, mapping, target, system instruction, options and seed match; only verified chronological history differs.

## 12. Prompt/parser

The exact unchanged explicit R1 Map instruction is in the [frozen preregistration](cross-episode-map-history-depth-v1-preregistration.md). Requests contain no depth labels, summaries, averages, confidence, recency guidance or evaluator designation. The existing strict parser was imported unchanged: exact two-field JSON, finite integers, no duplicates/extras/booleans/floats. Malformed output remains invalid and wrong on every component; no repair, retry or constrained decoding.

## 13. Model/config

Pinned dolphin-mixtral:latest; Ollama 0.1.16; GGUF 47B Q4_0. All five complete manifest blobs were freshly hashed before the first call; identities are frozen in preregistration. Temperature .2, top_p .9, top_k 40, num_predict 32, num_ctx 2048, repeat_penalty 1.1. Stateless request bodies carry no returned context or chat history. The pinned server is shared within the campaign; undocumented internal runtime behavior is not separately audited.

## 14. Call schedule

| Index | Context | Family | Condition | Seed |
| --- | --- | --- | --- | --- |
| 0 | 0 | O1 | D0 | 91001 |
| 1 | 0 | O1 | D1 | 91001 |
| 2 | 0 | O1 | D2 | 91001 |
| 3 | 1 | O1 | D1 | 91002 |
| 4 | 1 | O1 | D2 | 91002 |
| 5 | 1 | O1 | D0 | 91002 |
| 6 | 2 | O1 | D2 | 91003 |
| 7 | 2 | O1 | D0 | 91003 |
| 8 | 2 | O1 | D1 | 91003 |
| 9 | 3 | O1 | D0 | 91004 |
| 10 | 3 | O1 | D1 | 91004 |
| 11 | 3 | O1 | D2 | 91004 |
| 12 | 4 | O1 | D1 | 91005 |
| 13 | 4 | O1 | D2 | 91005 |
| 14 | 4 | O1 | D0 | 91005 |
| 15 | 5 | O1 | D2 | 91006 |
| 16 | 5 | O1 | D0 | 91006 |
| 17 | 5 | O1 | D1 | 91006 |
| 18 | 6 | O2 | D0 | 91001 |
| 19 | 6 | O2 | D1 | 91001 |
| 20 | 6 | O2 | D2 | 91001 |
| 21 | 7 | O2 | D1 | 91002 |
| 22 | 7 | O2 | D2 | 91002 |
| 23 | 7 | O2 | D0 | 91002 |
| 24 | 8 | O2 | D2 | 91003 |
| 25 | 8 | O2 | D0 | 91003 |
| 26 | 8 | O2 | D1 | 91003 |
| 27 | 9 | O2 | D0 | 91004 |
| 28 | 9 | O2 | D1 | 91004 |
| 29 | 9 | O2 | D2 | 91004 |
| 30 | 10 | O2 | D1 | 91005 |
| 31 | 10 | O2 | D2 | 91005 |
| 32 | 10 | O2 | D0 | 91005 |
| 33 | 11 | O2 | D2 | 91006 |
| 34 | 11 | O2 | D0 | 91006 |
| 35 | 11 | O2 | D1 | 91006 |

Exactly 36 Map calls completed once. Seeds 91001–91006 match across depths and corresponding family mappings. Context modulo three rotates D0→D1→D2, D1→D2→D0, D2→D0→D1. The independent server log records exactly 36 successful generation endpoints. Durable fsynced intent precedes send, raw response precedes parse, parsed result precedes next call. No extra or replacement calls.

## 15. Validity

| Depth | Valid | Next state | Consequence | Exact |
| --- | --- | --- | --- | --- |
| D0 | 12 | 6 | 1 | 0 |
| D1 | 12 | 12 | 7 | 7 |
| D2 | 12 | 12 | 10 | 10 |

Denominators are twelve per depth. Invalid output receives no partial accuracy. Actual complete responses are distinguished from transport failure; no transport failure occurred.

## 16. D0 results

Valid 12/12; next_state correct 6/12; consequence correct 1/12; exact pair 0/12. D0 had no authenticated observation. A correct fresh guess is scored correct without implying verified knowledge.

## 17. D1 results

Valid 12/12; next_state correct 12/12; consequence correct 7/12; exact pair 7/12. D1 is a registered secondary condition. It is fully reported without requiring the old 3/12 or inventing a new post-hoc success threshold.

## 18. D2 results

Valid 12/12; next_state correct 12/12; consequence correct 10/12; exact pair 10/12. Its two retained authentic exact-pair rows agree on (1,+1). The primary criterion requires at least 9/12 exact outcomes; state-only correctness cannot substitute.

## 19. D1-vs-D0 pairs

| Family | Mapping | D1 | D0 | Pair class |
| --- | --- | --- | --- | --- |
| O1 | 0 | {'consequence': 0, 'next_state': 1} | {'consequence': 0, 'next_state': 1} | both_wrong |
| O1 | 1 | {'consequence': 0, 'next_state': 1} | {'consequence': 0, 'next_state': 1} | both_wrong |
| O1 | 2 | {'consequence': 1, 'next_state': 1} | {'consequence': 0, 'next_state': 1} | favorable |
| O1 | 3 | {'consequence': 1, 'next_state': 1} | {'consequence': 0, 'next_state': 1} | favorable |
| O1 | 4 | {'consequence': 0, 'next_state': 1} | {'consequence': 0, 'next_state': 0} | both_wrong |
| O1 | 5 | {'consequence': 0, 'next_state': 1} | {'consequence': 0, 'next_state': 1} | both_wrong |
| O2 | 0 | {'consequence': 0, 'next_state': 1} | {'consequence': 0, 'next_state': 0} | both_wrong |
| O2 | 1 | {'consequence': 1, 'next_state': 1} | {'consequence': 0, 'next_state': 1} | favorable |
| O2 | 2 | {'consequence': 1, 'next_state': 1} | {'consequence': 1, 'next_state': 0} | favorable |
| O2 | 3 | {'consequence': 1, 'next_state': 1} | {'consequence': 0, 'next_state': 0} | favorable |
| O2 | 4 | {'consequence': 1, 'next_state': 1} | {'consequence': 0, 'next_state': 0} | favorable |
| O2 | 5 | {'consequence': 1, 'next_state': 1} | {'consequence': 0, 'next_state': 0} | favorable |

both_exact: 0, both_wrong: 5, favorable: 7, reverse: 0.

## 20. D2-vs-D0 pairs

| Family | Mapping | D2 | D0 | Pair class |
| --- | --- | --- | --- | --- |
| O1 | 0 | {'consequence': 1, 'next_state': 1} | {'consequence': 0, 'next_state': 1} | favorable |
| O1 | 1 | {'consequence': 1, 'next_state': 1} | {'consequence': 0, 'next_state': 1} | favorable |
| O1 | 2 | {'consequence': 1, 'next_state': 1} | {'consequence': 0, 'next_state': 1} | favorable |
| O1 | 3 | {'consequence': 1, 'next_state': 1} | {'consequence': 0, 'next_state': 1} | favorable |
| O1 | 4 | {'consequence': 0, 'next_state': 1} | {'consequence': 0, 'next_state': 0} | both_wrong |
| O1 | 5 | {'consequence': 1, 'next_state': 1} | {'consequence': 0, 'next_state': 1} | favorable |
| O2 | 0 | {'consequence': 1, 'next_state': 1} | {'consequence': 0, 'next_state': 0} | favorable |
| O2 | 1 | {'consequence': 0, 'next_state': 1} | {'consequence': 0, 'next_state': 1} | both_wrong |
| O2 | 2 | {'consequence': 1, 'next_state': 1} | {'consequence': 1, 'next_state': 0} | favorable |
| O2 | 3 | {'consequence': 1, 'next_state': 1} | {'consequence': 0, 'next_state': 0} | favorable |
| O2 | 4 | {'consequence': 1, 'next_state': 1} | {'consequence': 0, 'next_state': 0} | favorable |
| O2 | 5 | {'consequence': 1, 'next_state': 1} | {'consequence': 0, 'next_state': 0} | favorable |

both_exact: 0, both_wrong: 2, favorable: 10, reverse: 0.

## 21. D2-vs-D1 pairs

| Family | Mapping | D2 | D1 | Pair class |
| --- | --- | --- | --- | --- |
| O1 | 0 | {'consequence': 1, 'next_state': 1} | {'consequence': 0, 'next_state': 1} | favorable |
| O1 | 1 | {'consequence': 1, 'next_state': 1} | {'consequence': 0, 'next_state': 1} | favorable |
| O1 | 2 | {'consequence': 1, 'next_state': 1} | {'consequence': 1, 'next_state': 1} | both_exact |
| O1 | 3 | {'consequence': 1, 'next_state': 1} | {'consequence': 1, 'next_state': 1} | both_exact |
| O1 | 4 | {'consequence': 0, 'next_state': 1} | {'consequence': 0, 'next_state': 1} | both_wrong |
| O1 | 5 | {'consequence': 1, 'next_state': 1} | {'consequence': 0, 'next_state': 1} | favorable |
| O2 | 0 | {'consequence': 1, 'next_state': 1} | {'consequence': 0, 'next_state': 1} | favorable |
| O2 | 1 | {'consequence': 0, 'next_state': 1} | {'consequence': 1, 'next_state': 1} | reverse |
| O2 | 2 | {'consequence': 1, 'next_state': 1} | {'consequence': 1, 'next_state': 1} | both_exact |
| O2 | 3 | {'consequence': 1, 'next_state': 1} | {'consequence': 1, 'next_state': 1} | both_exact |
| O2 | 4 | {'consequence': 1, 'next_state': 1} | {'consequence': 1, 'next_state': 1} | both_exact |
| O2 | 5 | {'consequence': 1, 'next_state': 1} | {'consequence': 1, 'next_state': 1} | both_exact |

both_exact: 6, both_wrong: 1, favorable: 4, reverse: 1.

This contrast is descriptive and is not substituted for the frozen D2-vs-D0 primary test. D2 improves four contexts and worsens one relative to D1. O2 remains 5/6 exact at both depths, with one favorable and one reverse pair; aggregate improvement is not universal.

## 22. O1 breakdown

Denominators: six per depth.

| Depth | Valid | Next state | Consequence | Exact |
| --- | --- | --- | --- | --- |
| D0 | 6 | 5 | 0 | 0 |
| D1 | 6 | 6 | 2 | 2 |
| D2 | 6 | 6 | 5 | 5 |

| Comparison | Favorable | Reverse | Both exact | Both wrong |
| --- | --- | --- | --- | --- |
| D1_vs_D0 | 2 | 0 | 0 | 4 |
| D2_vs_D0 | 5 | 0 | 0 | 1 |
| D2_vs_D1 | 3 | 0 | 2 | 1 |

## 23. O2 breakdown

Denominators: six per depth.

| Depth | Valid | Next state | Consequence | Exact |
| --- | --- | --- | --- | --- |
| D0 | 6 | 1 | 1 | 0 |
| D1 | 6 | 6 | 5 | 5 |
| D2 | 6 | 6 | 5 | 5 |

| Comparison | Favorable | Reverse | Both exact | Both wrong |
| --- | --- | --- | --- | --- |
| D1_vs_D0 | 5 | 0 | 0 | 1 |
| D2_vs_D0 | 5 | 0 | 0 | 1 |
| D2_vs_D1 | 1 | 1 | 4 | 0 |

## 24. Next-state analysis

Correct next_state: D0 6/12, D1 12/12, D2 12/12. D2−D0 count difference +6; D2−D1 +0. These are component counts, not exact-outcome success.

## 25. Consequence analysis

Correct consequence: D0 1/12, D1 7/12, D2 10/12. D2−D0 count difference +9; D2−D1 +3. Exact accuracy still requires both fields in the same valid response. The earlier transfer-v0 state-correct/consequence-wrong pattern remains reported unchanged.

## 26. Trajectory patterns

| Context | Family | D0 → D1 → D2 |
| --- | --- | --- |
| 0 | O1 | wrong -> wrong -> exact |
| 1 | O1 | wrong -> wrong -> exact |
| 2 | O1 | wrong -> exact -> exact |
| 3 | O1 | wrong -> exact -> exact |
| 4 | O1 | wrong -> wrong -> wrong |
| 5 | O1 | wrong -> wrong -> exact |
| 6 | O2 | wrong -> wrong -> exact |
| 7 | O2 | wrong -> exact -> wrong |
| 8 | O2 | wrong -> exact -> exact |
| 9 | O2 | wrong -> exact -> exact |
| 10 | O2 | wrong -> exact -> exact |
| 11 | O2 | wrong -> exact -> exact |

| Trajectory | Count |
| --- | --- |
| wrong -> exact -> exact | 6 |
| wrong -> exact -> wrong | 1 |
| wrong -> wrong -> exact | 4 |
| wrong -> wrong -> wrong | 1 |

Aggregate exact monotonicity D0≤D1≤D2: **True**, using 0≤7≤10. This is descriptive only, not a primary gate. Invalid responses would count as wrong; all 36 responses in this campaign were valid.

## 27. Primary criterion

**TWO-OBSERVATION CROSS-EPISODE MAP EFFECT SUPPORTED**

| Frozen criterion | Passed |
| --- | --- |
| all_36_complete | yes |
| D0_valid_at_least_11 | yes |
| D1_valid_at_least_11 | yes |
| D2_valid_at_least_11 | yes |
| D2_exact_at_least_9 | yes |
| D2_exact_exceeds_D0 | yes |
| favorable_at_least_5 | yes |
| reverse_at_most_1 | yes |
| O1_favorable_exceeds_reverse | yes |
| O2_favorable_exceeds_reverse | yes |
| system_provenance_integrity | yes |
| exact_replay | yes |

All twelve frozen criteria passed. No threshold or denominator was changed.

## 28. Exact replay

All 36 saved responses replayed with network forbidden. Actual D0 fresh systems, D1/D2 authenticated histories, trusted resets, projections, exact prompts, strict parsing, scores, three contrasts and trajectories were reconstructed. Eight registered output files and twelve full system snapshots are byte-identical. Finalized live/replay results also match. An independent direct audit separately recalculated components, all contrasts, trajectories and the primary rule. Zero additional inference. The private audit initially rejected Ollama’s nanosecond timestamp under Python 3.10; its timestamp reader was corrected without changing raw evidence, scientific code or thresholds, and the audit then passed.

## 29. Historical preservation

All five executed historical replays passed: transfer-v0, initialization-v1, Map ablation, R1 composition and established-prior Map v1. Preflight ran 18 tests; the historical set ran 55 tests. All 537 inherited substantive files match the parent byte for byte. Six prior private archives passed complete checksum inventories. Transfer-v0 overall NOT ESTABLISHED / Explorer SUPPORTED / Map NOT ESTABLISHED, initialization A, boundary-v0 C, ablation SUPPORTED, R1 A and all older results remain unchanged. Main, tags and prior branch refs are untouched. See [verification.json](../experiments/cross_episode_map_history_depth_v1/verification.json) for actual executions and evidence hashes.

## 30. Limitations

Only twelve matched contexts, one pinned model, two opaque vocabularies, a stationary four-state fixture and depth 0/1/2 were tested. Seeds are reused across families; contexts are not independent population/model samples. Added authentic rows also add tokens and identities, so this does not isolate an internal mechanism or a universal minimum amount of experience. D2’s navigation is retained but filtered from input. Epoch presentation is fixed, not experimentally isolated. There is no new episode-2 event, nonstationarity, full composition or persistent model/chat state. Trusted emitter, registry, audit and initialization remain the authority boundary. This is not persistent/lifelong/weight learning, RL, causal world-model learning, AGI or RSI.

## 31. Narrowest defensible conclusion

Two authenticated prior-episode exact-pair observations produced sufficiently strong Map prediction versus a genuinely fresh system to pass the frozen rule in this fixture. D0/D1/D2 exact counts are 0/7/10 of twelve each. D2-versus-D1 favorable/reverse pairs are 4/1; this does not by itself establish that two observations are necessary or generally sufficient. The previous transfer-v0 verdict remains unchanged.

## 32. Recommendation

Stop at this checkpoint as authorized. Review the depth-specific components and matched trajectories before choosing any separately preregistered follow-up. Do not extend this campaign, rerun Explorer, alter epoch presentation, introduce nonstationarity or start full cross-episode composition automatically.
