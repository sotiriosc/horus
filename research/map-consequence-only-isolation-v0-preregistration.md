# Map consequence-only isolation v0 — prospective registration

Parent: `543b4c550bdff461c88dbc77ac976df15483a8a6` on
`research/map-self-loop-consequence-coupling-v0`; preserve its **A — SELF-LOOP /
CONSEQUENCE COUPLING EFFECT OBSERVED**. Grounded clean root:
`79921b1da735e1495dffb695c00d7e7a21a234a6`; existing claim firewall unchanged.

Exactly eight real-model calls. This is a prompt/output-decomposition diagnostic.
Both arms are detached read-only probes. No Explorer, model Recovery, production
architecture implementation, tuning, extra aliases/seeds/arms or extension.

## Authentic fixed task

Every independent trial begins at state 1, epoch 1001 and empty Memory. Acquire
one genuine HOLD 1→1,+1 through ordinary execution, original receipt, Measure,
authorization and Memory publication. The state-1/HOLD model projection contains
exactly that observation, epoch 1001, transaction 1, next_state 1, consequence +1.
No moving fixture, handwritten history, reset navigation or history-depth change.

Only the system instruction and its required output schema differ between arms.
J uses the exact existing Map instruction and parser unchanged:

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object with exactly two fields: next_state must be an integer in {0,1,2,3}, and consequence must be an integer in {-1,0,1}. Do not include any other fields or explanation.

C uses exactly:

> Predict the next externally realized consequence for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object with exactly one field: consequence must be an integer in {-1,0,1}. Do not include any other fields or explanation.

The literal words `field`/`fields` required in those supplied instructions are
retained; no extra hypothesis wording is introduced. C's diagnostic parser
accepts exactly one JSON object with only `consequence`, an exact integer in
{-1,0,1}. It rejects duplicate keys, bools, floats, strings, nonfinite values,
extra keys, prose, code fences and concatenated objects. No extraction, coercion,
retry or repair. C never supplies a protected next_state.

## Frozen schedule and matching

| Index | Block | Seed | Arm | HOLD alias |
|---:|---|---:|---|---|
| 0 | O1 mapping 0 | 99101 | J | K2 |
| 1 | O1 mapping 0 | 99101 | C | K2 |
| 2 | O2 mapping 0 | 99101 | C | M4 |
| 3 | O2 mapping 0 | 99101 | J | M4 |
| 4 | O2 mapping 0 | 99102 | J | M4 |
| 5 | O2 mapping 0 | 99102 | C | M4 |
| 6 | O1 mapping 0 | 99102 | C | K2 |
| 7 | O1 mapping 0 | 99102 | J | K2 |

Within each pair, require byte-identical serialized task data and identical
model, sampler, seed and envelope fields except `system`. Normalizing only that
instruction must make full transport request bytes equal. Require authentic
history identity, row order, surface action, next_state and consequence equal.
Freeze all eight request hashes before inference. Any additional mismatch stops
before inference. Seeds 99101 and 99102 are absent from inherited schedules.

Model: `dolphin-mixtral:latest`, Ollama 0.1.16, 47B Q4_0. Manifest
`4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`;
weights `bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3`.
Both arms: temperature 0.2, top_p 0.9, top_k 40, **num_predict 32**, num_ctx 2048,
repeat_penalty 1.1, registered paired seed. Stateless requests, unchanged model
template, no constrained decoding. Verify installed model bytes before inference.

## Detached probe and independent execution target

Durably record response and parse before the scored event. Neither J nor C
enters the framework as a proposal or authorizes, publishes or repairs anything.
Keep raw/parsed outputs in diagnostic records only. Use ordinary `MapModel`,
unchanged, to drive the next registered HOLD with its prospectively fixed
non-model control prediction **(next_state=1, consequence=+1)**. Assert that
prediction in every trial. Its full epoch/transaction identity is (1001,2),
pre_state 1 and action HOLD in both arms. No model adapter is installed.

The control is absent from model input as a control prediction; task history
necessarily contains the same outcome values. The execution method accepts no
probe output or condition argument. After its ordinary control latch, execute
HOLD, obtain the new original receipt and submit it through unchanged
Measure/authorization/Memory machinery. Score the detached probe only against
that receipt's consequence, never against the control or declared-law table.
For J, report next_state and joint exactness separately. For C these are not
applicable, never inferred. Framework measurement_matches evaluates the non-model
control, so it is recorded separately from diagnostic probe correctness.

A syntactically invalid response remains invalid, with no substitute or retry.
After durable parse rejection, the independently registered HOLD still executes
through the same non-model path; the invalid probe gets no prediction score and
forces final C. Continue only the remaining registered calls. Failed or ambiguous
transport stops with no automatic reissue, even if eight calls cannot finish.

## Pre-inference controls and replay

After acquiring authentic +1 history, throwaway canaries for all eight registered
contexts change only hidden future HOLD consequence to −1. Require exact J and C
request bytes unchanged, then execute after synthetic probes and verify new
original receipt and Memory consequence −1, with old +1 history unchanged.
These use zero model calls.

Additional software checks vary finite/invalid J/C probe outputs while holding
the world, request history and non-model control fixed; require identical grounded
execution, authorization and Memory. Exercise strict parsers, request mismatch
rejection, frozen decision boundaries, interrupted-journal detection and exact
synthetic replay. Clearly label synthetic evidence and exclude it from behavioral
counts. No expanded real-model campaign is authorized by these checks.

Use fsync write-ahead request intent, response, parse, control latch, execution
intent, original receipt and Measure/publication records. One exclusive durable
live reservation; no automatic retry or replacement. Replay all eight recorded
responses with network blocked, reconstruct genuine histories and post-response
receipts, and require byte-identical deterministic data and snapshots.

## Frozen decision

For each of four J/C pairs report J→C consequence transition: 0→+1, 0→0, +1→+1,
+1→0 or other/invalid. Improvement means valid J-wrong→valid C +1; regression
means valid J +1→valid C-wrong. Consequence drives classification, not joint
next_state/consequence correctness.

**A — JOINT-OUTPUT COUPLING EFFECT OBSERVED** iff all eight calls complete and
are valid, J predicts +1 ≤1/4, C predicts +1 ≥3/4, at least 2/4 pairs improve,
zero regress, all histories authentic, all scored receipts authentic and
post-response, matched requests, leak controls, integrity and exact replay pass.

**B — CONSEQUENCE-ONLY DOES NOT RESCUE SELF-LOOP FORECAST** iff C predicts +1
≤1/4 with a completed valid set and integrity/replay passing. Authentic histories,
post-response receipts, matching, detachment and leak controls are prerequisites
to a valid experiment in either interpretation.

**C — NOT ESTABLISHED** for intermediate/mixed outcomes or missing requirements.
If both arms are strong, explicitly report that the joint-arm error did not
reproduce in this sample. No new threshold, significance or mechanism rule.

If A, the permitted narrow statement is: “Removing the requirement to jointly
predict next_state changed consequence forecasts for the registered positive
self-loop case.” No internal mechanism claim. If B, the error persists without
next_state as required output, arguing against joint-output generation as the
primary explanation for this registered effect; retain the small-sample limit.
The instruction's target wording also changes exactly as supplied, so an observed
contrast cannot isolate hidden computation from instruction/schema effects.

W0 ADVANCE and W3 RETREAT are moving +1 relations that also produced errors.
Preserve that fact: even A addresses only the registered self-loop/W1 failure
mode. This diagnostic is not a production split or adoption of a new Map prompt.

Preserve all parent tracked files, grounded baseline A, mechanical A, ranking
forensics, positive-depth B, self-loop A, temporal Map/Explorer negatives,
stale-Memory results and authority history. No historical result is rewritten
or upgraded by these detached probes. After exactly eight real calls, replay,
report and STOP. No expansion, architecture change, push, main or tag change.
