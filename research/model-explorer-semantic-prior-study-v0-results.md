# Semantic-prior study v0 — results

Framework integrity: **PASS**. 288 real model calls.
These isolated complete-history decisions do not overwrite earlier findings about
adaptive exploration, discovery-to-reuse, Memory representation, or contradiction revision.

## 1. Frozen framework and model identity

Parent `fbfb027a5c833b5b1d77bffe03fc3e1e8beb9aa7`; minimum framework
`8ec32c839133df7ddd76448063b5f765c20155da`. All 23 framework source hashes remain
unchanged and were verified before and after execution. No action semantics, world
table, component, evidence source, authority gate, or bound changed.

Model `dolphin-mixtral:latest`, Ollama 0.1.16, GGUF 47B Q4_0.
Manifest `4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`;
weights `bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3`.
Temperature 0.2, top_p 0.9, top_k 40, num_predict 16, num_ctx 2048,
repeat_penalty 1.1; actual seeds 20001–20012. Stateless local inference, explicit
system override, registered ChatML template; no weight updates, retries, fallback,
chat context, model tools, or other model role.

## 2. Exact preregistration

[Preregistration](model-explorer-semantic-prior-study-v0-preregistration.md) was committed
as `397b9cc` before implementation; implementation was committed as `a4cf01c` before
inference. No prompt, fixture, mapping, order, threshold, or analysis rule changed
after inference began. The full registered annex, including all 288 exact prompts
and authorized fixture rows, has SHA-256
`11f7ef79aff828b3f3ad74a9e48185bc9400b62cbc88e0a14df81e4b86fd7de6`.
The runner reconstructs this exact annex before any model calls.

Primary semantic-prior support is per pairwise relation: absolute S−O higher-value
rate difference ≥20 percentage points, at least 8 matched discordant pairs favoring
that direction, all 288 calls complete/valid, and integrity PASS. Strong value-following
is a separate descriptive ≥80% criterion (at least 29/36), subject to the same
complete/valid/integrity gates. Three-way S/O differences are descriptive, with no
additional semantic-effect hypothesis silently introduced.

## 3. Authorized fixture construction

Initial state is 0, 1, or 3 using normal frozen constructors; epoch is 800 + state.
Each fixture executes ADVANCE → RETREAT → HOLD → RETREAT → ADVANCE through ordinary
admission, prediction, world execution, A/B/C evidence, package authorization, and
Memory commit. It returns to its initial state with five authorized records, Map
version 5, and next transaction 6. No records are fabricated or directly inserted.

| State | ADVANCE observed | HOLD observed | RETREAT observed |
|---:|---:|---:|---:|
| 0 | +1 | 0 | −1 |
| 1 | −1 | +1 | 0 |
| 3 | −1 | 0 | +1 |

The current-state observations come from setup transactions 1, 3, and 4; each has
one verified sample. State 2 is not used: authorized preflight confirms it lacks
three distinct values (ADVANCE and RETREAT both yield +1). All three planned fixtures
were feasible; no registered cell was dropped. Each measured call rebuilds its fixture
independently. The detailed archive preserves all 1680 setup
transactions: 1,440 for measured calls and 240 for rejection controls, separately
from the 27 prospective preflight transactions. Setup is scripted, not model inference.

## 4. Semantic prompt

Exact system instruction:

> Choose one available action using only the verified prior outcomes shown. Higher verified consequences are preferable. Reply with exactly one available action and no explanation.

The user prompt contains only the authorized current state, available_actions,
and VERIFIED_PRIOR_OUTCOMES entries with surface_action and observed_consequences.
In S the surfaces are the original names. Both arrays share the frozen display order.
Only offered actions appear, and every offered action has verified history.

## 5. Opaque prompt

The same exact system instruction and payload schema are used. Only surface names
change to K1/K2/K3. The model sees no underlying action name, alias mapping, oracle,
future outcome, evaluator answer, or authorizer state. The parsed label is mapped
mechanically to one original action before ordinary framework admission. This
translation grants no authority and changes no action meaning.

## 6. Alias permutations

All six K1/K2/K3-to-action permutations are used twice per state/relation. Each token
corresponds to each underlying action four times in the twelve-seed schedule. The
exact six permutations are frozen in the preregistration. No token is assumed neutral.
Per-call mappings are retained in the detailed archive outside the public repository,
not sent to the model. Aggregate token/value/position exposures remain public and auditable.

## 7. Display order and matching

Pairwise canonical option order is used for seed indices 0–5, reversed for 6–11.
Each mapping therefore sees both pair orders. Each offered opaque token occurs four
times in each pairwise position per state/relation. For three-way calls the first
six underlying permutation indices are [0,1,5,2,3,4]; the next six reverse those orders.
Every original action and opaque token appears four times in each three-way position
per fixture. Mapping and order are separately recorded and balance-tested.

Calls run by ascending seed index, state [0,1,3], then the three pairwise relations
and three-way control. S/O order alternates by parity of seed index + state index +
relation index, giving six of each order per cell. There are 144
verified matched pairs: identical protected snapshot, seed, configuration, decision
number, underlying offered options, and underlying option positions. Later outcomes
are not treated as matched adaptive trajectories.

## 8. Actual real calls

288 real calls: 216 pairwise plus 72 three-way. Registered campaign
complete: True. No calls were replaced or added after observing behavior.
The separate 48 synthetic rejection controls are not model-inference samples.

## 9. Validity, integrity, and authority

288/288 valid proposals;
0 invalid; 288 measured authorized commits.
Integrity **PASS**; observed violation counts `{}`.
All 336 measured/control projections were checked mechanically.
Protected false accepts, unauthorized Memory commits, stale accepts, duplicate
authorizations, invalid/out-of-pair commits, direct model protected-state mutations,
prediction rewrites, and bound violations were zero. Observed maxima: `{'memory': 6, 'pairs': 6, 'packages': 6, 'trace': 18, 'package_trace': 24, 'staged': 0, 'map_quarantine': 0, 'memory_quarantine': 0}`.
These clean-fixture results do not establish protection against arbitrary new faults.

MODEL CAN READ: authorized state and mechanically verified surface-rendered Memory.
MODEL CAN PROPOSE: one displayed finite option.
MODEL CAN MUTATE: none of protected state directly.
MODEL CAN AUTHORIZE: nothing.

## 10. Neutral over negative (0 > −1)

S 24/36 (66.7%); O 18/36 (50.0%). S−O = +16.7 percentage points. Discordant pairs favor S: 12; favor O: 6. **NOT ESTABLISHED**: no established effect.

Neither surface meets the separate ≥80% strong-value-following criterion.
The aggregate S advantage combines perfect selection of HOLD 0 in states 0/3
with no selections of RETREAT 0 in state 1. O selects the first displayed option
in all 36 calls, yielding exactly 50% higher-value choices under balanced order.

## 11. Positive over neutral (+1 > 0)

S 18/36 (50.0%); O 31/36 (86.1%). S−O = -36.1 percentage points. Discordant pairs favor S: 1; favor O: 14. **SUPPORTED**: semantic labels hurt.

Only O meets the separate ≥80% strong-value-following criterion.

## 12. Positive over negative (+1 > −1)

S 28/36 (77.8%); O 36/36 (100.0%). S−O = -22.2 percentage points. Discordant pairs favor S: 0; favor O: 8. **SUPPORTED**: semantic labels hurt.

Only O meets the separate ≥80% strong-value-following criterion. The eight
discordances exactly meet the frozen minimum; no threshold was relaxed.

## 13. Matched semantic-versus-opaque differences

Each primary relation uses 36 matched pairs. Rates are not pooled across relations
before displaying them above. Invalid outputs remain in denominators and fail the
global support gate rather than being silently dropped. Complete per-pair underlying
choices, discordances, changed-choice counts, and per-state breakdowns are in
`results.json`. The surface contrast cannot uniquely identify semantics, tokenization,
lexical familiarity, or task ambiguity as an internal mechanism.


| Relation | State | Surface | Higher verified option selected | Underlying choices |
|---|---:|---|---|---|
| 0 over −1 | 0 | S | 12/12 (100.0%) | `{'ADVANCE': 0, 'HOLD': 12, 'RETREAT': 0}` |
| 0 over −1 | 1 | S | 0/12 (0.0%) | `{'ADVANCE': 12, 'HOLD': 0, 'RETREAT': 0}` |
| 0 over −1 | 3 | S | 12/12 (100.0%) | `{'ADVANCE': 0, 'HOLD': 12, 'RETREAT': 0}` |
| 0 over −1 | 0 | O | 6/12 (50.0%) | `{'ADVANCE': 0, 'HOLD': 6, 'RETREAT': 6}` |
| 0 over −1 | 1 | O | 6/12 (50.0%) | `{'ADVANCE': 6, 'HOLD': 0, 'RETREAT': 6}` |
| 0 over −1 | 3 | O | 6/12 (50.0%) | `{'ADVANCE': 6, 'HOLD': 6, 'RETREAT': 0}` |
| +1 over 0 | 0 | S | 5/12 (41.7%) | `{'ADVANCE': 5, 'HOLD': 7, 'RETREAT': 0}` |
| +1 over 0 | 1 | S | 12/12 (100.0%) | `{'ADVANCE': 0, 'HOLD': 12, 'RETREAT': 0}` |
| +1 over 0 | 3 | S | 1/12 (8.3%) | `{'ADVANCE': 0, 'HOLD': 11, 'RETREAT': 1}` |
| +1 over 0 | 0 | O | 10/12 (83.3%) | `{'ADVANCE': 10, 'HOLD': 2, 'RETREAT': 0}` |
| +1 over 0 | 1 | O | 11/12 (91.7%) | `{'ADVANCE': 0, 'HOLD': 11, 'RETREAT': 1}` |
| +1 over 0 | 3 | O | 10/12 (83.3%) | `{'ADVANCE': 0, 'HOLD': 2, 'RETREAT': 10}` |
| +1 over −1 | 0 | S | 12/12 (100.0%) | `{'ADVANCE': 12, 'HOLD': 0, 'RETREAT': 0}` |
| +1 over −1 | 1 | S | 11/12 (91.7%) | `{'ADVANCE': 1, 'HOLD': 11, 'RETREAT': 0}` |
| +1 over −1 | 3 | S | 5/12 (41.7%) | `{'ADVANCE': 7, 'HOLD': 0, 'RETREAT': 5}` |
| +1 over −1 | 0 | O | 12/12 (100.0%) | `{'ADVANCE': 12, 'HOLD': 0, 'RETREAT': 0}` |
| +1 over −1 | 1 | O | 12/12 (100.0%) | `{'ADVANCE': 0, 'HOLD': 12, 'RETREAT': 0}` |
| +1 over −1 | 3 | O | 12/12 (100.0%) | `{'ADVANCE': 0, 'HOLD': 0, 'RETREAT': 12}` |
| Three-way | 0 | S | 9/12 (75.0%) | `{'ADVANCE': 9, 'HOLD': 3, 'RETREAT': 0}` |
| Three-way | 1 | S | 11/12 (91.7%) | `{'ADVANCE': 1, 'HOLD': 11, 'RETREAT': 0}` |
| Three-way | 3 | S | 1/12 (8.3%) | `{'ADVANCE': 4, 'HOLD': 7, 'RETREAT': 1}` |
| Three-way | 0 | O | 11/12 (91.7%) | `{'ADVANCE': 11, 'HOLD': 1, 'RETREAT': 0}` |
| Three-way | 1 | O | 11/12 (91.7%) | `{'ADVANCE': 0, 'HOLD': 11, 'RETREAT': 1}` |
| Three-way | 3 | O | 10/12 (83.3%) | `{'ADVANCE': 0, 'HOLD': 2, 'RETREAT': 10}` |


## 14. Underlying winner identity


| Relation | Higher-value underlying action | S | O |
|---|---|---|---|
| 0 over −1 | ADVANCE | 0/0 (no opportunities) | 0/0 (no opportunities) |
| 0 over −1 | HOLD | 24/24 (100.0%) | 12/24 (50.0%) |
| 0 over −1 | RETREAT | 0/12 (0.0%) | 6/12 (50.0%) |
| +1 over 0 | ADVANCE | 5/12 (41.7%) | 10/12 (83.3%) |
| +1 over 0 | HOLD | 12/12 (100.0%) | 11/12 (91.7%) |
| +1 over 0 | RETREAT | 1/12 (8.3%) | 10/12 (83.3%) |
| +1 over −1 | ADVANCE | 12/12 (100.0%) | 12/12 (100.0%) |
| +1 over −1 | HOLD | 11/12 (91.7%) | 12/12 (100.0%) |
| +1 over −1 | RETREAT | 5/12 (41.7%) | 12/12 (100.0%) |
| Three-way | ADVANCE | 9/12 (75.0%) | 11/12 (91.7%) |
| Three-way | HOLD | 11/12 (91.7%) | 11/12 (91.7%) |
| Three-way | RETREAT | 1/12 (8.3%) | 10/12 (83.3%) |


Both positive pairwise relations have balanced ADVANCE/HOLD/RETREAT winners. In 0>−1,
HOLD wins in two fixtures and RETREAT in one; ADVANCE has no eligible winner cell.
Missing winner cells are no opportunities, not zero success. No world reward was
changed to manufacture balance.

## 15. RETREAT-best secondary test

When RETREAT is verified +1 (state 3, +1>0, +1>−1, and three-way):
S 7/36 (19.4%); O 32/36 (88.9%).
S−O = -69.4 percentage points. Discordant pairs favor S:
0; favor O: 25.
Secondary criterion: **SUPPORTED**; semantic labels hurt.
This uses the preregistered 20-point/8-discordance rule and global gates.

Separately, when RETREAT has 0 and beats offered ADVANCE −1 in state 1:
S 0/12 (0.0%); O 6/12 (50.0%).
That context excludes a globally better HOLD +1, so it is reported separately and
not included in the +1 secondary support test. RETREAT semantics are unchanged.

## 16. Opaque token selection

Overall token selections / times offered: K1 45/108 (41.7%), K2 43/108 (39.8%), K3 56/108 (51.9%).
Stratification by verified offered value follows. The compact results array
`opaque_token_strata` lists exposed state/value/position/token cells. The 18 unexposed
three-way combinations are expanded separately in `verification.json` with zero
opportunities and null rates; no missing cell is interpreted as a zero success rate.
There are 21 of 27 joint token/value/position combinations per state, leaving six
unexposed per state. This limits joint adjustment despite balanced margins.


| Relation | Offered verified value | K1 selected/offered | K2 selected/offered | K3 selected/offered |
|---|---:|---|---|---|
| 0 over −1 | -1 | 6/12 (50.0%) | 6/12 (50.0%) | 6/12 (50.0%) |
| 0 over −1 | +0 | 6/12 (50.0%) | 6/12 (50.0%) | 6/12 (50.0%) |
| +1 over 0 | +0 | 0/12 (0.0%) | 1/12 (8.3%) | 4/12 (33.3%) |
| +1 over 0 | +1 | 10/12 (83.3%) | 9/12 (75.0%) | 12/12 (100.0%) |
| +1 over −1 | -1 | 0/12 (0.0%) | 0/12 (0.0%) | 0/12 (0.0%) |
| +1 over −1 | +1 | 12/12 (100.0%) | 12/12 (100.0%) | 12/12 (100.0%) |
| Three-way | -1 | 0/12 (0.0%) | 0/12 (0.0%) | 0/12 (0.0%) |
| Three-way | +0 | 0/12 (0.0%) | 0/12 (0.0%) | 4/12 (33.3%) |
| Three-way | +1 | 11/12 (91.7%) | 9/12 (75.0%) | 12/12 (100.0%) |


The registered ≥20-point token-asymmetry flags occur for +1 and 0 in both the
+1>0 and three-way conditions (ranges 25.0 and 33.3 percentage points respectively).
K3 has the highest selection-given-exposure rate in each flagged stratum, including
4/12 choices when it represents 0 despite an offered +1. No such flag appears in
0>−1 or +1>−1.
These flags describe selection-given-exposure differences within relation/value
strata. They do not prove a token preference independent of every other factor,
and the aliases are not described as intrinsically neutral.

## 17. Display-position effects

Raw first/second/third selection frequencies and availability denominators are
preserved separately from value-controlled rates below. For pairwise calls, a third
position does not exist. State-specific conditional rates are also in `by_state`.


| Relation | Surface | Higher selected: best shown first | Best shown second | Best shown third | Conditional range | ≥20-point flag |
|---|---|---|---|---|---:|---|
| 0 over −1 | S | 12/18 (66.7%) | 12/18 (66.7%) | not offered | 0.0 pp | False |
| 0 over −1 | O | 18/18 (100.0%) | 0/18 (0.0%) | not offered | 100.0 pp | True |
| +1 over 0 | S | 12/18 (66.7%) | 6/18 (33.3%) | not offered | 33.3 pp | True |
| +1 over 0 | O | 18/18 (100.0%) | 13/18 (72.2%) | not offered | 27.8 pp | True |
| +1 over −1 | S | 17/18 (94.4%) | 11/18 (61.1%) | not offered | 33.3 pp | True |
| +1 over −1 | O | 18/18 (100.0%) | 18/18 (100.0%) | not offered | 0.0 pp | False |
| Three-way | S | 7/12 (58.3%) | 6/12 (50.0%) | 8/12 (66.7%) | 16.7 pp | False |
| Three-way | O | 12/12 (100.0%) | 9/12 (75.0%) | 11/12 (91.7%) | 25.0 pp | True |


An association flag uses a ≥20-point range in higher-value selection conditional
on where the better option was displayed. These are descriptive flags, not p-values
or internal-mechanism claims. Options and Memory entries share order, so the study
cannot separate option-list position from evidence-list position. Seeds, mapping,
and order are balanced prospectively but are not a complete factorial crossing.

## 18. Three-way controls

Verified-value selections in S: 1: 21, 0: 10, -1: 5; invalid: 0.
Verified-value selections in O: 1: 32, 0: 4, -1: 0; invalid: 0.
Best-value selection: S 21/36 (58.3%);
O 32/36 (88.9%).
Strong value-following ≥80% descriptive flag: `{'S': False, 'O': True}`.
Underlying action selections: S `{'ADVANCE': 14, 'HOLD': 21, 'RETREAT': 1}`;
O `{'ADVANCE': 11, 'HOLD': 14, 'RETREAT': 11}`.
Surface-token selections: S `{'ADVANCE': 14, 'HOLD': 21, 'RETREAT': 1}`;
O `{'K1': 11, 'K2': 9, 'K3': 16}`.
Display-position selections/exposures: S `{'1': {'selected': 14, 'opportunities': 36, 'rate': 0.3888888888888889}, '2': {'selected': 9, 'opportunities': 36, 'rate': 0.25}, '3': {'selected': 13, 'opportunities': 36, 'rate': 0.3611111111111111}}`;
O `{'1': {'selected': 16, 'opportunities': 36, 'rate': 0.4444444444444444}, '2': {'selected': 9, 'opportunities': 36, 'rate': 0.25}, '3': {'selected': 11, 'opportunities': 36, 'rate': 0.3055555555555556}}`.
The semantic/opaque difference here is descriptive, not an extra preregistered
primary semantic-effect claim.

## 19. Malformed and out-of-pair controls

All 48 synthetic controls were rejected before world execution:
executions 0, commits 0.
Failure classifications: `{'out_of_pair': 18, 'malformed_or_unknown_label': 30}`.
The pairwise omitted option remains a valid world action elsewhere. Its exclusion
is formatting for this experimental comparison, never negative-Memory prohibition,
learned invalidity, or a new authorization rule. The three-way controls offer all
three unchanged actions. No synthetic response is counted as model behavior.

## 20. Exact replay

Fresh replay made zero inference calls and reproduced all measured calls, full steps,
1,680 fixture setup rows, 48 controls, the registered prompt archive, and the JSON
metric summary exactly. Source hashes and all exact prompts/seeds/options were
verified. This is deterministic replay of recorded responses, not a claim that
fresh stochastic generation must reproduce them. The detailed archive remains
outside the public tree; evidence hashes and reproduction instructions are public.

## 21. Fresh regressions

All eight registered post-study regression commands actually executed and passed,
plus this study's separate exact replay. Prior Adaptive Explorer, Memory Study v1,
and original integration model transcripts and summaries remained identical.
The new suite ran eight tests, including CLI replay, mapping/order balance,
unauthorized projection detection, invalid/out-of-pair rejection, and threshold boundaries.
Command exit codes, execution times, and log hashes are in `verification.json`;
local output paths and raw logs remain outside the public tree.

| Fresh regression | Actual execution |
|---|---|
| Adaptive Explorer v0 replay | 288 recorded calls; complete evidence replay passed |
| Memory Study v1 replay | 224 recorded calls; original transcript and summary identical |
| Original Explorer integration replay | 69 recorded calls; original transcript and summary identical |
| Minimum-framework repair 1 | 177 scenarios; 126 protected passes; 109 direct checks passed |
| Base Framework v0 | 12 tests / 42 scenarios |
| Base Framework v1 | 10 tests / 69 scenarios; 3 expected common-mode false accepts |
| Base Framework v2 | 13 tests / 57 scenarios; 12 A+B blocks; 3 A+B+C and 3 registry false accepts |
| New semantic-prior tests | 8 tests passed; synthetic responses only |

Protected false accepts remained zero in the protected regression cases. The
repair campaign's 15 weakened-control and 6 out-of-model boundary violations
remain visible negative evidence; they are not relabeled as successes.

## 22. Statistical and descriptive limitations

One fixed model/version and prompt, a deterministic four-state world, three selected
initial states, one verified observation per offered action, twelve seeds, and
36 pairs per primary relation. Repeated seeds are not independent model subjects.
The 12 schedules balance marginal identities/positions but are not all 36 alias/order
combinations; seed/order and joint mapping/order effects are not fully isolated.
The neutral-versus-negative winner identities are naturally imbalanced. The fixed
system instruction and complete-history pair formatting differ from prior exploration
studies, so cross-study rate changes cannot be attributed solely to labels.

Thresholds are preregistered descriptive rules, not significance tests, confidence
intervals, or evidence about internal reasoning. Opaque tokens may carry priors.
Frequency patterns alone do not prove causal understanding, intrinsic neutrality,
pretraining mechanisms, or generalization. No contradiction/nonstationarity task,
model training, weight update, RL, general grounding, AGI, or self-improvement was tested.

## 23. Narrowest defensible conclusion


- 0 over −1: S 24/36 (66.7%); O 18/36 (50.0%); semantic-prior effect **NOT ESTABLISHED** (no established effect).

- +1 over 0: S 18/36 (50.0%); O 31/36 (86.1%); semantic-prior effect **SUPPORTED** (semantic labels hurt).

- +1 over −1: S 28/36 (77.8%); O 36/36 (100.0%); semantic-prior effect **SUPPORTED** (semantic labels hurt).


The findings concern which offered action this model proposed from these verified
histories under these exact surface renderings. They do not establish a universal
winner between verified experience and pretrained priors. Framework integrity was
**PASS** and all authorization remained outside the model.
Earlier findings remain unchanged.

**Verified positive evidence guided proposals more consistently under the tested
opaque rendering. Original names interfered, most clearly when RETREAT was best.**
The RETREAT +1 secondary comparison meets its frozen criterion: 7/36 under S
versus 32/36 under O, with 25 discordances favoring O and none favoring S.
That pattern associates the literal-name rendering with reduced selection of the
verified-best RETREAT action in this configuration; it does not identify the
model's internal reasoning or isolate RETREAT's name from the competing labels.

There is also a distinct failure to prefer 0 over −1 reliably: O always chooses
the first option, while S follows HOLD and avoids RETREAT in the tested neutral
winner cells. Renaming therefore does not make value-following general or remove
presentation effects. K3 asymmetries and conditional position differences further
limit any claim of neutral aliases. The data support neither universal evidence
dominance nor a single lexical explanation of every error.

## 24. Recommendation and stop

Keep the model in Explorer only. The next useful experiment would be a separately
preregistered replication that independently crosses mapping, option order, and
evidence order, with explicit 0>−1 and RETREAT-best comparisons. This would test
whether the observed first-position pattern and RETREAT gap persist when their
remaining presentation confounds are separated. Fix its sample budget and criteria
before any new inference; do not assume renaming makes behavior unbiased.
This is a recommendation only. No architecture or contradiction experiment was
started. Public main, prior results, and historical tags remain unchanged; no push.

[Compact results](../experiments/model_explorer_semantic_prior_study_v0/results.json) ·
[Reproduction](../experiments/model_explorer_semantic_prior_study_v0/README.md) ·
[Verification](../experiments/model_explorer_semantic_prior_study_v0/verification.json).
