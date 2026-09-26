# Horus v0.13 canonical problem-ownership results

## Outcome

The zero-inference milestone succeeded. The bounded live continuation then
reached its first preregistered terminal condition in two decisions:

1. decision 84 used PR-0003's one `DEADLOCK_INFORMATION_PROBE`, selected
   `ADVANCE`, and received an authenticated consequence `-1`, next-state `2`
   receipt;
2. decision 85 selected PR-0002 by its exact state-2 scope, abstained on the
   existing `[ADVANCE,RETREAT]` tie, and the existing evidence assessment reached
   `CURRENT_OBJECTIVE_CANNOT_DISTINGUISH`.

The scientific status is `ROUTE_EXECUTED_NORMAL_OPERATION_RESUMED`. State 2 was
reached as an observed receipt outcome, never as an action-selection input or
optimization target.

## Canonical graph

| Problem | Scope | Owner | Final state | Assessment/request | Budget |
|---|---|---|---|---|---|
| PR-0001 | state 2 / `ADVANCE,RETREAT` | `EVIDENCE_COVERAGE` | `SUPERSEDED` canonical node; exact imported snapshot remains `UNRESOLVED` | `MORE_EVIDENCE_REQUIRED` / `MORE_RELATION_EVIDENCE` | legacy relation probe 2/2 |
| PR-0002 | state 2 / `ADVANCE,RETREAT` | `EVIDENCE_COVERAGE` | `REASSESSED` | `CURRENT_OBJECTIVE_CANNOT_DISTINGUISH` / `LONGER_HORIZON_VALUE` | legacy relation probe 2/2 |
| PR-0003 | state 1 / `ADVANCE,HOLD` | `EXPLORER_VALUE_COMPARISON` | `ROUTE_EXECUTED` | none | deadlock probe 1/1 |

The only lineage edge is `PR-0002 successor_of PR-0001`. PR-0003 remains an
independent problem. `LONGER_HORIZON_VALUE` was requested with external-approval
status and was not implemented.

## Detection and selection

Retrospective replay opened PR-0003 at decision 65, the second consecutive
identical valid tie with no intervening execution. Later retained attempts
appended evidence to that same problem.

At decision 84, both tied actions were unprobed for PR-0003, both specialists
disagreed, and neither action had an unresolved contradiction. `ADVANCE` had
four authenticated exact-relation observations versus `HOLD`'s twelve, so the
frozen information priority selected `ADVANCE` before staleness or canonical
order was needed. The selector received relation confidence and the tied set;
it did not receive the simulator transition table, future receipt, hidden
regime, or desired destination.

Exact scope lookup then changed the applicable identity from PR-0003 at state 1
to PR-0002 at state 2. No global current-problem pointer was used.

## Accounting

| Measure | Result |
|---|---:|
| Fresh decisions | 2 / 8 maximum |
| Local model calls | 18 / 72 maximum |
| Authorized executions | 1 |
| Abstentions | 1 |
| Deadlock probes granted/executed | 1 / 1 |
| Retries | 0 |
| Training runs | 0 |

PR-0002's relation-probe budget remained 2/2 while PR-0003 independently moved
from 0/1 to 1/1. Restart retained the consumed PR-0003 allowance.

## Post-campaign reporting failure

After the loop had reached its terminal condition and completed both durable
decision records, the public-result serializer raised `KeyError: pre_state`.
Authorized rows store that value inside the durable training record rather than
at the top-level location expected by `_plain_rows`.

The originally requested result file was therefore not created. The campaign
was not patched or rerun. `reconstructed-live-result.json` is a compact
reconstruction from the authenticated journals, and `operational-failure.json`
records the failure separately. Raw private prompts and responses are excluded.

## Verification

- The session, exploration, routing, and canonical manager stores reopened and
  validated after the run.
- The manager bound exactly to session attempt 85 and authorized execution 54.
- Replaying the 29 authenticated manager records reconstructed the exact graph
  and consumed budgets.
- A deliberately corrupt disposable index was rebuilt from the authoritative
  stream to the same state.
- 157/157 full Horus Python tests passed after the run.
- 53/53 core regression steps passed after the run.

The remaining implementation defect is confined to post-campaign result
serialization. It has not been repaired in this milestone. The larger research
limitation is that the canonical manager currently supports the finite v0.13
scope/type set and one deterministic route; it is not a learned problem detector
or route planner.
