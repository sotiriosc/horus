# Map-guided Explorer interface v0 — results

**A — MAP-GUIDED EXPLORER INTERFACE READY**. **Zero model calls.** All 18 invariants and 82 deterministic cases passed; exact replay, 75 tests and ten historical replays passed.

| Synthetic control | Cases | Result |
| --- | --- | --- |
| CONTROL | 12 | HOLD proposal; no authority |
| CHANGED | 12 | RETREAT proposal; no authority |
| Wrong Map | 12 | Wrong HOLD forecast admitted; no truth repair |
| Invalid Map, all mappings | 12 | Stopped before Explorer |
| Empty history | 12 | Finite forecasts admitted; Memory stays empty |
| Additional boundary/freshness | 22 | Registered stops/acceptances passed |

## 1. Parent explicit-mean negative

Parent `research/explorer-value-aggregation-contract-v0`, `6448aaca17bdc748f468a93e72a355bdb5331450`, remains **EXPLICIT-MEAN EXPLORER POLICY NOT ESTABLISHED** in both families: CHANGED B RETREAT 4/12 O1, 2/12 O2, favorable pairs 2/12 each; CONTROL B HOLD 12/12 each. The earlier stale-Memory Explorer negative also remains unchanged. Registration for this separate zero-call interface is `d07a377c40224fe21e9698791cf1dfb7730a10e8`.

## 2. Role-separation motivation

Map stale-Memory revision remains REPLICATED in its bounded fixture; neither Explorer negative is repaired or reinterpreted here. This motivates separating history interpretation from forecast-based action choice. A prior Map result is not evidence that all-action forecasts or a composed model pipeline will work behaviorally.

## 3. Exact research question

Can a bounded interface pass finite parsed current Map estimates for every legal action into Explorer without converting estimates into historical fact or authority? This phase tests only architectural binding using deterministic synthetic sources. **Zero real model calls.**

## 4. New forecast type/schema

A frozen CurrentActionForecast retains action_alias, underlying_action, proposal_id, epoch, state, decision_id, Memory SHA-256, full authenticated snapshot SHA-256, Map-input SHA-256 and parsed Prediction. ExplorerProposal retains the selected forecast and detached action identity. Neither is a MemoryRecord or RealizedEventReceipt; neither carries an authorization grant or writer capability.

## 5. Memory versus Map proposal distinction

Memory remains authenticated realized events. Map supplies a fallible Prediction and the view labels it map_prediction, never verified_outcomes. Synthetic type checks reject a proposal as an external receipt. Nothing inserts a forecast into Memory or manufactures a receipt. The prospective Prediction transaction ID is binding metadata, not an executed event.

## 6. All-action forecast collection

For each fresh decision independently collect ADVANCE, HOLD and RETREAT in canonical underlying order. Each source receives the corresponding epoch-visible exact-pair history from audited Memory. No unqueried action is inferred from another forecast. Exactly three parsed forecasts are required before Explorer can be invoked.

## 7. Map parser boundary

The historical strict Map parser is imported unchanged: exact next_state/consequence JSON fields, exact integers, next_state 0..3 and consequence −1/0/+1. Reject extra fields, booleans, malformed and missing text. Only parsed finite Prediction values enter the collector. Raw strings and exception/parser text never enter Explorer; failures expose bounded codes.

## 8. Explorer forecast view

Detached schema:

```json
{"state":1,"actions":[{"action":"K1","map_prediction":{"next_state":2,"consequence":-1}},{"action":"K2","map_prediction":{"next_state":1,"consequence":1}},{"action":"K3","map_prediction":{"next_state":0,"consequence":0}}]}
```

Rows follow the frozen opaque mapping order. This example uses the first O1 mapping. No raw history arrays, source capabilities, epochs, transcripts, parser errors or evaluator truth appear. Mutating a detached view does not alter retained forecasts or framework state.

## 9. Proposal provenance

Internal records bind the current authorized state/epoch, decision, prospective transaction, alias/action identity, Map proposal identity, exact Map-input hash and authenticated Memory/snapshot hashes. The reader verifies original receipt-object and actual-event bindings before constructing input. These are trusted audit bindings, not self-certification by model text or cryptographic proof.

## 10. Wrong-Map admissibility

A finite forecast is not checked against future hidden reality. In all twelve wrong-Map controls, authenticated CHANGED HOLD history is [+1,−1,−1], but synthetic Map still predicts HOLD +1. The binding accepts it and synthetic Explorer proposes HOLD. No oracle repairs it, no Memory changes, and no authorization occurs.

## 11. Invalid-Map fail-closed behavior

Malformed, parser-rejected and missing outputs stop immediately at each tested action position. Missing collected entries also stop. No Explorer invocation, partial-action view, implicit zero value, stale fallback, extraction or retry. Subsequent attempts on the failed session cannot restart collection. Source exceptions become bounded MAP_SOURCE_FAILURE without forwarding error text.

## 12. Freshness semantics

A coordinator has one active decision and no cross-event forecast cache. Check authenticated snapshot equality before and after each source call and before view/choice/proposal validation. New decision invalidates the old session; new Memory at unchanged state, changed state and changed epoch invalidate old forecasts. Cross-decision copied forecasts fail identity checks. A fresh decision must recollect all three actions. A later trusted execution driver must recheck freshness immediately before ordinary execution; this phase adds no executor.

## 13. UNKNOWN semantics

Existing Map projection remains [] for zero retained authenticated exact-pair observations and chronological authenticated rows otherwise. All twelve empty-Memory controls successfully admit finite synthetic forecasts from [] without inventing observations. No UNTRIED value is passed as a forecast. Absence of history differs from missing/invalid forecast; Memory stays empty throughout the proposal stage.

## 14. CONTROL fixture

Across all twelve mappings, synthetic forecasts are HOLD (1,+1), RETREAT (0,0), ADVANCE (2,−1). Synthetic Explorer returns the corresponding HOLD alias. Each case has three synthetic Map invocations and one synthetic Explorer invocation, zero model calls and no protected-state change.

## 15. CHANGED fixture

Across all twelve mappings, forecasts are HOLD (1,−1), RETREAT (0,0), ADVANCE (2,−1). Synthetic Explorer returns RETREAT. This demonstrates correct deterministic wiring, not a measured improvement in model behavior.

## 16. Wrong-Map fixture

All twelve deliberately wrong Map fixtures propose HOLD despite the changed external HOLD consequence −1 and authenticated negative history. The wrong finite forecast remains unchanged. Hidden-world execution is trapped during the proposal pipeline; zero external execution, Measure, Recovery and package-admission calls occur in that stage.

## 17. Invalid-Map fixture

Twelve mapping controls reject an invalid HOLD prediction. Nine additional cases cover malformed/extra-field/missing outputs at all three collection positions. Stops occur after one, two or three synthetic Map attempts respectively; Explorer calls remain zero. Additional controls reject ties, missing entries, substituted/aliased forecasts, invalid Explorer text and duplicate invocation. A valid but nonmaximum Explorer proposal remains admissible and non-authoritative.

## 18. Alias/order audit

Collection order is ADVANCE→HOLD→RETREAT independent of mapping. Rendering order is O1 K1/K2/K3 or O2 Q7/M4/Z2, using all six complete permutations per family. Source target aliases, parsed Prediction.action and forecast alias/action bindings are audited mechanically. Neither list position nor output text overrides the trusted mapping.

## 19. Model-to-model boundary

No real model instance is used here. Synthetic sources receive only immutable system/prompt strings. Explorer receives a new finite view, not raw Map responses, explanations, returned context, transcripts, parser errors or chain-of-thought. Shared future model weights would confer no authority. Future live transports must independently enforce stateless requests; provider-side behavior is not tested here.

## 20. Future call semantics

One eligible future decision requires three Map proposals plus one Explorer proposal, with no retries/replacements. An invalid Map response stops the remaining proposal flow before Explorer. v0 primary contexts require a unique predicted maximum; a tie yields TIED_MAXIMUM and zero Explorer calls. Stored future system instruction (never sent to a model here):

> Choose the allowed action whose current Map prediction has the highest predicted consequence. Reply with exactly one allowed action and no explanation.

A later campaign must preregister its contexts, invalid/tied-decision accounting and exact real-call budget before inference.

## 21. Measure placement

Measure remains downstream of real execution and its authentic receipt. The new interface never calls Measure to screen or repair forecasts before Explorer. Existing Measure implementation and authority code are byte-identical to the parent. Historical actual-execution regressions pass; proposal-stage profiling shows zero Measure calls.

## 22. Recovery placement

Recovery remains downstream of ordinary executed evidence. It does not repair missing, invalid or wrong forecasts before choice and never selects actions here. Existing Recovery is unchanged; proposal-stage profiling shows zero calls. Deterministic setup and intentional freshness events retain ordinary native behavior.

## 23. Authority audit

ExplorerProposal has no execution, receipt-minting, Memory-writing or authorization method. Selecting the maximum prediction produces only an action proposal, including when the prediction is wrong. Receipt creation/admission remains governed by existing non-model authority. Passing the proposal as a receipt fails. No protected-state mutation or authority transfer occurred in registered proposal stages.

## 24. Memory preservation

Full protected snapshots before/after every primary proposal pipeline are identical. All eight P2 historical events remain present with unchanged receipts; empty-history cases remain empty. Freshness controls deliberately realize an ordinary event or reset between stages, then prove the old forecast is rejected without further mutation. Those deterministic fixture events are not model-selected execution.

## 25. Exact replay

All 82 registered synthetic cases passed. Reconstructed authenticated fixtures and repeated deterministic sources with sockets forbidden; results.json and details.json are byte-identical between campaign and replay. Independent audit verified finite values, action/proposal identities, snapshot hashes, wrong-Map admissibility, absent-history behavior, zero stage effects and stale rejection. Raw provisional C results are retained unchanged; final replay/preservation gates are applied only after their checks pass.

## 26. Historical regressions

Eight focused interface tests and 67 historical tests passed (75 total). Ten historical zero-inference replays passed: explicit-mean contract, Explorer revision, Map revision, feasibility, depth, transfer, initialization, ablation, R1 and realized-event grounding. All 596 inherited substantive files are byte-identical, and eleven prior evidence archive inventories passed checksum verification. Both Explorer negatives, Map REPLICATED, historical Explorer transfer SUPPORTED, UNKNOWN, representation, grounding/contradiction and authority checkpoints remain unchanged. Main/tags/prior refs remain untouched. [Verification](../experiments/map_guided_explorer_interface_v0/verification.json) records actual executions and hashes.

## 27. Limitations

Trusted single-process Python prototype; not hostile-code isolation, cryptographic provenance, concurrent-device rollback or a complete execution adapter. The interface is read-only and ends at a detached action proposal. A future driver must bind the selected forecast into ordinary prediction/execution flow and recheck freshness without bypassing receipt/Measure/authorization. No live role transport, all-action Map accuracy, Explorer behavior, model coordination, long-horizon adaptation or composed performance was tested. Ties stop and require explicit future accounting. Trusted source/registry/reset remain the existing authority boundary.

## 28. Classification

**A — MAP-GUIDED EXPLORER INTERFACE READY**

| Required invariant | Passed |
| --- | --- |
| forecast_distinct_from_Memory | yes |
| no_raw_cross_role_text | yes |
| finite_action_identity | yes |
| all_legal_actions_required | yes |
| invalid_missing_fail_closed | yes |
| no_automatic_retry | yes |
| freshness_bound | yes |
| Explorer_has_no_authority | yes |
| wrong_Map_admitted | yes |
| no_hidden_truth_repair | yes |
| UNKNOWN_unchanged | yes |
| Memory_unchanged | yes |
| Measure_post_execution | yes |
| Recovery_post_execution | yes |
| receipt_authority_unchanged | yes |
| historical_APIs_results_unchanged | yes |
| exact_replay | yes |
| historical_regressions | yes |

All eighteen invariants and all 82 registered deterministic cases passed. No B boundary failure or missing C requirement remains within this interface scope. ZERO MODEL CALLS.

## 29. Narrowest defensible conclusion

A bounded interface can pass finite parsed current Map predictions for all legal actions into Explorer without converting those predictions into authenticated truth or authority. This is an architectural binding result. It establishes no Explorer behavioral improvement, adaptation, policy learning, model coordination, persistent learning, AGI or RSI.

## 30. Recommendation

Stop here, even though classification A passed. No live Map→Explorer study, prompt tuning, extra negative observation, historical-adapter replacement or Memory summarization is launched. The separate future question is whether real all-action Map forecasts enable Explorer to choose reliably between current estimates; this phase does not answer it.
