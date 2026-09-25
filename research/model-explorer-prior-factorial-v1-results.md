# Prior factorial v1 — results

Framework integrity: **PASS**. **216 real calls**;
no sample extension. **RETREAT lexical interference replicated** in both positive
targets and both opaque families. Value stability across both opaque families and
all crossed positions passed only for +1>−1; Target C dominance remained unresolved.
The prior semantic-prior v0 findings and all earlier results
remain unchanged. This study isolates three complete-history comparisons; it is
not an adaptive exploration or contradiction experiment.

## 1. Frozen identities

Parent `de3048ea6061ae6b7b26ac95d3a06441bba9d1b9`. Framework checkpoint
`8ec32c839133df7ddd76448063b5f765c20155da`, all 23 source hashes unchanged.
Preregistration commit `121be1d`; implementation `9e13eec` was tested and committed
before inference. No source, prompt, fixture, mapping, order schedule, or analysis
rule changed after inference began.

Model dolphin-mixtral:latest, Ollama 0.1.16, GGUF 47B Q4_0.
Manifest `4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`;
weights `bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3`.
Both the manifest and complete weight-file bytes were hashed before inference.
Temperature 0.2, top_p 0.9, top_k 40, num_predict 16, num_ctx 2048,
repeat_penalty 1.1; seeds 30001–30006. Sequential stateless local calls; no training,
weight update, resampling, correction, or model authority.

## 2. Exact design and preregistration

[Preregistration](model-explorer-prior-factorial-v1-preregistration.md) freezes the
exact fixtures, prompts, aliases, schedule, metrics, classifications, and stop rules.
The prospective 216-prompt annex SHA-256 is `b4781385f73737e8d2abe0d895686977979984132c55da00cc00013635655be5`.
It was reconstructed byte-for-byte before inference. Three targets × three families
× six mappings/seeds × two option orders × two evidence orders = 216 calls.

The unchanged system instruction is:

> Choose one available action using only the verified prior outcomes shown. Higher verified consequences are preferable. Reply with exactly one available action and no explanation.

User JSON serialization is `json.dumps(payload,sort_keys=True,separators=(",",":"))`.
Only state, available_actions and VERIFIED_PRIOR_OUTCOMES appear. Evidence entries
contain surface_action and authorized observed_consequences. No future outcomes,
canonical names in opaque conditions, mappings, recommendation, or authorizer state.

Support requires all 216 real calls complete/valid, integrity PASS, and all 14 controls
rejected. Matched surface differences require ≥20 percentage points and ≥8 favorable
discordances among 24 pairs. RETREAT replication requires both opaque families to
clear that criterion in each positive target separately. Strong value following is
≥20/24; stability across positions additionally requires ≥5/6 in every crossed cell.
These are descriptive criteria, not significance tests.

## 3. Authorized fixture confirmation

Reuse the earlier fixture constructor unchanged. Five ordinary authorized actions
ADVANCE → RETREAT → HOLD → RETREAT → ADVANCE return to the initial state with Map
version 5, five retained authorized records, and next transaction 6. Epoch=800+state.
Preflight ran ten scripted transactions, five each for states 1 and 3. No fabricated
Memory or directly inserted action/consequence examples. The model's sixth decision
uses an independently rebuilt fixture every time.

| Target | State | Higher authorized observation | Lower authorized observation |
|---|---:|---|---|
| A | 3 | RETREAT +1 | HOLD 0 |
| B | 3 | RETREAT +1 | ADVANCE −1 |
| C | 1 | RETREAT 0 | ADVANCE −1 |

All offered actions have exactly one current-state verified observation, taken from
the existing authorized history. Options and evidence contents are derived from
those records, not a model-adapter oracle lookup. All fixtures matched preflight.
The remaining third action is valid in the framework but not offered in that call.

## 4. Surface families

S: ADVANCE/HOLD/RETREAT. O1: K1/K2/K3. O2: Q7/M4/Z2, chosen and frozen without
model testing. Full maps and protected records stay in the separate evidence archive;
they are never model input. Both opaque families receive identical factual evidence
in the matching positions. Neither is assumed neutral.

## 5. Alias mappings and seeds

Both opaque families use all six permutations of ADVANCE/HOLD/RETREAT in that
canonical order. Mapping index j=0..5 is paired with seed 30001+j, across all four
order cells and both vocabularies. S uses six matched seeds with its identity map.
Each token maps to each underlying action eight times per target, 24 across targets.
The complete three-action mapping is retained even when only two options are offered.

Family execution order rotates through all six S/O1/O2 permutations, indexed by
(j + target_index + 2*(higher_option_position−1) + relative_evidence_index) modulo 6.
There are 72 checked matched triples; S–O1, S–O2 and O1–O2 each
have 24 matched pairs per target with identical protected snapshot, underlying
options/evidence order, decision number, seed and sampler.

## 6. Option-order crossing

Each mapping uses higher option first and second independently. Each target/family
has 12 calls at either position. Option order is not derived from the alias mapping.

## 7. Evidence-order crossing

For each option order, the evidence list is shown once in that order and once
reversed. Thus all four higher-option/higher-evidence combinations occur once per
mapping/seed, six times per target/family. Evidence facts are unchanged. This removes
the prior coupling between the two list orders; seed and mapping remain coupled.

## 8. Actual real calls

216 real calls, 216 measured decisions;
complete=True. Each family contributes 72 calls, 24 per target. No extra
call, optional extension, replacement, or post-inference tuning. Fourteen separate
synthetic controls are not counted as model behavior. Setup totals are
1150 authorized scripted transactions: 1,080 measured-fixture
setup and 70 control setup, separate from ten prospective preflight transactions. Each CLI invocation also reconstructs those ten
annex-validation transactions before the measured/control campaign; they are scripted
validation, outside the 1,150 emitted setup rows and outside model-call counts.

## 9. Integrity and authority

216/216 valid proposals, 0
invalid, 216 measured authorized commits. Framework integrity
**PASS**; observed violations: `{}`.
All 230 measured/control projections were checked.

Observed protected false accepts, unauthorized Memory commits, stale accepts,
duplicate authorizations, malformed/out-of-pair commits, direct protected model
mutations, prediction rewrites and bound violations were zero. Existing authority
and provenance mechanisms remain unchanged. This is a bounded fixture result,
not protection against new arbitrary faults. Observed maxima: `{'memory': 6, 'pairs': 6, 'packages': 6, 'trace': 18, 'package_trace': 24, 'staged': 0, 'map_quarantine': 0, 'memory_quarantine': 0}`.

Model reads authorized state and verified rendered evidence; proposes one finite
displayed label; directly mutates no protected state; authorizes nothing.

## 10. Target A — RETREAT +1 over HOLD 0

| Family | Higher option position | Higher evidence position | Higher selected | First option selected | First evidence selected |
|---|---|---|---|---|---|
| S | 1 | 1 | 0/6 (0.0%) | 0/6 (0.0%) | 0/6 (0.0%) |
| S | 1 | 2 | 0/6 (0.0%) | 0/6 (0.0%) | 6/6 (100.0%) |
| S | 2 | 1 | 0/6 (0.0%) | 6/6 (100.0%) | 0/6 (0.0%) |
| S | 2 | 2 | 0/6 (0.0%) | 6/6 (100.0%) | 6/6 (100.0%) |
| O1 | 1 | 1 | 6/6 (100.0%) | 6/6 (100.0%) | 6/6 (100.0%) |
| O1 | 1 | 2 | 6/6 (100.0%) | 6/6 (100.0%) | 0/6 (0.0%) |
| O1 | 2 | 1 | 6/6 (100.0%) | 0/6 (0.0%) | 6/6 (100.0%) |
| O1 | 2 | 2 | 4/6 (66.7%) | 2/6 (33.3%) | 2/6 (33.3%) |
| O2 | 1 | 1 | 6/6 (100.0%) | 6/6 (100.0%) | 6/6 (100.0%) |
| O2 | 1 | 2 | 6/6 (100.0%) | 6/6 (100.0%) | 0/6 (0.0%) |
| O2 | 2 | 1 | 6/6 (100.0%) | 0/6 (0.0%) | 6/6 (100.0%) |
| O2 | 2 | 2 | 4/6 (66.7%) | 2/6 (33.3%) | 2/6 (33.3%) |

After displaying the crossed cells, the marginal results are:

| Family | Higher selected | Strong ≥80% | Stable across all positions | Selected +1 / 0 / −1 |
|---|---|---|---|---|
| S | 0/24 (0.0%) | False | False | 0 / 24 / 0 |
| O1 | 22/24 (91.7%) | True | False | 22 / 2 / 0 |
| O2 | 22/24 (91.7%) | True | False | 22 / 2 / 0 |

Verified-value following replicated across **both opaque families**: NOT ESTABLISHED. Stable across **all three representations**: NOT ESTABLISHED.

## 11. Target B — RETREAT +1 over ADVANCE −1

| Family | Higher option position | Higher evidence position | Higher selected | First option selected | First evidence selected |
|---|---|---|---|---|---|
| S | 1 | 1 | 2/6 (33.3%) | 2/6 (33.3%) | 2/6 (33.3%) |
| S | 1 | 2 | 0/6 (0.0%) | 0/6 (0.0%) | 6/6 (100.0%) |
| S | 2 | 1 | 0/6 (0.0%) | 6/6 (100.0%) | 0/6 (0.0%) |
| S | 2 | 2 | 0/6 (0.0%) | 6/6 (100.0%) | 6/6 (100.0%) |
| O1 | 1 | 1 | 6/6 (100.0%) | 6/6 (100.0%) | 6/6 (100.0%) |
| O1 | 1 | 2 | 6/6 (100.0%) | 6/6 (100.0%) | 0/6 (0.0%) |
| O1 | 2 | 1 | 6/6 (100.0%) | 0/6 (0.0%) | 6/6 (100.0%) |
| O1 | 2 | 2 | 6/6 (100.0%) | 0/6 (0.0%) | 0/6 (0.0%) |
| O2 | 1 | 1 | 6/6 (100.0%) | 6/6 (100.0%) | 6/6 (100.0%) |
| O2 | 1 | 2 | 6/6 (100.0%) | 6/6 (100.0%) | 0/6 (0.0%) |
| O2 | 2 | 1 | 5/6 (83.3%) | 1/6 (16.7%) | 5/6 (83.3%) |
| O2 | 2 | 2 | 6/6 (100.0%) | 0/6 (0.0%) | 0/6 (0.0%) |

After displaying the crossed cells, the marginal results are:

| Family | Higher selected | Strong ≥80% | Stable across all positions | Selected +1 / 0 / −1 |
|---|---|---|---|---|
| S | 2/24 (8.3%) | False | False | 2 / 0 / 22 |
| O1 | 24/24 (100.0%) | True | True | 24 / 0 / 0 |
| O2 | 23/24 (95.8%) | True | True | 23 / 0 / 1 |

Verified-value following replicated across **both opaque families**: SUPPORTED. Stable across **all three representations**: NOT ESTABLISHED.

## 12. Target C — RETREAT 0 over ADVANCE −1

| Family | Higher option position | Higher evidence position | Higher selected | First option selected | First evidence selected |
|---|---|---|---|---|---|
| S | 1 | 1 | 0/6 (0.0%) | 0/6 (0.0%) | 0/6 (0.0%) |
| S | 1 | 2 | 0/6 (0.0%) | 0/6 (0.0%) | 6/6 (100.0%) |
| S | 2 | 1 | 0/6 (0.0%) | 6/6 (100.0%) | 0/6 (0.0%) |
| S | 2 | 2 | 0/6 (0.0%) | 6/6 (100.0%) | 6/6 (100.0%) |
| O1 | 1 | 1 | 6/6 (100.0%) | 6/6 (100.0%) | 6/6 (100.0%) |
| O1 | 1 | 2 | 6/6 (100.0%) | 6/6 (100.0%) | 0/6 (0.0%) |
| O1 | 2 | 1 | 6/6 (100.0%) | 0/6 (0.0%) | 6/6 (100.0%) |
| O1 | 2 | 2 | 0/6 (0.0%) | 6/6 (100.0%) | 6/6 (100.0%) |
| O2 | 1 | 1 | 4/6 (66.7%) | 4/6 (66.7%) | 4/6 (66.7%) |
| O2 | 1 | 2 | 6/6 (100.0%) | 6/6 (100.0%) | 0/6 (0.0%) |
| O2 | 2 | 1 | 1/6 (16.7%) | 5/6 (83.3%) | 1/6 (16.7%) |
| O2 | 2 | 2 | 2/6 (33.3%) | 4/6 (66.7%) | 4/6 (66.7%) |

After displaying the crossed cells, the marginal results are:

| Family | Higher selected | Strong ≥80% | Stable across all positions | Selected +1 / 0 / −1 |
|---|---|---|---|---|
| S | 0/24 (0.0%) | False | False | 0 / 0 / 24 |
| O1 | 18/24 (75.0%) | False | False | 0 / 18 / 6 |
| O2 | 13/24 (54.2%) | False | False | 0 / 13 / 11 |

Verified-value following replicated across **both opaque families**: NOT ESTABLISHED. Stable across **all three representations**: NOT ESTABLISHED.

## 13. Semantic versus O1

| Target | S | O1 | O1−S | Favor S | Favor O1 | Concordant | Surface difference |
|---|---|---|---|---|---|---|---|
| A | 0/24 (0.0%) | 22/24 (91.7%) | +91.7 pp | 0 | 22 | 2 | SUPPORTED |
| B | 2/24 (8.3%) | 24/24 (100.0%) | +91.7 pp | 0 | 22 | 2 | SUPPORTED |
| C | 0/24 (0.0%) | 18/24 (75.0%) | +75.0 pp | 0 | 18 | 6 | SUPPORTED |

## 14. Semantic versus O2

| Target | S | O2 | O2−S | Favor S | Favor O2 | Concordant | Surface difference |
|---|---|---|---|---|---|---|---|
| A | 0/24 (0.0%) | 22/24 (91.7%) | +91.7 pp | 0 | 22 | 2 | SUPPORTED |
| B | 2/24 (8.3%) | 23/24 (95.8%) | +87.5 pp | 0 | 21 | 3 | SUPPORTED |
| C | 0/24 (0.0%) | 13/24 (54.2%) | +54.2 pp | 0 | 13 | 11 | SUPPORTED |

Both comparisons use the same matched S observations; they are not independent
replications of the semantic arm. Interpret each target separately before any pooling.

## 15. O1 versus O2

| Target | O1 | O2 | O2−O1 | Favor O1 | Favor O2 | Concordant | Surface difference |
|---|---|---|---|---|---|---|---|
| A | 22/24 (91.7%) | 22/24 (91.7%) | +0.0 pp | 2 | 2 | 20 | NOT ESTABLISHED |
| B | 24/24 (100.0%) | 23/24 (95.8%) | -4.2 pp | 1 | 0 | 23 | NOT ESTABLISHED |
| C | 18/24 (75.0%) | 13/24 (54.2%) | -20.8 pp | 7 | 2 | 15 | NOT ESTABLISHED |


Target A: opaque vocabulary dependence **NOT ESTABLISHED**; basis: no frozen criterion met.

Target B: opaque vocabulary dependence **NOT ESTABLISHED**; basis: no frozen criterion met.

Target C: opaque vocabulary dependence **NOT ESTABLISHED**; basis: no frozen criterion met.


Not established means the criterion was not met, not equivalence of vocabularies.

## 16. Option-position effects

Higher-choice rates below compare higher option first versus second. Conditional
differences hold higher evidence position fixed (first / second). A support flag
requires ≥20 points marginally and ≥20 in the same direction in both strata.

| Target | Family | Higher at first | Higher at second | First−second | Conditional differences (pp) | Effect | Favored position |
|---|---|---|---|---|---|---|---|
| A | S | 0/12 (0.0%) | 0/12 (0.0%) | +0.0 pp | +0.0 / +0.0 | NOT ESTABLISHED | — |
| A | O1 | 12/12 (100.0%) | 10/12 (83.3%) | +16.7 pp | +0.0 / +33.3 | NOT ESTABLISHED | — |
| A | O2 | 12/12 (100.0%) | 10/12 (83.3%) | +16.7 pp | +0.0 / +33.3 | NOT ESTABLISHED | — |
| B | S | 2/12 (16.7%) | 0/12 (0.0%) | +16.7 pp | +33.3 / +0.0 | NOT ESTABLISHED | — |
| B | O1 | 12/12 (100.0%) | 12/12 (100.0%) | +0.0 pp | +0.0 / +0.0 | NOT ESTABLISHED | — |
| B | O2 | 12/12 (100.0%) | 11/12 (91.7%) | +8.3 pp | +16.7 / +0.0 | NOT ESTABLISHED | — |
| C | S | 0/12 (0.0%) | 0/12 (0.0%) | +0.0 pp | +0.0 / +0.0 | NOT ESTABLISHED | — |
| C | O1 | 12/12 (100.0%) | 6/12 (50.0%) | +50.0 pp | +0.0 / +100.0 | NOT ESTABLISHED | — |
| C | O2 | 10/12 (83.3%) | 3/12 (25.0%) | +58.3 pp | +50.0 / +66.7 | SUPPORTED | 1 |

## 17. Evidence-position effects

The analogous contrasts hold higher option position fixed (first / second).
The direction indicates favored evidence position, not which option was first.

| Target | Family | Higher at first | Higher at second | First−second | Conditional differences (pp) | Effect | Favored position |
|---|---|---|---|---|---|---|---|
| A | S | 0/12 (0.0%) | 0/12 (0.0%) | +0.0 pp | +0.0 / +0.0 | NOT ESTABLISHED | — |
| A | O1 | 12/12 (100.0%) | 10/12 (83.3%) | +16.7 pp | +0.0 / +33.3 | NOT ESTABLISHED | — |
| A | O2 | 12/12 (100.0%) | 10/12 (83.3%) | +16.7 pp | +0.0 / +33.3 | NOT ESTABLISHED | — |
| B | S | 2/12 (16.7%) | 0/12 (0.0%) | +16.7 pp | +33.3 / +0.0 | NOT ESTABLISHED | — |
| B | O1 | 12/12 (100.0%) | 12/12 (100.0%) | +0.0 pp | +0.0 / +0.0 | NOT ESTABLISHED | — |
| B | O2 | 11/12 (91.7%) | 12/12 (100.0%) | -8.3 pp | +0.0 / -16.7 | NOT ESTABLISHED | — |
| C | S | 0/12 (0.0%) | 0/12 (0.0%) | +0.0 pp | +0.0 / +0.0 | NOT ESTABLISHED | — |
| C | O1 | 12/12 (100.0%) | 6/12 (50.0%) | +50.0 pp | +0.0 / +100.0 | NOT ESTABLISHED | — |
| C | O2 | 5/12 (41.7%) | 8/12 (66.7%) | -25.0 pp | -33.3 / -16.7 | NOT ESTABLISHED | — |

## 18. Option × evidence interaction

All four cells and both raw first-position rates appear explicitly in sections
10–12 before marginal results. With p_oe denoting higher-choice rate, report
I=(p11+p22)−(p12+p21); agreement difference=I/2:


| Target | Family | Interaction I | Agreement difference |
|---|---|---|---|
| A | S | +0.000 | +0.000 |
| A | O1 | -0.333 | -0.167 |
| A | O2 | -0.333 | -0.167 |
| B | S | +0.333 | +0.167 |
| B | O1 | +0.000 | +0.000 |
| B | O2 | +0.167 | +0.083 |
| C | S | +0.000 | +0.000 |
| C | O1 | -1.000 | -0.500 |
| C | O2 | -0.167 | -0.083 |


## 19. Opaque token effects

Selection-given-exposure below conditions on target, verified value and underlying
action. Every token has eight exposures per row. The compact evidence also contains
full token/action/value/option-position/evidence-position joint tables with two
exposures per cell, plus token and position marginals. No missing joint strata for
offered actions. Unoffered actions have no decision opportunities.


| Family | Target | Value | Underlying action | First vocabulary token | Second vocabulary token | Third vocabulary token |
|---|---|---|---|---|---|---|
| O1 | A | 1 | RETREAT | K1 7/8 (87.5%) | K2 7/8 (87.5%) | K3 8/8 (100.0%) |
| O1 | A | 0 | HOLD | K1 0/8 (0.0%) | K2 0/8 (0.0%) | K3 2/8 (25.0%) |
| O1 | B | 1 | RETREAT | K1 8/8 (100.0%) | K2 8/8 (100.0%) | K3 8/8 (100.0%) |
| O1 | B | -1 | ADVANCE | K1 0/8 (0.0%) | K2 0/8 (0.0%) | K3 0/8 (0.0%) |
| O1 | C | 0 | RETREAT | K1 6/8 (75.0%) | K2 6/8 (75.0%) | K3 6/8 (75.0%) |
| O1 | C | -1 | ADVANCE | K1 2/8 (25.0%) | K2 2/8 (25.0%) | K3 2/8 (25.0%) |
| O2 | A | 1 | RETREAT | Q7 8/8 (100.0%) | M4 8/8 (100.0%) | Z2 6/8 (75.0%) |
| O2 | A | 0 | HOLD | Q7 1/8 (12.5%) | M4 1/8 (12.5%) | Z2 0/8 (0.0%) |
| O2 | B | 1 | RETREAT | Q7 8/8 (100.0%) | M4 8/8 (100.0%) | Z2 7/8 (87.5%) |
| O2 | B | -1 | ADVANCE | Q7 0/8 (0.0%) | M4 1/8 (12.5%) | Z2 0/8 (0.0%) |
| O2 | C | 0 | RETREAT | Q7 6/8 (75.0%) | M4 5/8 (62.5%) | Z2 2/8 (25.0%) |
| O2 | C | -1 | ADVANCE | Q7 5/8 (62.5%) | M4 5/8 (62.5%) | Z2 1/8 (12.5%) |


Registered ≥20-point token-asymmetry flags: O1/A/value +0 (25.0 pp), O2/A/value +1 (25.0 pp), O2/C/value +0 (50.0 pp), O2/C/value -1 (50.0 pp).


These are descriptive associations within this campaign. Mapping/order/evidence
are fully crossed, but seed and mapping are not independently crossed. Token
frequency patterns do not identify an intrinsic token preference or internal cause.

## 20. RETREAT lexical-interference replication


| Target | Both opaque families meet criterion |
|---|---|
| A | SUPPORTED |
| B | SUPPORTED |


Overall A-and-B replication: **SUPPORTED**. Both positive targets must pass separately; neither a pooled A+B rate nor one vocabulary can substitute for the frozen rule. All higher-value actions here are RETREAT, so any label association is scoped to these comparisons, including their competing labels.


## 21. Target C order-effect classification

Frozen categories require ≥5/6 matching selections in every crossed cell: first
option, first evidence entry, or higher value respectively. Conjunction requires
opposite ≥5/6 versus ≤1/6 higher-choice patterns in aligned and opposed cells,
plus ≥50-point agreement difference. All qualifying labels are retained; no
preferred interpretation is selected after seeing data.


| Family | Supported classification(s) | Conjunction favors |
|---|---|---|
| S | UNRESOLVED | — |
| O1 | UNRESOLVED | — |
| O2 | UNRESOLVED | — |


## 22. Bounded rejection controls

14 synthetic controls; executions 0, commits
0. Unknown alias, omitted action, multiple labels and explanatory
text were tested in every family; canonical RETREAT was additionally tested in O1
and O2. All were rejected before execution/commit. This is a 14-case admission check,
not a new fault campaign or model-behavior sample. Excluding the third displayed
option does not remove an allowed world action or rewrite negative Memory.

## 23. Exact replay

Fresh replay performed zero inference and reproduced the 216 call records, measured
steps, all 1,150 setup rows, 14 controls, exact registered annex, and JSON summary.
All five detailed evidence files are byte-identical; source hashes match. Raw
mappings, prompts, protected snapshots and responses remain outside the public tree.
The compact results were copied unchanged from the real run. Replaying recorded
responses does not imply fresh stochastic inference will reproduce them.

## 24. Fresh regressions

This study's replay and all nine additional requested commands actually ran and
passed. Four previous model transcripts and summaries remained identical.
Execution timestamps, exit codes and log hashes are in `verification.json`.

| Fresh check | Actual execution |
|---|---|
| Semantic-prior v0 replay | 288 recorded calls; byte-identical detailed evidence |
| Adaptive Explorer v0 replay | 288 recorded calls; complete exact replay |
| Memory Study v1 replay | 224 recorded calls; transcript/summary identical |
| Original Explorer integration replay | 69 recorded calls; transcript/summary identical |
| Minimum-framework repair 1 | 177 scenarios; 126 protected passes; 109 direct checks passed |
| Base framework v0 | 12 tests / 42 scenarios |
| Base framework v1 | 10 tests / 69 scenarios; 3 expected common-mode false accepts |
| Base framework v2 | 13 tests / 57 scenarios; 12 A+B blocks; 3 A+B+C and 3 registry false accepts |
| New factorial tests | 9 synthetic tests, including crossing, parser, classification thresholds and CLI replay |

Protected false accepts stayed zero in protected regression cases. The repair
campaign's 15 weakened-control and 6 out-of-model boundary violations remain visible
negative evidence. They are not relabeled as successful protection.

## 25. Limitations

One model/configuration, fixed instruction, two opaque vocabularies, two states,
three targeted contrasts, six seeds and only six calls per crossed order cell.
Each offered action has one authorized observation. No other winner identity is
represented: RETREAT is always the higher option. The third world action is not
available in these pairwise decisions. The neutral comparison in state 1 omits
HOLD +1; its result describes the offered pair, not the globally best action.

Mapping is fully crossed with both orders, but each mapping uses one seed. Token
identity and seed are therefore not fully separated; repetitions do not create
independent models. Tokenization, lexical familiarity and semantics are not isolated
internal mechanisms. The two opaque comparisons share S observations. No inferential
significance, equivalence, population generalization, or causal internal reasoning
is established by these descriptive thresholds. A NOT ESTABLISHED result must
remain such; the sample was not enlarged to obtain a stronger claim.

No neutral representation, general grounding, AGI, self-improvement, training or
weight learning claim. Contradiction revision remains UNTESTED. The bounded framework
trust assumptions and historical negative controls remain unchanged.

## 26. Narrowest defensible conclusion


Target A: S 0/24 (0.0%); O1 22/24 (91.7%); O2 22/24 (91.7%).

Target B: S 2/24 (8.3%); O1 24/24 (100.0%); O2 23/24 (95.8%).

Target C: S 0/24 (0.0%); O1 18/24 (75.0%); O2 13/24 (54.2%).


**RETREAT lexical interference replicated in both positive targets and both
opaque families under the frozen descriptive rule.** For A, each opaque family
improved higher-value selection by 91.7 percentage points, with 22 favorable and
zero reverse discordances. For B, O1 improved by 91.7 points (22 favorable, zero
reverse), and O2 by 87.5 points (21 favorable, zero reverse). The result concerns
these complete-history comparisons and cannot isolate RETREAT's literal name from
the other labels or identify an internal pretraining mechanism.

**Verified relational value was stable across both opaque vocabularies and all
crossed positions only for Target B (+1>−1).** O1 selected higher 24/24 and O2
23/24, with at least 5/6 in every crossed cell. Target A's 22/24 in both families
meets strong marginal value-following, but each falls to 4/6 when both the option
and its evidence appear second, failing the stricter stability criterion. No target
meets value stability across all three representations because S remains weak.

**Target C does not support one general explanation for the earlier coupled-order
pattern.** S always selected ADVANCE −1 over verified RETREAT 0. O1 selected the
higher action 6/6 whenever it appeared first in at least one list, and 0/6 when it
appeared second in both. This observed pattern is neither first-option dominance,
first-evidence dominance, nor the preregistered aligned-versus-opposed conjunction
pattern. It remains UNRESOLVED under those categories. O1's +50-point marginal
option and evidence differences each disappear in one conditioned stratum, so
neither clears the separately frozen position-effect rule.

O2 shows a supported option-position effect in C: higher-selection is 10/12 with
the higher option first versus 3/12 second (+58.3 points), with conditional gaps
of +50.0 and +66.7 points at fixed evidence positions. It still fails the stronger
first-option-dominance criterion because first-option choices fall below 5/6 in
two crossed cells. No evidence-position effect passes the frozen conditioned rule.
All three C dominance classifications therefore remain UNRESOLVED despite this
narrower supported O2 option effect.

C's opaque rates differ by 20.8 points (18/24 O1 versus 13/24 O2), but only seven
discordances favor O1 and two favor O2. The required eight favorable discordances
are absent, and neither vocabulary has a supported dominance classification.
**OPAQUE VOCABULARY DEPENDENCE: NOT ESTABLISHED** by the frozen criteria. This does
not hide the visible table differences or establish vocabulary equivalence. Token
asymmetry flags likewise remain descriptive, with mapping/seed confounding retained.

The targeted C comparisons against S pass the new study's surface-difference
criteria; they do not revise the previous v0 pooled 0>−1 finding. Target selection,
independent evidence order, seeds and vocabulary design differ. Earlier results,
including untested contradiction revision, remain unchanged.

The answer to stability across changes of representation is therefore conditional:
positive-over-negative value following survives both tested opaque vocabularies
and positions, but verified value does not dominate across every representation
or every tested relation. Opacity supplies no general guarantee of neutrality.

## 27. Recommendation and stop

Keep the framework frozen and the model in Explorer. This bounded study is
sufficient to document the positive RETREAT replication and its limitations;
there is no need to expand A/B merely to obtain more favorable numbers.

If the next research decision requires resolving the order mechanism, restrict a
new preregistered follow-up to Target C. Freeze a direct test of the observed
"higher appears first in at least one list" pattern and the O2 option-position
pattern, with a small prospective budget and seed assignments rotated across
mappings. Treat these as hypotheses motivated by this result, not discoveries
already supported by the old categories. Agree the smallest useful design before
additional calls; do not automatically broaden the campaign or relax thresholds.

No further inference, architecture change, nonstationarity or model promotion was
started. Public main and historical tags remain unchanged; nothing was pushed.

[Compact results](../experiments/model_explorer_prior_factorial_v1/results.json) ·
[Verification](../experiments/model_explorer_prior_factorial_v1/verification.json) ·
[Reproduction](../experiments/model_explorer_prior_factorial_v1/README.md).
