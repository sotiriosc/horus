# Horus v0.21 grounded relation reacquisition

Parent: `bec668b391fb90205923fe4b6202bf25465e5696`.

At the authenticated v0.20 endpoint, PR-0003 requests additional evidence for `(1, ADVANCE)`, its scoped probe budget is limit 2 / granted 1 / executed 1, and current state is 2. This freezes `TARGET_RELATION_NOT_CURRENT` without asserting that a route exists.

The transition graph is constructed only from authenticated `AUTHORIZED_REALIZED_EVENT` receipts in durable Memory. Each edge retains pre-state, action, realized next state and consequence, receipt identity, epoch, transaction, chronological event sequence, timestamp, and provenance hash. Model predictions, simulator tables, inferred laws, and counterfactuals cannot create edges.

The zero-inference one-edge search found five authenticated exact `state 2 + RETREAT → state 1` receipts. The selector chooses the action supported by the most recent receipt, then exact-transition repetition count, then canonical action order. It therefore freezes `RETREAT`, supported by event 55, receipt `HORUS:a67e675004193a13c31485bad53fbb86:runtime:12:ff1b1b2419b3ee4c / 1 / 2012 / 1`. Consequence values do not participate in selection.

One `GROUNDED_RELATION_REACQUISITION` execution is authorized for PR-0003 only. Its reason is `REACQUIRE_TARGET_RELATION_STATE`. The action is frozen before execution and must pass through the ordinary prediction, protected begin, external execution, original receipt, Measure, authorization, Memory, and relation-evidence path. There is no state reset or state injection.

If the navigation receipt does not realize state 1, record `REACQUISITION_TRANSITION_CONTRADICTED`, preserve both receipts, and stop. If it realizes state 1, record `TARGET_RELATION_REACQUIRED` and use exactly the one remaining v0.20 `PROBLEM_SCOPED_RELATION_PROBE` for `(1, ADVANCE)`. The existing limit is not reset or replenished.

After the second ADVANCE receipt, record the exact row evicted from and added to the rolling six-row relation window, both specialists' correctness and scores, challenger lead, and unchanged-router decision. Classify `G3_SWITCHES`, `G2_REMAINS`, `G2_STRENGTHENS`, `REACQUISITION_FAILED`, or `OPERATIONAL_FAILURE` without outcome tuning.

Only if G3 switches and the mechanically recomputed state-1 values have a unique maximum may one ordinary follow-up run. It receives no special route, navigation objective, or option-profile override.

The live ceiling is three behavioral decisions and 27 logical local model calls: one navigation execution, one already-authorized remaining scoped probe, and one conditional ordinary follow-up, at nine calls per decision. There are no retries, training runs, model changes, router-threshold changes, probe-budget replenishments, global navigation, or multi-step searches.
