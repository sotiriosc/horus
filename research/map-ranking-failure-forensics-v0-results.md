# Map ranking failure forensics v0

**Diagnosis: NOT DETERMINABLE FROM RETAINED EVIDENCE** for the dominant internal explanation among recency, representation bias and finite-domain compression. The observable bottleneck is nevertheless exact: **all 23 residual failures underpredict the true-best positive consequence, contrary to its latest authenticated history.** No failure requires overprediction of a competing action.

Zero model calls, zero world executions, zero prompt or architecture changes. Mechanical exploitation is preserved as the reference path and was not rerun or modified. This is descriptive forensics, with no model-performance pass/fail threshold.

## Identity, retained inputs and claim boundary

Parent/mechanical: `004ec5a6952d6b1c2c793eabe7200215611ea7b0`. Grounded root: `79921b1da735e1495dffb695c00d7e7a21a234a6`. Decomposition evidence: `2679cff20b28079b4358fe463f68e5822e5cc205`. Branch: `research/map-ranking-failure-forensics-v0`.

The unchanged [grounded manifest](../experiments/grounded_lineage_rebaseline_v0/clean-root-manifest.json) and [claim firewall](../experiments/grounded_lineage_rebaseline_v0/claim_eligibility.json) classify this decomposition as **D — MIXED / AMBIGUOUS**, explicitly combining receipt-derived past with detached evaluator truth. Permitted scope is authenticated-past-to-detached-world forecast scoring / finite prompt behavior. “Actual” below always means the **retained current detached-world evaluator outcome**, never a newly executed or receipt-grounded future outcome. Those truth labels were not Map-visible.

The source archive’s 900 sealed files were verified. All 144 Map requests and parsed responses were matched to original records, the parent finite evidence, and the 48 contexts. All 180 model-visible chronological observation rows matched the exact `(pre_state, action)` subset of retained Memory in order; epoch/transaction identities, receipt fields, executed-event fields and pair fields were cross-checked. D1 cross-epoch observations are preserved, including both old +1 and later −1 HOLD outcomes. No observations were overwritten or turned into action bans. Retained original-receipt-object flags were checked; JSON cannot reconstruct historical object identity.

Artifacts: [complete finite reconstruction](../experiments/map_ranking_failure_forensics_v0/retained-evidence.json), [results and all breakdowns](../experiments/map_ranking_failure_forensics_v0/results.json), [source hashes](../experiments/map_ranking_failure_forensics_v0/source-manifest.json), [verification](../experiments/map_ranking_failure_forensics_v0/verification.json), and [reproduction instructions](../experiments/map_ranking_failure_forensics_v0/README.md). Public exports contain the requested finite histories and predictions, not raw prompts, private predecessor material, or full protected archives.

## W1: every tie has the same mechanism at the output level

Triple order throughout is **(ADVANCE, HOLD, RETREAT)**. Every W1 actual/latest triple is **(−1, +1, 0)**. All twelve predicted triples are **(−1, 0, 0)**: HOLD is underpredicted and ties with correctly predicted RETREAT. ADVANCE’s consequence is correct. All three histories have depth one. There are no `(0,0,0)`, `(+1,+1,0)` or `(−1,+1,+1)` W1 cases.

| Context | Family | Mapping | Aliases A / H / R | Predicted triple | Latest relations A / H / R |
| --- | --- | --- | --- | --- | --- |
| 12 | O2 | 0 | Q7 / M4 / Z2 | (-1, 0, 0) | COPY / NON-LATEST / COPY |
| 13 | O1 | 0 | K1 / K2 / K3 | (-1, 0, 0) | COPY / NON-LATEST / COPY |
| 14 | O1 | 1 | K1 / K3 / K2 | (-1, 0, 0) | COPY / NON-LATEST / COPY |
| 15 | O2 | 1 | Q7 / Z2 / M4 | (-1, 0, 0) | COPY / NON-LATEST / COPY |
| 16 | O2 | 2 | M4 / Q7 / Z2 | (-1, 0, 0) | COPY / NON-LATEST / COPY |
| 17 | O1 | 2 | K2 / K1 / K3 | (-1, 0, 0) | COPY / NON-LATEST / COPY |
| 18 | O1 | 3 | K3 / K1 / K2 | (-1, 0, 0) | COPY / NON-LATEST / COPY |
| 19 | O2 | 3 | Z2 / Q7 / M4 | (-1, 0, 0) | COPY / NON-LATEST / COPY |
| 20 | O2 | 4 | M4 / Z2 / Q7 | (-1, 0, 0) | COPY / NON-LATEST / COPY |
| 21 | O1 | 4 | K2 / K3 / K1 | (-1, 0, 0) | COPY / NON-LATEST / COPY |
| 22 | O1 | 5 | K3 / K2 / K1 | (-1, 0, 0) | COPY / NON-LATEST / COPY |
| 23 | O2 | 5 | Z2 / M4 / Q7 | (-1, 0, 0) | COPY / NON-LATEST / COPY |

This persists through both families, all six mappings and every HOLD alias. The same underlying exact-pair consequence histories are present each time. This recurrence does not isolate an alias-specific explanation: the error survives every alias assignment. Exact outcome accuracy is 21/36, below consequence accuracy 24/36 because three additional next_state errors occur (contexts 12 and 16 RETREAT; context 18 ADVANCE). These state errors do not create the ties.

## W0: seven ties, without promoting a competitor

Actual/latest triple is (+1, 0, −1). All seven ties predict **(0, 0, −1)**: ADVANCE is reduced from +1 to 0 and ties with correctly predicted HOLD. RETREAT is correctly −1. No other action is incorrectly promoted. The remaining five contexts predict the actual triple exactly.

| Context | Family | Mapping | ADVANCE / HOLD / RETREAT aliases | Tied actions | Latest relations |
| --- | --- | --- | --- | --- | --- |
| 2 | O2 | 1 | Q7 / Z2 / M4 | ADVANCE = HOLD | NON-LATEST / COPY / COPY |
| 3 | O1 | 1 | K1 / K3 / K2 | ADVANCE = HOLD | NON-LATEST / COPY / COPY |
| 5 | O2 | 2 | M4 / Q7 / Z2 | ADVANCE = HOLD | NON-LATEST / COPY / COPY |
| 7 | O1 | 3 | K3 / K1 / K2 | ADVANCE = HOLD | NON-LATEST / COPY / COPY |
| 8 | O1 | 4 | K2 / K3 / K1 | ADVANCE = HOLD | NON-LATEST / COPY / COPY |
| 9 | O2 | 4 | M4 / Z2 / Q7 | ADVANCE = HOLD | NON-LATEST / COPY / COPY |
| 10 | O2 | 5 | Z2 / M4 / Q7 | ADVANCE = HOLD | NON-LATEST / COPY / COPY |

W0 ties are O1 3/6 and O2 4/6. In O1, every ADVANCE alias appears once with +1 and once with 0: K1 in mappings 0/1, K2 in 2/4, K3 in 5/3. Thus an alias alone does not fix the error. Mapping/seed and other request differences remain entangled; recurring representation associations are descriptive, not causal.

## W3: inspect all four wrong unique maxima

Actual/latest triple is (−1, 0, +1). Each wrong case predicts **(−1, 0, −1)**. Correctly forecast HOLD becomes the wrong unique maximum because RETREAT is underpredicted by two consequence levels. HOLD is **not** overpredicted and **does** copy its latest observation; ADVANCE is correctly −1 and does not supply an additional forecast error. RETREAT does **not** copy latest. Full chronological histories, predictions and actual pairs are shown individually below; `(next_state, consequence)` is the pair notation.

**Context 27 — O1, mapping 1, state 3.**

| Action | Alias | Chronological history: epoch/transaction:(next_state, consequence) | Map prediction | Actual | Latest relation |
| --- | --- | --- | --- | --- | --- |
| ADVANCE | K1 | 1001/4:(0, -1) | (0, -1) | (0, -1) | LATEST_COPY |
| HOLD | K3 | 1001/1:(3, 0) | (3, 0) | (3, 0) | LATEST_COPY |
| RETREAT | K2 | 1001/2:(2, +1) | (1, -1) | (2, +1) | NON_LATEST |

Predicted: **HOLD > ADVANCE = RETREAT**. Actual: **RETREAT > HOLD > ADVANCE**. Wrong maximum: HOLD (K3).

**Context 30 — O2, mapping 3, state 3.**

| Action | Alias | Chronological history: epoch/transaction:(next_state, consequence) | Map prediction | Actual | Latest relation |
| --- | --- | --- | --- | --- | --- |
| ADVANCE | Z2 | 1001/4:(0, -1) | (0, -1) | (0, -1) | LATEST_COPY |
| HOLD | Q7 | 1001/1:(3, 0) | (3, 0) | (3, 0) | LATEST_COPY |
| RETREAT | M4 | 1001/2:(2, +1) | (1, -1) | (2, +1) | NON_LATEST |

Predicted: **HOLD > ADVANCE = RETREAT**. Actual: **RETREAT > HOLD > ADVANCE**. Wrong maximum: HOLD (Q7).

**Context 32 — O1, mapping 4, state 3.**

| Action | Alias | Chronological history: epoch/transaction:(next_state, consequence) | Map prediction | Actual | Latest relation |
| --- | --- | --- | --- | --- | --- |
| ADVANCE | K2 | 1001/4:(0, -1) | (0, -1) | (0, -1) | LATEST_COPY |
| HOLD | K3 | 1001/1:(3, 0) | (3, 0) | (3, 0) | LATEST_COPY |
| RETREAT | K1 | 1001/2:(2, +1) | (0, -1) | (2, +1) | NON_LATEST |

Predicted: **HOLD > ADVANCE = RETREAT**. Actual: **RETREAT > HOLD > ADVANCE**. Wrong maximum: HOLD (K3).

**Context 33 — O2, mapping 4, state 3.**

| Action | Alias | Chronological history: epoch/transaction:(next_state, consequence) | Map prediction | Actual | Latest relation |
| --- | --- | --- | --- | --- | --- |
| ADVANCE | M4 | 1001/4:(0, -1) | (0, -1) | (0, -1) | LATEST_COPY |
| HOLD | Z2 | 1001/1:(3, 0) | (3, 0) | (3, 0) | LATEST_COPY |
| RETREAT | Q7 | 1001/2:(2, +1) | (0, -1) | (2, +1) | NON_LATEST |

Predicted: **HOLD > ADVANCE = RETREAT**. Actual: **RETREAT > HOLD > ADVANCE**. Wrong maximum: HOLD (Z2).

The other eight W3 contexts have the correct unique maximum. Four of those nevertheless underpredict HOLD from 0 to −1 (contexts 25, 26, 31, 34), creating a lower-ranked tie while leaving RETREAT uniquely best. These are errors without pipeline ranking failure and are retained in all accuracy counts.

## D1: successful ranking, not uniformly exact forecasts

All twelve contexts have histories ADVANCE [−1] (depth 1), HOLD [+1, −1, −1] (depth 3), RETREAT [0, 0] (depth 2), and actual/latest triple **(−1, −1, 0)**. Eleven predict that consequence triple; context 45 predicts **(−1, −1, +1)**. All twelve therefore rank RETREAT uniquely best. Ten contexts have all three complete outcomes exact. Context 45 has an ADVANCE next_state error (3 instead of 2) and a RETREAT consequence error (+1 instead of 0); context 47 has an ADVANCE next_state error (0 instead of 2).

| Context | Family | Mapping | Predicted triple | All three outcomes exact? | Predicted ranking |
| --- | --- | --- | --- | --- | --- |
| 36 | O2 | 0 | (-1, -1, 0) | yes | RETREAT > ADVANCE = HOLD |
| 37 | O1 | 0 | (-1, -1, 0) | yes | RETREAT > ADVANCE = HOLD |
| 38 | O1 | 1 | (-1, -1, 0) | yes | RETREAT > ADVANCE = HOLD |
| 39 | O2 | 1 | (-1, -1, 0) | yes | RETREAT > ADVANCE = HOLD |
| 40 | O2 | 2 | (-1, -1, 0) | yes | RETREAT > ADVANCE = HOLD |
| 41 | O1 | 2 | (-1, -1, 0) | yes | RETREAT > ADVANCE = HOLD |
| 42 | O1 | 3 | (-1, -1, 0) | yes | RETREAT > ADVANCE = HOLD |
| 43 | O2 | 3 | (-1, -1, 0) | yes | RETREAT > ADVANCE = HOLD |
| 44 | O2 | 4 | (-1, -1, 0) | yes | RETREAT > ADVANCE = HOLD |
| 45 | O1 | 4 | (-1, -1, +1) | no | RETREAT > ADVANCE = HOLD |
| 46 | O1 | 5 | (-1, -1, 0) | yes | RETREAT > ADVANCE = HOLD |
| 47 | O2 | 5 | (-1, -1, 0) | no | RETREAT > ADVANCE = HOLD |

D1 consequence/latest-copy accuracy is 35/36; exact accuracy is 33/36. Latest-history behavior aligns with retained current reality, but ranking survives the one consequence error. Unlike W1, the current best consequence is 0, both competitors are −1, and no current +1 must be retained. HOLD’s depth, chronological contradiction, current consequence and epoch also differ. These covary; the data do not identify a beneficial history-depth effect or a revision mechanism.

## Complete 48-context ranking table

Classification: TRUE = true-best unique; WRONG = wrong unique; TIE = tied maximum. Mapping indices and context indices are zero-based. Ranking describes the full weak order, including ties below the maximum.

| Context | World | Family | Mapping | State | Aliases A/H/R | Prediction triple | Actual triple | Predicted ranking | Actual ranking | Class |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | W0 | O1 | 0 | 0 | K1/K2/K3 | (+1, 0, -1) | (+1, 0, -1) | ADVANCE > HOLD > RETREAT | ADVANCE > HOLD > RETREAT | TRUE |
| 1 | W0 | O2 | 0 | 0 | Q7/M4/Z2 | (+1, 0, -1) | (+1, 0, -1) | ADVANCE > HOLD > RETREAT | ADVANCE > HOLD > RETREAT | TRUE |
| 2 | W0 | O2 | 1 | 0 | Q7/Z2/M4 | (0, 0, -1) | (+1, 0, -1) | ADVANCE = HOLD > RETREAT | ADVANCE > HOLD > RETREAT | TIE |
| 3 | W0 | O1 | 1 | 0 | K1/K3/K2 | (0, 0, -1) | (+1, 0, -1) | ADVANCE = HOLD > RETREAT | ADVANCE > HOLD > RETREAT | TIE |
| 4 | W0 | O1 | 2 | 0 | K2/K1/K3 | (+1, 0, -1) | (+1, 0, -1) | ADVANCE > HOLD > RETREAT | ADVANCE > HOLD > RETREAT | TRUE |
| 5 | W0 | O2 | 2 | 0 | M4/Q7/Z2 | (0, 0, -1) | (+1, 0, -1) | ADVANCE = HOLD > RETREAT | ADVANCE > HOLD > RETREAT | TIE |
| 6 | W0 | O2 | 3 | 0 | Z2/Q7/M4 | (+1, 0, -1) | (+1, 0, -1) | ADVANCE > HOLD > RETREAT | ADVANCE > HOLD > RETREAT | TRUE |
| 7 | W0 | O1 | 3 | 0 | K3/K1/K2 | (0, 0, -1) | (+1, 0, -1) | ADVANCE = HOLD > RETREAT | ADVANCE > HOLD > RETREAT | TIE |
| 8 | W0 | O1 | 4 | 0 | K2/K3/K1 | (0, 0, -1) | (+1, 0, -1) | ADVANCE = HOLD > RETREAT | ADVANCE > HOLD > RETREAT | TIE |
| 9 | W0 | O2 | 4 | 0 | M4/Z2/Q7 | (0, 0, -1) | (+1, 0, -1) | ADVANCE = HOLD > RETREAT | ADVANCE > HOLD > RETREAT | TIE |
| 10 | W0 | O2 | 5 | 0 | Z2/M4/Q7 | (0, 0, -1) | (+1, 0, -1) | ADVANCE = HOLD > RETREAT | ADVANCE > HOLD > RETREAT | TIE |
| 11 | W0 | O1 | 5 | 0 | K3/K2/K1 | (+1, 0, -1) | (+1, 0, -1) | ADVANCE > HOLD > RETREAT | ADVANCE > HOLD > RETREAT | TRUE |
| 12 | W1 | O2 | 0 | 1 | Q7/M4/Z2 | (-1, 0, 0) | (-1, +1, 0) | HOLD = RETREAT > ADVANCE | HOLD > RETREAT > ADVANCE | TIE |
| 13 | W1 | O1 | 0 | 1 | K1/K2/K3 | (-1, 0, 0) | (-1, +1, 0) | HOLD = RETREAT > ADVANCE | HOLD > RETREAT > ADVANCE | TIE |
| 14 | W1 | O1 | 1 | 1 | K1/K3/K2 | (-1, 0, 0) | (-1, +1, 0) | HOLD = RETREAT > ADVANCE | HOLD > RETREAT > ADVANCE | TIE |
| 15 | W1 | O2 | 1 | 1 | Q7/Z2/M4 | (-1, 0, 0) | (-1, +1, 0) | HOLD = RETREAT > ADVANCE | HOLD > RETREAT > ADVANCE | TIE |
| 16 | W1 | O2 | 2 | 1 | M4/Q7/Z2 | (-1, 0, 0) | (-1, +1, 0) | HOLD = RETREAT > ADVANCE | HOLD > RETREAT > ADVANCE | TIE |
| 17 | W1 | O1 | 2 | 1 | K2/K1/K3 | (-1, 0, 0) | (-1, +1, 0) | HOLD = RETREAT > ADVANCE | HOLD > RETREAT > ADVANCE | TIE |
| 18 | W1 | O1 | 3 | 1 | K3/K1/K2 | (-1, 0, 0) | (-1, +1, 0) | HOLD = RETREAT > ADVANCE | HOLD > RETREAT > ADVANCE | TIE |
| 19 | W1 | O2 | 3 | 1 | Z2/Q7/M4 | (-1, 0, 0) | (-1, +1, 0) | HOLD = RETREAT > ADVANCE | HOLD > RETREAT > ADVANCE | TIE |
| 20 | W1 | O2 | 4 | 1 | M4/Z2/Q7 | (-1, 0, 0) | (-1, +1, 0) | HOLD = RETREAT > ADVANCE | HOLD > RETREAT > ADVANCE | TIE |
| 21 | W1 | O1 | 4 | 1 | K2/K3/K1 | (-1, 0, 0) | (-1, +1, 0) | HOLD = RETREAT > ADVANCE | HOLD > RETREAT > ADVANCE | TIE |
| 22 | W1 | O1 | 5 | 1 | K3/K2/K1 | (-1, 0, 0) | (-1, +1, 0) | HOLD = RETREAT > ADVANCE | HOLD > RETREAT > ADVANCE | TIE |
| 23 | W1 | O2 | 5 | 1 | Z2/M4/Q7 | (-1, 0, 0) | (-1, +1, 0) | HOLD = RETREAT > ADVANCE | HOLD > RETREAT > ADVANCE | TIE |
| 24 | W3 | O1 | 0 | 3 | K1/K2/K3 | (-1, 0, +1) | (-1, 0, +1) | RETREAT > HOLD > ADVANCE | RETREAT > HOLD > ADVANCE | TRUE |
| 25 | W3 | O2 | 0 | 3 | Q7/M4/Z2 | (-1, -1, +1) | (-1, 0, +1) | RETREAT > ADVANCE = HOLD | RETREAT > HOLD > ADVANCE | TRUE |
| 26 | W3 | O2 | 1 | 3 | Q7/Z2/M4 | (-1, -1, +1) | (-1, 0, +1) | RETREAT > ADVANCE = HOLD | RETREAT > HOLD > ADVANCE | TRUE |
| 27 | W3 | O1 | 1 | 3 | K1/K3/K2 | (-1, 0, -1) | (-1, 0, +1) | HOLD > ADVANCE = RETREAT | RETREAT > HOLD > ADVANCE | WRONG |
| 28 | W3 | O1 | 2 | 3 | K2/K1/K3 | (-1, 0, +1) | (-1, 0, +1) | RETREAT > HOLD > ADVANCE | RETREAT > HOLD > ADVANCE | TRUE |
| 29 | W3 | O2 | 2 | 3 | M4/Q7/Z2 | (-1, 0, +1) | (-1, 0, +1) | RETREAT > HOLD > ADVANCE | RETREAT > HOLD > ADVANCE | TRUE |
| 30 | W3 | O2 | 3 | 3 | Z2/Q7/M4 | (-1, 0, -1) | (-1, 0, +1) | HOLD > ADVANCE = RETREAT | RETREAT > HOLD > ADVANCE | WRONG |
| 31 | W3 | O1 | 3 | 3 | K3/K1/K2 | (-1, -1, +1) | (-1, 0, +1) | RETREAT > ADVANCE = HOLD | RETREAT > HOLD > ADVANCE | TRUE |
| 32 | W3 | O1 | 4 | 3 | K2/K3/K1 | (-1, 0, -1) | (-1, 0, +1) | HOLD > ADVANCE = RETREAT | RETREAT > HOLD > ADVANCE | WRONG |
| 33 | W3 | O2 | 4 | 3 | M4/Z2/Q7 | (-1, 0, -1) | (-1, 0, +1) | HOLD > ADVANCE = RETREAT | RETREAT > HOLD > ADVANCE | WRONG |
| 34 | W3 | O2 | 5 | 3 | Z2/M4/Q7 | (-1, -1, +1) | (-1, 0, +1) | RETREAT > ADVANCE = HOLD | RETREAT > HOLD > ADVANCE | TRUE |
| 35 | W3 | O1 | 5 | 3 | K3/K2/K1 | (-1, 0, +1) | (-1, 0, +1) | RETREAT > HOLD > ADVANCE | RETREAT > HOLD > ADVANCE | TRUE |
| 36 | D1 | O2 | 0 | 1 | Q7/M4/Z2 | (-1, -1, 0) | (-1, -1, 0) | RETREAT > ADVANCE = HOLD | RETREAT > ADVANCE = HOLD | TRUE |
| 37 | D1 | O1 | 0 | 1 | K1/K2/K3 | (-1, -1, 0) | (-1, -1, 0) | RETREAT > ADVANCE = HOLD | RETREAT > ADVANCE = HOLD | TRUE |
| 38 | D1 | O1 | 1 | 1 | K1/K3/K2 | (-1, -1, 0) | (-1, -1, 0) | RETREAT > ADVANCE = HOLD | RETREAT > ADVANCE = HOLD | TRUE |
| 39 | D1 | O2 | 1 | 1 | Q7/Z2/M4 | (-1, -1, 0) | (-1, -1, 0) | RETREAT > ADVANCE = HOLD | RETREAT > ADVANCE = HOLD | TRUE |
| 40 | D1 | O2 | 2 | 1 | M4/Q7/Z2 | (-1, -1, 0) | (-1, -1, 0) | RETREAT > ADVANCE = HOLD | RETREAT > ADVANCE = HOLD | TRUE |
| 41 | D1 | O1 | 2 | 1 | K2/K1/K3 | (-1, -1, 0) | (-1, -1, 0) | RETREAT > ADVANCE = HOLD | RETREAT > ADVANCE = HOLD | TRUE |
| 42 | D1 | O1 | 3 | 1 | K3/K1/K2 | (-1, -1, 0) | (-1, -1, 0) | RETREAT > ADVANCE = HOLD | RETREAT > ADVANCE = HOLD | TRUE |
| 43 | D1 | O2 | 3 | 1 | Z2/Q7/M4 | (-1, -1, 0) | (-1, -1, 0) | RETREAT > ADVANCE = HOLD | RETREAT > ADVANCE = HOLD | TRUE |
| 44 | D1 | O2 | 4 | 1 | M4/Z2/Q7 | (-1, -1, 0) | (-1, -1, 0) | RETREAT > ADVANCE = HOLD | RETREAT > ADVANCE = HOLD | TRUE |
| 45 | D1 | O1 | 4 | 1 | K2/K3/K1 | (-1, -1, +1) | (-1, -1, 0) | RETREAT > ADVANCE = HOLD | RETREAT > ADVANCE = HOLD | TRUE |
| 46 | D1 | O1 | 5 | 1 | K3/K2/K1 | (-1, -1, 0) | (-1, -1, 0) | RETREAT > ADVANCE = HOLD | RETREAT > ADVANCE = HOLD | TRUE |
| 47 | D1 | O2 | 5 | 1 | Z2/M4/Q7 | (-1, -1, 0) | (-1, -1, 0) | RETREAT > ADVANCE = HOLD | RETREAT > ADVANCE = HOLD | TRUE |

## Latest-copy, depth, action and alias analysis

LATEST_COPY compares **consequence only**, as requested; it does not assert copying occurred internally. NON_LATEST is its complement. Exact accuracy requires both next_state and consequence. Rates include every forecast. “Tie members” counts forecasts at a tied maximum; “tie-creating errors” counts erroneous forecasts whose individual replacement by the retained actual consequence removes that maximum tie. This last metric is finite arithmetic, not a new world execution or a change to the operational forecast. “Wrong-max members” counts the forecast selected by a wrong unique ranking, even if that individual forecast is correct (all four are correct HOLD forecasts).

| World | N | Outputs −1 / 0 / +1 | Latest copy | Exact accuracy | Consequence accuracy | Tie members | Tie-creating errors | Wrong-ranking errors | Wrong-max members |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | 36 | 24 / 11 / 1 | 35/36 (97.2%) | 33/36 (91.7%) | 35/36 (97.2%) | 0 | 0 | 0 | 0 |
| W0 | 36 | 12 / 19 / 5 | 29/36 (80.6%) | 29/36 (80.6%) | 29/36 (80.6%) | 14 | 7 | 0 | 0 |
| W1 | 36 | 12 / 24 / 0 | 24/36 (66.7%) | 21/36 (58.3%) | 24/36 (66.7%) | 24 | 12 | 0 | 0 |
| W3 | 36 | 20 / 8 / 8 | 28/36 (77.8%) | 28/36 (77.8%) | 28/36 (77.8%) | 0 | 0 | 4 | 4 |

| Family | N | Outputs −1 / 0 / +1 | Latest copy | Exact accuracy | Consequence accuracy | Tie members | Tie-creating errors | Wrong-ranking errors | Wrong-max members |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| O1 | 72 | 33 / 31 / 8 | 59/72 (81.9%) | 57/72 (79.2%) | 59/72 (81.9%) | 18 | 9 | 2 | 2 |
| O2 | 72 | 35 / 31 / 6 | 57/72 (79.2%) | 54/72 (75.0%) | 57/72 (79.2%) | 20 | 10 | 2 | 2 |

| Depth | N | Outputs −1 / 0 / +1 | Latest copy | Exact accuracy | Consequence accuracy | Tie members | Tie-creating errors | Wrong-ranking errors | Wrong-max members |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 120 | 56 / 51 / 13 | 93/120 (77.5%) | 88/120 (73.3%) | 93/120 (77.5%) | 38 | 19 | 4 | 4 |
| 2 | 12 | 0 / 11 / 1 | 11/12 (91.7%) | 11/12 (91.7%) | 11/12 (91.7%) | 0 | 0 | 0 | 0 |
| 3+ | 12 | 12 / 0 / 0 | 12/12 (100.0%) | 12/12 (100.0%) | 12/12 (100.0%) | 0 | 0 | 0 | 0 |

| Action | N | Outputs −1 / 0 / +1 | Latest copy | Exact accuracy | Consequence accuracy | Tie members | Tie-creating errors | Wrong-ranking errors | Wrong-max members |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | 48 | 36 / 7 / 5 | 41/48 (85.4%) | 38/48 (79.2%) | 41/48 (85.4%) | 7 | 7 | 0 | 0 |
| HOLD | 48 | 16 / 32 / 0 | 32/48 (66.7%) | 32/48 (66.7%) | 32/48 (66.7%) | 19 | 12 | 0 | 4 |
| RETREAT | 48 | 16 / 23 / 9 | 43/48 (89.6%) | 41/48 (85.4%) | 43/48 (89.6%) | 12 | 0 | 4 | 0 |

| Alias | N | Outputs −1 / 0 / +1 | Latest copy | Exact accuracy | Consequence accuracy | Tie members | Tie-creating errors | Wrong-ranking errors | Wrong-max members |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| K1 | 24 | 12 / 9 / 3 | 18/24 (75.0%) | 18/24 (75.0%) | 18/24 (75.0%) | 6 | 3 | 1 | 0 |
| K2 | 24 | 11 / 11 / 2 | 20/24 (83.3%) | 19/24 (79.2%) | 20/24 (83.3%) | 5 | 3 | 1 | 0 |
| K3 | 24 | 10 / 11 / 3 | 21/24 (87.5%) | 20/24 (83.3%) | 21/24 (87.5%) | 7 | 3 | 0 | 2 |
| M4 | 24 | 13 / 10 / 1 | 17/24 (70.8%) | 17/24 (70.8%) | 17/24 (70.8%) | 7 | 4 | 1 | 0 |
| Q7 | 24 | 11 / 11 / 2 | 20/24 (83.3%) | 20/24 (83.3%) | 20/24 (83.3%) | 6 | 3 | 1 | 1 |
| Z2 | 24 | 11 / 10 / 3 | 20/24 (83.3%) | 17/24 (70.8%) | 20/24 (83.3%) | 7 | 3 | 0 | 1 |

Overall: **116/144 LATEST_COPY, 28/144 NON_LATEST; 111/144 exact, 116/144 consequence-correct.** Latest consequence equals retained actual consequence in all 144 inputs. Consequently, latest-copy and consequence-accuracy counts coincide here and cannot distinguish genuine forecasting from copying. Of 36 actual +1 outcomes, 23 are underpredicted; of 108 nonpositive outcomes, five consequence forecasts are wrong. Those five occur in successful-ranking contexts (four W3 HOLD errors and one D1 RETREAT error).

Depth 1 has 120 forecasts, depth 2 has 12 (D1 RETREAT only), and depth 3+ has 12 (all depth 3, D1 HOLD only). All 19 tie-creating errors and all four wrong-ranking errors are depth 1. That association does not isolate depth: action, world, consequence and epoch differ. Full family × world/action/alias/mapping/depth breakdowns are in results.json; no forecast is omitted.

## Mapping, position and seed audit

| Mapping | N | Outputs −1 / 0 / +1 | Latest copy | Exact accuracy | Consequence accuracy | Tie members | Tie-creating errors | Wrong-ranking errors | Wrong-max members |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 24 | 11 / 9 / 4 | 21/24 (87.5%) | 20/24 (83.3%) | 21/24 (87.5%) | 4 | 2 | 0 | 0 |
| 1 | 24 | 12 / 11 / 1 | 18/24 (75.0%) | 18/24 (75.0%) | 18/24 (75.0%) | 8 | 4 | 1 | 1 |
| 2 | 24 | 10 / 11 / 3 | 21/24 (87.5%) | 20/24 (83.3%) | 21/24 (87.5%) | 6 | 3 | 0 | 0 |
| 3 | 24 | 12 / 10 / 2 | 19/24 (79.2%) | 18/24 (75.0%) | 19/24 (79.2%) | 6 | 3 | 1 | 1 |
| 4 | 24 | 12 / 11 / 1 | 17/24 (70.8%) | 16/24 (66.7%) | 17/24 (70.8%) | 8 | 4 | 2 | 2 |
| 5 | 24 | 11 / 10 / 3 | 20/24 (83.3%) | 19/24 (79.2%) | 20/24 (83.3%) | 6 | 3 | 0 | 0 |

| Alias registry position | N | Outputs −1 / 0 / +1 | Latest copy | Exact accuracy | Consequence accuracy | Tie members | Tie-creating errors | Wrong-ranking errors | Wrong-max members |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 48 | 23 / 20 / 5 | 38/48 (79.2%) | 38/48 (79.2%) | 38/48 (79.2%) | 12 | 6 | 2 | 1 |
| 2 | 48 | 24 / 21 / 3 | 37/48 (77.1%) | 36/48 (75.0%) | 37/48 (77.1%) | 12 | 7 | 2 | 0 |
| 3 | 48 | 21 / 21 / 6 | 41/48 (85.4%) | 37/48 (77.1%) | 41/48 (85.4%) | 14 | 6 | 0 | 3 |

| Map call position | N | Outputs −1 / 0 / +1 | Latest copy | Exact accuracy | Consequence accuracy | Tie members | Tie-creating errors | Wrong-ranking errors | Wrong-max members |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 48 | 36 / 7 / 5 | 41/48 (85.4%) | 38/48 (79.2%) | 41/48 (85.4%) | 7 | 7 | 0 | 0 |
| 2 | 48 | 16 / 32 / 0 | 32/48 (66.7%) | 32/48 (66.7%) | 32/48 (66.7%) | 19 | 12 | 0 | 4 |
| 3 | 48 | 16 / 23 / 9 | 43/48 (89.6%) | 41/48 (85.4%) | 43/48 (89.6%) | 12 | 0 | 4 | 0 |

Registered alias positions are O1 **K1/K2/K3** and O2 **Q7/M4/Z2**, recovered from retained ordered forecast views, not alphabetic sorting. They are not positions in a Map list: each Map request has one target alias and its own history. Alias registry position is inseparable from alias identity within a family. Call position is always ADVANCE/HOLD/RETREAT and is therefore inseparable from underlying action. Neither is evidence of an independent positional mechanism. Mapping index also covaries with seed; state and next_state values are visible, but world names, underlying action names and mapping indices are analyst labels.

| World | Matched seed/action pairs | Same consequence | Different consequence |
| --- | --- | --- | --- |
| W0 | 18 | 15 | 3 |
| W1 | 18 | 18 | 0 |
| W3 | 18 | 12 | 6 |
| D1 | 18 | 17 | 1 |

There are 72 O1/O2 matched world/mapping/action pairs using the same recorded seed; 62/72 predict the same consequence and 10/72 differ. Underlying histories and current state match within these pairs, while opaque aliases differ. This is compatible with sensitivity to the representation under the recorded sampling setup, not proof of a causal token or dominant representation mechanism. One output per exact request/seed cannot separate sampling/runtime variation from representation. W1 remains invariantly wrong across all twelve contexts and all six HOLD aliases. Every seed, call index and prediction is listed in the reconstruction; seed-group distributions and all 72 pairs are in results.json.

## Simple explanation compatibility, not fitted causal models

Rules A–C compare predicted consequence with latest, most frequent, or first visible consequence. Most-frequent and latest coincide for every retained action history, so this dataset cannot separate them. Rule D is scored only as the observable **constant-zero proxy**; uncertainty was not recorded, so “return zero when uncertain” itself is not identifiable. Rules E/F use the best single fixed output per alias/underlying action over all 144 observations, an optimistic in-sample modal baseline with no held-out predictive claim. No complex predictor was fitted.

| Rule | All /144 | O1 /72 | O2 /72 | W0 /36 | W1 /36 | W3 /36 | D1 /36 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A: latest | 116/144 (80.6%) | 59/72 (81.9%) | 57/72 (79.2%) | 29/36 (80.6%) | 24/36 (66.7%) | 28/36 (77.8%) | 35/36 (97.2%) |
| B: most frequent | 116/144 (80.6%) | 59/72 (81.9%) | 57/72 (79.2%) | 29/36 (80.6%) | 24/36 (66.7%) | 28/36 (77.8%) | 35/36 (97.2%) |
| C: first | 104/144 (72.2%) | 53/72 (73.6%) | 51/72 (70.8%) | 29/36 (80.6%) | 24/36 (66.7%) | 28/36 (77.8%) | 23/36 (63.9%) |
| D: zero proxy | 62/144 (43.1%) | 31/72 (43.1%) | 31/72 (43.1%) | 19/36 (52.8%) | 24/36 (66.7%) | 8/36 (22.2%) | 11/36 (30.6%) |
| E: fixed alias (fitted) | 69/144 (47.9%) | 34/72 (47.2%) | 35/72 (48.6%) | 13/36 (36.1%) | 14/36 (38.9%) | 20/36 (55.6%) | 22/36 (61.1%) |
| F: fixed action (fitted) | 91/144 (63.2%) | 46/72 (63.9%) | 45/72 (62.5%) | 12/36 (33.3%) | 36/36 (100.0%) | 20/36 (55.6%) | 23/36 (63.9%) |

Fixed-action constants are ADVANCE −1, HOLD 0, RETREAT 0. Fixed-alias selected constants are K1 −1, K2 −1, K3 0, M4 −1, Q7 −1, Z2 −1. K2 and Q7 each have tied modes {−1, 0}; the lowest value is selected solely to make these descriptive rule tables reproducible. Either alternative gives the same overall/family match total but changes some world breakdowns. This convention does **not** modify or tie-break the mechanical exploitation interface. Every alias produces multiple output values; no fixed alias rule describes the full data. Underlying action labels were not model-visible.

## Latest-value ranking counterfactual

Using only the last retained history consequences yields **48/48 true-best unique rankings**, zero maximum ties and zero wrong maxima. Actual Map gives 25 true-best unique, 19 ties and four wrong unique. Thus **none of the 23 ranking failures is reproduced by the latest-value rule**. This counterfactual changes only an analyst’s finite table; no forecast or world is modified.

| Full weak-order comparison | Contexts |
| --- | --- |
| DIFFERENT | 27 |
| SAME_RANKING | 21 |
| SAME_TIE | 0 |
| SAME_WRONG_MAXIMUM | 0 |

The mutually exclusive comparison uses exact full weak-order equality: same ranking 21, same tie 0, same wrong maximum 0, different 27. Maximum-set equality is **25/48**; exact consequence-triple equality is **20/48**. The four extra full-ranking differences are successful W3 contexts 25, 26, 31, 34, where HOLD joins ADVANCE at −1 below correct RETREAT. D1 context 45 changes RETREAT’s value from 0 to +1 while preserving the full order. These definitions prevent a lower-ranked tie from being confused with a failure to act.

## All 23 residual-failure classifications and finite-domain diagnosis

All 23 classify **A — TRUE-BEST ACTION UNDERPREDICTED**. B, C, D, E and F each have zero cases. For potentially overlapping categories, the analysis would assign D to a tie with multiple consequence errors, then C if both under/over flags exist, then A/B, then E/F; it preserves the individual flags and error actions. No such overlap occurs here. “Error” in this classification means consequence error; unrelated next_state errors are reported separately.

| Context | World | Family | Mapping | True-best alias/action | Latest = actual | Predicted | Maximum produced | Class |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | W0 | O2 | 1 | Q7/ADVANCE | +1 | 0 | ADVANCE = HOLD | A |
| 3 | W0 | O1 | 1 | K1/ADVANCE | +1 | 0 | ADVANCE = HOLD | A |
| 5 | W0 | O2 | 2 | M4/ADVANCE | +1 | 0 | ADVANCE = HOLD | A |
| 7 | W0 | O1 | 3 | K3/ADVANCE | +1 | 0 | ADVANCE = HOLD | A |
| 8 | W0 | O1 | 4 | K2/ADVANCE | +1 | 0 | ADVANCE = HOLD | A |
| 9 | W0 | O2 | 4 | M4/ADVANCE | +1 | 0 | ADVANCE = HOLD | A |
| 10 | W0 | O2 | 5 | Z2/ADVANCE | +1 | 0 | ADVANCE = HOLD | A |
| 12 | W1 | O2 | 0 | M4/HOLD | +1 | 0 | HOLD = RETREAT | A |
| 13 | W1 | O1 | 0 | K2/HOLD | +1 | 0 | HOLD = RETREAT | A |
| 14 | W1 | O1 | 1 | K3/HOLD | +1 | 0 | HOLD = RETREAT | A |
| 15 | W1 | O2 | 1 | Z2/HOLD | +1 | 0 | HOLD = RETREAT | A |
| 16 | W1 | O2 | 2 | Q7/HOLD | +1 | 0 | HOLD = RETREAT | A |
| 17 | W1 | O1 | 2 | K1/HOLD | +1 | 0 | HOLD = RETREAT | A |
| 18 | W1 | O1 | 3 | K1/HOLD | +1 | 0 | HOLD = RETREAT | A |
| 19 | W1 | O2 | 3 | Q7/HOLD | +1 | 0 | HOLD = RETREAT | A |
| 20 | W1 | O2 | 4 | Z2/HOLD | +1 | 0 | HOLD = RETREAT | A |
| 21 | W1 | O1 | 4 | K3/HOLD | +1 | 0 | HOLD = RETREAT | A |
| 22 | W1 | O1 | 5 | K2/HOLD | +1 | 0 | HOLD = RETREAT | A |
| 23 | W1 | O2 | 5 | M4/HOLD | +1 | 0 | HOLD = RETREAT | A |
| 27 | W3 | O1 | 1 | K2/RETREAT | +1 | -1 | HOLD | A |
| 30 | W3 | O2 | 3 | M4/RETREAT | +1 | -1 | HOLD | A |
| 32 | W3 | O1 | 4 | K1/RETREAT | +1 | -1 | HOLD | A |
| 33 | W3 | O2 | 4 | Q7/RETREAT | +1 | -1 | HOLD | A |

**All 19 maximum ties involve forecast error; 0/19 are genuine correct-forecast ties under the declared finite objective.** Every retained actual triple has a unique best. W0/W1 tie creation is +1→0 compression introduced by an erroneous forecast, not an unavoidable limitation of {−1,0,+1}. D1’s correct −1/−1 tie is below the unique maximum and does not prevent exploitation. No continuous quality measure was retained, so the study cannot diagnose hidden within-bin differences in unrecorded utility. No domain, confidence field or continuous value was introduced.

## Narrowest defensible diagnosis and smallest next experiment

**MAP RANKING FAILURE DOMINANTLY CONSISTENT WITH: NOT DETERMINABLE FROM RETAINED EVIDENCE.** This category concerns the requested mechanistic alternatives, not missing or ambiguous arithmetic. Observed behavior is compatible with frequent latest-value matching overall and context-dependent departure from positive history. Recency alone explains none of the residual failures; intrinsic finite-domain maximum ties explain none; alias/seed-associated variation exists but does not establish that representation bias dominates. A MIXED-CAUSES label would overclaim multiple established mechanisms, so it is not selected.

Recommend one small prospective **W1 HOLD history-depth contrast**, not a new architecture: depth 1 versus depth 2 with two independently authenticated +1 observations for the same state/action, identical latest outcome and current finite truth. Hold model, prompt, action alias within each pair, current state, next_state and scoring fixed. Use two retained alias blocks (O1 mapping 0 HOLD=K2 and O2 mapping 0 HOLD=M4), each with two predeclared paired seeds: **2 depths × 2 alias blocks × 2 seeds = 8 Map calls**, no Explorer calls. Fresh baseline/treatment responses must both be retained; do not compare only a new treatment against an old lucky/unlucky run. The extra observation must be genuinely acquired and authenticated in the separately approved future experiment; never duplicate a record or relabel a synthetic observation as verified. Chronological identity fields necessarily differ and should be disclosed.

This tests sensitivity to sparse versus repeated positive evidence while keeping the positive consequence and alias fixed within pairs. +1 in both conditions is compatible with latest/history following; systematic 0→+1 changes are evidence of sensitivity to additional positive history; continued 0 in both is compatible with a persistent non-latest, context-dependent output pattern. None identifies an internal algorithm, and eight calls would be a feasibility diagnostic, not a broad mechanism claim. Freeze schedule/scoring before that future run; expand only if its retained contrast justifies it. Mechanical exploitation remains the unchanged reference and no Explorer redesign is proposed. **Not executed or preregistered here.**

## Firewall, verification and limitations

Actual execution during this task was limited to JSON extraction, hashing and deterministic finite-data analysis. No model/transport/world/runtime or mechanical chooser module was imported. Truth labels are held separately from model-visible histories; exact archived requests were checked rather than changed. No declared-law score was upgraded to receipt-grounded forecast evidence, and no old stationary A/B/C observer supplied truth. The historical pipeline and mechanical reports remain unchanged. All **685** parent tracked files retained exact bytes/modes; root/firewall and parent evidence hashes matched. Two separate analysis/verification processes produced byte-identical JSON outputs. Original archive seals were rechecked after analysis. Main/tags unchanged; no push.

All 48 contexts and 144 forecasts are included. Analyses are post hoc and descriptive; no significance or performance threshold was added. There is one recorded forecast per target/request/seed. Histories, current state, output consequence, epoch and depth are not independently randomized. Most history depths are one; latest and mode agree everywhere. Exact-pair provenance is reconstructed from retained fields and hashes, not live object identity. Actual current outcomes are detached evaluator labels. These records support precise error attribution and compatibility counts, not hidden cognition, causality, confidence, generalized learning, closed-loop improvement or future behavioral guarantees.

The requested neutral / predecessor-only / hardware-only / combined factorial remains deferred. The unchanged predecessor-specific four-arm note is retained privately outside the public tree; it is not implemented or mixed into this analysis.

## Complete 144-action reconstruction: all three actions in all 48 contexts

Each history cell lists **all** chronological exact-pair observations as `epoch/transaction:(next_state, consequence)`; pre_state is the context’s current state, and surface_action is the row’s opaque alias. No history is abbreviated. “Latest” is the final history pair; full latest epoch/transaction identity is retained by that final entry. Prediction is the exact parsed finite Map object represented as `(next_state, consequence)`; original raw response text is not needed or published. C = consequence correct, E = both fields exact; latest relation is consequence-only. Seeds are original transport seeds, not new inference.

### Context 0 — W0 / O1 / mapping 0 / state 0 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | K1 | 1001/2:(1, +1) | 1 | (1, +1) | (1, +1) | (1, +1) | yes / yes | LATEST_COPY | 96002 |
| HOLD | K2 | 1001/1:(0, 0) | 1 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96003 |
| RETREAT | K3 | 1001/4:(3, -1) | 1 | (3, -1) | (3, -1) | (3, -1) | yes / yes | LATEST_COPY | 96004 |

Predicted: **ADVANCE > HOLD > RETREAT**. Actual: **ADVANCE > HOLD > RETREAT**. `MAP_TRUE_BEST_UNIQUE`.

### Context 1 — W0 / O2 / mapping 0 / state 0 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | Q7 | 1001/2:(1, +1) | 1 | (1, +1) | (1, +1) | (1, +1) | yes / yes | LATEST_COPY | 96002 |
| HOLD | M4 | 1001/1:(0, 0) | 1 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96003 |
| RETREAT | Z2 | 1001/4:(3, -1) | 1 | (3, -1) | (3, -1) | (3, -1) | yes / yes | LATEST_COPY | 96004 |

Predicted: **ADVANCE > HOLD > RETREAT**. Actual: **ADVANCE > HOLD > RETREAT**. `MAP_TRUE_BEST_UNIQUE`.

### Context 2 — W0 / O2 / mapping 1 / state 0 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | Q7 | 1001/2:(1, +1) | 1 | (1, +1) | (1, 0) | (1, +1) | no / no | NON_LATEST | 96012 |
| HOLD | Z2 | 1001/1:(0, 0) | 1 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96013 |
| RETREAT | M4 | 1001/4:(3, -1) | 1 | (3, -1) | (3, -1) | (3, -1) | yes / yes | LATEST_COPY | 96014 |

Predicted: **ADVANCE = HOLD > RETREAT**. Actual: **ADVANCE > HOLD > RETREAT**. `MAP_TIE`.

### Context 3 — W0 / O1 / mapping 1 / state 0 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | K1 | 1001/2:(1, +1) | 1 | (1, +1) | (1, 0) | (1, +1) | no / no | NON_LATEST | 96012 |
| HOLD | K3 | 1001/1:(0, 0) | 1 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96013 |
| RETREAT | K2 | 1001/4:(3, -1) | 1 | (3, -1) | (3, -1) | (3, -1) | yes / yes | LATEST_COPY | 96014 |

Predicted: **ADVANCE = HOLD > RETREAT**. Actual: **ADVANCE > HOLD > RETREAT**. `MAP_TIE`.

### Context 4 — W0 / O1 / mapping 2 / state 0 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | K2 | 1001/2:(1, +1) | 1 | (1, +1) | (1, +1) | (1, +1) | yes / yes | LATEST_COPY | 96022 |
| HOLD | K1 | 1001/1:(0, 0) | 1 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96023 |
| RETREAT | K3 | 1001/4:(3, -1) | 1 | (3, -1) | (3, -1) | (3, -1) | yes / yes | LATEST_COPY | 96024 |

Predicted: **ADVANCE > HOLD > RETREAT**. Actual: **ADVANCE > HOLD > RETREAT**. `MAP_TRUE_BEST_UNIQUE`.

### Context 5 — W0 / O2 / mapping 2 / state 0 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | M4 | 1001/2:(1, +1) | 1 | (1, +1) | (1, 0) | (1, +1) | no / no | NON_LATEST | 96022 |
| HOLD | Q7 | 1001/1:(0, 0) | 1 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96023 |
| RETREAT | Z2 | 1001/4:(3, -1) | 1 | (3, -1) | (3, -1) | (3, -1) | yes / yes | LATEST_COPY | 96024 |

Predicted: **ADVANCE = HOLD > RETREAT**. Actual: **ADVANCE > HOLD > RETREAT**. `MAP_TIE`.

### Context 6 — W0 / O2 / mapping 3 / state 0 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | Z2 | 1001/2:(1, +1) | 1 | (1, +1) | (1, +1) | (1, +1) | yes / yes | LATEST_COPY | 96032 |
| HOLD | Q7 | 1001/1:(0, 0) | 1 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96033 |
| RETREAT | M4 | 1001/4:(3, -1) | 1 | (3, -1) | (3, -1) | (3, -1) | yes / yes | LATEST_COPY | 96034 |

Predicted: **ADVANCE > HOLD > RETREAT**. Actual: **ADVANCE > HOLD > RETREAT**. `MAP_TRUE_BEST_UNIQUE`.

### Context 7 — W0 / O1 / mapping 3 / state 0 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | K3 | 1001/2:(1, +1) | 1 | (1, +1) | (1, 0) | (1, +1) | no / no | NON_LATEST | 96032 |
| HOLD | K1 | 1001/1:(0, 0) | 1 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96033 |
| RETREAT | K2 | 1001/4:(3, -1) | 1 | (3, -1) | (3, -1) | (3, -1) | yes / yes | LATEST_COPY | 96034 |

Predicted: **ADVANCE = HOLD > RETREAT**. Actual: **ADVANCE > HOLD > RETREAT**. `MAP_TIE`.

### Context 8 — W0 / O1 / mapping 4 / state 0 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | K2 | 1001/2:(1, +1) | 1 | (1, +1) | (1, 0) | (1, +1) | no / no | NON_LATEST | 96042 |
| HOLD | K3 | 1001/1:(0, 0) | 1 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96043 |
| RETREAT | K1 | 1001/4:(3, -1) | 1 | (3, -1) | (3, -1) | (3, -1) | yes / yes | LATEST_COPY | 96044 |

Predicted: **ADVANCE = HOLD > RETREAT**. Actual: **ADVANCE > HOLD > RETREAT**. `MAP_TIE`.

### Context 9 — W0 / O2 / mapping 4 / state 0 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | M4 | 1001/2:(1, +1) | 1 | (1, +1) | (1, 0) | (1, +1) | no / no | NON_LATEST | 96042 |
| HOLD | Z2 | 1001/1:(0, 0) | 1 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96043 |
| RETREAT | Q7 | 1001/4:(3, -1) | 1 | (3, -1) | (3, -1) | (3, -1) | yes / yes | LATEST_COPY | 96044 |

Predicted: **ADVANCE = HOLD > RETREAT**. Actual: **ADVANCE > HOLD > RETREAT**. `MAP_TIE`.

### Context 10 — W0 / O2 / mapping 5 / state 0 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | Z2 | 1001/2:(1, +1) | 1 | (1, +1) | (1, 0) | (1, +1) | no / no | NON_LATEST | 96052 |
| HOLD | M4 | 1001/1:(0, 0) | 1 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96053 |
| RETREAT | Q7 | 1001/4:(3, -1) | 1 | (3, -1) | (3, -1) | (3, -1) | yes / yes | LATEST_COPY | 96054 |

Predicted: **ADVANCE = HOLD > RETREAT**. Actual: **ADVANCE > HOLD > RETREAT**. `MAP_TIE`.

### Context 11 — W0 / O1 / mapping 5 / state 0 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | K3 | 1001/2:(1, +1) | 1 | (1, +1) | (1, +1) | (1, +1) | yes / yes | LATEST_COPY | 96052 |
| HOLD | K2 | 1001/1:(0, 0) | 1 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96053 |
| RETREAT | K1 | 1001/4:(3, -1) | 1 | (3, -1) | (3, -1) | (3, -1) | yes / yes | LATEST_COPY | 96054 |

Predicted: **ADVANCE > HOLD > RETREAT**. Actual: **ADVANCE > HOLD > RETREAT**. `MAP_TRUE_BEST_UNIQUE`.

### Context 12 — W1 / O2 / mapping 0 / state 1 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | Q7 | 1001/4:(2, -1) | 1 | (2, -1) | (2, -1) | (2, -1) | yes / yes | LATEST_COPY | 96102 |
| HOLD | M4 | 1001/1:(1, +1) | 1 | (1, +1) | (1, 0) | (1, +1) | no / no | NON_LATEST | 96103 |
| RETREAT | Z2 | 1001/2:(0, 0) | 1 | (0, 0) | (1, 0) | (0, 0) | yes / no | LATEST_COPY | 96104 |

Predicted: **HOLD = RETREAT > ADVANCE**. Actual: **HOLD > RETREAT > ADVANCE**. `MAP_TIE`.

### Context 13 — W1 / O1 / mapping 0 / state 1 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | K1 | 1001/4:(2, -1) | 1 | (2, -1) | (2, -1) | (2, -1) | yes / yes | LATEST_COPY | 96102 |
| HOLD | K2 | 1001/1:(1, +1) | 1 | (1, +1) | (1, 0) | (1, +1) | no / no | NON_LATEST | 96103 |
| RETREAT | K3 | 1001/2:(0, 0) | 1 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96104 |

Predicted: **HOLD = RETREAT > ADVANCE**. Actual: **HOLD > RETREAT > ADVANCE**. `MAP_TIE`.

### Context 14 — W1 / O1 / mapping 1 / state 1 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | K1 | 1001/4:(2, -1) | 1 | (2, -1) | (2, -1) | (2, -1) | yes / yes | LATEST_COPY | 96112 |
| HOLD | K3 | 1001/1:(1, +1) | 1 | (1, +1) | (1, 0) | (1, +1) | no / no | NON_LATEST | 96113 |
| RETREAT | K2 | 1001/2:(0, 0) | 1 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96114 |

Predicted: **HOLD = RETREAT > ADVANCE**. Actual: **HOLD > RETREAT > ADVANCE**. `MAP_TIE`.

### Context 15 — W1 / O2 / mapping 1 / state 1 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | Q7 | 1001/4:(2, -1) | 1 | (2, -1) | (2, -1) | (2, -1) | yes / yes | LATEST_COPY | 96112 |
| HOLD | Z2 | 1001/1:(1, +1) | 1 | (1, +1) | (1, 0) | (1, +1) | no / no | NON_LATEST | 96113 |
| RETREAT | M4 | 1001/2:(0, 0) | 1 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96114 |

Predicted: **HOLD = RETREAT > ADVANCE**. Actual: **HOLD > RETREAT > ADVANCE**. `MAP_TIE`.

### Context 16 — W1 / O2 / mapping 2 / state 1 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | M4 | 1001/4:(2, -1) | 1 | (2, -1) | (2, -1) | (2, -1) | yes / yes | LATEST_COPY | 96122 |
| HOLD | Q7 | 1001/1:(1, +1) | 1 | (1, +1) | (1, 0) | (1, +1) | no / no | NON_LATEST | 96123 |
| RETREAT | Z2 | 1001/2:(0, 0) | 1 | (0, 0) | (1, 0) | (0, 0) | yes / no | LATEST_COPY | 96124 |

Predicted: **HOLD = RETREAT > ADVANCE**. Actual: **HOLD > RETREAT > ADVANCE**. `MAP_TIE`.

### Context 17 — W1 / O1 / mapping 2 / state 1 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | K2 | 1001/4:(2, -1) | 1 | (2, -1) | (2, -1) | (2, -1) | yes / yes | LATEST_COPY | 96122 |
| HOLD | K1 | 1001/1:(1, +1) | 1 | (1, +1) | (1, 0) | (1, +1) | no / no | NON_LATEST | 96123 |
| RETREAT | K3 | 1001/2:(0, 0) | 1 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96124 |

Predicted: **HOLD = RETREAT > ADVANCE**. Actual: **HOLD > RETREAT > ADVANCE**. `MAP_TIE`.

### Context 18 — W1 / O1 / mapping 3 / state 1 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | K3 | 1001/4:(2, -1) | 1 | (2, -1) | (0, -1) | (2, -1) | yes / no | LATEST_COPY | 96132 |
| HOLD | K1 | 1001/1:(1, +1) | 1 | (1, +1) | (1, 0) | (1, +1) | no / no | NON_LATEST | 96133 |
| RETREAT | K2 | 1001/2:(0, 0) | 1 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96134 |

Predicted: **HOLD = RETREAT > ADVANCE**. Actual: **HOLD > RETREAT > ADVANCE**. `MAP_TIE`.

### Context 19 — W1 / O2 / mapping 3 / state 1 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | Z2 | 1001/4:(2, -1) | 1 | (2, -1) | (2, -1) | (2, -1) | yes / yes | LATEST_COPY | 96132 |
| HOLD | Q7 | 1001/1:(1, +1) | 1 | (1, +1) | (1, 0) | (1, +1) | no / no | NON_LATEST | 96133 |
| RETREAT | M4 | 1001/2:(0, 0) | 1 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96134 |

Predicted: **HOLD = RETREAT > ADVANCE**. Actual: **HOLD > RETREAT > ADVANCE**. `MAP_TIE`.

### Context 20 — W1 / O2 / mapping 4 / state 1 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | M4 | 1001/4:(2, -1) | 1 | (2, -1) | (2, -1) | (2, -1) | yes / yes | LATEST_COPY | 96142 |
| HOLD | Z2 | 1001/1:(1, +1) | 1 | (1, +1) | (1, 0) | (1, +1) | no / no | NON_LATEST | 96143 |
| RETREAT | Q7 | 1001/2:(0, 0) | 1 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96144 |

Predicted: **HOLD = RETREAT > ADVANCE**. Actual: **HOLD > RETREAT > ADVANCE**. `MAP_TIE`.

### Context 21 — W1 / O1 / mapping 4 / state 1 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | K2 | 1001/4:(2, -1) | 1 | (2, -1) | (2, -1) | (2, -1) | yes / yes | LATEST_COPY | 96142 |
| HOLD | K3 | 1001/1:(1, +1) | 1 | (1, +1) | (1, 0) | (1, +1) | no / no | NON_LATEST | 96143 |
| RETREAT | K1 | 1001/2:(0, 0) | 1 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96144 |

Predicted: **HOLD = RETREAT > ADVANCE**. Actual: **HOLD > RETREAT > ADVANCE**. `MAP_TIE`.

### Context 22 — W1 / O1 / mapping 5 / state 1 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | K3 | 1001/4:(2, -1) | 1 | (2, -1) | (2, -1) | (2, -1) | yes / yes | LATEST_COPY | 96152 |
| HOLD | K2 | 1001/1:(1, +1) | 1 | (1, +1) | (1, 0) | (1, +1) | no / no | NON_LATEST | 96153 |
| RETREAT | K1 | 1001/2:(0, 0) | 1 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96154 |

Predicted: **HOLD = RETREAT > ADVANCE**. Actual: **HOLD > RETREAT > ADVANCE**. `MAP_TIE`.

### Context 23 — W1 / O2 / mapping 5 / state 1 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | Z2 | 1001/4:(2, -1) | 1 | (2, -1) | (2, -1) | (2, -1) | yes / yes | LATEST_COPY | 96152 |
| HOLD | M4 | 1001/1:(1, +1) | 1 | (1, +1) | (1, 0) | (1, +1) | no / no | NON_LATEST | 96153 |
| RETREAT | Q7 | 1001/2:(0, 0) | 1 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96154 |

Predicted: **HOLD = RETREAT > ADVANCE**. Actual: **HOLD > RETREAT > ADVANCE**. `MAP_TIE`.

### Context 24 — W3 / O1 / mapping 0 / state 3 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | K1 | 1001/4:(0, -1) | 1 | (0, -1) | (0, -1) | (0, -1) | yes / yes | LATEST_COPY | 96202 |
| HOLD | K2 | 1001/1:(3, 0) | 1 | (3, 0) | (3, 0) | (3, 0) | yes / yes | LATEST_COPY | 96203 |
| RETREAT | K3 | 1001/2:(2, +1) | 1 | (2, +1) | (2, +1) | (2, +1) | yes / yes | LATEST_COPY | 96204 |

Predicted: **RETREAT > HOLD > ADVANCE**. Actual: **RETREAT > HOLD > ADVANCE**. `MAP_TRUE_BEST_UNIQUE`.

### Context 25 — W3 / O2 / mapping 0 / state 3 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | Q7 | 1001/4:(0, -1) | 1 | (0, -1) | (0, -1) | (0, -1) | yes / yes | LATEST_COPY | 96202 |
| HOLD | M4 | 1001/1:(3, 0) | 1 | (3, 0) | (0, -1) | (3, 0) | no / no | NON_LATEST | 96203 |
| RETREAT | Z2 | 1001/2:(2, +1) | 1 | (2, +1) | (2, +1) | (2, +1) | yes / yes | LATEST_COPY | 96204 |

Predicted: **RETREAT > ADVANCE = HOLD**. Actual: **RETREAT > HOLD > ADVANCE**. `MAP_TRUE_BEST_UNIQUE`.

### Context 26 — W3 / O2 / mapping 1 / state 3 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | Q7 | 1001/4:(0, -1) | 1 | (0, -1) | (0, -1) | (0, -1) | yes / yes | LATEST_COPY | 96212 |
| HOLD | Z2 | 1001/1:(3, 0) | 1 | (3, 0) | (0, -1) | (3, 0) | no / no | NON_LATEST | 96213 |
| RETREAT | M4 | 1001/2:(2, +1) | 1 | (2, +1) | (2, +1) | (2, +1) | yes / yes | LATEST_COPY | 96214 |

Predicted: **RETREAT > ADVANCE = HOLD**. Actual: **RETREAT > HOLD > ADVANCE**. `MAP_TRUE_BEST_UNIQUE`.

### Context 27 — W3 / O1 / mapping 1 / state 3 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | K1 | 1001/4:(0, -1) | 1 | (0, -1) | (0, -1) | (0, -1) | yes / yes | LATEST_COPY | 96212 |
| HOLD | K3 | 1001/1:(3, 0) | 1 | (3, 0) | (3, 0) | (3, 0) | yes / yes | LATEST_COPY | 96213 |
| RETREAT | K2 | 1001/2:(2, +1) | 1 | (2, +1) | (1, -1) | (2, +1) | no / no | NON_LATEST | 96214 |

Predicted: **HOLD > ADVANCE = RETREAT**. Actual: **RETREAT > HOLD > ADVANCE**. `MAP_WRONG_UNIQUE`.

### Context 28 — W3 / O1 / mapping 2 / state 3 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | K2 | 1001/4:(0, -1) | 1 | (0, -1) | (0, -1) | (0, -1) | yes / yes | LATEST_COPY | 96222 |
| HOLD | K1 | 1001/1:(3, 0) | 1 | (3, 0) | (3, 0) | (3, 0) | yes / yes | LATEST_COPY | 96223 |
| RETREAT | K3 | 1001/2:(2, +1) | 1 | (2, +1) | (2, +1) | (2, +1) | yes / yes | LATEST_COPY | 96224 |

Predicted: **RETREAT > HOLD > ADVANCE**. Actual: **RETREAT > HOLD > ADVANCE**. `MAP_TRUE_BEST_UNIQUE`.

### Context 29 — W3 / O2 / mapping 2 / state 3 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | M4 | 1001/4:(0, -1) | 1 | (0, -1) | (0, -1) | (0, -1) | yes / yes | LATEST_COPY | 96222 |
| HOLD | Q7 | 1001/1:(3, 0) | 1 | (3, 0) | (3, 0) | (3, 0) | yes / yes | LATEST_COPY | 96223 |
| RETREAT | Z2 | 1001/2:(2, +1) | 1 | (2, +1) | (2, +1) | (2, +1) | yes / yes | LATEST_COPY | 96224 |

Predicted: **RETREAT > HOLD > ADVANCE**. Actual: **RETREAT > HOLD > ADVANCE**. `MAP_TRUE_BEST_UNIQUE`.

### Context 30 — W3 / O2 / mapping 3 / state 3 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | Z2 | 1001/4:(0, -1) | 1 | (0, -1) | (0, -1) | (0, -1) | yes / yes | LATEST_COPY | 96232 |
| HOLD | Q7 | 1001/1:(3, 0) | 1 | (3, 0) | (3, 0) | (3, 0) | yes / yes | LATEST_COPY | 96233 |
| RETREAT | M4 | 1001/2:(2, +1) | 1 | (2, +1) | (1, -1) | (2, +1) | no / no | NON_LATEST | 96234 |

Predicted: **HOLD > ADVANCE = RETREAT**. Actual: **RETREAT > HOLD > ADVANCE**. `MAP_WRONG_UNIQUE`.

### Context 31 — W3 / O1 / mapping 3 / state 3 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | K3 | 1001/4:(0, -1) | 1 | (0, -1) | (0, -1) | (0, -1) | yes / yes | LATEST_COPY | 96232 |
| HOLD | K1 | 1001/1:(3, 0) | 1 | (3, 0) | (0, -1) | (3, 0) | no / no | NON_LATEST | 96233 |
| RETREAT | K2 | 1001/2:(2, +1) | 1 | (2, +1) | (2, +1) | (2, +1) | yes / yes | LATEST_COPY | 96234 |

Predicted: **RETREAT > ADVANCE = HOLD**. Actual: **RETREAT > HOLD > ADVANCE**. `MAP_TRUE_BEST_UNIQUE`.

### Context 32 — W3 / O1 / mapping 4 / state 3 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | K2 | 1001/4:(0, -1) | 1 | (0, -1) | (0, -1) | (0, -1) | yes / yes | LATEST_COPY | 96242 |
| HOLD | K3 | 1001/1:(3, 0) | 1 | (3, 0) | (3, 0) | (3, 0) | yes / yes | LATEST_COPY | 96243 |
| RETREAT | K1 | 1001/2:(2, +1) | 1 | (2, +1) | (0, -1) | (2, +1) | no / no | NON_LATEST | 96244 |

Predicted: **HOLD > ADVANCE = RETREAT**. Actual: **RETREAT > HOLD > ADVANCE**. `MAP_WRONG_UNIQUE`.

### Context 33 — W3 / O2 / mapping 4 / state 3 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | M4 | 1001/4:(0, -1) | 1 | (0, -1) | (0, -1) | (0, -1) | yes / yes | LATEST_COPY | 96242 |
| HOLD | Z2 | 1001/1:(3, 0) | 1 | (3, 0) | (3, 0) | (3, 0) | yes / yes | LATEST_COPY | 96243 |
| RETREAT | Q7 | 1001/2:(2, +1) | 1 | (2, +1) | (0, -1) | (2, +1) | no / no | NON_LATEST | 96244 |

Predicted: **HOLD > ADVANCE = RETREAT**. Actual: **RETREAT > HOLD > ADVANCE**. `MAP_WRONG_UNIQUE`.

### Context 34 — W3 / O2 / mapping 5 / state 3 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | Z2 | 1001/4:(0, -1) | 1 | (0, -1) | (0, -1) | (0, -1) | yes / yes | LATEST_COPY | 96252 |
| HOLD | M4 | 1001/1:(3, 0) | 1 | (3, 0) | (0, -1) | (3, 0) | no / no | NON_LATEST | 96253 |
| RETREAT | Q7 | 1001/2:(2, +1) | 1 | (2, +1) | (2, +1) | (2, +1) | yes / yes | LATEST_COPY | 96254 |

Predicted: **RETREAT > ADVANCE = HOLD**. Actual: **RETREAT > HOLD > ADVANCE**. `MAP_TRUE_BEST_UNIQUE`.

### Context 35 — W3 / O1 / mapping 5 / state 3 / epoch 1001

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | K3 | 1001/4:(0, -1) | 1 | (0, -1) | (0, -1) | (0, -1) | yes / yes | LATEST_COPY | 96252 |
| HOLD | K2 | 1001/1:(3, 0) | 1 | (3, 0) | (3, 0) | (3, 0) | yes / yes | LATEST_COPY | 96253 |
| RETREAT | K1 | 1001/2:(2, +1) | 1 | (2, +1) | (2, +1) | (2, +1) | yes / yes | LATEST_COPY | 96254 |

Predicted: **RETREAT > HOLD > ADVANCE**. Actual: **RETREAT > HOLD > ADVANCE**. `MAP_TRUE_BEST_UNIQUE`.

### Context 36 — D1 / O2 / mapping 0 / state 1 / epoch 1002

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | Q7 | 1001/4:(2, -1) | 1 | (2, -1) | (2, -1) | (2, -1) | yes / yes | LATEST_COPY | 96302 |
| HOLD | M4 | 1001/1:(1, +1); 1002/1:(1, -1); 1002/2:(1, -1) | 3 | (1, -1) | (1, -1) | (1, -1) | yes / yes | LATEST_COPY | 96303 |
| RETREAT | Z2 | 1001/2:(0, 0); 1001/6:(0, 0) | 2 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96304 |

Predicted: **RETREAT > ADVANCE = HOLD**. Actual: **RETREAT > ADVANCE = HOLD**. `MAP_TRUE_BEST_UNIQUE`.

### Context 37 — D1 / O1 / mapping 0 / state 1 / epoch 1002

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | K1 | 1001/4:(2, -1) | 1 | (2, -1) | (2, -1) | (2, -1) | yes / yes | LATEST_COPY | 96302 |
| HOLD | K2 | 1001/1:(1, +1); 1002/1:(1, -1); 1002/2:(1, -1) | 3 | (1, -1) | (1, -1) | (1, -1) | yes / yes | LATEST_COPY | 96303 |
| RETREAT | K3 | 1001/2:(0, 0); 1001/6:(0, 0) | 2 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96304 |

Predicted: **RETREAT > ADVANCE = HOLD**. Actual: **RETREAT > ADVANCE = HOLD**. `MAP_TRUE_BEST_UNIQUE`.

### Context 38 — D1 / O1 / mapping 1 / state 1 / epoch 1002

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | K1 | 1001/4:(2, -1) | 1 | (2, -1) | (2, -1) | (2, -1) | yes / yes | LATEST_COPY | 96312 |
| HOLD | K3 | 1001/1:(1, +1); 1002/1:(1, -1); 1002/2:(1, -1) | 3 | (1, -1) | (1, -1) | (1, -1) | yes / yes | LATEST_COPY | 96313 |
| RETREAT | K2 | 1001/2:(0, 0); 1001/6:(0, 0) | 2 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96314 |

Predicted: **RETREAT > ADVANCE = HOLD**. Actual: **RETREAT > ADVANCE = HOLD**. `MAP_TRUE_BEST_UNIQUE`.

### Context 39 — D1 / O2 / mapping 1 / state 1 / epoch 1002

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | Q7 | 1001/4:(2, -1) | 1 | (2, -1) | (2, -1) | (2, -1) | yes / yes | LATEST_COPY | 96312 |
| HOLD | Z2 | 1001/1:(1, +1); 1002/1:(1, -1); 1002/2:(1, -1) | 3 | (1, -1) | (1, -1) | (1, -1) | yes / yes | LATEST_COPY | 96313 |
| RETREAT | M4 | 1001/2:(0, 0); 1001/6:(0, 0) | 2 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96314 |

Predicted: **RETREAT > ADVANCE = HOLD**. Actual: **RETREAT > ADVANCE = HOLD**. `MAP_TRUE_BEST_UNIQUE`.

### Context 40 — D1 / O2 / mapping 2 / state 1 / epoch 1002

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | M4 | 1001/4:(2, -1) | 1 | (2, -1) | (2, -1) | (2, -1) | yes / yes | LATEST_COPY | 96322 |
| HOLD | Q7 | 1001/1:(1, +1); 1002/1:(1, -1); 1002/2:(1, -1) | 3 | (1, -1) | (1, -1) | (1, -1) | yes / yes | LATEST_COPY | 96323 |
| RETREAT | Z2 | 1001/2:(0, 0); 1001/6:(0, 0) | 2 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96324 |

Predicted: **RETREAT > ADVANCE = HOLD**. Actual: **RETREAT > ADVANCE = HOLD**. `MAP_TRUE_BEST_UNIQUE`.

### Context 41 — D1 / O1 / mapping 2 / state 1 / epoch 1002

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | K2 | 1001/4:(2, -1) | 1 | (2, -1) | (2, -1) | (2, -1) | yes / yes | LATEST_COPY | 96322 |
| HOLD | K1 | 1001/1:(1, +1); 1002/1:(1, -1); 1002/2:(1, -1) | 3 | (1, -1) | (1, -1) | (1, -1) | yes / yes | LATEST_COPY | 96323 |
| RETREAT | K3 | 1001/2:(0, 0); 1001/6:(0, 0) | 2 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96324 |

Predicted: **RETREAT > ADVANCE = HOLD**. Actual: **RETREAT > ADVANCE = HOLD**. `MAP_TRUE_BEST_UNIQUE`.

### Context 42 — D1 / O1 / mapping 3 / state 1 / epoch 1002

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | K3 | 1001/4:(2, -1) | 1 | (2, -1) | (2, -1) | (2, -1) | yes / yes | LATEST_COPY | 96332 |
| HOLD | K1 | 1001/1:(1, +1); 1002/1:(1, -1); 1002/2:(1, -1) | 3 | (1, -1) | (1, -1) | (1, -1) | yes / yes | LATEST_COPY | 96333 |
| RETREAT | K2 | 1001/2:(0, 0); 1001/6:(0, 0) | 2 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96334 |

Predicted: **RETREAT > ADVANCE = HOLD**. Actual: **RETREAT > ADVANCE = HOLD**. `MAP_TRUE_BEST_UNIQUE`.

### Context 43 — D1 / O2 / mapping 3 / state 1 / epoch 1002

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | Z2 | 1001/4:(2, -1) | 1 | (2, -1) | (2, -1) | (2, -1) | yes / yes | LATEST_COPY | 96332 |
| HOLD | Q7 | 1001/1:(1, +1); 1002/1:(1, -1); 1002/2:(1, -1) | 3 | (1, -1) | (1, -1) | (1, -1) | yes / yes | LATEST_COPY | 96333 |
| RETREAT | M4 | 1001/2:(0, 0); 1001/6:(0, 0) | 2 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96334 |

Predicted: **RETREAT > ADVANCE = HOLD**. Actual: **RETREAT > ADVANCE = HOLD**. `MAP_TRUE_BEST_UNIQUE`.

### Context 44 — D1 / O2 / mapping 4 / state 1 / epoch 1002

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | M4 | 1001/4:(2, -1) | 1 | (2, -1) | (2, -1) | (2, -1) | yes / yes | LATEST_COPY | 96342 |
| HOLD | Z2 | 1001/1:(1, +1); 1002/1:(1, -1); 1002/2:(1, -1) | 3 | (1, -1) | (1, -1) | (1, -1) | yes / yes | LATEST_COPY | 96343 |
| RETREAT | Q7 | 1001/2:(0, 0); 1001/6:(0, 0) | 2 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96344 |

Predicted: **RETREAT > ADVANCE = HOLD**. Actual: **RETREAT > ADVANCE = HOLD**. `MAP_TRUE_BEST_UNIQUE`.

### Context 45 — D1 / O1 / mapping 4 / state 1 / epoch 1002

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | K2 | 1001/4:(2, -1) | 1 | (2, -1) | (3, -1) | (2, -1) | yes / no | LATEST_COPY | 96342 |
| HOLD | K3 | 1001/1:(1, +1); 1002/1:(1, -1); 1002/2:(1, -1) | 3 | (1, -1) | (1, -1) | (1, -1) | yes / yes | LATEST_COPY | 96343 |
| RETREAT | K1 | 1001/2:(0, 0); 1001/6:(0, 0) | 2 | (0, 0) | (0, +1) | (0, 0) | no / no | NON_LATEST | 96344 |

Predicted: **RETREAT > ADVANCE = HOLD**. Actual: **RETREAT > ADVANCE = HOLD**. `MAP_TRUE_BEST_UNIQUE`.

### Context 46 — D1 / O1 / mapping 5 / state 1 / epoch 1002

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | K3 | 1001/4:(2, -1) | 1 | (2, -1) | (2, -1) | (2, -1) | yes / yes | LATEST_COPY | 96352 |
| HOLD | K2 | 1001/1:(1, +1); 1002/1:(1, -1); 1002/2:(1, -1) | 3 | (1, -1) | (1, -1) | (1, -1) | yes / yes | LATEST_COPY | 96353 |
| RETREAT | K1 | 1001/2:(0, 0); 1001/6:(0, 0) | 2 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96354 |

Predicted: **RETREAT > ADVANCE = HOLD**. Actual: **RETREAT > ADVANCE = HOLD**. `MAP_TRUE_BEST_UNIQUE`.

### Context 47 — D1 / O2 / mapping 5 / state 1 / epoch 1002

| Action | Alias | Full authenticated history | Depth | Latest | Map prediction | Actual retained outcome | C / E | Latest relation | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADVANCE | Z2 | 1001/4:(2, -1) | 1 | (2, -1) | (0, -1) | (2, -1) | yes / no | LATEST_COPY | 96352 |
| HOLD | M4 | 1001/1:(1, +1); 1002/1:(1, -1); 1002/2:(1, -1) | 3 | (1, -1) | (1, -1) | (1, -1) | yes / yes | LATEST_COPY | 96353 |
| RETREAT | Q7 | 1001/2:(0, 0); 1001/6:(0, 0) | 2 | (0, 0) | (0, 0) | (0, 0) | yes / yes | LATEST_COPY | 96354 |

Predicted: **RETREAT > ADVANCE = HOLD**. Actual: **RETREAT > ADVANCE = HOLD**. `MAP_TRUE_BEST_UNIQUE`.
