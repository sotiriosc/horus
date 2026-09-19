# Contradiction revision v1 — frozen feasibility-only protocol

Parent: `ca131869b97dd5c96dd60eb7329f65b1a293246f`, realized-event grounding v0. This document is frozen before implementing/executing the feasibility fixture. All repair files, earlier studies, main and tags remain unchanged. No push. **Zero model calls, parser controls, model startup or stochastic inference.** No 144-call behavioral campaign implementation.

## Scope and external world

Question: can both complete CONTROL/SHIFT H0/H1/H2 histories safely coexist through the unchanged receipt-bound implementation? Use `RealizedEventFramework` and `ExternalExecutionBoundary` from `experiments/realized_event_grounding_v0/`. Authority is authentic receipt origin and binding, not conformity with expectation. The existing shared-root software trust limits remain; no physical truth or hostile-process security claim.

Both arms start state 1, epoch 1001 and execute exactly HOLD, ADVANCE, RETREAT, HOLD, ADVANCE, RETREAT, HOLD. CONTROL retains the stationary world. SHIFT executes the same external world and changes only state-1 HOLD consequence +1→−1 and ADVANCE −1→+1 after execution 3, preserving next states 1 and 2. The regime flag stays inside the external world fixture/audit, never Map, authorizer or projection input. Reuse the repair's existing external `TestWorld`; do not infer actual events from predictions.

Required authorized histories, checked against real receipts (never injected):

| Stage | CONTROL HOLD / ADVANCE | SHIFT HOLD / ADVANCE |
|---|---|---|
| H0, after tx3 | [+1] / [−1] | [+1] / [−1] |
| H1, after tx6 | [+1,+1] / [−1,−1] | [+1,−1] / [−1,+1] |
| H2, after tx7 | [+1,+1,+1] / [−1,−1] | [+1,−1,−1] / [−1,+1] |

## Frozen checks and evidence

Every step records actual event, exact authentic receipt identity, full candidate package, authorized package/pair/Memory, latched prediction, measurement, Map version, quarantine, Recovery proposal/authorization, incumbent retention/replacement, commit and bounds. To observe transient Recovery/quarantine without replacing any implementation, a read-only Python profiling hook may record returns from the original functions; run an uninstrumented duplicate and require identical protected outcomes if that hook is used. This is harness observation, not another authority path.

Audit the original receipt object retained in the authorized package using object identity against the root captured after external execution, plus all eight receipt fields and external event identity. Audit every visible target observation at all six stages; retain old records unchanged and separate new event identities. No numeric-only provenance shortcut. The experiment's finite external audit records are never passed to Explorer or used to authorize.

Explicitly require acceptance of valid contradictory events at SHIFT tx4, tx5 and tx7 despite prediction and earlier same-state/action history. No prediction rewrite, prior-record relabeling, substitution or disagreement-only rejection. On any failed step require commit_delta=0, unchanged protected published state and no continuation grant; stop and report without automatic repair. The successful 14-step fixture may have no rejection opportunities: distinguish that from the repair's separately rerun adversarial atomicity checks.

Memory/pairs/packages ≤8, pending root ≤1, trace ≤24 and existing other bounds unchanged. Compare starting state, epoch/tx/action/pre-state/next-state, event-ID shape and package shape between arms; report actual metadata differences. Use distinct opaque source-lifetime identities for the two external executors; do not claim identical full receipt identities across arms.

At each stage project authorized pre_state=1 HOLD/ADVANCE observations in chronological epoch/transaction order, with exact epoch/transaction/event identifiers, surface action and consequence. Preview one fixed O1 mapping (K1=ADVANCE,K2=HOLD,K3=RETREAT) and O2 mapping (Q7=ADVANCE,M4=HOLD,Z2=RETREAT). Source identity and full provenance stay in the separate audit, not the model-visible preview. No regime labels, averaging, rewritten history or hidden archive. These are deterministic data previews, not model prompts or inference.

Retain bounded detailed evidence privately and publish compact results and hashes. Exact replay must regenerate deterministic evidence and compact results byte-for-byte. Run unchanged repair campaign/replay; old contradiction-v0 diagnostic (expected original false accept/exit 2); minimum repair 1; base frameworks v0/v1/v2; recorded-response replays of original integration, Memory v1, Adaptive v0, Semantic v0 and Prior-factorial v1. Verify prior source/evidence preservation.

## Frozen classification and stop rule

**A — CONTRADICTION REVISION FIXTURE FEASIBLE** only if all 16 requirements pass: complete CONTROL H0/H1/H2; complete SHIFT H0/H1/H2; correct changed HOLD −1; correct changed ADVANCE +1; original HOLD +1 unchanged; original ADVANCE −1 unchanged; every commit equals its authentic receipt; zero protected false accepts; zero receipt-mismatch accepts; zero prediction rewrites; no contradiction-only rejection; atomicity; unchanged bounds; exact chronological authorized-Memory projection; exact replay; required historical regressions. Campaign gate is provisional until replay/regressions complete.

**B — FEASIBILITY CORE CORRECTION REQUIRED** for any protected false accept, receipt substitution, wrong commit, rewritten history or contradiction-only rejection. **C — NOT ESTABLISHED** for any other missing completion requirement. Stop for B/C with the failed boundary; do not patch automatically. If A, stop with the completed feasibility report. No model revision, adaptation, contradiction understanding, causal inference, drift detection, RL, weight learning, general grounding, physical verification, AGI or RSI claim. The next decision about the behavioral study remains separate.
