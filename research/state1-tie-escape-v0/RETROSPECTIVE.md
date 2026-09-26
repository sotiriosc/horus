# Horus v0.12 state-1 tie retrospective

## Decision

The proposed `DEADLOCK_INFORMATION_PROBE` was not implemented. The required
diagnostic condition was false: the ordinary probe budget was unavailable, but
it was not the only blocker. The active v0.11 runtime had no mechanism that
could open an `UNRESOLVED_VALUE_TIE` problem for state 1 and candidate actions
`[ADVANCE, HOLD]`.

This invokes the milestone's mandatory stop rule. There was no prospective
live run, no model call, no world execution, no policy change, and no training.

## Decisions 64--83

The retained authenticated decision stream contains twenty frozen decisions,
64 through 83. Every one has the same relevant values:

| Field | Retained value |
|---|---|
| State | `1` |
| Routed values | `ADVANCE=1`, `HOLD=1`, `RETREAT=0` |
| Tied maximum | `[ADVANCE, HOLD]` |
| G2 predictions | `ADVANCE=1`, `HOLD=1`, `RETREAT=0` |
| G3 predictions | `ADVANCE=-1`, `HOLD=-1`, `RETREAT=0` |
| Prediction validity | all valid |
| Explorer result | `EXPLOIT_TIED_MAXIMUM`, abstain, no action |
| Ordinary probe budget | unavailable |
| Qualifying probe blocked by budget | true |
| Attached problem | none |

The local exact-relation evidence also remained unchanged because no execution
occurred:

| Action | Authenticated observations | Staleness | Unresolved contradiction | Qualifying ordinary probe reason |
|---|---:|---:|---|---|
| `ADVANCE` | 4 | 3 | none | `PROBE_DISAGREEMENT` |
| `HOLD` | 12 | 4 | none | none |
| `RETREAT` | 8 | 8 | none | `PROBE_STALE` |

The source decision stream is
`research/bounded-evidence-coverage-v0/new-exploration-decisions.jsonl`, SHA-256
`2d3696cbb4f2c6007e571b01b762399cec3bd649309677b79c24c06e209bd32f`.
The exact machine-readable extraction is in `diagnosis.json`.

## Ordinary probe budget path

`GroundedExplorer.derive` computes `next_authorized` as the authenticated
authorized-decision count plus one, then makes the ordinary budget available
only when the distance from `last_probe_authorized_decision` meets the frozen
minimum of three (`horus/grounded_exploration.py`, lines 180--185).

At the v0.11 endpoint and throughout decisions 64--83:

- `authorized_decisions = 53`;
- `last_probe_authorized_decision = 53`;
- prospective authorized index = `54`;
- distance = `1`, below the required `3`.

`ADVANCE` supplied a qualifying ordinary candidate through specialist
disagreement, so the decision correctly retained
`qualifying_probe_blocked_by_budget=true`. An abstention advances
`attempted_decisions` but returns before advancing `authorized_decisions`
(`horus/grounded_exploration.py`, lines 343--352). The ordinary budget therefore
cannot age while this loop only abstains.

## Why no problem opened

The active v0.11 runtime is `CoverageExtensionRuntime`, which inherits
`CapabilityGapRuntime`. `CapabilityGapRuntime` wraps `GroundedExplorer` only
with `CapabilityGapStore` (`horus/capability_gap.py`, lines 506--523). It does
not construct or invoke the v0.8 `ProblemRouteRuntime` or `ProblemRouteStore`.

The active capability-gap store already owns `PR-0002`, a state-2 problem for
`[ADVANCE, RETREAT]`. Its frozen `prepare` rule can create a problem only when
there is no current problem and the state and candidates exactly match its
retained source problem. It can evolve an existing problem only when the
current state equals that problem's state (`horus/capability_gap.py`, lines
350--356). For a state-1 `[ADVANCE, HOLD]` tie:

- `current_problem is None` is false;
- `pre_state == current_problem.state` is false;
- the source problem's state/candidate identity is also state 2 /
  `[ADVANCE, RETREAT]`.

Consequently the final decision keeps `problem_id=null`, and no state-1 problem
can be opened or evolved on this path.

The older v0.8 `ProblemRouteStore` does contain a rule that remembers one tie
and opens a problem on the next consecutive identical tie without an
intervening authorized execution (`horus/problem_routing.py`, lines 363--442).
That store is not composed into the active runtime. Its retained state also
ends at attempt 54 while the v0.11 session ends at attempt 83, so it cannot be
silently rebound without a separately specified state migration and component
composition rule.

## Narrowest defensible bottleneck

The bottleneck is the active problem-lifecycle composition: persistent new ties
outside the single inherited state-2 capability problem have no active owner.
Ordinary budget exhaustion explains why the ordinary `PROBE` route cannot act,
but does not by itself explain why condition 6 of the proposed deadlock route
cannot become true.

Adding only a broker route would therefore leave its required open-problem
precondition unreachable. A later milestone must first choose and preregister
how concurrent or successor problems are represented, authenticated, replayed,
and composed with the existing capability-gap problem. That architectural
choice is outside this experiment.

## Preserved endpoint

The existing problem remains `PR-0002`: state 2, candidates
`[ADVANCE, RETREAT]`, assessment `MORE_EVIDENCE_REQUIRED`, localization
`EVIDENCE_COVERAGE`, requested capability `MORE_RELATION_EVIDENCE`, status
`ROUTE_EXECUTED`, two authenticated problem probes, and no terminal classifier
result. No state-1 problem exists.
