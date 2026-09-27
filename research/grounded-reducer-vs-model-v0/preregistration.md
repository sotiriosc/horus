# Grounded reducer versus model v0 — prospective registration

Parent completed v0.1 commit: `0341322b1f9494f16d76f9a746668ffb9bd4ef23`.
That study remains `HORUS_NET_HARMFUL` with unchanged evidence. The new study
uses fresh isolated arms for **each** schedule; no behavioral state is copied
from v0.1 or between schedules. Zakhor, Horus cognition, training and route
selection are absent. Shared receipt authorization, fail-closed publication,
modern append-only authenticated Memory, provenance/replay, bounded transport
repair and durable recovery remain engineering infrastructure.

## Frozen prediction rules

All arms execute only the registered observation-controlled HOLD action. No
Explorer chooses an action. M uses the previously validated exact-relation
retrieval (recent four, newest missing-consequence anchors, recency fill to six,
chronological prompt order), the unchanged common joint next-state model,
unchanged frozen G2 consequence specialist, seed 20260927 and temperature zero.
Only the HOLD joint and G2 requests are needed per observation. These are the
same request bodies as the HOLD requests in the previous M batch. M does not
predict unused ADVANCE/RETREAT actions. M has no cold-start heuristic: its
frozen model handles an empty history.

L predicts the consequence of the **latest authorized receipt for exact
`(pre_state,HOLD)`** from the existing durable memory. R3 takes at most the
three latest authenticated consequences for the exact relation, chooses the
most frequent value, and resolves any tie by the latest observation among the
tied values. Both predict next state from the latest exact receipt. With **zero**
exact receipts, both predict neutral consequence **0** and identity next state
(equal to current state); these cases are counted separately. No model, hidden
process state, new index, router, or prompt reinterprets their history.

## Frozen schedule

The four schedules below are independent, fresh matched campaigns. All arms
receive the same prospectively ordered hidden external regime and a separately
authenticated original receipt for each observation. Model predictions precede
the receipt. Each row in `protocol.py` has fixed schedule, event number,
observation identity, regime, phase and HOLD action before live inference.
`A`/`B` are the existing external simulator's consequence regimes. An isolated
noise event is exactly one hidden B consequence override followed immediately
by return to A; it is neither disclosed to the predictors nor inserted as an
unprotected synthetic memory. All three arms receive the same anomalous
realized consequence through their own protected execution.

| Schedule | Events | External sequence | Phases |
|---|---:|---|---|
| A: clean change | 12 | A×4, B×4, A×4 | stable, change/persistence, restoration |
| B: isolated noise | 9 | A×4, B×1, A×4 | stable, one anomaly, recovery |
| C: change after noise | 12 | A×4, B×1, A×3, B×4 | stable, anomaly, recovery, genuine change |
| D: restoration timing | 14 | A×4, B×6, A×4 | stable, longer change, restoration |

Schedule A restarts a fresh worker process after event 6. It checks exact
protected file hashes, durable-memory hash and replay, authenticated event count,
scheduled identities and separate receipt sources before continuing. L and R3
are reconstructed solely from protected memory. After restart and before event
7, one registered malformed joint-model output is injected **after** M obtains
an otherwise valid model response. The attempt and strict parser rejection are
retained. All three arms have unchanged receipt and memory counts and resume
with the ordinary scheduled event 7. Operational transport failures are logged
separately and never reinterpreted as this perturbation.

For each ordinary event: prepare M, L and R3 without changing experience;
validate all; then execute independently in private transaction state and
publish one validated triple snapshot through a single atomic `current`
pointer. Failed preparation publishes no event in any arm and stops. Any
mismatch or private execution failure is INVALID and stops without automatic
resumption. Atomicity here is committed visibility for the simulated worlds,
not simultaneous physical actuation. Each arm's authorized receipt stays local.

## Call and transport ceiling

There are 47 ordinary matched opportunities and one perturbation opportunity.
M makes two logical model requests per opportunity, for **96 logical calls**.
L and R3 make **zero** model requests. Maximum one exact-byte transport repair
per M call permits at most **192 physical attempts**. The unchanged v0.1
transport rule and hash apply equally to every eligible M call. No semantic
invalid output is retried. Valid calls are never regenerated as a batch. Model
transport is not part of comparative prediction accuracy.

## Frozen metrics and interpretation

Report consequence accuracy overall, by schedule and phase, early/middle/late
thirds, worst rolling four, first-correct adaptation latency within each
sustained change and restoration phase, false persistence, the anomaly-event
error and next-event recovery error, false regime switches after isolated
noise, cold-start score separately, call counts, context tokens, inference
latency and campaign wall time. Accuracy is scored from original authenticated
receipts only. Consequence prediction is primary; next-state exact match is
reported as a diagnostic.

For each M error, report non-exclusive flags: correct current signal supplied,
stale signal matched the wrong prediction, contradictory supplied history,
no exact history, and wrong despite a clear recent grounded signal. A current
signal means an authenticated receipt with the correct consequence from the
ongoing sustained external phase, known only to the **post-event audit**. Clear
means the three most recent exact receipts before the event unanimously match
the realized consequence. This audit does not enter any prediction.

For each L/R3 error, assign one primary cause in this order: no exact history
(`INSUFFICIENT_HISTORY`); anomaly or post-anomaly overreaction when the most
recent outcome is the isolated anomaly (`LATEST_OUTCOME_WAS_NOISE`); R3 tie
resolved toward a wrong latest observation (`TIE_RULE_ERROR`); wrong forecast
within two receipts after a sustained regime transition (`WINDOW_TOO_SLOW`);
otherwise `OTHER_MECHANICAL`. The first unknown regime event is also labeled
`INSUFFICIENT_HISTORY` for the **new regime** even if old exact history exists.
Report all raw evidence and classification context alongside the labels.

Head-to-head classification excludes each schedule’s first cold-start event;
those four events are scored and reported separately. Model-call costs include
cold starts. Classification is descriptive and requires protected/restart/perturbation/
matching/accounting/replay validity; otherwise INVALID. With validity:
`SPEED_ROBUSTNESS_TRADEOFF` if L is strictly faster than R3 in at least one
sustained transition (no slower in any) and R3 has fewer post-anomaly errors
across B and C, with neither reducer dominating the challenged phase windows;
`MECHANICAL_GROUNDING_SUFFICIENT` if at least one reducer matches/exceeds M in
**each schedule and each challenged phase** and exceeds it in at least one,
with fewer model calls; `MODEL_INTERPRETATION_ADDS_VALUE` if M has a uniquely
correct prediction where both reducers are wrong in at least two distinct
schedule/phase settings; otherwise `MIXED`. Apply the tradeoff rule first, then
sufficiency, then model value. Do not choose a winner by one aggregate score.
No architecture change, training, Horus or Zakhor addition follows this run.
