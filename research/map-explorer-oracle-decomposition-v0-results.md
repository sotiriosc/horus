# Map–Explorer oracle decomposition v0 results

**PIPELINE NOT FULLY ESTABLISHED**

All three primary stage criteria are **NOT ESTABLISHED** in both families. Oracle Explorer scored **21/24 (O1)** and **17/24 (O2)**, but D1 failed at **3/6** and **2/6**. Map produced **19/48 ties**. Model-Map Explorer had **15/24** and **14/24** eligible contexts; all issued responses were valid, with following-Map scores **13/15** and **9/14**. Its support failure includes insufficient eligibility, not invalid responses. End-to-end true-best selection was **11/24** and **7/24**.

The campaign completed **269 calls (240 mandatory + 29 conditional)**. Exact replay, **95 tests** and **12 historical replays** passed. The earlier temporal-negative result remains unchanged.

## 1. Parent temporal-negative result

Parent `5781473435c1fc5eadf53e80edc44259796e6610`; preregistration `a54b617c3ae2ef0641466c839918ae30e834845d`. **MAP TEMPORAL-RELATION FORECASTING BEYOND PURE RECENCY NOT ESTABLISHED** remains unchanged. Earlier transient and periodic failures are not reinterpreted by this simpler current-relation study.

## 2. Exact decomposition question

Can Explorer choose the current true-best action from accurate finite forecasts? How often does Map rank that action highest, and what changes when Explorer receives those real forecasts? A separate next-state control tests matched behavioral invariance with the specified distinct seeds.

## 3. Four world contexts

W0 state 0 has ADVANCE→(1,+1), HOLD→(0,0), RETREAT→(3,-1), best ADVANCE. W1 state 1 has ADVANCE→(2,-1), HOLD→(1,+1), RETREAT→(0,0), best HOLD. W3 state 3 has ADVANCE→(0,-1), HOLD→(3,0), RETREAT→(2,+1), best RETREAT. D1 state 1 changes only HOLD consequence to -1, leaving RETREAT uniquely best at 0. These registered outcome tables audit construction; detached world execution supplies evaluation values.

## 4. Authenticated fixture construction

Stationary contexts use the registered five-event navigation sequences and end in their starting state. D1 reuses the preserved six-event episode 1 fixture, trusted initialization to epoch 1002/state 1, and two authentic changed HOLD events. All setup observations originate from ordinary execution, authentic original receipt, Measure, authorization and Memory. Five or eight records remain within unchanged bounds with no eviction. Every current-state legal action has exact-pair history; no UNTRIED/empty input.

## 5. Current-world oracle definition

For each action, independently copy the current external world and execute that action once on the detached copy. The resulting finite next_state/consequence forms the oracle forecast. This is not aggregation or manually supplied scoring. Each copy starts from the same context. Detached evaluation mints no receipt, changes no live world or Memory, and grants no authority.

## 6. No-leak ordering

Freeze all three Map requests first; durably record and strict-parse ADVANCE, HOLD, RETREAT once each; feed the recorded real outputs through unchanged interface-v0; only then evaluate detached world outcomes. World execution is forbidden during Map and Explorer calls. Original snapshots/provenance remain equal. Oracle construction never repairs a forecast or enters a Map prompt.

## 7. Map prompt/parser

Exact established explicit finite-JSON Map instruction and unchanged strict historical parser; see [preregistration](map-explorer-oracle-decomposition-v0-preregistration.md). Each request contains state, opaque target_action and only its authenticated chronological exact-pair history. Original parsed forecasts remain unmodified, including incorrect values. All three mandatory responses are recorded before interface binding; malformed output blocks the composed arm without suppressing the other mandatory Map diagnostics.

## 8. Explorer forecast prompt/parser

Exact interface-v0 instruction: choose the allowed action with highest current Map predicted consequence; reply only with one allowed token. Historical strict opaque parser unchanged. No truth label, evidence counts, confidence, rationale, averages or hints. Invalid response gets no retry.

## 9. Forecast view

Exactly state plus three actions rows containing action and map_prediction {next_state, consequence}. Row order follows the frozen mapping. Oracle and ModelMap use the same schema; ModelMap values are exactly the original parsed forecasts. Source identity and authority capabilities never enter Explorer.

## 10. Evidence-blind decision

Explorer sees no history or depth fields. Every primary action has authenticated evidence. W0/W1/W3 exact-pair depths are one per action; D1 depths are ADVANCE 1, HOLD 3, RETREAT 2. Depth is recorded for diagnosis only; no evidence-aware action policy was added.

## 11. Tie policy

Unchanged interface-v0: a shared maximum produces TIED_MAXIMUM and no Explorer invocation. Invalid/missing collection also blocks composed Explorer. No tie-break, replacement or unqueried forecast. Mandatory oracle-based calls still occur. Unissued conditional slots are preserved exactly in replay.

## 12. Representation mappings

O1 K1/K2/K3 and O2 Q7/M4/Z2 each use all six complete historical mappings once per world. There are 48 matched contexts. Mapping identity and every action-level forecast/alias appear in [results.json](../experiments/map_explorer_oracle_decomposition_v0/results.json).

## 13. Seeds

base=96001+100*w+10*j. Map ADVANCE/HOLD/RETREAT use +1/+2/+3; Oracle +4; Permutation +5; ModelMap +6. Corresponding family seeds match. The distinct base/permutation seeds limit attribution of any choice change solely to next_state.

## 14. Call schedule / issued counts

World order W0,W1,W3,D1; mappings ascending; family order alternates by w+j parity. Map canonical order first; Oracle/Permutation order counterbalanced by context index; eligible ModelMap last. **240 mandatory calls** = 144 Map + 48 Oracle Explorer + 48 permutation Explorer. **29 eligible, 29 conditional calls, 269 total**. Unissued tie slots 19; invalid-Map slots 0. No retries/replacements/extensions. Pinned dolphin-mixtral:latest, Ollama 0.1.16, GGUF 47B Q4_0; all model blobs fully verified. Historical sampler unchanged: .2/.9/40/2048/1.1, num_predict 32 Map / 16 Explorer, stateless.

## 15. Map validity

| Family | Map calls | Valid /72 |
|---|---|---|
| O1 | 72 | 72 |
| O2 | 72 | 72 |

## 16. Map action-level accuracy

| Family | World | Map n | Valid | Exact | State correct | Consequence correct |
|---|---|---|---|---|---|---|
| O1 | D1 | 18 | 18 | 16 | 17 | 17 |
| O1 | W0 | 18 | 18 | 15 | 18 | 15 |
| O1 | W1 | 18 | 18 | 11 | 17 | 12 |
| O1 | W3 | 18 | 18 | 15 | 15 | 15 |
| O2 | D1 | 18 | 18 | 17 | 17 | 18 |
| O2 | W0 | 18 | 18 | 14 | 18 | 14 |
| O2 | W1 | 18 | 18 | 10 | 16 | 12 |
| O2 | W3 | 18 | 18 | 13 | 13 | 13 |

All 144 individual forecast rows retain world, action, alias, mapping, parsed forecast, detached actual outcome and separate exact/state/consequence scores. Compact evidence includes aggregates by underlying action, alias, world and mapping; no hidden-truth repair.

## 17. W0 Map ranking

| Family | Unique max | True-best unique | Wrong unique | Tie | Invalid/missing |
|---|---|---|---|---|---|
| O1 | 3 | 3 | 0 | 3 | 0 |
| O2 | 2 | 2 | 0 | 4 | 0 |

## 18. W1 Map ranking

| Family | Unique max | True-best unique | Wrong unique | Tie | Invalid/missing |
|---|---|---|---|---|---|
| O1 | 0 | 0 | 0 | 6 | 0 |
| O2 | 0 | 0 | 0 | 6 | 0 |

## 19. W3 Map ranking

| Family | Unique max | True-best unique | Wrong unique | Tie | Invalid/missing |
|---|---|---|---|---|---|
| O1 | 6 | 4 | 2 | 0 | 0 |
| O2 | 6 | 4 | 2 | 0 | 0 |

## 20. D1 Map ranking

| Family | Unique max | True-best unique | Wrong unique | Tie | Invalid/missing |
|---|---|---|---|---|---|
| O1 | 6 | 6 | 0 | 0 | 0 |
| O2 | 6 | 6 | 0 | 0 | 0 |

## 21. Oracle Explorer W0

| Family | Calls | Valid | True-best /6 | Selected actions |
|---|---|---|---|---|
| O1 | 6 | 6 | 6 | {"ADVANCE": 6} |
| O2 | 6 | 6 | 4 | {"ADVANCE": 4, "HOLD": 1, "RETREAT": 1} |

## 22. Oracle Explorer W1

| Family | Calls | Valid | True-best /6 | Selected actions |
|---|---|---|---|---|
| O1 | 6 | 6 | 6 | {"HOLD": 6} |
| O2 | 6 | 6 | 6 | {"HOLD": 6} |

## 23. Oracle Explorer W3

| Family | Calls | Valid | True-best /6 | Selected actions |
|---|---|---|---|---|
| O1 | 6 | 6 | 6 | {"RETREAT": 6} |
| O2 | 6 | 6 | 5 | {"HOLD": 1, "RETREAT": 5} |

## 24. Oracle Explorer D1

| Family | Calls | Valid | True-best /6 | Selected actions |
|---|---|---|---|---|
| O1 | 6 | 6 | 3 | {"ADVANCE": 1, "HOLD": 2, "RETREAT": 3} |
| O2 | 6 | 6 | 2 | {"ADVANCE": 2, "HOLD": 2, "RETREAT": 2} |

## 25. Next-state permutation control

| Family | World | Issued | Valid | Same action | Changed action | Not comparable | True best |
|---|---|---|---|---|---|---|---|
| O1 | all | 24 | 24 | 22 | 2 | 0 | 23 |
| O1 | D1 | 6 | 6 | 4 | 2 | 0 | 5 |
| O1 | W0 | 6 | 6 | 6 | 0 | 0 | 6 |
| O1 | W1 | 6 | 6 | 6 | 0 | 0 | 6 |
| O1 | W3 | 6 | 6 | 6 | 0 | 0 | 6 |
| O2 | all | 24 | 24 | 18 | 6 | 0 | 19 |
| O2 | D1 | 6 | 6 | 4 | 2 | 0 | 4 |
| O2 | W0 | 6 | 6 | 5 | 1 | 0 | 5 |
| O2 | W1 | 6 | 6 | 5 | 1 | 0 | 5 |
| O2 | W3 | 6 | 6 | 4 | 2 | 0 | 5 |

Only next_state values rotate one row left; consequences, aliases, current state and row order remain fixed. Same action requires two valid parsed choices; invalid pairs are not comparable. Registered seed also differs. This tests bounded behavioral invariance, not proof that next_state is never used. Its separate gates are reported below and do not modify the frozen A+B+C pipeline decision.

## 26. Model-Map Explorer eligibility

Eligible contexts: 29/48. Issued conditional calls: 29/48. Eligibility requires all three finite valid forecasts and a unique predicted maximum. The following-stage support threshold separately requires>=18/24 per family. Insufficient eligibility is not reported as Explorer invalidity.

## 27. Explorer follows Map

| Family | Slice | Eligible / contexts | Issued / contexts | Valid / contexts | Valid / issued | Followed / valid |
|---|---|---|---|---|---|---|
| O1 | all | 15/24 | 15/24 | 15/24 | 15/15 | 13/15 |
| O1 | D1 | 6/6 | 6/6 | 6/6 | 6/6 | 4/6 |
| O1 | W0 | 3/6 | 3/6 | 3/6 | 3/3 | 3/3 |
| O1 | W1 | 0/6 | 0/6 | 0/6 | 0/0 (undefined) | 0/0 (undefined) |
| O1 | W3 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 |
| O1 | mapping 0 | 3/4 | 3/4 | 3/4 | 3/3 | 2/3 |
| O1 | mapping 1 | 2/4 | 2/4 | 2/4 | 2/2 | 2/2 |
| O1 | mapping 2 | 3/4 | 3/4 | 3/4 | 3/3 | 2/3 |
| O1 | mapping 3 | 2/4 | 2/4 | 2/4 | 2/2 | 2/2 |
| O1 | mapping 4 | 2/4 | 2/4 | 2/4 | 2/2 | 2/2 |
| O1 | mapping 5 | 3/4 | 3/4 | 3/4 | 3/3 | 3/3 |
| O2 | all | 14/24 | 14/24 | 14/24 | 14/14 | 9/14 |
| O2 | D1 | 6/6 | 6/6 | 6/6 | 6/6 | 2/6 |
| O2 | W0 | 2/6 | 2/6 | 2/6 | 2/2 | 2/2 |
| O2 | W1 | 0/6 | 0/6 | 0/6 | 0/0 (undefined) | 0/0 (undefined) |
| O2 | W3 | 6/6 | 6/6 | 6/6 | 6/6 | 5/6 |
| O2 | mapping 0 | 3/4 | 3/4 | 3/4 | 3/3 | 2/3 |
| O2 | mapping 1 | 2/4 | 2/4 | 2/4 | 2/2 | 1/2 |
| O2 | mapping 2 | 2/4 | 2/4 | 2/4 | 2/2 | 0/2 |
| O2 | mapping 3 | 3/4 | 3/4 | 3/4 | 3/3 | 2/3 |
| O2 | mapping 4 | 2/4 | 2/4 | 2/4 | 2/2 | 2/2 |
| O2 | mapping 5 | 2/4 | 2/4 | 2/4 | 2/2 | 2/2 |

Frozen validity is **valid>=17 AND 10*valid>=9*issued**. The stricter17/18 rate alternative was considered and not adopted. Following requires>=90% of valid issued choices to match the unique Map maximum, independent of reality. No world may have more than two valid-choice disagreements. Ratios add no thresholds; zero denominators are undefined. World denominator 6, mapping denominator 4, family denominator 24.

## 28. End-to-end current-best

| Family | World | Oracle true best | Composed true best | Context denominator | Oracle minus composed |
|---|---|---|---|---|---|
| O1 | all | 21 | 11 | 24 | 10 |
| O1 | D1 | 3 | 4 | 6 | -1 |
| O1 | W0 | 6 | 3 | 6 | 3 |
| O1 | W1 | 6 | 0 | 6 | 6 |
| O1 | W3 | 6 | 4 | 6 | 2 |
| O2 | all | 17 | 7 | 24 | 10 |
| O2 | D1 | 2 | 2 | 6 | 0 |
| O2 | W0 | 4 | 2 | 6 | 2 |
| O2 | W1 | 6 | 0 | 6 | 6 |
| O2 | W3 | 5 | 3 | 6 | 2 |

Family denominator remains 24. Ties, invalid Map, absent/invalid Explorer and wrong choices count unsuccessful. Oracle minus composed correct count is descriptive, not causal attribution: forecasts and registered Explorer seeds differ. End-to-end alone cannot rescue any stage gate.

## 29. Pipeline failure decomposition

| Family | Failure classification | Count |
|---|---|---|
| O1 | MAP_CORRECT_EXPLORER_CORRECT | 11 |
| O1 | MAP_CORRECT_EXPLORER_WRONG | 2 |
| O1 | MAP_TIE_NO_EXPLORER | 9 |
| O1 | MAP_WRONG_EXPLORER_FOLLOWS_MAP | 2 |
| O2 | MAP_CORRECT_EXPLORER_CORRECT | 7 |
| O2 | MAP_CORRECT_EXPLORER_WRONG | 5 |
| O2 | MAP_TIE_NO_EXPLORER | 10 |
| O2 | MAP_WRONG_EXPLORER_FOLLOWS_MAP | 2 |

A wrong Map followed correctly remains a Map-ranking failure. A correct Map followed incorrectly is a comparison failure. Valid disagreement with a wrong Map may accidentally recover the true-best action; its forecast-compliance score remains separate. Invalid Explorer and unissued tie/invalid-Map slots have separate categories.

## 30. O1 decisions

**A_ORACLE_COMPARISON: NOT ESTABLISHED**

| Frozen gate | Passed |
|---|---|
| D1_best_at_least_5 | False |
| W0_best_at_least_5 | True |
| W1_best_at_least_5 | True |
| W3_best_at_least_5 | True |
| all_24_complete | True |
| exact_replay | True |
| integrity | True |
| total_best_at_least_20 | True |
| valid_at_least_23 | True |

**B_MAP_RANKING: NOT ESTABLISHED**

| Frozen gate | Passed |
|---|---|
| D1_best_unique_at_least_4 | True |
| W0_best_unique_at_least_4 | False |
| W1_best_unique_at_least_4 | False |
| W3_best_unique_at_least_4 | True |
| all_72_Map_complete | True |
| exact_replay | True |
| no_oracle_leakage | True |
| true_best_unique_at_least_18 | False |
| unique_max_at_least_20 | False |
| valid_at_least_69 | True |

**C_EXPLORER_FOLLOWS_MAP: NOT ESTABLISHED** — INSUFFICIENT_ELIGIBLE_CONTEXTS

| Frozen gate | Passed |
|---|---|
| all_eligible_calls_complete | True |
| eligible_at_least_18 | False |
| exact_replay | True |
| follows_at_least_90pct_valid | False |
| no_world_over_two_disagreements | True |
| valid_at_least_17 | False |
| validity_at_least_90pct | True |

**NEXT_STATE_CONTROL: SUPPORTED**

| Frozen gate | Passed |
|---|---|
| all_24_complete | True |
| best_at_least_20 | True |
| no_world_below_5 | True |
| same_at_least_22 | True |
| valid_at_least_23 | True |

## 31. O2 decisions

**A_ORACLE_COMPARISON: NOT ESTABLISHED**

| Frozen gate | Passed |
|---|---|
| D1_best_at_least_5 | False |
| W0_best_at_least_5 | False |
| W1_best_at_least_5 | True |
| W3_best_at_least_5 | True |
| all_24_complete | True |
| exact_replay | True |
| integrity | True |
| total_best_at_least_20 | False |
| valid_at_least_23 | True |

**B_MAP_RANKING: NOT ESTABLISHED**

| Frozen gate | Passed |
|---|---|
| D1_best_unique_at_least_4 | True |
| W0_best_unique_at_least_4 | False |
| W1_best_unique_at_least_4 | False |
| W3_best_unique_at_least_4 | True |
| all_72_Map_complete | True |
| exact_replay | True |
| no_oracle_leakage | True |
| true_best_unique_at_least_18 | False |
| unique_max_at_least_20 | False |
| valid_at_least_69 | True |

**C_EXPLORER_FOLLOWS_MAP: NOT ESTABLISHED** — INSUFFICIENT_ELIGIBLE_CONTEXTS

| Frozen gate | Passed |
|---|---|
| all_eligible_calls_complete | True |
| eligible_at_least_18 | False |
| exact_replay | True |
| follows_at_least_90pct_valid | False |
| no_world_over_two_disagreements | False |
| valid_at_least_17 | False |
| validity_at_least_90pct | True |

**NEXT_STATE_CONTROL: NOT ESTABLISHED**

| Frozen gate | Passed |
|---|---|
| all_24_complete | True |
| best_at_least_20 | False |
| no_world_below_5 | False |
| same_at_least_22 | False |
| valid_at_least_23 | True |

## 32. Representation correlation analysis

| World | Mapping | O1 rank | O2 rank | Oracle correct O1/O2 | Follows Map O1/O2 | End-to-end O1/O2 |
|---|---|---|---|---|---|---|
| W0 | 0 | TRUE_BEST_UNIQUE_MAX | TRUE_BEST_UNIQUE_MAX | True/True | True/True | True/True |
| W0 | 1 | TIED_MAXIMUM | TIED_MAXIMUM | True/True | False/False | False/False |
| W0 | 2 | TRUE_BEST_UNIQUE_MAX | TIED_MAXIMUM | True/True | True/False | True/False |
| W0 | 3 | TIED_MAXIMUM | TRUE_BEST_UNIQUE_MAX | True/False | False/True | False/True |
| W0 | 4 | TIED_MAXIMUM | TIED_MAXIMUM | True/True | False/False | False/False |
| W0 | 5 | TRUE_BEST_UNIQUE_MAX | TIED_MAXIMUM | True/False | True/False | True/False |
| W1 | 0 | TIED_MAXIMUM | TIED_MAXIMUM | True/True | False/False | False/False |
| W1 | 1 | TIED_MAXIMUM | TIED_MAXIMUM | True/True | False/False | False/False |
| W1 | 2 | TIED_MAXIMUM | TIED_MAXIMUM | True/True | False/False | False/False |
| W1 | 3 | TIED_MAXIMUM | TIED_MAXIMUM | True/True | False/False | False/False |
| W1 | 4 | TIED_MAXIMUM | TIED_MAXIMUM | True/True | False/False | False/False |
| W1 | 5 | TIED_MAXIMUM | TIED_MAXIMUM | True/True | False/False | False/False |
| W3 | 0 | TRUE_BEST_UNIQUE_MAX | TRUE_BEST_UNIQUE_MAX | True/True | True/True | True/True |
| W3 | 1 | WRONG_ACTION_UNIQUE_MAX | TRUE_BEST_UNIQUE_MAX | True/True | True/True | False/True |
| W3 | 2 | TRUE_BEST_UNIQUE_MAX | TRUE_BEST_UNIQUE_MAX | True/False | True/False | True/False |
| W3 | 3 | TRUE_BEST_UNIQUE_MAX | WRONG_ACTION_UNIQUE_MAX | True/True | True/True | True/False |
| W3 | 4 | WRONG_ACTION_UNIQUE_MAX | WRONG_ACTION_UNIQUE_MAX | True/True | True/True | False/False |
| W3 | 5 | TRUE_BEST_UNIQUE_MAX | TRUE_BEST_UNIQUE_MAX | True/True | True/True | True/True |
| D1 | 0 | TRUE_BEST_UNIQUE_MAX | TRUE_BEST_UNIQUE_MAX | False/False | False/False | False/False |
| D1 | 1 | TRUE_BEST_UNIQUE_MAX | TRUE_BEST_UNIQUE_MAX | True/False | True/False | True/False |
| D1 | 2 | TRUE_BEST_UNIQUE_MAX | TRUE_BEST_UNIQUE_MAX | False/False | False/False | False/False |
| D1 | 3 | TRUE_BEST_UNIQUE_MAX | TRUE_BEST_UNIQUE_MAX | False/False | True/False | True/False |
| D1 | 4 | TRUE_BEST_UNIQUE_MAX | TRUE_BEST_UNIQUE_MAX | True/True | True/True | True/True |
| D1 | 5 | TRUE_BEST_UNIQUE_MAX | TRUE_BEST_UNIQUE_MAX | True/True | True/True | True/True |

| Family | Group | Contexts | Correct Map rank | Oracle correct | ModelMap follows/valid | End-to-end |
|---|---|---|---|---|---|---|
| O1 | all | 24 | 13 | 21 | 13/15 | 11 |
| O1 | world D1 | 6 | 6 | 3 | 4/6 | 4 |
| O1 | world W0 | 6 | 3 | 6 | 3/3 | 3 |
| O1 | world W1 | 6 | 0 | 6 | 0/0 | 0 |
| O1 | world W3 | 6 | 4 | 6 | 6/6 | 4 |
| O1 | mapping 0 | 4 | 3 | 3 | 2/3 | 2 |
| O1 | mapping 1 | 4 | 1 | 4 | 2/2 | 1 |
| O1 | mapping 2 | 4 | 3 | 3 | 2/3 | 2 |
| O1 | mapping 3 | 4 | 2 | 3 | 2/2 | 2 |
| O1 | mapping 4 | 4 | 1 | 4 | 2/2 | 1 |
| O1 | mapping 5 | 4 | 3 | 4 | 3/3 | 3 |
| O1 | true-best alias K1 | 8 | 4 | 8 | 5/5 | 4 |
| O1 | true-best alias K2 | 8 | 4 | 7 | 5/5 | 4 |
| O1 | true-best alias K3 | 8 | 5 | 6 | 3/5 | 3 |
| O2 | all | 24 | 12 | 17 | 9/14 | 7 |
| O2 | world D1 | 6 | 6 | 2 | 2/6 | 2 |
| O2 | world W0 | 6 | 2 | 4 | 2/2 | 2 |
| O2 | world W1 | 6 | 0 | 6 | 0/0 | 0 |
| O2 | world W3 | 6 | 4 | 5 | 5/6 | 3 |
| O2 | mapping 0 | 4 | 3 | 3 | 2/3 | 2 |
| O2 | mapping 1 | 4 | 2 | 3 | 1/2 | 1 |
| O2 | mapping 2 | 4 | 2 | 2 | 0/2 | 0 |
| O2 | mapping 3 | 4 | 2 | 2 | 2/3 | 1 |
| O2 | mapping 4 | 4 | 1 | 4 | 2/2 | 1 |
| O2 | mapping 5 | 4 | 2 | 3 | 2/2 | 2 |
| O2 | true-best alias M4 | 8 | 3 | 6 | 2/4 | 1 |
| O2 | true-best alias Q7 | 8 | 4 | 8 | 5/5 | 4 |
| O2 | true-best alias Z2 | 8 | 5 | 3 | 2/5 | 2 |

| Family | Error category | Selected alias counts |
|---|---|---|
| O1 | Map_wrong_max_alias | {"K3": 2} |
| O1 | Oracle_wrong_choice_alias | {"K1": 3} |
| O1 | ModelMap_disagreement_alias | {"K1": 2} |
| O1 | end_to_end_wrong_valid_alias | {"K1": 2, "K3": 2} |
| O2 | Map_wrong_max_alias | {"Q7": 1, "Z2": 1} |
| O2 | Oracle_wrong_choice_alias | {"Q7": 7} |
| O2 | ModelMap_disagreement_alias | {"Q7": 5} |
| O2 | end_to_end_wrong_valid_alias | {"Q7": 6, "Z2": 1} |

The matched table preserves joint outcomes; the grouped table exposes concentrations by family, world, mapping and true-best alias with denominators. Followed=False in an unissued/invalid context is not a valid disagreement; eligibility and validity remain in compact rows. Shared model weights mean stage errors need not be independent. Ties were concentrated in W0 (7/12) and W1 (12/12), with none in W3 or D1. All four wrong unique maxima occurred in W3 (two per family). Oracle errors were concentrated in D1 (7 of 10 errors); valid composed Explorer disagreements were also concentrated there (six ofseven). The matched mapping and selected-alias tables retain the individual representation patterns. These are descriptive counts, not causal token-bias or statistically established clustering claims.

## 33. D1 focused analysis

| Family | Mapping | Map ADVANCE | Map HOLD | Map RETREAT | Ranking | Oracle choice | ModelMap choice | End-to-end |
|---|---|---|---|---|---|---|---|---|
| O2 | 0 | {"consequence": -1, "next_state": 2} | {"consequence": -1, "next_state": 1} | {"consequence": 0, "next_state": 0} | TRUE_BEST_UNIQUE_MAX | ADVANCE | ADVANCE | False |
| O1 | 0 | {"consequence": -1, "next_state": 2} | {"consequence": -1, "next_state": 1} | {"consequence": 0, "next_state": 0} | TRUE_BEST_UNIQUE_MAX | ADVANCE | ADVANCE | False |
| O1 | 1 | {"consequence": -1, "next_state": 2} | {"consequence": -1, "next_state": 1} | {"consequence": 0, "next_state": 0} | TRUE_BEST_UNIQUE_MAX | RETREAT | RETREAT | True |
| O2 | 1 | {"consequence": -1, "next_state": 2} | {"consequence": -1, "next_state": 1} | {"consequence": 0, "next_state": 0} | TRUE_BEST_UNIQUE_MAX | ADVANCE | ADVANCE | False |
| O2 | 2 | {"consequence": -1, "next_state": 2} | {"consequence": -1, "next_state": 1} | {"consequence": 0, "next_state": 0} | TRUE_BEST_UNIQUE_MAX | HOLD | HOLD | False |
| O1 | 2 | {"consequence": -1, "next_state": 2} | {"consequence": -1, "next_state": 1} | {"consequence": 0, "next_state": 0} | TRUE_BEST_UNIQUE_MAX | HOLD | HOLD | False |
| O1 | 3 | {"consequence": -1, "next_state": 2} | {"consequence": -1, "next_state": 1} | {"consequence": 0, "next_state": 0} | TRUE_BEST_UNIQUE_MAX | HOLD | RETREAT | True |
| O2 | 3 | {"consequence": -1, "next_state": 2} | {"consequence": -1, "next_state": 1} | {"consequence": 0, "next_state": 0} | TRUE_BEST_UNIQUE_MAX | HOLD | HOLD | False |
| O2 | 4 | {"consequence": -1, "next_state": 2} | {"consequence": -1, "next_state": 1} | {"consequence": 0, "next_state": 0} | TRUE_BEST_UNIQUE_MAX | RETREAT | RETREAT | True |
| O1 | 4 | {"consequence": -1, "next_state": 3} | {"consequence": -1, "next_state": 1} | {"consequence": 1, "next_state": 0} | TRUE_BEST_UNIQUE_MAX | RETREAT | RETREAT | True |
| O1 | 5 | {"consequence": -1, "next_state": 2} | {"consequence": -1, "next_state": 1} | {"consequence": 0, "next_state": 0} | TRUE_BEST_UNIQUE_MAX | RETREAT | RETREAT | True |
| O2 | 5 | {"consequence": -1, "next_state": 0} | {"consequence": -1, "next_state": 1} | {"consequence": 0, "next_state": 0} | TRUE_BEST_UNIQUE_MAX | RETREAT | RETREAT | True |

Current true best is RETREAT; old HOLD success remains in the authentic history alongside two newer -1 outcomes. D1 is reported separately for all three forecasts, ranking, Oracle choice, ModelMap choice and end-to-end correctness; no pooling hides this case.

## 34. Tie accounting

**Overall model-forecast tie count: 19/48**.

| Family | World | Ties / contexts |
|---|---|---|
| O1 | all | 9/24 |
| O1 | D1 | 0/6 |
| O1 | W0 | 3/6 |
| O1 | W1 | 6/6 |
| O1 | W3 | 0/6 |
| O2 | all | 10/24 |
| O2 | D1 | 0/6 |
| O2 | W0 | 4/6 |
| O2 | W1 | 6/6 |
| O2 | W3 | 0/6 |

Mapping-level tie counts and denominators appear in each family’s by_mapping compact results. A tie is a practical pipeline limitation in the finite consequence domain, not a formatting error or missing request.

## 35. Provenance / Memory preservation

Original authenticated setup histories, receipts, packages, pairs and current state are unchanged across measured calls. Oracle values and model forecasts remain detached proposals; no receipt or authorization capability is supplied to either model role. Measured choice executions, receipts and Memory publications are all zero. All current actions remain legal; no historical negative becomes an action ban. Interface-v0 and all authority implementations remain byte-identical.

## 36. Exact replay

All 269 issued raw responses were replayed with sockets forbidden and zero inference. The same conditional slots remained unissued. All fixtures, requests, parser results, oracle evaluations, permutations, interface bindings, classifications, ratios and gates reconstructed exactly: seven deterministic files and 48 snapshots matched byte-for-byte; finalized results matched separately. Original live metrics retain their provisional replay status without overwriting raw evidence.

## 37. Historical preservation

95 tests passed (7 new study, 6 durability, 82 historical), plus 12 historical zero-inference replays. 619 inherited substantive files remain byte-identical; all earlier archive inventories and prior refs/main/tags are unchanged. Temporal negative, interface A, both Explorer negatives, Map revision REPLICATED, feasibility A, depth SUPPORTED, transfer history, initialization A, ablation SUPPORTED, R1 A and grounding/contradiction/UNKNOWN/representation checkpoints are preserved. See [verification.json](../experiments/map_explorer_oracle_decomposition_v0/verification.json).

## 38. Limitations

Four small deterministic current-relation fixtures, one pinned model/sampler and six alias mappings per family. No measured choice executes; this does not establish closed-loop success. All actions have history, so empty-history uncertainty and confidence are untested. Oracle and model arms have different seeds, as does the next-state control, limiting causal attribution. Shared model weights may induce correlated errors. Trusted in-process external worlds, receipt sources and driver are not cryptographic attestation or hostile-code isolation. No general temporal/world modeling, policy or persistent learning, independent-error assumption, RL, AGI or RSI claim.

## 39. Narrowest defensible conclusion

**PIPELINE NOT FULLY ESTABLISHED**.

| Stage | Replicated across both families |
|---|---|
| A_ORACLE_COMPARISON | False |
| B_MAP_RANKING | False |
| C_EXPLORER_FOLLOWS_MAP | False |

Failed stage(s): A_ORACLE_COMPARISON, B_MAP_RANKING, C_EXPLORER_FOLLOWS_MAP. A stage is replicated only when its full frozen rule passes independently in O1 and O2. The stage-specific positive and negative findings remain separate; success at another stage does not repair a failed gate. In this run, all 144 Map forecasts and all 125 issued Explorer responses were valid. Map tied in 19/48 contexts and ranked the true best uniquely in 25/48. Oracle Explorer scored 21/24 (O1) and 17/24 (O2), with D1 only 3/6 and 2/6. Conditional eligibility was 15/24 and 14/24, so following-Map is NOT ESTABLISHED due to insufficient eligible contexts, not invalidity; observed compliance 13/15 and 9/14 also fell below 90%. Composed true-best was 11/24 and 7/24, an observed decrease of 10 correct choices per family from the Oracle arm. Different registered seeds prevent attributing that difference solely to forecast replacement. The next-state control passed in O1 and failed in O2. The previous temporal-negative result remains binding.

## 40. Recommendation

Use the preserved stage/failure tables, D1 cells, tie rates and clarified denominators to choose the next separately authorized research question. Stop here: no measured action execution, closed loop, confidence fields, prompt tuning, tie-policy change, added calls, main/tag changes or push.
