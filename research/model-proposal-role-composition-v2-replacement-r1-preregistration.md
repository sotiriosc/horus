# Composition v2 replacement R1 — execution and durability registration

Parent interrupted checkpoint `7f3fa22e432adc5b280a6a12a5b289052de6e0b7`.
Original v2 remains permanently **C — NOT ESTABLISHED / INTERRUPTED / LIVE EVIDENCE
UNAVAILABLE**. The user explicitly authorized one separately recorded replacement
because original evidence was lost, not because of unfavorable behavior. No data,
console counts or reported commits from that run enter R1. Nothing is pushed.

## Frozen science, separate identity

Adopt the unchanged [v2 scientific preregistration](model-proposal-role-composition-v2-preregistration.md),
implementation `c4d241400feb455a3dfcd88af4117ae0c20f66a5`, exact prompts, parsers,
projections, world, model bytes/runtime/sampler, schedule, mappings, seeds, bounds,
UNKNOWN semantics, authority and all classification criteria. All inherited source
files remain unchanged. Only evidence-storage/crash-handling infrastructure is new.

Campaign ID: `HORUS_COMPOSITION_V2_REPLACEMENT_R1`. Start episode 0 / decision 0,
state 0 and empty Memory. All 12 episodes, maximum eight decisions each; caps
96 Explorer / 96 Map / 96 Recovery, 288 total. No retries, replacement episodes,
new seeds, forced Recovery, extension or second run. A fresh source lifetime is
namespaced with the campaign identity using the unchanged setup function; this
changes no model-visible content or authority predicate. The record archive owns
R1 identity separately from historical studies. R1 is not an exact replay of the
crashed stochastic execution.

## Durable storage and ordering

Live evidence resides in a dedicated persistent home-directory archive outside
all worktrees and temporary directories. Reject ephemeral output paths. New live
execution requires a nonexistent output directory; never resume by replaying an
unfinished call. A process lock and exclusive journal creation prevent two writers.

Deterministic call ID derives from campaign, episode, decision and role. Before
HTTP send append REQUEST_INTENT_RECORDED with all identifiers, mapping, original
seed, authorized state, Memory snapshot/digest, structured projection, exact system
and user text, exact options and serialized request. Flush and fsync the journal.
After receiving response append RESPONSE_RECEIVED with raw output and metadata,
flush/fsync **before** parser invocation. After strict parsing append PARSED with
finite result/admission or rejection and flush/fsync. No returned context is reused.

Read-only observation journals each boundary: trusted Prediction latch before
world execution; external event; receipt; Measure; genuine Recovery opportunity;
Recovery response and parse; framework candidate envelope; independent authorizer
decision; publication/rejection and continuation. TRANSACTION_FINALIZED contains
the entire frozen transaction record, protected/Memory snapshot and digests,
bounds, call counts and termination. Flush/fsync before the next decision.
Observers do not alter proposals, evidence, authority or routing decisions.

After every finalized decision write compact campaign-state: last episode/decision,
real-call count by role, termination states, protected/Memory digests and evidence
sizes/hashes. Write a temporary file **in the durable directory**, fsync it, atomic
rename, fsync the parent directory. Durability failures abort before further I/O.
Journal entries form a deterministic hash chain; replay checks complete identity,
ordering and byte equality. Supplemental wall-clock/server logs are separate.

## Crash semantics and mandatory zero-call gate

Inspection distinguishes not issued, intent recorded (AMBIGUOUS / POSSIBLY ISSUED),
response received, parsed and transaction finalized. Partial/truncated/corrupt
journal records or any intent lacking response prevent automatic continuation.
A finalized transaction without matching atomic campaign state also requires
inspection. Existing-output live reruns are refused even after clean completion.
No console-derived state or automatic request reissue is permitted.

Before first inference: verify inherited scientific hashes and exact v2 systems,
all seeds/schedules/parsers/UNKNOWN, full model bytes and runtime, durable directory,
write-ahead/flush/fsync ordering, atomic state writes and simulated crash/restart
at all five phases. Tests use zero model calls. Verify instrumented synthetic
transactions equal uninstrumented frozen transactions byte-for-byte under the same
fresh source identity. If any gate fails, stop with zero real model calls.

## Decisions and completion

Keep v2's 20 integrity requirements and seven required live paths unchanged.
A requires all of them plus exact R1 replay and historical regressions. B means an
observed protected authority/integrity violation. C covers incomplete coverage or
requirements; behavioral weakness is not automatically B. Incomplete/ambiguous
infrastructure evidence produces an interrupted C, with unknowns never invented.
Live result stays provisional until recorded replay/regression evidence is complete.

After the one campaign: exact inherited 5/14/22 synthetic role controls, full R1
recorded-response replay with zero inference, original required historical
regressions, final report with all original 44 scientific sections plus separate
identity/durability accounting. Require byte-identical regenerated calls, routing,
projections/prompts, parsers, latches, events/receipts/Measure/Recovery/authorizers,
Memory, terminations, chains, journal, state and summaries where registered.
Finalize from R1's own complete archive only. Preserve the original interrupted
checkpoint and all prior milestones unchanged. Stop after R1; no R2, pooling,
optimization, tuning, architecture changes or push.
