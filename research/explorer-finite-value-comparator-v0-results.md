# Explorer finite-value comparator v0 results

## Decisions

**ZERO-OVER-NEGATIVE COMPARATOR NOT ESTABLISHED**. Separately, **NEXT_STATE IRRELEVANCE NOT ESTABLISHED**.

| Family | R3 valid /24 | N correct /12 | V correct /12 | Same /12 | N ADVANCE /4 | N HOLD /4 | N RETREAT /4 | Decision |
|---|---|---|---|---|---|---|---|---|
| O1 | 24 | 12 | 8 | 8 | 4 | 4 | 4 | ZERO-OVER-NEGATIVE COMPARATOR NOT ESTABLISHED |
| O2 | 24 | 4 | 7 | 8 | 2 | 1 | 1 | ZERO-OVER-NEGATIVE COMPARATOR NOT ESTABLISHED |

| Family | Valid /72 | Same /36 | Different /36 | Not comparable | N correct /36 | V correct /36 | Absolute gap | Decision |
|---|---|---|---|---|---|---|---|---|
| O1 | 72 | 32 | 4 | 0 | 36 | 32 | 4 | NEXT_STATE IRRELEVANCE NOT ESTABLISHED |
| O2 | 72 | 28 | 8 | 0 | 27 | 28 | 1 | NEXT_STATE IRRELEVANCE NOT ESTABLISHED |

## Parent and prospective freeze

Parent `2679cff20b28079b4358fe463f68e5822e5cc205`; preregistration `5af3764110d76f771146b51e7c5329baba67bd57` was committed before the first live request. [Frozen preregistration](explorer-finite-value-comparator-v0-preregistration.md) and 144 exact request hashes retain the complete schedule and decision rules. PIPELINE NOT FULLY ESTABLISHED, all three earlier decomposition stage negatives, the temporal Map negative, interface A, both earlier Explorer negatives and stale-Memory Map REPLICATED remain unchanged.

## Exact question and scope

Can Explorer select the unique maximum among finite values, especially 0>-1, and do irrelevant next_state values change its choice? These are detached experimental forecasts. There is no world execution, Map call, Memory construction/change, receipt, learned action ban or authorization. A numeric maximum is used only to evaluate responses; no mechanical production Explorer is implemented.

## Protocol and balancing

R1={+1,0,-1}; R2={+1,-1,-1}; primary R3={0,-1,-1}. The unique-best underlying action and opaque alias each appear four times per relation/family/condition. R1 uses all six full assignments twice. Each family uses all six mappings twice, mapping j mod 6. N has next_state 1 for every action. V has distinct 0,1,2, all six assignments twice and best-action next_state balanced four times each. Consequences, row order, aliases and current state 1 stay identical within each pair. See the preregistered assignment list; no output-dependent fixture or schedule changes.

## Prompt, parser, seeds and model

Exact established instruction: “Choose the allowed action whose current Map prediction has the highest predicted consequence. Reply with exactly one allowed action and no explanation.” View contains only state and three actions with opaque action and map_prediction {next_state,consequence}. Historical strict opaque parser unchanged. Seed 97001+100*relation_index+j is identical within each N/V pair and matched across O1/O2. Pinned dolphin-mixtral:latest, Ollama 0.1.16, GGUF 47B Q4_0, all five model blobs fully verified. Historical sampler .2 temperature, .9 top_p, 40 top_k, 2048 context, 1.1 repeat penalty, 16 output tokens. Stateless requests; no history, confidence, mean, evaluator hint or tuning.

## Actual calls and validity

Exactly **144 real Explorer calls** completed; **144/144 valid**. Zero retries, replacements, extensions, Map calls, Recovery model calls, world executions or Memory changes. All scheduled calls were issued once. The owned model server was stopped after the campaign. All model responses, including errors, are retained privately.

## All relation and condition results

| Family | Relation | Condition | Calls | Valid | Correct | Underlying choice counts | Alias choice counts |
|---|---|---|---|---|---|---|---|
| O1 | R1 | N | 12 | 12 | 12 | {"ADVANCE": 4, "HOLD": 4, "RETREAT": 4} | {"K1": 4, "K2": 4, "K3": 4} |
| O1 | R1 | V | 12 | 12 | 12 | {"ADVANCE": 4, "HOLD": 4, "RETREAT": 4} | {"K1": 4, "K2": 4, "K3": 4} |
| O1 | R2 | N | 12 | 12 | 12 | {"ADVANCE": 4, "HOLD": 4, "RETREAT": 4} | {"K1": 4, "K2": 4, "K3": 4} |
| O1 | R2 | V | 12 | 12 | 12 | {"ADVANCE": 4, "HOLD": 4, "RETREAT": 4} | {"K1": 4, "K2": 4, "K3": 4} |
| O1 | R3 | N | 12 | 12 | 12 | {"ADVANCE": 4, "HOLD": 4, "RETREAT": 4} | {"K1": 4, "K2": 4, "K3": 4} |
| O1 | R3 | V | 12 | 12 | 8 | {"ADVANCE": 3, "HOLD": 5, "RETREAT": 4} | {"K1": 7, "K2": 5} |
| O2 | R1 | N | 12 | 12 | 11 | {"ADVANCE": 3, "HOLD": 5, "RETREAT": 4} | {"M4": 4, "Q7": 5, "Z2": 3} |
| O2 | R1 | V | 12 | 12 | 9 | {"ADVANCE": 3, "HOLD": 4, "RETREAT": 5} | {"M4": 4, "Q7": 7, "Z2": 1} |
| O2 | R2 | N | 12 | 12 | 12 | {"ADVANCE": 4, "HOLD": 4, "RETREAT": 4} | {"M4": 4, "Q7": 4, "Z2": 4} |
| O2 | R2 | V | 12 | 12 | 12 | {"ADVANCE": 4, "HOLD": 4, "RETREAT": 4} | {"M4": 4, "Q7": 4, "Z2": 4} |
| O2 | R3 | N | 12 | 12 | 4 | {"ADVANCE": 4, "HOLD": 4, "RETREAT": 4} | {"Q7": 12} |
| O2 | R3 | V | 12 | 12 | 7 | {"ADVANCE": 5, "HOLD": 3, "RETREAT": 4} | {"M4": 3, "Q7": 8, "Z2": 1} |

R1/R2 are descriptive controls only: no pass thresholds were supplied or added. They do not rescue a failed R3 gate. Choice counts distinguish validity from correct finite comparison.

## Frozen gates

### O1

| Decision | Frozen criterion | Passed |
|---|---|---|
| primary | N_best_at_least_10 | yes |
| primary | V_best_at_least_10 | no |
| primary | all_24_R3_complete | yes |
| primary | every_N_target_at_least_3_of_4 | yes |
| primary | exact_replay | yes |
| primary | same_at_least_10 | no |
| primary | valid_at_least_23 | yes |
| next_state | R3_same_at_least_10 | no |
| next_state | accuracy_difference_at_most_3 | no |
| next_state | all_72_complete | yes |
| next_state | exact_replay | yes |
| next_state | same_at_least_32 | yes |
| next_state | valid_at_least_70 | yes |

### O2

| Decision | Frozen criterion | Passed |
|---|---|---|
| primary | N_best_at_least_10 | no |
| primary | V_best_at_least_10 | no |
| primary | all_24_R3_complete | yes |
| primary | every_N_target_at_least_3_of_4 | no |
| primary | exact_replay | yes |
| primary | same_at_least_10 | no |
| primary | valid_at_least_23 | yes |
| next_state | R3_same_at_least_10 | no |
| next_state | accuracy_difference_at_most_3 | yes |
| next_state | all_72_complete | yes |
| next_state | exact_replay | yes |
| next_state | same_at_least_32 | no |
| next_state | valid_at_least_70 | yes |

Overall replication requires each full rule to pass independently in both families. R3 requires 24 complete, valid>=23, N>=10, V>=10, same>=10, every N target>=3/4 and replay. Invariance independently requires 72 complete, valid>=70, same>=32, absolute N/V accuracy gap<=3, R3 same>=10 and replay.

## All 72 same-seed pairs

| Family | Relation | j | Mapping | Seed | Target alias / action | N choice | V choice | Comparison | N correct | V correct |
|---|---|---|---|---|---|---|---|---|---|---|
| O1 | R1 | 0 | 0 | 97001 | K1 / ADVANCE | K1 / ADVANCE | K1 / ADVANCE | same | yes | yes |
| O1 | R1 | 1 | 1 | 97002 | K2 / RETREAT | K2 / RETREAT | K2 / RETREAT | same | yes | yes |
| O1 | R1 | 2 | 2 | 97003 | K1 / HOLD | K1 / HOLD | K1 / HOLD | same | yes | yes |
| O1 | R1 | 3 | 3 | 97004 | K3 / ADVANCE | K3 / ADVANCE | K3 / ADVANCE | same | yes | yes |
| O1 | R1 | 4 | 4 | 97005 | K1 / RETREAT | K1 / RETREAT | K1 / RETREAT | same | yes | yes |
| O1 | R1 | 5 | 5 | 97006 | K2 / HOLD | K2 / HOLD | K2 / HOLD | same | yes | yes |
| O1 | R1 | 6 | 0 | 97007 | K2 / HOLD | K2 / HOLD | K2 / HOLD | same | yes | yes |
| O1 | R1 | 7 | 1 | 97008 | K1 / ADVANCE | K1 / ADVANCE | K1 / ADVANCE | same | yes | yes |
| O1 | R1 | 8 | 2 | 97009 | K3 / RETREAT | K3 / RETREAT | K3 / RETREAT | same | yes | yes |
| O1 | R1 | 9 | 3 | 97010 | K2 / RETREAT | K2 / RETREAT | K2 / RETREAT | same | yes | yes |
| O1 | R1 | 10 | 4 | 97011 | K3 / HOLD | K3 / HOLD | K3 / HOLD | same | yes | yes |
| O1 | R1 | 11 | 5 | 97012 | K3 / ADVANCE | K3 / ADVANCE | K3 / ADVANCE | same | yes | yes |
| O1 | R2 | 0 | 0 | 97101 | K1 / ADVANCE | K1 / ADVANCE | K1 / ADVANCE | same | yes | yes |
| O1 | R2 | 1 | 1 | 97102 | K2 / RETREAT | K2 / RETREAT | K2 / RETREAT | same | yes | yes |
| O1 | R2 | 2 | 2 | 97103 | K1 / HOLD | K1 / HOLD | K1 / HOLD | same | yes | yes |
| O1 | R2 | 3 | 3 | 97104 | K3 / ADVANCE | K3 / ADVANCE | K3 / ADVANCE | same | yes | yes |
| O1 | R2 | 4 | 4 | 97105 | K1 / RETREAT | K1 / RETREAT | K1 / RETREAT | same | yes | yes |
| O1 | R2 | 5 | 5 | 97106 | K2 / HOLD | K2 / HOLD | K2 / HOLD | same | yes | yes |
| O1 | R2 | 6 | 0 | 97107 | K2 / HOLD | K2 / HOLD | K2 / HOLD | same | yes | yes |
| O1 | R2 | 7 | 1 | 97108 | K1 / ADVANCE | K1 / ADVANCE | K1 / ADVANCE | same | yes | yes |
| O1 | R2 | 8 | 2 | 97109 | K3 / RETREAT | K3 / RETREAT | K3 / RETREAT | same | yes | yes |
| O1 | R2 | 9 | 3 | 97110 | K2 / RETREAT | K2 / RETREAT | K2 / RETREAT | same | yes | yes |
| O1 | R2 | 10 | 4 | 97111 | K3 / HOLD | K3 / HOLD | K3 / HOLD | same | yes | yes |
| O1 | R2 | 11 | 5 | 97112 | K3 / ADVANCE | K3 / ADVANCE | K3 / ADVANCE | same | yes | yes |
| O1 | R3 | 0 | 0 | 97201 | K1 / ADVANCE | K1 / ADVANCE | K1 / ADVANCE | same | yes | yes |
| O1 | R3 | 1 | 1 | 97202 | K2 / RETREAT | K2 / RETREAT | K2 / RETREAT | same | yes | yes |
| O1 | R3 | 2 | 2 | 97203 | K1 / HOLD | K1 / HOLD | K1 / HOLD | same | yes | yes |
| O1 | R3 | 3 | 3 | 97204 | K3 / ADVANCE | K3 / ADVANCE | K1 / HOLD | different | yes | no |
| O1 | R3 | 4 | 4 | 97205 | K1 / RETREAT | K1 / RETREAT | K1 / RETREAT | same | yes | yes |
| O1 | R3 | 5 | 5 | 97206 | K2 / HOLD | K2 / HOLD | K2 / HOLD | same | yes | yes |
| O1 | R3 | 6 | 0 | 97207 | K2 / HOLD | K2 / HOLD | K2 / HOLD | same | yes | yes |
| O1 | R3 | 7 | 1 | 97208 | K1 / ADVANCE | K1 / ADVANCE | K1 / ADVANCE | same | yes | yes |
| O1 | R3 | 8 | 2 | 97209 | K3 / RETREAT | K3 / RETREAT | K1 / HOLD | different | yes | no |
| O1 | R3 | 9 | 3 | 97210 | K2 / RETREAT | K2 / RETREAT | K2 / RETREAT | same | yes | yes |
| O1 | R3 | 10 | 4 | 97211 | K3 / HOLD | K3 / HOLD | K2 / ADVANCE | different | yes | no |
| O1 | R3 | 11 | 5 | 97212 | K3 / ADVANCE | K3 / ADVANCE | K1 / RETREAT | different | yes | no |
| O2 | R1 | 0 | 0 | 97001 | Q7 / ADVANCE | Q7 / ADVANCE | Q7 / ADVANCE | same | yes | yes |
| O2 | R1 | 1 | 1 | 97002 | M4 / RETREAT | M4 / RETREAT | M4 / RETREAT | same | yes | yes |
| O2 | R1 | 2 | 2 | 97003 | Q7 / HOLD | Q7 / HOLD | Q7 / HOLD | same | yes | yes |
| O2 | R1 | 3 | 3 | 97004 | Z2 / ADVANCE | Q7 / HOLD | Z2 / ADVANCE | different | no | yes |
| O2 | R1 | 4 | 4 | 97005 | Q7 / RETREAT | Q7 / RETREAT | Q7 / RETREAT | same | yes | yes |
| O2 | R1 | 5 | 5 | 97006 | M4 / HOLD | M4 / HOLD | M4 / HOLD | same | yes | yes |
| O2 | R1 | 6 | 0 | 97007 | M4 / HOLD | M4 / HOLD | M4 / HOLD | same | yes | yes |
| O2 | R1 | 7 | 1 | 97008 | Q7 / ADVANCE | Q7 / ADVANCE | Q7 / ADVANCE | same | yes | yes |
| O2 | R1 | 8 | 2 | 97009 | Z2 / RETREAT | Z2 / RETREAT | Q7 / HOLD | different | yes | no |
| O2 | R1 | 9 | 3 | 97010 | M4 / RETREAT | M4 / RETREAT | M4 / RETREAT | same | yes | yes |
| O2 | R1 | 10 | 4 | 97011 | Z2 / HOLD | Z2 / HOLD | Q7 / RETREAT | different | yes | no |
| O2 | R1 | 11 | 5 | 97012 | Z2 / ADVANCE | Z2 / ADVANCE | Q7 / RETREAT | different | yes | no |
| O2 | R2 | 0 | 0 | 97101 | Q7 / ADVANCE | Q7 / ADVANCE | Q7 / ADVANCE | same | yes | yes |
| O2 | R2 | 1 | 1 | 97102 | M4 / RETREAT | M4 / RETREAT | M4 / RETREAT | same | yes | yes |
| O2 | R2 | 2 | 2 | 97103 | Q7 / HOLD | Q7 / HOLD | Q7 / HOLD | same | yes | yes |
| O2 | R2 | 3 | 3 | 97104 | Z2 / ADVANCE | Z2 / ADVANCE | Z2 / ADVANCE | same | yes | yes |
| O2 | R2 | 4 | 4 | 97105 | Q7 / RETREAT | Q7 / RETREAT | Q7 / RETREAT | same | yes | yes |
| O2 | R2 | 5 | 5 | 97106 | M4 / HOLD | M4 / HOLD | M4 / HOLD | same | yes | yes |
| O2 | R2 | 6 | 0 | 97107 | M4 / HOLD | M4 / HOLD | M4 / HOLD | same | yes | yes |
| O2 | R2 | 7 | 1 | 97108 | Q7 / ADVANCE | Q7 / ADVANCE | Q7 / ADVANCE | same | yes | yes |
| O2 | R2 | 8 | 2 | 97109 | Z2 / RETREAT | Z2 / RETREAT | Z2 / RETREAT | same | yes | yes |
| O2 | R2 | 9 | 3 | 97110 | M4 / RETREAT | M4 / RETREAT | M4 / RETREAT | same | yes | yes |
| O2 | R2 | 10 | 4 | 97111 | Z2 / HOLD | Z2 / HOLD | Z2 / HOLD | same | yes | yes |
| O2 | R2 | 11 | 5 | 97112 | Z2 / ADVANCE | Z2 / ADVANCE | Z2 / ADVANCE | same | yes | yes |
| O2 | R3 | 0 | 0 | 97201 | Q7 / ADVANCE | Q7 / ADVANCE | Q7 / ADVANCE | same | yes | yes |
| O2 | R3 | 1 | 1 | 97202 | M4 / RETREAT | Q7 / ADVANCE | Q7 / ADVANCE | same | no | no |
| O2 | R3 | 2 | 2 | 97203 | Q7 / HOLD | Q7 / HOLD | Q7 / HOLD | same | yes | yes |
| O2 | R3 | 3 | 3 | 97204 | Z2 / ADVANCE | Q7 / HOLD | Z2 / ADVANCE | different | no | yes |
| O2 | R3 | 4 | 4 | 97205 | Q7 / RETREAT | Q7 / RETREAT | Q7 / RETREAT | same | yes | yes |
| O2 | R3 | 5 | 5 | 97206 | M4 / HOLD | Q7 / RETREAT | Q7 / RETREAT | same | no | no |
| O2 | R3 | 6 | 0 | 97207 | M4 / HOLD | Q7 / ADVANCE | M4 / HOLD | different | no | yes |
| O2 | R3 | 7 | 1 | 97208 | Q7 / ADVANCE | Q7 / ADVANCE | Q7 / ADVANCE | same | yes | yes |
| O2 | R3 | 8 | 2 | 97209 | Z2 / RETREAT | Q7 / HOLD | Q7 / HOLD | same | no | no |
| O2 | R3 | 9 | 3 | 97210 | M4 / RETREAT | Q7 / HOLD | M4 / RETREAT | different | no | yes |
| O2 | R3 | 10 | 4 | 97211 | Z2 / HOLD | Q7 / RETREAT | M4 / ADVANCE | different | no | no |
| O2 | R3 | 11 | 5 | 97212 | Z2 / ADVANCE | Q7 / RETREAT | Q7 / RETREAT | same | no | no |

Same/different requires two valid choices. Invalid pairs are not comparable, never credited as same. Mapping dictionaries and all144 individual scores appear in compact results.

## Mapping, target and alias diagnostics

| Family | Relation | Group | Value | Condition | Calls | Valid | Correct | Selected alias counts |
|---|---|---|---|---|---|---|---|---|
| O1 | R1 | mapping | 0 | N | 2 | 2 | 2 | {"K1": 1, "K2": 1} |
| O1 | R1 | mapping | 0 | V | 2 | 2 | 2 | {"K1": 1, "K2": 1} |
| O1 | R1 | mapping | 1 | N | 2 | 2 | 2 | {"K1": 1, "K2": 1} |
| O1 | R1 | mapping | 1 | V | 2 | 2 | 2 | {"K1": 1, "K2": 1} |
| O1 | R1 | mapping | 2 | N | 2 | 2 | 2 | {"K1": 1, "K3": 1} |
| O1 | R1 | mapping | 2 | V | 2 | 2 | 2 | {"K1": 1, "K3": 1} |
| O1 | R1 | mapping | 3 | N | 2 | 2 | 2 | {"K2": 1, "K3": 1} |
| O1 | R1 | mapping | 3 | V | 2 | 2 | 2 | {"K2": 1, "K3": 1} |
| O1 | R1 | mapping | 4 | N | 2 | 2 | 2 | {"K1": 1, "K3": 1} |
| O1 | R1 | mapping | 4 | V | 2 | 2 | 2 | {"K1": 1, "K3": 1} |
| O1 | R1 | mapping | 5 | N | 2 | 2 | 2 | {"K2": 1, "K3": 1} |
| O1 | R1 | mapping | 5 | V | 2 | 2 | 2 | {"K2": 1, "K3": 1} |
| O1 | R2 | mapping | 0 | N | 2 | 2 | 2 | {"K1": 1, "K2": 1} |
| O1 | R2 | mapping | 0 | V | 2 | 2 | 2 | {"K1": 1, "K2": 1} |
| O1 | R2 | mapping | 1 | N | 2 | 2 | 2 | {"K1": 1, "K2": 1} |
| O1 | R2 | mapping | 1 | V | 2 | 2 | 2 | {"K1": 1, "K2": 1} |
| O1 | R2 | mapping | 2 | N | 2 | 2 | 2 | {"K1": 1, "K3": 1} |
| O1 | R2 | mapping | 2 | V | 2 | 2 | 2 | {"K1": 1, "K3": 1} |
| O1 | R2 | mapping | 3 | N | 2 | 2 | 2 | {"K2": 1, "K3": 1} |
| O1 | R2 | mapping | 3 | V | 2 | 2 | 2 | {"K2": 1, "K3": 1} |
| O1 | R2 | mapping | 4 | N | 2 | 2 | 2 | {"K1": 1, "K3": 1} |
| O1 | R2 | mapping | 4 | V | 2 | 2 | 2 | {"K1": 1, "K3": 1} |
| O1 | R2 | mapping | 5 | N | 2 | 2 | 2 | {"K2": 1, "K3": 1} |
| O1 | R2 | mapping | 5 | V | 2 | 2 | 2 | {"K2": 1, "K3": 1} |
| O1 | R3 | mapping | 0 | N | 2 | 2 | 2 | {"K1": 1, "K2": 1} |
| O1 | R3 | mapping | 0 | V | 2 | 2 | 2 | {"K1": 1, "K2": 1} |
| O1 | R3 | mapping | 1 | N | 2 | 2 | 2 | {"K1": 1, "K2": 1} |
| O1 | R3 | mapping | 1 | V | 2 | 2 | 2 | {"K1": 1, "K2": 1} |
| O1 | R3 | mapping | 2 | N | 2 | 2 | 2 | {"K1": 1, "K3": 1} |
| O1 | R3 | mapping | 2 | V | 2 | 2 | 1 | {"K1": 2} |
| O1 | R3 | mapping | 3 | N | 2 | 2 | 2 | {"K2": 1, "K3": 1} |
| O1 | R3 | mapping | 3 | V | 2 | 2 | 1 | {"K1": 1, "K2": 1} |
| O1 | R3 | mapping | 4 | N | 2 | 2 | 2 | {"K1": 1, "K3": 1} |
| O1 | R3 | mapping | 4 | V | 2 | 2 | 1 | {"K1": 1, "K2": 1} |
| O1 | R3 | mapping | 5 | N | 2 | 2 | 2 | {"K2": 1, "K3": 1} |
| O1 | R3 | mapping | 5 | V | 2 | 2 | 1 | {"K1": 1, "K2": 1} |
| O1 | R1 | underlying target | ADVANCE | N | 4 | 4 | 4 | {"K1": 2, "K3": 2} |
| O1 | R1 | underlying target | ADVANCE | V | 4 | 4 | 4 | {"K1": 2, "K3": 2} |
| O1 | R1 | underlying target | HOLD | N | 4 | 4 | 4 | {"K1": 1, "K2": 2, "K3": 1} |
| O1 | R1 | underlying target | HOLD | V | 4 | 4 | 4 | {"K1": 1, "K2": 2, "K3": 1} |
| O1 | R1 | underlying target | RETREAT | N | 4 | 4 | 4 | {"K1": 1, "K2": 2, "K3": 1} |
| O1 | R1 | underlying target | RETREAT | V | 4 | 4 | 4 | {"K1": 1, "K2": 2, "K3": 1} |
| O1 | R2 | underlying target | ADVANCE | N | 4 | 4 | 4 | {"K1": 2, "K3": 2} |
| O1 | R2 | underlying target | ADVANCE | V | 4 | 4 | 4 | {"K1": 2, "K3": 2} |
| O1 | R2 | underlying target | HOLD | N | 4 | 4 | 4 | {"K1": 1, "K2": 2, "K3": 1} |
| O1 | R2 | underlying target | HOLD | V | 4 | 4 | 4 | {"K1": 1, "K2": 2, "K3": 1} |
| O1 | R2 | underlying target | RETREAT | N | 4 | 4 | 4 | {"K1": 1, "K2": 2, "K3": 1} |
| O1 | R2 | underlying target | RETREAT | V | 4 | 4 | 4 | {"K1": 1, "K2": 2, "K3": 1} |
| O1 | R3 | underlying target | ADVANCE | N | 4 | 4 | 4 | {"K1": 2, "K3": 2} |
| O1 | R3 | underlying target | ADVANCE | V | 4 | 4 | 2 | {"K1": 4} |
| O1 | R3 | underlying target | HOLD | N | 4 | 4 | 4 | {"K1": 1, "K2": 2, "K3": 1} |
| O1 | R3 | underlying target | HOLD | V | 4 | 4 | 3 | {"K1": 1, "K2": 3} |
| O1 | R3 | underlying target | RETREAT | N | 4 | 4 | 4 | {"K1": 1, "K2": 2, "K3": 1} |
| O1 | R3 | underlying target | RETREAT | V | 4 | 4 | 3 | {"K1": 2, "K2": 2} |
| O1 | R1 | target alias | K1 | N | 4 | 4 | 4 | {"K1": 4} |
| O1 | R1 | target alias | K1 | V | 4 | 4 | 4 | {"K1": 4} |
| O1 | R1 | target alias | K2 | N | 4 | 4 | 4 | {"K2": 4} |
| O1 | R1 | target alias | K2 | V | 4 | 4 | 4 | {"K2": 4} |
| O1 | R1 | target alias | K3 | N | 4 | 4 | 4 | {"K3": 4} |
| O1 | R1 | target alias | K3 | V | 4 | 4 | 4 | {"K3": 4} |
| O1 | R2 | target alias | K1 | N | 4 | 4 | 4 | {"K1": 4} |
| O1 | R2 | target alias | K1 | V | 4 | 4 | 4 | {"K1": 4} |
| O1 | R2 | target alias | K2 | N | 4 | 4 | 4 | {"K2": 4} |
| O1 | R2 | target alias | K2 | V | 4 | 4 | 4 | {"K2": 4} |
| O1 | R2 | target alias | K3 | N | 4 | 4 | 4 | {"K3": 4} |
| O1 | R2 | target alias | K3 | V | 4 | 4 | 4 | {"K3": 4} |
| O1 | R3 | target alias | K1 | N | 4 | 4 | 4 | {"K1": 4} |
| O1 | R3 | target alias | K1 | V | 4 | 4 | 4 | {"K1": 4} |
| O1 | R3 | target alias | K2 | N | 4 | 4 | 4 | {"K2": 4} |
| O1 | R3 | target alias | K2 | V | 4 | 4 | 4 | {"K2": 4} |
| O1 | R3 | target alias | K3 | N | 4 | 4 | 4 | {"K3": 4} |
| O1 | R3 | target alias | K3 | V | 4 | 4 | 0 | {"K1": 3, "K2": 1} |
| O2 | R1 | mapping | 0 | N | 2 | 2 | 2 | {"M4": 1, "Q7": 1} |
| O2 | R1 | mapping | 0 | V | 2 | 2 | 2 | {"M4": 1, "Q7": 1} |
| O2 | R1 | mapping | 1 | N | 2 | 2 | 2 | {"M4": 1, "Q7": 1} |
| O2 | R1 | mapping | 1 | V | 2 | 2 | 2 | {"M4": 1, "Q7": 1} |
| O2 | R1 | mapping | 2 | N | 2 | 2 | 2 | {"Q7": 1, "Z2": 1} |
| O2 | R1 | mapping | 2 | V | 2 | 2 | 1 | {"Q7": 2} |
| O2 | R1 | mapping | 3 | N | 2 | 2 | 1 | {"M4": 1, "Q7": 1} |
| O2 | R1 | mapping | 3 | V | 2 | 2 | 2 | {"M4": 1, "Z2": 1} |
| O2 | R1 | mapping | 4 | N | 2 | 2 | 2 | {"Q7": 1, "Z2": 1} |
| O2 | R1 | mapping | 4 | V | 2 | 2 | 1 | {"Q7": 2} |
| O2 | R1 | mapping | 5 | N | 2 | 2 | 2 | {"M4": 1, "Z2": 1} |
| O2 | R1 | mapping | 5 | V | 2 | 2 | 1 | {"M4": 1, "Q7": 1} |
| O2 | R2 | mapping | 0 | N | 2 | 2 | 2 | {"M4": 1, "Q7": 1} |
| O2 | R2 | mapping | 0 | V | 2 | 2 | 2 | {"M4": 1, "Q7": 1} |
| O2 | R2 | mapping | 1 | N | 2 | 2 | 2 | {"M4": 1, "Q7": 1} |
| O2 | R2 | mapping | 1 | V | 2 | 2 | 2 | {"M4": 1, "Q7": 1} |
| O2 | R2 | mapping | 2 | N | 2 | 2 | 2 | {"Q7": 1, "Z2": 1} |
| O2 | R2 | mapping | 2 | V | 2 | 2 | 2 | {"Q7": 1, "Z2": 1} |
| O2 | R2 | mapping | 3 | N | 2 | 2 | 2 | {"M4": 1, "Z2": 1} |
| O2 | R2 | mapping | 3 | V | 2 | 2 | 2 | {"M4": 1, "Z2": 1} |
| O2 | R2 | mapping | 4 | N | 2 | 2 | 2 | {"Q7": 1, "Z2": 1} |
| O2 | R2 | mapping | 4 | V | 2 | 2 | 2 | {"Q7": 1, "Z2": 1} |
| O2 | R2 | mapping | 5 | N | 2 | 2 | 2 | {"M4": 1, "Z2": 1} |
| O2 | R2 | mapping | 5 | V | 2 | 2 | 2 | {"M4": 1, "Z2": 1} |
| O2 | R3 | mapping | 0 | N | 2 | 2 | 1 | {"Q7": 2} |
| O2 | R3 | mapping | 0 | V | 2 | 2 | 2 | {"M4": 1, "Q7": 1} |
| O2 | R3 | mapping | 1 | N | 2 | 2 | 1 | {"Q7": 2} |
| O2 | R3 | mapping | 1 | V | 2 | 2 | 1 | {"Q7": 2} |
| O2 | R3 | mapping | 2 | N | 2 | 2 | 1 | {"Q7": 2} |
| O2 | R3 | mapping | 2 | V | 2 | 2 | 1 | {"Q7": 2} |
| O2 | R3 | mapping | 3 | N | 2 | 2 | 0 | {"Q7": 2} |
| O2 | R3 | mapping | 3 | V | 2 | 2 | 2 | {"M4": 1, "Z2": 1} |
| O2 | R3 | mapping | 4 | N | 2 | 2 | 1 | {"Q7": 2} |
| O2 | R3 | mapping | 4 | V | 2 | 2 | 1 | {"M4": 1, "Q7": 1} |
| O2 | R3 | mapping | 5 | N | 2 | 2 | 0 | {"Q7": 2} |
| O2 | R3 | mapping | 5 | V | 2 | 2 | 0 | {"Q7": 2} |
| O2 | R1 | underlying target | ADVANCE | N | 4 | 4 | 3 | {"Q7": 3, "Z2": 1} |
| O2 | R1 | underlying target | ADVANCE | V | 4 | 4 | 3 | {"Q7": 3, "Z2": 1} |
| O2 | R1 | underlying target | HOLD | N | 4 | 4 | 4 | {"M4": 2, "Q7": 1, "Z2": 1} |
| O2 | R1 | underlying target | HOLD | V | 4 | 4 | 3 | {"M4": 2, "Q7": 2} |
| O2 | R1 | underlying target | RETREAT | N | 4 | 4 | 4 | {"M4": 2, "Q7": 1, "Z2": 1} |
| O2 | R1 | underlying target | RETREAT | V | 4 | 4 | 3 | {"M4": 2, "Q7": 2} |
| O2 | R2 | underlying target | ADVANCE | N | 4 | 4 | 4 | {"Q7": 2, "Z2": 2} |
| O2 | R2 | underlying target | ADVANCE | V | 4 | 4 | 4 | {"Q7": 2, "Z2": 2} |
| O2 | R2 | underlying target | HOLD | N | 4 | 4 | 4 | {"M4": 2, "Q7": 1, "Z2": 1} |
| O2 | R2 | underlying target | HOLD | V | 4 | 4 | 4 | {"M4": 2, "Q7": 1, "Z2": 1} |
| O2 | R2 | underlying target | RETREAT | N | 4 | 4 | 4 | {"M4": 2, "Q7": 1, "Z2": 1} |
| O2 | R2 | underlying target | RETREAT | V | 4 | 4 | 4 | {"M4": 2, "Q7": 1, "Z2": 1} |
| O2 | R3 | underlying target | ADVANCE | N | 4 | 4 | 2 | {"Q7": 4} |
| O2 | R3 | underlying target | ADVANCE | V | 4 | 4 | 3 | {"Q7": 3, "Z2": 1} |
| O2 | R3 | underlying target | HOLD | N | 4 | 4 | 1 | {"Q7": 4} |
| O2 | R3 | underlying target | HOLD | V | 4 | 4 | 2 | {"M4": 2, "Q7": 2} |
| O2 | R3 | underlying target | RETREAT | N | 4 | 4 | 1 | {"Q7": 4} |
| O2 | R3 | underlying target | RETREAT | V | 4 | 4 | 2 | {"M4": 1, "Q7": 3} |
| O2 | R1 | target alias | M4 | N | 4 | 4 | 4 | {"M4": 4} |
| O2 | R1 | target alias | M4 | V | 4 | 4 | 4 | {"M4": 4} |
| O2 | R1 | target alias | Q7 | N | 4 | 4 | 4 | {"Q7": 4} |
| O2 | R1 | target alias | Q7 | V | 4 | 4 | 4 | {"Q7": 4} |
| O2 | R1 | target alias | Z2 | N | 4 | 4 | 3 | {"Q7": 1, "Z2": 3} |
| O2 | R1 | target alias | Z2 | V | 4 | 4 | 1 | {"Q7": 3, "Z2": 1} |
| O2 | R2 | target alias | M4 | N | 4 | 4 | 4 | {"M4": 4} |
| O2 | R2 | target alias | M4 | V | 4 | 4 | 4 | {"M4": 4} |
| O2 | R2 | target alias | Q7 | N | 4 | 4 | 4 | {"Q7": 4} |
| O2 | R2 | target alias | Q7 | V | 4 | 4 | 4 | {"Q7": 4} |
| O2 | R2 | target alias | Z2 | N | 4 | 4 | 4 | {"Z2": 4} |
| O2 | R2 | target alias | Z2 | V | 4 | 4 | 4 | {"Z2": 4} |
| O2 | R3 | target alias | M4 | N | 4 | 4 | 0 | {"Q7": 4} |
| O2 | R3 | target alias | M4 | V | 4 | 4 | 2 | {"M4": 2, "Q7": 2} |
| O2 | R3 | target alias | Q7 | N | 4 | 4 | 4 | {"Q7": 4} |
| O2 | R3 | target alias | Q7 | V | 4 | 4 | 4 | {"Q7": 4} |
| O2 | R3 | target alias | Z2 | N | 4 | 4 | 0 | {"Q7": 4} |
| O2 | R3 | target alias | Z2 | V | 4 | 4 | 1 | {"M4": 1, "Q7": 2, "Z2": 1} |

O2 chose Q7 in all 12 neutral R3 views despite the rotated underlying targets; only four of those choices were correct. In varied R3, O2 chose Q7 eight times, M4 three times and Z2 once. O1 varied R3 choices were K1 seven times and K2 five times, with no K3 choices. These are observed alias distributions, not an explanation of internal token preference.

Counts are descriptive; no subgroup threshold is added. The only per-target decision criterion remains the registered R3 N minimum3/4 for each underlying action. Full chosen-underlying-action and alias distributions are preserved for every cell in results.json.

## Interpretation

In this registered run, R2 was correct 48/48 and R1 correct 44/48; R3 was correct 31/48. Thus 17 of 21 observed errors occurred in R3, while four occurred in O2 R1. The weakness is concentrated in the 0-over-negative relation but is not exclusive to it. O1 was perfect in neutral R3 but fell to 8/12 in V. O2 failed neutral R3 at 4/12 and improved to 7/12 in V, so next_state variation did not have a uniform adverse direction. These counts do not establish an internal cause or general comparison failure across all finite relations. Both representations must satisfy the frozen gates independently; these descriptive pooled error counts do not replace those decisions.

O1 R1 N/V=12/12,12/12; R2 N/V=12/12,12/12. O2 R1 N/V=11/12,9/12; R2 N/V=12/12,12/12.

O1: R3 meets the registered N accuracy threshold (12/12) but misses V (8/12). The paired difference is compatible with irrelevant-field/representation interference; it does not establish the internal mechanism or satisfy the full R3 rule.

O2: R3 remains below the registered N threshold even with neutral next_state (4/12, required 10/12). This is evidence against relying on this model role as a deterministic finite argmax comparator in this bounded task.

Comparison across the three finite relations is descriptive. Stronger positive-best counts may locate a concentration of errors but do not prove that 0>-1 is the sole failure mode or reveal why the model behaves this way. Same-seed N/V controls remove the earlier seed mismatch; observed invariance remains bounded to the registered views.

## Replay and independent verification

All 144 saved real responses were replayed with network sockets forbidden and zero inference. Nine deterministic files match byte-for-byte, including exact request intents, raw/parsed records, pair metrics, journal, final campaign state and isolation proof. Separate final-results files match exactly after setting the verified replay gate; provisional live metrics were not overwritten. An independent audit rederived numeric maxima from the actual views, strict parsed choices, all 72 pair matches, seeds, exact registered request hashes, both families’ decision gates and journal integrity. Runtime guards recorded zero world/Map/Memory attempts.

## Tests and historical preservation

Six new study tests and five write-ahead durability tests passed. A synthetic 144-response invalid-output control replayed exactly; synthetic outputs are explicitly separate from real model evidence. All 631 inherited substantive files remain byte-identical. Read-only checks verified 14 prior sealed evidence inventories and unchanged earlier refs, main and tags. **No historical tests, historical live campaigns or world-based replays were rerun in this study.** This avoids world execution and is reported as preservation, not new historical experimental evidence. See [verification.json](../experiments/explorer_finite_value_comparator_v0/verification.json).

## Limits and prospective architecture

This is one pinned model/sampler with two opaque representations, 12 schedules and three finite consequence relations. It measures finite comparison and behavioral sensitivity, not Memory use, world modeling, causality, policy learning, general reasoning or closed-loop success. Shared model weights, repeated fixtures and paired seeds are not independent population samples. In-process guards assume a trusted driver.

If the registered neutral-next-state comparator is unreliable, a later separately authorized architecture decision should compare **MODEL EXPLORER** with **MECHANICAL ARGMAX EXPLORER**: a deterministic finite comparison need not require a language model unless the role contributes something beyond exploitation. Neither that comparison nor a mechanical Explorer is implemented here.

## Narrowest defensible result and stop

**ZERO-OVER-NEGATIVE COMPARATOR NOT ESTABLISHED; NEXT_STATE IRRELEVANCE NOT ESTABLISHED.** R3 correct N/V was 12/12 and 8/12 in O1, 4/12 and 7/12 in O2; each family had 8/12 same R3 choices. Overall N/V consistency was 32/36 and 28/36 respectively. All 144 replies were valid. The positive-best controls were stronger, but R1 also had errors in O2. The exact cell and pair counts above delimit these results. All previous decisions remain binding. Stop after 144 calls, exact replay and preservation. No Map modification, world execution, Memory change, closed loop, mechanical Explorer, added calls, threshold/prompt changes, main/tag edits or push.
