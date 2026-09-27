# Horus v0.7 grounded exploration protocol

This milestone tests whether Horus can acquire the receipt evidence needed by
relation-local routing without a forced calibration action. It does not train a
model, add a specialist, alter receipt authority, or collapse Memory.

## Frozen mechanics

Every decision predicts all three legal actions with the existing joint model,
G2, and G3. Consequences are selected independently for each exact
`(pre_state, action)` relation by the v0.6 router. The Explorer then either:

- **PROBE:** executes the highest-priority qualifying relation; or
- **EXPLOIT:** applies the existing mechanical consequence comparison when the
  probe budget does not select a candidate.

The finite probe priority is:

1. `PROBE_CONTRADICTION`
2. `PROBE_UNTRIED`
3. `PROBE_DISAGREEMENT`
4. `PROBE_STALE`

Ties use the oldest last execution and then `ADVANCE, HOLD, RETREAT` order. A
relation is stale after eight completed executions without being executed.
Current specialist disagreement is unresolved unless at least three local
receipt-scored observations exist and one specialist leads by at least two
correct predictions. A recent contradiction begins when a receipt differs from
the immediately preceding run of at least three identical authenticated local
outcomes. It remains unresolved until the local receipt window establishes the
same minimum-three, two-correct-prediction qualifying specialist lead used by
the router. That may retain the incumbent or cause a switch.

At most one probe may occur in any three-decision span. A probe at decision
`d` permits the next probe no earlier than `d+3`. A relation just probed cannot
be immediately probed again through another reason because the same global
budget applies. Probe mode, action, reason, forecasts, and confidence state are
HMAC-frozen durably before external execution. Outcomes cannot rewrite them.

Only authorized original receipts update confidence, Memory, or routing.
Invalid model output, corrupt routing/confidence state, unverifiable artifacts,
or a non-derivable reason fails closed.

## Prospective campaign

The campaign contains exactly 54 autonomous decision attempts and 486 model
calls, without retry or outcome-based extension:

| Segment | External regime | Decisions |
|---|---|---:|
| A1 | A | 18 |
| B1 | B | 9 |
| B2, after restart | B | 9 |
| A2 | A | 18 |

Every successful execution is labeled `EXPLORER_PROBE_EXECUTION` or
`EXPLORER_EXPLOIT_EXECUTION`. `ROUTING_CALIBRATION_EXECUTION` is forbidden.
The hidden regime is harness-only and unavailable to Map, specialists, router,
and Explorer. The campaign does not extend if HOLD is not revisited or either
switch fails to occur.

Probe usefulness is frozen as at least one of: first authenticated evidence for
an untried relation, revelation of a new contradiction, resolution of a current
specialist disagreement, or contribution within the local six-observation
window of a later router switch. Positive outcome alone is never sufficient.

The exploit-only comparison replays the frozen routed forecasts with probing
disabled. It compares decisions and information acquisition only. It never
constructs receipts or rewards for actions that were not executed.
