# Prior factorial v1 — preregistration

Freeze before study implementation or inference. Parent:
`de3048ea6061ae6b7b26ac95d3a06441bba9d1b9`.
Framework checkpoint: `8ec32c839133df7ddd76448063b5f765c20155da`.
The unchanged 23 framework source hashes and model digests are in this experiment's
`frozen-framework.json`. Earlier findings are unchanged. No framework component,
world transition, action semantics, evidence source, registry, provenance, prediction
latch, authorization, or bound changes. Explorer is the only model role.

## Small bounded design and prospective evidence

Exactly **216 real calls**. No optional extension, additional vocabulary, three-way
condition, or new fault campaign. Four crossed order cells, six mappings/seeds,
three targets, and three families are the complete design requested. Fourteen
separate synthetic rejection controls exercise the parser and existing admission
boundary. No synthetic response is a model observation.

Normal authorized preflight ran ten scripted transactions: five per state fixture.
The resulting complete protected snapshots, setup rows, all 216 exact prompt
strings/descriptors, and 14 control specifications are retained outside the public
tree as `registered-fixtures-and-prompts.json`, SHA-256:
`b4781385f73737e8d2abe0d895686977979984132c55da00cc00013635655be5`.
This digest is committed in `registration-digests.json`. The implementation must
reconstruct exactly these bytes before inference. No model call selected tokens,
prompts, seeds, schedules, or thresholds.

## Authorized fixtures

Reuse the existing semantic-prior v0 fixture constructor unchanged. Initialize the
ordinary framework and world at state 1 or 3, epoch 800 + state. Execute ADVANCE,
RETREAT, HOLD, RETREAT, ADVANCE through normal proposal, prediction, world execution,
A/B/C evidence, package authorization, and Memory commit. This returns to the
initial state with five authorized records, Map version 5, and next transaction 6.
No fabricated Memory or direct insertion. Reconstruct independently for every call.

Preflight obtained these current-state records through authorized transactions:

| State | ADVANCE | HOLD | RETREAT |
|---:|---:|---:|---:|
| 1 | −1 | +1 | 0 |
| 3 | −1 | 0 | +1 |

Each value has one verified observation (transactions 1, 3, 4 for ADVANCE, HOLD,
RETREAT respectively). All five original records remain retained; only the two
offered actions' current-state records enter the model-visible projection.

| Target | State | Higher observed action | Lower observed action |
|---|---:|---|---|
| A | 3 | RETREAT +1 | HOLD 0 |
| B | 3 | RETREAT +1 | ADVANCE −1 |
| C | 1 | RETREAT 0 | ADVANCE −1 |

Determine options and empirical means from actual authorized records; these tables
are preflight assertions, never adapter oracle lookups. Stop before inference if
any fixture or comparison differs. Every measured decision is decision six. The
omitted third action stays generally valid; exclusion is fixed proposal formatting,
not a learned prohibition. No exploration, contradiction, or nonstationarity task.

## Model and exact prompts

Unchanged `dolphin-mixtral:latest`, Ollama 0.1.16, GGUF 47B Q4_0.
Manifest `4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`.
Weights `bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3`.
Temperature 0.2, top_p 0.9, top_k 40, num_predict 16, num_ctx 2048,
repeat_penalty 1.1. Six seeds: **30001–30006**. Sequential stateless local
`/api/generate`, stream=false; no context carryover, retries, resampling, fallback,
majority vote, output correction, model tools, training, or weight updates.
Installed template unchanged:
`<|im_start|>system\n{{ .System }}<|im_end|>\n<|im_start|>user\n{{ .Prompt }}<|im_end|>\n<|im_start|>assistant\n`.

Exact unchanged system instruction in all families:

> Choose one available action using only the verified prior outcomes shown. Higher verified consequences are preferable. Reply with exactly one available action and no explanation.

Exact user prompt: `json.dumps(payload,sort_keys=True,separators=(",",":"))`.
Only state, available_actions, VERIFIED_PRIOR_OUTCOMES. Each evidence entry has
surface_action and observed_consequences. The latter is the authorized observation
list, not a recommendation. No UNTRIED, hidden canonical identity in opaque calls,
mapping, authorizer state, future consequence, evaluator answer, or world table.
Only the separately registered option/evidence orders and surface labels vary.
All exact serialized prompts are frozen in the prospective annex.

## Families, mappings, and independent orders

S uses original ADVANCE, HOLD, RETREAT. O1 uses K1, K2, K3.
O2 uses **Q7, M4, Z2** in that fixed token order, chosen without testing.
Neither opaque set is assumed neutral.

Let P be `itertools.permutations(("ADVANCE","HOLD","RETREAT"))`:

| Index | First token maps to | Second token maps to | Third token maps to |
|---:|---|---|---|
| 0 | ADVANCE | HOLD | RETREAT |
| 1 | ADVANCE | RETREAT | HOLD |
| 2 | HOLD | ADVANCE | RETREAT |
| 3 | HOLD | RETREAT | ADVANCE |
| 4 | RETREAT | ADVANCE | HOLD |
| 5 | RETREAT | HOLD | ADVANCE |

Seed index j = 0..5; seed = 30001 + j. Both opaque families use mapping P[j];
S uses the identity mapping and its six seeds as repeats. Every opaque mapping
includes all three original actions, including the omitted action.
Each mapping is crossed with higher option position 1 or 2, and evidence order
same or reversed relative to options. Therefore each mapping contains all four
(higher option position, higher evidence position) cells: (1,1), (1,2), (2,1), (2,2).
Neither order is derived from token identity. Evidence facts never change.

Per target/family: 6 mappings or semantic seeds × 2 × 2 = 24 calls.
Each four-cell table has n=6 per cell. Each opaque token maps to each underlying
action eight times per target (24 across three targets), and has two exposures
for each offered underlying action within each order cell. No unexposed token/
value/order cells for an offered action. Unoffered actions have no opportunities.

Exact execution schedule: j ascending; targets A, B, C; higher option position
1 then 2; relative evidence order same then reversed. For each matched triple,
family order is `list(itertools.permutations(("S","O1","O2")))`
indexed by `(j + target_index + 2*(option_position-1) + relative_index) % 6`.
Thus every family order occurs once within each target/order cell. No adaptive
schedule selection or extra seeds.

Match the three surfaces by j/target/option-position/relative-evidence-order:
72 triples, each with identical protected starting snapshot, decision number,
underlying options and evidence orders, seed, and sampler. Pair S–O1, S–O2,
O1–O2 only within these triples (24 pairs per target). Mapping/token assignment
is explicit. Seeds are not independently crossed with mapping: one seed per
mapping, shared across orders/families. Token-versus-seed effects remain a
limitation; repeated calls are not independent model subjects.

## Metrics and fixed support gates

All support labels require complete 216 real/valid calls, all 14 controls rejected
without execution/commit, 1,150 scripted setup transactions, and integrity PASS.
Invalid outputs remain in denominators, are rejected, and fail the global support
gate. Do not discard, replace, or relabel them. Rate denominators include every
registered call; unexposed strata have null rates, never imputed zero success.

Primary value following: higher authorized empirical mean among the two offered
actions. Show the four crossed cells first for every target/family, then n=24
marginals, canonical/surface selections, chosen values, and validity. Never pool
targets or opaque vocabularies before these results. Strong value following per
target/family is >=80% (>=20/24), descriptively. Stable across crossed positions
additionally requires >=5/6 higher choices in each of the four cells. VERIFIED
VALUE FOLLOWING REPLICATED across the two opaque families for a target requires
this latter rule in both; stability across all three representations additionally
requires S to satisfy it. Distinguish these scopes explicitly.

For matched surface comparisons, delta is higher-choice rate in the right family
minus left (S→O1, S→O2, O1→O2). A descriptive surface difference is supported iff
absolute delta >=0.20 and >=8 discordant pairs favor that direction (n=24 pairs),
plus global gates. Report both discordance directions, concordance, and changed
canonical choices. No p-values or significance claims. Eight discordances is an
absolute count, not a lower threshold scaled to sample size.

RETREAT lexical-interference replication for A or B requires **both O1 and O2**
to exceed S by >=20 percentage points and each to have >=8 discordances favoring
opaque, with global gates. Overall A/B replication requires both targets to meet
that rule separately. Otherwise NOT ESTABLISHED; do not substitute pooled A+B
results or a one-family success. Report C's surface comparisons separately.

Option effect: higher-selection rate when higher option is first minus when
second, marginal n=12 each. Also show the same contrast within each fixed higher
evidence position (n=6 cells). OPTION POSITION EFFECT SUPPORTED requires absolute
marginal difference >=0.20 and both stratified differences in the same direction
with magnitude >=0.20, plus gates. Report whether first or second is favored.
Evidence effect uses the analogous contrast, conditioning on higher option
position. These conservative descriptive flags do not identify internal causality.

Interaction: show p11,p12,p21,p22, then
I = (p11+p22) - (p12+p21); and agreement difference I/2.
Report all values irrespective of flags. Raw first-option and first-evidence choice
rates accompany higher-choice rates, preserving the distinction between position
following and value following.

For opaque tokens report selections / times offered, separately per family, by
target, token, verified value, underlying action, option position, evidence position,
and joint strata. Also show marginals. A descriptive token-asymmetry flag uses
max-minus-min token rate >=0.20 within a target/verified-value/underlying-action
stratum (8 exposures per token). Do not claim independence from seed or an
intrinsically preferred token. Joint strata have only two exposures per token.

## Target C competing order classifications

Apply independently to S, O1, O2; all use the global gates and n=6 per order cell.
Use all criteria and report any overlap; never pick a favored story afterwards.

* OPTION POSITION DOMINATES: first option selected >=5/6 in **each** order cell.
* EVIDENCE POSITION DOMINATES: first evidence entry selected >=5/6 in each cell.
* VERIFIED VALUE DOMINATES: higher value selected >=5/6 in each cell.
* CONJUNCTION EFFECT: the two aligned cells (1,1),(2,2) both select higher >=5/6
  and both opposed cells (1,2),(2,1) select higher <=1/6, or the reverse pattern;
  additionally absolute agreement difference >=0.50. State which alignment wins.
* UNRESOLVED: no listed criterion clears the gates. Record raw descriptive patterns
  even when no category is supported. A second-position tendency can appear in the
  signed position-effect metrics without being forced into a first-position category.

OPAQUE VOCABULARY DEPENDENCE OBSERVED for a target if the O1–O2 matched surface
difference clears the 20-point/8-discordance rule. Additionally for C, vocabulary
dependence is observed if O1/O2 each have a nonempty supported classification set
and those sets are disjoint. State the basis; otherwise vocabulary dependence is
NOT ESTABLISHED, not proof of equivalence. Report order-cell discrepancies even
when these conservative gates are not met. No post-hoc power expansion.

## Integrity, controls, stopping, and evidence

Zero protected false accepts, unauthorized Memory commits, stale accepts, duplicate
authorizations, malformed/out-of-pair commits, direct protected model mutation,
prediction rewrites, or bound violations. Existing observers and authorizers stay
unchanged; added checks observe projection/order/mapping integrity only on the test
side. Verify all displayed observations against the authorized setup events and
retain old Memory records unchanged. The model receives only authorized state and
verified rendered evidence, proposes one finite displayed label, mutates no
protected state directly, and authorizes nothing.

Bounded controls use Target C, j=0, higher option first, evidence reversed; rebuild
the fixture each time. For each family inject X9; the omitted third surface label;
the two displayed labels separated by one space; and first displayed label followed
by ` because it is better`. Additionally inject canonical RETREAT in O1 and O2.
This is 4 S + 5 O1 + 5 O2 = 14 controls, after real calls. Reject all before world
execution/Memory commit. Whitespace-only trimming is permitted, no output repair.
Measured setup: 1,080 transactions; control setup: 70; total 1,150. The ten
prospective preflight transactions are separate. No control is real model behavior.

Stop immediately on fixture, prompt/annex, hash/model/version mismatch, transport
error, or integrity violation. An invalid real output is recorded/rejected and the
next independent fixture proceeds, but global behavioral support fails. Never
retry, replace, increase sample count, tune prompts, or alter metrics after inference.

Keep raw per-call mappings, prompts, outputs, observations, predictions, executed
consequences, authorization, resulting Memory, setup rows, and model configuration
outside the public repository. Publish compact aggregate metrics, protocol and
hashes. Replay requires byte-identical call/step/setup/control/annex evidence and
JSON-equal summary/source hashes with zero new inference. Fresh stochastic
regeneration need not reproduce recorded outputs.

Fresh checks after real inference: this study's exact replay; semantic-prior v0
replay from its retained archive; adaptive v0, Memory v1, and original integration
replays; minimum-framework-repair-1; base-framework v0/v1/v2; new factorial tests.
Preserve expected historical negative controls. Verify all earlier files unchanged
apart from append-only repository navigation and refreshed public manifest.

Commit protocol first, then implementation tested with synthetic responses, then
real results/replay and the required 27-part report. No modification of main, tags,
or earlier results; no push. Stop after this experiment. No architecture expansion,
model promotion, nonstationarity, neutral-representation or causal-reasoning claim.
