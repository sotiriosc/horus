# Representation priors and neutrality — interpretation checkpoint

Parent: `492d257e2c999ab167050353cba43a3fbeb7f9a5`. This checkpoint interprets existing evidence only: **zero new model calls**, no new Explorer token-bias experiment, and no historical result changed. Scope is the pinned dolphin-mixtral:latest / Ollama 0.1.16 task family, not a population of models.

## What the evidence establishes

There is no demonstrated representation-free proposal interface in these studies. Semantic names, opaque aliases/token identities and presentation positions can materially change this model's proposals despite unchanged underlying verified evidence. **OPAQUE != NEUTRAL. SEMANTIC != PURE VALUE REPRESENTATION.** No tested rendering established representation-independent neutrality. This does not establish that absolute neutrality is impossible in principle, nor identify an intrinsic token mechanism.

### Semantic-prior v0

The [original report](model-explorer-semantic-prior-study-v0-results.md), [compact results](../experiments/model_explorer_semantic_prior_study_v0/results.json) and [frozen criteria](model-explorer-semantic-prior-study-v0-preregistration.md) at `de3048ea6061ae6b7b26ac95d3a06441bba9d1b9` document 288 real calls. When RETREAT was verified best, original semantic naming interfered strongly (7/36 best-action choices versus 32/36 under opaque rendering). Opaque rendering improved +1>0 selection from 18/36 to 31/36 and +1>−1 from 28/36 to 36/36, meeting the registered surface-effect criteria. Opaque 0>−1 choices always selected the first displayed option, producing 18/36 higher-value choices. The earlier aggregate 0>−1 surface effect remained **NOT ESTABLISHED**. Opacity improved some value-following while exposing presentation effects; it did not establish neutrality.

### Prior-factorial v1

The [report](model-explorer-prior-factorial-v1-results.md), [compact results](../experiments/model_explorer_prior_factorial_v1/results.json) and [criteria](model-explorer-prior-factorial-v1-preregistration.md) at `4a25129948e7eb57917cefae1af2e3fd0f1235e9` document 216 calls with independently crossed option/evidence positions. RETREAT lexical interference replicated in both positive targets and both opaque families. Higher-value counts S/O1/O2 were 0/22/22 of 24 for +1>0, 2/24/23 for +1>−1, and 0/18/13 for 0>−1.

**+1>−1 was the only tested relation stable across both opaque families and every crossed option/evidence-position cell** under the frozen rule (≥5/6 per cell). It was not stable across all representations, because semantic-label behavior remained weak. +1>0 had strong opaque marginal rates but failed position stability. Target C (0>−1) remained **UNRESOLVED** under all registered dominance classifications. The narrower O2 option-position effect was supported; no evidence-position effect met the separately frozen conditioned rule. O1's observed joint-position pattern remains descriptive, not a promoted dominance claim. The 18/24 versus 13/24 vocabulary contrast itself remained **NOT ESTABLISHED** under its frozen criterion (seven favorable discordances, fewer than eight). These qualifications must remain attached to the numbers.

### Contradiction-revision v1

The [report](model-explorer-contradiction-revision-v1-results.md), [compact results](../experiments/model_explorer_contradiction_revision_v1/results.json), [prospective schedule/prompt hashes](../experiments/model_explorer_contradiction_revision_v1/registration-digests.json) and [criteria](model-explorer-contradiction-revision-v1-preregistration.md) at `492d257e2c999ab167050353cba43a3fbeb7f9a5` preserve the 144-call result exactly. O1 satisfied every criterion: SHIFT H0 HOLD 12/12, SHIFT H2 ADVANCE 11/12, CONTROL H2 HOLD 12/12, favorable H2 pairs 11/12, reverse 0. O2 had 10/12, 8/12, 11/12, favorable 7/12 and reverse 0. O2 missed the ≥9 SHIFT-H2 and ≥8 favorable-pair requirements. **Overall contradiction-driven behavioral revision remained NOT ESTABLISHED**, because both families were required independently. Framework integrity passed; the lack of behavioral replication did not invalidate authenticated history.

## Recorded O2 M4/Z2 pattern — descriptive only

The existing H2 transcript was inspected without new calls. Entries below identify actual registered schedule IDs (seed=40001+j), complete mappings and offered order; canonical interpretation is evaluator-side only. Both arms had matched mapping/order/seed and differed only in verified historical consequences. Full exact-response evidence remains privately retained; its original hash is in the linked compact results under `evidence_sha256.model-calls.jsonl`. The table is a small descriptive extraction, not a replacement result or a new hypothesis test.

| j | Q7 / M4 / Z2 map to | Offered order | CONTROL H2 response | SHIFT H2 response |
|---:|---|---|---|---|
| 4 | RETREAT / ADVANCE / HOLD | Z2, M4 | Z2 = HOLD | M4 = ADVANCE |
| 10 | RETREAT / ADVANCE / HOLD | M4, Z2 | Z2 = HOLD | M4 = ADVANCE |
| 5 | RETREAT / HOLD / ADVANCE | M4, Z2 | M4 = HOLD | M4 = HOLD |
| 11 | RETREAT / HOLD / ADVANCE | Z2, M4 | M4 = HOLD | M4 = HOLD |

When this M4/Z2 pair was offered, SHIFT H2 selected M4 in all four recorded schedules: it was ADVANCE (the revised direction) at j=4/10 and HOLD (a miss) at j=5/11, spanning both option orders. CONTROL selected underlying HOLD in all four and therefore changed its surface response with the mapping. Two of O2's four SHIFT-H2 misses are j=5/11; the others are j=0 (M4=HOLD versus Q7=ADVANCE) and j=3 (Q7=HOLD versus Z2=ADVANCE). CONTROL's sole H2 ADVANCE choice is j=7, where SHIFT also chose ADVANCE; that pair supplies no favorable discordance.

This schedule structure is **consistent with residual surface-token/presentation dependence** and gives a concrete future revisit target. It does **not** establish intrinsic M4 preference: the sample is small, alias assignments and seeds are not independently separated here, and this extraction was not a preregistered token-effect test. It does not upgrade the original failed overall replication criterion or the earlier factorial vocabulary-effect result.

## Standing methodological rule

**REPRESENTATION IS AN EXPERIMENTAL VARIABLE.** When the behavioral claim warrants it:

- Use more than one rendering where practical and rotate mappings prospectively.
- Separate option position from evidence position when relevant.
- Do not assume opaque symbols erase priors.
- Distinguish relational-value robustness from rendering-specific behavior.
- Require cross-representation replication only when specified prospectively; never add it retroactively to reinterpret an earlier result.

Controls should be proportional to the claim. This is not a demand for endless alias studies before every new capability experiment.

## Neutrality principle

The goal need not be a symbol with “no prior.” Transform the rendering and ask which behavioral relation survives. Stability across materially different renderings is stronger evidence than one vocabulary alone. Failure of stability does not make the underlying verified observations false; it may reflect competition between verified experience and prior representational structure. The internal mechanism is not established by these behavioral contrasts.

## Revisit triggers and stopping principle

Return to this question when a key result depends on one family but not another; another model has substantially different rendering sensitivity; Map/Recovery studies become dominated by token identity; deployment requires rendering robustness; cross-model comparisons need equivalent interfaces; or a safety-relevant decision changes materially under harmless renaming. A trigger motivates a bounded research decision, not an automatic new campaign.

“Demanding confirmation can itself become the thing requiring correction.”

Likewise, demanding ever more representational neutrality can stop increasing knowledge and merely postpone the next substantive capability test. Once dependence is measured, bounded, documented and included as a limitation, proceed unless it prevents interpretation of the next question. The initial Map-proposal study should retain its two registered families and its prospective replication rule, without launching another neutrality search.

## Status

- Representation dependence: **ESTABLISHED AS A MATERIAL EXPERIMENTAL CONFOUND** for this model/task family.
- Absolute neutrality: **NOT ESTABLISHED**.
- Intrinsic cause of particular token effects: **NOT ESTABLISHED**.
- Need for immediate additional token study: **NO**.
- Revisit conditions: documented above.
