# Zakhor durable-memory trial v0 — preregistration

Status: frozen before behavioral inference.

## Question and boundaries

This focused viability trial asks whether a small Zakhor-style organization and
retrieval index adds useful behavior beyond a strong ordinary durable-memory
baseline when both read exactly the same authorized evidence.

The protected substrate is reused, not recreated:
`ExternalExecutionBoundary` produces the original receipt;
`StatusBoundFramework` performs Measure, independent/status-bound authorization,
and atomic publication; `SessionStore` preserves HMAC-authenticated event, call,
and scoring chains. Only an event with status `AUTHORIZED`, exact receipt
identity/provenance, and Memory/receipt equality may enter the shared SQLite
store. No Horus router, grounded Explorer, problem manager, learned specialist
selection, or route-handoff policy participates.

Both conditions use the same SQLite `events` rows, the same Qwen 0.5B revision,
the same frozen G2 adapter, the same consequence-only system instruction, the
same event order, and the same maximum context of six records. There is one model
instance per fresh process; calls alternate M/Z order by event parity. There is
no training, retry, autonomous action, activation keeper, or outcome-driven
extension.

## Durable records and interface

Every append-only event row retains global chronological order, complete receipt
identity, source identity, event and transaction identity, epoch, pre-state,
relation, action, realized consequence and next state, receipt provenance hash,
authorization status and identity, context identifier, and authenticated event
stream sequence/head. Contradictions are separate rows and are never updated or
deleted.

The experiment adapter exposes `record`, `retrieve_modern`, `retrieve_zakhor`,
`history`, `checkpoint`, and reopen/reconcile behavior. SQLite uses foreign-key
checks, full synchronous commits, a schema version, and exact-session
reconciliation on restore.

## Frozen retrieval rules

M is an intentionally strong ordinary baseline. It performs exact relation
lookup, takes the four most recent records, adds the most recent anchor for every
missing consequence value, fills remaining capacity by recency, and returns the
selected records in chronological order. Capacity is six.

Z uses the same records and capacity. Its only extra mechanism is a persistent
Zakhor-style regime index: the first outcome initializes an active regime;
different outcomes remain separately retained “stranger” candidates; three
consecutive matching strangers (`K=3`, the existing Zakhor rebirth constant)
confirm a new regime. Retrieval prioritizes up to three unassimilated stranger
records, then three recent active-regime records, then one anchor from each prior
confirmed regime, then recency fill. It returns chronological records to the
same prompt. Its state and regime index are durably hashed. This is a retrieval
adapter, not a redesigned Zakhor architecture.

Activation keeper hooks are excluded because they would change model computation
and confound the memory-organization comparison.

## Event schedule and restart

Exactly 24 observation-controlled HOLD events occur at state 1:

- events 1–6: stable regime A, consequence +1;
- events 7–16: changed regime B, consequence −1;
- fresh-process restart after event 12;
- events 13–16: post-restart changed-regime persistence;
- events 17–24: restoration to regime A, consequence +1 and endurance.

Protected runtimes are deterministically segmented at 1, 7, 13, and 17 so none
exceeds the existing episode bound. Runtime boundaries never depend on outcomes.
Before restart, hashes cover the database, logical event store, M policy state,
Z state/index, protected checkpoint, event/call/scoring chains, and local
authority key. Stage 2 is a separate process. It must reopen and reconcile exact
durable artifacts before its first prediction, with no hidden runtime object.

## Calls and measurements

There is one M and one Z consequence-model call before every event: exactly
`24 × 2 = 48` calls, with no retry or extra call.

Every request records candidate count, selected identities, retrieval reasons,
chronological positions, candidate and selected consequences, contradiction
inclusion/exclusion, tokenizer context cost, retrieval latency, and Z index state.
Mechanical audits report whether the selected set contains the most recent event,
current-phase relevant evidence, contradictory outcomes, detected change, and
restoration evidence. These complement model accuracy so this is not merely a
next-token comparison.

Relevant evidence means prior records from the current registered phase. Stale
evidence means a selected prior record whose outcome differs from the current
registered consequence. Relevant retrieval rate is relevant selections divided
by `min(relevant available, 6)` summed across opportunities. Stale retrieval rate
is stale selections divided by all selections.

Report consequence accuracy, first-correct change/restoration latency (zero-based
opportunity offset), false persistence, contradiction preservation, retrieval
rates, restart integrity, events 1–8/9–16/17–24, worst rolling six events, context
tokens, retrieval/model/combined measured time, and error causes.

Wrong predictions use the first applicable mechanical classification:
`RELEVANT_MEMORY_NOT_RETRIEVED`, `CONTRADICTORY_MEMORY_LOST`,
`STALE_MEMORY_OVERWEIGHTED`, `CORRECT_MEMORY_RETRIEVED_MODEL_WRONG`, or
`RETRIEVAL_AMBIGUOUS`. `MEMORY_CORRECT_NO_BEHAVIORAL_EFFECT` is reserved for a
paired retrieval improvement that changes no prediction and is reported outside
the per-error priority when observed.

## Decision gate

`INVALID` applies if protected preflight, exact replay, source identity, store
reconciliation, restart hashes, schedule, or call budget fails.
`DISTINCT_USEFUL_SIGNAL` requires a traceable Z-only retrieval behavior that
improves at least one behavioral property without harming another primary
behavioral property. `MODERN_MEMORY_SUFFICIENT` applies if M is behaviorally equal
or better while Z adds complexity or overhead. `MIXED` applies to behavioral or
memory-quality tradeoffs. `NO_USEFUL_SEPARATION` applies when behavior and
material retrieval properties do not separate. No combined score is used.

