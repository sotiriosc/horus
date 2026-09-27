# Horus v0.20 scoped evidence authorization result

V0.19 was preserved unchanged at `a5472be42355c45e4accb85142f6d3d83cfa2083` and pushed to `build/horus-v0.19-scoped-relation-reassessment` before this work.

## Zero-inference result

The ordinary cadence cannot advance through abstentions. At the v0.19 endpoint, authorized executions were 55 and the last ordinary probe was authorized execution 54. The next authorized index was therefore 56, giving distance 2 against the unchanged minimum distance 3. An abstention changes neither authorized-execution count nor the last-probe marker, so repeated abstention leaves distance 2. This mechanically established `ROUTE_GATING_DEADLOCK` for PR-0003, `(1, ADVANCE)`, `MORE_RELATION_EVIDENCE`, blocked by `RELATION_PROBE_CADENCE`.

The separate external grant authorized at most two `PROBLEM_SCOPED_RELATION_PROBE` executions for exactly PR-0003 and `(1, ADVANCE)`, with the frozen reason `GROUND_RELATION_FOR_SPECIALIST_SELECTION`. It did not alter the global cadence, router threshold, specialist artifacts, option profiles, horizon, or training.

## Live result

Exactly one scoped probe ran, using nine logical model calls and 27 authenticated call-stream records. All nine responses parsed. The original authenticated receipt was:

| Field | Value |
|---|---|
| action | `ADVANCE` |
| pre-state | 1 |
| consequence | -1 |
| next state | 2 |
| epoch | 2014 |
| event / transaction | 1 / 1 |
| source | `HORUS:a67e675004193a13c31485bad53fbb86:runtime:14:030997733fe0c0e2` |

The unchanged six-observation router window became:

| Specialist | Correct | Total |
|---|---:|---:|
| G2 | 3 | 6 |
| G3 | 4 | 6 |

The absolute lead was 1, below the required lead 2. G2 remained selected. The mechanically recomputed state-1 routed values remained `ADVANCE=1`, `HOLD=1`, `RETREAT=0`; the `[ADVANCE,HOLD]` tie therefore persisted.

A second scoped probe did not run because the authenticated first execution moved the current state to 2, so the exact target relation `(1, ADVANCE)` was no longer current. This was a preregistered eligibility stop, not outcome tuning. No ordinary follow-up ran because the original state-1 tie did not disappear.

The result is `MORE_RELATION_EVIDENCE_REQUIRED`. The Problem Manager's canonical stored enum remains `MORE_EVIDENCE_REQUIRED`, with requested capability `MORE_RELATION_EVIDENCE`. PR-0002 is byte-for-byte unchanged. The scoped mode did not consume or reset the ordinary probe marker: it remained authorized decision 54. As with every authenticated execution, the global authorized-execution count advanced from 55 to 56.

## Verification

All authenticated session, relation-routing, Explorer-confidence, and Problem-Manager stores replay exactly. The post-result repository suite passed 262/262 tests, including the 15 v0.20 properties. All 53 core regression steps passed. No training ran and no model or router threshold changed.

The remaining limitation is that one new receipt only produced a one-point G3 lead and the real transition left the target relation. V0.20 therefore does not establish which specialist is better for `(1, ADVANCE)`, does not resolve the state-1 value tie, and does not show ordinary behavior resuming.
