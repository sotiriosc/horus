# Horus v0.8 problem/route request results

## Result

The bounded self-problem milestone is established. A persistent state-2 value
tie opened one non-authoritative problem at decision 32. The broker granted
only `TIE_INFORMATION_PROBE`, the Explorer selected `RETREAT` from the tied
maximum set, and normal protected execution produced an original authorized
receipt. That receipt updated Memory, relation routing, confidence, and the
problem evidence. No calibration or forced action was used.

The result is mixed beyond that milestone. Both allowed probes escaped state 2
and enabled continued A2 grounding, including a later G3→G2 switchback. They did
not permanently resolve the original ranking tie. When the same tie appeared
again after the two-probe allowance, the problem correctly became
`UNRESOLVED` and Horus abstained at decision 54.

## Identity, taxonomy, and frozen rules

- Branch: `build/horus-v0.8-problem-route-request`
- Parent: `0155df09d7cad0b6df9fefd185d3da25b64389fd`
- Implementation: `2c7375f5185d305647085ec9261bf620e4aa248b`
- Preregistration: `4d1b5c79a659a30212874a53084b8a0764888eac`
- Preflight: `41baf62`
- Taxonomy: `UNRESOLVED_VALUE_TIE`, `UNRESOLVED_RELATION`,
  `EXTERNAL_SERVICE_PROBLEM`, `INTERNAL_ROUTE_PROBLEM`
- Detection: two consecutive attempts at the same state with the same tied
  maximum action set and no authorized execution between them
- Registered routes: `NORMAL_EXPLOIT`, `RELATION_PROBE`,
  `TIE_INFORMATION_PROBE`
- Tie-probe order: specialist disagreement, unresolved contradiction, less
  authenticated local evidence, greater staleness, canonical action order
- Bound: at most two tie-information probes per problem

The problem object has explicit false-valued authority fields. It cannot
execute, alter Memory, choose a specialist, change a prediction, train, change
a protected bound, alter the simulator, or create a receipt.

## Prospective schedule and counts

The campaign ran A decisions 1–18, B decisions 19–36, then A decisions 37–54
in six preregistered nine-attempt runtimes. Every runtime used a fresh source
identity and epoch. The protected `EPISODE_LIMIT=12` was unchanged.

| Measure | Result |
|---|---:|
| Autonomous attempts | 54 |
| Real model calls | 486 / 486 |
| Joint next-state calls | 162 |
| G2 consequence calls | 162 |
| G3 consequence calls | 162 |
| Authorized executions | 50 |
| Abstentions | 4 |
| Framework rejections | 0 |
| Calibration executions | 0 |
| Tie-information probes | 2 |
| Retries or replacement calls | 0 |

Two joint next-state calls ended in `TimeoutError`, at decisions 7 and 26.
They produced two fail-closed `INVALID_MAP_COMPONENT` abstentions. They were not
retried. The other two abstentions were the first tie observation at decision
31 and probe-bound exhaustion at decision 54.

## Opened problem objects

Exactly one problem was created; there were no false or unnecessary problem
objects and no duplicate ID.

| Field | Value |
|---|---|
| Problem | `PR-0001` |
| Type | `UNRESOLVED_VALUE_TIE` |
| Opened | decision 32, after identical ties at 31 and 32 |
| State | 2 |
| Tied maximum actions | `ADVANCE`, `RETREAT` |
| Values at opening | `ADVANCE=+1`, `HOLD=0`, `RETREAT=+1` |
| Specialists at opening | G2 and G3 both predicted +1 for both tied actions |
| Evidence at opening | ADVANCE 3 observations; RETREAT 1 observation |
| Requested capability | `MORE_RELATION_EVIDENCE` |
| Failure observations | 4: decisions 31, 32, 38, and 54 |
| Route requests | 2 granted, then one bound-exhausted record |
| Probe receipts | 2 |
| Final status | `UNRESOLVED` |

## Route requests and probes

| Decision | Broker result | Route | Action | Pre-execution reason | Receipt consequence / next state | Status after |
|---:|---|---|---|---|---|---|
| 32 | `ROUTE_GRANTED` | `TIE_INFORMATION_PROBE` | `RETREAT` | fewer local observations: 1 vs ADVANCE 3 | +1 / 1 | `ROUTE_EXECUTED` |
| 38 | `ROUTE_GRANTED` | `TIE_INFORMATION_PROBE` | `RETREAT` | fewer local observations: 2 vs ADVANCE 3 | +1 / 1 | `ROUTE_EXECUTED` |
| 54 | `PROBE_BOUND_EXHAUSTED` | none | none | both permitted probes already consumed | no execution | `UNRESOLVED` |

Neither probe was marked resolved merely because it produced a receipt. On
each probe, `RETREAT` was selected from the tied set by the frozen information
priority. There was no specialist disagreement or unresolved contradiction in
that tied pair, so the lower local evidence count was decisive.

## Deadlock, A2 evidence, and routing

The R2 state-2 deadlock was escaped operationally: both state-2 tie probes had
authorized receipts whose realized next state was 1. The system therefore
continued to interact with reality instead of abstaining through the remainder
of the schedule.

There were 17 authorized receipts in A2, on decisions 37–53. Relation-local
HOLD routing at state 1 switched G2→G3 on decision 27 after a contradiction
probe in B. It switched G3→G2 on decision 50 after grounded A2 evidence. Full
switchback therefore occurred.

This does not mean the state-2 tie itself was solved. The same routed +1/+1
maximum recurred at decision 54, and the frozen bound required abstention. The
campaign shows a bounded route can restore reality interaction and enable
later relevant learning while still leaving the originating problem
unresolved.

## Runtime requests and restart proof

No protected-framework refusal occurred, so no live `NEW_RUNTIME` request was
emitted. All six rollovers followed the preregistered schedule. The tested
broker grants `NEW_RUNTIME` only at such a separately authorized rollover,
never changes `EPISODE_LIMIT`, and otherwise returns
`REQUEST_REQUIRES_EXTERNAL_APPROVAL`.

`PR-0001` opened in runtime 4, survived into runtime 5 with its first probe
budget consumed, issued its second probe there, and survived into runtime 6
with both probes consumed. At decision 54 it became `UNRESOLVED` without a
duplicate route or problem. Session, relation, confidence, and problem streams
all replayed exactly. Two independent report generations were byte-identical
with SHA-256
`4e73a7383c7557253602cbee690c5d0b7cdf9e126d8c97217a266b60249fb11e`.

## Verification and limitations

- 18/18 focused problem/route tests passed.
- 99/99 full Horus Python tests passed.
- 53/53 core regression steps passed.
- The final report passed exact replay and hidden-input checks for all 486
  requests.
- R2 evidence remained byte-identical and no earlier evidence was modified.

The broker has only three action routes and no learned detector or planner. It
cannot add a specialist, predictor, representation, or architecture without
external approval. The information probe gathers one chosen action's outcome;
when both specialists agree and that receipt does not alter their equal value
ranking, the original tie can recur. The two-probe limit prevents an endless
loop but leaves that case unresolved. The campaign tests one A→B→A trajectory
and does not establish broader task or model generality.
