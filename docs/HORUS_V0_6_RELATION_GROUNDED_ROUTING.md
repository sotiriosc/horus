# Horus v0.6 relation-grounded routing

Status: frozen before live inference.

V0.6 retains the exact G2 and pure G3 adapters from v0.5. G2 remains globally
`ACTIVE`; G3 remains globally `REJECTED` and separately
`ROUTABLE_SPECIALIST`. Generation 3R is absent. No weights, model, Explorer,
next-state path, or router are trained.

## Relation identity and evidence

The bounded routing identity is exactly `(pre_state, action)`, using the
authenticated underlying action rather than its presentation alias. Evidence
for `(1, HOLD)` cannot affect `(0, HOLD)`, `(1, ADVANCE)`, or any other
relation. This is a narrow engineering representation for this experiment,
not a claim that state/action is a complete general representation of
relations.

Each relation cold-starts at G2. Its most recent six shared authorized
receipt-scored observations form its local window. At least three observations
are required, and a challenger must lead the relation incumbent by at least
two correct predictions. Ties retain the incumbent. The same rule applies
after a switch.

Both specialists predict every legal action from the same authenticated
context before routing or execution. The router then selects a specialist
independently for every `(state, action)` forecast. Mechanical Explorer sees
the resulting three routed consequences. Only the executed relation is later
scored, and only against its authorized original receipt.

## Frozen campaign

Every calibration action is a real forced action through the existing trusted
execution boundary. It is labeled `ROUTING_CALIBRATION_EXECUTION`, creates an
original receipt, passes ordinary Measure/authorization, and enters Memory.
It is not evidence that Explorer would have selected HOLD.

| Segment | Hidden regime | Fixed work | Process boundary |
|---|---|---|---|
| A1 | A | six `(1,HOLD)` calibrations, one ordinary comparison batch | start |
| B1 | B | three `(1,HOLD)` calibrations | A→B transition |
| B2 | B | three `(1,HOLD)` calibrations, one ordinary comparison batch | required restart |
| A2 | A | six `(1,HOLD)` calibrations, one ordinary production execution | B→A transition |

HOLD is a self-loop at state 1, so the 18 calibration events guarantee six
real observations in each phase without reset, navigation, fabricated
outcomes, or simulator changes. The A1 and B comparison batches compute
G2-only, G3-only, and locally routed Explorer choices from one shared frozen
prediction batch and execute none of those paths. The A2 ordinary batch
computes the same three choices and executes only the locally routed production
choice.

The campaign contains 21 prediction batches. Every batch makes three existing
joint next-state calls, three G2 consequence calls, and three G3 consequence
calls, for exactly 189 scheduled real model calls. It contains 19 scheduled
executions: 18 calibrations and one Explorer-selected production execution.
No phase or segment may be extended because of the result.

## Causal and persistence requirements

```text
all nine requests committed
→ all nine responses durably parsed
→ local specialist selected independently for each action
→ Explorer choices computed
→ one registered path executes, or comparison is explicitly nonexecuting
→ original receipt authorized and published to Memory
→ both frozen predictions for the executed relation scored
→ that relation's routing evidence updated for future batches
```

The B restart occurs after three contradictory target receipts. On resume the
registry, both artifacts, the HMAC-chained relation evidence, every relation's
selection, chronological Memory, source identity, and epoch are reverified.
Simulator regime is audit-only and is absent from model requests and routing
inputs.

Afterward, the v0.5 global router is replayed offline over the same frozen
predictions and receipts. This makes no new model calls and supports only a
routing-selection comparison. It is not a counterfactual executed-outcome
claim.

Private authority keys, session checkpoints, and raw prompt/response streams
remain outside the public repository. Compact receipt-linked evidence and
aggregate results may be published after completion.
