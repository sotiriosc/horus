# Horus v0.22 route-handoff durable recovery preregistration

Parent: `9c3f7b866def0d3d3c1b106493723afdbf1bde91`.

This milestone repairs one operational handoff defect and recovers one already authenticated, uncheckpointed prediction suffix. It does not alter v0.21, router thresholds, global Explorer policy, model weights, or the retained scoped authorization.

## Frozen route rule

Route precedence is:

1. an ordinary legitimate Explorer route;
2. an existing problem-scoped fallback when no ordinary route is available;
3. abstain or request authority.

When the ordinary route becomes available after a special route has fulfilled its purpose, the outcome is recorded as `NORMAL_ROUTE_REGAINS_CONTROL`. The older special route cannot override it.

## Frozen recovery boundary

The source checkpoint registers 2,502 call records while the physical authenticated stream contains 2,529. Recovery is permitted only if the 27-record suffix authenticates, continues the registered chain, represents exactly the nine intent/response/parse calls for unfinished decision 91, and has no receipt, Memory publication, routing evidence, Explorer completion, or contradictory durable state. Failure of any predicate produces `DURABLE_TAIL_RECOVERY_REJECTED` and stops the run. Recovery may update only the checkpoint's registered call count/head. It cannot rewrite the stream, reissue calls, execute, publish Memory, or update routing.

The exact logical call identity and nine request hashes are frozen in `policy.json`. Raw prompts and responses remain private.

## Zero-inference gate

Before recovery or execution, durable state must replay as state 1 with PR-0003 applicable, the ordinary cadence available, and the ordinary Explorer decision equal to decision 91 / `PROBE` / `ADVANCE` / `PROBE_DISAGREEMENT`. The ordinary route must outrank the scoped fallback. Otherwise the run stops.

## Live bound

Reuse the nine authenticated predictions and issue zero new model calls. Freeze the ordinary decision before external execution. Permit at most one ordinary ADVANCE probe. Then score the exact rolling six-observation `(1, ADVANCE)` window and report the evicted and added rows, both specialist scores, lead, and selection before/after.

A maximum of one ordinary follow-up is allowed only if the tie resolves and an exact reusable zero-call prediction batch exists. New model calls require separate authorization, so absence of such a batch stops the follow-up without changing the completed probe result.

The scoped v0.20 budget must remain `(limit=2, granted=1, executed=1)`. PR-0003 and PR-0005 remain distinct. No training, new exploration rule, forced destination, model change, or additional route is allowed.
