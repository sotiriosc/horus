# V0.16 option-profile dominance preregistration

This zero-inference representation evaluation follows completed v0.15 commit
`2bd59598768ffda008583e79d6d0cd86c13b2927` and implementation checkpoint
`53ad318c2e87860b6b1504584461cdeb0990211d`.

## Frozen question

When the best depth-2 trajectory ties, can the complete ranked multisets of
available depth-2 consequence trajectories be partially ordered without a
scalar tradeoff?

The only source is committed v0.15 `results.json`, SHA-256
`2fc4e2ddc489aa1c2d8bc394a041b182215f080df486afd637f827dee5759341`.
V0.15 itself remains `STILL_TIED_AT_DEPTH2` and is not reinterpreted.

## OPTION_PROFILE

For each current action, require exactly one trajectory for each legal second
action ADVANCE, HOLD, and RETREAT. Each trajectory must contain exactly three
consequences in `{-1,0,+1}` and the frozen provenance:

```
c0     AUTHENTICATED_RECEIPT
state1 AUTHENTICATED_RECEIPT
c1     MODEL_FORECAST
state2 MODEL_FORECAST
c2     MODEL_FORECAST
```

Retain the complete finite multiset and second-action identities. Preserve
equal sequences as separate entries. Sort from best to worst by the existing
lexicographic consequence order. Canonical action order resolves display order
between equal sequences but contributes no preference or value.

## OPTION_PROFILE_DOMINATES

For equal-cardinality profiles X and Y, X dominates Y exactly when every ranked
X trajectory is lexicographically greater than or equal to the corresponding Y
trajectory and at least one rank is strictly greater.

Possible outcomes are `ADVANCE_PROFILE_DOMINATES`,
`RETREAT_PROFILE_DOMINATES`, `PROFILES_EQUAL`, and `PROFILES_INCOMPARABLE`.
Equal and crossing profiles select no action. The comparison returns no scalar.

No sum, average, weight, discount, probability, novelty, uncertainty, action
diversity, state identity, or hidden world information is permitted.

## Authorization and scope

Authorization SHA-256
`77c09cca9ba8d9e5eb47964cccbf3acd307c415662f1dfab4b8ed0a423e83738`
grants one `OPTION_PROFILE_DOMINANCE` evaluation for PR-0002. Eligibility
requires:

1. PR-0002 remains applicable to state 2 / `[ADVANCE,RETREAT]`;
2. assessment remains `CURRENT_OBJECTIVE_CANNOT_DISTINGUISH`;
3. request is `ALTERNATIVE_VALUE_REPRESENTATION`;
4. v0.15 supplies three complete trajectories per current action;
5. immediate consequences and best depth-2 trajectories remain tied;
6. this representation has not previously been evaluated.

Model calls, training runs, behavioral executions, depth 3, global Explorer
changes, and scalar objectives are all fixed at zero.

## Prospective integration gate

If one profile uniquely dominates, v0.16 may record the implied current action
and request `OPTION_PROFILE_BEHAVIORAL_INTEGRATION` with
external-approval-only status. It may not execute that action or install the
representation globally. A later behavioral step would require separate
explicit authorization and must remain scoped to PR-0002 or an equivalent
problem satisfying all registered eligibility conditions.

If profiles are equal or incomparable, PR-0002 remains unresolved and no
arbitrary scalar tradeoff is introduced.

## Frozen implementation

- `horus/problem_manager.py`:
  `83dc94cb295717ae9836fc331816431200e3f338a0135d089f2ff3ce8d87024e`
- `horus/option_profile.py`:
  `d2c6e3f9675afe020e168eea0af5050b2baca7d712d3f1337b9a839a6be02f90`
- `horus/option_profile_cli.py`:
  `0dc5ddc5561caf45a648a4b70ea1a24a4d36ae6c30622b46b02a40314ba8a7e0`

The deterministic result is preserved whether it dominates, ties, is
incomparable, or fails source validation.
