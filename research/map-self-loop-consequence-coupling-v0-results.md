# Map self-loop / consequence coupling v0 — results

**A — SELF-LOOP / CONSEQUENCE COUPLING EFFECT OBSERVED.** Exactly eight real Map
calls completed and were valid. Positive consequence predictions were **0/4 S**
and **4/4 M**. All four paired consequence forecasts improved from 0 to +1;
none regressed. Integrity, matched-request checks and exact replay passed.

> Changing the authenticated prior outcome from a positive self-loop to a
> positive state transition changed Map consequence forecasts in this small
> matched W1 contrast.

This is compatible with state-transition/consequence coupling. It does not
identify an internal mechanism or establish that interference caused the errors.

## Registration and evidence

The [preregistration](map-self-loop-consequence-coupling-v0-preregistration.md),
code, schedule and authenticated-request hashes were committed before inference
as `aab4ce50dfce7438ca97dde6529b04e8ba47cfb7`. Parent:
`1b1f75650215a333498e0d7de5ba23dc9db407ec`. The existing Map instruction, strict
parser, model and sampler were unchanged. Seeds were 99001 and 99002; the only
blocks were O1 mapping 0 (HOLD=K2) and O2 mapping 0 (HOLD=M4).

[Compact results](../experiments/map_self_loop_consequence_coupling_v0/results.json)
contain every raw model output, parsed prediction, paired comparison, visible
history, original setup and score receipts, actual scored execution,
authorization, measurement match and source-record hashes.
[Verification](../experiments/map_self_loop_consequence_coupling_v0/verification.json)
records control counts, model hashes, replay file hashes and preservation checks.
[Reproduction instructions](../experiments/map_self_loop_consequence_coupling_v0/README.md)
explain zero-inference replay using the retained private archive. The public
compact evidence is not the complete raw replay archive.

## All eight observations

Pairs below are `(next_state, consequence)`. Each model-visible target history
contains exactly one authenticated observation. Both requests start at state 1.

| Call | Block | Seed | Condition | Prior outcome | Prediction | New receipt outcome | Consequence correct | Exact |
|---:|---|---:|---|---|---|---|---|---|
| 1 | O1 | 99001 | S | (1,+1) | (1,0) | (1,+1) | no | no |
| 2 | O1 | 99001 | M | (2,+1) | (2,+1) | (2,+1) | yes | yes |
| 3 | O2 | 99001 | M | (2,+1) | (2,+1) | (2,+1) | yes | yes |
| 4 | O2 | 99001 | S | (1,+1) | (1,0) | (1,+1) | no | no |
| 5 | O2 | 99002 | S | (1,+1) | (1,0) | (1,+1) | no | no |
| 6 | O2 | 99002 | M | (2,+1) | (2,+1) | (2,+1) | yes | yes |
| 7 | O1 | 99002 | M | (2,+1) | (2,+1) | (2,+1) | yes | yes |
| 8 | O1 | 99002 | S | (1,+1) | (1,0) | (1,+1) | no | no |

Next-state predictions were independently correct in **8/8** cases: 4/4 S and
4/4 M. Joint exactness was 0/4 S and 4/4 M. For each of O1/99001, O1/99002,
O2/99001 and O2/99002, the S→M consequence transition was **0→+1**. There were
zero 0→0, +1→+1, +1→0, other or invalid pairs.

Every scored event invoked Measure once and obtained `AUTHORIZED`, committed,
continued publication of the actual receipt outcome into Memory. Measurement
matched the prediction in four M events and disagreed in four S events. A wrong
consequence forecast was retained as wrong; it was not repaired to earn credit.

## Matching, grounding and controls

Each trial began with empty Memory. S executed one genuine HOLD 1→1,+1. M
executed genuine HOLD 1→2,+1 and then ordinary RETREAT 2→1,+1. All setup records
published through the ordinary receipt/Measure/authorization path. M's navigation
observation remained in Memory but was absent from the exact-pair state-1/HOLD
projection. Both visible histories had epoch 1001 and transaction 1.

Before inference and again on retained real requests, all four pairs differed
at exactly one wire byte: the historical `next_state` digit 1→2. Normalizing
only that field made complete request bytes equal. All other payload and
transport fields matched, including consequence +1, history depth, ordering,
state, alias, epoch, transaction, model, instruction, sampler and seed.

Zero-model preflight executed all twelve state/action relations in both external
fixtures. Only state-1/HOLD next_state changed; all consequences stayed the same.
Eight throwaway canaries changed only the hidden future scored consequence to
−1 after authentic setup. Request bytes stayed unchanged, while subsequent
original receipts and Memory carried −1 and old history remained intact.

Additional executed controls covered eleven strict-parser rejections, ten frozen
decision boundaries, two interrupted-journal durability cases, an invalid output
with no scored execution, extra-field mismatch rejection, and eight synthetic
responses with exact synthetic replay. These were software controls, not model
observations or additional experimental arms.

For the real campaign, each new scored event occurred after durable response,
strict parse and prediction latch. Original receipt identity and full binding
were checked during live execution and replay. Twenty distinct live original
receipts covered twelve setup executions and eight new scored executions, with
twenty ordinary Memory publications. There were four native deterministic state
Recovery authorizations during setup and zero during scoring; there were **zero
model Recovery calls and zero Explorer calls**.

The 72-record journal passed its chain and ordering checks. Exactly eight server
inference requests matched eight recorded responses. There were no retries,
replacement calls or prediction repairs. The owned model server was stopped.
Network-blocked replay issued zero inference calls and reproduced seven data
files, eight snapshots and the empty writer-lock file byte for byte (16 files).
Raw live and replay metrics retain their provisional C / `AWAITING_EXACT_REPLAY`
status; the separate final result is A only after the completed replay audit.

Execution accounting: 12 registration setup executions; 85 preflight/control
executions; 20 live executions; 20 replay executions: **137 simulated world
executions total**. Only the eight real Map calls constitute behavioral evidence.

## Frozen decision and limits

All A requirements passed: 8/8 complete and valid; S positive 0/4 ≤1/4;
M positive 4/4 ≥3/4; improving pairs 4/4 ≥2/4; zero regressions; matched requests;
authentic post-prediction scoring; integrity; exact replay. The classification
was independently recomputed from consequence predictions, not joint accuracy.
No threshold or decision rule was changed after observation.

This is an eight-call contrast using one model configuration, two alias blocks
and two paired seeds. Its authentic events are executions of the external
software simulator, not measurements from physical hardware. The model-visible
historical next_state and the corresponding external fixture relation differ;
the observed response contrast does not reveal the model's internal reason for
using that information. No broader transfer or end-to-end success is claimed.

All **706 parent tracked files** were verified unchanged, including their
executable modes. The grounded root and claim firewall, grounded baseline A,
mechanical baseline A, ranking forensics, positive-evidence depth **B — NO DEPTH
RESCUE OBSERVED**, temporal Map and Explorer negatives, stale-Memory results and
authority history remain intact. This study does not upgrade historical detached
or declared-law scores or reinterpret the earlier decomposition result.

Separate next_state and consequence projections/queries remain only a possible
future design question. No fix, prompt tuning, architecture change, extra seeds,
aliases, arms or extension was implemented. The campaign is complete and stopped.
No push, main-branch update or tag change was made.
