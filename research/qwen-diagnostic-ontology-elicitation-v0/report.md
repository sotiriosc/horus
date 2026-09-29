# Qwen diagnostic ontology elicitation v0

QWEN_DIAGNOSTIC_ONTOLOGY_ELICITATION_COMPLETE_V0

Branch: `research/qwen-diagnostic-ontology-elicitation-v0`. Base: `0193ae2e9241a6675dbb6d61e47feea026bc3e11`.

Method Freeze: `bb0713afeaf2d0c42a6999322f06572e6d974698`. Case Freeze: `44fc16c2830df4e76753c6747a177ff48717fe1d`. Raw pre-scoring commit: `d9df1ee407b79f8e6dd5492f9677248946c32487`. Final publication SHA is the exact remote branch head containing this report; it is reported in the publication handoff (a Git commit cannot contain its own SHA).

Calls attempted/completed: 100/100 of 100. Scientific units: 20 worlds, with five correlated observations each.

## Registered findings

- `MINIMAL_ONTOLOGY_GATE_FAILED`
- `EPISTEMIC_DISTINCTION_GATE_FAILED`
- `ORDER_SENSITIVITY_PRESENT`
- `LABEL_SENSITIVITY_PRESENT`
- `RATIONALE_BURDEN_PRESENT`
- `STRUCTURED_CLASSIFICATION_BURDEN_PRESENT`

## Classification

D=current supported defect; H=no supported diagnosis; U=insufficient evidence; T=historical not current; X=invalid/contradictory package. Every class has four worlds. Primary correctness requires strict JSON and the full arm schema as preregistered.

| Arm | Correct /20 | D /4 | H /4 | U /4 | T /4 | X /4 | U+T+X /12 | Schema /20 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | 16 | 4 | 3 | 3 | 3 | 3 | 9 | 20 |
| B | 12 | 4 | 2 | 1 | 2 | 3 | 6 | 20 |
| C | 16 | 4 | 4 | 3 | 2 | 3 | 8 | 20 |
| D | 12 | 4 | 3 | 2 | 0 | 3 | 5 | 20 |
| E | 12 | 4 | 3 | 1 | 1 | 3 | 5 | 20 |

A=natural class only; B=reversed definitions; C=opaque class labels; D=class plus rationale; E=full R2 schema. A minimal gate is >=17/20 and >=3/4 in every class. Independent epistemic gate is >=10/12 U/T/X.

| Arm | Primitive /10 | Composite /10 |
| --- | --- | --- |
| A | 10 | 6 |
| B | 8 | 4 |
| C | 9 | 7 |
| D | 8 | 4 |
| E | 7 | 5 |

Per-class primitive/composite scores (each cell denominator 2):

| Arm | Class | Primitive /2 | Composite /2 |
| --- | --- | --- | --- |
| A | D | 2 | 2 |
| A | H | 2 | 1 |
| A | U | 2 | 1 |
| A | T | 2 | 1 |
| A | X | 2 | 1 |
| B | D | 2 | 2 |
| B | H | 2 | 0 |
| B | U | 1 | 0 |
| B | T | 1 | 1 |
| B | X | 2 | 1 |
| C | D | 2 | 2 |
| C | H | 2 | 2 |
| C | U | 1 | 2 |
| C | T | 2 | 0 |
| C | X | 2 | 1 |
| D | D | 2 | 2 |
| D | H | 2 | 1 |
| D | U | 2 | 0 |
| D | T | 0 | 0 |
| D | X | 2 | 1 |
| E | D | 2 | 2 |
| E | H | 2 | 1 |
| E | U | 1 | 0 |
| E | T | 0 | 1 |
| E | X | 2 | 1 |

## Matched contrasts

| Contrast | Other minus A /20 | Class disagreements /20 | Correct -> wrong | Wrong -> correct | Wrong -> different wrong | Unchanged |
| --- | --- | --- | --- | --- | --- | --- |
| A vs B | -4 | 6 | 4 | 0 | 2 | 14 |
| A vs C | 0 | 6 | 2 | 2 | 2 | 14 |
| A vs D | -4 | 5 | 4 | 0 | 1 | 15 |
| A vs E | -4 | 9 | 6 | 2 | 1 | 11 |

Order and label sensitivity thresholds are >=4 changed recognized classes. Rationale and structured classification burden thresholds are >=4 fewer primary-correct worlds than A. Missing labels are not counted as semantic class disagreements. Transition categories follow method.md; exact world memberships are in scores.json.

- A_B: disagreement worlds ['w50ad03b1ff9a', 'w6c05ad6d73ce', 'wb2954c1dc4ce', 'wc614d594a5b0', 'wc65d5a638652', 'wd6abcd641feb']; missing-label pairs []; same-label/schema flips [].
- A_C: disagreement worlds ['w50ad03b1ff9a', 'w5bacb9bef603', 'wa959649c47ea', 'wb2954c1dc4ce', 'wb9c8647a850a', 'wc65d5a638652']; missing-label pairs []; same-label/schema flips [].
- A_D: disagreement worlds ['w186968d18fa2', 'w6c05ad6d73ce', 'wa959649c47ea', 'wb9c8647a850a', 'wc614d594a5b0']; missing-label pairs []; same-label/schema flips [].
- A_E: disagreement worlds ['w186968d18fa2', 'w50ad03b1ff9a', 'w5bacb9bef603', 'w6c05ad6d73ce', 'wa959649c47ea', 'wb9c8647a850a', 'wc614d594a5b0', 'wc65d5a638652', 'wd6abcd641feb']; missing-label pairs []; same-label/schema flips [].

## Full structured evidence

All 100 outputs satisfy their arm schemas, so the observed primary accuracy differences arise from selected classifications, not schema rejection.

Arm E full witness success: 1/4 true-current worlds. Joint decisive record + field + observed value + required value localization: 1/4. Required current citation occurrences: 12/12.

| Current-world criterion | Success /4 |
| --- | --- |
| primary_classification | 4 |
| affected_component | 4 |
| citation_complete | 4 |
| contract_evidence_id | 4 |
| cause_evidence_id | 4 |
| effect_evidence_id | 4 |
| decisive_evidence_id | 3 |
| decisive_field | 2 |
| observed_value | 1 |
| required_value | 1 |

Across all E worlds, complete required citation sets: 18/20; required citations present: 62/64; outputs with nonexistent evidence IDs: 0/20. Exact structural criteria only; no rationale, diagnostic prose or private reasoning rescue.

## Interpretation

Arm A fails the registered minimal ontology gate. Full structured-output burden alone therefore does not explain the preserved R2 failures: minimal elicitation also fails under these fresh cases. This does not imply that Qwen has no useful diagnostic reasoning.
The independent U/T/X gate also fails: 9/12 against the fixed 10/12 threshold. Arm A meets the per-class floor (at least 3/4 in each class), but its 16/20 total misses the 17/20 requirement. All four Arm A errors occur on composite worlds; the primitive/composite difference is descriptive.
Diagnostic decisions are materially representation-dependent under this model/interface. The registered contrast identifies sensitivity within these matched cases; it does not allocate causal percentages or establish general model behavior.
The registered pattern is mixed: both semantic and interface factors contribute under the tested conditions. No attribution percentages are estimated.

A threshold not reached means not established, not absence. Primitive/composite comparisons are descriptive only. The twenty worlds do not support general scaling claims. No hybrid architecture or follow-up study was designed or run.

## Runtime, controls and provenance

- Model: Qwen3-14B Q4_K_M; SHA-256 `500a8806e85ee9c83f3ae08420295592451379b4f8cf2d0f41c15dffeb6b81f0`. llama.cpp b11242 / `526c43b8f7dfea9032e9f35e7a1be9183ca7cc20`. Model, server and distribution archive hashes reverified before execution.
- Context 16384; reasoning on/deepseek/512; temperature .2; top_p .9; top_k 40; min_p .05; max_tokens 2048 for every arm. Seed 731926581, distinct from R2 and shared across matched arms. One server/slot, fresh private slot path, erase then inspect before every request; prompt/KV caching disabled. No tools or external model access.
- Five-arm balanced schedule: each arm occupies each within-world position exactly four times. Two independently generated opaque permutations, ten worlds each; assigned before execution. Class-only C retains the A object wrapper to control serialization burden. Both permutations happen to assign T4 to the historical class; independent generation does not guarantee every assignment changes.
- A/B exact sole definition-order delta and A/C exact label-only delta verified. All 123 materialized files regenerate byte-for-byte. Class balance 4 each, primitive/composite 2 each within class. 124 new evidence/component IDs have zero R2 overlap. Arithmetic/provenance construction checks and template-by-template mechanism comparison support novelty; byte non-overlap alone is not a semantic proof. Ontology and generic record grammar are explicitly reused.
- No case-specific expected class, mechanism family label, gold witness, compiler output or prior Qwen answer enters a model request. Generator and schedule do not import the scorer; runner never reads gold. R2 outputs were not rescored or rerun.
- 34 zero-model tests passed before Case Freeze, including a full 100-request mock HTTP run, failure stopping, exact dispatch, no retries, strict JSON, witness checks and threshold boundaries. Known pinned grammar limitations remain: Python Draft7, not grammar enforcement alone, determines schema validity.
- Raw-first proof: `d9df1ee407b79f8e6dd5492f9677248946c32487` commits the raw finals and raw-freeze.json before scores.json exists. All 202 raw artifacts hash-verified and read-only; private envelope hashes match completed outputs. Raw finals were not inspected for correctness during execution.
- Exact score replay: byte-identical; SHA-256 `c132dc5bc54d7f97ac116b06dfbcd3611f2dfbd2e849ba9c4ab37cb63a284f9e`. No inference in replay.
- Preservation: 1954 parent files byte-identical; 15 local and 15 remote protected heads unchanged. R2/raw/scores, postmortem, compiler, v0/R1, runtime qualification, earlier Qwen studies, active S/E, Memory, policy and thresholds preserved. Local and remote main remain at their separately recorded pre-existing heads.
- 15 private/archive refs excluded from public ancestry. Private envelopes, reasoning, server logs and slot artifacts are outside the repository; only hashes/sizes are public. Complete reachable-history publication audit is recorded separately, then rerun on the exact final publication head.
- Zero retries, repairs, critics, compiler calls, comparator calls, Horus actions or architecture/policy/model changes. No merge. Publish this branch alone and stop.
