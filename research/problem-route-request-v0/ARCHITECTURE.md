# Horus v0.8 bounded problem/route request

Horus v0.8 adds a finite, inspectable path for a local decision failure. It
does not train a model, change G2 or G3, weaken value comparison, change the
simulator, or grant a problem object authority.

## Boundary

The unchanged v0.7 explorer first derives its ordinary decision from
authenticated relation evidence. The v0.8 detector can observe that frozen
decision, its forecasts, relation-confidence metadata, prior authenticated
evidence references, and completed receipts. It cannot observe the external
regime, simulator law, future result, or an unexecuted counterfactual.

One tied maximum remains an ordinary abstention. The second consecutive
attempt at the same state with the same tied-maximum action set, with no
authorized execution between the attempts, opens one `UNRESOLVED_VALUE_TIE`.
Further identical observations update that problem; they do not create another
problem ID.

## Non-authoritative problem object

The authenticated append-only stream records problem identity, component,
type, state, tied candidates, forecasts, routing state, relation confidence,
evidence references, failure count, last successful execution count,
requested capability, status, route count, probe count, and receipt
references. Explicit false-valued fields bind the fact that the object cannot
execute, publish Memory, select a specialist, rewrite a prediction, train,
change a protected bound, alter the simulator, or create a receipt.

The finite statuses are `OPEN`, `ROUTE_REQUESTED`, `ROUTE_EXECUTED`,
`RESOLVED`, and `UNRESOLVED`. A receipt changes a tie problem to
`ROUTE_EXECUTED`; it does not by itself establish resolution. Resolution
requires a later ordinary decision at that same state to proceed. Evidence at
another state cannot resolve it.

## Mechanical broker

The registered action routes are exactly:

- `NORMAL_EXPLOIT`
- `RELATION_PROBE`
- `TIE_INFORMATION_PROBE`

The generic capability interface accepts `MORE_RELATION_EVIDENCE`,
`ALTERNATIVE_PREDICTOR`, `DIFFERENT_REPRESENTATION`, `NEW_SPECIALIST`, and
`NEW_RUNTIME`. In v0.8, `MORE_RELATION_EVIDENCE` can grant the registered tie
probe. `NEW_RUNTIME` can be satisfied only by a separately preregistered
schedule boundary. The other capabilities require external approval.

For an open tie problem, the broker considers only tied maximum actions and
sorts them mechanically by specialist disagreement, unresolved contradiction,
fewer authenticated local observations, greater staleness, then canonical
action order. The selected action is a real `PROBE_TIED_MAXIMUM` execution
through the protected receipt, authorization, Memory, relation-routing, and
confidence path.

Each problem can issue at most two tie-information probes. If the same tie
persists after both, its status becomes `UNRESOLVED` and Horus abstains.

## Prospective runtime schedule

The 54 attempts use six registered fresh runtimes. Each has nine attempts and
therefore no more than nine possible executions. The protected
`EPISODE_LIMIT=12` remains unchanged.

| Segment | Attempts | External regime |
|---|---:|---|
| `V08_A1_1` | 1–9 | A |
| `V08_A1_2` | 10–18 | A |
| `V08_B1` | 19–27 | B |
| `V08_B2` | 28–36 | B |
| `V08_A2_1` | 37–45 | A |
| `V08_A2_2` | 46–54 | A |

Rollover follows only this table. The request for a new runtime has no
authority to move a boundary or increase the protected episode limit.
