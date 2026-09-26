# Bounded longer-horizon route

`ONE_STEP_CONTINUATION_VALUE` is one explicitly authorized route for PR-0002.
It does not add a general planner.

The route reads each current action's immediate consequence and continuation
state from an authenticated, problem-specific receipt. It then obtains fresh
G2 and G3 consequence-only forecasts for all three legal actions at each of
the two realized continuation states. The existing exact-relation router
selects one specialist for each `(continuation_state, action)` relation.

For current action `a`, the comparison value is:

```
(authenticated immediate consequence,
 maximum routed forecast at the authenticated continuation state)
```

Pairs are compared lexicographically. The second component is read only when
the first components tie. There is no sum, discount, recursion, simulated
transition, or predicted-next-state input to the downstream specialists.

All 12 downstream request intents are durably frozen before the first response.
The forecasts cannot execute or publish anything. If the pairs differ, one
selected current action may pass through the ordinary protected boundary once.
If they remain tied, no action is selected and the manager may request
`DEEPER_HORIZON_VALUE` with external-approval-only status.

The live ceiling is 12 consequence-only calls, plus the existing nine-call
current-decision integration batch only if the one-step comparison distinguishes
the actions: 21 calls total and at most one behavioral execution.
