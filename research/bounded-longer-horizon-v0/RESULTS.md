# Horus v0.14 bounded longer-horizon results

## Outcome

The authorized `ONE_STEP_CONTINUATION_VALUE` route completed once and returned
`STILL_TIED_AT_ONE_STEP`. The public result marker is
`ONE_STEP_CONTINUATION_INSUFFICIENT`.

PR-0002 supplied two retained authenticated transitions:

| Current action | Grounded immediate | Grounded continuation |
|---|---:|---:|
| ADVANCE | +1 | state 3 |
| RETREAT | +1 | state 1 |

The route made 12 consequence-only calls. All 12 request intents were durable
before the first response. No downstream prompt was given a predicted next
state, all outputs parsed, and the route used the existing exact-relation
selection independently for each continuation-state/action relation.

## Downstream forecasts

| Continuation | Action | G2 | G3 | Routed specialist | Routed consequence |
|---:|---|---:|---:|---|---:|
| 3 | ADVANCE | -1 | -1 | G2 | -1 |
| 3 | HOLD | 0 | 0 | G2 | 0 |
| 3 | RETREAT | +1 | +1 | G2 | +1 |
| 1 | ADVANCE | +1 | -1 | G2 | +1 |
| 1 | HOLD | +1 | -1 | G2 | +1 |
| 1 | RETREAT | 0 | 0 | G2 | 0 |

The maximum routed forecast is `+1` at both continuation states. The frozen
lexicographic comparison was therefore:

```
ADVANCE = (+1, +1)
RETREAT = (+1, +1)
```

The added layer did not distinguish the actions. Horus selected no action,
opened no protected runtime, issued none of the conditional nine integration
calls, and received no new receipt. This is a valid negative result.

## Problem state

PR-0002 remains `REASSESSED` with assessment
`CURRENT_OBJECTIVE_CANNOT_DISTINGUISH`. Its one-step budget is consumed 1/1.
It now requests `DEEPER_HORIZON_VALUE` with
`REQUEST_REQUIRES_EXTERNAL_APPROVAL`; v0.14 does not grant or implement that
request. The manager history records the canonical result
`STILL_TIED_AT_ONE_STEP`, and this evidence package records the requested
interpretive marker `ONE_STEP_CONTINUATION_INSUFFICIENT` without rewriting the
authenticated manager stream.

PR-0003 is unchanged. Its before/after canonical digest is
`52abbc28b599fafd771452499e9503738fedf212434062f4526317b7d4eaba8b`.

## Accounting

| Measure | Result |
|---|---:|
| Downstream consequence calls | 12 / 12 |
| Conditional integration calls | 0 / 9 |
| Total model calls | 12 / 21 |
| Behavioral executions | 0 / 1 |
| Added consequence layers | 1 |
| Recursive calls | 0 |
| Training runs | 0 |
| Retries | 0 |

The session remains at 85 attempted decisions, 54 authenticated executions,
state 2, runtime 11, and epoch 2011. The result added 36 call envelopes, one
compact evaluation record, and two manager events. It added no execution,
routing, or Explorer-confidence record.

## Serializer repair and verification

Before live inference, the v0.13 `KeyError: pre_state` was reproduced with a
deterministic authorized-row fixture. The narrow repair normalizes only the
public result view: it reads `pre_state`, falls back to the authorized runtime
row's `state`, and requires an integer. No behavioral authority was added,
v0.13 was not rerun, and every v0.13 evidence file remains byte-identical.

After the v0.14 result:

- all authenticated stores reopened and replayed;
- the manager bound to the unchanged session decision/receipt counts;
- all 12 intents precede response sequence 2281;
- PR-0003 and v0.13 public evidence remain unchanged;
- 173/173 Horus Python tests passed;
- 53/53 core regression steps passed.

## Narrow interpretation and limitation

At the tested endpoint, immediate value tied and one additional predicted
consequence layer also tied. The experiment therefore establishes that this
particular bounded route was insufficient. It does not establish general
planning, long-term optimality, a causal world model, or the usefulness of a
deeper horizon. The downstream values remain forecasts rather than
authenticated outcomes.
