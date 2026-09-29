# Grounded reducer versus model v0 — completed report

Registered classification: **SPEED_ROBUSTNESS_TRADEOFF**. Campaign status: COMPLETE. The result is descriptive for the four frozen sequences.

1. **Branch:** `research/grounded-reducer-vs-model-v0`.
2. **Commit:** preregistration `a032a6dd548013fba30c2366da465ed17ec9b98b`; the final evidence commit is the branch tip containing this report. Completed parent v0.1 remains exactly `0341322b1f9494f16d76f9a746668ffb9bd4ef23` and `HORUS_NET_HARMFUL`.
3. **Protected framework:** zero-inference preflight passed original receipt identity, failed-execution exclusion, unauthorized-memory rejection, authenticated restart, source/model hashes and bounded transport. Each of 56 committed triple snapshots has matching scheduled authenticated observations and exact memory replay. A clean archive was replayed separately after packaging.
4. **M:** the frozen modern Memory retrieval (exact relation, recent four, contradiction anchors, deterministic fill to six, chronological order), common joint next-state Map, and frozen G2 model consequence prediction. Only the prospective HOLD action is predicted; all 26 M HOLD request bodies, including the two perturbation calls, match the parent baseline requests exactly; see [request equivalence](baseline-request-equivalence.json).
5. **L:** most recent authorized authenticated receipt for the exact `(pre_state,HOLD)` relation; use its consequence and next state. No model call. At zero exact history, predict neutral consequence `0` and identity next state.
6. **R3:** at most three latest authorized exact-relation consequences; choose their majority. A tie goes to the latest observation among tied values. Next state comes from the most recent exact receipt. It shares L’s zero-history fallback and makes no model call.
7. **Frozen schedules:** A = A×4/B×4/A×4 (12, clean change and restoration); B = A×4/B×1/A×4 (9, isolated anomaly); C = A×4/B×1/A×3/B×4 (12, noise then genuine change); D = A×4/B×6/A×4 (14, longer change before restoration). All events are HOLD and identities were frozen before inference. Each schedule begins with three fresh protected arms.
8. **Call budget:** 47 ordinary matched observations plus one non-executing perturbation; 96 logical and 192 maximum physical M attempts. Actual M calls: 96 logical and 96 physical. L/R3: zero. The perturbation uses two M calls.
9. **Total and per-schedule results:** see the consequence/exact table below. First-event cold starts are reported separately from head-to-head classification.
10. **Change adaptation:** first-correct latency, measured in subsequent events after the first changed-regime event, appears in the transition table. Null means no correct prediction in the registered window.
11. **Restoration:** same latency metric in A and D appears below. First restoration events have no new restored-regime receipt yet; correctness there alone does not prove relearning.
12. **Isolated noise:** B and C anomaly-event errors and immediate recovery-event errors appear below. The one-event B override is an authentic protected receipt in all arms.
13. **False switches/persistence:** post-anomaly false switches and old-regime predictions during sustained transitions appear below. They are reported separately from ordinary errors.
14. **Restart:** PASS after A6 in a fresh process; exact signed session-file and durable-memory hashes, matched identities and receipt-source separation checked before A7.
15. **Perturbation:** PASS; the registered malformed parser input created no receipt or memory in any arm. L and R3 therefore retained the same grounded predictions. Transport failures are distinct.
16. **Error causes:** counts are below; M flags are non-exclusive and each L/R3 error has one primary cause. Full per-event evidence is in [the error audit](error-audit.json). `CORRECT_CURRENT_SIGNAL_PRESENT` is assigned only after the actual receipt, using the frozen schedule for audit and never as a model input.
17. **Operational cost:** logical calls, physical attempts, context tokens, model time and prediction latency are below. L/R3 use no model for consequence or next-state prediction. Campaign wall time includes three-arm protected publication and process starts.
18. **Classification:** **SPEED_ROBUSTNESS_TRADEOFF**, under the preregistered rule. The first cold-start event of each schedule is excluded from head-to-head classification but fully scored and reported.
19. **Simplest architecture indicated:** see the final interpretation paragraph after the tables. No new agent, router, training or representation was built.
20. **Limitations:** Four small deterministic simulated sequences and one frozen model family; no population inference. The isolated anomaly uses a one-event hidden regime override; other noise types are untested. All actions are observation-controlled HOLD, so autonomy and unseen relations are outside this comparison. Cold-start fallback is a neutral consequence and identity next-state assumption, scored separately. Single machine service latency can vary; model inference time is observational. Atomicity is committed visibility of simulated worlds, not simultaneous physical actuation.

## Accuracy by schedule

| Schedule | Arm | Consequence | Exact | Post-cold-start consequence | Stable | Change/persistence | Restoration | Noise | Recovery | Worst rolling 4 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A | M | 8/12 | 8/12 | 7/11 | 4/4 | 0/4 | 4/4 | — | — | 0/4 |
| A | L | 9/12 | 9/12 | 9/11 | 3/4 | 3/4 | 3/4 | — | — | 3/4 |
| A | R3 | 7/12 | 7/12 | 7/11 | 3/4 | 2/4 | 2/4 | — | — | 2/4 |
| B | M | 8/9 | 8/9 | 7/8 | 4/4 | — | — | 0/1 | 4/4 | 3/4 |
| B | L | 6/9 | 6/9 | 6/8 | 3/4 | — | — | 0/1 | 3/4 | 2/4 |
| B | R3 | 7/9 | 7/9 | 7/8 | 3/4 | — | — | 0/1 | 4/4 | 3/4 |
| C | M | 7/12 | 7/12 | 6/11 | 4/4 | 0/4 | — | 0/1 | 3/3 | 0/4 |
| C | L | 8/12 | 8/12 | 8/11 | 3/4 | 3/4 | — | 0/1 | 2/3 | 2/4 |
| C | R3 | 8/12 | 8/12 | 8/11 | 3/4 | 2/4 | — | 0/1 | 3/3 | 2/4 |
| D | M | 8/14 | 8/14 | 7/13 | 4/4 | 0/6 | 4/4 | — | — | 0/4 |
| D | L | 11/14 | 11/14 | 11/13 | 3/4 | 5/6 | 3/4 | — | — | 3/4 |
| D | R3 | 9/14 | 9/14 | 9/13 | 3/4 | 4/6 | 2/4 | — | — | 2/4 |

Overall consequence accuracy: M 31/47, L 34/47, R3 31/47.
Cold-start correctness: M 4/4, L 0/4, R3 0/4.

## Transition and anomaly behavior

| Schedule | Arm | Change latency | Restoration latency | False persistence | Anomaly error | Immediate recovery error | False switch |
|---|---|---:|---:|---:|---:|---:|---:|
| A | M | N/A | 0 | 4 | — | — | — |
| A | L | 1 | 1 | 2 | — | — | — |
| A | R3 | 2 | 2 | 4 | — | — | — |
| B | M | — | — | 0 | True | False | False |
| B | L | — | — | 0 | True | True | True |
| B | R3 | — | — | 0 | True | False | False |
| C | M | N/A | — | 4 | True | False | False |
| C | L | 1 | — | 1 | True | True | True |
| C | R3 | 2 | — | 2 | True | False | False |
| D | M | N/A | 0 | 6 | — | — | — |
| D | L | 1 | 1 | 2 | — | — | — |
| D | R3 | 2 | 2 | 4 | — | — | — |

Early/middle/late consequence accuracy (each schedule split at floor(n/3) and floor(2n/3)):

| Schedule | Arm | Early | Middle | Late |
|---|---|---:|---:|---:|
| A | M | 4/4 | 0/4 | 4/4 |
| A | L | 3/4 | 3/4 | 3/4 |
| A | R3 | 3/4 | 2/4 | 2/4 |
| B | M | 3/3 | 2/3 | 3/3 |
| B | L | 2/3 | 1/3 | 3/3 |
| B | R3 | 2/3 | 2/3 | 3/3 |
| C | M | 4/4 | 3/4 | 0/4 |
| C | L | 3/4 | 2/4 | 3/4 |
| C | R3 | 3/4 | 3/4 | 2/4 |
| D | M | 4/4 | 0/5 | 4/5 |
| D | L | 3/4 | 4/5 | 4/5 |
| D | R3 | 3/4 | 3/5 | 3/5 |

## Error causes

| Arm | Error count | Labels and counts |
|---|---:|---|
| M | 16 | STALE_SIGNAL_DOMINATED: 10, AMBIGUOUS_HISTORY: 12, CORRECT_CURRENT_SIGNAL_PRESENT: 11, MODEL_WRONG_DESPITE_CLEAR_GROUNDED_SIGNAL: 5 |
| L | 13 | INSUFFICIENT_HISTORY: 11, LATEST_OUTCOME_WAS_NOISE: 2 |
| R3 | 16 | INSUFFICIENT_HISTORY: 11, WINDOW_TOO_SLOW: 5 |

## Operational cost

| Metric | M | L | R3 |
|---|---:|---:|---:|
| logical_model_calls | 96 | 0 | 0 |
| physical_transport_attempts | 96 | 0 | 0 |
| transport_failures | 0 | 0 | 0 |
| repaired_calls | 0 | 0 | 0 |
| unrepaired_failures | 0 | 0 | 0 |
| model_invalid_outputs | 0 | 0 | 0 |
| intentional_parser_rejections | 1 | 0 | 0 |
| context_tokens | 13440 | 0 | 0 |
| model_seconds | 1235.536 | 0.000 | 0.000 |
| prediction_seconds | 1238.749 | 0.014 | 0.014 |
| mean_prediction_seconds | 26.356 | 0.000 | 0.000 |
| model_call_completion_rate | 1.000 | N/A (zero calls) | N/A (zero calls) |

Ordinary-event mean M prediction latency: 25.913 seconds over 47 forecasts. The machine-readable `mean_prediction_seconds` amortizes the registered perturbation over those 47 events; L and R3 have no perturbation calls.

Combined worker wall time: 1250.456 seconds. Exact replay: PASS with 96 logical model calls and 96 physical attempts.

The transition comparison is A change: L 1, R3 2; A restoration: L 1, R3 2; C change: L 1, R3 2; D change: L 1, R3 2; D restoration: L 1, R3 2. The anomaly comparison is B immediate recovery: L wrong, R3 correct; C immediate recovery: L wrong, R3 correct.
The evidence supports a protected durable exact-relation model built from authenticated receipts for repeated observations. L captures the latest consequence quickly; R3 is a small window that can resist one-off anomalous receipts. The frozen model remains a candidate for unseen relations and other cases lacking enough grounded evidence. This study did not implement a selector between these rules or test autonomous decisions.

[Full machine-readable results](evidence/results.json) · [Authenticated replay](evidence/replay.json) · [Preregistration](preregistration.md) · [Frozen source manifest](source-manifest.json)
