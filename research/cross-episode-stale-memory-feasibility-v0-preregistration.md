# Cross-episode stale-Memory feasibility v0 — preregistration

Parent: `research/cross-episode-map-history-depth-v1`, `eed191991087b0b47990091faf2a2cf156f40e87`. Preserve its SUPPORTED result and all older results, especially transfer-v0 overall NOT ESTABLISHED / Explorer SUPPORTED / Map NOT ESTABLISHED. Main and tags unchanged; nothing pushed.

**ZERO MODEL CALLS.** No Ollama, prompts sent, stochastic inference or automatic behavioral follow-up. Existing deterministic Explorer/Map sources, receipt authority, Measure, Memory, Recovery and initialization are imported unchanged. Only a separate external test fixture changes one realized consequence law.

## Question and frozen sequence

Can authentic old observations and later authentic contradictory observations coexist across trusted fresh-state initialization, without rewriting the past or confusing historical evidence with current state?

Construct two independent systems (harness labels CONTROL and CHANGED). In each, begin epoch 1001/state 0. Freeze:

| Event ID | Epoch | Transaction | Action | Transition | CONTROL consequence | CHANGED consequence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 1001 | 1 | ADVANCE | 0→1 | +1 | +1 |
| 2 | 1001 | 2 | RETREAT | 1→0 | 0 | 0 |
| 3 | 1001 | 3 | ADVANCE | 0→1 | +1 | +1 |
| boundary | 1002 | none | trusted start_episode(1002,0) | 1→0 | no event | no event |
| P0 | 1002 | none | render at state 0 | none | [+1,+1] | [+1,+1] |
| external intervention | 1002 | none | change target law in CHANGED only | state unchanged | no change | no event |
| 4 | 1002 | 1 | ADVANCE | 0→1 | +1 | −1 |
| 5 | 1002 | 2 | RETREAT | 1→0 | 0 | 0 |
| P1 | 1002 | none | render at state 0 | none | [+1,+1,+1] | [+1,+1,−1] |
| 6 | 1002 | 3 | ADVANCE | 0→1 | +1 | −1 |
| 7 | 1002 | 4 | RETREAT | 1→0 | 0 | 0 |
| P2 | 1002 | none | render at state 0 | none | [+1,+1,+1,+1] | [+1,+1,−1,−1] |

Primary Memory/pair/package lengths are 3 at P0, 5 at P1, 7 at P2. Four target observations coexist without eviction. State 0 at P1/P2 comes only from authentic RETREAT navigation. No direct state assignment outside the unchanged trusted initialization primitive. No extra episode-1 navigation is necessary because event 3 ends at nonzero state 1.

After captured P2 only, run two ordinary HOLD actions at state 0 (epoch 1002 transactions 5 and 6): event 8 fills capacity; event 9 checks ordinary FIFO eviction of event 1 across Memory, pair and package rings. P0/P1/P2 evidence remains frozen and uncontaminated. HOLD transitions from genuinely unknown to known after authentic observation. Bounds remain Memory/pairs/packages 8, trace 24, source lifetime 24 and two epochs.

## External intervention and authority

The external world wrapper changes only state-0 ADVANCE consequence from +1 to −1; next_state remains 1. Every other transition and consequence remains identical to the existing stationary oracle. Audit all twelve state/action law entries. The mutation occurs after completed initialization and captured P0, before epoch-1002 transaction 1. It emits no event, receipt, package or Memory; before/after snapshots must match exactly. It is not communicated to framework components or projections as a regime/stale label.

Every record originates in ordinary action → external execution → original receipt → Measure → authorized publication. Retain original receipt objects in a private audit archive, separately recording each actual external execution. Audit Memory → pair → package → exact original receipt → actual event, including source identity, event ID, epoch, transaction, pre_state, action, next_state and consequence. Old records/receipts must remain unchanged through P2. Source lifetime survives each boundary; independent arms have different source identities and cannot have fully equal receipts.

Use the existing native deterministic Map, which latches (1,+1) at state-0 ADVANCE before execution. CHANGED’s new events must authorize (1,−1) despite mismatch. Neither prediction nor receipt is rewritten. No synthetic state candidate or Recovery fault is injected. Observe native Recovery calls rather than requiring zero: source inspection shows the current authorizer’s candidate path also depends on full measurement match, so consequence mismatch may cause native state Recovery even with correct next-state prediction. Report actual invocation and selected values; do not modify this policy.

Freeze four separate negative receipt controls after the primary fixtures: replay an old-epoch original receipt; substitute an equal-content copy of the new receipt; substitute a fake +1 receipt; change evidence A/B consequence bindings to +1 while keeping the actual −1 receipt. Each runs its own ordinary old-history/reset/intervention context. Require rejection and unchanged protected publication. These controls do not contaminate the two primary histories.

## Projections and matching

Use the unchanged epoch-visible Map projection. At each primary stage render all twelve existing opaque mappings as read-only values from the same two authentic systems; this is no model campaign. Rows contain only epoch, transaction_id, surface_action, next_state, consequence. P0 target identities are (1001,1),(1001,3); P1 adds (1002,1); P2 adds (1002,3). P0 arm projections must be identical for each mapping. P1/P2 Map projections differ only in authentic episode-1002 target consequences. No summaries, averages, current-truth labels, confidence or recency instructions.

Target ADVANCE is known throughout; it must never render UNTRIED/empty. State-0 HOLD and RETREAT have no matching primary records, so their UNKNOWN/empty projections are truthful (the navigation RETREAT records start at state 1). No absence marker is stored. No stale bit, obsolete label, deletion, ban or rewritten old consequence. Negative outcomes remain admissible observations.

Compare actual start state, epochs, actions, navigation, transaction/event-ID shape, source-lifetime structure, ring sizes and projection schemas. Record actual snapshot differences, including independent source identities and native mismatch/recovery bookkeeping. Do not assert complete receipt equality across independent sources.

## Frozen completion classification

A — CROSS-EPISODE STALE-MEMORY FIXTURE FEASIBLE only if all seventeen hold:

1. Both episode-1 +1 target records are authentic.
2. Trusted fresh-state initialization passes.
3. Old records survive unchanged.
4. External relation changes without Memory rewrite.
5. First authentic changed −1 event authorizes.
6. Second authentic changed −1 event authorizes.
7. CONTROL P0/P1/P2 exact histories are correct.
8. CHANGED P0/P1/P2 exact histories are correct.
9. Current external/authorized state is 0 at every future probe stage.
10. Cross-epoch chronology is unambiguous.
11. No contradiction-only rejection.
12. Every committed observation equals its authentic receipt and actual event.
13. Zero protected false accepts in the tested fixtures/controls.
14. Zero receipt, prediction or historical rewrites.
15. Existing bounds hold.
16. Exact replay passes.
17. Historical preservation passes.

B — CROSS-EPISODE AUTHORITY / HISTORY FAILURE for false acceptance, authentic contradiction rejection due to history, rewritten past, provenance detachment, identity collision, stale UNKNOWN contradiction, receipt substitution, or current-state/history conflation. C — NOT ESTABLISHED for another missing completion requirement. Provisional raw results keep replay/preservation pending; no A until both actually pass. A fixture exception is preserved in STOP evidence; never hide or repair an observed architecture failure within this study.

## Evidence and preservation

Freeze this preregistration, exact sequence, implementation, tests and all inherited substantive public files before executing the fixture. Root README/manifest may be updated only to link completed results. Durable detailed evidence remains outside the public tree; public code, compact results, report and verification suffice to rerun this deterministic zero-model fixture.

Run with network access forbidden. Replay deterministic generation and require byte-identical results and details: old history, boundary, intervention timing, executions, receipts, Memory, projections, provenance, bounds, controls and summary. Finalized live/replay results must also match. Execute zero-inference historical replay for history-depth-v1, transfer-v0, initialization-v1, Map ablation, R1 and realized-event grounding; preserve contradiction checkpoints and all older files/results by complete parent hashes plus focused tests. Verify prior branch refs, main, tags and private archive checksum inventories unchanged. Never invoke model inference in regressions.

## Claim and stop

If A: authenticated prior-episode observations and later contradictory authenticated observations can coexist across a fresh episode boundary with provenance, chronology and authority preserved in this bounded changed-world fixture. Trusted simulator reset and external emission remain trust assumptions. No model adaptation, drift detection, stale-memory reasoning, persistent learning, RL, AGI or RSI is tested. Report actual native Recovery even if it is not zero.

Create the required 31-part report and compact results. Stop after verification. Any future model stale-memory behavioral experiment requires a separate research decision and authorization.
