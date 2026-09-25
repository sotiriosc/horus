# Map consequence-schema transfer v0 — results

**C — NOT ESTABLISHED.** Exactly 16 real Map calls completed and **16/16**
were valid. Consequence accuracy was **J 7/8** and **S 8/8**, with **1/8
improving pairs** and **0/8 regressions**. Authentic histories and navigation,
new original post-response receipts, matching, leak controls, detachment,
integrity and exact replay passed.

A is not established because J predicted +1 in 7/8 calls, exceeding its frozen
maximum of 4/8, and only 1/8 pairs improved, below the required 3/8. B is not
established because S predicted +1 in 8/8, above B's maximum of 2/8.

Both arms were already correct on consequence in almost every trial. The prior
moving-positive underprediction did not reproduce strongly under this registered
one-row-history, alias and seed schedule. There was only one J error for S to
rescue. This is not evidence of the preregistered transfer effect and is not the
registered B outcome. No internal mechanism is inferred.

## Registration and evidence

The [preregistration](map-consequence-schema-transfer-v0-preregistration.md),
exact imported instructions and parsers, diagnostic code, balanced schedule and
16 authentic-request hashes were committed before inference as
`0a5c5adb50fad1bda88c528dfbe98cd399f25c20`. Parent:
`bf74d7eda79345efa7168ea1551de8b153b68791`.

[Compact results](../experiments/map_consequence_schema_transfer_v0/results.json)
retain all raw and parsed responses, scores, eight paired comparisons, subgroup
breakdowns, authentic target histories, setup and navigation receipts, scored
original receipts, actual executions, non-model controls, Measure,
authorizations, Memory publications and source-record hashes.
[Verification](../experiments/map_consequence_schema_transfer_v0/verification.json)
records model hashes, controls, replay hashes and historical preservation.
[Reproduction instructions](../experiments/map_consequence_schema_transfer_v0/README.md)
require the retained private raw archive; compact public evidence is not the
complete replay archive.

## All 16 observations

WA used current state 0 and ADVANCE with authentic target outcome (1,+1). WR
used current state 3 and RETREAT with authentic target outcome (2,+1). Every
new scored receipt matched its world's target outcome. JSON is displayed
compactly below; `results.json` retains exact raw strings, including whitespace.

| Call | World | Block | Seed | Arm | Parsed response | Consequence correct | next_state correct | Joint exact |
|---:|---|---|---:|---|---|---|---|---|
| 1 | WA | O1 | 99301 | J | `{"next_state":1,"consequence":1}` | yes | yes | yes |
| 2 | WA | O1 | 99301 | S | `{"consequence":1}` | yes | n/a | n/a |
| 3 | WR | O1 | 99301 | S | `{"consequence":1}` | yes | n/a | n/a |
| 4 | WR | O1 | 99301 | J | `{"next_state":2,"consequence":1}` | yes | yes | yes |
| 5 | WA | O2 | 99301 | S | `{"consequence":1}` | yes | n/a | n/a |
| 6 | WA | O2 | 99301 | J | `{"next_state":1,"consequence":1}` | yes | yes | yes |
| 7 | WR | O2 | 99301 | J | `{"next_state":2,"consequence":1}` | yes | yes | yes |
| 8 | WR | O2 | 99301 | S | `{"consequence":1}` | yes | n/a | n/a |
| 9 | WR | O2 | 99302 | S | `{"consequence":1}` | yes | n/a | n/a |
| 10 | WR | O2 | 99302 | J | `{"next_state":2,"consequence":1}` | yes | yes | yes |
| 11 | WA | O2 | 99302 | J | `{"next_state":1,"consequence":1}` | yes | yes | yes |
| 12 | WA | O2 | 99302 | S | `{"consequence":1}` | yes | n/a | n/a |
| 13 | WR | O1 | 99302 | J | `{"next_state":2,"consequence":1}` | yes | yes | yes |
| 14 | WR | O1 | 99302 | S | `{"consequence":1}` | yes | n/a | n/a |
| 15 | WA | O1 | 99302 | S | `{"consequence":1}` | yes | n/a | n/a |
| 16 | WA | O1 | 99302 | J | `{"next_state":1,"consequence":0}` | no | yes | no |

J next_state accuracy was **8/8** and J joint exactness **7/8**, reported
separately from consequence accuracy. S has no next_state or joint exactness
score; neither was inferred or manufactured.

## Eight pairs and breakdowns

| World | Block | Seed | J consequence | S consequence | Category | Improvement | Regression |
|---|---|---:|---:|---:|---|---|---|
| WA | O1 | 99301 | +1 | +1 | +1→+1 | no | no |
| WA | O1 | 99302 | 0 | +1 | 0→+1 | yes | no |
| WA | O2 | 99301 | +1 | +1 | +1→+1 | no | no |
| WA | O2 | 99302 | +1 | +1 | +1→+1 | no | no |
| WR | O1 | 99301 | +1 | +1 | +1→+1 | no | no |
| WR | O1 | 99302 | +1 | +1 | +1→+1 | no | no |
| WR | O2 | 99301 | +1 | +1 | +1→+1 | no | no |
| WR | O2 | 99302 | +1 | +1 | +1→+1 | no | no |

Registered category counts: 0→+1: **1**; −1→+1: **0**; +1→+1: **7**;
0→0: **0**; −1→−1: **0**; +1→wrong: **0**; other/invalid: **0**.

| Group | J +1 | S +1 | J next_state | J exact | Improvements | Regressions |
|---|---:|---:|---:|---:|---:|---:|
| WA | 3/4 | 4/4 | 4/4 | 3/4 | 1 | 0 |
| WR | 4/4 | 4/4 | 4/4 | 4/4 | 0 | 0 |
| O1 | 3/4 | 4/4 | 4/4 | 3/4 | 1 | 0 |
| O2 | 4/4 | 4/4 | 4/4 | 4/4 | 0 | 0 |
| seed 99301 | 4/4 | 4/4 | 4/4 | 4/4 | 0 | 0 |
| seed 99302 | 3/4 | 4/4 | 4/4 | 3/4 | 1 | 0 |

Both worlds passed the descriptive S +1 ≥3/4 gate. These subgroup results do
not replace the frozen overall thresholds.

## Authentic navigation, matching and authority separation

Each trial began independently at epoch 1001 with empty Memory. WA acquired
ADVANCE 0→1,+1 and navigated RETREAT 1→0,0. WR acquired RETREAT 3→2,+1 and
navigated ADVANCE 2→3,+1. Every target and navigation event published through
ordinary original receipt, Measure, authorization and Memory machinery. No
world law changed and no state reset followed history acquisition.

Both setup observations remained in Memory. The target projection contained
only transaction 1, the authentic target observation; navigation transaction 2
was excluded in all 16 contexts. The row, chronology, next_state, consequence
and identity were authenticated rather than written or synthesized.

All eight J/S pairs passed exact request matching before inference and on the
retained real requests. Task data were byte-identical. The first instruction
sentence retained “Predict the next externally realized outcome” verbatim; the
last sentence also matched. Only the response-format sentence differed.
Normalizing it made the complete transport request bytes equal. State, alias,
history and identity, depth and order, model, sampler, seed and envelope
matched. Both arms retained num_predict=32 and the prior exact parsers.

Both outputs remained detached from protected Prediction and from execution,
receipt, authorization, repair, Recovery and Memory-publication capabilities.
After durable response and parse, unchanged ordinary MapModel used non-model
control WA (1,+1) or WR (2,+1), epoch 1001, transaction 3, with the target
pre-state and action. The control matched within each pair and was absent from
model input as a prediction. No model adapter was installed.

Only after the control latch did the new target action execute. Probe scores
used its new original receipt, never the control or a declared law. All 16
scored events invoked Measure once and obtained committed, continued
`AUTHORIZED` Memory publication. Framework measurement_matches was true in
16/16 because it evaluated the non-model control; it was not used as model
credit.

There were 32 setup executions—16 target and 16 navigation—and 16 scored
executions: **48 unique original live receipts and 48 Memory publications**.
Historical target and navigation records remained unchanged. Native state
Recovery authorizations were zero in setup and scoring. Explorer and model
Recovery calls were zero.

## Controls and replay

All 16 pre-inference canaries preserved authentic visible history and changed
only the hidden next target consequence from +1 to −1. Exact requests remained
unchanged. New original score receipts and Memory carried −1, while the old +1
target and navigation records remained intact. These used zero inference.

Sixteen detachment variants across both worlds covered finite and invalid J/S
outputs and wrong J next_state; grounded controls, executions, authorizations
and Memory matched within each world. Executed controls also covered eleven
strict J-parser rejections, twenty reused S-parser rejections, three valid S
integers, changed task-field and first-sentence rejection, fourteen decision
cases, seven paired categories, the per-world gate and two durability cases.
Sixteen synthetic responses reproduced under exact synthetic replay. These are
software controls, not extra model worlds, arms or behavioral observations.

The real 144-record journal passed its hash chain and ordering checks: intent →
response → parse → non-model control latch → execution intent → original receipt
→ Measure/publication. Original object identity and full binding were checked
during live execution and replay. Serialized equality alone is not treated as
proof of live object identity.

Exactly 16 server generation requests matched 16 recorded responses. There was
no retry, repair, replacement or extra call, and the owned server stopped.
Network-blocked replay made **zero model calls** and reproduced seven data files,
16 snapshots and the empty writer-lock file—**24 files**—byte for byte. Raw
live/replay metrics retain provisional C / `AWAITING_EXACT_REPLAY`; final C was
recomputed separately after replay passed.

Execution accounting: 32 registration setup + 192 preflight/control + 48 live
+ 48 replay = **320 simulated world executions**. Only the 16 live calls are
real-model behavioral evidence. Model blobs were verified before inference. A
syntax error prevented the initial registration import; it was corrected before
registration, inference or world execution and did not alter a frozen rule.

## Frozen decision, limits and preservation

A required 16/16 valid, S +1 ≥7/8, J +1 ≤4/8, at least three improvements,
zero regressions, each world S +1 ≥3/4, and all scientific-integrity gates.
Observed: 16/16 valid; S 8/8; J 7/8; one improvement; zero regressions; WA S 4/4;
WR S 4/4. B required S +1 ≤2/8. Classification and breakdowns were independently
recomputed from retained consequence values. Joint exactness did not replace
consequence scoring, and no threshold was tuned.

This is a small diagnostic of two target relations, two opaque alias blocks and
two paired seeds using one-row authentic target histories. It does not rerun the
23 historical ranking failures, evaluate Explorer or ranking end to end,
identify an internal mechanism, or establish general Map correctness. Authentic
events here are executions of the external software simulator, not physical
hardware. Earlier failures are not retroactively rewritten.

All **742 parent tracked files**, including executable modes, remain unchanged:
grounded baseline A and claim firewall, mechanical A, ranking forensics,
positive-depth B, self-loop A, consequence-only A, output-schema **C — NOT
ESTABLISHED**, temporal Map and Explorer negatives, stale-Memory results and
authority history.

The 16-call campaign is complete and stopped. No production split,
next_state-only model, prompt adoption, architecture change, tuning, extra
worlds, seeds, mappings, arms or calls. No push, main-branch modification or
tag change.
