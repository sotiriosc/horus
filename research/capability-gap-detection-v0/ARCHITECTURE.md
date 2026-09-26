# Horus v0.9 capability-gap detection

V0.9 is an additive assessment layer over the completed v0.8 history. It does
not rewrite `PR-0001`, change Memory or receipt authority, train a model,
change G2/G3, alter the mechanical value comparison, or implement downstream
value estimation.

## Retrospective boundary

V0.8 gave `PR-0001` two authenticated problem-specific RETREAT receipts and no
problem-specific ADVANCE receipt. Under the v0.9 rule this is an epistemic gap,
not evidence that the immediate-consequence objective is insufficient. The
retrospective classification is therefore `MORE_EVIDENCE_REQUIRED`, localized
to `EVIDENCE_COVERAGE`. `PR-0001` remains `UNRESOLVED`.

A fresh successor `PR-0002` may use the unresolved history as its persistence
evidence. This preserves the earlier two-probe bound rather than reopening or
rewriting `PR-0001`. `PR-0002` has its own prospectively frozen two-probe bound
and coverage rule.

## Probe coverage and assessment

For a tied set, an action without a problem-specific authenticated receipt is
always ranked ahead of an already-probed action. Remaining priority is
specialist disagreement, unresolved contradiction, fewer local observations,
greater staleness, then canonical action order.

The finite assessments are:

- `MORE_EVIDENCE_REQUIRED`: relevant tied-action coverage is incomplete.
- `VALUE_TIE_RESOLVED`: a later ordinary decision at the problem state is no
  longer tied.
- `CURRENT_OBJECTIVE_CANNOT_DISTINGUISH`: every tied action has a legitimate
  problem receipt, immediate outcomes remain equal, current routed forecasts
  remain tied and valid, and the two allowed evidence routes are exhausted.
- `ROUTE_FAILED`: service, authorization, or protected execution prevented the
  required comparison.

An objective-gap assessment requests `LONGER_HORIZON_VALUE` with
`REQUEST_REQUIRES_EXTERNAL_APPROVAL`. It records predicted next states as model
outputs separately from authenticated realized next states and consequences.
The request cannot call a model, execute, change the objective, create an
architecture, train, or inspect the simulator law.

## Failure localization

Localization uses only registered labels: `MAP_NEXT_STATE`, `MAP_CONSEQUENCE`,
`RELATION_ROUTER`, `EXPLORER_VALUE_COMPARISON`, `EVIDENCE_COVERAGE`,
`RUNTIME_CAPACITY`, `MODEL_SERVICE`, and `REPRESENTATION`. This keeps “wrong,”
“cannot distinguish,” and “cannot proceed” mechanically separate.

## Future interface, intentionally unimplemented

`DownstreamValueRouteInput` binds current state, action, authenticated immediate
consequence, predicted next state, and authenticated-history reference.
`DownstreamValueRouteOutput` reserves a secondary value, comparison basis, and
evidence references. V0.9 defines these types only. It specifies no discount,
reward sum, scoring formula, model, or automatic grant.
