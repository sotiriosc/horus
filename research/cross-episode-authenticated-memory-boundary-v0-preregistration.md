# Cross-episode authenticated Memory boundary v0 — preregistration

Parent `46d01e1e6d09a24191aea1ddf9e413f04711b14b` (paired Map history effect
SUPPORTED). Preserve all prior results, authority implementations, main and tags.
Zero model calls. No Ollama, model requests, conversational state or stochastic
inference. No core repair or reset API is introduced. No push.

Question: can a fresh episode start at registered state 0 while retaining earlier
authenticated events, full provenance, unique identities, chronology, bounded
eviction and UNKNOWN semantics under existing APIs?

## Interpretation frozen from source inspection

Test the existing `StatusBoundFramework.start_epoch(1002)` on the same framework,
external source and stationary `TestWorld(0, False)` lifetime, starting at epoch
1001. The wrapper audits history, requires no pending external event and calls
the unchanged core epoch method. New instances are a separate diagnostic, not a
history import mechanism. Do not transplant records, mutate world internals,
call Map.commit directly to reset state, or invent a RESET Memory event.

Initial inspection: start_epoch retains Memory/pairs/packages and world/current
state; resets transaction counter, episode step counter, Map version/quarantine
and authorizer state; allows continuation. It accepts only an epoch argument.
The study must distinguish a natural return to 0 through authentic actions from
a boundary operation that can initialize nonzero state to 0. A successful
zero-ending continuity fixture alone cannot establish the latter.

## Bounded diagnostics

1. Same-lifetime continuity: epoch 1001, initial state 0; ordinary authenticated
   HOLD, ADVANCE, RETREAT, HOLD commits. This naturally ends at 0. Apply existing
   start_epoch(1002), without world mutation. Render Explorer/Map history. Execute
   the same four ordinary actions. Memory/pair/package bound remains eight.
   This is a limited epoch-continuity fixture, not proof of an independent reset.
2. Ninth ordinary HOLD commit: existing FIFO eviction must remove the oldest
   matching Memory record, pair and package together. No epoch preference.
3. Nonzero diagnostic: HOLD, ADVANCE ends at state 1. start_epoch(1002) must be
   observed, not assumed to reset state. Inspect rejection of an unsupported
   initial_state parameter. Compare a fresh constructor at 0, which does not
   import prior history. No manual state rewrite.
4. Existing epoch guards: same epoch, third epoch, pending core proposal and
   pending authentic receipt. Require rejection without state mutation.
5. Throwaway negative controls: replay prior-epoch receipt; substitute equal-field
   copy of current receipt; discard pairs only; discard packages only. Require
   ordinary rejection and no protected partial publication. Deliberate invalid
   controls do not become a proposed retention mechanism.
6. Fresh-lifetime diagnostic: two separate sources/instances at epoch 1001 each
   commit one HOLD. Audit which partial keys repeat and which full receipt/package
   identities differ. Do not combine these histories or silently equate lifetimes.
7. Read-only contradiction representation: use preserved Map established-prior v1
   setup call index 2 / setup step 3 with authorized HOLD consequences [1,1,-1].
   Verify saved provenance and immutable history. Diagnostic earlier/later group
   metadata separates original records 1–2 from 3 without changing epochs or
   identities. This is not a new shifted world or proof of a reset-capable
   cross-epoch contradiction fixture. Do not manufacture cross-epoch receipts.

All new executed world fixtures use the unchanged stationary law. The archived
contradiction control executes nothing. Deterministic sources and direct projection
inspection only. Block socket creation during the diagnostic; record zero attempts.

## Projections, provenance and bounds

Existing projections sort authorized matching records by (epoch, transaction_id).
Verify stability even when input records are reversed and transaction IDs repeat
across epochs. Retained known pairs must not render UNTRIED; untouched pairs must
render UNTRIED / []. No marker enters Memory. Keep historical values immutable.
Audit Memory→pair→package→original authenticated receipt and exact receipt object
retention. Retire each pending root slot through ordinary release. Never retain
old receipts in that slot. Source event count continues, at most 24 per lifetime;
Memory/pairs/packages remain eight; epoch limit remains two; authorizer capacity
remains 24 per epoch. Do not enlarge any bound.

Document that a displayed transaction_id alone is not globally unique across
epochs. Do not silently modify the projection schema. Full protected provenance
must remain distinct from the abbreviated model-visible history.

## Seventeen required invariants and frozen classification

1. Prior authenticated records unchanged until ordinary eviction.
2. Provenance traceable.
3. No identity collision in the proposed registered boundary.
4. Fresh registered current-state initialization without historical rewrite.
5. Known retained pairs do not revert to UNKNOWN.
6. Untouched pairs remain UNKNOWN.
7. New observations append chronologically.
8. No boundary pseudo-event.
9. Memory bound eight.
10. Ordinary FIFO eviction unchanged.
11. Pending authentic receipt at most one.
12. Receipt authority unchanged.
13. Measure unchanged.
14. Recovery unchanged.
15. No model/chat persistence.
16. Exact replay passes.
17. Historical regression checks pass.

**A — CROSS-EPISODE AUTHENTICATED MEMORY BOUNDARY READY** only when all pass,
including a complete fresh-state two-episode fixture. **B — MEMORY / AUTHORITY
SEMANTIC FAILURE** for actual provenance detachment, collision, false authorization,
history rewrite, stale UNKNOWN contradiction, state/history conflation, receipt
substitution or partial publication caused by the supported carryover operation.
**C — NOT ESTABLISHED** for another missing required property, including an
unsupported fresh-state reset. Correctly rejected negative controls are not B.
Report unsupported/unexecuted properties explicitly. If required semantics are
missing, stop at the feasibility result; do not repair core or initiate inference.

## Evidence and verification

Freeze inherited substantive files, study sources, this preregistration and the
archived contradiction source hash before execution. Save detailed deterministic
evidence privately. Replay the diagnostic from the same frozen inputs, requiring
results.json and details.json byte-identical. Final assurance may mark actual
replay/regression results but cannot change the missing-property finding.

Run bounded historical zero-inference checks: paired ablation recorded-response
replay, R1 recorded-response replay, unchanged v2 UNKNOWN tests, receipt-boundary
tests, status-authorizer tests and input-binding tests. Preserve all inherited
substantive files and prior Git refs; historical raw source hashes remain intact.
Public output: compact results, verification, reproduction and a 32-section report.
Raw historical data, detailed traces, local paths and private research stay private.

Stop afterward. No cross-episode model campaign or automatic separate repair.
A result establishes neither persistent/lifelong model learning, nonstationary
adaptation, general transfer, cross-task generalization, AGI nor RSI.
