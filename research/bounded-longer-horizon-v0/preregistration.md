# V0.14 bounded longer-horizon preregistration

This preregistration follows the completed v0.13 evidence commit
`0eda60382b3d9cdaef0896e0648ae2a6bc25cb9e` and the v0.14 implementation
checkpoint `88608e38b2ccf82bbaa1ab5662d0490649858c1a`.

## Frozen question

When PR-0002's two actions have equal authenticated immediate consequence but
different authenticated realized continuation states, can exactly one added
layer of routed consequence forecasts distinguish them?

## Source state and grounded transitions

- Session attempt count: 85.
- Authorized execution count: 54.
- Current state: 2.
- Applicable problem: PR-0002 at state 2 / `[ADVANCE,RETREAT]`.
- Assessment: `CURRENT_OBJECTIVE_CANNOT_DISTINGUISH`.
- Historical request: `LONGER_HORIZON_VALUE`, external approval required.
- ADVANCE: consequence `+1`, realized state `3`, receipt identity
  `HORUS:a67e675004193a13c31485bad53fbb86:runtime:7:fbd6aa709480146c / 1 / 2007 / 1`.
- RETREAT: consequence `+1`, realized state `1`, receipt identity
  `HORUS:a67e675004193a13c31485bad53fbb86:runtime:8:9e523c741279b221 / 1 / 2008 / 1`.

Both receipts must remain authenticated and problem-specific. A predicted next
state cannot replace either realized continuation state. PR-0003 must remain
byte-for-byte equal as a manager object throughout the v0.14 route.

## Authorized route

The authorization document SHA-256 is
`06d673d0ff2d9f6601d1db057665b3c2072d4903dd1bc5ab72cb9be74f53ec0c`.
It grants `ONE_STEP_CONTINUATION_VALUE` once for PR-0002 only.

For each current action `a`:

```
primary(a) = authenticated immediate consequence
state(a) = authenticated realized continuation state
secondary(a) = max routed consequence forecast over ADVANCE, HOLD, RETREAT at state(a)
pair(a) = (primary(a), secondary(a))
```

Pairs are compared lexicographically. Primary value dominates. Secondary value
is consulted only because the primaries are tied. Values are not added or
discounted.

## Frozen downstream evaluation

Exactly 12 consequence-only calls are permitted: two continuation states,
three legal actions, and independent G2/G3 forecasts. Every request intent must
be durably appended before the first response. The existing exact-relation
router chooses the routed specialist independently for each `(state, action)`.

No downstream request contains a predicted next state, hidden simulator law,
regime label, future receipt, or counterfactual outcome. No joint-output call is
used for the downstream layer. The maximum added horizon is one consequence
layer; recursive calls, search, planning, dynamic programming, simulation, and
training are prohibited.

## Outcomes and stop rules

1. `ONE_STEP_DISTINGUISHES`: if secondary values differ, freeze the unique
   lexicographic selection and execute that current action once through the
   ordinary protected boundary. The existing integration path requires one
   nine-call current-decision batch (three joint, three G2, three G3 calls).
   Stop after the resulting original receipt.
2. `STILL_TIED_AT_ONE_STEP`: select and execute nothing. Append
   `ONE_STEP_CONTINUATION_INSUFFICIENT` in the result interpretation, request
   `DEEPER_HORIZON_VALUE` with external-approval-only status, and stop without
   granting or implementing it.
3. `INVALID_DOWNSTREAM_PREDICTION`: localize an external service problem and
   fail closed without execution.
4. `MISSING_GROUNDED_TRANSITION`: do not authorize the route; retain the need
   for relation evidence and stop without using a prediction as fact.
5. Any new operational/runtime defect: preserve evidence and stop. No patch and
   rerun is authorized.

## Bounds

- Consequence-only downstream calls: exactly 12.
- Conditional ordinary integration calls: 9 only after a distinguishing result.
- Absolute model-call ceiling: 21.
- Behavioral executions: at most 1.
- Additional consequence layers: exactly 1.
- Route uses for PR-0002: at most 1.
- Training runs: 0.
- Retries, extensions, deeper-horizon calls, and follow-on experiments: 0.

## Frozen implementation

- `horus/problem_manager.py`:
  `7c627f1716649a35937c4096a7d2a425f3270f6b4257cb2d704172f689f65927`
- `horus/one_step_value.py`:
  `fb730785835dea2f2636eb6e926b030fbb0f800b3ca1690a017271907897bc3f`
- `horus/one_step_value_cli.py`:
  `f35ef693da09ded43a7bea4d9688156a2f69e3d45a6b5ce44eeccadb90356190`
- `horus/grounded_exploration.py`:
  `88f744965f661b0a2c0bf610ff82e145a692da98d3ec58aea49c2ae07327af34`
- `horus/relation_routing.py`:
  `4845d0fdeb34ac3101fca915f1cd5979048b4b1d80c89a91c913e8fc3962d396`
- `horus/live.py`:
  `7a9d78692e2c07b1d3fc9ee24a0c079fe6b4b4cd247485f5bdf1024027faf92e`

The result is preserved whether the route distinguishes, remains tied, or
fails operationally.
