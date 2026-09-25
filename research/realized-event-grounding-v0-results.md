# Realized-event grounding v0 — repair result

**A — REALIZED-EVENT GROUNDING REPAIR COMPLETE FOR DECLARED SCOPE.**

The new path authorized changed HOLD **−1** and changed ADVANCE **+1**, preserving their earlier contradictory observations and the original predictions. The campaign recorded **105 protected clean authorizations, 20/20 atomic attack rejections, zero protected false accepts, 12/12 stationary passes**, and **one out-of-model wrong acceptance when the trusted root lied**. Six additional boundary tests passed. Exact replay and all requested historical regressions passed. **New model calls: zero. Model contradiction revision: UNTESTED.**

[Preregistration](realized-event-grounding-v0-preregistration.md) · [compact results](../experiments/realized_event_grounding_v0/results.json) · [actual execution verification](../experiments/realized_event_grounding_v0/verification.json) · [implementation and reproduction](../experiments/realized_event_grounding_v0/README.md).

## 1. Demonstrated historical failure

In the preserved old path, SHIFT transaction 4 executed state-1 HOLD with actual consequence −1. Its prediction and stationary A/B/C said +1; authorization committed +1. That was an externally audited false accept. The old diagnostic remains unchanged and still reproduces this result. This repair changes the evidence boundary in a separate implementation, not the interpretation of that negative checkpoint.

## 2. Frozen parent and historical hashes

Parent: `f21c62532590c35b7c459b647ec09ecfbcb5bb0c`. Protocol: `bcf7356`; initial implementation: `9075e9e`; campaign and regressions: `3aaae70`. The historical framework checkpoint remains `8ec32c839133df7ddd76448063b5f765c20155da`. All 23 frozen source hashes were checked before and after execution; exact hashes and new source hashes are in compact results. Of 293 inherited files, 291 remain byte-identical; root README receives only an appended checkpoint and PUBLIC_MANIFEST an inventory refresh. Main remains `b8e4245ef14b11ee5d94ce851aec4d8dc059963f`; all five historical tag targets are unchanged. No push or history rewrite.

## 3. New realized-event trust root

`ExternalExecutionBoundary` owns the executor and one pending immutable receipt. It calls external execution first and emits the receipt only after that returns. Source authenticity and receipt integrity are trusted. Components receive a read-only pending-receipt port; they do not receive the external execution/release capability. A same-valued fabricated receipt has no authentic origin. This is a bounded software capability boundary in a single-threaded prototype, not cryptographic or hostile-process isolation. Failed execution creates no receipt.

## 4. Authority direction

Proposal → prediction latch → completed external execution → authentic receipt → package binding checks → staged framework processing → atomic publication → Memory. Explorer, model, Map, Measure, Memory, Recovery, adapters and package authorization cannot mint an authentic receipt through their interfaces. Constructing a `RealizedEventReceipt` dataclass does not make it authentic: the exact object must occupy the protected pending slot. The external driver retires that slot after resolution. Predictions never become event authority.

## 5. Exact receipt schema and provenance

The frozen receipt has eight fields: `epoch`, `transaction_id`, `pre_state`, `action`, `next_state`, `realized_consequence`, `event_id`, `source_identity`. The trusted source identity names one source lifetime; event IDs increase from 1 to at most 24 in that lifetime, including across epoch changes. A committed `AuthorizedEvent` retains the exact receipt, latched prediction, pair ID and package ID `(source_identity, event_id, epoch, transaction_id)`. Memory's pair ID links to that package and hence the full receipt/execution identity. Numeric equality alone does not establish origin.

## 6. A/B/C relationship to the root

The new layer reuses the historical v1 five-component loop, its Measure/Recovery behavior and the staged-copy publication pattern. Its shared-receipt pair gate replaces the old stationary pair authority. A/B carry full eight-field bindings; the package's C field carries source/event/epoch/transaction identity. The old stationary C producer and v2 separation registry are not used to confer new event authority. The internal legacy A/B ports receive receipt-derived adapters marked `SHARED_REALIZED_EVENT_ROOT` in both lineage and domain fields. This avoids inventing three separate physical evidence paths.

## 7. Why this is not three independent truth measurements

All bindings descend from **one** authentic receipt. Adapter redundancy is structural compatibility and package consistency, not independent observation or a fault-tolerance voting scheme. The gate requires authentic object origin, correct pending execution identity and exact A/B/C binding to that root. Agreement among fake descendants supplies no authority. There is no 2-of-3 or 3-of-3 truth rule.

## 8. Prediction versus realized outcome

The original prediction is latched before execution and retained unchanged in the authorized package. Measure compares that prediction against the receipt-derived pair. Both changed-action records correctly have `measurement_matches=false`. Across all 105 protected clean authorizations, no prediction was rewritten. Contradiction is a prediction error eligible for authorization, not automatically evidence corruption.

## 9. Exact NEW HOLD −1 result

The primary test executed before the broader campaign: HOLD, ADVANCE, RETREAT, changed HOLD, changed ADVANCE, from state 1 and epoch 1001. Transaction 4 held state 1: prediction +1, authentic receipt −1, authorized Memory −1. The old transaction-1 HOLD +1 record remained byte-for-byte equal. No model call, prediction rewrite or protected false accept. Because next state stayed 1, ordinary incumbent retention sufficed; no Recovery was needed for this HOLD.

## 10. NEW ADVANCE +1 result

Transaction 5 executed state-1 ADVANCE: prediction −1, authentic receipt +1, authorized Memory +1, next state 2. The earlier transaction-2 ADVANCE −1 record remained unchanged. Ordinary bounded Recovery corrected the proposed Map state after the prediction mismatch. Recovery did not alter the receipt or consequence.

## 11. Old-history preservation

After the primary five transactions, authorized state-1 histories are HOLD `[+1, −1]` and ADVANCE `[−1, +1]`. Navigation also remains in Memory. Both old and new observations have their own execution identities. No records were overwritten, action bans created, or allowed actions removed. Separate rotation tests exercise the existing eight-slot eviction rule; indefinite historical retention is not claimed. Detailed evidence checks retained records against their earlier values.

## 12. Stale receipt attack

An authentic earlier receipt, retained by the test driver after its transaction, was submitted for the new transaction. It failed exact identity against the current protected pending root. No commit or continuation grant; published state unchanged.

## 13. Wrong transaction, epoch, state and action

Four package attacks changed these fields while keeping the authentic root. All rejected. Four additional execution-mismatch cases emitted authentic receipts for a different transaction, epoch, pre-state or action than the pending proposal. Those rejected at the execution-identity check. This separately exercises candidate content binding and actual receipt-to-proposal identity, rather than relying only on malformed receipts.

## 14. Wrong consequence

A/B were made to agree on the old +1 consequence for the correct transaction while the authentic receipt said −1. Full receipt binding rejected the package. No Memory append or Map/pair/package publication occurred. A wrong-next-state package also rejected.

## 15. Wrong event ID and source identity

Correct event content with an altered event ID rejected; so did an altered source identity. An independently constructed, exactly equal receipt also rejected because value equality did not confer authentic origin. The tested event IDs remained unique across both bounded epochs.

## 16. Map-derived fake event

The attack constructed a receipt-shaped object containing the latched Map expectation +1. It was not the authentic −1 object in the external pending slot and could not authorize. The test injects a fake candidate payload; it does not grant Map an execution capability.

## 17. Recovery-derived fake event

A simulated Recovery proposal carried the desired/expected +1 as if realized. Its receipt-shaped payload likewise lacked external origin and rejected. The unchanged Recovery implementation itself does not mint receipts. An additional downstream failed state-Recovery case also rejected atomically after valid receipt checks.

## 18. Replacement/substitution attack

After authentic capture, a receipt from a different legitimate external source lifetime was substituted. Although authentic to its own source, it was not this transaction's protected root and rejected. A separate unit test swapped the root during staged processing using a test-only external-driver capability; the final identity check discarded the staged commit. No protected publication or continuation grant occurred.

## 19. Shared-descendant negative control

A/B both received the same Map-derived fake event and agreed. Authorization still rejected because they did not descend from the authentic pending receipt. This is the direct control for the historical failure mode: agreement alone cannot establish grounding.

## 20. Root-corruption out-of-model control

**OUT-OF-MODEL ROOT FAILURE: 1/1 wrong acceptance.** The trusted emitter deliberately turned the actual changed HOLD −1 into an authentic receipt saying +1. Downstream authorization accepted +1. An external audit, separate from authority, observed the wrong actual-world result. The committed value matched the corrupted root, so this is not a protected receipt-mismatch acceptance. Three earlier clean warmup events preceded this control. This explicitly demonstrates where verification stops; no extra verifier was added to hide the limitation.

## 21. Atomicity

All 20 campaign attacks had `commit_delta=0`, identical before/after published Map, Map quarantine, Memory, Memory quarantine, pair and package state, and no continuation grant. Checks precede publication; the original core runs on a staged deep copy. Rejection may update bounded control diagnostics and reject status, not protected history. The failed-Recovery attack exercises discarding a staged Map quarantine. Six additional boundary tests include a post-check root substitution and wrong Measure repair.

## 22. Boundedness and counting

The source retains one pending receipt; the authorized provenance ring, Memory and pairs remain bounded at eight each. The campaign exercised 24 executions over two epochs, 16 synchronized evictions and 24 distinct event IDs. The attempted 25th source execution rejected. Observed Memory/pair/package maxima were 8/8/8; trace maximum was 24. Existing quarantine, Recovery and authorization limits remain.

The 105 protected clean authorizations comprise five primary, 12 stationary, 24 rotation, three Memory-causality and 61 attack-setup transactions. Twenty protected attack submissions are counted separately, including one before execution. The out-of-model fixture has three clean warmups and one corrupted-root event. These are deterministic cases, not an empirical failure-rate estimate. Detailed finite logs remain outside the public tree; the framework has no unbounded event archive. Final accounting includes attack setup rows that were omitted from the preliminary compact denominator; all preliminary evidence is retained privately and no outcome changed.

## 23. Measure behavior

Historical Measure now receives receipt-grounded content through the new layer rather than a stationary reconstruction. Both changed events preserve prediction disagreement. A unit test corrupts the measurement and confirms bounded correction restores `matches=false` while leaving receipt −1 unchanged. A deliberately wrong measurement repair rejects without publication. Historical Measure source is unchanged.

## 24. Recovery behavior

Changed HOLD retained the valid incumbent; changed ADVANCE used ordinary bounded state Recovery to reach state 2. A failed state correction rejected and left the prior published Map intact. Recovery-derived event forgery and wrong Measure repair rejected. Historical Memory repair remains available only from a receipt-bound retained pair. Recovery proposals never supply realized-event authority.

## 25. Memory causality

The new receipt-path test used actual authorized HOLD +1, ADVANCE −1 and navigation records. At the same state 1, deterministic Explorer chose HOLD with that history versus ADVANCE with empty history. All three actions remained allowed. Historical minimum-repair causality cases for v0/v1/v2 also passed unchanged. This shows the registered deterministic dependence on Memory, not model causal inference or model contradiction revision. A separate unit test verified bounded Memory correction preserved the original receipt/history; jointly corrupting retained pair and Memory could not redefine the receipt.

## 26. Stationary regressions

All **12/12** state/action combinations authorized the actual old-regime next states and consequences through the new receipt path, with correct matching measurements. Each starts a fresh bounded system. No historical evidence was edited or reinterpreted.

## 27. Historical regressions actually executed

All commands were run after implementation; exact commands, UTC execution times, expected/actual exit codes and private-log hashes are in `verification.json`.

| Regression | Actual result |
|---|---|
| Old contradiction diagnostic | Expected exit 2; still one false accept; both evidence files byte-identical to the old checkpoint |
| Old contradiction unit tests | 3/3 passed |
| Minimum framework repair 1 | 177 runs; 126/126 protected passes; 0 protected violations; 15 ablation and 6 boundary violation runs retained |
| Base framework v0 | 12 tests / 42 scenarios passed |
| Base framework v1 | 10 tests / 69 scenarios passed; three out-of-model common-mode false accepts retained |
| Base framework v2 | 13 tests / 57 scenarios passed; 12 A+B blocks; three A+B+C and three registry false accepts retained |
| Original Explorer integration | Recorded-response replay passed; 69 original model responses plus existing synthetic controls |
| Memory Study v1 | 224 recorded responses replayed; transcript and summary unchanged |
| Adaptive Explorer v0 | 288 recorded responses replayed; transcript and summary unchanged |
| Semantic-prior v0 | 288 recorded responses replayed; transcript and summary unchanged |
| Prior-factorial v1 | 216 recorded responses replayed; transcript and summary unchanged |
| New boundary unit tests | 6/6 passed |

All five model transcripts and summaries matched their preserved evidence. The 1,085 recorded original model responses are replay inputs, not new inference. Historical negative findings remain visible.

## 28. Exact replay and evidence

The final new `campaign.json` and compact `results.json` regenerated byte-for-byte under exact replay. Source/evidence SHA-256 values are public; detailed bounded transaction/root/attack/publication rows and regression logs are retained separately. Public reproduction uses only standard-library Python and no private inputs for the new deterministic campaign. Prior Semantic/Factorial replays require their separately retained historical transcripts. The six new unit tests and campaign independently use zero model transport.

## 29. Trust roots and remaining limits

Trusted: external event-source authenticity, source-lifetime identity, pending receipt integrity, read-port wiring and the staged coordinator's execution under the declared software fault model. Not solved: physically wrong sensors, physical common mode, malicious external root, hostile same-process introspection/mutation, concurrent races, arbitrary world truth, general causal independence, general nonstationarity adaptation or unbounded history. A read-only Python interface is not an operating-system isolation guarantee. The root-corruption control makes this limitation observable.

## 30. Narrowest defensible conclusion

Horus can bind authorization to a candidate-unwritable realized-event receipt and preserve newly verified consequences even when they contradict prior predictions/history, within the declared software trust root. This is supported by the repaired HOLD/ADVANCE cases, stationary coverage, identity/content/provenance attacks, atomicity, bounded rotation and preserved historical regressions. It does not establish physical grounding, universal truth, model adaptation, causal inference, AGI or RSI.

## 31. Recommendation

Accept **A** for this bounded repair scope. Stop here. The next research decision is whether to rerun the complete contradiction feasibility gate through this new path before considering the registered model-revision study. The five-transaction primary repair test is not represented as the full old CONTROL/SHIFT model-study preflight. No 144-call inference campaign was run or scheduled. Main, tags and historical checkpoints remain unchanged; nothing was pushed.
