# Capability boundary — Diagnostic Reasoning Factorization v0

The registered result is `D_MULTIPLE_ISOLATED_LIMITATIONS`. All four competence gates are NOT ESTABLISHED. Operational computation is substantially stronger than evidence-state construction or epistemic reduction in these cases, but its across-family gate also fails. The evidence does not support a claim that independently reliable diagnostic responsibilities merely fail when composed.

## 1. Can Qwen perform the required operational computations?

Often, under these bounded tasks: 18/20 worlds have both results correct, and 38/40 individual computations are correct. All twenty responses satisfy the schema. Nine operation families score 2/2 worlds and 4/4 individual results. Finite linear convolution scores 0/2 joint worlds and 2/4 individual results. In each convolution world, the first result is correct and the second is wrong.

This clears the registered 17/20 total threshold but fails the required minimum of one jointly correct world in every family. Therefore `OPERATIONAL_COMPUTATION_COMPETENCE_NOT_ESTABLISHED` is the exact gate outcome. It would be misleading either to call the entire operational arm strong under the registered definition or to describe computation as uniformly poor. The observed successes support narrow, case-specific operational ability; two worlds per family do not establish reliable family-wide generalization.

The two final-output mismatches are objectively verifiable. In world wc615b7a5117f, the second expected convolution result is `4,4,7,3`, but Qwen returns `4,5,8,6`. In world w207cc12f3c2e, the second expected result is `-1,-1,10,6`, but Qwen returns `3,-11,2,2`. These are value errors, not reversed result order or invalid JSON.

## 2. Can Qwen construct the relevant evidence state when computation is removed?

Reliable complete state construction is not established: 8/20 whole states are exactly correct, with 18/20 schema-valid responses. Target component and in-service build each score 18/20; all schema-valid responses get these two fields correct. Other-build partition scores 12/20, source knowledge 11/20 and conflicting-capture detection 13/20. The complete nine-field results appear in report.md and scores.json.

The two schema-invalid responses contain duplicate entries: source_knowledge in wcaafc1a41315; capture_groups and source_knowledge in wcde36fb724f5. They remain invalid under the frozen uniqueItems rules and receive no rescued field credit. Ten additional responses are schema-valid but contain at least one incorrect state field. Thus schema duplication alone does not explain the low whole-state result.

The state arm supplied all operational requirements and did not ask for a final class. Its failure shows unreliability on this specified structured state task after computation was supplied. The result does not isolate an internal cognitive cause: reference resolution, coverage of all records, consistency judgments and structured-output discipline remain bundled within this arm. Simpler/composition-dependent whole-state scores are 6/10 and 2/10, descriptive matched-design strata rather than a separate causal experiment.

## 3. Can Qwen make the correct epistemic judgment when bookkeeping/binding is removed?

The registered competence claim is not established: 10/20 correct, all 20 schema-valid. Per-class accuracy is current defect 4/4, no supported diagnosis 2/4, insufficient evidence 2/4, historical defect 2/4 and contradictory evidence 0/4. The U+T+X subset is 4/12, below the descriptive 10/12 check.

These inputs supply independently authored aligned target facts and mechanically computed requirements without opaque record addressing or class-like conclusion flags. Qwen still has to compare observations with requirements, interpret unknown completions and recognize incompatible assertions about the same immutable capture. Performance remains unreliable with these mechanical burdens removed. It is therefore unsupported to claim that the desired epistemic responsibility is already independently demonstrated and only a bookkeeping helper is missing.

All four contradictory-evidence worlds are misclassified: three as historical defect and one as no supported diagnosis. This is a statement about the final answers, not an explanation inferred from private reasoning. Current-defect success on four worlds does not establish the full five-class epistemic capability.

## 4. Can Qwen compose those abilities end-to-end?

Reliable end-to-end diagnosis is not established: 8/20 correct, all twenty schema-valid. Per-class scores are current defect 4/4, no supported diagnosis 3/4, insufficient evidence 1/4, historical defect 0/4 and contradictory evidence 0/4. The U+T+X subset is 1/12. Both the 17/20 total and the 3/4-every-class requirements fail.

Among four worlds with O/S/R all correct, one end-to-end answer is wrong: wcf8ac40be9b1, a historical-defect world. This is a local observation consistent with composition difficulty, not the registered Pattern C: the isolated arms do not pass their overall gates. Conversely, five of eight correct end-to-end answers coexist with an error in at least one isolated arm. That pattern cautions against treating isolated outputs as literal intermediate states of the independent end-to-end call.

R and E select different labels in 12/20 worlds. Three R-correct worlds become E-wrong, one R-wrong world becomes E-correct, and eight change from one wrong label to another. E has two fewer correct worlds overall. No statistical or causal benefit percentage is inferred from these matched observations.

## 5. Which boundaries are established, not established or ambiguous?

**Observed bounded abilities:** Qwen returns correct operational results for 38/40 computations and complete correct states for eight worlds; it correctly diagnoses all four current-defect cases in both R and E. These are observed task successes, not new competence gates or generalization claims.

**Registered competence not established:** all-family operational competence, reliable complete evidence-state construction, reliable five-class epistemic reduction and reliable end-to-end diagnosis. Multiple isolated responsibilities fail their preregistered gates. Even setting aside O's localized convolution failure, both S and R fail; the multiple-limitations conclusion is not driven only by the family floor.

**Ambiguous:** the model's internal cause of any error; how much of S failure comes from binding versus output discipline; the extent to which limited reasoning budget, wording or other frozen runtime choices shape performance; transfer to other families, seeds, models or real-world evidence; any causal decomposition of end-to-end failures. These questions were not identified by this design. There is one sampled call per world/arm, twenty internally authored matched worlds and ten two-world families. Correlations and small per-class denominators constrain inference. There are no registered decisive-change pairs, so sensitivity is NOT_APPLICABLE.

All eighty calls finish normally with `finish_reason=stop`; none reaches the 2048-token completion limit. The state arm uses 1086–1436 completion tokens, including native reasoning; the largest prompt is 3465 tokens, within the 16384-token context. This excludes completion/context truncation as the recorded reason for the two schema failures. It does not test alternative reasoning budgets or settings. No such alternate runs were made.

## Model, software and combined-system capability

**Model capability:** the exact frozen-arm observations above, under Qwen3-14B Q4_K_M and the pinned runtime. No weights or Memory-conditioned behavior changed, and Qwen did not learn from this study.

**Deterministic software capability:** prospective fixture construction, exact operation evaluation, independent gold verification, schema checking, transport preservation and scoring replay succeeded for the specified finite tasks. This verification is evidence about the benchmark machinery. It is not a model capability result, and it does not establish a general-purpose runtime diagnosis system.

**Combined-system capability:** NOT TESTED. No model output was passed to a subsequent stage; no existing evidence compiler was invoked; no helper selected Qwen's final class. Supplying the assigned fixed facts in S/R is the preregistered task manipulation, not an evaluated deployed pipeline. The results do not demonstrate a hybrid repair, Horus self-improvement or RSI progress. Replacing every failed responsibility with deterministic answers would not establish the missing model capability.

The study ends with these responsibility boundaries. No intervention, independent comparator or next study is designed or executed.
