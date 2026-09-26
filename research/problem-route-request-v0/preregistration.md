# Horus v0.8 problem/route request preregistration

## Identity and lineage

- Campaign: `HORUS_PROBLEM_ROUTE_REQUEST_V0`
- Parent completed evidence: `0155df09d7cad0b6df9fefd185d3da25b64389fd`
- Frozen implementation commit: `2c7375f5185d305647085ec9261bf620e4aa248b`
- Implementation tree: `4a4c49050d19c5598cb0b2b3f93ef0ecbea77c4b`
- Branch: `build/horus-v0.8-problem-route-request`

The campaign is prospective and fresh. It does not replay or extend R2. No
training, weight update, specialist creation, calibration execution, forced
action, retry, or replacement decision is permitted.

## Frozen question

Can persistent inability of the ordinary mechanical path to select among tied
maximum actions create one grounded, non-authoritative problem, request a
finite preauthorized route, obtain a real receipt, and use that receipt to
determine whether the original decision condition resolves?

## Frozen detector and lifecycle

A single tie creates no problem. An `UNRESOLVED_VALUE_TIE` is opened iff the
same state and same canonical tied-maximum action set occur on two consecutive
attempted decisions with no authorized execution between them. An identical
existing problem is updated; a duplicate ID is forbidden.

The finite statuses are `OPEN`, `ROUTE_REQUESTED`, `ROUTE_EXECUTED`,
`RESOLVED`, and `UNRESOLVED`. A probe receipt establishes only
`ROUTE_EXECUTED`. Resolution requires a later ordinary decision at the same
state to proceed. Evidence at another state cannot resolve the problem.

Exactly two tie-information probes are allowed per problem. If the same tie is
observed after both receipts, the problem becomes `UNRESOLVED` and the attempt
abstains. The campaign is not extended.

## Frozen broker

Registered action routes are exactly `NORMAL_EXPLOIT`, `RELATION_PROBE`, and
`TIE_INFORMATION_PROBE`. A tie-information probe considers only maximum-tied
actions and sorts them by:

1. specialist disagreement;
2. unresolved contradiction;
3. fewer authenticated local observations;
4. greater time since execution, treating never executed as most stale;
5. canonical `ADVANCE`, `HOLD`, `RETREAT` order.

The generic requests are `MORE_RELATION_EVIDENCE`, `ALTERNATIVE_PREDICTOR`,
`DIFFERENT_REPRESENTATION`, `NEW_SPECIALIST`, and `NEW_RUNTIME`. Only
`MORE_RELATION_EVIDENCE` and a separately preregistered `NEW_RUNTIME` rollover
are mechanically grantable. All others produce
`REQUEST_REQUIRES_EXTERNAL_APPROVAL`. A request cannot execute, publish, alter
Memory/routing, train, or change a protected bound.

## Frozen campaign and calls

There are exactly 54 autonomous attempts and nine model calls per attempt:
three joint next-state calls, three G2 consequence calls, and three G3
consequence calls. Expected and maximum campaign calls are 486. There are no
retries or extra behavioral calls.

| Segment | Attempts | Regime | Resume | Prior runtimes |
|---|---:|---|---|---:|
| `V08_A1_1` | 1–9 | A | no | 0 |
| `V08_A1_2` | 10–18 | A | yes | 1 |
| `V08_B1` | 19–27 | B transition | yes | 2 |
| `V08_B2` | 28–36 | B | yes | 3 |
| `V08_A2_1` | 37–45 | A transition | yes | 4 |
| `V08_A2_2` | 46–54 | A | yes | 5 |

Each runtime has nine attempts and at most nine executions. Rollover is driven
only by this table. `EPISODE_LIMIT=12` is unchanged.

## Frozen interpretation

The primary milestone is established if at least one persistent identical tie
opens a problem, creates a durable route request, the broker grants only the
registered tie-information route, and the selected tied action produces an
authorized original receipt that updates Memory, relation routing, confidence,
and the problem evidence. Whether that receipt resolves the tie is reported
separately.

Full escape from the R2 state-2 deadlock means a state-2 tie-information probe
has an authorized receipt whose realized next state is not state 2. A2
grounding is the count of authorized receipts on decisions 37–54. A G3→G2
switchback is desirable and descriptive, not required for the primary
milestone.

Every opened problem, request, grant/refusal, selected action and priority,
receipt reference, status transition, false/unnecessary creation, abstention,
and framework rejection will be reported. Negative results remain results and
do not authorize tuning or extension.

## Frozen hashes and artifacts

- `problem_routing.py`: `016e73eb66044198a379856b1c1c09676580a94cc516b36d8983af2f58dc3e97`
- Problem/route policy: `08dfaf20e2202383c4d596c662e7ae521a70771b8c9e681cd471bc61ae7ee109`
- Grounded exploration integration: `88f744965f661b0a2c0bf610ff82e145a692da98d3ec58aea49c2ae07327af34`
- One-shot runner: `d1f06a9e2550176a9124bbe3f4e7ec82dca086f0925f2a29ab4eaa7e42965d5a`
- Unchanged v0.7 policy: `f6f963403a6ffaa827069288df49340035a4f9a7556d7111de9ba426382db7b3`
- Joint system instruction: `805542ebed5d2fa09b9b36f4895bdbd917b5d2af58db56d744478887a824b3e7`
- Consequence system instruction: `9fa97c24f33f7e25497bce9bb23a70cea52f91f6e02a3a01bd8e2d571ea37df8`
- G2 artifact: `effb5eebef0649818c0697f1dfbadc73bc9e047eb1eaf6e3d5f6c63e0a35d39a`
- G3 artifact: `edb9f6ff90dff7af75ece168825f04839ab720dc8a79ce166225a5ffcc1efb24`

## Stop rule

Run this campaign once. A model, code, storage, schedule, or service failure is
preserved and stops the campaign. Do not patch and resume, retry failed calls,
replace decisions, add calibration, extend the schedule, train, or start a
follow-up experiment without new explicit authorization.
