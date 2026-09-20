# Map self-loop / consequence coupling v0 — prospective registration

Parent: `1b1f75650215a333498e0d7de5ba23dc9db407ec` on
`research/map-positive-evidence-depth-v0`; preserve its **B — NO DEPTH RESCUE
OBSERVED** result. Grounded root: `79921b1da735e1495dffb695c00d7e7a21a234a6`.

Exactly eight real Map calls. No Explorer or model Recovery. No prompt,
architecture or history-depth change; no extra arms, retry, repair, replacement,
additional aliases/seeds, tuning or extension. Existing framework interfaces,
parser, Map instruction, sampler and receipt authority remain unchanged.

Each trial starts independently at state 1, epoch 1001 and empty Memory.

- **S:** one ordinary authentic HOLD execution, 1→1, +1; request Map at state 1.
- **M:** change only the external state-1 HOLD next_state from 1 to 2, keeping +1.
  Execute genuine HOLD 1→2, +1, then unchanged RETREAT 2→1 via ordinary original
  receipt/Measure/authorization/Memory publication. Request Map at state 1.

Both target histories have exactly one row, epoch 1001, transaction 1. M's
navigation event remains in Memory but is excluded from the state-1/HOLD
exact-pair projection. History is never handwritten, copied or synthesized.
All twelve external state/action relations are checked in zero-model software
controls: only state-1 HOLD next_state differs; every consequence is unchanged.
The external world fixture changes; no framework architecture or authority does.
Native deterministic state Recovery may occur on genuine moving transitions;
it is unchanged, separately recorded, and never a model Recovery call.

| Index | Block | Seed | Condition | HOLD alias |
|---:|---|---:|---|---|
| 0 | O1 mapping 0 | 99001 | S | K2 |
| 1 | O1 mapping 0 | 99001 | M | K2 |
| 2 | O2 mapping 0 | 99001 | M | M4 |
| 3 | O2 mapping 0 | 99001 | S | M4 |
| 4 | O2 mapping 0 | 99002 | S | M4 |
| 5 | O2 mapping 0 | 99002 | M | M4 |
| 6 | O1 mapping 0 | 99002 | M | K2 |
| 7 | O1 mapping 0 | 99002 | S | K2 |

Before inference, require the complete paired transport request bytes to differ
only at `VERIFIED_CHRONOLOGICAL_HISTORY[0].next_state`: S=1, M=2. All envelope
fields, model, instruction, sampler, seed, state, target alias, history epoch,
transaction, surface action, consequence, count and order must match. Normalize
that one field and require byte equality; additionally require exactly one wire
byte difference, digit 1→2. Any additional visible mismatch stops before
inference. Freeze all eight authentic-history-derived request hashes.

Model: `dolphin-mixtral:latest`, Ollama 0.1.16, 47B Q4_0. Manifest
`4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`;
weights `bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3`.
Sampler: temperature 0.2, top_p 0.9, top_k 40, num_predict 32, num_ctx 2048,
repeat_penalty 1.1 and the registered seed. Stateless, unchanged template,
no constrained decoding. Exact existing Map instruction:

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object with exactly two fields: next_state must be an integer in {0,1,2,3}, and consequence must be an integer in {-1,0,1}. Do not include any other fields or explanation.

No condition/hypothesis/movement/reward/self-loop/neutrality wording is added to
model input. Use the unchanged strict parser. After durable response and parse,
latch the finite prediction through the existing MapProposalAdapter and unchanged
framework; only then execute the scored HOLD and obtain its original authentic
receipt. Score next_state and consequence independently and their exact pair.
Record Measure, ordinary authorization, Memory publication and any native
Recovery. Actual receipts, not declared-law tables or history aggregates, score
the real campaign. Invalid stays invalid: no fallback latch or score execution,
continue only the remaining registered requests, and classify C. Ambiguous or
failed transport stops without automatic reissue.

Before inference, both conditions receive throwaway future-answer canaries:
after genuine history acquisition, alter only the hidden next scored HOLD
consequence to −1. Require exact request bytes unchanged. After a synthetic
latched forecast, execute and verify receipt and Memory really contain −1,
while old history stays unchanged. Canaries and software controls use zero model
calls and remain separate from behavioral evidence.

For each of four S/M pairs retain full finite predictions and classify consequence
transition 0→+1, 0→0, +1→+1, +1→0, or other/invalid. Improvement means S consequence
wrong and M consequence +1; regression means S +1 and M consequence wrong.
These comparisons concern **consequence**, not exact joint prediction. Report
next_state accuracy separately; incorrect next_state does not silently change
the consequence-based thresholds.

**A — SELF-LOOP / CONSEQUENCE COUPLING EFFECT OBSERVED** iff all eight calls
complete and are valid, S consequence +1 ≤1/4, M consequence +1 ≥3/4, improving
pairs ≥2/4, regressions 0/4, exact matched-request check passes, all scored
receipts are authentic and post-prediction, integrity passes and exact replay
passes.

**B — NO MOVEMENT RESCUE OBSERVED** iff M consequence +1 ≤1/4 with completed
valid receipt-scored set and matched-request/integrity/replay checks passing.

**C — NOT ESTABLISHED** for intermediate/mixed outcomes or missing requirements.
No statistical or broad mechanism threshold is added. If both conditions are
strong, report historical underprediction not reproducing in this sample.

Use established fsync write-ahead recording and one exclusive durable live
reservation. Persist request intent before dispatch, response before parse,
prediction latch before execution, and original receipt before Measure/publication.
Replay all eight retained responses with network blocked, reconstructing genuine
histories and post-latch events. Require byte-identical deterministic files and
snapshots. Synthetic controls are explicitly labeled and never count as real
model observations.

If A, the permitted narrow statement is: “Changing the authenticated prior
outcome from a positive self-loop to a positive state transition changed Map
consequence forecasts in this small matched W1 contrast.” This is compatible
with state-transition/consequence coupling, not an identified internal mechanism.
If B, the self-loop hypothesis is not supported by this diagnostic. Separate
next_state/consequence projections or queries remain only a possible later
design question if A; no fix is implemented here.

Freeze code, this registration, schedule and request hashes in Git before any
inference. Preserve every parent tracked file, the grounded/claim manifest,
mechanical A, forensics, depth B, temporal/Explorer negatives, stale-Memory and
authority results. New receipt-scored evidence does not upgrade any historical
detached or declared-law score. After exactly eight real calls, replay, report,
and stop. No push or main/tag changes.
