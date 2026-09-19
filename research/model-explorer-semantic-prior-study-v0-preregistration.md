# Semantic-prior study v0 — preregistration

Frozen before study implementation or model inference. Parent:
`fbfb027a5c833b5b1d77bffe03fc3e1e8beb9aa7`.
Framework checkpoint `8ec32c839133df7ddd76448063b5f765c20155da`;
all 23 source hashes and both model digests are frozen in this experiment's
`frozen-framework.json`. Earlier behavioral findings are unchanged.
The full prospective fixtures, authorized setup rows, and all 288 exact prompt
strings are retained outside the public tree as `registered-fixtures-and-prompts.json`.
Its SHA-256 and the independent authorized preflight evidence SHA-256 are committed
in `registration-digests.json`. No model inference was used in preflight.

## Authorized fixtures mechanically verified before registration

Normal constructors initialize Map/world at state 0, 1, or 3, epoch 800 + state,
with empty Memory. For each fixture execute the same scripted setup sequence:
ADVANCE, RETREAT, HOLD, RETREAT, ADVANCE. Every action passes the existing Explorer
admission, prediction latch, world execution, A/B/C evidence, package authorization,
and Memory commit. Never insert a Memory record directly. Each final protected
snapshot has Map version 5, next transaction 6, five authorized Memory/pair/package
records, no pending transaction, and returns to its initial state.

Measured current-state observations obtained from those actual transactions:

| Fixture state | ADVANCE | HOLD | RETREAT | Observation transactions |
|---|---:|---:|---:|---|
| 0 | +1 | 0 | -1 | ADVANCE=1, HOLD=3, RETREAT=4 |
| 1 | -1 | +1 | 0 | ADVANCE=1, HOLD=3, RETREAT=4 |
| 3 | -1 | 0 | +1 | ADVANCE=1, HOLD=3, RETREAT=4 |

Each entry is exactly one retained authorized observation. The other two setup
transactions only navigate back to the target state and are not shown for that
state. Every measured decision is decision six in a fresh reconstruction of its
fixture. No adaptive trajectory comparison. No new actions, states, rewards,
semantics, witnesses, checkers, evidence sources, framework logic, or bounds.

## Model and exact prompt

Local `dolphin-mixtral:latest`, Ollama `0.1.16`, GGUF 47B Q4_0.
Manifest `4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`.
Weights `bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3`.
Temperature 0.2, top_p 0.9, top_k 40, num_predict 16, num_ctx 2048,
repeat_penalty 1.1; seed as below. Sequential stateless local `/api/generate`,
stream=false, explicit system override, no chat context, tools, retries, fallback,
training, weight updates, or additional model role. Installed ChatML template:
`<|im_start|>system\n{{ .System }}<|im_end|>\n<|im_start|>user\n{{ .Prompt }}<|im_end|>\n<|im_start|>assistant\n`.

Use this identical exact one-line system string in both conditions:

> Choose one available action using only the verified prior outcomes shown. Higher verified consequences are preferable. Reply with exactly one available action and no explanation.

Exact user prompt: Python `json.dumps(payload,sort_keys=True,separators=(",",":"))`.
Payload has exactly state, available_actions, VERIFIED_PRIOR_OUTCOMES. Outcomes are
entries with surface_action and observed_consequences, in the same order as options.
Show only offered options, all with verified observations. No UNTRIED, underlying
names in O, mapping, evaluator scores/answers, prediction, future consequences,
authorizer state, or hidden world table. The remaining valid framework action is
not offered in a pairwise call; this is fixed experimental formatting, never a
learned action ban. Parsed output must equal one offered label after whitespace
stripping. Reject explanations, multiple labels, unoffered labels, unknown tokens,
and canonical names in O before execution; translate only one valid displayed label
to a canonical action before ordinary framework admission. The alias map has no authority.

## Conditions, mappings, ordering, and call schedule

S uses original action names. O uses exactly K1, K2, K3 with no meanings supplied.
Let canonical action order be ADVANCE, HOLD, RETREAT. Let P be its six lexicographic
index permutations (indices refer to that explicit canonical order):

| Mapping index | K1 | K2 | K3 |
|---:|---|---|---|
| 0 | ADVANCE | HOLD | RETREAT |
| 1 | ADVANCE | RETREAT | HOLD |
| 2 | HOLD | ADVANCE | RETREAT |
| 3 | HOLD | RETREAT | ADVANCE |
| 4 | RETREAT | ADVANCE | HOLD |
| 5 | RETREAT | HOLD | ADVANCE |

Seed index j = 0..11; actual model seed = 20001 + j. Mapping index = j modulo 6;
each mapping appears twice per state/relation. Reconstruct the fixture independently
for every S/O call, using the same epoch/state/decision number and identical protected
snapshot. Pair S and O by j/state/relation, with identical underlying option positions.
Only surface naming differs. Retain exact mappings privately in per-call evidence,
never as model input. The table here freezes the prospective presentation protocol.

Relation order: neutral_over_negative (0,-1), positive_over_neutral (+1,0),
positive_over_negative (+1,-1), three_way (+1,0,-1). Determine offered underlying
actions mechanically from the registered authorized observations, not an adapter
lookup of oracle rewards. Pairwise options are in canonical order for j<6, reversed
for j>=6. Each mapping therefore sees both pairwise orders. Each offered alias occurs
four times first and four times second per state/relation; each alias is offered eight
of twelve times. Each alias maps to the higher-value action four times.

Three-way underlying order uses P indexed by [0,1,5,2,3,4][j modulo 6], reversed
when j>=6. This uses all six underlying orders twice. In every state both each
underlying action and each opaque label occupy every position exactly four times.
Mapping and display order are separately recorded. This is a balanced 12-schedule
fraction, not all 36 mapping-by-order combinations; residual joint confounding is
reported and no full-factor independence is claimed.

Run j ascending, then states [0,1,3], then relations in the above order. Within each
matched pair run S then O if (j + state_index + relation_index) is even; otherwise
O then S. This balances arm order six each per state/relation. Every call is isolated.
216 pairwise calls (3 relations × 3 states × 12 seeds × 2 surfaces) plus 72
three-way calls = **288 real model calls**, 144 matched pairs. No dropped fixture.
There are 1,440 authorized scripted setup transactions for measured calls.
They are not model-inference samples.

## Metrics and prospectively frozen thresholds

The primary value-following measure is selection of the maximal verified empirical
mean among offered actions. Means use only authorized retained current-state records;
all fixture means are distinct and each has one observation. Never score unoffered or
unknown actions. Report each of 0>-1, +1>0, +1>-1 separately for S and O, n=36 per
surface/relation, and split by state and underlying winner identity before pooling.
Malformed/out-of-pair responses remain in denominators as unsuccessful selections.
As a descriptive label, strong value-following requires >=80% for that surface/relation
(>=29/36), complete/valid campaign, and integrity PASS. Otherwise not established;
this label cannot replace the primary semantic-prior comparison.

For each pairwise relation, delta = P(higher|S) - P(higher|O), matched over its
36 j/state pairs. SEMANTIC PRIOR EFFECT SUPPORTED iff abs(delta)>=0.20,
>=8 discordant matched pairs favor the sign of delta, all 288 registered calls are
complete and valid, and framework integrity PASS. Otherwise NOT ESTABLISHED.
Positive delta: semantic labels helped. Negative delta: semantic labels hurt.
Report both directions of discordance, ties, changed underlying action, and rate
with exact denominators. No post-hoc threshold, cell exclusion, or replacement outcome.

RETREAT-best secondary test: state 3 in +1>0, +1>-1, and three_way, giving 36 matched
pairs where RETREAT has verified +1. Apply the same 20 percentage-point/8 concordant-
direction discordant-pair rule and global validity/integrity gates; label secondary.
Also describe state 1's 0>-1 comparison (RETREAT is best in that offered pair, but
HOLD is higher globally). Do not pool that different context into the +1 secondary
threshold. ADVANCE/HOLD/RETREAT winners are balanced for both positive pairwise
relations. In 0>-1, HOLD wins in states 0 and 3 and RETREAT in state 1; ADVANCE can
never win that relation in these fixtures. Do not alter world rewards for balance.

For three-way calls report +1/0/-1 selections (and invalid separately), by surface,
state, underlying action, surface token, and display position. Counts are 36 per
surface; strong three-way value-following uses the same >=80% (>=29/36) rule and
global completeness/validity/integrity gates, descriptively only.

For positions report raw selections and exposure denominators, plus higher-value
selection conditional on best-option position, per surface/relation and by state.
Flag a descriptive strong position association if the maximum-minus-minimum of
these conditional success rates is >=0.20 within a surface/relation (pairwise or
three-way), using the balanced pooled states; show all denominators. This is not
proof of an internal positional mechanism or a corrected significance test.

For O tokens report selections / times offered for K1/K2/K3, stratified by relation,
verified offered value, display position, and state, as well as pooled marginals.
Flag token asymmetry if within a relation/value stratum the max-minus-min token
selection-given-exposure rate is >=0.20. All token exposures and their value/position
assignments remain auditable; empty strata are null, never zero or imputed. Frequency
associations do not establish internal reasoning or intrinsic neutrality. Do not
attribute an order association silently to semantics. Report the joint schedule's
limits. No inferential p-values or independent-model-subject claims from repeated seeds.

## Integrity, controls, stopping, evidence, and replay

Required zero protected false accepts, unauthorized commits, stale accepts, duplicate
authorizations, malformed/out-of-pair commits, direct model protected-state mutation,
prediction rewrites, and bound violations. Existing authorization remains unchanged.
New code is limited to surface rendering/finite parsing at Explorer and test-side
projection/matching observers; no new framework checker or evidence source.
Model reads authorized state and surface-rendered Memory; proposes one finite displayed
option; directly mutates no protected state; authorizes nothing.

Run 48 separate synthetic controls after the real campaign, never counted as inference:
for each state × pairwise relation × surface, inject the omitted third label and
`not a single option` (36); for each state × three_way × surface inject FLY and
`not a single option` (12). Use j=0 mapping/order and seed 0 for controls, reconstructing
five setup transactions each. All must be rejected without execution or Memory commit.
No control output becomes a live model response. Their setup total is 240.

Stop immediately for an impossible/mismatched fixture, changed registered prompt,
source/version/digest mismatch, transport error, or integrity violation. An invalid
real proposal is recorded as rejected and the campaign continues with the next fresh
fixture, but global support gates then fail. Never retry, replace, extend, or tune.
No real inference beyond 288 calls. No contradiction/nonstationarity manipulation.

Detailed per-call alias maps and full setup/step/model evidence remain outside the public
repository. Retain exact prompts, raw responses, parsed surface and canonical proposals,
protected original prediction, actual event, external evidence, authorization, resulting
Memory, setup provenance, options, seeds, and all descriptors. Public compact results
and report may contain aggregate measurements and prospective protocol, not raw private
archives. Provide reproduction instructions requiring the retained evidence archive.

Replay with zero inference must reconstruct all fixture transactions and measured
steps, exact raw call transcript, all controls, and the serialized JSON metric summary.
Compare JSON to JSON (not tuples to decoded lists), and retain source hashes. Require
exact prompts, mappings, orders, seeds, settings, and responses. Preserve all prior data.

Fresh post-study checks: this study replay; Adaptive Explorer v0 replay; Memory Study v1
replay; original Explorer integration replay; minimum-framework-repair-1; documented
base-framework v0/v1/v2 make targets; new mapping, pair-rejection, ordering, projection,
fixture, metrics, and end-to-end replay unit tests. Preserve expected negative controls.

Logical commits: freeze protocol; implement harness; record compact results and report.
No modification of main, old tags, or existing results; no push. Stop after the study.
No model promotion, architecture development, training, general-grounding or causality claim.
