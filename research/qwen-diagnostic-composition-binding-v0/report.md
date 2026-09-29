# Qwen diagnostic composition and binding v0

QWEN_DIAGNOSTIC_COMPOSITION_BINDING_COMPLETE_V0

Branch: `research/qwen-diagnostic-composition-binding-v0`. Base: `827e568a9de26324990ed837a2f773a20d0ff43e`.

Method Freeze: `240f48e62b820259985af89b1138809d42e48534`. Case Freeze: `6e43930058a3a0d9dbb50e5c55556d1780127677`.
Raw commit before scoring: `f17e4053e95219152da6ab6fae733155033e425f`. Final publication SHA is supplied in the publication handoff and verified against this branch's remote head; a Git commit cannot include its own SHA.

Scientific calls: 70 attempted, 70 completed, of 70. Schema-valid finals: 70/70. Part A 50 calls, Part B 20. Units are ten correlated ladders and ten correlated pairs, not seventy independent tasks.

## Registered findings

- `MINIMAL_CORE_COMPETENCE_NOT_ESTABLISHED`
- `COMPOSITIONAL_INVARIANCE_NOT_ESTABLISHED`
- `DECISIVE_COUNTERFACTUAL_SENSITIVITY_NOT_ESTABLISHED`

## Part A: baseline and composition

Class key: D=current supported defect; H=no supported diagnosis; U=insufficient evidence; T=historical not current; X=invalid/contradictory evidence.

| Level | Correct /10 | D /2 | H /2 | U /2 | T /2 | X /2 | Schema /10 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| L0 | 5 | 1 | 1 | 0 | 2 | 1 | 10 |
| L1 | 4 | 1 | 2 | 0 | 0 | 1 | 10 |
| L2 | 2 | 0 | 1 | 0 | 0 | 1 | 10 |
| L3 | 4 | 0 | 2 | 0 | 1 | 1 | 10 |
| L4 | 6 | 2 | 2 | 0 | 1 | 1 | 10 |

L0 gate requires >=9/10 and >=1/2 in every class. Selected-class invariant cores: 3/10. Gold-preserving invariant / correct-at-all-five cores: 1/10, against the fixed >=8/10 gate.

First changed level means first recognized class differing from L0. First incorrect level includes L0. Missing labels are tracked separately and never count as invariance.

| Core | Mechanism | Gold | L0-L4 selected | First changed | First incorrect | First invalid label |
| --- | --- | --- | --- | --- | --- | --- |
| u0563ae27d6b3 | cyclic alphabet substitution | H | D/H/H/H/H | L1 | L0 | none |
| u073cdee833e0 | LIFO stack removal | T | T/U/H/D/D | L1 | L1 | none |
| u1219d4152913 | run-length expansion | D | D/D/U/T/D | L2 | L2 | none |
| u1809f7af1dfe | signed zigzag integer coding | T | T/D/H/T/T | L1 | L1 | none |
| u4028529a5dd9 | literal codeword concatenation | U | D/D/D/D/D | none | L0 | none |
| u8a261494f62d | sentinel octet stuffing | D | H/U/H/H/D | L1 | L0 | none |
| u98cd1c26463e | matrix axis transposition | U | D/D/D/D/D | none | L0 | none |
| ub9fbb567f9bd | Euclidean quotient and residue | X | U/H/H/H/H | L1 | L0 | none |
| uea6e3ce0eafd | lexicographic key canonicalization | X | X/X/X/X/X | none | none | none |
| uf22f3606eead | bitwise XOR whitening | H | H/H/T/H/H | L2 | L2 | none |

## Matched ladder transitions

| Contrast | Correct -> wrong | Wrong -> correct | Wrong -> different wrong | Unchanged | Class disagreements |
| --- | --- | --- | --- | --- | --- |
| L0 -> L1 | 2 | 1 | 2 | 5 | 5 |
| L1 -> L2 | 2 | 0 | 3 | 5 | 5 |
| L2 -> L3 | 0 | 2 | 2 | 6 | 4 |
| L3 -> L4 | 0 | 2 | 0 | 8 | 2 |
| L0 -> L4 | 1 | 2 | 1 | 6 | 4 |

Exact core memberships, missing-label pairs and schema flips are retained in scores.json. Changes are matched, never independent-sample comparisons.

Aggregate level accuracy is not monotonic: [5, 4, 2, 4, 6]. No monotonic complexity degradation is claimed.

## Part B: decisive sensitivity

Endpoint accuracy: 12/20. Pair passes: 4/10. A pair requires both correct endpoints and the required class change. Gate: >=8/10 pairs and >=1/2 in every contrast.

| Contrast | Pair passes /2 |
| --- | --- |
| H_D | 1 |
| H_U | 0 |
| D_T | 1 |
| H_X | 1 |
| U_D | 1 |

| Pair | Contrast | Gold A/B | Selected A/B | Pass |
| --- | --- | --- | --- | --- |
| u06bf9798528e | H_U | H/U | T/H | False |
| u160a48853b52 | H_D | H/D | H/D | True |
| u2a1e70b9cba7 | H_X | H/X | H/T | False |
| u383e79d99206 | H_D | H/D | T/T | False |
| u4d9ce97bf19f | U_D | U/D | U/D | True |
| u74bbfc5ce7f1 | D_T | D/T | D/T | True |
| u80ad2516f7d1 | H_X | H/X | H/X | True |
| u80f17f629701 | H_U | H/U | D/U | False |
| ua7e435ac2c53 | U_D | U/D | D/D | False |
| uc53c91ee87ff | D_T | D/T | D/H | False |

## Binding tags: descriptive only

| Added-level tag | Level accuracy /10 | Adjacent stable /10 | Correct at both /10 |
| --- | --- | --- | --- |
| COMPONENT_BINDING | 4 | 5 | 3 |
| VERSION_BINDING | 2 | 5 | 2 |
| REDUNDANT_EVIDENCE | 4 | 6 | 2 |
| TARGET_VS_DISTRACTOR | 6 | 8 | 4 |

| Flip tag | Endpoint accuracy | Class-changing pairs | Pair passes |
| --- | --- | --- | --- |
| CURRENTNESS | 3/4 | 2/2 | 1/2 |
| PROVENANCE_IDENTITY | 3/4 | 2/2 | 1/2 |
| UNKNOWN_DEPENDENCY | 4/8 | 3/4 | 1/4 |
| VALUE_DEPENDENCY | 2/4 | 1/2 | 1/2 |

Tags were assigned before inference, excluded from prompts and not used to generate gold. UNKNOWN_DEPENDENCY covers both H_U and U_D, four pairs total. No tag-specific significance threshold or causal attribution is introduced.

## Registered interpretation

- B_WEAK_CORES: L0 competence is not established. The limitation is not attributable solely to added composition; failures cannot primarily be attributed to distractors from this study.
- D_BOTH_WEAK: Both preservation under complexity and response to decisive changes are unreliable under the registered gates.

These internally authored research-program cases are not independently authored external tasks. The study measures transfer to prospectively frozen fresh mechanisms, not open-world generalization. Ten mechanisms are reused across independently parameterized Part A/Part B domains, so mechanism-level observations are also related. No overall intelligence score, general scaling claim or attribution percentages.

## Verification and preservation

- Runtime hashes verified for Qwen3-14B Q4_K_M (`500a8806e85ee9c83f3ae08420295592451379b4f8cf2d0f41c15dffeb6b81f0`), llama.cpp b11242 (`526c43b8f7dfea9032e9f35e7a1be9183ca7cc20`), installed server and distribution archives. Context 16384; reasoning on/deepseek/512; temp .2; top_p .9; top_k 40; min_p .05; max_tokens 2048; seed 384206917. All calls share the new seed and fixed minimal natural-label interface.
- One server start, one slot, fresh private slot-save-path; erase and idle inspection before every request. Prompt/KV caching disabled; no tools, model web/filesystem/repository access or history. No prior answer enters another call.
- 36 zero-model tests passed before Case Freeze, including full 70-request mock HTTP execution, no-retry failure paths, strict JSON, missing-label invariance, threshold boundaries, first failure/change and independent operation vectors.
- All 70 gold classifications independently checked mechanically before inference; author proof records cite contracts, decisive facts, current receipts and compatible/excluded alternatives. A pre-Case-Freeze author-proof display correction aligned D_T proofs to the deployed receipt; no evidence or request byte changed.
- Ten ladders pass additive-only canonical comparison; target scope and decisive records remain unchanged across all five levels. Every one of ten pairs differs at exactly its declared scalar JSON leaf, and both endpoint gold classes are independently verified. Canonical comparison is offline auditing only; it does not preprocess model input.
- All 213 materialized files regenerate exactly. No prior world/record IDs, evidence objects, operational contracts, mechanism labels or decisive tuples were reused. The 386 new record/component/capture IDs have zero prior overlap. Semantic novelty combines mechanism review and mechanical checks; exact-byte non-overlap alone is not a proof of semantic novelty. Ontology/class definitions are intentionally reused.
- No gold, author proof, level name or binding tag enters a request. Schedule has no scorer dependency. Seventy model-neutral message/schema tasks preserve identical semantic content for a possible future separately authorized comparator; none was executed.
- Ten seven-call blocks each contain five Part A calls (one per class and one per complexity level) and one Part B pair. Every contrast occurs once per five-block half. Five pairs A-first, five B-first; B position counts are 3/3/3/2/3/3/3. Part B class totals H6 D6 U4 T2 X2 follow the required pair families and are not falsely described as equal.
- Raw-first proof: raw freeze was committed before scoring; no correctness inspection during execution. Exact final strings, private full envelopes, request hashes, reasoning hashes only, usage, timing and slot control evidence were preserved. Selected labels were extracted by the frozen scorer after raw commit.
- All 142 raw artifacts hash-verified and read-only; 70 private response hashes verified. Raw reasoning and envelopes remain outside the repository. Score replay is byte-identical, SHA256 `3cdec2ce5978543b3a9bee3ab80c58a087fc21ecb262954d88adbd4c6fa5f592`, with zero model calls.
- 2307 parent files remain byte-identical. All 16 protected local and 16 remote heads preserved: R2, postmortem, compiler, ontology study, v0/R1, runtime qualification, prior Qwen studies, S/E, architecture, Memory/policy/threshold sources. Local and remote main retain their separately recorded pre-existing heads.
- All 15 private/archive refs excluded from reachable public ancestry. Existing full-history publication audit is recorded separately and rerun on the exact final head before pushing only this branch. No merge.
- Zero retries, repairs, critics, evidence-compiler use, comparator calls, Horus actions/changes, training, improvement proposals or intervention design. This externally designed model-behavior study is not Horus learning, self-diagnosis, self-improvement, RSI or architecture improvement.

After publication and exact remote-head verification: STOP.
