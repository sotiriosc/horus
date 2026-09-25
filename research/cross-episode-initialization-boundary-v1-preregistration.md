# Cross-episode initialization boundary v1 — preregistration

Parent `b2306c917cfd8cdfc89d272e8f72fa1f01927605`, boundary-v0 **C — NOT ESTABLISHED**.
Preserve it and every earlier result, authority implementation and historical
projection unchanged. Branch `research/cross-episode-initialization-boundary-v1`.
Zero model calls; no Ollama or inference; no push or automatic model campaign.

## Question and minimal change

Can a trusted operation reset the present without resetting the past? Add a separate
controller-owned `start_episode(new_epoch, initial_state)` and separate epoch-visible
Map projection. Do not modify historical framework/receipt/Measure/Recovery/eviction
code, import old history into a fresh framework, fabricate a RESET event or expand
bounds. Existing Explorer schema and old Map adapters remain unchanged.

Same external source **object/lifetime** spans epochs 1001→1002; its event counter
continues. The immutable registered plan supplies start state (0 in the primary
fixture), first epoch 1001, second epoch 1002. Exact built-in integer state in 0…3
and exact integer epoch are required, and supplied state must match the plan.
Map reset convention: registered current state, new epoch, version 0, valid state,
empty Map quarantine, inherited empty repaired authorizer for the new epoch.

## Trusted ownership and atomic publication

A driver-only controller owns a single publication object containing both the
current simulation world and current framework wrapper. The external receipt source
is unchanged and holds a stable execution-only route to the active world. No model
gets the controller, source, framework or reset capability; projections are detached
plain values. Historical read ports/admission logic remain unchanged.

Preconditions: same owned source/lifetime; no pending external receipt; no in-flight
core transaction; continuation legal, current Map valid, quarantines empty; existing
world/Map states agree; retained provenance passes the existing audit; epoch passes
existing bounds and the registered 1001→1002 schedule; target state matches the plan.

Prepare a shallow wrapper copy with a deep-copied core and copied package list
retaining the exact historical package/receipt objects. Invoke the unchanged
start_epoch on the staged core, then construct its Map at the registered state.
Separately deep-copy the simulation world and invoke its trusted initialization
primitive **only on that unpublished copy**. Preserve execution count and last
actual event. Audit all staged history and states. Publish both through **one
reference assignment**, under the controller lock, with no callback or I/O at that
commit point. Public reads use the same lock and detached coherent snapshots.

Exceptions before publication discard preparations and leave current publication,
source counters/pending slot, history and identity state unchanged. There is no
physical-device reset or distributed rollback claim. This assumes the in-process
copy-stageable simulator and trusted controller APIs; direct hostile mutation of
private Python objects, interpreter/process crashes and external irreversible I/O
are outside the atomicity claim. No rollback after successful publication is claimed.

Initialization emits only boundary metadata: zero realized events/receipts/Memory
records/pairs/packages/consequences. Earlier last next_state need not equal new
current state. It must not trigger Measure or Recovery merely due to initialization.

## Projection identity

New Map history records contain exactly epoch, transaction_id, surface_action,
next_state and consequence. Sort matching authorized history by (epoch,transaction_id).
No source capability, receipt object, package ID or authorizer fields are model-visible.
Epoch is identity/chronology metadata, not a regime label. Removing epoch must recover
the old Map projection; old prompt records are not modified. Explorer retains its
consequence-only chronological lists. Known retained pairs are not UNTRIED; untouched
pairs use UNTRIED / [] only at projection time. No marker enters history.

## Frozen bounded campaign

Primary stationary fixture, one source lifetime:

- Epoch 1001 from state 0: HOLD, ADVANCE, ADVANCE, ADVANCE. Four ordinary authenticated
  commits end at **state 3**, distinct from new start 0.
- start_episode(1002,0): world and Map become 0, Map version 0; source execution/event
  counters remain 4; four historical events still end in their original states.
  Instrument the boundary: no external execution, package admission, Measure or
  Recovery calls. Audit retained receipt objects and complete provenance.
- Epoch 1002: HOLD, ADVANCE, RETREAT, HOLD, four ordinary authenticated commits.
  Source event IDs 5–8, transaction IDs 1–4. Old/new history coexists, including
  repeated transaction ID 1 under different visible epochs. Reverse input iteration
  and require identical serialization. Explorer/Map bind current state 0 after reset.
- Ninth commit: HOLD. Ordinary FIFO must remove epoch 1001 / transaction 1 and its
  matching pair/package, with no special episode policy.

24 failure cases: pending receipt; pending transaction; same epoch; third epoch;
bool, float, string, negative, out-of-range and unregistered state; bool, float and
unregistered epoch; detached pair ring; detached package ring; corrupt Memory record;
illegal continuation; replaced source lifetime; external preparation failure before
and after staged mutation; wrong staged external state; authorized preparation failure
before and after staging; wrong staged authorized state. Each must reject with exact
published snapshot equality and unchanged publication/source receipt identity.

Four current-admission controls: old receipt after reset, equal-field copy, wrong
receipt epoch and duplicate current package. Require ordinary rejection without
partial publication. Separately exercise unchanged duplicate/capacity authorizer
checks (24 identities). Preparation observation hooks must see the old coherent
publication throughout staging. Six unit tests also check each finite registered
initial state and detached projection/snapshot values.

## Differing-outcome representation control

Primary fixture remains stationary. A **separate deterministic control** reuses the
already-established Map-prior-v1 `HoldWorld` and its existing switch-after-event-2
rule, with state 1. It reconstructs three authenticated events [1,1,-1] entirely
**before** initialization, then initializes epoch 1002 at registered state 1 and
executes one further HOLD with consequence -1. Old epoch-1001 positive observations
and later epoch-1002 negative observations must coexist with original provenance.
No epoch or receipt is relabeled; no new regime law is invented; the boundary does
not cause or adjudicate the earlier switch. This control proves representation and
authority only, not nonstationary transfer or model behavior. Historical files are
unchanged. The primary same-source world remains stationary across initialization.

## Bounds and exact replay

Unchanged: Memory/pairs/packages 8, pending authentic receipt 1, trace 24, source
lifetime executions 24, epochs 2, core steps per epoch 12, authorizations per epoch 24.
Run without networking; retain detailed deterministic records privately. Repeat the
full campaign from frozen sources; require details.json and results.json byte-identical.
Final compact result must regenerate identically using actual replay/regression proof.

Historical checks: replay prior boundary-v0 (still C), paired Map-memory ablation,
R1, and run composition bindings, status/Recovery, realized-event, UNKNOWN and relevant
old Map projection tests. No new inference. Hash-preserve all inherited substantive
files and saved historical archives; preserve prior branch refs, main and tags.

## Eighteen frozen requirements and classification

1. Explicit new epoch.
2. Nonzero current state resets to registered initial state.
3. External and authorized state synchronized.
4. Zero realized events at initialization.
5. Historical Memory/pairs/packages unchanged.
6. Provenance traceable.
7. Identities do not collide.
8. Authorizer reset safe.
9. Known pairs remain known.
10. Untouched pairs remain UNKNOWN.
11. New Map history exposes unambiguous cross-epoch identity.
12. Later observations append chronologically.
13. Ordinary ninth-event FIFO unchanged.
14. Failure paths atomic.
15. No model capability controls reset.
16. Bounds unchanged.
17. Exact replay passes.
18. Historical regressions pass.

**A — CROSS-EPISODE INITIALIZATION BOUNDARY COMPLETE** only if all pass.
**B — EPISODE INITIALIZATION AUTHORITY FAILURE** for split state, fake events,
history rewrite, provenance detachment, identity collision, anti-replay bypass or
partial reset/publication caused by the boundary. **C — NOT ESTABLISHED** for another
missing requirement. Correct rejection of deliberately invalid controls is not B.
Before actual verification the result remains provisional C; passing structural tests
alone cannot establish A. Never relax a threshold after seeing results.

Stop after the complete report, replay and checks even if A. No persistent/lifelong
model learning, autonomous reset, cross-source import, nonstationary transfer, AGI
or RSI claim. A later model campaign requires a separate decision.
