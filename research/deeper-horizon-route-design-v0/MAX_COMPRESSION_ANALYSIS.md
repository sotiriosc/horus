# V0.15 zero-inference max-compression analysis

This analysis uses only the committed v0.14 result and existing route code. It
made no model calls and used no simulator transition law.

## Retained structure

| Current action | Immediate | Grounded continuation | Routed downstream vector | Maximum |
|---|---:|---:|---|---:|
| ADVANCE | +1 | state 3 | `[-1,0,+1]` for `[ADVANCE,HOLD,RETREAT]` | +1 |
| RETREAT | +1 | state 1 | `[+1,+1,0]` for `[ADVANCE,HOLD,RETREAT]` | +1 |

The v0.14 representation retained the authenticated current action, immediate
consequence, first continuation state, both G2/G3 forecasts, relation-local
specialist selection, and the full routed vector in its evidence. Its decision
reduction retained only `(immediate, max(routed vector))`. This discarded:

- which second actions attained the maximum;
- the lower-valued second alternatives;
- multiplicity of equal-valued second alternatives;
- the existing joint Map's predicted next state for each second action;
- any consequence opportunity conditional on that predicted state.

The vectors are structurally different but both reduce to `max=+1`. This
confirms max compression is a real information bottleneck. It does not license
a preference for either vector, the number of positive actions, novelty,
variance, entropy, uncertainty, or any state identity.

## Route-design gate

`BOUNDED_DEPTH2_TRAJECTORY_VALUE` does not algebraically reduce to the v0.14
maximum. It retains every second action and adds that action's independently
predicted next state plus the best routed consequence at that predicted state.
The candidate sequences `(c0,c1,c2)` can differ even when `max(c1)` is equal.
The route therefore has the possibility of adding information and passes the
prospective live gate.

This only establishes structural non-equivalence. Whether the actual frozen
forecasts distinguish PR-0002 remains an empirical question.
