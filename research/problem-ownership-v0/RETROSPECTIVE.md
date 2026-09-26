# V0.13 zero-inference retrospective

The canonical manager imported PR-0001 and PR-0002, then replayed the retained
decisions 64--83. This phase did not enable a deadlock route and made zero model
calls, zero world executions, and zero training runs.

The replay mechanically created `PR-0003` at decision 65, the second consecutive
state-1 `[ADVANCE,HOLD]` tied maximum with no intervening authorized execution.
Decisions 66--83 appended evidence to the same scoped problem; they did not
create duplicates.

The resulting graph contains:

| Problem | Type | Exact scope | Owner | State | Independent budget |
|---|---|---|---|---|---|
| PR-0001 | `UNRESOLVED_VALUE_TIE` | state 2 / `ADVANCE,RETREAT` | `EVIDENCE_COVERAGE` | `SUPERSEDED` canonical node; imported snapshot remains `UNRESOLVED` | legacy relation probe 2/2 |
| PR-0002 | `UNRESOLVED_VALUE_TIE` | state 2 / `ADVANCE,RETREAT` | `EVIDENCE_COVERAGE` | `ROUTE_EXECUTED` | legacy relation probe 2/2 |
| PR-0003 | `UNRESOLVED_VALUE_TIE` | state 1 / `ADVANCE,HOLD` | `EXPLORER_VALUE_COMPARISON` | `OPEN` | deadlock probe 0/1 |

The graph has one conservative lineage edge: `PR-0002 successor_of PR-0001`.
PR-0003 has no inferred relationship to either state-2 problem.

Exact scoped lookup selects PR-0003 for state 1 / `[ADVANCE,HOLD]` and PR-0002
for state 2 / `[ADVANCE,RETREAT]`. PR-0002 did not block PR-0003 creation.

The manager reopened from its authenticated stream to the same graph and stream
head. Deliberately corrupting the disposable index in tests caused it to be
rebuilt from the stream. Operational and runtime-capacity test problems remained
separate from their behavioral problem, with only explicit `blocked_by` edges.

This result satisfies the prerequisite for separately preregistering the
bounded `DEADLOCK_INFORMATION_PROBE`. At this retrospective checkpoint the
route is still disabled and no allowance has been granted.
