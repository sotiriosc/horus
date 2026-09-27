# Horus v0.19 scoped relation reassessment

## Result

`ROUTING_CORRECT_AS_FROZEN`

The retained `(state 1, ADVANCE)` router state exactly replays. G2 remains selected because the current five-observation window is tied: G2 is correct 3/5 and G3 is correct 3/5. The frozen rule requires at least three shared observations and a challenger lead of two. The most recent authenticated comparison favored G3, but it only erased G2's prior one-point lead.

PR-0003 now records `MORE_RELATION_EVIDENCE_REQUIRED`. No existing route can legally execute it: the ordinary `RELATION_PROBE` cadence is at distance 2 with a minimum of 3, and the PR-0003 deadlock probe budget is consumed at 1/1. A non-authoritative request for a scoped `(1, ADVANCE)` `RELATION_PROBE` was appended, and execution stopped for external approval.

## PR-0003 reconstruction

PR-0003 was created at decision 65 for state 1 and tied actions `[ADVANCE, HOLD]`. The same tie was reobserved through decision 84. Its preregistered deadlock allowance was one probe. At decision 84 the route selected ADVANCE before execution: G2 predicted `+1`, G3 predicted `-1`, and the authenticated receipt returned consequence `-1` and next state `2`. This was the single granted and executed deadlock probe.

Before this reassessment PR-0003 was `ROUTE_EXECUTED`, with deadlock budget `{limit: 1, granted: 1, executed: 1}` and no pending capability. The zero-inference audit appended one scoped external request. It is now `ROUTE_REQUESTED`, assessment `MORE_EVIDENCE_REQUIRED`, requested capability `MORE_RELATION_EVIDENCE`; the consumed deadlock budget is unchanged.

## `(1, ADVANCE)` authenticated routing evidence

| Evidence | G2 | G3 | Realized | G2 correct | G3 correct | Before | After |
|---:|---:|---:|---:|:---:|:---:|:---:|:---:|
| 1 | -1 | +1 | -1 | yes | no | G2 | G2 |
| 16 | -1 | -1 | -1 | yes | yes | G2 | G2 |
| 28 | -1 | -1 | +1 | no | no | G2 | G2 |
| 50 | -1 | -1 | -1 | yes | yes | G2 | G2 |
| 54 | +1 | -1 | -1 | no | yes | G2 | G2 |

The current window contains all five rows. Scores are G2 3/5 and G3 3/5; G3 lead is 0; selected specialist is G2; minimum evidence is 3; required challenger lead is 2.

For the current state-1 tie, HOLD also replays exactly. Its six-row window scores G2 6/6 and G3 1/6, with G2 selected. The complete twelve-row HOLD trace is retained in `routing-evidence.json`.

## Reassessment and stop

The routed values remain `ADVANCE=+1`, `HOLD=+1`, `RETREAT=0`. The ordinary result remains `EXPLOIT_TIED_MAXIMUM`, with no action. There was no router switch, ordinary follow-up, receipt, Memory publication, routing update, training, horizon extension, option-profile use, or model call.

Final PR-0003 assessment: `MORE_RELATION_EVIDENCE_REQUIRED`.

PR-0002's canonical object hash remained unchanged. Its option-profile authority did not enter PR-0003. The request reason is only relation-specific evidence insufficiency; hidden destination information and the known transition to state 2 were excluded.

## Verification and limit

Authenticated replay passed for the session, problem manager, relation evidence, and Explorer confidence stores. The full Horus suite passed 247/247 tests, including fourteen scoped v0.19 tests, and all 53 core regression steps passed. V0.18 public evidence is unchanged.

This audit establishes why G2 still controls; it does not establish which specialist will win after another receipt. Live evidence is required, but no retained route currently has authority to gather it. External approval is required before any fresh decision or call.
