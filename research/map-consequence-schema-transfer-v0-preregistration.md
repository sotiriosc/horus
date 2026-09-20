# Map consequence-schema transfer v0 — prospective registration

Parent: `bf74d7eda79345efa7168ea1551de8b153b68791` on
`research/map-output-schema-isolation-v0`; preserve **C — NOT ESTABLISHED**.
Grounded root: `79921b1da735e1495dffb695c00d7e7a21a234a6`; claim firewall unchanged.

Exactly **16 real Map calls**, detached read-only probes. No Explorer, model
Recovery, production architecture change, tuning, extra worlds/arms or extension.
Test whether the one-field consequence response schema helps the two registered
moving-positive relations previously associated with ranking failures.

## Authentic histories and navigation

Each independent trial starts with empty Memory and epoch 1001 in its target
state. Use the unchanged external world and ordinary grounded execution:

| World | Initial/current state | Target setup (transaction 1) | Navigation (transaction 2) | Post-response scored target (transaction 3) |
|---|---:|---|---|---|
| WA / W0 | 0 | ADVANCE 0→1,+1 | RETREAT 1→0,0 | ADVANCE 0→1,+1 |
| WR / W3 | 3 | RETREAT 3→2,+1 | ADVANCE 2→3,+1 | RETREAT 3→2,+1 |

Both setup events publish via original receipt → Measure → authorization →
Memory. Navigation remains in protected Memory, but is excluded from the target
exact-pair projection. The target history contains exactly one authentic row,
epoch 1001, transaction 1, historical next_state 1 (WA) or 2 (WR), consequence +1.
Return to current state occurs only through the ordinary navigation execution;
no state reset, moving-law modification, handwritten history or depth change.

## Exact paired instructions and parsers

**J — JOINT**, exact established instruction:

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object with exactly two fields: next_state must be an integer in {0,1,2,3}, and consequence must be an integer in {-1,0,1}. Do not include any other fields or explanation.

**S — CONSEQUENCE-ONLY SCHEMA**, unchanged from output-schema isolation:

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object with exactly one field: consequence must be an integer in {-1,0,1}. Do not include any other fields or explanation.

The first and last sentences are byte-identical; only the response-format
sentence differs. Never ask to “predict the consequence” or add focus/hypothesis
wording. Import the previous diagnostic's exact instructions and parser dispatcher:
J uses the existing strict joint parser; S uses the same strict one-field parser.
Exact integer domains only; no bools, floats, prose, extra/duplicate keys,
extraction, coercion, retry or repair. S supplies no next_state.

## Counterbalanced schedule and matching

| Index | World | Block | Seed | Arm | Target alias |
|---:|---|---|---:|---|---|
| 0 | WA | O1 mapping 0 | 99301 | J | K1 |
| 1 | WA | O1 mapping 0 | 99301 | S | K1 |
| 2 | WR | O1 mapping 0 | 99301 | S | K3 |
| 3 | WR | O1 mapping 0 | 99301 | J | K3 |
| 4 | WA | O2 mapping 0 | 99301 | S | Q7 |
| 5 | WA | O2 mapping 0 | 99301 | J | Q7 |
| 6 | WR | O2 mapping 0 | 99301 | J | Z2 |
| 7 | WR | O2 mapping 0 | 99301 | S | Z2 |
| 8 | WR | O2 mapping 0 | 99302 | S | Z2 |
| 9 | WR | O2 mapping 0 | 99302 | J | Z2 |
| 10 | WA | O2 mapping 0 | 99302 | J | Q7 |
| 11 | WA | O2 mapping 0 | 99302 | S | Q7 |
| 12 | WR | O1 mapping 0 | 99302 | J | K3 |
| 13 | WR | O1 mapping 0 | 99302 | S | K3 |
| 14 | WA | O1 mapping 0 | 99302 | S | K1 |
| 15 | WA | O1 mapping 0 | 99302 | J | K1 |

Fresh paired seeds 99301/99302; only O1/O2 mapping 0. Eight J/S pairs. Each world
has two J-first and two S-first pairs. Within each pair require identical state,
target alias, authentic history, epoch/transaction, historical next_state and
consequence, depth/order, model, sampler, seed and envelope. Serialized task data
must be byte-identical. Normalize only the response-format sentence and require
complete request-byte equality. Verify exact instructions and identical first/
last sentences. Any extra mismatch stops before inference. Freeze all 16 request
hashes derived from genuine histories before inference.

Model: `dolphin-mixtral:latest`, Ollama 0.1.16, 47B Q4_0. Manifest
`4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`;
weights `bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3`.
Both arms: temperature 0.2, top_p 0.9, top_k 40, num_predict 32, num_ctx 2048,
repeat_penalty 1.1 and the registered seed. Stateless, unchanged template, no
constrained decoding. Verify installed model bytes before inference.

## Detached probes and new receipt scoring

Neither model output enters protected Prediction or obtains execution, receipt,
authorization, Memory publication, repair or Recovery capability. Durably record
response and parse before the scored event. Ordinary unchanged MapModel supplies
a prospectively fixed non-model control for the target: **WA (1,+1)** and
**WR (2,+1)**. Full control identity: epoch 1001, transaction 3, target pre-state
and target action. Controls are identical within every J/S pair and absent from
model input as predictions; authentic history shares the corresponding values.
No model adapter is installed.

The grounded execution method accepts no model output or output-condition
argument. After the non-model control latch, execute the target action and obtain
a new original receipt. Submit it through ordinary Measure/authorization/Memory.
Score the detached model against the new receipt, never the non-model control,
a declared law, or historical target label. Primary score is consequence. For J
report next_state and joint exactness separately; S has neither score. Framework
measurement_matches assesses the control and is recorded separately from model
accuracy. Native deterministic Recovery, if any, remains ordinary and is counted
separately from zero model Recovery calls.

Invalid responses remain invalid, with no substitution or retry. After durable
parse rejection, the independently registered target execution still uses the
non-model control; no model prediction score is assigned and final classification
is C. Continue only the remaining registered requests. Failed or ambiguous
transport stops without automatic reissue, even if 16 cannot complete.

## Pre-inference controls and replay

For all 16 registered contexts, acquire authentic target and navigation history,
then in throwaway canaries change only the hidden next target consequence to −1.
Hold historical receipts/Memory fixed and require exact model request bytes
unchanged. After synthetic probe and ordinary control latch, execute and require
new original receipt and Memory consequence −1, with the old target +1 observation
and navigation record unchanged. Zero inference for canaries.

Other zero-model checks verify navigation exclusion, both conditions' detachment
under finite/invalid outputs, strict parsers, rejection of changed task data or
first-sentence wording, all frozen decision boundaries, per-world requirements,
paired category classification, interrupted-journal handling and exact synthetic
replay. Label synthetic evidence; exclude it from real behavioral counts.

Fsync request intent → response → parse → control latch → execution intent →
original receipt → Measure/publication. One exclusive durable live reservation;
no automatic retry, repair or replacement. Replay all 16 retained responses with
network blocked, reconstruct authentic histories and scored events, and require
byte-identical deterministic data and snapshots.

## Primary pairs and frozen decision

Classify each of eight J→S consequence pairs: 0→+1, −1→+1, +1→+1, 0→0,
−1→−1, +1→wrong, other/invalid. Retain full finite outputs even when category
is other. Improvement: valid J-wrong→valid S +1; regression: valid J +1→valid
S-wrong. Report arm counts and paired improvements/regressions separately by
world, alias family and seed, with all eight individual pairs.

**A — CONSEQUENCE-ONLY SCHEMA TRANSFERS TO MOVING POSITIVE RELATIONS** iff all:
16/16 complete and valid; S +1 ≥7/8; J +1 ≤4/8; ≥3/8 improving pairs; zero
regressions; **each world S +1 ≥3/4**; authentic histories and post-response
receipts; matched requests; future-answer controls; integrity; exact replay.

**B — NO MOVING-POSITIVE TRANSFER OBSERVED** iff S +1 ≤2/8 with completed valid
set and all scientific integrity/matching/leak/replay requirements passing.

**C — NOT ESTABLISHED** for intermediate/mixed outcomes or missing requirements.
Consequence determines thresholds; J joint exactness must not substitute for it.
Do not tune thresholds based on observed outcomes.

If A, permitted: “Removing next_state from the required response schema improved
consequence forecasting across the registered moving-positive W0/W3 relations.”
Together with earlier diagnostics, this motivates a separate architectural study,
not a production split here. No internal mechanism or general Map correctness
claim. If B, no transfer was observed here; the previously observed rescue remains
bounded to its registered self-loop setting, not proof of impossibility elsewhere.
If C, retain mixed evidence without tuning or expansion.

The prior forensics' 23 residual ranking failures underpredicted the true-best
+1 action; this study tests only two finite target relations and does not rerun
or establish a full ranking, Explorer, long-horizon or production result.

Preserve all parent files and outcomes: grounded baseline A and firewall,
mechanical A, ranking forensics, positive-depth B, self-loop A, consequence-only
A, output-schema C, temporal Map/Explorer negatives, stale-Memory and authority
history. After exactly 16 calls, replay, report and STOP. No production split,
next_state-only model, prompt adoption, additional worlds/seeds/mappings/arms,
Explorer, push, main or tag change.
