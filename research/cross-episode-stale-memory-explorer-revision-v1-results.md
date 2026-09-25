# Cross-episode stale-Memory Explorer revision v1 — results

**CROSS-EPISODE STALE-MEMORY EXPLORER REVISION NOT ESTABLISHED**. Exactly 144 Explorer calls; 144/144 valid. Exact replay and historical preservation passed.

| Family | CHANGED P0 HOLD /12 | CHANGED P2 RETREAT /12 | CONTROL P2 HOLD /12 | Favorable /12 | Reverse /12 | Supported |
| --- | --- | --- | --- | --- | --- | --- |
| O1 | 12 | 1 | 12 | 1 | 0 | False |
| O2 | 12 | 0 | 12 | 0 | 0 | False |

## 1. Parent Map revision result

Parent `research/cross-episode-stale-memory-map-revision-v1`, `82e04f31a8a532547e4a1858ef22643dd1986843`, remains **CROSS-EPISODE STALE-MEMORY MAP REVISION REPLICATED**. New Explorer-only branch: `research/cross-episode-stale-memory-explorer-revision-v1`. Preregistration commit `c833f9a95092b98a0ac154301fae90229334dcd9` preceded inference; all request hashes and scientific files remained frozen.

## 2. Exact research question

Can a stateless Explorer change its proposal from formerly best HOLD toward RETREAT after authentic fresh-episode HOLD consequences turn negative, relative to matched stationary CONTROL, while older true observations remain present? This tests input-conditioned proposals without action execution.

## 3. CONTROL/CHANGED worlds

CONTROL retains every original relation. After initialization, CHANGED alters only state-1 HOLD consequence +1→−1. HOLD remains 1→1. All transitions and other outcomes remain unchanged, independently checked across all twelve state/action combinations. Arm/change labels are evaluator metadata only.

## 4. State-1 value structure

Original state-1 outcomes: HOLD→(1,+1), RETREAT→(0,0), ADVANCE→(2,−1), ranking HOLD > RETREAT > ADVANCE. Current changed-world consequences rank RETREAT 0 > HOLD −1 = ADVANCE −1. No ranking or current-best label appears in the prompt.

## 5. Episode-1 authenticated history

Each independent context starts at state 1 and executes epoch-1001 transactions: tx1 HOLD 1→1,+1; tx2 RETREAT 1→0,0; tx3 ADVANCE 0→1,+1; tx4 ADVANCE 1→2,−1; tx5 RETREAT 2→1,+1; tx6 RETREAT 1→0,0. All six events use ordinary external execution, authentic receipts, Measure, authorization and Memory publication. Navigation tx3/tx5 stays in protected Memory but is mechanically excluded from current-state-1 histories.

## 6. Fresh episode boundary

Unchanged trusted `start_episode(1002,1)` genuinely resets external and authorized current state 0→1. Source lifetime and all six original receipt/package objects survive. Every initialization creates zero events, receipts or Memory entries; no RESET pseudo-event.

## 7. External change timing

Capture the initialized P0 state/history first; then change only CHANGED’s external HOLD consequence before any epoch-1002 event or measured request. The intervention leaves framework/history snapshots unchanged and creates no pseudo-event. CONTROL remains stationary. The model receives no regime flag.

## 8. P0 histories

Both arms: HOLD [+1], RETREAT [0,0], ADVANCE [−1]. Full Memory length six, current state 1, epoch 1002. All 24 same-family/schedule P0 request pairs are byte-identical. No newly negative HOLD observation exists at P0; old HOLD remains the preregistered preference prerequisite.

## 9. P1 histories

One ordinary epoch-1002 HOLD, transaction 1, yields CONTROL HOLD [+1,+1] versus CHANGED [+1,−1]. RETREAT [0,0] and ADVANCE [−1] remain unchanged. Current state remains 1; Memory length seven. P1 is descriptive and intentionally ambiguous under different evidence-use rules.

## 10. P2 histories

A second ordinary HOLD, epoch 1002 transaction 2, yields CONTROL [+1,+1,+1] versus CHANGED [+1,−1,−1]. RETREAT [0,0], ADVANCE [−1]. Current state 1, Memory exactly eight, no eviction or bound enlargement. The primary fixture stops here.

## 11. Explorer projection

The unchanged generalized projection contains only `state` and three `actions`, each with opaque `action` and chronological `verified_outcomes`. No epochs, source/event/package identity, regime/stale tags, averages, recommendations, Map predictions or Recovery metadata. The unchanged exact system instruction is in the [preregistration](cross-episode-stale-memory-explorer-revision-v1-preregistration.md).

## 12. UNKNOWN semantics

All three actions have retained authentic state-1 evidence at every stage; none renders UNTRIED. UNKNOWN remains absence of retained matching observations, never a stored event or consequence zero. Old +1 remains a true historical observation. Negative outcomes do not ban an action or remove it from the offered action set.

## 13. Model/config

Pinned dolphin-mixtral:latest, Ollama 0.1.16, GGUF 47B Q4_0. All five complete model blobs verified before inference. Temperature .2, top_p .9, top_k 40, num_predict 16, num_ctx 2048, repeat_penalty 1.1. No weight changes, chat persistence or returned-context reuse. Strict inherited alias parser; no extraction, coercion, repair, retry or constrained decoding. Undocumented runtime internals are not separately audited.

## 14. Mappings/seeds

O1 K1/K2/K3; O2 Q7/M4/Z2. j=0..11; all six complete mappings twice per family, index j mod 6. Seed 93001+j, matched across both arms/all three stages and corresponding families. Alias breakdown below is descriptive (four schedules per HOLD alias); mapping/seed details are in all trajectory tables. No intrinsic-token mechanism or neutrality claim.

| Family | HOLD alias | CHANGED P0 HOLD /4 | CHANGED P2 RETREAT /4 | CONTROL P2 HOLD /4 |
| --- | --- | --- | --- | --- |
| O1 | K1 | 4 | 0 | 4 |
| O1 | K2 | 4 | 0 | 4 |
| O1 | K3 | 4 | 1 | 4 |
| O2 | M4 | 4 | 0 | 4 |
| O2 | Q7 | 4 | 0 | 4 |
| O2 | Z2 | 4 | 0 | 4 |

## 15. Call schedule

Exactly **144 real Explorer calls**, zero model Map and zero model Recovery. Independent fixture per request. j ascends; even j O1→O2, odd j O2→O1. Within family P0→P1→P2; even (j+family_index+stage_index) CONTROL→CHANGED, odd reverses. Exact [144-entry annex](../experiments/cross_episode_stale_memory_explorer_revision_v1/schedule.json) was committed before inference and checked before every send. No retries, replacements, extra seeds or extension. Server logs independently confirm 144 successful generation requests. Every measured proposal remained read-only.

## 16. Validity

**144/144 valid**; 0 invalid. Frozen gate: ≥140/144 globally and ≥11/12 in every family × arm × stage cell. All invalids remain in denominators.

| Family | Arm | Stage | Valid /12 | Invalid /12 |
| --- | --- | --- | --- | --- |
| O1 | CONTROL | P0 | 12 | 0 |
| O1 | CONTROL | P1 | 12 | 0 |
| O1 | CONTROL | P2 | 12 | 0 |
| O1 | CHANGED | P0 | 12 | 0 |
| O1 | CHANGED | P1 | 12 | 0 |
| O1 | CHANGED | P2 | 12 | 0 |
| O2 | CONTROL | P0 | 12 | 0 |
| O2 | CONTROL | P1 | 12 | 0 |
| O2 | CONTROL | P2 | 12 | 0 |
| O2 | CHANGED | P0 | 12 | 0 |
| O2 | CHANGED | P1 | 12 | 0 |
| O2 | CHANGED | P2 | 12 | 0 |

## 17. P0 old preference O1

CHANGED P0 HOLD **12/12**, required ≥10/12. CONTROL P0 HOLD 12/12. Old HOLD is the required prior preference even though CHANGED's hidden external law has changed. It is not labeled irrational.

## 18. P0 old preference O2

CHANGED P0 HOLD **12/12**, required ≥10/12. CONTROL P0 HOLD 12/12. Old HOLD is the required prior preference even though CHANGED's hidden external law has changed. It is not labeled irrational.

## 19. CONTROL trajectories O1

| j | Mapping | Seed | HOLD alias | RETREAT alias | P0 → P1 → P2 | Path class |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | 93001 | K2 | K3 | HOLD → HOLD → HOLD | HOLD_throughout |
| 1 | 1 | 93002 | K3 | K2 | HOLD → HOLD → HOLD | HOLD_throughout |
| 2 | 2 | 93003 | K1 | K3 | HOLD → HOLD → HOLD | HOLD_throughout |
| 3 | 3 | 93004 | K1 | K2 | HOLD → HOLD → HOLD | HOLD_throughout |
| 4 | 4 | 93005 | K3 | K1 | HOLD → HOLD → HOLD | HOLD_throughout |
| 5 | 5 | 93006 | K2 | K1 | HOLD → HOLD → HOLD | HOLD_throughout |
| 6 | 0 | 93007 | K2 | K3 | HOLD → HOLD → HOLD | HOLD_throughout |
| 7 | 1 | 93008 | K3 | K2 | HOLD → HOLD → HOLD | HOLD_throughout |
| 8 | 2 | 93009 | K1 | K3 | HOLD → HOLD → HOLD | HOLD_throughout |
| 9 | 3 | 93010 | K1 | K2 | HOLD → HOLD → HOLD | HOLD_throughout |
| 10 | 4 | 93011 | K3 | K1 | HOLD → HOLD → HOLD | HOLD_throughout |
| 11 | 5 | 93012 | K2 | K1 | HOLD → HOLD → HOLD | HOLD_throughout |

## 20. CONTROL trajectories O2

| j | Mapping | Seed | HOLD alias | RETREAT alias | P0 → P1 → P2 | Path class |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | 93001 | M4 | Z2 | HOLD → HOLD → HOLD | HOLD_throughout |
| 1 | 1 | 93002 | Z2 | M4 | HOLD → HOLD → HOLD | HOLD_throughout |
| 2 | 2 | 93003 | Q7 | Z2 | HOLD → HOLD → HOLD | HOLD_throughout |
| 3 | 3 | 93004 | Q7 | M4 | HOLD → HOLD → HOLD | HOLD_throughout |
| 4 | 4 | 93005 | Z2 | Q7 | HOLD → HOLD → HOLD | HOLD_throughout |
| 5 | 5 | 93006 | M4 | Q7 | HOLD → HOLD → HOLD | HOLD_throughout |
| 6 | 0 | 93007 | M4 | Z2 | HOLD → HOLD → HOLD | HOLD_throughout |
| 7 | 1 | 93008 | Z2 | M4 | HOLD → HOLD → HOLD | HOLD_throughout |
| 8 | 2 | 93009 | Q7 | Z2 | HOLD → HOLD → HOLD | HOLD_throughout |
| 9 | 3 | 93010 | Q7 | M4 | HOLD → HOLD → HOLD | HOLD_throughout |
| 10 | 4 | 93011 | Z2 | Q7 | HOLD → HOLD → HOLD | HOLD_throughout |
| 11 | 5 | 93012 | M4 | Q7 | HOLD → HOLD → HOLD | HOLD_throughout |

## 21. CHANGED trajectories O1

| j | Mapping | Seed | HOLD alias | RETREAT alias | P0 → P1 → P2 | Path class |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | 93001 | K2 | K3 | HOLD → HOLD → HOLD | HOLD_throughout |
| 1 | 1 | 93002 | K3 | K2 | HOLD → ADVANCE → ADVANCE | other |
| 2 | 2 | 93003 | K1 | K3 | HOLD → HOLD → HOLD | HOLD_throughout |
| 3 | 3 | 93004 | K1 | K2 | HOLD → HOLD → HOLD | HOLD_throughout |
| 4 | 4 | 93005 | K3 | K1 | HOLD → RETREAT → RETREAT | HOLD_to_RETREAT_at_P1 |
| 5 | 5 | 93006 | K2 | K1 | HOLD → HOLD → HOLD | HOLD_throughout |
| 6 | 0 | 93007 | K2 | K3 | HOLD → HOLD → HOLD | HOLD_throughout |
| 7 | 1 | 93008 | K3 | K2 | HOLD → ADVANCE → ADVANCE | other |
| 8 | 2 | 93009 | K1 | K3 | HOLD → HOLD → HOLD | HOLD_throughout |
| 9 | 3 | 93010 | K1 | K2 | HOLD → HOLD → HOLD | HOLD_throughout |
| 10 | 4 | 93011 | K3 | K1 | HOLD → HOLD → HOLD | HOLD_throughout |
| 11 | 5 | 93012 | K2 | K1 | HOLD → HOLD → HOLD | HOLD_throughout |

## 22. CHANGED trajectories O2

| j | Mapping | Seed | HOLD alias | RETREAT alias | P0 → P1 → P2 | Path class |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | 93001 | M4 | Z2 | HOLD → HOLD → HOLD | HOLD_throughout |
| 1 | 1 | 93002 | Z2 | M4 | HOLD → HOLD → HOLD | HOLD_throughout |
| 2 | 2 | 93003 | Q7 | Z2 | HOLD → HOLD → HOLD | HOLD_throughout |
| 3 | 3 | 93004 | Q7 | M4 | HOLD → HOLD → HOLD | HOLD_throughout |
| 4 | 4 | 93005 | Z2 | Q7 | HOLD → HOLD → HOLD | HOLD_throughout |
| 5 | 5 | 93006 | M4 | Q7 | HOLD → HOLD → HOLD | HOLD_throughout |
| 6 | 0 | 93007 | M4 | Z2 | HOLD → HOLD → HOLD | HOLD_throughout |
| 7 | 1 | 93008 | Z2 | M4 | HOLD → HOLD → ADVANCE | other |
| 8 | 2 | 93009 | Q7 | Z2 | HOLD → HOLD → HOLD | HOLD_throughout |
| 9 | 3 | 93010 | Q7 | M4 | HOLD → HOLD → HOLD | HOLD_throughout |
| 10 | 4 | 93011 | Z2 | Q7 | HOLD → HOLD → HOLD | HOLD_throughout |
| 11 | 5 | 93012 | M4 | Q7 | HOLD → HOLD → HOLD | HOLD_throughout |

## 23. Matched P2 O1

| j | CONTROL P2 | CHANGED P2 | Favorable | Reverse |
| --- | --- | --- | --- | --- |
| 0 | HOLD | HOLD | False | False |
| 1 | HOLD | ADVANCE | False | False |
| 2 | HOLD | HOLD | False | False |
| 3 | HOLD | HOLD | False | False |
| 4 | HOLD | RETREAT | True | False |
| 5 | HOLD | HOLD | False | False |
| 6 | HOLD | HOLD | False | False |
| 7 | HOLD | ADVANCE | False | False |
| 8 | HOLD | HOLD | False | False |
| 9 | HOLD | HOLD | False | False |
| 10 | HOLD | HOLD | False | False |
| 11 | HOLD | HOLD | False | False |

Totals: {'favorable': 1, 'reverse': 0}.

## 24. Matched P2 O2

| j | CONTROL P2 | CHANGED P2 | Favorable | Reverse |
| --- | --- | --- | --- | --- |
| 0 | HOLD | HOLD | False | False |
| 1 | HOLD | HOLD | False | False |
| 2 | HOLD | HOLD | False | False |
| 3 | HOLD | HOLD | False | False |
| 4 | HOLD | HOLD | False | False |
| 5 | HOLD | HOLD | False | False |
| 6 | HOLD | HOLD | False | False |
| 7 | HOLD | ADVANCE | False | False |
| 8 | HOLD | HOLD | False | False |
| 9 | HOLD | HOLD | False | False |
| 10 | HOLD | HOLD | False | False |
| 11 | HOLD | HOLD | False | False |

Totals: {'favorable': 0, 'reverse': 0}.

## 25. P1 descriptive result

| Family | Arm | HOLD | RETREAT | ADVANCE | Invalid |
| --- | --- | --- | --- | --- | --- |
| O1 | CONTROL | 12 | 0 | 0 | 0 |
| O1 | CHANGED | 9 | 1 | 2 | 0 |
| O2 | CONTROL | 12 | 0 | 0 | 0 |
| O2 | CHANGED | 12 | 0 | 0 | 0 |

Denominator twelve per row. No P1 success threshold; these outcomes do not rescue failed primary gates.

## 26. Revision latency

| Family | P1 | P2 | Never | Excluded: no HOLD P0 |
| --- | --- | --- | --- | --- |
| O1 | 1 | 0 | 11 | 0 |
| O2 | 0 | 0 | 12 | 0 |

Only CHANGED schedules selecting HOLD at P0 are eligible. First later RETREAT is P1, else P2, else never. These trajectories join independently reconstructed stateless requests, not one model retaining an internal belief. Invalids and later reversals remain visible. No internal threshold is inferred.

## 27. Value-evidence analysis

| Stage | CONTROL HOLD | CHANGED HOLD | RETREAT both | ADVANCE both |
| --- | --- | --- | --- | --- |
| P0 | [+1] | [+1] | [0,0] | [−1] |
| P1 | [+1,+1] | [+1,−1] | [0,0] | [−1] |
| P2 | [+1,+1,+1] | [+1,−1,−1] | [0,0] | [−1] |

Evaluator-only empirical means: P0 HOLD +1, RETREAT 0, ADVANCE −1; CHANGED P1 HOLD 0 ties RETREAT 0; CHANGED P2 HOLD −1/3 < RETREAT 0, with ADVANCE −1. Means are absent from prompts. The study does not establish that the model averaged, preferred recency, inferred causality or used any particular internal evidence rule.

## 28. Current-world action accuracy

| Family | Arm | Stage | Current-best proposals /12 |
| --- | --- | --- | --- |
| O1 | CONTROL | P0 | 12 |
| O1 | CONTROL | P1 | 12 |
| O1 | CONTROL | P2 | 12 |
| O1 | CHANGED | P0 | 0 |
| O1 | CHANGED | P1 | 1 |
| O1 | CHANGED | P2 | 1 |
| O2 | CONTROL | P0 | 12 |
| O2 | CONTROL | P1 | 12 |
| O2 | CONTROL | P2 | 12 |
| O2 | CHANGED | P0 | 0 |
| O2 | CHANGED | P1 | 0 |
| O2 | CHANGED | P2 | 0 |

Secondary only: current best is CONTROL HOLD and CHANGED RETREAT after the external change. At CHANGED P0 no new evidence is visible; HOLD is the required old preference and is not irrational. The hidden current-best score comes from the registered fixture law, not a fabricated new Memory event. No measured action executes, so these are proposal counts, not realized policy rewards.

## 29. Native fixture behavior

All 1008 ordinary setup events committed authentic outcomes. The unchanged deterministic Map predicted HOLD (1,+1) even after the external change. Measure recorded **72** prediction/consequence mismatches across independent CHANGED P1/P2 construction; the actual next state remained 1. The already-valid incumbent state was retained and authentic −1 Memory published normally. Observed native state Recovery: **0**; measurement Recovery: **0**. Both are zero in every arm/stage. This preserves native behavior; no Recovery was forced or suppressed. Native metadata never entered Explorer prompts. Measured probes executed zero actions and committed zero records.

## 30. Provenance/history preservation

Before/after each measured request, all Memory→pair→package→original receipt→actual execution bindings were checked. All six old records (including navigation) survived unchanged; new negative HOLD records were appended and preserved. Epoch identities are 1001 tx1..6 and, stage appropriately, 1002 tx1/tx2. Source lifetime survives within each system; source identities differ between independently reconstructed contexts. Zero fake reset events, no eviction, no UNKNOWN target markers, no receipt rewrites or model authority. Full post-response snapshots remain equal to pre-request snapshots. All 144 live fixture evidence records also match the preflight constructions byte-for-byte.

## 31. O1 primary decision

**CROSS-EPISODE STALE-MEMORY EXPLORER REVISION NOT ESTABLISHED**

| Frozen criterion | Passed |
| --- | --- |
| CHANGED_P0_HOLD_at_least_10 | yes |
| CHANGED_P2_RETREAT_at_least_9 | NO |
| CONTROL_P2_HOLD_at_least_9 | yes |
| P2_favorable_at_least_8 | NO |
| P2_reverse_at_most_1 | yes |
| all_144_complete | yes |
| global_and_cell_validity | yes |
| histories_authentic | yes |
| old_records_present_unchanged | yes |
| new_records_present_unchanged | yes |
| framework_provenance_integrity | yes |
| exact_replay | yes |

Failed gates: CHANGED_P2_RETREAT_at_least_9, P2_favorable_at_least_8.

## 32. O2 primary decision

**CROSS-EPISODE STALE-MEMORY EXPLORER REVISION NOT ESTABLISHED**

| Frozen criterion | Passed |
| --- | --- |
| CHANGED_P0_HOLD_at_least_10 | yes |
| CHANGED_P2_RETREAT_at_least_9 | NO |
| CONTROL_P2_HOLD_at_least_9 | yes |
| P2_favorable_at_least_8 | NO |
| P2_reverse_at_most_1 | yes |
| all_144_complete | yes |
| global_and_cell_validity | yes |
| histories_authentic | yes |
| old_records_present_unchanged | yes |
| new_records_present_unchanged | yes |
| framework_provenance_integrity | yes |
| exact_replay | yes |

Failed gates: CHANGED_P2_RETREAT_at_least_9, P2_favorable_at_least_8.

## 33. Overall replication decision

**CROSS-EPISODE STALE-MEMORY EXPLORER REVISION NOT ESTABLISHED**

Both families are evaluated independently; no pooling, threshold changes or extra samples. Invalids are retained. Historical results remain separate and unchanged.

## 34. Exact replay

Replayed all 144 saved responses with sockets forbidden and zero inference. Reconstructed the actual authenticated histories, reset, change timing, projections, requests, seeds, parser outputs, counts, pairs, trajectories and latency. Eight registered files and 144 snapshots match byte-for-byte. Finalized live/replay results also match. An independent verifier checked scores, all decision gates, fixture provenance and server request count. Original provisional raw metrics were retained without rewriting; the final replay gate is set only after executed replay passes.

## 35. Historical preservation

Eight historical zero-inference replays passed: parent Map revision, stale-Memory feasibility, history depth, transfer, initialization, Map ablation, R1 and realized-event grounding. Nineteen preflight tests and 67 historical tests passed. All 572 inherited substantive files remain byte-identical; nine prior private archives passed checksum verification. Map revision remains REPLICATED, feasibility A, history depth SUPPORTED, transfer historical overall NOT ESTABLISHED with Explorer SUPPORTED, initialization A, ablation SUPPORTED and R1 A. Prior contradiction/grounding, representation checkpoint and UNKNOWN semantics remain untouched. Main, tags and prior refs are preserved; nothing pushed. The initial preflight command had a misspelled durability module; its import-error log was retained, the corrected command passed, and no scientific code or fixture was patched. [Verification](../experiments/cross_episode_stale_memory_explorer_revision_v1/verification.json) records actual executions and hashes.

## 36. Limitations

One pinned model, two opaque vocabularies, twelve matched seeds per family, a single external consequence change, two episodes and at most eight retained events. Seeds repeat across arms/stages and corresponding families; this is a matched design, not independent population sampling. The generalized Explorer schema does not expose epochs; this tests retained cross-episode evidence, not model recognition of an episode boundary. P1 is descriptive. No chosen action executes, so retesting, realized return, long-horizon action selection and closed-loop adaptation are not tested. Chronology and empirical values coexist without isolating a reasoning mechanism. Trusted source, registry and in-process initialization remain the authority boundary.

## 37. Narrowest defensible conclusion

The frozen cross-episode Explorer revision claim is not established. O1: CHANGED_P2_RETREAT_at_least_9, P2_favorable_at_least_8; O2: CHANGED_P2_RETREAT_at_least_9, P2_favorable_at_least_8. The earlier Map revision result remains a separate supported checkpoint; it does not establish Explorer action-preference revision. This concerns input-conditioned action proposals only. It establishes no persistent learning, reinforcement/policy learning, internal belief revision, general drift detection, weight learning, AGI or RSI.

## 38. Recommendation

Stop after this registered campaign, replay and preservation. Inspect the separate family gates, CONTROL drift, invalids, P1 ambiguity and conditional latency before choosing any separately authorized next question. No composed adaptation, extra value sample, recency teaching, Memory/world enlargement or automatic follow-up campaign.
