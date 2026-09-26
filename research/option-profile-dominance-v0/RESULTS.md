# Horus v0.16 option-profile dominance results

## Result

The zero-inference retrospective evaluation returned
`RETREAT_PROFILE_DOMINATES`. No model call, training run, world execution, or
new receipt occurred.

`OPTION_PROFILE` is the complete finite multiset of depth-2 consequence
trajectories beneath one current action, sorted lexicographically from best to
worst. Trajectory identity and duplicates are preserved.

### ADVANCE profile

| Rank | Second action | Sequence |
|---:|---|---|
| 1 | RETREAT | `(+1,+1,+1)` |
| 2 | HOLD | `(+1,0,+1)` |
| 3 | ADVANCE | `(+1,-1,+1)` |

### RETREAT profile

| Rank | Second action | Sequence |
|---:|---|---|
| 1 | ADVANCE | `(+1,+1,+1)` |
| 2 | HOLD | `(+1,+1,+1)` |
| 3 | RETREAT | `(+1,0,+1)` |

The duplicate RETREAT trajectories at ranks 1 and 2 remain separate because
distinct second actions produced them.

## Rank comparison

| Rank | ADVANCE | RETREAT | Relation |
|---:|---|---|---|
| 1 | `(+1,+1,+1)` | `(+1,+1,+1)` | equal |
| 2 | `(+1,0,+1)` | `(+1,+1,+1)` | RETREAT greater |
| 3 | `(+1,-1,+1)` | `(+1,0,+1)` | RETREAT greater |

The profiles have equal cardinality. RETREAT is no worse at every rank and is
strictly better at ranks 2 and 3, so it dominates under the frozen partial
order. The representation implies RETREAT for PR-0002. It produces no scalar,
sum, average, weight, discount, or probability.

## Provenance and scope

Every `c0` and first continuation state remains authenticated receipt evidence.
Every `c1`, predicted second state, and `c2` remains a model forecast inherited
unchanged from v0.15. The reconstruction used no hidden world information.

The result does not establish that flexibility is universally valuable, that
more options are always better, or that any predicted trajectory will occur.
It establishes only that the complete retained RETREAT profile dominates the
complete retained ADVANCE profile under the registered consequence ordering.

## Problem Manager and integration gate

PR-0002 remains `REASSESSED`. Its option-profile evaluation allowance is
consumed 1/1. The manager appended:

1. `ALTERNATIVE_VALUE_REPRESENTATION_AUTHORIZED`, representation
   `OPTION_PROFILE_DOMINANCE`;
2. `REPRESENTATION_EVALUATED`, result `RETREAT_PROFILE_DOMINATES`, implied
   action RETREAT.

PR-0002 now requests `OPTION_PROFILE_BEHAVIORAL_INTEGRATION` with
`REQUEST_REQUIRES_EXTERNAL_APPROVAL`. Behavioral use is technically justified
for a separately authorized, PR-0002-scoped step because the rule, tests, and
eligibility gate are frozen. It is not authorized in v0.16. The global Explorer
objective remains unchanged and RETREAT was not executed.

PR-0003 remains unchanged with before/after digest
`52abbc28b599fafd771452499e9503738fedf212434062f4526317b7d4eaba8b`.
All v0.15 evidence remains byte-identical.

## Verification

- Model calls: 0.
- Behavioral executions: 0.
- New receipts: 0.
- 203/203 Horus tests passed.
- 53/53 core regression steps passed.
- All authenticated stores reopened and replayed.

## Remaining limitation

This is a retrospective representation result over forecasts collected in
v0.15. It has not shown that the implied action changes behavior safely, that
the predicted suffixes realize, or that option-profile dominance generalizes
beyond the narrowly registered PR-0002 eligibility conditions.
