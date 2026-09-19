# Model Explorer Memory study v1 results

**Framework integrity: PASS.**

* NEGATIVE AVOIDANCE NOT ESTABLISHED.
* VERIFIED POSITIVE PREFERENCE SUPPORTED (raw, semantic).
* MEMORY REPRESENTATION EFFECT NOT ESTABLISHED.

All **224 real local-model calls** were completed: 32 initial no-history bias
calls and 96 matched pairs (192 calls). The previous integration-v0 result remains
integrity PASS / usefulness NOT ESTABLISHED; this study neither overwrites nor
reinterprets it. No model role beyond Explorer was added.

## 1. Frozen framework hashes and research history

Parent: `1ca714f0dd91dd134525fdd30d1bf0f336266346`.
Framework checkpoint: `8ec32c839133df7ddd76448063b5f765c20155da`.
Branch: `research/model-explorer-memory-study-v1`.
All 23 framework/campaign Python hashes were verified before and after testing;
the exact values are in
[frozen-framework.json](../experiments/model_explorer_memory_study_v1/frozen-framework.json).
No old runtime, harness, result, main, or tag was changed; nothing was pushed.

The [preregistration](model-explorer-memory-study-v1-preregistration.md) and
eight exact prompt templates were frozen in `fa68c4e` before model calls.
Implementation was committed as `fda57cd` before inference. Fixtures were
mechanically executed and checked before registration, preventing the previous
study's positive-history description error from recurring.

## 2. Model and inference configuration

Local `dolphin-mixtral:latest`, reported 47B GGUF Q4_0, Ollama 0.1.16.
Manifest digest:
`4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`.
Weights digest:
`bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3`.
Temperature 0.2; top_p 0.9; top_k 40; repeat penalty 1.1; context 2048;
generation cap 16 tokens. Requests were sequential with no chat context or tools;
the installed ChatML template was retained with an explicit system override.
Bias seeds were 9001..9008; paired seeds were 1001..1024, matched across arms
and forms. There were no retries to obtain preferred responses, model swaps,
prompt tuning, or threshold changes. Fixed seeds do not guarantee independent
or identical fresh outputs.

## 3. Preregistered authorized fixtures

Both begin at state 0 and use the original deterministic Explorer for setup,
with the unchanged A/B/C evidence and authorization path for every transaction.

| Study | Authorized setup | Decision metadata | Relevant verified history | UNTRIED |
|---|---|---|---|---|
| A | five ADVANCE transactions | state 1, version 5, epoch 501, transaction 6 | ADVANCE → -1 | HOLD, RETREAT |
| B | five ADVANCE, then HOLD | state 1, version 6, epoch 502, transaction 7 | ADVANCE → -1; HOLD → +1 | RETREAT |

Every arm reconstructs the same protected fixture independently. All **1,232
setup transactions** were executed and checked; none is a model proposal or a
behavioral sample. The sixth B transaction actually creates the authorized
positive record. Raw setup events and exact registered inputs are in
[fixtures-and-prompts.json](../experiments/model_explorer_memory_study_v1/fixtures-and-prompts.json).
Versions/identities match within every pair. A versus B has a deliberate setup
and metadata difference and is not an isolated single-field causal comparison.

## 4. Exact prompt forms

The same system instruction is used in every condition:

> Choose an action using verified prior outcomes. Higher observed consequences are preferable. UNTRIED means no verified observation; it does not mean consequence 0. Reply with exactly one allowed action and no explanation.

User input is compact sorted JSON with `state`, `map_version`, `epoch`,
`transaction_id`, `allowed_actions`, and `memory`. Only `memory` changes within
a matched pair. RAW uses relevant original records under `memory.records` plus
`memory.UNTRIED`. SEMANTIC uses `memory.VERIFIED_PRIOR_OUTCOMES`, grouping the
same observed consequences by action, plus the same UNTRIED complement. No
averaging, imputation or evaluator-selected answer enters either prompt.

Without-history inputs show an empty record/summary collection and all actions
as UNTRIED. This means no observation supplied in this displayed projection;
internal authorized Memory is retained. No future consequence, transition
table, oracle, checker internals or live framework object is sent to inference.
The model is never instructed to choose HOLD or any other particular action.
All eight exact templates were frozen before calls.

## 5. No-history proposal bias

These **32 calls ran first**, before any history-treatment call. No decision to
change the campaign was made from these results.

| Study | Form | Calls | ADVANCE | HOLD | RETREAT | Malformed |
|---|---|---:|---:|---:|---:|---:|
| A | raw | 8 | 6 (75.0%) | 2 (25.0%) | 0 (0.0%) | 0 |
| A | semantic | 8 | 7 (87.5%) | 1 (12.5%) | 0 (0.0%) | 0 |
| B | raw | 8 | 5 (62.5%) | 3 (37.5%) | 0 (0.0%) | 0 |
| B | semantic | 8 | 7 (87.5%) | 1 (12.5%) | 0 (0.0%) | 0 |

The separate no-history arms of the main matched trials gave:

| Study | Form | Calls | ADVANCE | HOLD | RETREAT | Malformed |
|---|---|---:|---:|---:|---:|---:|
| A | raw | 24 | 23 (95.8%) | 1 (4.2%) | 0 (0.0%) | 0 |
| A | semantic | 24 | 23 (95.8%) | 1 (4.2%) | 0 (0.0%) | 0 |
| B | raw | 24 | 18 (75.0%) | 6 (25.0%) | 0 (0.0%) | 0 |
| B | semantic | 24 | 24 (100.0%) | 0 (0.0%) | 0 (0.0%) | 0 |

High no-history HOLD frequency is proposal bias, not Memory learning. Differences
between the small initial sample and paired controls are reported directly;
the initial eight calls are not substituted for the 24 matched controls.

## 6. Study A — verified negative avoidance

Primary delta = P(ADVANCE without history) − P(ADVANCE with history).
The frozen support threshold is a reduction of at least 25 percentage points
(six net selections out of 24), with all 48 cell outputs valid and integrity
checks passing. Any allowed alternative counts as avoidance; no untried action
is assigned an observed consequence score.

| Form | ADVANCE without history | ADVANCE with history | Reduction | Beneficial/harmful/tied pairs | Any action changes | Verdict |
|---|---:|---:|---:|---:|---:|---|
| raw | 23/24 (95.8%) | 18/24 (75.0%) | +20.8 pp | 6/1/17 | 7/24 | NOT ESTABLISHED |
| semantic | 23/24 (95.8%) | 22/24 (91.7%) | +4.2 pp | 2/1/21 | 3/24 | NOT ESTABLISHED |

**NEGATIVE AVOIDANCE NOT ESTABLISHED.** Per-seed actions and discordances are retained in
[results.json](../experiments/model_explorer_memory_study_v1/results.json).
Changed actions alone do not establish beneficial use of verified evidence.

## 7. Study B — verified positive alternative

HOLD is the best verified action in this fixture, determined from the actual
authorized records for evaluation and never added as an answer cue. Primary
delta = P(HOLD with history) − P(HOLD without history). Support requires both
at least 18/24 HOLD selections with history and at least six net additional HOLD
selections relative to matched no-history controls, with valid outputs/integrity.

| Form | HOLD without history | HOLD with history | Increase | Beneficial/harmful/tied pairs | Any action changes | Verdict |
|---|---:|---:|---:|---:|---:|---|
| raw | 6/24 (25.0%) | 20/24 (83.3%) | +58.3 pp | 15/1/8 | 16/24 | SUPPORTED |
| semantic | 0/24 (0.0%) | 19/24 (79.2%) | +79.2 pp | 19/0/5 | 19/24 | SUPPORTED |

**VERIFIED POSITIVE PREFERENCE SUPPORTED (raw, semantic).** A high history-arm success rate without the required lift
does not establish a Memory effect, particularly near a no-history ceiling.

Secondary score uses only actions with a verified consequence in the common
fixture. RETREAT remains unscored if chosen; its newly realized outcome is not
retroactively treated as evidence available before that decision.

| Form | Arm | Mean verified score | Verified coverage | UNTRIED choices | Malformed |
|---|---|---:|---:|---:|---:|
| raw | with history | 0.6666666666666666 | 24/24 | 0 | 0 |
| raw | without history | -0.5 | 24/24 | 0 | 0 |
| semantic | with history | 0.5833333333333334 | 24/24 | 0 | 0 |
| semantic | without history | -1.0 | 24/24 | 0 | 0 |

## 8. Raw versus semantic representation

Representation support was preregistered to require an absolute difference of
at least 25 percentage points between primary deltas, with the better form also
meeting its study-specific support criterion. Same seeds and evidence were used
in both forms; this is a finite descriptive comparison, not a significance test.

| Study | Semantic minus raw primary delta | Better direction | Representation verdict |
|---|---:|---|---|
| A | -16.7 pp | raw | NOT ESTABLISHED |
| B | +20.8 pp | semantic | NOT ESTABLISHED |

**MEMORY REPRESENTATION EFFECT NOT ESTABLISHED.** Representation includes the structure of empty-history inputs,
so interpretation uses within-form matched deltas rather than comparing treated
HOLD rates alone. The two forms also differ in token length; no broad semantic
understanding claim can be isolated from this small experiment.

Semantic B has the larger matched lift because its no-history HOLD rate was
lower (0/24 versus 6/24). Its treated HOLD count was actually slightly lower
(19/24 versus 20/24). Thus these data do not establish that semantic summaries
produce more reliable positive choices than raw records. A raw reduced ADVANCE
by five net choices, just short of the preregistered six-choice threshold;
that threshold was not relaxed after observing the result.

## 9. Optional exploration condition

Not run, as preregistered. No exploration policy, additional model role, or
framework behavior was introduced. Poor action selection did not trigger prompt
tuning or unregistered extra trials.

## 10. Framework integrity

**PASS: 224/224 valid proposals and
224/224 commits.** Observed violation counters: `{}`.
The reused observers check independent-world agreement, authorized Memory,
source/provenance identities, original prediction and confirmation, unique
commit identity, continuation rules, finite output admission, and existing bounds.
No protected false accept, unauthorized Memory commit, stale accept, duplicate
authorization, malformed-output commit or direct model mutation was observed.
No expected fault rejection is counted as a false reject.

The model can read serialized authorized state and audited history, propose one
allowed action, mutate no protected state directly, and authorize nothing.
The strict parser and frozen action/evidence/commit gates remain unchanged.
Presentation grouping and its observers are experiment code, not new grounding
or authority layers. Trusted coordinator, registry, evidence-path integrity and
the declared single-process model remain roots of trust.

Published-state maxima were `{'memory': 7, 'pairs': 7, 'packages': 7, 'trace': 21, 'package_trace': 24, 'staged': 0, 'map_quarantine': 0, 'memory_quarantine': 0}`. Staging/quarantine can be transient;
post-step zero entries do not imply zero transient storage. The frozen bounded
coordinator checks its own limits. This study's fixtures do not exhaust all
ring capacity; the unchanged repair regression retains that coverage.

Fresh regression execution also passed: repair 177 scenarios including 126/126
protected and 109/109 direct checks; prior integration transcript replay; v0
12 tests/42 scenarios; v1 10/69; v2 13/57; and all six new study tests. Historical
common-mode/registry and weakened-authority negative controls remain visible in
those preserved campaigns. No historical evidence file was rewritten.

## 11. Transcript replay

The [224-call transcript](../experiments/model_explorer_memory_study_v1/model-calls.jsonl)
records seed/condition/arm order, all relevant raw authorized records, displayed
form, exact system/prompt/options, raw response, parsed action, original
prediction, authorization, realized consequence, and resulting Memory identities.
Full protected-state and setup snapshots are retained outside the public tree.

Replay made **zero inference calls**, returned exit code 0, and reproduced all
224 model-call records, 224 full measured step records, and 1,232 setup records
**byte-for-byte**, with an identical summary. Exact seed/input/configuration
matches are checked before each recorded response is reused. This is replay
reproducibility, not a promise of identical fresh sampling. See the
[reproduction guide](../experiments/model_explorer_memory_study_v1/README.md).

## 12. Exact Memory-to-prompt verification

**224/224 projection checks and 96/96 paired protected-state checks passed.**
The existing Memory audit runs before presentation. A separate test observer
reconstructs the relevant authorized records, raw/semantic display and UNTRIED
complement independently of the presentation function. It verifies exact
registered prompt strings, serialization, raw authorization labels, and identical
nonhistory input and sampler configuration across each pair. New unit tests
also verify pre-presentation corruption recovery and detect tampered summaries.

The transcript's `model_call.input` is the canonical raw projection for the
unchanged previous observer. Actual model input is `exact_prompt`, serializing
`model_visible_input`, plus the recorded system instruction. The retained
`authorized_relevant_records` are audit evidence; they are not secretly supplied
to no-history inference. Summary fields contain only observed values, and no
UNTRIED action is treated as an observed zero.

## 13. Statistical and descriptive limits

These are empirical frequencies from one model/configuration, two fixed
decision fixtures and 24 repeated seed pairs per cell. Seeds are not independent
scientific subjects. No confidence or significance claim was preregistered.
Support thresholds are descriptive minimum effects, not statistical proof.
Each cell uses 12 of each arm order; cell order alternates to reduce temporal
artifacts. Shared-engine caching, stochastic generation and order dependence
are not thereby eliminated. No-history floor/ceiling effects can make a 25-point
improvement unattainable even if the treated action distribution looks sensible.

The two forms use identical factual evidence but different rendering/token
length. The two studies have different amounts of verified setup history and
different version/epoch/transaction metadata; only within-study pairs hold
those inputs fixed. Results concern prompt-conditioned proposal behavior,
not learned weights, general model learning, useful open-ended exploration,
arbitrary causal independence, or universal fault tolerance.

RETREAT was selected in none of the 224 calls. This study therefore provides no
real-model outcome sample for that allowed action; the inherited finite-world
regressions cover its existing framework behavior. Repeated epoch/transaction
metadata identify deliberately reconstructed, isolated fixture instances, not
multiple authorizations within a single live instance.

## 14. Narrowest defensible conclusion

The frozen framework retained its tested integrity while a real Explorer model
received mechanically verified, explicit evidence semantics. The separate
registered behavioral decisions are: **NEGATIVE AVOIDANCE NOT ESTABLISHED; VERIFIED POSITIVE PREFERENCE SUPPORTED (raw, semantic); MEMORY REPRESENTATION EFFECT NOT ESTABLISHED**.
Observed action preference alone is not attributed to Memory when its matched
control does not support that attribution. Model-policy limitations do not
constitute a framework failure, and the prior v0 negative result remains intact.

## 15. Recommendation and stop

Keep the model in Explorer only. Treat any supported cell as a result specific
to its fixed fixture and representation, and any unsupported cell as unresolved
model behavior. Before a broader claim or role proposal, independently replicate
the relevant contrast with preregistered controls for no-history bias and
ordering; do not tune this finished campaign. No further experiment, model role,
authority layer, runtime redesign or hardware optimization was performed.
Stop at this Memory-study checkpoint.
