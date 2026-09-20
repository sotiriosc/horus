# Map output-schema isolation v0 — prospective registration

Parent: `9646927d05943f687da778876c8bcb88cb8b1af9` on
`research/map-consequence-only-isolation-v0`; preserve **A — JOINT-OUTPUT COUPLING
EFFECT OBSERVED**. Grounded clean root:
`79921b1da735e1495dffb695c00d7e7a21a234a6`; existing claim firewall unchanged.

Exactly eight real-model calls. Test removing next_state from required output
while retaining the original outcome-prediction task wording. Both arms are
detached diagnostic probes. No Explorer, model Recovery, production architecture
implementation, tuning, extra aliases/seeds/arms or extension.

## Fixed authentic task and exact instructions

Every independent trial begins at state 1, epoch 1001 and empty Memory. Execute
one genuine HOLD 1→1,+1 through original receipt, Measure, authorization and
Memory publication. The exact-pair model-visible history has one observation,
epoch 1001, transaction 1, next_state 1 and consequence +1. No moving fixture,
synthetic history, navigation or depth change.

**J — ORIGINAL JOINT** uses the unchanged existing instruction and strict parser:

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object with exactly two fields: next_state must be an integer in {0,1,2,3}, and consequence must be an integer in {-1,0,1}. Do not include any other fields or explanation.

**S — SCHEMA-ONLY REMOVAL OF NEXT_STATE** uses exactly:

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object with exactly one field: consequence must be an integer in {-1,0,1}. Do not include any other fields or explanation.

The first and last sentences are byte-identical. Only the middle response-format
sentence differs. Never substitute “predict the consequence” or add hypothesis
wording. S directly reuses the prior diagnostic's strict one-field parser,
requiring only `consequence`, an exact integer −1,0,+1. No bool, float, coercion,
extraction, duplicate/extra key, prose, retry or repair. The parser grants no
authority; S never manufactures a protected next_state.

## Frozen schedule and matching

| Index | Block | Seed | Arm | HOLD alias |
|---:|---|---:|---|---|
| 0 | O1 mapping 0 | 99201 | J | K2 |
| 1 | O1 mapping 0 | 99201 | S | K2 |
| 2 | O2 mapping 0 | 99201 | S | M4 |
| 3 | O2 mapping 0 | 99201 | J | M4 |
| 4 | O2 mapping 0 | 99202 | J | M4 |
| 5 | O2 mapping 0 | 99202 | S | M4 |
| 6 | O1 mapping 0 | 99202 | S | K2 |
| 7 | O1 mapping 0 | 99202 | J | K2 |

Seeds 99201/99202 are fresh relative to inherited schedules. Within each pair,
require identical state, target alias, authentic history, depth, epoch,
transaction identity, historical next_state/consequence, row order, model,
sampler, seed and envelope. Require exact instructions, byte-identical first
and last sentences and byte-identical serialized task data. Normalizing only
the response-format difference must make complete transport request bytes equal.
Freeze all eight authentic-history request hashes before inference; stop before
inference on any extra visible mismatch.

Model: `dolphin-mixtral:latest`, Ollama 0.1.16, 47B Q4_0. Manifest
`4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`;
weights `bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3`.
Both arms: temperature 0.2, top_p 0.9, top_k 40, num_predict 32, num_ctx 2048,
repeat_penalty 1.1 and the registered paired seed. Stateless requests, unchanged
template, no constrained decoding. Verify model bytes before inference.

## Detached probes and post-response scoring

Durably record response and parse before the new scored event. Neither J nor S
enters protected framework Prediction, executes, authorizes, publishes, repairs
or writes Memory. The unchanged ordinary `MapModel` drives registered HOLD using
the prospectively fixed non-model control **(next_state=1, consequence=+1)** in
both arms, with epoch 1001, transaction 2, pre-state 1, action HOLD. Assert that
control in each trial. No model adapter is installed. The control is absent
from model input as a prediction; authentic history shares those finite values.

The ordinary execution method accepts no probe output or condition argument.
After control latch, execute real simulated HOLD through the grounded boundary,
obtain its new original receipt and submit through Measure/authorization/Memory.
Score the probe against that receipt only, never the control or declared law.
Report J next_state, consequence and joint exactness; S consequence only, with
next_state/exactness not applicable. Framework measurement_matches assesses the
non-model control and stays separate from probe correctness.

Invalid parsed responses remain invalid with no substitute or retry. The
independently registered non-model HOLD still executes after durable rejection;
the invalid probe gets no prediction score and forces final C. Continue only the
remaining registered calls. Failed or ambiguous transport stops without automatic
reissue, even if eight cannot complete.

## Pre-inference controls and replay

Eight throwaway canaries acquire authentic +1 history, then mutate only hidden
future HOLD consequence to −1. Require exact J/S request bytes unchanged. After
synthetic probe and ordinary control latch, verify new original receipt and
Memory consequence −1, with old +1 history unchanged. Zero inference.

Zero-model software controls also vary finite/invalid J/S outputs, including
wrong J next_state, while requiring identical grounded control, execution,
authorization and Memory; exercise parsers, extra task-field and changed-first-
sentence rejection, decision boundaries, interrupted-journal detection, and exact
synthetic replay. Synthetic evidence is labeled and excluded from behavioral
counts; these checks do not authorize extra real-model arms.

Fsync record request intent, response, parse, control latch, execution intent,
original receipt and Measure/publication in order. One exclusive durable live
reservation; no retry or replacement. Replay all eight retained responses with
network blocked, reconstruct authentic histories and new post-response receipts,
and require byte-identical deterministic records and snapshots.

## Frozen decision

For each of four J/S pairs report consequence J→S: 0→+1, 0→0, +1→+1, +1→0,
or other/invalid. Improvement means valid J-wrong→valid S +1; regression means
valid J +1→valid S-wrong. Consequence alone drives thresholds; J next_state and
joint exactness remain descriptive.

**A — OUTPUT-SCHEMA COUPLING EFFECT OBSERVED** iff 8/8 complete and valid,
J +1 ≤1/4, S +1 ≥3/4, ≥2/4 improving pairs, zero regressions, matched task data,
byte-identical first instruction sentence, authentic histories, authentic
post-response score receipts, leak controls, integrity and exact replay pass.

**B — REMOVING NEXT_STATE FIELD ALONE DOES NOT RESCUE** iff S +1 ≤1/4 with a
completed valid set and matching/integrity/replay passing. Authentic histories,
post-response receipts, detachment and leak controls are prerequisites for a
valid experiment in either interpretation.

**C — NOT ESTABLISHED** for intermediate/mixed outcomes or missing requirements.
If both arms become strong, report that the joint-arm error did not reproduce.
No added statistical threshold or internal-mechanism decision rule.

If A, the permitted narrow statement is: “Removing next_state from the required
response schema, while retaining the original outcome-prediction wording,
changed consequence forecasts in the registered positive self-loop case.” This
supports a contribution from the required joint output representation in this
contrast; it does not identify an internal mechanism. If B, the prior rescue
likely depended on more than removing next_state; target wording remains a
candidate explanation, without inferring internal cause.

W0 ADVANCE and W3 RETREAT moving +1 failures remain unexplained even if A. This
addresses only the registered W1/self-loop case. No production split or new
production Map prompt adoption.

Preserve all parent tracked files, grounded baseline A and claim firewall,
mechanical A, ranking forensics, positive-depth B, self-loop coupling A,
consequence-only isolation A, temporal Map/Explorer negatives, stale-Memory and
authority history. No historical result is rewritten or upgraded by this
probe diagnostic. After exactly eight calls, replay, report and STOP. No
architecture change, expansion, extra seeds/mappings/calls, push, main or tag change.
