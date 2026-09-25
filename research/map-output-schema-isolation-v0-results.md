# Map output-schema isolation v0 — results

**C — NOT ESTABLISHED.** Exactly eight real calls
completed; **8/8** were valid. Positive consequence forecasts were
**J 2/4** and **S 4/4**. There were
**2/4 improving pairs** and **0/4 regressions**.
Matching, authentic history, original post-response receipts, leak controls,
detachment, integrity and exact replay passed.

The experiment completed with all validity and integrity checks passing, but
**A fails because J predicted +1 in 2/4 cases, exceeding its frozen maximum of
1/4**. B also fails because S predicted +1 in 4/4, exceeding B's maximum of 1/4.
The correct final classification is C, not a failed execution or an A result.

Both improving pairs occurred in O2; both O1 pairs were +1→+1. The schema-only
arm was descriptively more accurate, but this sample does not establish the
registered output-schema effect. It also does not establish that changed target
wording caused the previous rescue. No internal mechanism is inferred.

## Preregistration and evidence

[Preregistration](map-output-schema-isolation-v0-preregistration.md), diagnostic
code, exact instructions, schedule and authentic-request hashes were committed
before inference as `06aa8715690ae785ec7453f7da38e7046548a504`.
Parent: `9646927d05943f687da778876c8bcb88cb8b1af9`.

[Compact results](../experiments/map_output_schema_isolation_v0/results.json)
preserve all raw/parsed outputs, receipt scores, paired comparisons, visible
histories, original setup and scored receipts, actual executions, fixed controls,
Measure counts, authorizations, Memory publications and source-record hashes.
[Verification](../experiments/map_output_schema_isolation_v0/verification.json)
contains control counts, model hashes, replay hashes and preservation checks.
[Replay instructions](../experiments/map_output_schema_isolation_v0/README.md)
require access to the retained private archive. Public compact evidence is not
the complete raw archive.

## All eight calls and four pairs

Every trial started at state 1 with one authentic HOLD history outcome (1,+1).
Every new scored original receipt was (1,+1). JSON is displayed compactly below;
exact response strings, including whitespace, are retained in `results.json`.

| Call | Block | Seed | Arm | Parsed response | Consequence correct | next_state correct | Joint exact |
|---:|---|---:|---|---|---|---|---|
| 1 | O1 | 99201 | J | `{"consequence":1,"next_state":1}` | yes | yes | yes |
| 2 | O1 | 99201 | S | `{"consequence":1}` | yes | n/a | n/a |
| 3 | O2 | 99201 | S | `{"consequence":1}` | yes | n/a | n/a |
| 4 | O2 | 99201 | J | `{"consequence":0,"next_state":1}` | no | yes | no |
| 5 | O2 | 99202 | J | `{"consequence":0,"next_state":1}` | no | yes | no |
| 6 | O2 | 99202 | S | `{"consequence":1}` | yes | n/a | n/a |
| 7 | O1 | 99202 | S | `{"consequence":1}` | yes | n/a | n/a |
| 8 | O1 | 99202 | J | `{"consequence":1,"next_state":2}` | yes | no | no |

J next_state accuracy was **3/4** and joint exactness
**1/4**, separately from consequence accuracy. S has no next_state or
joint exactness score; neither was inferred.

| Pair | J consequence | S consequence | Transition | Improvement | Regression |
|---|---:|---:|---|---|---|
| O1 / 99201 | 1 | 1 | 1 -> 1 | no | no |
| O1 / 99202 | 1 | 1 | 1 -> 1 | no | no |
| O2 / 99201 | 0 | 1 | 0 -> 1 | yes | no |
| O2 / 99202 | 0 | 1 | 0 -> 1 | yes | no |

Call 8's joint response `(next_state=2, consequence=+1)` had the wrong next_state
but a correct consequence. It therefore counts toward J's **2/4 consequence
positives**, despite being jointly wrong. Substituting J's **1/4 joint exactness**
for that consequence count would incorrectly turn this result into A and is not
permitted. Two pairs were 0→+1 and two were +1→+1; all other categories were zero.

## Exact matching and ordinary execution

The byte-identical first instruction sentence in both arms was:

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown.

The final instruction sentence was also identical. Only the middle response-format
sentence changed: J required next_state and consequence; S required consequence
alone. S did not ask to “predict the consequence.” It reused the previous
consequence-only diagnostic parser directly; J used the existing strict parser.

All four pairs passed exact matching before inference and on retained real
requests. Serialized task data were byte-identical, and normalizing only the
response-format sentence made the complete request bytes equal. Current state,
alias, authentic history, depth, epoch, transaction, historical next_state and
consequence, row order, model, sampler, paired seed and envelope matched. Both
arms retained num_predict=32, with the unchanged registered model and sampler.

Each independent setup started with empty Memory, state 1, epoch 1001, then
executed one ordinary HOLD. Its original receipt passed Measure and authorization
and published normally; the sole visible observation had transaction 1 and
outcome (1,+1). No moving fixture, synthetic history or depth change was used.

Both model outputs were detached probes. Neither entered protected Prediction
or received execution, authorization, publication, repair or Memory-write
capability. No model adapter was installed. After durable response and parse,
ordinary unchanged MapModel supplied the fixed **non-model (1,+1)** control,
epoch 1001, transaction 2, pre-state 1, action HOLD. That control was absent from
model input as a prediction; authentic history necessarily shared its values.

The execution method accepted no probe output or condition argument. After the
ordinary control latch, HOLD executed and generated a new original receipt.
Probe scores used that receipt only, never the control or declared law. All eight
scored events invoked Measure once and obtained committed, continued
`AUTHORIZED` Memory publication. Framework measurement_matches was true in 8/8
because it evaluated the non-model control; this is separate from model accuracy.

Eight setup plus eight scored executions produced **16 unique original live
receipts and 16 Memory publications**. Old observations remained unchanged.
Native state Recovery authorizations: 0 during setup,
0 during scoring. Explorer calls and model Recovery calls: zero.

## Actual validation and replay

Before inference, all eight canaries changed only the hidden next HOLD consequence
to −1 after authentic +1 setup. J/S requests remained byte-identical; subsequent
original receipts and Memory carried −1, and old +1 history remained intact.
These used zero model inference.

Eight synthetic detachment variants covered both arms, finite consequences,
wrong J next_state and invalid outputs; their grounded control, execution,
receipt, authorization and Memory records were identical. Additional executed
controls passed: eleven strict J-parser rejections, twenty reused S-parser
rejections, the three valid S integers, extra task-field mismatch rejection,
changed-first-sentence rejection, twelve classification cases, two durability
cases, and exact replay of eight synthetic responses. These are software checks,
not extra model arms or behavioral observations.

The real campaign's **72-record** hash chain and ordering passed:
intent → response → parse → non-model control latch → execution intent → original
receipt → Measure/publication. Original receipt object identity and full binding
were checked in execution and replay; serialized equality alone does not attest
to live object identity.

Exactly eight server generation requests matched eight recorded responses; no
retry, repair, replacement or extra call occurred. The owned server stopped.
Network-blocked replay made **zero inference calls** and reproduced seven data
files, eight snapshots and the empty writer-lock file (**16 files**) byte for byte.
Raw live/replay metrics retain provisional C / `AWAITING_EXACT_REPLAY`; final
classification was separately recomputed only after replay passed.

Simulated execution accounting: 8 registration setup + 64 preflight/control +
16 live + 16 replay = **104**. Only the eight live calls are behavioral evidence.
Model blobs were verified against registered hashes before inference.

## Frozen decision, limits and preservation

Observed thresholds: complete/valid 8/8; J +1 2/4
(A requires ≤1); S +1 4/4 (A requires ≥3; B requires ≤1);
improvements 2/4 (A requires ≥2); regressions 0/4 (A requires zero).
All scientific integrity gates passed. Consequence-based classification was
independently recomputed; J joint exactness did not replace the primary score.
No instruction, threshold, schedule or decision rule changed after inference.

This addresses one registered W1/self-loop case, one model configuration, two
alias blocks and two paired seeds. It does not establish a general mechanism,
production reliability or a protected model-proposal integration. The authentic
events were executions of the external software simulator, not physical-device
measurements. **W0 ADVANCE and W3 RETREAT moving +1 failures remain unexplained.**

All **730 parent tracked files**, including executable modes, are unchanged:
grounded baseline A and claim firewall, mechanical A, ranking forensics,
positive-depth B, self-loop coupling A, consequence-only isolation A, temporal
Map and Explorer negatives, stale-Memory results and authority history. These
detached probes do not rewrite or upgrade historical claims.

The eight-call campaign is complete and stopped. No production prompt adoption,
split Map, architecture implementation, tuning, extra seeds, mappings, arms or
calls. No push, main-branch modification or tag change.
