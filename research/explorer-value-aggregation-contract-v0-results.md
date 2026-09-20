# Explorer value-aggregation contract v0 — results

**EXPLICIT-MEAN EXPLORER POLICY NOT ESTABLISHED**. Exactly 96 Explorer calls; 96/96 valid. Exact replay and historical preservation passed.

| Family | CONTROL B HOLD /12 | CHANGED A RETREAT /12 | CHANGED B RETREAT /12 | CHANGED favorable /12 | Reverse /12 | B valid /24 | Supported |
| --- | --- | --- | --- | --- | --- | --- | --- |
| O1 | 12 | 2 | 4 | 2 | 0 | 24 | False |
| O2 | 12 | 0 | 2 | 2 | 0 | 24 | False |

## 1. Parent Explorer negative result

Parent `research/cross-episode-stale-memory-explorer-revision-v1`, `8e7e9905ae346d1c3e9beb0a04b7e9ba0deb1626`, permanently remains **CROSS-EPISODE STALE-MEMORY EXPLORER REVISION NOT ESTABLISHED** in O1 and O2. Historical CHANGED P2 RETREAT was 1/12 and 0/12; neither family passed its revision or favorable-pair threshold. This separate branch `research/explorer-value-aggregation-contract-v0` has preregistration `b50a65a7237cb3edbe38ea01787c800cb18ba6c9` preceding all inference. No previous score, result or interpretation was retroactively changed.

## 2. Ambiguity diagnosis

The original instruction preferred higher observed consequences but did not define how to aggregate a history. It specified neither arithmetic mean, recency, median, maximum nor minimum. The earlier negative result concerns that original contract and does not establish failure under an explicit mean policy. This motivates a new prospective comparator; it does not prove ambiguity caused the historical result.

## 3. Exact question

With identical authentic P2 input, model, sampler, parser, seed and action set, does replacing the original A system instruction with the explicit B arithmetic-mean policy change Explorer proposals toward the mechanically derived unique mean target? A is a fresh matched comparator, not a demand to reproduce historical counts.

## 4. P2 CONTROL history

Each independent context uses the exact unchanged prior fixture: epoch 1001 starts at state 1 and executes HOLD, RETREAT, ADVANCE, ADVANCE, RETREAT, RETREAT; a trusted zero-event reset moves 0→1 into epoch 1002; two ordinary HOLD events follow. At measured state 1, CONTROL histories are HOLD [+1,+1,+1], RETREAT [0,0], ADVANCE [−1]. All eight original event records remain in protected Memory, including two navigation records excluded mechanically by current-state projection.

## 5. P2 CHANGED history

Identical execution/initialization schedule. Only external state-1 HOLD consequence changes +1→−1 after the reset and before epoch-1002 execution. Histories are HOLD [+1,−1,−1], RETREAT [0,0], ADVANCE [−1]. The episode-1 +1 remains authentic, present and visible. State remains 1; Memory stays at its unchanged bound of eight, with no eviction.

## 6. Evaluator arithmetic means

For every request, authenticate the complete Memory→pair→package→original receipt→actual execution chain, mechanically derive the shown histories, then calculate exact rational sum/count and unique argmax. The independent audit redoes these calculations from protected records. No handwritten summary determines the target.

| Arm | HOLD mean | RETREAT mean | ADVANCE mean | Unique target |
| --- | --- | --- | --- | --- |
| CONTROL | 1 | 0 | −1 | HOLD |
| CHANGED | −1/3 | 0 | −1 | RETREAT |

No target ties occurred. Means and target labels stay evaluator-only; no precomputed means appear in model input.

## 7. Original A instruction

Exact unchanged historical system text:

> Choose an action using verified prior outcomes. Higher observed consequences are preferable. UNTRIED means no verified observation; it does not mean consequence 0. When evidence is insufficient, you may choose an UNTRIED action to gather information. Reply with exactly one allowed action and no explanation.

A has no new success threshold. Its outputs are compared against this study’s prospective mean target without asserting that A explicitly instructed arithmetic mean.

## 8. Explicit B instruction

Exact prospective system text:

> Choose the allowed action with the highest arithmetic mean of its verified prior outcomes. For each action, compute the arithmetic mean using all verified outcomes shown for that action. Do not discard earlier outcomes and do not give extra weight to later outcomes. UNTRIED means no verified observation and has no arithmetic mean. If at least one action has verified outcomes, choose only among actions with verified outcomes. Reply with exactly one allowed action and no explanation.

No tie-breaking instruction is needed in these registered contexts. B explicitly defines the operation; it does not demonstrate spontaneous selection of that operation.

## 9. Unchanged projection

Only `state` and three opaque `action`/chronological `verified_outcomes` rows. No means, episode/epoch labels, old/new flags, arm labels, stale/current labels, current-best target, regime or Map result. All 48 matched A/B request pairs are identical except system text. Authenticated fixtures were independently reconstructed for every request; disjoint fixture source indices 1000..1095 are evaluator metadata only.

## 10. UNKNOWN semantics

All registered actions have nonempty authentic histories, so no UNTRIED marker appears. UNKNOWN remains absence of retained matching observations, not zero consequence or an event. Every allowed action remains offered; negative evidence never becomes an action ban.

## 11. Mappings/seeds

O1 K1/K2/K3 and O2 Q7/M4/Z2. All six complete mappings twice per family: j=0..11, mapping index j mod 6. Fresh seed 94001+j is shared across the four arm/condition requests and corresponding families. Each mapping/seed and parsed pair appears below and in compact results. No semantic arm, third vocabulary or intrinsic-token inference.

## 12. Model/config

Unchanged pinned dolphin-mixtral:latest, Ollama 0.1.16, GGUF 47B Q4_0. Every complete manifest blob verified before inference. Temperature .2, top_p .9, top_k 40, num_ctx 2048, repeat_penalty 1.1, num_predict 16. Stateless requests, no returned-context/chat reuse, no weights changed. Strict inherited opaque parser; no extraction, repair, retry or constrained decoding. No model Map or model Recovery.

## 13. Call schedule

Exactly **96 real Explorer calls**: two families × twelve schedules × two arms × A/B. j ascending; family order alternates by j parity. CONTROL→CHANGED when (floor(j/2)+family_index) is even, reverse otherwise. Within arm, A→B when (j+family_index+arm_index) is even, reverse otherwise. Indices O1/CONTROL=0, O2/CHANGED=1. Exact [schedule/request hashes](../experiments/explorer_value_aggregation_contract_v0/schedule.json) were committed before inference and checked before every send. No retries, replacements, extra seeds or extension; server logs independently confirm 96 successful generation requests.

## 14. Validity

**96/96 valid**, 0 invalid. B’s frozen validity requirement is ≥23/24 within each family. Invalids remain in denominators and never become actions or target selections.

| Family | Arm | Condition | Valid /12 | Invalid /12 |
| --- | --- | --- | --- | --- |
| O1 | CONTROL | A | 12 | 0 |
| O1 | CONTROL | B | 12 | 0 |
| O1 | CHANGED | A | 12 | 0 |
| O1 | CHANGED | B | 12 | 0 |
| O2 | CONTROL | A | 12 | 0 |
| O2 | CONTROL | B | 12 | 0 |
| O2 | CHANGED | A | 12 | 0 |
| O2 | CHANGED | B | 12 | 0 |

## 15. CONTROL A

| Family | HOLD /12 | RETREAT /12 | ADVANCE /12 | Invalid /12 | Mean-target selections /12 |
| --- | --- | --- | --- | --- | --- |
| O1 | 12 | 0 | 0 | 0 | 12 |
| O2 | 12 | 0 | 0 | 0 | 12 |

Original contract, contemporaneous comparator; no separate A threshold.

## 16. CONTROL B

| Family | HOLD /12 | RETREAT /12 | ADVANCE /12 | Invalid /12 | Mean-target selections /12 |
| --- | --- | --- | --- | --- | --- |
| O1 | 12 | 0 | 0 | 0 | 12 |
| O2 | 12 | 0 | 0 | 0 | 12 |

Explicit-mean target HOLD; required ≥10/12 independently in each family.

## 17. CHANGED A

| Family | HOLD /12 | RETREAT /12 | ADVANCE /12 | Invalid /12 | Mean-target selections /12 |
| --- | --- | --- | --- | --- | --- |
| O1 | 8 | 2 | 2 | 0 | 2 |
| O2 | 12 | 0 | 0 | 0 | 0 |

Fresh original-contract counts are not required to reproduce historical 1/12 and 0/12 RETREAT. Prior observations remain unchanged and are not pooled.

## 18. CHANGED B

| Family | HOLD /12 | RETREAT /12 | ADVANCE /12 | Invalid /12 | Mean-target selections /12 |
| --- | --- | --- | --- | --- | --- |
| O1 | 8 | 4 | 0 | 0 | 4 |
| O2 | 10 | 2 | 0 | 0 | 2 |

Explicit-mean target RETREAT; required ≥10/12 independently in each family.

## 19. O1 A/B pairs

| j | Mapping | Seed | Arm | A | B | Sensitivity | Favorable | Reverse | Invalid pair |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | 94001 | CONTROL | HOLD | HOLD | same_action | False | False | False |
| 0 | 0 | 94001 | CHANGED | HOLD | HOLD | same_action | False | False | False |
| 1 | 1 | 94002 | CONTROL | HOLD | HOLD | same_action | False | False | False |
| 1 | 1 | 94002 | CHANGED | ADVANCE | RETREAT | ADVANCE_to_RETREAT | True | False | False |
| 2 | 2 | 94003 | CONTROL | HOLD | HOLD | same_action | False | False | False |
| 2 | 2 | 94003 | CHANGED | HOLD | HOLD | same_action | False | False | False |
| 3 | 3 | 94004 | CONTROL | HOLD | HOLD | same_action | False | False | False |
| 3 | 3 | 94004 | CHANGED | HOLD | HOLD | same_action | False | False | False |
| 4 | 4 | 94005 | CONTROL | HOLD | HOLD | same_action | False | False | False |
| 4 | 4 | 94005 | CHANGED | RETREAT | RETREAT | same_action | False | False | False |
| 5 | 5 | 94006 | CONTROL | HOLD | HOLD | same_action | False | False | False |
| 5 | 5 | 94006 | CHANGED | HOLD | HOLD | same_action | False | False | False |
| 6 | 0 | 94007 | CONTROL | HOLD | HOLD | same_action | False | False | False |
| 6 | 0 | 94007 | CHANGED | HOLD | HOLD | same_action | False | False | False |
| 7 | 1 | 94008 | CONTROL | HOLD | HOLD | same_action | False | False | False |
| 7 | 1 | 94008 | CHANGED | ADVANCE | RETREAT | ADVANCE_to_RETREAT | True | False | False |
| 8 | 2 | 94009 | CONTROL | HOLD | HOLD | same_action | False | False | False |
| 8 | 2 | 94009 | CHANGED | HOLD | HOLD | same_action | False | False | False |
| 9 | 3 | 94010 | CONTROL | HOLD | HOLD | same_action | False | False | False |
| 9 | 3 | 94010 | CHANGED | HOLD | HOLD | same_action | False | False | False |
| 10 | 4 | 94011 | CONTROL | HOLD | HOLD | same_action | False | False | False |
| 10 | 4 | 94011 | CHANGED | RETREAT | RETREAT | same_action | False | False | False |
| 11 | 5 | 94012 | CONTROL | HOLD | HOLD | same_action | False | False | False |
| 11 | 5 | 94012 | CHANGED | HOLD | HOLD | same_action | False | False | False |

| Arm | Favorable /12 | Reverse /12 | Invalid pairs | Favorable both valid | Reverse both valid |
| --- | --- | --- | --- | --- | --- |
| CONTROL | 0 | 0 | 0 | 0 | 0 |
| CHANGED | 2 | 0 | 0 | 2 | 0 |

## 20. O2 A/B pairs

| j | Mapping | Seed | Arm | A | B | Sensitivity | Favorable | Reverse | Invalid pair |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | 94001 | CONTROL | HOLD | HOLD | same_action | False | False | False |
| 0 | 0 | 94001 | CHANGED | HOLD | HOLD | same_action | False | False | False |
| 1 | 1 | 94002 | CONTROL | HOLD | HOLD | same_action | False | False | False |
| 1 | 1 | 94002 | CHANGED | HOLD | RETREAT | HOLD_to_RETREAT | True | False | False |
| 2 | 2 | 94003 | CONTROL | HOLD | HOLD | same_action | False | False | False |
| 2 | 2 | 94003 | CHANGED | HOLD | HOLD | same_action | False | False | False |
| 3 | 3 | 94004 | CONTROL | HOLD | HOLD | same_action | False | False | False |
| 3 | 3 | 94004 | CHANGED | HOLD | HOLD | same_action | False | False | False |
| 4 | 4 | 94005 | CONTROL | HOLD | HOLD | same_action | False | False | False |
| 4 | 4 | 94005 | CHANGED | HOLD | HOLD | same_action | False | False | False |
| 5 | 5 | 94006 | CONTROL | HOLD | HOLD | same_action | False | False | False |
| 5 | 5 | 94006 | CHANGED | HOLD | HOLD | same_action | False | False | False |
| 6 | 0 | 94007 | CONTROL | HOLD | HOLD | same_action | False | False | False |
| 6 | 0 | 94007 | CHANGED | HOLD | HOLD | same_action | False | False | False |
| 7 | 1 | 94008 | CONTROL | HOLD | HOLD | same_action | False | False | False |
| 7 | 1 | 94008 | CHANGED | HOLD | RETREAT | HOLD_to_RETREAT | True | False | False |
| 8 | 2 | 94009 | CONTROL | HOLD | HOLD | same_action | False | False | False |
| 8 | 2 | 94009 | CHANGED | HOLD | HOLD | same_action | False | False | False |
| 9 | 3 | 94010 | CONTROL | HOLD | HOLD | same_action | False | False | False |
| 9 | 3 | 94010 | CHANGED | HOLD | HOLD | same_action | False | False | False |
| 10 | 4 | 94011 | CONTROL | HOLD | HOLD | same_action | False | False | False |
| 10 | 4 | 94011 | CHANGED | HOLD | HOLD | same_action | False | False | False |
| 11 | 5 | 94012 | CONTROL | HOLD | HOLD | same_action | False | False | False |
| 11 | 5 | 94012 | CHANGED | HOLD | HOLD | same_action | False | False | False |

| Arm | Favorable /12 | Reverse /12 | Invalid pairs | Favorable both valid | Reverse both valid |
| --- | --- | --- | --- | --- | --- |
| CONTROL | 0 | 0 | 0 | 0 | 0 |
| CHANGED | 2 | 0 | 0 | 2 | 0 |

## 21. Output sensitivity

| Family | Arm | A→B class | Pairs /12 |
| --- | --- | --- | --- |
| O1 | CONTROL | same_action | 12 |
| O1 | CONTROL | HOLD_to_RETREAT | 0 |
| O1 | CONTROL | ADVANCE_to_RETREAT | 0 |
| O1 | CONTROL | RETREAT_to_HOLD | 0 |
| O1 | CONTROL | RETREAT_to_ADVANCE | 0 |
| O1 | CONTROL | other | 0 |
| O1 | CONTROL | invalid_in_pair | 0 |
| O1 | CHANGED | same_action | 10 |
| O1 | CHANGED | HOLD_to_RETREAT | 0 |
| O1 | CHANGED | ADVANCE_to_RETREAT | 2 |
| O1 | CHANGED | RETREAT_to_HOLD | 0 |
| O1 | CHANGED | RETREAT_to_ADVANCE | 0 |
| O1 | CHANGED | other | 0 |
| O1 | CHANGED | invalid_in_pair | 0 |
| O2 | CONTROL | same_action | 12 |
| O2 | CONTROL | HOLD_to_RETREAT | 0 |
| O2 | CONTROL | ADVANCE_to_RETREAT | 0 |
| O2 | CONTROL | RETREAT_to_HOLD | 0 |
| O2 | CONTROL | RETREAT_to_ADVANCE | 0 |
| O2 | CONTROL | other | 0 |
| O2 | CONTROL | invalid_in_pair | 0 |
| O2 | CHANGED | same_action | 10 |
| O2 | CHANGED | HOLD_to_RETREAT | 2 |
| O2 | CHANGED | ADVANCE_to_RETREAT | 0 |
| O2 | CHANGED | RETREAT_to_HOLD | 0 |
| O2 | CHANGED | RETREAT_to_ADVANCE | 0 |
| O2 | CHANGED | other | 0 |
| O2 | CHANGED | invalid_in_pair | 0 |

Invalid-containing pairs are explicitly separated within other and never called action transitions. Primary CHANGED favorable means A≠RETREAT and B=RETREAT; reverse A=RETREAT and B≠RETREAT. Invalid is never a target selection, so invalid A/correct B counts favorable and correct A/invalid B counts reverse under the prospectively stated rule. Both-valid sensitivity counts are also shown and do not replace primary counts. CONTROL pairs are descriptive against their HOLD target.

## 22. O1 primary criterion

**EXPLICIT-MEAN EXPLORER POLICY NOT ESTABLISHED**

| Frozen criterion | Passed |
| --- | --- |
| all_B_calls_complete | yes |
| B_valid_at_least_23 | yes |
| CONTROL_B_HOLD_at_least_10 | yes |
| CHANGED_B_RETREAT_at_least_10 | NO |
| CHANGED_favorable_at_least_8 | NO |
| CHANGED_reverse_at_most_1 | yes |
| histories_authentic | yes |
| old_and_new_records_unchanged | yes |
| model_sampler_parser_integrity | yes |
| exact_replay | yes |

Failed gates: CHANGED_B_RETREAT_at_least_10, CHANGED_favorable_at_least_8.

## 23. O2 primary criterion

**EXPLICIT-MEAN EXPLORER POLICY NOT ESTABLISHED**

| Frozen criterion | Passed |
| --- | --- |
| all_B_calls_complete | yes |
| B_valid_at_least_23 | yes |
| CONTROL_B_HOLD_at_least_10 | yes |
| CHANGED_B_RETREAT_at_least_10 | NO |
| CHANGED_favorable_at_least_8 | NO |
| CHANGED_reverse_at_most_1 | yes |
| histories_authentic | yes |
| old_and_new_records_unchanged | yes |
| model_sampler_parser_integrity | yes |
| exact_replay | yes |

Failed gates: CHANGED_B_RETREAT_at_least_10, CHANGED_favorable_at_least_8.

## 24. Overall decision

**EXPLICIT-MEAN EXPLORER POLICY NOT ESTABLISHED**

Both families must pass separately. No pooling, relaxed threshold or extra sample. The old Explorer NOT ESTABLISHED and old Map REPLICATED decisions remain unchanged.

## 25. Provenance

All 96 independently constructed systems passed full original-receipt and actual-execution binding checks before/after the measured request. Epoch 1002, external/authorized state 1, all eight records authenticated, source lifetime unchanged through the zero-event reset, no fake RESET observation. All 768 setup events committed normally. Native Measure recorded 96 consequence/prediction mismatches in CHANGED construction while HOLD self-loop state stayed valid; state Recovery 0, measurement Recovery 0. Native behavior was observed, not forced or suppressed. Measured proposals never execute, create receipts or modify Memory.

## 26. Memory preservation

All six episode-1 and two episode-2 events stay present, with their original epoch/transaction identity and receipts. No event deletion, relabeling, rewriting or eviction; no bound enlargement. The old +1 HOLD remains true history alongside the two new −1 events in CHANGED. Full protected snapshots remain unchanged through each measured probe. Every live construction record is byte-identical to its pre-inference counterpart.

## 27. Exact replay

All 96 saved responses replayed with sockets forbidden and zero inference. Actual authenticated fixtures, projections, A/B system text, exact requests, parsing, exact mean arithmetic, targets, pairs, sensitivity, gates and final decision were reconstructed. Eight registered files and 96 snapshots are byte-identical; finalized live/replay results also match. Independent audit rechecked arithmetic directly from protected Memory and all paired counts. Provisional raw metrics remain unmodified; replay is only marked passed after executed verification.

## 28. Historical preservation

Nine historical zero-inference replays passed: parent Explorer revision, Map revision, stale-Memory feasibility, history depth, transfer, initialization, Map ablation, R1 and realized-event grounding. Twenty preflight tests and 67 historical tests passed. All 584 inherited substantive files are byte-identical; ten prior private archive checksum inventories passed. Explorer negative remains NOT ESTABLISHED in both families, Map REPLICATED, historical Explorer transfer SUPPORTED, depth SUPPORTED, feasibility/initialization A, ablation SUPPORTED and R1 A. Grounding/contradiction, UNKNOWN and representation checkpoints remain unchanged. Main, tags and previous refs remain untouched; nothing pushed. [Verification](../experiments/explorer_value_aggregation_contract_v0/verification.json) records actual executions and hashes.

## 29. Limitations

One pinned model, two opaque vocabularies, twelve matched seeds per family and two fixed P2 contexts with unique arithmetic-mean targets. Seeds are reused across matched conditions and families, not independent population samples. No ties, UNTRIED selection, arbitrary list lengths, additional worlds or policy generalization are tested. B changes the complete specified instruction, including explicit aggregation and associated all-outcome/weighting clauses; this comparison does not isolate a single clause or internal computation. Correct choices alone do not establish that the model internally calculated a mean. No proposal executes, so realized returns and closed-loop adaptation are untested. Trusted external source, registry and simulator reset remain authority boundaries.

## 30. Narrowest defensible conclusion

The explicit-mean Explorer policy claim is not established under the frozen rule. O1: CHANGED_B_RETREAT_at_least_10, CHANGED_favorable_at_least_8; O2: CHANGED_B_RETREAT_at_least_10, CHANGED_favorable_at_least_8. The historical original-contract negative result remains intact. This study does not establish spontaneous stale-Memory adaptation, persistent policy learning, RL, internal belief revision, natural mean computation, universal correctness of arithmetic mean, AGI or RSI. It does not identify the sole cause of the earlier failure.

## 31. Recommendation

Stop after the registered 96 calls, replay and preservation. Review the family gates, matched A/B outcomes, CONTROL behavior and invalid-pair sensitivity before choosing any separately authorized next question. No automatic full composition, recency instruction, additional negative observation, historical re-scoring or follow-up campaign.
