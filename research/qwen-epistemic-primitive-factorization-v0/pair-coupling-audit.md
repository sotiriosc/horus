# Frozen cross-primitive pair coupling audit

All values below were committed in Method/Case Freeze before inference. This rendering introduces no new gold judgments. The offline vectors audit fixture semantics; they are not measured Qwen responses. Each endpoint receives only its designated primitive question and an independent reduction question.

D=current defect; H=no supported diagnosis; U=insufficient evidence; T=historical defect; X=contradictory evidence. Primitive labels refer to their exact frozen scopes. Operational sufficiency uses deployment/trial facts; mark assertions do not constrain operational inputs.

| Pair | Target | Target A → B | Other changed primitives | Class A → B |
|---|---|---|---|---|
| pcb75442d46cf | IDENTITY_EQUALITY | same_referent=true, equal_value=true → same_referent=false, equal_value=true | None | T → T |
| pb83de3daa4c9 | IDENTITY_EQUALITY | same_referent=false, equal_value=false → same_referent=true, equal_value=false | CONTRADICTION | T → X |
| p6a9d06a11205 | IDENTITY_EQUALITY | same_referent=true, equal_value=true → same_referent=true, equal_value=false | CONTRADICTION | D → X |
| pc41b9ceb9742 | IDENTITY_EQUALITY | same_referent=false, equal_value=false → same_referent=false, equal_value=true | None | H → H |
| p9147188c88d5 | CURRENTNESS | answer=current → answer=not_current | None | D → T |
| p54186fe7d147 | CURRENTNESS | answer=current → answer=not_current | None | D → H |
| p6573d8bb3bcc | CURRENTNESS | answer=current → answer=not_current | EVIDENCE_SUFFICIENCY | U → H |
| p4448c687622e | CURRENTNESS | answer=current → answer=not_current | None | X → X |
| pfe5134c8aba6 | KNOWN_VS_UNKNOWN | answer=known → answer=unknown | ALTERNATIVE_COMPLETION_EXISTENCE, EVIDENCE_SUFFICIENCY | D → U |
| pfea0877e44e6 | KNOWN_VS_UNKNOWN | answer=known → answer=unknown | ALTERNATIVE_COMPLETION_EXISTENCE, EVIDENCE_SUFFICIENCY | H → U |
| p85beaefc6d27 | KNOWN_VS_UNKNOWN | answer=known → answer=unknown | ALTERNATIVE_COMPLETION_EXISTENCE | T → T |
| p3b126a65a170 | KNOWN_VS_UNKNOWN | answer=known → answer=unknown | ALTERNATIVE_COMPLETION_EXISTENCE | D → D |
| pe769b04b8bb4 | CONTRADICTION | answer=consistent → answer=contradictory | IDENTITY_EQUALITY | T → X |
| p1b34b0fb1fdb | CONTRADICTION | answer=consistent → answer=contradictory | IDENTITY_EQUALITY | T → X |
| pe89e1cbd08fd | CONTRADICTION | answer=consistent → answer=contradictory | IDENTITY_EQUALITY | T → X |
| p9b6e9ea58666 | CONTRADICTION | answer=consistent → answer=contradictory | IDENTITY_EQUALITY | H → X |
| pe6150a0d0f53 | ALTERNATIVE_COMPLETION_EXISTENCE | answer=no_alternative → answer=alternative_exists | KNOWN_VS_UNKNOWN | H → H |
| p290c1440f38a | ALTERNATIVE_COMPLETION_EXISTENCE | answer=no_alternative → answer=alternative_exists | KNOWN_VS_UNKNOWN | D → D |
| p09c35169512d | ALTERNATIVE_COMPLETION_EXISTENCE | answer=no_alternative → answer=alternative_exists | KNOWN_VS_UNKNOWN, EVIDENCE_SUFFICIENCY | H → U |
| p8205c60fcc6a | ALTERNATIVE_COMPLETION_EXISTENCE | answer=no_alternative → answer=alternative_exists | KNOWN_VS_UNKNOWN, EVIDENCE_SUFFICIENCY | D → U |
| pa7fdd2bdb981 | OBSERVATION_REQUIREMENT_COMPARISON | answer=match → answer=mismatch | None | H → D |
| p869553eb45c8 | OBSERVATION_REQUIREMENT_COMPARISON | answer=match → answer=mismatch | None | H → T |
| pc4e6e87979b9 | OBSERVATION_REQUIREMENT_COMPARISON | answer=match → answer=mismatch | None | U → U |
| p9464ebed4ef3 | OBSERVATION_REQUIREMENT_COMPARISON | answer=match → answer=mismatch | None | X → X |
| pf2edb8d17b19 | EVIDENCE_SUFFICIENCY | answer=determinate → answer=underdetermined | None | H → U |
| p2d668f50a4c4 | EVIDENCE_SUFFICIENCY | answer=determinate → answer=underdetermined | None | D → U |
| pb9fcb5be062e | EVIDENCE_SUFFICIENCY | answer=determinate → answer=underdetermined | None | T → U |
| p05e943ec08b0 | EVIDENCE_SUFFICIENCY | answer=determinate → answer=underdetermined | None | D → U |

Exactly 15 pairs change one or more non-target primitives; 13 preserve all six non-target judgments. Nineteen change the diagnostic class; nine preserve it. No isolated causal attribution is made from a coupled pair.

## Exact deltas and all seven offline judgments

### pcb75442d46cf — IDENTITY_EQUALITY

Change only the second assertion cycle to the next event; agreeing values remain equal.

Exact JSON path: `/assertions/1/subject/cycle`.

Before: `71`. After: `72`.

No non-target primitive truth changes under its frozen scope. Identity/value equality and consistency share the same two immutable mark assertions; changing one can necessarily change whether both assertions coexist.

| Primitive | A gold | B gold | Changed |
|---|---|---|---|
| IDENTITY_EQUALITY | same_referent=true, equal_value=true | same_referent=false, equal_value=true | Yes |
| CURRENTNESS | answer=current | answer=current | No |
| KNOWN_VS_UNKNOWN | answer=known | answer=known | No |
| CONTRADICTION | answer=consistent | answer=consistent | No |
| ALTERNATIVE_COMPLETION_EXISTENCE | answer=no_alternative | answer=no_alternative | No |
| OBSERVATION_REQUIREMENT_COMPARISON | answer=match | answer=match | No |
| EVIDENCE_SUFFICIENCY | answer=determinate | answer=determinate | No |

Five-class gold: HISTORICAL_DEFECT_NOT_CURRENT → HISTORICAL_DEFECT_NOT_CURRENT.

### pb83de3daa4c9 — IDENTITY_EQUALITY

Change only the second station from the annex to the first station, making unequal marks claims about one event.

Exact JSON path: `/assertions/1/subject/station`.

Before: `"birch-mark-stand-annex"`. After: `"birch-mark-stand"`.

Identity/value equality and consistency share the same two immutable mark assertions; changing one can necessarily change whether both assertions coexist.

| Primitive | A gold | B gold | Changed |
|---|---|---|---|
| IDENTITY_EQUALITY | same_referent=false, equal_value=false | same_referent=true, equal_value=false | Yes |
| CURRENTNESS | answer=current | answer=current | No |
| KNOWN_VS_UNKNOWN | answer=known | answer=known | No |
| CONTRADICTION | answer=consistent | answer=contradictory | Yes |
| ALTERNATIVE_COMPLETION_EXISTENCE | answer=no_alternative | answer=no_alternative | No |
| OBSERVATION_REQUIREMENT_COMPARISON | answer=match | answer=match | No |
| EVIDENCE_SUFFICIENCY | answer=determinate | answer=determinate | No |

Five-class gold: HISTORICAL_DEFECT_NOT_CURRENT → INVALID_OR_CONTRADICTORY_EVIDENCE.

### p6a9d06a11205 — IDENTITY_EQUALITY

Change only the second asserted mark value while retaining one immutable referent.

Exact JSON path: `/assertions/1/asserted_value`.

Before: `"ochre-etched"`. After: `"ochre-smooth"`.

Identity/value equality and consistency share the same two immutable mark assertions; changing one can necessarily change whether both assertions coexist.

| Primitive | A gold | B gold | Changed |
|---|---|---|---|
| IDENTITY_EQUALITY | same_referent=true, equal_value=true | same_referent=true, equal_value=false | Yes |
| CURRENTNESS | answer=current | answer=current | No |
| KNOWN_VS_UNKNOWN | answer=known | answer=known | No |
| CONTRADICTION | answer=consistent | answer=contradictory | Yes |
| ALTERNATIVE_COMPLETION_EXISTENCE | answer=no_alternative | answer=no_alternative | No |
| OBSERVATION_REQUIREMENT_COMPARISON | answer=mismatch | answer=mismatch | No |
| EVIDENCE_SUFFICIENCY | answer=determinate | answer=determinate | No |

Five-class gold: SUPPORTED_CURRENT_DEFECT → INVALID_OR_CONTRADICTORY_EVIDENCE.

### pc41b9ceb9742 — IDENTITY_EQUALITY

Change only the second asserted mark value to agree; the two events remain distinct.

Exact JSON path: `/assertions/1/asserted_value`.

Before: `"linen-smooth"`. After: `"linen-etched"`.

No non-target primitive truth changes under its frozen scope. Identity/value equality and consistency share the same two immutable mark assertions; changing one can necessarily change whether both assertions coexist.

| Primitive | A gold | B gold | Changed |
|---|---|---|---|
| IDENTITY_EQUALITY | same_referent=false, equal_value=false | same_referent=false, equal_value=true | Yes |
| CURRENTNESS | answer=current | answer=current | No |
| KNOWN_VS_UNKNOWN | answer=known | answer=known | No |
| CONTRADICTION | answer=consistent | answer=consistent | No |
| ALTERNATIVE_COMPLETION_EXISTENCE | answer=no_alternative | answer=no_alternative | No |
| OBSERVATION_REQUIREMENT_COMPARISON | answer=match | answer=match | No |
| EVIDENCE_SUFFICIENCY | answer=determinate | answer=determinate | No |

Five-class gold: NO_SUPPORTED_DIAGNOSIS → NO_SUPPORTED_DIAGNOSIS.

### p9147188c88d5 — CURRENTNESS

Deploy the newer second build instead of the first older build; observations and contracts stay fixed.

Exact JSON path: `/deployment/build`.

Before: `"flint-revision-k"`. After: `"flint-revision-m"`.

No non-target primitive truth changes under its frozen scope. Deployment selects which trial proposition the sufficiency question concerns; moving from an unresolved trial to a captured trial changes determinacy.

| Primitive | A gold | B gold | Changed |
|---|---|---|---|
| IDENTITY_EQUALITY | same_referent=true, equal_value=true | same_referent=true, equal_value=true | No |
| CURRENTNESS | answer=current | answer=not_current | Yes |
| KNOWN_VS_UNKNOWN | answer=known | answer=known | No |
| CONTRADICTION | answer=consistent | answer=consistent | No |
| ALTERNATIVE_COMPLETION_EXISTENCE | answer=no_alternative | answer=no_alternative | No |
| OBSERVATION_REQUIREMENT_COMPARISON | answer=mismatch | answer=mismatch | No |
| EVIDENCE_SUFFICIENCY | answer=determinate | answer=determinate | No |

Five-class gold: SUPPORTED_CURRENT_DEFECT → HISTORICAL_DEFECT_NOT_CURRENT.

### p54186fe7d147 — CURRENTNESS

Deploy the older second build instead of the first newer build; the non-serving newer violation is not an older-version defect.

Exact JSON path: `/deployment/build`.

Before: `"heath-revision-k"`. After: `"heath-revision-m"`.

No non-target primitive truth changes under its frozen scope. Deployment selects which trial proposition the sufficiency question concerns; moving from an unresolved trial to a captured trial changes determinacy.

| Primitive | A gold | B gold | Changed |
|---|---|---|---|
| IDENTITY_EQUALITY | same_referent=true, equal_value=true | same_referent=true, equal_value=true | No |
| CURRENTNESS | answer=current | answer=not_current | Yes |
| KNOWN_VS_UNKNOWN | answer=known | answer=known | No |
| CONTRADICTION | answer=consistent | answer=consistent | No |
| ALTERNATIVE_COMPLETION_EXISTENCE | answer=no_alternative | answer=no_alternative | No |
| OBSERVATION_REQUIREMENT_COMPARISON | answer=mismatch | answer=mismatch | No |
| EVIDENCE_SUFFICIENCY | answer=determinate | answer=determinate | No |

Five-class gold: SUPPORTED_CURRENT_DEFECT → NO_SUPPORTED_DIAGNOSIS.

### p6573d8bb3bcc — CURRENTNESS

Deploy the second build with a captured input instead of the first with unresolved input; all observations stay fixed.

Exact JSON path: `/deployment/build`.

Before: `"coral-revision-k"`. After: `"coral-revision-m"`.

Deployment selects which trial proposition the sufficiency question concerns; moving from an unresolved trial to a captured trial changes determinacy.

| Primitive | A gold | B gold | Changed |
|---|---|---|---|
| IDENTITY_EQUALITY | same_referent=true, equal_value=true | same_referent=true, equal_value=true | No |
| CURRENTNESS | answer=current | answer=not_current | Yes |
| KNOWN_VS_UNKNOWN | answer=unknown | answer=unknown | No |
| CONTRADICTION | answer=consistent | answer=consistent | No |
| ALTERNATIVE_COMPLETION_EXISTENCE | answer=alternative_exists | answer=alternative_exists | No |
| OBSERVATION_REQUIREMENT_COMPARISON | answer=match | answer=match | No |
| EVIDENCE_SUFFICIENCY | answer=underdetermined | answer=determinate | Yes |

Five-class gold: INSUFFICIENT_EVIDENCE → NO_SUPPORTED_DIAGNOSIS.

### p4448c687622e — CURRENTNESS

Change only deployment; the separate immutable mark disagreement stays present on both sides.

Exact JSON path: `/deployment/build`.

Before: `"wren-revision-k"`. After: `"wren-revision-m"`.

No non-target primitive truth changes under its frozen scope. Deployment selects which trial proposition the sufficiency question concerns; moving from an unresolved trial to a captured trial changes determinacy.

| Primitive | A gold | B gold | Changed |
|---|---|---|---|
| IDENTITY_EQUALITY | same_referent=true, equal_value=false | same_referent=true, equal_value=false | No |
| CURRENTNESS | answer=current | answer=not_current | Yes |
| KNOWN_VS_UNKNOWN | answer=known | answer=known | No |
| CONTRADICTION | answer=contradictory | answer=contradictory | No |
| ALTERNATIVE_COMPLETION_EXISTENCE | answer=no_alternative | answer=no_alternative | No |
| OBSERVATION_REQUIREMENT_COMPARISON | answer=match | answer=match | No |
| EVIDENCE_SUFFICIENCY | answer=determinate | answer=determinate | No |

Five-class gold: INVALID_OR_CONTRADICTORY_EVIDENCE → INVALID_OR_CONTRADICTORY_EVIDENCE.

### pfe5134c8aba6 — KNOWN_VS_UNKNOWN

Remove only the captured input, leaving three admissible completions with different outputs.

Exact JSON path: `/trials/0/reported_input`.

Before: `"cedar-woven"`. After: `"UNKNOWN"`.

Removing a captured input enlarges the compatible domain, necessarily introducing alternatives; sufficiency also changes exactly when those completions differ on output compliance.

| Primitive | A gold | B gold | Changed |
|---|---|---|---|
| IDENTITY_EQUALITY | same_referent=true, equal_value=true | same_referent=true, equal_value=true | No |
| CURRENTNESS | answer=current | answer=current | No |
| KNOWN_VS_UNKNOWN | answer=known | answer=unknown | Yes |
| CONTRADICTION | answer=consistent | answer=consistent | No |
| ALTERNATIVE_COMPLETION_EXISTENCE | answer=no_alternative | answer=alternative_exists | Yes |
| OBSERVATION_REQUIREMENT_COMPARISON | answer=mismatch | answer=mismatch | No |
| EVIDENCE_SUFFICIENCY | answer=determinate | answer=underdetermined | Yes |

Five-class gold: SUPPORTED_CURRENT_DEFECT → INSUFFICIENT_EVIDENCE.

### pfea0877e44e6 — KNOWN_VS_UNKNOWN

Remove only the captured input; do not invert the measured output into an input assumption.

Exact JSON path: `/trials/0/reported_input`.

Before: `"larch-woven"`. After: `"UNKNOWN"`.

Removing a captured input enlarges the compatible domain, necessarily introducing alternatives; sufficiency also changes exactly when those completions differ on output compliance.

| Primitive | A gold | B gold | Changed |
|---|---|---|---|
| IDENTITY_EQUALITY | same_referent=true, equal_value=true | same_referent=true, equal_value=true | No |
| CURRENTNESS | answer=current | answer=current | No |
| KNOWN_VS_UNKNOWN | answer=known | answer=unknown | Yes |
| CONTRADICTION | answer=consistent | answer=consistent | No |
| ALTERNATIVE_COMPLETION_EXISTENCE | answer=no_alternative | answer=alternative_exists | Yes |
| OBSERVATION_REQUIREMENT_COMPARISON | answer=match | answer=match | No |
| EVIDENCE_SUFFICIENCY | answer=determinate | answer=underdetermined | Yes |

Five-class gold: NO_SUPPORTED_DIAGNOSIS → INSUFFICIENT_EVIDENCE.

### p85beaefc6d27 — KNOWN_VS_UNKNOWN

Remove only the captured input; all three possibilities retain the same required output.

Exact JSON path: `/trials/0/reported_input`.

Before: `"amber-woven"`. After: `"UNKNOWN"`.

Removing a captured input enlarges the compatible domain, necessarily introducing alternatives; sufficiency also changes exactly when those completions differ on output compliance.

| Primitive | A gold | B gold | Changed |
|---|---|---|---|
| IDENTITY_EQUALITY | same_referent=true, equal_value=true | same_referent=true, equal_value=true | No |
| CURRENTNESS | answer=current | answer=current | No |
| KNOWN_VS_UNKNOWN | answer=known | answer=unknown | Yes |
| CONTRADICTION | answer=consistent | answer=consistent | No |
| ALTERNATIVE_COMPLETION_EXISTENCE | answer=no_alternative | answer=alternative_exists | Yes |
| OBSERVATION_REQUIREMENT_COMPARISON | answer=match | answer=match | No |
| EVIDENCE_SUFFICIENCY | answer=determinate | answer=determinate | No |

Five-class gold: HISTORICAL_DEFECT_NOT_CURRENT → HISTORICAL_DEFECT_NOT_CURRENT.

### p3b126a65a170 — KNOWN_VS_UNKNOWN

Remove only the captured input; every possibility still requires a value different from the observation.

Exact JSON path: `/trials/0/reported_input`.

Before: `"slate-woven"`. After: `"UNKNOWN"`.

Removing a captured input enlarges the compatible domain, necessarily introducing alternatives; sufficiency also changes exactly when those completions differ on output compliance.

| Primitive | A gold | B gold | Changed |
|---|---|---|---|
| IDENTITY_EQUALITY | same_referent=true, equal_value=true | same_referent=true, equal_value=true | No |
| CURRENTNESS | answer=current | answer=current | No |
| KNOWN_VS_UNKNOWN | answer=known | answer=unknown | Yes |
| CONTRADICTION | answer=consistent | answer=consistent | No |
| ALTERNATIVE_COMPLETION_EXISTENCE | answer=no_alternative | answer=alternative_exists | Yes |
| OBSERVATION_REQUIREMENT_COMPARISON | answer=mismatch | answer=mismatch | No |
| EVIDENCE_SUFFICIENCY | answer=determinate | answer=determinate | No |

Five-class gold: SUPPORTED_CURRENT_DEFECT → SUPPORTED_CURRENT_DEFECT.

### pe769b04b8bb4 — CONTRADICTION

Change only one mark assertion to a different value about the same immutable event.

Exact JSON path: `/assertions/1/asserted_value`.

Before: `"moss-etched"`. After: `"moss-smooth"`.

Consistency flips here by changing either referent identity or value equality, so the identity/equality vector necessarily changes too.

| Primitive | A gold | B gold | Changed |
|---|---|---|---|
| IDENTITY_EQUALITY | same_referent=true, equal_value=true | same_referent=true, equal_value=false | Yes |
| CURRENTNESS | answer=current | answer=current | No |
| KNOWN_VS_UNKNOWN | answer=known | answer=known | No |
| CONTRADICTION | answer=consistent | answer=contradictory | Yes |
| ALTERNATIVE_COMPLETION_EXISTENCE | answer=no_alternative | answer=no_alternative | No |
| OBSERVATION_REQUIREMENT_COMPARISON | answer=match | answer=match | No |
| EVIDENCE_SUFFICIENCY | answer=determinate | answer=determinate | No |

Five-class gold: HISTORICAL_DEFECT_NOT_CURRENT → INVALID_OR_CONTRADICTORY_EVIDENCE.

### p1b34b0fb1fdb — CONTRADICTION

Change only the second assertion station so the two unequal values concern one immutable event.

Exact JSON path: `/assertions/1/subject/station`.

Before: `"ivory-mark-stand-annex"`. After: `"ivory-mark-stand"`.

Consistency flips here by changing either referent identity or value equality, so the identity/equality vector necessarily changes too.

| Primitive | A gold | B gold | Changed |
|---|---|---|---|
| IDENTITY_EQUALITY | same_referent=false, equal_value=false | same_referent=true, equal_value=false | Yes |
| CURRENTNESS | answer=current | answer=current | No |
| KNOWN_VS_UNKNOWN | answer=known | answer=known | No |
| CONTRADICTION | answer=consistent | answer=contradictory | Yes |
| ALTERNATIVE_COMPLETION_EXISTENCE | answer=no_alternative | answer=no_alternative | No |
| OBSERVATION_REQUIREMENT_COMPARISON | answer=match | answer=match | No |
| EVIDENCE_SUFFICIENCY | answer=determinate | answer=determinate | No |

Five-class gold: HISTORICAL_DEFECT_NOT_CURRENT → INVALID_OR_CONTRADICTORY_EVIDENCE.

### pe89e1cbd08fd — CONTRADICTION

Change only the second assertion build so the two unequal values concern one immutable event.

Exact JSON path: `/assertions/1/subject/build`.

Before: `"reed-revision-m"`. After: `"reed-revision-k"`.

Consistency flips here by changing either referent identity or value equality, so the identity/equality vector necessarily changes too.

| Primitive | A gold | B gold | Changed |
|---|---|---|---|
| IDENTITY_EQUALITY | same_referent=false, equal_value=false | same_referent=true, equal_value=false | Yes |
| CURRENTNESS | answer=current | answer=current | No |
| KNOWN_VS_UNKNOWN | answer=known | answer=known | No |
| CONTRADICTION | answer=consistent | answer=contradictory | Yes |
| ALTERNATIVE_COMPLETION_EXISTENCE | answer=no_alternative | answer=no_alternative | No |
| OBSERVATION_REQUIREMENT_COMPARISON | answer=match | answer=match | No |
| EVIDENCE_SUFFICIENCY | answer=determinate | answer=determinate | No |

Five-class gold: HISTORICAL_DEFECT_NOT_CURRENT → INVALID_OR_CONTRADICTORY_EVIDENCE.

### p9b6e9ea58666 — CONTRADICTION

Change only the second assertion cycle so the two unequal values concern one immutable event.

Exact JSON path: `/assertions/1/subject/cycle`.

Before: `117`. After: `116`.

Consistency flips here by changing either referent identity or value equality, so the identity/equality vector necessarily changes too.

| Primitive | A gold | B gold | Changed |
|---|---|---|---|
| IDENTITY_EQUALITY | same_referent=false, equal_value=false | same_referent=true, equal_value=false | Yes |
| CURRENTNESS | answer=current | answer=current | No |
| KNOWN_VS_UNKNOWN | answer=known | answer=known | No |
| CONTRADICTION | answer=consistent | answer=contradictory | Yes |
| ALTERNATIVE_COMPLETION_EXISTENCE | answer=no_alternative | answer=no_alternative | No |
| OBSERVATION_REQUIREMENT_COMPARISON | answer=match | answer=match | No |
| EVIDENCE_SUFFICIENCY | answer=determinate | answer=determinate | No |

Five-class gold: NO_SUPPORTED_DIAGNOSIS → INVALID_OR_CONTRADICTORY_EVIDENCE.

### pe6150a0d0f53 — ALTERNATIVE_COMPLETION_EXISTENCE

Add exactly one allowed input to an uncaptured singleton domain; the requirement table and observation stay fixed.

Exact JSON path: `/trials/0/admissible_inputs`.

Before: `["ash-woven"]`. After: `["ash-woven", "ash-glazed"]`.

Expanding a singleton remaining domain removes unique input determination; sufficiency additionally changes when the added input implies a different violation truth value.

| Primitive | A gold | B gold | Changed |
|---|---|---|---|
| IDENTITY_EQUALITY | same_referent=true, equal_value=true | same_referent=true, equal_value=true | No |
| CURRENTNESS | answer=current | answer=current | No |
| KNOWN_VS_UNKNOWN | answer=known | answer=unknown | Yes |
| CONTRADICTION | answer=consistent | answer=consistent | No |
| ALTERNATIVE_COMPLETION_EXISTENCE | answer=no_alternative | answer=alternative_exists | Yes |
| OBSERVATION_REQUIREMENT_COMPARISON | answer=match | answer=match | No |
| EVIDENCE_SUFFICIENCY | answer=determinate | answer=determinate | No |

Five-class gold: NO_SUPPORTED_DIAGNOSIS → NO_SUPPORTED_DIAGNOSIS.

### p290c1440f38a — ALTERNATIVE_COMPLETION_EXISTENCE

Add exactly one allowed input to an uncaptured singleton domain; the requirement table and observation stay fixed.

Exact JSON path: `/trials/0/admissible_inputs`.

Before: `["pearl-woven"]`. After: `["pearl-woven", "pearl-glazed"]`.

Expanding a singleton remaining domain removes unique input determination; sufficiency additionally changes when the added input implies a different violation truth value.

| Primitive | A gold | B gold | Changed |
|---|---|---|---|
| IDENTITY_EQUALITY | same_referent=true, equal_value=true | same_referent=true, equal_value=true | No |
| CURRENTNESS | answer=current | answer=current | No |
| KNOWN_VS_UNKNOWN | answer=known | answer=unknown | Yes |
| CONTRADICTION | answer=consistent | answer=consistent | No |
| ALTERNATIVE_COMPLETION_EXISTENCE | answer=no_alternative | answer=alternative_exists | Yes |
| OBSERVATION_REQUIREMENT_COMPARISON | answer=mismatch | answer=mismatch | No |
| EVIDENCE_SUFFICIENCY | answer=determinate | answer=determinate | No |

Five-class gold: SUPPORTED_CURRENT_DEFECT → SUPPORTED_CURRENT_DEFECT.

### p09c35169512d — ALTERNATIVE_COMPLETION_EXISTENCE

Add exactly one allowed input to an uncaptured singleton domain; the requirement table and observation stay fixed.

Exact JSON path: `/trials/0/admissible_inputs`.

Before: `["fern-woven"]`. After: `["fern-woven", "fern-glazed"]`.

Expanding a singleton remaining domain removes unique input determination; sufficiency additionally changes when the added input implies a different violation truth value.

| Primitive | A gold | B gold | Changed |
|---|---|---|---|
| IDENTITY_EQUALITY | same_referent=true, equal_value=true | same_referent=true, equal_value=true | No |
| CURRENTNESS | answer=current | answer=current | No |
| KNOWN_VS_UNKNOWN | answer=known | answer=unknown | Yes |
| CONTRADICTION | answer=consistent | answer=consistent | No |
| ALTERNATIVE_COMPLETION_EXISTENCE | answer=no_alternative | answer=alternative_exists | Yes |
| OBSERVATION_REQUIREMENT_COMPARISON | answer=match | answer=match | No |
| EVIDENCE_SUFFICIENCY | answer=determinate | answer=underdetermined | Yes |

Five-class gold: NO_SUPPORTED_DIAGNOSIS → INSUFFICIENT_EVIDENCE.

### p8205c60fcc6a — ALTERNATIVE_COMPLETION_EXISTENCE

Add exactly one allowed input to an uncaptured singleton domain; the requirement table and observation stay fixed.

Exact JSON path: `/trials/0/admissible_inputs`.

Before: `["willow-woven"]`. After: `["willow-woven", "willow-glazed"]`.

Expanding a singleton remaining domain removes unique input determination; sufficiency additionally changes when the added input implies a different violation truth value.

| Primitive | A gold | B gold | Changed |
|---|---|---|---|
| IDENTITY_EQUALITY | same_referent=true, equal_value=true | same_referent=true, equal_value=true | No |
| CURRENTNESS | answer=current | answer=current | No |
| KNOWN_VS_UNKNOWN | answer=known | answer=unknown | Yes |
| CONTRADICTION | answer=consistent | answer=consistent | No |
| ALTERNATIVE_COMPLETION_EXISTENCE | answer=no_alternative | answer=alternative_exists | Yes |
| OBSERVATION_REQUIREMENT_COMPARISON | answer=mismatch | answer=mismatch | No |
| EVIDENCE_SUFFICIENCY | answer=determinate | answer=underdetermined | Yes |

Five-class gold: SUPPORTED_CURRENT_DEFECT → INSUFFICIENT_EVIDENCE.

### pa7fdd2bdb981 — OBSERVATION_REQUIREMENT_COMPARISON

Change only the first trial observation from its reference-input requirement to a different supplied result.

Exact JSON path: `/trials/0/observed_result`.

Before: `"dune-pulse"`. After: `"dune-beam"`.

No non-target primitive truth changes under its frozen scope. Only the designated comparison changes; any diagnostic transition is a consequence of that changed observation under the fixed deployment facts.

| Primitive | A gold | B gold | Changed |
|---|---|---|---|
| IDENTITY_EQUALITY | same_referent=true, equal_value=true | same_referent=true, equal_value=true | No |
| CURRENTNESS | answer=current | answer=current | No |
| KNOWN_VS_UNKNOWN | answer=known | answer=known | No |
| CONTRADICTION | answer=consistent | answer=consistent | No |
| ALTERNATIVE_COMPLETION_EXISTENCE | answer=no_alternative | answer=no_alternative | No |
| OBSERVATION_REQUIREMENT_COMPARISON | answer=match | answer=mismatch | Yes |
| EVIDENCE_SUFFICIENCY | answer=determinate | answer=determinate | No |

Five-class gold: NO_SUPPORTED_DIAGNOSIS → SUPPORTED_CURRENT_DEFECT.

### p869553eb45c8 — OBSERVATION_REQUIREMENT_COMPARISON

Change only the older first trial observation; the explicitly deployed newer trial remains unchanged.

Exact JSON path: `/trials/0/observed_result`.

Before: `"opal-pulse"`. After: `"opal-beam"`.

No non-target primitive truth changes under its frozen scope. Only the designated comparison changes; any diagnostic transition is a consequence of that changed observation under the fixed deployment facts.

| Primitive | A gold | B gold | Changed |
|---|---|---|---|
| IDENTITY_EQUALITY | same_referent=true, equal_value=true | same_referent=true, equal_value=true | No |
| CURRENTNESS | answer=not_current | answer=not_current | No |
| KNOWN_VS_UNKNOWN | answer=known | answer=known | No |
| CONTRADICTION | answer=consistent | answer=consistent | No |
| ALTERNATIVE_COMPLETION_EXISTENCE | answer=no_alternative | answer=no_alternative | No |
| OBSERVATION_REQUIREMENT_COMPARISON | answer=match | answer=mismatch | Yes |
| EVIDENCE_SUFFICIENCY | answer=determinate | answer=determinate | No |

Five-class gold: NO_SUPPORTED_DIAGNOSIS → HISTORICAL_DEFECT_NOT_CURRENT.

### pc4e6e87979b9 — OBSERVATION_REQUIREMENT_COMPARISON

Change only the older first trial observation; the deployed second trial retains decision-relevant unresolved input.

Exact JSON path: `/trials/0/observed_result`.

Before: `"spruce-pulse"`. After: `"spruce-beam"`.

No non-target primitive truth changes under its frozen scope. Only the designated comparison changes; any diagnostic transition is a consequence of that changed observation under the fixed deployment facts.

| Primitive | A gold | B gold | Changed |
|---|---|---|---|
| IDENTITY_EQUALITY | same_referent=true, equal_value=true | same_referent=true, equal_value=true | No |
| CURRENTNESS | answer=not_current | answer=not_current | No |
| KNOWN_VS_UNKNOWN | answer=known | answer=known | No |
| CONTRADICTION | answer=consistent | answer=consistent | No |
| ALTERNATIVE_COMPLETION_EXISTENCE | answer=no_alternative | answer=no_alternative | No |
| OBSERVATION_REQUIREMENT_COMPARISON | answer=match | answer=mismatch | Yes |
| EVIDENCE_SUFFICIENCY | answer=underdetermined | answer=underdetermined | No |

Five-class gold: INSUFFICIENT_EVIDENCE → INSUFFICIENT_EVIDENCE.

### p9464ebed4ef3 — OBSERVATION_REQUIREMENT_COMPARISON

Change only the first trial observation; the separate immutable mark disagreement remains on both sides.

Exact JSON path: `/trials/0/observed_result`.

Before: `"maple-pulse"`. After: `"maple-beam"`.

No non-target primitive truth changes under its frozen scope. Only the designated comparison changes; any diagnostic transition is a consequence of that changed observation under the fixed deployment facts.

| Primitive | A gold | B gold | Changed |
|---|---|---|---|
| IDENTITY_EQUALITY | same_referent=true, equal_value=false | same_referent=true, equal_value=false | No |
| CURRENTNESS | answer=current | answer=current | No |
| KNOWN_VS_UNKNOWN | answer=known | answer=known | No |
| CONTRADICTION | answer=contradictory | answer=contradictory | No |
| ALTERNATIVE_COMPLETION_EXISTENCE | answer=no_alternative | answer=no_alternative | No |
| OBSERVATION_REQUIREMENT_COMPARISON | answer=match | answer=mismatch | Yes |
| EVIDENCE_SUFFICIENCY | answer=determinate | answer=determinate | No |

Five-class gold: INVALID_OR_CONTRADICTORY_EVIDENCE → INVALID_OR_CONTRADICTORY_EVIDENCE.

### pf2edb8d17b19 — EVIDENCE_SUFFICIENCY

Change only the required result for the third admissible input; three completions remain, but they now disagree about the operational violation proposition.

Exact JSON path: `/trials/0/required_results/2/result`.

Before: `"clay-pulse"`. After: `"clay-extra-ray"`.

No non-target primitive truth changes under its frozen scope. A non-reference requirement cell changes decision relevance while input identity, domain size, capture, deployment, mark assertions and reference comparison remain fixed.

| Primitive | A gold | B gold | Changed |
|---|---|---|---|
| IDENTITY_EQUALITY | same_referent=true, equal_value=true | same_referent=true, equal_value=true | No |
| CURRENTNESS | answer=current | answer=current | No |
| KNOWN_VS_UNKNOWN | answer=unknown | answer=unknown | No |
| CONTRADICTION | answer=consistent | answer=consistent | No |
| ALTERNATIVE_COMPLETION_EXISTENCE | answer=alternative_exists | answer=alternative_exists | No |
| OBSERVATION_REQUIREMENT_COMPARISON | answer=match | answer=match | No |
| EVIDENCE_SUFFICIENCY | answer=determinate | answer=underdetermined | Yes |

Five-class gold: NO_SUPPORTED_DIAGNOSIS → INSUFFICIENT_EVIDENCE.

### p2d668f50a4c4 — EVIDENCE_SUFFICIENCY

Change only the required result for the third admissible input; three completions remain, but they now disagree about the operational violation proposition.

Exact JSON path: `/trials/0/required_results/2/result`.

Before: `"pine-pulse"`. After: `"pine-beam"`.

No non-target primitive truth changes under its frozen scope. A non-reference requirement cell changes decision relevance while input identity, domain size, capture, deployment, mark assertions and reference comparison remain fixed.

| Primitive | A gold | B gold | Changed |
|---|---|---|---|
| IDENTITY_EQUALITY | same_referent=true, equal_value=true | same_referent=true, equal_value=true | No |
| CURRENTNESS | answer=current | answer=current | No |
| KNOWN_VS_UNKNOWN | answer=unknown | answer=unknown | No |
| CONTRADICTION | answer=consistent | answer=consistent | No |
| ALTERNATIVE_COMPLETION_EXISTENCE | answer=alternative_exists | answer=alternative_exists | No |
| OBSERVATION_REQUIREMENT_COMPARISON | answer=mismatch | answer=mismatch | No |
| EVIDENCE_SUFFICIENCY | answer=determinate | answer=underdetermined | Yes |

Five-class gold: SUPPORTED_CURRENT_DEFECT → INSUFFICIENT_EVIDENCE.

### pb9fcb5be062e — EVIDENCE_SUFFICIENCY

Change only the required result for the third admissible input; three completions remain, but they now disagree about the operational violation proposition.

Exact JSON path: `/trials/0/required_results/2/result`.

Before: `"quartz-pulse"`. After: `"quartz-extra-ray"`.

No non-target primitive truth changes under its frozen scope. A non-reference requirement cell changes decision relevance while input identity, domain size, capture, deployment, mark assertions and reference comparison remain fixed.

| Primitive | A gold | B gold | Changed |
|---|---|---|---|
| IDENTITY_EQUALITY | same_referent=true, equal_value=true | same_referent=true, equal_value=true | No |
| CURRENTNESS | answer=current | answer=current | No |
| KNOWN_VS_UNKNOWN | answer=unknown | answer=unknown | No |
| CONTRADICTION | answer=consistent | answer=consistent | No |
| ALTERNATIVE_COMPLETION_EXISTENCE | answer=alternative_exists | answer=alternative_exists | No |
| OBSERVATION_REQUIREMENT_COMPARISON | answer=match | answer=match | No |
| EVIDENCE_SUFFICIENCY | answer=determinate | answer=underdetermined | Yes |

Five-class gold: HISTORICAL_DEFECT_NOT_CURRENT → INSUFFICIENT_EVIDENCE.

### p05e943ec08b0 — EVIDENCE_SUFFICIENCY

Change only the required result for the third admissible input; three completions remain, but they now disagree about the operational violation proposition.

Exact JSON path: `/trials/0/required_results/2/result`.

Before: `"hazel-pulse"`. After: `"hazel-beam"`.

No non-target primitive truth changes under its frozen scope. A non-reference requirement cell changes decision relevance while input identity, domain size, capture, deployment, mark assertions and reference comparison remain fixed.

| Primitive | A gold | B gold | Changed |
|---|---|---|---|
| IDENTITY_EQUALITY | same_referent=true, equal_value=true | same_referent=true, equal_value=true | No |
| CURRENTNESS | answer=current | answer=current | No |
| KNOWN_VS_UNKNOWN | answer=unknown | answer=unknown | No |
| CONTRADICTION | answer=consistent | answer=consistent | No |
| ALTERNATIVE_COMPLETION_EXISTENCE | answer=alternative_exists | answer=alternative_exists | No |
| OBSERVATION_REQUIREMENT_COMPARISON | answer=mismatch | answer=mismatch | No |
| EVIDENCE_SUFFICIENCY | answer=determinate | answer=underdetermined | Yes |

Five-class gold: SUPPORTED_CURRENT_DEFECT → INSUFFICIENT_EVIDENCE.
