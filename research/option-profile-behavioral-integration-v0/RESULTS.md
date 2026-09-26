# Horus v0.17 option-profile behavioral integration result

## Result

`INTEGRATION_EXECUTED_CONSISTENT`

The frozen v0.16 evidence reconstructed exactly to `RETREAT_PROFILE_DOMINATES`. Under the one-use PR-0002 authority, ordinary immediate value was again tied exactly between `ADVANCE` and `RETREAT`. The problem manager froze `RETREAT` before reality, and the ordinary protected boundary executed only `RETREAT`.

## Commitments

- Behavioral authorization SHA-256: `b112a70071d510a3f24aa44fdc093936312894f42c433c2e785e8db092b533b5`
- Frozen v0.16 result SHA-256: `54fc0a6f95195329d0a033b272b2305175fcdd224581705f3a605e0dcb2d6214`
- Frozen decision record SHA-256: `0e00d1d2050cafd3f82ffc4fc787ab4c7c3341f625f42c83e14da531ff64edc8`
- Selected action: `RETREAT`
- Fresh decisions: 2 / 2 maximum
- Model calls: 18 / 18 maximum
- Retries: 0
- Training runs: 0

## Reconstructed profiles

| Rank | ADVANCE profile | RETREAT profile | Relation |
|---:|---|---|---|
| 1 | `[1, 1, 1]` | `[1, 1, 1]` | equal |
| 2 | `[1, 0, 1]` | `[1, 1, 1]` | RETREAT greater |
| 3 | `[1, -1, 1]` | `[1, 0, 1]` | RETREAT greater |

The v0.16 partial-order rule therefore selected `RETREAT`; no new objective was computed from live outputs.

## Authenticated reality

The new original receipt has identity:

```text
(HORUS:a67e675004193a13c31485bad53fbb86:runtime:12:ff1b1b2419b3ee4c, 1, 2012, 1)
```

It records state 2, action `RETREAT`, consequence `+1`, and next state 1. Both fields exactly match the retained grounded first-step relation. This observation does not establish what `ADVANCE` would have produced; `ADVANCE` was not executed.

## Ordinary follow-up

The one permitted follow-up decision ran at state 1 under the ordinary grounded Explorer. It abstained with `INVALID_MAP_COMPONENT`: the joint next-state call for `RETREAT` timed out. No retry or campaign extension occurred, and no follow-up receipt was created. The timeout is preserved as `PR-0004`, an open `EXTERNAL_SERVICE_PROBLEM`; it does not change the successful option-profile integration classification.

Because the follow-up did not execute, `OBSERVED_SUFFIX_PREFIX_CHECK` is not applicable. No suffix trajectory is claimed as validated.

## Problem state and verification

PR-0002 remains `REASSESSED` with capability assessment `CURRENT_OBJECTIVE_CANNOT_DISTINGUISH`; it is not globally marked resolved. Its one-use behavioral allowance is consumed. PR-0003 is byte-identical to its pre-run state.

Authenticated replay passed for the session, routing, confidence, and problem-manager stores. The frozen decision precedes the receipt, the only new executed action is `RETREAT`, and the v0.16 evidence remains byte-identical. Both before and after the run, 218/218 Horus tests and all 53 core regression steps passed.

## Limits

This is one scoped execution. The dominance remains forecast-derived, no same-decision `ADVANCE` counterfactual exists, and the ordinary-continuation observation ended in an operational abstention. The result does not justify globalizing `OPTION_PROFILE_DOMINANCE`, training on it, adding depth, or claiming complete suffix validation.
