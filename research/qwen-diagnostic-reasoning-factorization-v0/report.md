# Diagnostic Reasoning Factorization v0 — completed results

Status: `DIAGNOSTIC_REASONING_FACTORIZATION_COMPLETE_V0`. This report applies only to the new prospective factorization study. Prior completed studies remain preserved without reanalysis.

## Provenance and execution

- Branch: `research/qwen-diagnostic-reasoning-factorization-v0`.
- Base: `98acb89c75a4ecd2a05463fa46bddead0c60c316`.
- Method Freeze: `e1c5932870a074ec24a5d58ff69994125676a33a`.
- Case Freeze: `ad78344f870de2b442c319b77e0110b68dfad45c`.
- Raw pre-scoring commit: `2091c8fe6f1b6e77c8c56af78e49a07a5d349f64`.
- Scientific calls: 80 attempted / 80 completed / 80 scheduled. Zero retries, repairs, critics, comparator calls or compiler calls.
- Qwen3-14B Q4_K_M model SHA256: `500a8806e85ee9c83f3ae08420295592451379b4f8cf2d0f41c15dffeb6b81f0`.
- llama.cpp b11242, commit `526c43b8f7dfea9032e9f35e7a1be9183ca7cc20`; installed server SHA256 `778f1b3fbbb76e921af1d7f25a5b61d82859962dcd18c71ce86ab84d7f4884e5`.
- Context 16384; one slot; reasoning on/DeepSeek, budget 512; temperature 0.2, top_p 0.9, top_k 40, min_p 0.05, max_tokens 2048; seed 862540719. Fresh erased idle state per request, caching disabled, no model tools or history.
- Raw outputs were committed before the frozen scorer ran. Full native reasoning and envelopes remain private; public artifacts contain final answers and safe metadata/hashes.

## Separate registered results

| Arm | Exact joint/class accuracy | Schema-valid | Registered gate | Simpler /10 | Composition-dependent /10 |
|---|---:|---:|---|---:|---:|
| O: Operational computation | 18/20 | 20/20 | NOT ESTABLISHED | 9 | 9 |
| S: Evidence-state reasoning | 8/20 | 18/20 | NOT ESTABLISHED | 6 | 2 |
| R: Epistemic reduction | 10/20 | 20/20 | NOT ESTABLISHED | 4 | 6 |
| E: End-to-end diagnosis | 8/20 | 20/20 | NOT ESTABLISHED | 5 | 3 |

O requires at least 17/20 joint and at least one jointly correct world in every operation family. S requires at least 17/20 joint and at least 18/20 in every field. R and E each independently require at least 17/20 and at least 3/4 in every class. These gates were frozen before inference. No pooled intelligence score is defined.

### O: exact operational computation

Individual computations correct: **38/40**. Each world asks for two ordered results; joint credit requires both.

| Operation family | Joint worlds /2 | Individual results /4 |
|---|---:|---:|
| binomial selection count | 2 | 4 |
| conjunctive-disjunctive Boolean circuit | 2 | 4 |
| directed reachability closure | 2 | 4 |
| finite linear convolution | 0 | 2 |
| finite-state sequence recognizer | 2 | 4 |
| greatest common divisor | 2 | 4 |
| overlapping substring occurrence count | 2 | 4 |
| sliding window maximum | 2 | 4 |
| stable vowel deletion | 2 | 4 |
| unit-cost string edit distance | 2 | 4 |

O error categories: `{"VALUE_MISMATCH": 2}`.

### S: evidence-state construction

| Exact field | Correct /20 |
|---|---:|
| target_component_id | 18 |
| in_service_build_id | 18 |
| in_service_receipt_ids | 16 |
| other_build_receipt_ids | 12 |
| other_component_receipt_ids | 16 |
| receipt_source_links | 17 |
| capture_groups | 15 |
| source_knowledge | 11 |
| conflicting_capture_ids | 13 |

A schema-invalid response receives zero field and joint credit. All arrays are compared as unordered sets of unique schema-valid entries. No partial prose repair is used. Whole-state failure combines binding and the demanding structured-output task; it does not by itself identify an internal cognitive mechanism.

S error categories: `{"SCHEMA_FAILURE": 2, "STATE_FIELD_MISMATCH": 10}`.

### Class-stratified performance

D = SUPPORTED_CURRENT_DEFECT; H = NO_SUPPORTED_DIAGNOSIS; U = INSUFFICIENT_EVIDENCE; T = HISTORICAL_DEFECT_NOT_CURRENT; X = INVALID_OR_CONTRADICTORY_EVIDENCE. O and S columns describe strata of their exact operational/state tasks, not class-selection tasks.

| Gold class | O /4 | S /4 | R /4 | E /4 |
|---|---:|---:|---:|---:|
| D | 4 | 2 | 4 | 4 |
| H | 3 | 1 | 2 | 3 |
| U | 3 | 1 | 2 | 1 |
| T | 4 | 2 | 2 | 0 |
| X | 4 | 2 | 0 | 0 |

### R: Epistemic reduction

Class accuracy 10/20; schema-valid 20/20. Critical U+T+X subset: 4/12; descriptive 10/12 check: NOT MET. This subset check is not an extra competence gate. Matched decisive-change sensitivity: NOT_APPLICABLE, because no flip pairs were preregistered.

Confusion matrix: rows are gold, columns are selected class; invalid output gets its own column.

| Gold \ selected | D | H | U | T | X | Invalid output |
|---|---:|---:|---:|---:|---:|---:|
| D | 4 | 0 | 0 | 0 | 0 | 0 |
| H | 0 | 2 | 0 | 2 | 0 | 0 |
| U | 0 | 1 | 2 | 1 | 0 | 0 |
| T | 0 | 0 | 1 | 2 | 1 | 0 |
| X | 0 | 1 | 0 | 3 | 0 | 0 |

R error categories: `{"CLASS_MISMATCH": 10}`.

### E: End-to-end diagnosis

Class accuracy 8/20; schema-valid 20/20. Critical U+T+X subset: 1/12; descriptive 10/12 check: NOT MET. This subset check is not an extra competence gate. Matched decisive-change sensitivity: NOT_APPLICABLE, because no flip pairs were preregistered.

Confusion matrix: rows are gold, columns are selected class; invalid output gets its own column.

| Gold \ selected | D | H | U | T | X | Invalid output |
|---|---:|---:|---:|---:|---:|---:|
| D | 4 | 0 | 0 | 0 | 0 | 0 |
| H | 1 | 3 | 0 | 0 | 0 | 0 |
| U | 1 | 2 | 1 | 0 | 0 | 0 |
| T | 1 | 3 | 0 | 0 | 0 | 0 |
| X | 2 | 2 | 0 | 0 | 0 | 0 |

E error categories: `{"CLASS_MISMATCH": 12}`.

## Matched cross-arm factorization

Twenty semantic worlds are matched units, with additional correlation within ten operation families. The 80 calls are not 80 independent observations. A check mark denotes exact full-schema correctness for the requested arm.

| World | Family | Gold | O | S | R | E | R selected | E selected |
|---|---|---|---|---|---|---|---|---|
| w1e04f7b3754e | unit-cost string edit distance | X | ✓ | ✗ | ✗ | ✗ | T | D |
| w207cc12f3c2e | finite linear convolution | U | ✗ | ✗ | ✗ | ✗ | H | H |
| w2d40dc1ef9ab | greatest common divisor | X | ✓ | ✗ | ✗ | ✗ | H | D |
| w4045154ea61d | conjunctive-disjunctive Boolean circuit | D | ✓ | ✓ | ✓ | ✓ | D | D |
| w50e12a812eb3 | sliding window maximum | D | ✓ | ✓ | ✓ | ✓ | D | D |
| w80751078b01a | finite-state sequence recognizer | U | ✓ | ✗ | ✓ | ✗ | U | D |
| w84507bf62726 | overlapping substring occurrence count | U | ✓ | ✗ | ✗ | ✗ | T | H |
| w8778803bb730 | unit-cost string edit distance | T | ✓ | ✗ | ✗ | ✗ | X | H |
| wa43120033b1c | stable vowel deletion | D | ✓ | ✗ | ✓ | ✓ | D | D |
| wb465decd9d84 | directed reachability closure | U | ✓ | ✓ | ✓ | ✓ | U | U |
| wc0f27af52686 | stable vowel deletion | X | ✓ | ✓ | ✗ | ✗ | T | H |
| wc615b7a5117f | finite linear convolution | H | ✗ | ✓ | ✗ | ✓ | T | H |
| wc7e52e7d1b96 | binomial selection count | T | ✓ | ✓ | ✗ | ✗ | U | H |
| wcaafc1a41315 | directed reachability closure | T | ✓ | ✗ | ✓ | ✗ | T | H |
| wcde36fb724f5 | greatest common divisor | D | ✓ | ✗ | ✓ | ✓ | D | D |
| wcf8ac40be9b1 | overlapping substring occurrence count | T | ✓ | ✓ | ✓ | ✗ | T | D |
| wd0562a3af7f3 | conjunctive-disjunctive Boolean circuit | H | ✓ | ✗ | ✓ | ✓ | H | H |
| wd440bda21d29 | finite-state sequence recognizer | H | ✓ | ✗ | ✓ | ✓ | H | H |
| wf0649f5ed7c1 | sliding window maximum | H | ✓ | ✗ | ✗ | ✗ | T | D |
| wffd7271aa8b2 | binomial selection count | X | ✓ | ✓ | ✗ | ✗ | T | H |

### Matched associations

The rows overlap and are descriptive associations, not causal partitions. Denominators condition on the named eligible world set. Exact memberships are provided in scores.json.

| Observation | Count / eligible worlds |
|---|---:|
| E wrong among O-wrong worlds | 1/2 |
| S wrong among O-correct worlds | 11/18 |
| R wrong among S-correct worlds | 4/8 |
| E wrong among worlds with O/S/R all correct | 1/4 |
| Any O/S/R error among E-correct worlds | 5/8 |
| At least two O/S/R errors among all worlds | 7/20 |
| S wrong among O-wrong worlds | 1/2 |
| R wrong among O-wrong worlds | 2/2 |
| E wrong among O-wrong worlds | 1/2 |
| R wrong among S-wrong worlds | 6/12 |
| E wrong among S-wrong worlds | 8/12 |
| E wrong among R-wrong worlds | 9/10 |

E minus R exact correct: -2/20. Recognized class disagreements: 12/20; worlds missing a recognized label in either arm: 0.

| R → E outcome transition | Worlds |
|---|---:|
| correct_to_wrong | 3 |
| wrong_to_correct | 1 |
| wrong_to_different_wrong | 8 |
| unchanged | 8 |

Class disagreements and correctness transitions are different summaries: two wrong but different labels count as a label disagreement, while an unchanged wrong label does not. Missing labels are explicitly reported. No result from one arm entered another prompt.

## Registered interpretation and capability boundary

Registered pattern: `D_MULTIPLE_ISOLATED_LIMITATIONS`.

See [capability-boundary.md](capability-boundary.md) for the five explicit capability questions, literal gate interpretation and limitations.

All 80 calls ended with finish_reason=stop; none reached the 2048-token completion limit. The largest prompt was 3465 tokens. execution-profile.json provides per-arm token ranges.

## Reproducibility, leakage and preservation

- 40 zero-model qualification tests passed before inference; all 262 generated files regenerated exactly. Model/runtime hashes passed pre-inference verification.
- Preflight examined 1,704 prior files, parsed 1,216 JSON files, and audited IDs, operational contracts, concrete worlds/tuples and mechanism templates. All 570 new evidence IDs are fresh. Universal ontology, deployment and provenance concepts are disclosed reuse.
- R uses independently authored lower-level aligned facts, with no opaque record IDs or class-like judgment flags. O contains only its bounded computation. S/E raw packages are identical; S alone adds the assigned computation table. No existing compiler is used.
- postflight.json records raw hash/read-only checks, request schedule, private-response hashes, slot erasures, server shutdown and preservation of 2,688 inherited files plus 19 local and 19 remote protected heads.
- replay.json records byte-identical scoring replay without inference. Exact score SHA256: `d98790bcb4eb50eee09d659be34b064126ea09c5fd6ae7cff056c847ba342cc5`.
- Publication audit covers the entire reachable public history using unchanged scan rules. Private archive heads and private raw reasoning/envelopes remain outside public ancestry. Only the new branch is published. Exact final remote SHA is verified after push and reported in the handoff; it cannot be embedded in its own commit.

No weights, Memory, policy, thresholds, Horus architecture or promoted lineage changed. No merge, intervention, comparator or next study was performed.
