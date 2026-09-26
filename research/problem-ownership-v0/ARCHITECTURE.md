# Horus v0.13 canonical problem ownership

`ProblemManager` is the single active problem-management boundary introduced by
v0.13. Its HMAC-chained event stream is authoritative. The JSON index is a
disposable projection rebuilt from that stream at every open.

Each problem has a stable `PR-NNNN` identity, a finite type, an exact structured
scope, an owner, a lifecycle state, a capability assessment kept in a separate
field, independent route budgets, evidence, and append-only history. Exact type
and scope deduplicate active problems. Different scopes create different
problems. Relationships are explicit graph edges and never merge identity.

The manager can detect, append, relate, expose an applicable problem, and emit a
typed request. Every authority flag is false. Execution, receipts, Memory,
prediction, training, objectives, models, and authorization remain outside it.

The legacy PR-0001 and PR-0002 objects are retained byte-for-byte as nested
`imported_snapshot` values with SHA-256 commitments. PR-0001's canonical graph
node is `SUPERSEDED` because PR-0002 owns the live state-2 scope; its imported
snapshot remains `UNRESOLVED`. PR-0002 remains `ROUTE_EXECUTED`. The explicit
edge is `PR-0002 successor_of PR-0001`.

The current problem is selected mechanically by exact problem type and scope.
For value ties the scope is `(pre_state, canonical tied_action_set)`. A global
current-problem pointer does not exist.

Operational service and runtime-capacity failures receive separate problem
identities and scopes. A `blocked_by` edge can connect the behavioral problem to
the operational blocker without changing either problem's identity or type.

The active runtime adapter composes the unchanged ordinary grounded Explorer
with scoped problem lookup. The manager is called before the existing
confidence freeze and completed only after the ordinary runtime returns. A
pending decision and every consumed per-problem allowance replay from the
authoritative stream.

Inspection is available with:

```bash
python -m horus.problems list --registry REGISTRY
python -m horus.problems show --registry REGISTRY --problem-id PR-0003
python -m horus.problems rebuild --registry REGISTRY
```
