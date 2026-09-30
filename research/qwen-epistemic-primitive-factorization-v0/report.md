# Qwen Epistemic Primitive Factorization v0 — completed results

Status: `QWEN_EPISTEMIC_PRIMITIVE_FACTORIZATION_COMPLETE_V0`. Registered interpretation: `PRIMITIVES_ESTABLISHED_REDUCTION_NOT_ESTABLISHED`. Prior completed studies are preserved without reanalysis.

## Provenance and runtime

- Branch: research/qwen-epistemic-primitive-factorization-v0.
- Directly verified remote base: `2170b160527c41f4084ca6268dcb03a79b8d3641`.
- Method Freeze: `767bf35fb87f77229929468b7af28151057250cc`.
- Case Freeze: `bb004b5ff4b91bf85053167241538639bac1d46d`.
- Raw pre-scoring freeze: `3d9214bf3c9d6e1899aad4475e3deb54c9fe0b8e`.
- Seed: 413708629.
- Scientific calls: 112 scheduled / 112 attempted / 112 completed. No retries, repairs, critics, compiler or comparator calls.
- Qwen3-14B Q4_K_M model SHA256: `500a8806e85ee9c83f3ae08420295592451379b4f8cf2d0f41c15dffeb6b81f0`.
- llama.cpp b11242 commit: `526c43b8f7dfea9032e9f35e7a1be9183ca7cc20`; installed server SHA256: `778f1b3fbbb76e921af1d7f25a5b61d82859962dcd18c71ce86ab84d7f4884e5`.
- Context16384, one slot, reasoning on/DeepSeek/budget512, temperature0.2, top_p0.9, top_k40, min_p0.05, max_tokens2048; caching disabled, fresh erased idle slot, no model tools or history.
- Native reasoning and full envelopes remain private. Final outputs and safe metadata were hashed, made read-only and committed before scoring.

## Seven separate primitive results

Each primitive gate requires at least 7/8 exact endpoints AND at least 3/4 exact directional pair passes. No pooled primitive competence score is defined.

| Primitive | Correct /8 | Schema-valid /8 | Pair passes /4 | Gate |
|---|---|---|---|---|
| IDENTITY_EQUALITY | 8 | 8 | 4 | ESTABLISHED |
| CURRENTNESS | 8 | 8 | 4 | ESTABLISHED |
| KNOWN_VS_UNKNOWN | 8 | 8 | 4 | ESTABLISHED |
| CONTRADICTION | 8 | 8 | 4 | ESTABLISHED |
| ALTERNATIVE_COMPLETION_EXISTENCE | 8 | 8 | 4 | ESTABLISHED |
| OBSERVATION_REQUIREMENT_COMPARISON | 8 | 8 | 4 | ESTABLISHED |
| EVIDENCE_SUFFICIENCY | 8 | 8 | 4 | ESTABLISHED |

## Five-class reduction

Exact accuracy: **41/56**. Schema-valid: **56/56**. Gate: **NOT ESTABLISHED**. The frozen gate requires at least 48/56 plus every exact class floor below.

| Class | Correct | Denominator | Required minimum |
|---|---|---|---|
| SUPPORTED_CURRENT_DEFECT | 7 | 12 | 9 |
| NO_SUPPORTED_DIAGNOSIS | 11 | 12 | 9 |
| INSUFFICIENT_EVIDENCE | 6 | 11 | 9 |
| HISTORICAL_DEFECT_NOT_CURRENT | 7 | 11 | 9 |
| INVALID_OR_CONTRADICTORY_EVIDENCE | 10 | 10 | 8 |

D=current defect; H=no supported diagnosis; U=insufficient evidence; T=historical defect; X=contradictory evidence. Confusion rows are gold and columns are selected class. Invalid outputs occupy their own column.

| Gold \ selected | D | H | U | T | X | Invalid |
|---|---|---|---|---|---|---|
| D | 7 | 0 | 5 | 0 | 0 | 0 |
| H | 0 | 11 | 0 | 1 | 0 | 0 |
| U | 0 | 3 | 6 | 2 | 0 | 0 |
| T | 2 | 2 | 0 | 7 | 0 | 0 |
| X | 0 | 0 | 0 | 0 | 10 | 0 |

Reduction exact-pair passes: 16/28. Diagnostic-flip sensitivity: 11/19. Class-stable exact retention: 5/9. A stable-class pair is not a failed flip opportunity.

Reduction error categories: `{"VALUE_MISMATCH": 15}`.

## Matched primitive/reduction comparisons

These compare one queried primitive and reduction on each same state. They do not measure all seven model primitives on every state. The 112 calls represent 56 states in 28 correlated pairs, grouped by seven primitive families.

| Family | P correct /8 | P pairs /4 | R correct /8 | R pairs /4 | R flip passes | R stable passes |
|---|---|---|---|---|---|---|
| IDENTITY_EQUALITY | 8 | 4 | 8 | 4 | 2/2 | 2/2 |
| CURRENTNESS | 8 | 4 | 6 | 2 | 1/3 | 1/1 |
| KNOWN_VS_UNKNOWN | 8 | 4 | 5 | 2 | 2/2 | 0/2 |
| CONTRADICTION | 8 | 4 | 7 | 3 | 3/4 | N/A |
| ALTERNATIVE_COMPLETION_EXISTENCE | 8 | 4 | 5 | 2 | 1/2 | 1/2 |
| OBSERVATION_REQUIREMENT_COMPARISON | 8 | 4 | 7 | 3 | 2/2 | 1/2 |
| EVIDENCE_SUFFICIENCY | 8 | 4 | 3 | 0 | 0/4 | N/A |

N/A means no pairs of that type were included.

Endpoint joint outcomes:

| Family | P✓ R✓ | P✓ R✗ | P✗ R✓ | P✗ R✗ |
|---|---|---|---|---|
| IDENTITY_EQUALITY | 8 | 0 | 0 | 0 |
| CURRENTNESS | 6 | 2 | 0 | 0 |
| KNOWN_VS_UNKNOWN | 5 | 3 | 0 | 0 |
| CONTRADICTION | 7 | 1 | 0 | 0 |
| ALTERNATIVE_COMPLETION_EXISTENCE | 5 | 3 | 0 | 0 |
| OBSERVATION_REQUIREMENT_COMPARISON | 7 | 1 | 0 | 0 |
| EVIDENCE_SUFFICIENCY | 3 | 5 | 0 | 0 |

Pair joint outcomes (P means directional primitive pair pass; R means both reduction endpoints correct with their expected flip or retention):

| Family | P✓ R✓ | P✓ R✗ | P✗ R✓ | P✗ R✗ |
|---|---|---|---|---|
| IDENTITY_EQUALITY | 4 | 0 | 0 | 0 |
| CURRENTNESS | 2 | 2 | 0 | 0 |
| KNOWN_VS_UNKNOWN | 2 | 2 | 0 | 0 |
| CONTRADICTION | 3 | 1 | 0 | 0 |
| ALTERNATIVE_COMPLETION_EXISTENCE | 2 | 2 | 0 | 0 |
| OBSERVATION_REQUIREMENT_COMPARISON | 3 | 1 | 0 | 0 |
| EVIDENCE_SUFFICIENCY | 0 | 4 | 0 | 0 |

Diagnostic-changing pairs only:

| Family | P✓ R✓ | P✓ R✗ | P✗ R✓ | P✗ R✗ |
|---|---|---|---|---|
| IDENTITY_EQUALITY | 2 | 0 | 0 | 0 |
| CURRENTNESS | 1 | 2 | 0 | 0 |
| KNOWN_VS_UNKNOWN | 2 | 0 | 0 | 0 |
| CONTRADICTION | 3 | 1 | 0 | 0 |
| ALTERNATIVE_COMPLETION_EXISTENCE | 1 | 1 | 0 | 0 |
| OBSERVATION_REQUIREMENT_COMPARISON | 2 | 0 | 0 | 0 |
| EVIDENCE_SUFFICIENCY | 0 | 4 | 0 | 0 |

Across-family association counts are descriptive only:

| Outcome | States | Pairs |
|---|---|---|
| P_correct_R_correct | 41 | 16 |
| P_correct_R_wrong | 15 | 12 |
| P_wrong_R_correct | 0 | 0 |
| P_wrong_R_wrong | 0 | 0 |

Exact memberships are retained in scores.json. These counts are not causal contributions and are not a pooled intelligence score.

## Detailed primitive endpoint and pair tables

### IDENTITY_EQUALITY

Endpoint accuracy 8/8; schema-valid 8/8; directional pair passes 4/4; gate ESTABLISHED.

Error categories: `{}`. Missing/invalid endpoint IDs: `[]`.

| State | Pair side | Primitive gold | Primitive selected | P correct | Reduction gold | Reduction selected | R correct |
|---|---|---|---|---|---|---|---|
| s6cdeffc06513 | A | same_referent=true, equal_value=true | same_referent=true, equal_value=true | ✓ | T | T | ✓ |
| s0f8ca39efe1a | B | same_referent=false, equal_value=true | same_referent=false, equal_value=true | ✓ | T | T | ✓ |
| s9a67fca88b40 | A | same_referent=false, equal_value=false | same_referent=false, equal_value=false | ✓ | T | T | ✓ |
| s86867ae27e30 | B | same_referent=true, equal_value=false | same_referent=true, equal_value=false | ✓ | X | X | ✓ |
| s9dd0670c8d6e | A | same_referent=true, equal_value=true | same_referent=true, equal_value=true | ✓ | D | D | ✓ |
| s9a4508a6b7ca | B | same_referent=true, equal_value=false | same_referent=true, equal_value=false | ✓ | X | X | ✓ |
| see461eaf3749 | A | same_referent=false, equal_value=false | same_referent=false, equal_value=false | ✓ | H | H | ✓ |
| s0a88b08259e2 | B | same_referent=false, equal_value=true | same_referent=false, equal_value=true | ✓ | H | H | ✓ |

| Pair | P selected A → B | P pass | R selected A → B | Gold class flips | R exact pair | Other changed primitives |
|---|---|---|---|---|---|---|
| pcb75442d46cf | same_referent=true, equal_value=true → same_referent=false, equal_value=true | ✓ | HISTORICAL_DEFECT_NOT_CURRENT → HISTORICAL_DEFECT_NOT_CURRENT | False | ✓ | None |
| pb83de3daa4c9 | same_referent=false, equal_value=false → same_referent=true, equal_value=false | ✓ | HISTORICAL_DEFECT_NOT_CURRENT → INVALID_OR_CONTRADICTORY_EVIDENCE | True | ✓ | CONTRADICTION |
| p6a9d06a11205 | same_referent=true, equal_value=true → same_referent=true, equal_value=false | ✓ | SUPPORTED_CURRENT_DEFECT → INVALID_OR_CONTRADICTORY_EVIDENCE | True | ✓ | CONTRADICTION |
| pc41b9ceb9742 | same_referent=false, equal_value=false → same_referent=false, equal_value=true | ✓ | NO_SUPPORTED_DIAGNOSIS → NO_SUPPORTED_DIAGNOSIS | False | ✓ | None |

Identity field accuracy: same_referent 8/8; equal_value 8/8. Main gate uses joint exact correctness. Joint confusion uses (same_referent,equal_value).

| Gold \ selected | false,false | false,true | true,false | true,true | INVALID_OUTPUT |
|---|---|---|---|---|---|
| false,false | 2 | 0 | 0 | 0 | 0 |
| false,true | 0 | 2 | 0 | 0 | 0 |
| true,false | 0 | 0 | 2 | 0 | 0 |
| true,true | 0 | 0 | 0 | 2 | 0 |

same_referent confusion:

| Gold \ selected | False | True | INVALID_OUTPUT |
|---|---|---|---|
| False | 4 | 0 | 0 |
| True | 0 | 4 | 0 |

equal_value confusion:

| Gold \ selected | False | True | INVALID_OUTPUT |
|---|---|---|---|
| False | 4 | 0 | 0 |
| True | 0 | 4 | 0 |

### CURRENTNESS

Endpoint accuracy 8/8; schema-valid 8/8; directional pair passes 4/4; gate ESTABLISHED.

Error categories: `{}`. Missing/invalid endpoint IDs: `[]`.

| State | Pair side | Primitive gold | Primitive selected | P correct | Reduction gold | Reduction selected | R correct |
|---|---|---|---|---|---|---|---|
| scba9cc461d2b | A | CURRENT | CURRENT | ✓ | D | D | ✓ |
| s6e13e0d63044 | B | NOT_CURRENT | NOT_CURRENT | ✓ | T | T | ✓ |
| s45f64a8ae9fd | A | CURRENT | CURRENT | ✓ | D | D | ✓ |
| sb7e1cc7ef7e3 | B | NOT_CURRENT | NOT_CURRENT | ✓ | H | T | ✗ |
| sccf2acfbfa18 | A | CURRENT | CURRENT | ✓ | U | H | ✗ |
| s0bf0c65011cf | B | NOT_CURRENT | NOT_CURRENT | ✓ | H | H | ✓ |
| s915d60919d64 | A | CURRENT | CURRENT | ✓ | X | X | ✓ |
| s839c64090ee5 | B | NOT_CURRENT | NOT_CURRENT | ✓ | X | X | ✓ |

| Pair | P selected A → B | P pass | R selected A → B | Gold class flips | R exact pair | Other changed primitives |
|---|---|---|---|---|---|---|
| p9147188c88d5 | CURRENT → NOT_CURRENT | ✓ | SUPPORTED_CURRENT_DEFECT → HISTORICAL_DEFECT_NOT_CURRENT | True | ✓ | None |
| p54186fe7d147 | CURRENT → NOT_CURRENT | ✓ | SUPPORTED_CURRENT_DEFECT → HISTORICAL_DEFECT_NOT_CURRENT | True | ✗ | None |
| p6573d8bb3bcc | CURRENT → NOT_CURRENT | ✓ | NO_SUPPORTED_DIAGNOSIS → NO_SUPPORTED_DIAGNOSIS | True | ✗ | EVIDENCE_SUFFICIENCY |
| p4448c687622e | CURRENT → NOT_CURRENT | ✓ | INVALID_OR_CONTRADICTORY_EVIDENCE → INVALID_OR_CONTRADICTORY_EVIDENCE | False | ✓ | None |

Primitive confusion:

| Gold \ selected | CURRENT | NOT_CURRENT | INVALID_OUTPUT |
|---|---|---|---|
| CURRENT | 4 | 0 | 0 |
| NOT_CURRENT | 0 | 4 | 0 |

### KNOWN_VS_UNKNOWN

Endpoint accuracy 8/8; schema-valid 8/8; directional pair passes 4/4; gate ESTABLISHED.

Error categories: `{}`. Missing/invalid endpoint IDs: `[]`.

| State | Pair side | Primitive gold | Primitive selected | P correct | Reduction gold | Reduction selected | R correct |
|---|---|---|---|---|---|---|---|
| s0d42cacc76e1 | A | KNOWN | KNOWN | ✓ | D | D | ✓ |
| s8eba35a1979e | B | UNKNOWN | UNKNOWN | ✓ | U | U | ✓ |
| sea9358dce992 | A | KNOWN | KNOWN | ✓ | H | H | ✓ |
| sacf7733e9675 | B | UNKNOWN | UNKNOWN | ✓ | U | U | ✓ |
| s2bb230536616 | A | KNOWN | KNOWN | ✓ | T | D | ✗ |
| s3d1adf0ce938 | B | UNKNOWN | UNKNOWN | ✓ | T | D | ✗ |
| s5a4643f8f3d5 | A | KNOWN | KNOWN | ✓ | D | D | ✓ |
| s134eea583827 | B | UNKNOWN | UNKNOWN | ✓ | D | U | ✗ |

| Pair | P selected A → B | P pass | R selected A → B | Gold class flips | R exact pair | Other changed primitives |
|---|---|---|---|---|---|---|
| pfe5134c8aba6 | KNOWN → UNKNOWN | ✓ | SUPPORTED_CURRENT_DEFECT → INSUFFICIENT_EVIDENCE | True | ✓ | ALTERNATIVE_COMPLETION_EXISTENCE, EVIDENCE_SUFFICIENCY |
| pfea0877e44e6 | KNOWN → UNKNOWN | ✓ | NO_SUPPORTED_DIAGNOSIS → INSUFFICIENT_EVIDENCE | True | ✓ | ALTERNATIVE_COMPLETION_EXISTENCE, EVIDENCE_SUFFICIENCY |
| p85beaefc6d27 | KNOWN → UNKNOWN | ✓ | SUPPORTED_CURRENT_DEFECT → SUPPORTED_CURRENT_DEFECT | False | ✗ | ALTERNATIVE_COMPLETION_EXISTENCE |
| p3b126a65a170 | KNOWN → UNKNOWN | ✓ | SUPPORTED_CURRENT_DEFECT → INSUFFICIENT_EVIDENCE | False | ✗ | ALTERNATIVE_COMPLETION_EXISTENCE |

Primitive confusion:

| Gold \ selected | KNOWN | UNKNOWN | INVALID_OUTPUT |
|---|---|---|---|
| KNOWN | 4 | 0 | 0 |
| UNKNOWN | 0 | 4 | 0 |

### CONTRADICTION

Endpoint accuracy 8/8; schema-valid 8/8; directional pair passes 4/4; gate ESTABLISHED.

Error categories: `{}`. Missing/invalid endpoint IDs: `[]`.

| State | Pair side | Primitive gold | Primitive selected | P correct | Reduction gold | Reduction selected | R correct |
|---|---|---|---|---|---|---|---|
| sa7bd8a6a8528 | A | CONSISTENT | CONSISTENT | ✓ | T | T | ✓ |
| s05ec96a2a6dc | B | CONTRADICTORY | CONTRADICTORY | ✓ | X | X | ✓ |
| s6dfa7b546adb | A | CONSISTENT | CONSISTENT | ✓ | T | H | ✗ |
| s42de03a09167 | B | CONTRADICTORY | CONTRADICTORY | ✓ | X | X | ✓ |
| s2697ff347b99 | A | CONSISTENT | CONSISTENT | ✓ | T | T | ✓ |
| s04e9ee967879 | B | CONTRADICTORY | CONTRADICTORY | ✓ | X | X | ✓ |
| sb8f321279191 | A | CONSISTENT | CONSISTENT | ✓ | H | H | ✓ |
| s0f2956ae97be | B | CONTRADICTORY | CONTRADICTORY | ✓ | X | X | ✓ |

| Pair | P selected A → B | P pass | R selected A → B | Gold class flips | R exact pair | Other changed primitives |
|---|---|---|---|---|---|---|
| pe769b04b8bb4 | CONSISTENT → CONTRADICTORY | ✓ | HISTORICAL_DEFECT_NOT_CURRENT → INVALID_OR_CONTRADICTORY_EVIDENCE | True | ✓ | IDENTITY_EQUALITY |
| p1b34b0fb1fdb | CONSISTENT → CONTRADICTORY | ✓ | NO_SUPPORTED_DIAGNOSIS → INVALID_OR_CONTRADICTORY_EVIDENCE | True | ✗ | IDENTITY_EQUALITY |
| pe89e1cbd08fd | CONSISTENT → CONTRADICTORY | ✓ | HISTORICAL_DEFECT_NOT_CURRENT → INVALID_OR_CONTRADICTORY_EVIDENCE | True | ✓ | IDENTITY_EQUALITY |
| p9b6e9ea58666 | CONSISTENT → CONTRADICTORY | ✓ | NO_SUPPORTED_DIAGNOSIS → INVALID_OR_CONTRADICTORY_EVIDENCE | True | ✓ | IDENTITY_EQUALITY |

Primitive confusion:

| Gold \ selected | CONSISTENT | CONTRADICTORY | INVALID_OUTPUT |
|---|---|---|---|
| CONSISTENT | 4 | 0 | 0 |
| CONTRADICTORY | 0 | 4 | 0 |

### ALTERNATIVE_COMPLETION_EXISTENCE

Endpoint accuracy 8/8; schema-valid 8/8; directional pair passes 4/4; gate ESTABLISHED.

Error categories: `{}`. Missing/invalid endpoint IDs: `[]`.

| State | Pair side | Primitive gold | Primitive selected | P correct | Reduction gold | Reduction selected | R correct |
|---|---|---|---|---|---|---|---|
| sd96aa46e6676 | A | NO_ALTERNATIVE | NO_ALTERNATIVE | ✓ | H | H | ✓ |
| saf58342c12c0 | B | ALTERNATIVE_EXISTS | ALTERNATIVE_EXISTS | ✓ | H | H | ✓ |
| sfb25a574ca20 | A | NO_ALTERNATIVE | NO_ALTERNATIVE | ✓ | D | D | ✓ |
| s7702e20ad7b4 | B | ALTERNATIVE_EXISTS | ALTERNATIVE_EXISTS | ✓ | D | U | ✗ |
| s0765f4605459 | A | NO_ALTERNATIVE | NO_ALTERNATIVE | ✓ | H | H | ✓ |
| s69eb6a090d10 | B | ALTERNATIVE_EXISTS | ALTERNATIVE_EXISTS | ✓ | U | U | ✓ |
| s05ba8d17548c | A | NO_ALTERNATIVE | NO_ALTERNATIVE | ✓ | D | U | ✗ |
| sab307858b73d | B | ALTERNATIVE_EXISTS | ALTERNATIVE_EXISTS | ✓ | U | H | ✗ |

| Pair | P selected A → B | P pass | R selected A → B | Gold class flips | R exact pair | Other changed primitives |
|---|---|---|---|---|---|---|
| pe6150a0d0f53 | NO_ALTERNATIVE → ALTERNATIVE_EXISTS | ✓ | NO_SUPPORTED_DIAGNOSIS → NO_SUPPORTED_DIAGNOSIS | False | ✓ | KNOWN_VS_UNKNOWN |
| p290c1440f38a | NO_ALTERNATIVE → ALTERNATIVE_EXISTS | ✓ | SUPPORTED_CURRENT_DEFECT → INSUFFICIENT_EVIDENCE | False | ✗ | KNOWN_VS_UNKNOWN |
| p09c35169512d | NO_ALTERNATIVE → ALTERNATIVE_EXISTS | ✓ | NO_SUPPORTED_DIAGNOSIS → INSUFFICIENT_EVIDENCE | True | ✓ | KNOWN_VS_UNKNOWN, EVIDENCE_SUFFICIENCY |
| p8205c60fcc6a | NO_ALTERNATIVE → ALTERNATIVE_EXISTS | ✓ | INSUFFICIENT_EVIDENCE → NO_SUPPORTED_DIAGNOSIS | True | ✗ | KNOWN_VS_UNKNOWN, EVIDENCE_SUFFICIENCY |

Primitive confusion:

| Gold \ selected | ALTERNATIVE_EXISTS | NO_ALTERNATIVE | INVALID_OUTPUT |
|---|---|---|---|
| ALTERNATIVE_EXISTS | 4 | 0 | 0 |
| NO_ALTERNATIVE | 0 | 4 | 0 |

### OBSERVATION_REQUIREMENT_COMPARISON

Endpoint accuracy 8/8; schema-valid 8/8; directional pair passes 4/4; gate ESTABLISHED.

Error categories: `{}`. Missing/invalid endpoint IDs: `[]`.

| State | Pair side | Primitive gold | Primitive selected | P correct | Reduction gold | Reduction selected | R correct |
|---|---|---|---|---|---|---|---|
| s2dcbcbc31e7d | A | MATCH | MATCH | ✓ | H | H | ✓ |
| s299b5eeddb41 | B | MISMATCH | MISMATCH | ✓ | D | D | ✓ |
| s37bc9fbd4c28 | A | MATCH | MATCH | ✓ | H | H | ✓ |
| s95eb3f9311a7 | B | MISMATCH | MISMATCH | ✓ | T | T | ✓ |
| s7074290a7c0e | A | MATCH | MATCH | ✓ | U | U | ✓ |
| sb576e9584f1c | B | MISMATCH | MISMATCH | ✓ | U | T | ✗ |
| sf759b3af8e75 | A | MATCH | MATCH | ✓ | X | X | ✓ |
| sefdd360d92e4 | B | MISMATCH | MISMATCH | ✓ | X | X | ✓ |

| Pair | P selected A → B | P pass | R selected A → B | Gold class flips | R exact pair | Other changed primitives |
|---|---|---|---|---|---|---|
| pa7fdd2bdb981 | MATCH → MISMATCH | ✓ | NO_SUPPORTED_DIAGNOSIS → SUPPORTED_CURRENT_DEFECT | True | ✓ | None |
| p869553eb45c8 | MATCH → MISMATCH | ✓ | NO_SUPPORTED_DIAGNOSIS → HISTORICAL_DEFECT_NOT_CURRENT | True | ✓ | None |
| pc4e6e87979b9 | MATCH → MISMATCH | ✓ | INSUFFICIENT_EVIDENCE → HISTORICAL_DEFECT_NOT_CURRENT | False | ✗ | None |
| p9464ebed4ef3 | MATCH → MISMATCH | ✓ | INVALID_OR_CONTRADICTORY_EVIDENCE → INVALID_OR_CONTRADICTORY_EVIDENCE | False | ✓ | None |

Primitive confusion:

| Gold \ selected | MATCH | MISMATCH | INVALID_OUTPUT |
|---|---|---|---|
| MATCH | 4 | 0 | 0 |
| MISMATCH | 0 | 4 | 0 |

### EVIDENCE_SUFFICIENCY

Endpoint accuracy 8/8; schema-valid 8/8; directional pair passes 4/4; gate ESTABLISHED.

Error categories: `{}`. Missing/invalid endpoint IDs: `[]`.

| State | Pair side | Primitive gold | Primitive selected | P correct | Reduction gold | Reduction selected | R correct |
|---|---|---|---|---|---|---|---|
| s4e4487eb947a | A | DETERMINATE | DETERMINATE | ✓ | H | H | ✓ |
| s3619d857b3d1 | B | UNDERDETERMINED | UNDERDETERMINED | ✓ | U | H | ✗ |
| s88cda4031925 | A | DETERMINATE | DETERMINATE | ✓ | D | U | ✗ |
| sfea7d23cd93b | B | UNDERDETERMINED | UNDERDETERMINED | ✓ | U | U | ✓ |
| s8c353e553e52 | A | DETERMINATE | DETERMINATE | ✓ | T | H | ✗ |
| s059455a331cf | B | UNDERDETERMINED | UNDERDETERMINED | ✓ | U | T | ✗ |
| s93bb85d7f07a | A | DETERMINATE | DETERMINATE | ✓ | D | U | ✗ |
| se8ae05e202d5 | B | UNDERDETERMINED | UNDERDETERMINED | ✓ | U | U | ✓ |

| Pair | P selected A → B | P pass | R selected A → B | Gold class flips | R exact pair | Other changed primitives |
|---|---|---|---|---|---|---|
| pf2edb8d17b19 | DETERMINATE → UNDERDETERMINED | ✓ | NO_SUPPORTED_DIAGNOSIS → NO_SUPPORTED_DIAGNOSIS | True | ✗ | None |
| p2d668f50a4c4 | DETERMINATE → UNDERDETERMINED | ✓ | INSUFFICIENT_EVIDENCE → INSUFFICIENT_EVIDENCE | True | ✗ | None |
| pb9fcb5be062e | DETERMINATE → UNDERDETERMINED | ✓ | NO_SUPPORTED_DIAGNOSIS → HISTORICAL_DEFECT_NOT_CURRENT | True | ✗ | None |
| p05e943ec08b0 | DETERMINATE → UNDERDETERMINED | ✓ | INSUFFICIENT_EVIDENCE → INSUFFICIENT_EVIDENCE | True | ✗ | None |

Primitive confusion:

| Gold \ selected | DETERMINATE | UNDERDETERMINED | INVALID_OUTPUT |
|---|---|---|---|
| DETERMINATE | 4 | 0 | 0 |
| UNDERDETERMINED | 0 | 4 | 0 |

## Coupling, interpretation and limitations

All 28 pair audits, exact JSON deltas, gold transitions and seven-primitive truth vectors are in [pair-coupling-audit.md](pair-coupling-audit.md). Fifteen pairs necessarily couple primitives; thirteen preserve all six non-target judgments. These were frozen before inference.

Registered interpretation: `PRIMITIVES_ESTABLISHED_REDUCTION_NOT_ESTABLISHED` (category A). Failed primitive gates: None.

Failed primitive with a matching reduction subset meeting the preregistered descriptive 7/8-and-3/4 criterion: None. This subset check does not replace the global reduction gate.

The [capability boundary](capability-boundary.md) answers all ten scientific questions and distinguishes observed model capability, deterministic benchmark machinery and combined-system capability NOT TESTED.

## Audit and replay

- 44 zero-model qualification tests passed; all 395 generated files reproduced exactly.
- Freshness/leakage PASS: 2,116 prior files and 1,344 JSON files audited; 170 fresh symbolic input/output values; 196 fresh IDs; no copied exact state/subject/trial/table or complete prior user prompt.
- The seven epistemic concepts and class ontology are intentional reuse. [freshness-review.md](freshness-review.md) documents semantic review and limits of the novelty claim.
- P/R state bytes are identical at every endpoint. No primitive vector, answer, gold or helper conclusion enters a model input. The existing compiler is unused.
- Raw-first checks: 112 completions, 112 slot erasures, 227 successful controls and 226 hashed read-only raw artifacts; server shutdown and zero retries/repairs/critics verified.
- Preservation PASS: 3,141 inherited files, twenty protected local heads and twenty protected remote heads. No prior study, Memory, policy, threshold, weights or Horus architecture changed.
- Byte-identical scorer replay without inference: PASS. Score SHA256 `5dd018b316230b8126c0e6eefe86363d6983f3dc179b934f4b4735119edfd99b`.
- Full reachable-history publication audit uses unchanged rules and excludes private archive ancestry. Only the new branch is pushed; exact final remote SHA is verified after publication and reported in the handoff.

All 112 calls ended normally without completion truncation. Five primitive envelopes omitted the optional separate reasoning_content field; the other 107 supplied separated reasoning strings. No reasoning-channel markers appeared in the five short finals, and the frozen transport allows this absence. The runtime configuration remained unchanged. Execution metadata are recorded in execution-profile.json and channel-presence checks in postflight.json. Private native reasoning is non-authoritative and remains outside public history. No comparator, intervention or subsequent study is run.
