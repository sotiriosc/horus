# V0.13 deadlock-information route preregistration

This preregistration follows the completed zero-inference checkpoint commit
`95a0639181e15e3478c89e2ee58a0cb349e1ed79`. That checkpoint mechanically
created PR-0003 from retained decisions 64--83 while the route was disabled.

## Frozen question

Can the independently discovered state-1 problem request one bounded
information interaction, after which the canonical manager exposes the problem
applicable to the resulting context?

No destination or outcome is required. Reaching state 2 is not an optimization
target.

## Source state

- Session attempt count: 83.
- Authorized execution count: 53.
- Current state: 1.
- Applicable problem: PR-0003.
- Exact scope: state 1 / `[ADVANCE,HOLD]`.
- PR-0003 state: `OPEN`.
- PR-0003 deadlock allowance before run: 0 granted, 0 executed, limit 1.
- Ordinary probe state: unavailable at the retained endpoint.
- PR-0002 remains separate at state 2 / `[ADVANCE,RETREAT]`.

## Eligibility

`DEADLOCK_INFORMATION_PROBE` may be granted only when all are true:

1. an active `UNRESOLVED_VALUE_TIE` problem applies by exact state and tied set;
2. the ordinary Explorer reports `EXPLOIT_TIED_MAXIMUM` and abstains;
3. the ordinary probe budget is unavailable;
4. every required prediction is valid;
5. the applicable problem's one-probe allowance has not been granted.

The retrospective detector remains two consecutive identical valid tied
attempts with no intervening authorized execution. Retrospective replay itself
does not grant a route.

## Deterministic selection

Selection is restricted to the tied maximum set and ordered by:

1. unprobed for this problem;
2. specialist disagreement;
3. unresolved contradiction;
4. fewer authenticated exact-relation observations;
5. greater staleness;
6. canonical action order.

The selection input has no simulator transition table, realized outcome,
future consequence, desired destination, or hidden regime.

## Bound and stop rule

- Maximum fresh decisions: 8.
- Calls per decision: 9.
- Maximum model calls: 72.
- Runtime schedule: one fresh runtime with at most 8 decisions, below the
  protected `EPISODE_LIMIT=12`.
- No retries, repair calls, training, model changes, objective changes, or
  schedule extension.

Stop after the first applicable condition:

1. the route executes and one later ordinary decision does not reproduce the
   same state-1 deadlock;
2. the identical state-1 deadlock returns after its allowance is exhausted;
3. an operational failure prevents continuation;
4. the route never becomes eligible by decision 8.

## Frozen implementation commitments

- `horus/problem_manager.py`:
  `10e282448e081fb6d6bbf30a27b6d10ed73224c9f89fa5f81e2f90892143126a`
- `horus/problem_ownership_policy.json`:
  `1fcf7d5d453ee5a91ced9401db0a78a881be30dd641d9e5a6db0a9b994a06157`
- `horus/problem_ownership_run.py`:
  `301e2bef5f2c2b8f5e965501decd99db90801614694cebdba609b1174d3b6717`
- `horus/grounded_exploration.py`:
  `88f744965f661b0a2c0bf610ff82e145a692da98d3ec58aea49c2ae07327af34`
- `horus/relation_routing.py`:
  `4845d0fdeb34ac3101fca915f1cd5979048b4b1d80c89a91c913e8fc3962d396`
- `horus/live.py`:
  `7a9d78692e2c07b1d3fc9ee24a0c079fe6b4b4cd247485f5bdf1024027faf92e`

The result is preserved whether the route executes, fails operationally,
returns to the same deadlock, or never becomes eligible.
