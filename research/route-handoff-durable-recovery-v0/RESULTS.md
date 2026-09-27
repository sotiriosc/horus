# Horus v0.22 — route handoff and durable-tail recovery

Status: **COMPLETED**.

The v0.21 endpoint replayed at authenticated state 1 with PR-0003 applicable. Global ordinary-probe cadence was available (`58 - 54 = 4`, minimum 3), and the unchanged Explorer derived decision 91 as `PROBE_DISAGREEMENT`, action `ADVANCE`. Under the frozen precedence rule, this ordinary route regained control and the remaining scoped fallback could not supersede it.

All eight recovery predicates passed. The checkpoint-registered call head at 2,502 was the exact prefix of the 2,529-record authenticated stream. Records 2,503–2,529 were exactly nine complete request/response/parse calls for the one unfinished decision 91. No receipt, Memory publication, routing evidence, Explorer completion, or contradictory durable state existed for that decision. Recovery registered the existing head without deleting or rewriting a call record.

The nine retained predictions were reused and **zero new model calls** were issued. The ordinary Explorer decision was frozen before execution. The protected path executed `ADVANCE` from state 1 under fresh runtime 16 / epoch 2016 and produced an original authenticated receipt with consequence `-1` and next state 2. Measure authorized it, Memory published it, and relation evidence sequence 58 scored it.

For `(1, ADVANCE)`, evidence row 1 was evicted and row 58 was added. The evicted row had G2 correct and G3 incorrect. The added row had G2 incorrect and G3 correct. The rolling six score changed from G2 `3/6`, G3 `4/6` to G2 `2/6`, G3 `5/6`. The three-correct lead exceeded the unchanged threshold, so selection switched from G2 to G3.

The resulting state-1 routed values are `ADVANCE=-1`, `HOLD=1`, and `RETREAT=0`; HOLD is the unique maximum and the prior `[ADVANCE, HOLD]` tie is gone. No follow-up ran because state moved to 2 and no exact reusable prediction batch existed there; issuing new model calls would have required separate authorization.

The problem-scoped v0.20 allowance remained exactly limit 2, granted 1, executed 1. The ordinary probe did not consume or replenish it. PR-0003 is `REASSESSED / VALUE_TIE_RESOLVED` with no requested capability. PR-0005 is `CLOSED / ROUTE_HANDOFF_RECOVERED` and remains separately linked to PR-0003.

No model training ran, no weights changed, no new route was added, and no router threshold or global Explorer policy changed.

After the authenticated execution completed, the first report-assembly attempt failed because the compact serializer expected an obsolete routing-row field. The execution and model calls were not repeated. The serializer was corrected and this report was rebuilt from the authenticated session, routing, Explorer, and Problem-Manager stores.

The narrow limitation is that one realized regime-A receipt supports the switch. This milestone demonstrates safe handoff, recovery, execution, and existing-router reassessment; it does not establish behavior under another regime or provide a follow-up decision at state 2.
