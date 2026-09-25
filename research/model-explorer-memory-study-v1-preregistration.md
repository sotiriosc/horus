# Model Explorer Memory study v1 — frozen preregistration

Parent: `1ca714f0dd91dd134525fdd30d1bf0f336266346`.
The previous integrity PASS and usefulness NOT ESTABLISHED remain unchanged.
Framework: `8ec32c839133df7ddd76448063b5f765c20155da`; the 23 source hashes in
`experiments/model_explorer_memory_study_v1/frozen-framework.json` were verified.
No old runtime, harness, result, main, or tag will be rewritten. No push.

## Freeze and exact inputs

This document and `experiments/model_explorer_memory_study_v1/fixtures-and-prompts.json`
are committed before model calls. The JSON contains the actual authorized setup
events, relevant raw Memory, and **all eight exact system/user prompt pairs**
(two studies × two representations × two history arms). Every inference request
must reproduce one of these prompt strings exactly; only its seed changes.
Fixtures were mechanically exercised through the unchanged framework before
registration. No fabricated Memory record is permitted.

## Model and settings

Local `dolphin-mixtral:latest`, GGUF 47B Q4_0, Ollama 0.1.16.
Manifest digest:
`4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`.
Weights digest:
`bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3`.
Keep the existing ChatML template and default CPU/GPU placement. Override only
the system prompt as specified below. All calls are sequential, no tools/chat
history, `/api/generate`, stream=false. Fixed temperature=0.2, top_p=0.9,
top_k=40, repeat_penalty=1.1, num_ctx=2048, num_predict=16. Record per-call seed,
actual response metadata, raw output, and any infrastructure error. No output
repair, fallback, model/config switching, or inference retry to obtain success.

Exact system prompt (one line):

> Choose an action using verified prior outcomes. Higher observed consequences are preferable. UNTRIED means no verified observation; it does not mean consequence 0. Reply with exactly one allowed action and no explanation.

User input is compact sorted-key JSON. Common fields are state, Map version,
epoch, transaction ID, and allowed actions in ADVANCE/HOLD/RETREAT order.
Only `memory` differs within a matched pair. RAW: `memory.records` contains
the relevant audited records and `memory.UNTRIED` lists actions with no shown
record. SEMANTIC: `memory.VERIFIED_PRIOR_OUTCOMES` groups observed consequences
by action in allowed-action order; `memory.UNTRIED` is the same complement.
No averaging, imputation, evaluator choice label, oracle information, or future
consequence enters the prompt. Empty history shows all actions as UNTRIED.
No-history means "no evidence supplied in this view," not erasure of internal
authorized Memory. UNTRIED is relative to this displayed audited projection.

## Fixtures, verified before registration

Both fixtures start at true/incumbent state 0 and use the **original
deterministic Explorer** plus normal A/B/C admission for setup.

* A: five ADVANCE transactions, epoch 501. Decision state 1, Map version 5,
  transaction 6. Relevant authorized Memory: ADVANCE=-1. HOLD and RETREAT UNTRIED.
* B: five ADVANCE transactions followed by one HOLD, epoch 502. Decision state 1,
  Map version 6, transaction 7. Relevant authorized Memory: ADVANCE=-1, HOLD=+1.
  RETREAT UNTRIED. The positive HOLD record is an actual authorized sixth outcome.

Each arm reconstructs the same fixture and compares its entire protected state
against the matched arm. Versions and identities are identical within a study;
the one extra positive-observation transaction explains the between-study
version/transaction difference. All raw setup records are retained externally.

## Fixed sample sizes and ordering

First measure proposal prior/bias with **eight no-history calls per study/form**,
seeds 9001..9008: 32 calls, completed before any history treatment call. No
threshold, prompt, fixture, or sample-size adaptation follows this measurement.

Then run **24 matched pairs per study per representation**, seeds 1001..1024:
96 matched pairs / 192 calls, plus the initial 32 = **224 real calls total**.
The same seed is used in both arms and all study/form cells. Cell order is
A/raw, A/semantic, B/raw, B/semantic, reversed on every odd zero-based seed index.
During paired trials, history comes first when `(seed_index + fixed_cell_index)`
is even, otherwise no-history first. Each cell therefore has 12 of each arm order.
Bias calls use the same alternating cell order and their own eight fixed seeds.
Each call starts from a fresh identical authorized fixture, never a previous
model-controlled trajectory. No optional exploration condition is run.

## Primary metrics and fixed descriptive thresholds

Compute each study/form cell separately; never pool the 24 seeds into apparent
independent subjects or tune thresholds after outcomes. Empirical rates use all
24 calls per arm and show malformed outputs separately. A support verdict also
requires all 48 responses in that cell to parse as allowed actions and all
integrity/input-matching checks to pass; rejection alone cannot count as learning.

**A — negative avoidance:**
`delta_A = P(ADVANCE | no history) - P(ADVANCE | negative history)`.
Support requires delta_A >= 0.25 (at least six net fewer ADVANCE selections out
of 24). No specific alternative is required. Report both distributions, matched
beneficial/harmful/tied discordances, and any-action-change count. UNTRIED is
never scored as an observed zero consequence.

**B — positive preference:**
The highest verified action is mechanically derived from the authorized
fixture, not supplied as an answer cue. `delta_B = P(best verified action |
history) - P(best verified action | no history)`.
Support requires P(best | history) >= 0.75 (18/24) AND delta_B >= 0.25 (six net
additional selections). High HOLD frequency without matched improvement is
proposal bias/ceiling, not evidence for Memory use.

B secondary score: mean verified consequence among choices whose actions have
an observed record in the common fixture. Report coverage and counts of
UNTRIED/malformed choices explicitly; do not impute a score to either. Apply
the same fixture for scoring both arms without exposing it to the no-history arm.

**Representation comparison:** report semantic-minus-raw differences in each
study's primary delta, with matched seeds. "Representation matters" is supported
descriptively only if the absolute delta difference is >= 0.25 and the better
representation meets that study's own support threshold. Report either direction.
Bias distributions P(ADVANCE), P(HOLD), P(RETREAT) are shown separately by
fixture/form for the first eight calls and for the 24 paired no-history controls.
No p-value or significance/independent-subject inference is preregistered.
Floor/ceiling limitations, stochasticity, small finite settings and order
dependence must be explicit. A/B support labels are scoped by representation;
absence of support is NOT ESTABLISHED, not a framework failure.

## Mechanical Memory-to-prompt and integrity checks

Reuse the previous integration harness's world, evidence delivery and every
existing integrity observer. Extend only the experiment-side presentation and
measurement adapter. The model remains a finite action proposer and authorizes
nothing. Strict parser/action admission remains unchanged.

For every input retain all relevant audited raw records even when withheld;
verify they match the retained authorized Memory projection. Independently
reconstruct each displayed raw/semantic form and UNTRIED complement, compare
the full exact prompt with the registered template, and check paired protected
state and all nonhistory input fields for equality. Verify corrected records,
not corrupted inputs, reach presentation. These are test-side observations,
not new framework authority or grounding layers.

Integrity PASS requires zero protected false accepts, unauthorized Memory
commits, stale accepts, duplicate authorizations, malformed-output commits,
direct model protected-state mutations, prediction/provenance errors or bound
violations. Unexpected inference/harness errors are incomplete evidence and
must not be silently excluded. No extra seeds replace failures.

Record seed, study/form/arm/order, raw authorized Memory, exact displayed form,
prompt/system/options, raw response, parsed action, original prediction,
authorization, realized consequence, and post-commit identities. Retain exact
transcript replay with no new inference. Separately rerun the repaired
177-scenario/109-check campaign, prior model-integration transcript replay,
v0/v1/v2 regressions, and new presentation/parser tests. Recheck frozen hashes.

Stop after the report. No model integration into another role, no runtime
repair/redesign, no hardware work. Preserve the previous negative model-use
result. This study concerns prompt-conditioned proposal behavior, not weight
learning or general intelligence.
