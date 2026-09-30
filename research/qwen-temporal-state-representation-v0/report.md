# Horus Temporal State Representation Gate v0 — completed report

Registered result: **TEMPORAL_STATE_REPRESENTATION_NOT_ESTABLISHED**.

Put the current Horus research direction on hold pending a genuinely new technical hypothesis, model capability or architecture. Do not launch another prompt workaround or decomposition benchmark.

Joint exact **28/36**; current field **33/36**; prior field **30/36**; historical focus **12/12**; schema-valid **36/36**. Scheduled / attempted / completed: **36 / 36 / 36**. No optional arm.

The historical-focus relation is correct in all 12 cases, while joint accuracy outside that subset is 16/24. That positive subset does not rescue the hard gate: five of seven conditions fail. Current-field errors are three UNKNOWN→NO selections. Prior-field errors are three NO→UNKNOWN, two UNKNOWN→YES, and one YES→UNKNOWN. Stable-vector agreement is 7/8, but only 5/8 stable pairs are exactly correct; agreement on a wrong vector is not retention of the required state.

## Provenance

- Branch: `research/qwen-temporal-state-representation-v0`
- Verified base: `19c50c06caf99736acbf5c728da0148840e665a5`
- Method Freeze: `8366b2815ed203240495308e1f38297bd432da61`
- Case Freeze: `db4d25017e6d8bcb1b58c20712b5f19ff6dbac0d`
- Post-freeze qualification: `3cf82dd18e71b1bf17fa822b08039b0216e7d03b`
- Raw pre-scoring commit: `8a97d8330d51248bc60de78a0da7d6641890a620`
- Final publication SHA: the verified remote head reported in the final completion handoff; a file cannot contain its own commit SHA.
- Seed: `1264087953`
- Qwen3-14B Q4_K_M SHA256: `500a8806e85ee9c83f3ae08420295592451379b4f8cf2d0f41c15dffeb6b81f0`
- llama.cpp b11242 commit: `526c43b8f7dfea9032e9f35e7a1be9183ca7cc20`
- Runtime executable SHA256: `778f1b3fbbb76e921af1d7f25a5b61d82859962dcd18c71ce86ab84d7f4884e5`

Context 16384; one slot; f16 KV and flash attention; thinking enabled, DeepSeek format, reasoning budget 512; temperature .2, top_p .9, top_k 40, min_p .05, max_tokens 2048. Cache disabled and slot erased per request. Same 41/41 GPU layer offload and inherited CPU-mapped embedding allocation. No tools, retrieval or conversation history. Native reasoning is private and non-authoritative.

## Hard-gate assessment

| Frozen condition | Observed | Pass |
|---|---|---|
| joint_at_least_32 | 28/36 | False |
| current_at_least_34 | 33/36 | False |
| prior_at_least_34 | 30/36 | False |
| historical_focus_at_least_11 | 12/12 | True |
| changing_pairs_at_least_9 | 7/10 | False |
| stable_pairs_all_8 | 5/8 | False |
| schema_valid_at_least_35 | 36/36 | True |

All-pair exact passes: **12/18**. Changing-field-only direction tracking: 7/10. Raw stable-vector agreement: 7/8. These two descriptive measures cannot replace exact changing or stable pair correctness. Every pair is disjoint and differs in one declared primitive field.

## Field confusion matrices

Rows are gold, columns selected. Invalid schema is wrong for both fields.

### current_violation

| Gold / selected | YES | NO | UNKNOWN | Invalid |
|---|---:|---:|---:|---:|
| YES | 7 | 0 | 0 | 0 |
| NO | 0 | 19 | 0 | 0 |
| UNKNOWN | 0 | 3 | 7 | 0 |

### prior_violation

| Gold / selected | YES | NO | UNKNOWN | Invalid |
|---|---:|---:|---:|---:|
| YES | 18 | 0 | 1 | 0 |
| NO | 0 | 8 | 3 | 0 |
| UNKNOWN | 2 | 0 | 4 | 0 |

## Joint confusion matrix

Pairs are current/prior. YES/UNKNOWN is an unsampled gold cell, so its zero row does not establish competence there.

| Gold / selected | YES/YES | YES/NO | YES/UNKNOWN | NO/YES | NO/NO | NO/UNKNOWN | UNKNOWN/YES | UNKNOWN/NO | UNKNOWN/UNKNOWN | Invalid |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| YES/YES | 2 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| YES/NO | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| YES/UNKNOWN | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| NO/YES | 0 | 0 | 0 | 12 | 0 | 0 | 0 | 0 | 0 | 0 |
| NO/NO | 0 | 0 | 0 | 0 | 1 | 3 | 0 | 0 | 0 | 0 |
| NO/UNKNOWN | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 |
| UNKNOWN/YES | 0 | 0 | 0 | 2 | 0 | 0 | 2 | 0 | 0 | 0 |
| UNKNOWN/NO | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 |
| UNKNOWN/UNKNOWN | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 1 | 0 |

## Controls and sampling

| Subset | Joint correct | Total |
|---|---:|---:|
| contradictory_packages | 17 | 21 |
| consistent_packages | 11 | 15 |
| multiple_prior_trials | 28 | 34 |
| prior_unknown | 4 | 6 |
| current_unknown | 6 | 10 |

Historical focus is intentionally oversampled: 12 NO/YES states; the remaining seven requested combinations have either three or four states each. Contradiction controls concern separate provenance assertions, so authoritative trial propositions remain mechanically evaluable under the frozen semantics. This is not a claim that a contradictory package supports a valid operational diagnosis.

## All matched-pair outcomes

| Pair | Changed primitive | Gold A→B | Selected A→B | Changing | Exact pass | Changed-field direction |
|---|---|---|---|---|---|---|
| ts-p01 | .current_trial.observation_requirement | NO/YES→YES/YES | NO/YES→YES/YES | True | True | True |
| ts-p02 | .current_trial.observation_requirement | NO/YES→YES/YES | NO/YES→YES/YES | True | True | True |
| ts-p03 | .current_trial.evidence_sufficiency | NO/YES→UNKNOWN/YES | NO/YES→UNKNOWN/YES | True | True | True |
| ts-p04 | .non_current_trials.2.observation_requirement | NO/NO→NO/YES | NO/UNKNOWN→NO/YES | True | False | False |
| ts-p05 | .non_current_trials.1.evidence_sufficiency | NO/YES→NO/UNKNOWN | NO/YES→NO/UNKNOWN | True | True | True |
| ts-p06 | .non_current_trials.3.evidence_sufficiency | NO/UNKNOWN→NO/YES | NO/UNKNOWN→NO/YES | True | True | True |
| ts-p07 | .non_current_trials.2.observation_requirement | YES/NO→YES/YES | YES/NO→YES/UNKNOWN | True | False | False |
| ts-p08 | .current_trial.observation_requirement | YES/NO→NO/NO | YES/NO→NO/NO | True | True | True |
| ts-p09 | .non_current_trials.0.observation_requirement | UNKNOWN/YES→UNKNOWN/NO | UNKNOWN/YES→UNKNOWN/NO | True | True | True |
| ts-p10 | .current_trial.evidence_sufficiency | NO/UNKNOWN→UNKNOWN/UNKNOWN | NO/UNKNOWN→NO/YES | True | False | False |
| ts-p11 | .package.consistency | NO/YES→NO/YES | NO/YES→NO/YES | False | True | None |
| ts-p12 | .non_current_trials.1.observation_requirement | NO/YES→NO/YES | NO/YES→NO/YES | False | True | None |
| ts-p13 | .package.consistency | NO/YES→NO/YES | NO/YES→NO/YES | False | True | None |
| ts-p14 | .package.consistency | YES/NO→YES/NO | YES/NO→YES/NO | False | True | None |
| ts-p15 | .package.consistency | NO/NO→NO/NO | NO/UNKNOWN→NO/UNKNOWN | False | False | None |
| ts-p16 | .non_current_trials.0.observation_requirement | UNKNOWN/YES→UNKNOWN/YES | NO/YES→NO/YES | False | False | None |
| ts-p17 | .package.consistency | UNKNOWN/NO→UNKNOWN/NO | UNKNOWN/NO→UNKNOWN/NO | False | True | None |
| ts-p18 | .non_current_trials.1.observation_requirement | UNKNOWN/UNKNOWN→UNKNOWN/UNKNOWN | UNKNOWN/YES→UNKNOWN/UNKNOWN | False | False | None |

## Exact endpoint table

| State | Pair / side | Gold current/prior | Selected current/prior | Joint correct | Historical focus |
|---|---|---|---|---|---|
| ts-v0-aeb3b4bb75b506 | ts-p01/A | NO/YES | NO/YES | True | True |
| ts-v0-7ee6016eb8e611 | ts-p01/B | YES/YES | YES/YES | True | False |
| ts-v0-39e18be3c317e9 | ts-p02/A | NO/YES | NO/YES | True | True |
| ts-v0-7b0ee2f9fea043 | ts-p02/B | YES/YES | YES/YES | True | False |
| ts-v0-b0d1c8b3e0ae64 | ts-p03/A | NO/YES | NO/YES | True | True |
| ts-v0-6f86c2c7dd446d | ts-p03/B | UNKNOWN/YES | UNKNOWN/YES | True | False |
| ts-v0-df0eaaf6671c80 | ts-p04/A | NO/NO | NO/UNKNOWN | False | False |
| ts-v0-f9967e69213990 | ts-p04/B | NO/YES | NO/YES | True | True |
| ts-v0-a26628e4ae0610 | ts-p05/A | NO/YES | NO/YES | True | True |
| ts-v0-c59671ee66cefd | ts-p05/B | NO/UNKNOWN | NO/UNKNOWN | True | False |
| ts-v0-0c668665c90b65 | ts-p06/A | NO/UNKNOWN | NO/UNKNOWN | True | False |
| ts-v0-330d94293ea800 | ts-p06/B | NO/YES | NO/YES | True | True |
| ts-v0-89b524beb9f53f | ts-p07/A | YES/NO | YES/NO | True | False |
| ts-v0-55a893467cbba8 | ts-p07/B | YES/YES | YES/UNKNOWN | False | False |
| ts-v0-bd0d8ab4dd92da | ts-p08/A | YES/NO | YES/NO | True | False |
| ts-v0-09837cee941fd8 | ts-p08/B | NO/NO | NO/NO | True | False |
| ts-v0-a4e106c4c867d7 | ts-p09/A | UNKNOWN/YES | UNKNOWN/YES | True | False |
| ts-v0-feb704384d5d9b | ts-p09/B | UNKNOWN/NO | UNKNOWN/NO | True | False |
| ts-v0-024a820f994e30 | ts-p10/A | NO/UNKNOWN | NO/UNKNOWN | True | False |
| ts-v0-1b52f068a3f71f | ts-p10/B | UNKNOWN/UNKNOWN | NO/YES | False | False |
| ts-v0-0046f99f6350bf | ts-p11/A | NO/YES | NO/YES | True | True |
| ts-v0-c96043fb03b7bb | ts-p11/B | NO/YES | NO/YES | True | True |
| ts-v0-1c9581141f1b6d | ts-p12/A | NO/YES | NO/YES | True | True |
| ts-v0-bd0674281d558a | ts-p12/B | NO/YES | NO/YES | True | True |
| ts-v0-2ed1163c882e41 | ts-p13/A | NO/YES | NO/YES | True | True |
| ts-v0-0b6a4e844a6860 | ts-p13/B | NO/YES | NO/YES | True | True |
| ts-v0-9d05bc41c54ebe | ts-p14/A | YES/NO | YES/NO | True | False |
| ts-v0-3503ccf52e36c5 | ts-p14/B | YES/NO | YES/NO | True | False |
| ts-v0-19c5c04a551093 | ts-p15/A | NO/NO | NO/UNKNOWN | False | False |
| ts-v0-3bc8ca26b5483c | ts-p15/B | NO/NO | NO/UNKNOWN | False | False |
| ts-v0-bbc1a09704032e | ts-p16/A | UNKNOWN/YES | NO/YES | False | False |
| ts-v0-095cd8a8182549 | ts-p16/B | UNKNOWN/YES | NO/YES | False | False |
| ts-v0-eba8597228ee0c | ts-p17/A | UNKNOWN/NO | UNKNOWN/NO | True | False |
| ts-v0-7d4e5751a06823 | ts-p17/B | UNKNOWN/NO | UNKNOWN/NO | True | False |
| ts-v0-9ae0772932b33b | ts-p18/A | UNKNOWN/UNKNOWN | UNKNOWN/YES | False | False |
| ts-v0-946dd869d28e87 | ts-p18/B | UNKNOWN/UNKNOWN | UNKNOWN/UNKNOWN | True | False |

## Freshness, leakage and execution integrity

Independent validation recomputed every primitive from finite witnesses, evaluated all current and existential-prior truth possibilities, and verified every gold vector and one-field pair delta. All 36 input objects satisfy the frozen schema. Thirty-six unique normalized temporal signatures exclude all 136 prior state objects/projections, even after removing IDs, wording, identity decorations and prior-trial order. Prior model outputs and gold did not influence construction. The primitive definitions and abstract output combinations are intentionally reused.

No diagnostic ontology labels/definitions, answer examples, demonstrations, gold vectors, proof, pair metadata or deterministic temporal summary enter model-visible inputs. The output semantics are explicitly provided as required, so any positive result is scoped to that interface. The input provides only resolved trial propositions, including sufficiency and reference relations.

33 qualification checks passed after Method and Case Freeze, using zero-model synthetic transport fixtures and strict two-field scoring/gate boundaries. Pinned hashes and zero-completion runtime startup passed. No scientific inference was used for qualification or tuning. Frozen method, case, prompt, scorer and runtime settings stayed unchanged.

All 36 calls completed once. Zero retries, repairs or critics; no correctness inspection during execution. Total completion wall time 391.75s, mean 10.88s. Finals and safe metadata were hashed, made read-only and committed before scoring. Zero-inference replay is byte-identical: `7555d5cbc0a325b2cd811f2f9580b99eeb5557a90f4d814e4c5c1c37e2180cf7`. Private envelopes, native reasoning and logs remain outside Git with a public hash-only manifest.

Prior bare role-grounding historical accuracy was 2/6; the earlier primitive-to-ontology study had 5/10. These are different cases and different output tasks. This study establishes no causal improvement percentage, same-case compression experiment, or internal cognitive mechanism. Interpret the registered hard gate literally.

## Preservation and publication

All inherited files, prior heads, main, S/E sources, grounded state, Memory, policy, thresholds and completed studies remain unchanged. Audit artifacts record full reachable commit/path and unique-blob scanning plus private-artifact exclusion. Only this study branch is published, with final remote SHA verification. No merge, promotion, architecture change, hard-coded operational reducer or subsequent study.

## Requested answers

1. **Can Qwen reliably represent current violation state?** 33/36, below the frozen 34/36 field threshold. The full competence claim still requires every gate condition.

2. **Can it reliably preserve prior violation state?** 30/36, below the frozen 34/36 field threshold, including existential aggregation across older trials.

3. **Can it represent current=NO, prior=YES reliably?** Historical-focus joint accuracy is 12/12, meeting the 11/12 floor.

4. **Does it track minimal temporal changes?** Changing-pair exact passes: 7/10, below the 9/10 gate. Changed-field-only direction tracking is 7/10 and is descriptive, not a substitute for exact output-vector correctness.

5. **Does it ignore irrelevant changes?** Stable-pair exact retention: 5/8, below the required 8/8. Mere selection agreement, including consistently wrong outputs, is reported separately.

6. **Does removing the five-class ontology repair the historical failure?** The historical-focus relation itself is correct in 12/12 fresh cases, so the observed subset failure is absent under this two-field interface. However, the complete temporal capability fails the hard gate because other combinations and controlled pairs remain unreliable. Different cases and output semantics prevent proving that removal of five-class compression caused the subset improvement.

7. **Is a factorized temporal state empirically justified?** Not as an established Qwen capability under this gate. Hard-coding the state construction would demonstrate software behavior, not supply the missing evidence about Qwen.

8. **If not, should this research direction be paused?** Yes. Put the current Horus research direction on hold pending a genuinely new technical hypothesis, model capability or architecture. Do not launch another prompt workaround, comparator or decomposition benchmark.

9. **If yes, what exact capability is established?** No whole-task temporal representation capability has been established by the registered gate. Report the measured field, focus and pair results literally.

10. **What remains necessary before any RSI claim?** A future system must perform a useful task, accumulate authenticated consequences and improve later behavior; diagnose its own limitation; propose a bounded modification and predict its improvement prospectively; apply it through an external/sandboxed authorization boundary; test it prospectively; retain it only when real consequences support it; and successfully repeat with the improved system. At least two prospectively separated successful improvement cycles are required before a strictly scoped BOUNDED_RECURSIVE_SELF_IMPROVEMENT_SUPPORTED claim. One self-modification is insufficient.

## Future engineering and RSI boundary

If the gate passes, a separately authorized engineering study may consider authenticated evidence → factorized grounded epistemic state → persistent temporal relations → action/evidence-selection policy, with five-class labels serving reporting/compatibility. That work must demonstrate actual behavior improvement; it is not implemented here. If the gate fails, the current research direction should be put on hold pending a genuinely new technical reason, not another automatic prompt workaround.

Any RSI claim additionally requires the full prospective sequence:

1. Perform a useful real task.
2. Accumulate authenticated consequences.
3. Improve later behavior from those consequences.
4. Diagnose a limitation in the current implementation.
5. Propose a bounded modification to implementation, policy or model configuration.
6. Predict measurable improvement before applying it.
7. Apply the modification only through an external/sandboxed authorization boundary.
8. Prospectively test the modified system.
9. Retain the modification only when real consequences support it.
10. Repeat successfully with the improved system.

At least two prospectively separated successful improvement cycles are required before BOUNDED_RECURSIVE_SELF_IMPROVEMENT_SUPPORTED, scoped strictly to the tested environment and modification class. A single self-modification is insufficient. No RSI has been established here.

