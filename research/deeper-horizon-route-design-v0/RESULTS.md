# Horus v0.15 bounded depth-2 trajectory results

## Zero-inference diagnosis

V0.14 preserved different routed structures for the two authenticated
continuation states:

- current ADVANCE → state 3 → `[-1,0,+1]`;
- current RETREAT → state 1 → `[+1,+1,0]`.

Reducing each vector to its maximum erased that difference because both maxima
were `+1`. The diagnosis establishes a real max-compression bottleneck but does
not make either structure preferable. The registered depth-2 route passed its
design gate because it retained every second action and added a consequence
opportunity conditional on that action's predicted next state.

## Route result

The single authorized route completed with `STILL_TIED_AT_DEPTH2`. The public
result marker is `DEPTH2_TRAJECTORY_INSUFFICIENT`.

| Current action | Grounded state | Second action | `c1` routed | Predicted state | `c2` maximum | Sequence |
|---|---:|---|---:|---:|---:|---|
| ADVANCE | 3 | ADVANCE | -1 | 0 | +1 | `(+1,-1,+1)` |
| ADVANCE | 3 | HOLD | 0 | 3 | +1 | `(+1,0,+1)` |
| ADVANCE | 3 | RETREAT | +1 | 2 | +1 | `(+1,+1,+1)` |
| RETREAT | 1 | ADVANCE | +1 | 2 | +1 | `(+1,+1,+1)` |
| RETREAT | 1 | HOLD | +1 | 1 | +1 | `(+1,+1,+1)` |
| RETREAT | 1 | RETREAT | 0 | 0 | +1 | `(+1,0,+1)` |

The best ADVANCE trajectory is `(+1,+1,+1)` through second action RETREAT.
The best RETREAT trajectory is also `(+1,+1,+1)`, attained through second
actions ADVANCE and HOLD. The route therefore made no arbitrary choice.

## Provenance

Every trajectory retains the same provenance:

| Element | Provenance |
|---|---|
| `c0` | authenticated receipt |
| first continuation state | authenticated receipt |
| `c1` | routed model forecast |
| second next state | joint model forecast |
| `c2` | routed model forecast |

Predicted states were 0, 1, 2, and 3. No predicted state was inserted into
verified history or represented as a receipt. The route made no world execution,
so none of its predicted trajectory suffixes became authenticated outcomes.

## Terminal routed consequences

| Predicted state | ADVANCE | HOLD | RETREAT | Maximum |
|---:|---:|---:|---:|---:|
| 0 | +1 | 0 | -1 | +1 |
| 1 | +1 | +1 | 0 | +1 |
| 2 | +1 | 0 | +1 | +1 |
| 3 | -1 | 0 | +1 | +1 |

G2 was the existing relation-local selection for every evaluated relation. G3
remained independently evaluated; its outputs are preserved in `results.json`.

## Accounting and integrity

| Measure | Result |
|---|---:|
| Second-layer calls | 18 |
| New terminal calls | 12 |
| Byte-identical terminal reuses | 12 |
| Total calls | 30 / 30 |
| Maximum depth | 2 |
| Recursive calls | 0 |
| Behavioral executions | 0 |
| Training runs | 0 |
| Retries | 0 |

All 18 second-layer intents were durable before response sequence 2323. All 12
new terminal intents were durable before terminal response sequence 2371. The
12 reused terminal results matched complete canonical request bytes.

PR-0002 remains `REASSESSED`; its depth-2 budget is consumed 1/1. It now
requests `ALTERNATIVE_VALUE_REPRESENTATION` with
`REQUEST_REQUIRES_EXTERNAL_APPROVAL`. The canonical manager stream records
`STILL_TIED_AT_DEPTH2`; this package records the corresponding
`DEPTH2_TRAJECTORY_INSUFFICIENT` marker without rewriting that stream. No depth
3 capability or new objective was implemented.

PR-0003 remains unchanged with before/after digest
`52abbc28b599fafd771452499e9503738fedf212434062f4526317b7d4eaba8b`.
V0.14 evidence remains byte-identical.

After the result, 188/188 Horus tests and 53/53 core regression steps passed.
All authenticated session, routing, Explorer-confidence, and Problem Manager
stores reopened and replayed.

## Limitation

Finite depth-2 trajectory preservation still produced equal best consequence
sequences. This supports investigating representation under explicit external
authorization rather than automatically extending horizon depth. It does not
show that alternative value features are valid objectives, that either action
is better, or that the predicted trajectories describe realized reality.
