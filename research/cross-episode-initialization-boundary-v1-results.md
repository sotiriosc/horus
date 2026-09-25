# Cross-episode initialization boundary v1 — results

**A — CROSS-EPISODE INITIALIZATION BOUNDARY COMPLETE. ZERO MODEL CALLS.**

A trusted staged operation reset external/current state from 3 to 0 while retaining four authenticated prior events. All 18 frozen requirements, exact replay and historical checks passed. Atomicity is bounded to the in-process simulator.

## 1. Parent boundary-v0 C

Parent `b2306c917cfd8cdfc89d272e8f72fa1f01927605`, `research/cross-episode-authenticated-memory-boundary-v0`. Its **C — NOT ESTABLISHED** result remains unchanged. New branch: `research/cross-episode-initialization-boundary-v1`. The protocol and sources were committed before execution in `7829158`; [preregistration](cross-episode-initialization-boundary-v1-preregistration.md).

## 2. Demonstrated missing operation

The old start_epoch retained authenticated rings but preserved current world/Map state. Fresh construction initialized at 0 but discarded history. The old natural-return-to-zero fixture did not prove a fresh-state reset. This separate extension supplies the missing trusted initialization operation without changing the old implementation or its C result.

## 3. Exact research question

Can we reset the present without resetting the past? Specifically: can a trusted episode boundary initialize both external and authorized current state while retaining bounded authenticated history, provenance, epoch identity and ordinary authority semantics? This is architecture/semantics verification, not a model-performance study.

## 4. Same-source-lifetime decision

One unchanged ExternalExecutionBoundary object/lifetime spans registered epochs **1001→1002**. A stable execution-only route resolves the currently published simulation world. Source event IDs continue; the pending slot must be empty before initialization. No cross-source import or fresh-framework history transplant is implemented. Historical source identity remains the original lifetime string.

## 5. Minimal implementation

Two separate production modules: [boundary.py](../experiments/cross_episode_initialization_boundary_v1/boundary.py) adds EpisodePlan, a staged simulation initializer and trusted EpisodeController; [projection.py](../experiments/cross_episode_initialization_boundary_v1/projection.py) adds epoch to cross-episode Map history. The controller uses the unchanged StatusBoundFramework and ExternalExecutionBoundary. All old receipt, Measure, Recovery, authorizer, eviction and projection files remain byte-identical. Campaign/test/replay modules are evidence support. No new truth verifier or transition law.

## 6. Trusted initialization authority

`EpisodeController.start_episode(new_epoch, initial_state)` is a first-class driver-only operation. An immutable registered plan fixes start state and epochs; the primary plan is state 0 and 1001→1002. Supplied state must match that plan. Models receive detached projection values only, never the controller, source, world, framework or reset operation. Existing action domains contain no reset action. No model output requests or parameterizes initialization.

## 7. Preconditions

Require exact built-in integer state in {0,1,2,3}, exact integer epoch, registered state/schedule, unchanged owned source object, empty pending external receipt, no in-flight transaction, legal continuation, valid current Map, empty quarantines, matching pre-boundary world/current state, retained provenance passing the existing audit and matching source lifetime. Existing epoch/instance bounds run on the staged core. Any failure rejects before publication; invalid detached/corrupt history is not silently repaired during reset.

## 8. Atomic external/authorized reset

The controller owns a single `Publication(world, framework)` reference. It stages a shallow framework wrapper with a deep-copied core and copied package list preserving historical package objects. It invokes unchanged start_epoch on that staged core and creates its registered-state Map. It separately deep-copies the simulation world, then invokes the trusted initializer only on the unpublished world copy.

After state/history checks, one reference assignment publishes world and framework together under the controller lock. There is no world assignment followed by a separate Map assignment, and no callback or I/O at the commit point. Coherent public snapshots use the same lock; four preparation-time observations all saw the old complete publication.

Pre-publication exceptions discard staged state. The old source and publication remain unchanged. This is an in-process copy-stageable simulator guarantee, **not** a physical-device reset transaction, distributed rollback, durable crash recovery or hostile same-process guarantee. After a successful publication, no rollback is claimed.

## 9. Reset is not experience

The boundary created **zero realized events, receipts, Memory observations, pairs and packages**. Event/execution counters stayed 4. Instrumentation observed zero calls to external execution, package admission, Measure and Recovery during initialization. It returned boundary metadata only; no RESET/INITIALIZE/START observation entered historical rings. The last actual external event also remained unchanged.

## 10. History preservation

All four epoch-1001 Memory records, pairs, packages, bound predictions, measurement status, identities, pre/next states and consequences were content-identical across initialization. Historical package and receipt objects retained exact identity. The core is staged by copy, not re-created through a fresh framework constructor. No prior event was relabeled epoch 1002 or rewritten to end at 0. Old records remained unchanged through the next four commits and left only through ordinary FIFO eviction.

## 11. Epoch/transaction identity

Primary epochs are 1001 and 1002. Transactions restart at 1 under the inherited epoch operation. Full event/package identity remains `(source_identity, event_id, epoch, transaction_id)`. Pair/observation identities retain the existing epoch/transaction construction. New current-state initialization does not alter any historical identity. The new boundary enforces the registered schedule in addition to inherited epoch checks.

## 12. Source event continuity

The identical source object issued event IDs **1…9**. IDs 1–4 precede initialization; 5–8 are the first four later events; 9 is the ordinary eviction test. Initialization changed neither source counter nor pending root slot. The simulation execution count is preserved in the staged copy and remains aligned with source executions. No second lifetime is treated as the first.

## 13. Authorizer reset

The staged inherited start_epoch clears prior authorization keys, restarts transaction and step counters, and retains the repaired `StatusBoundAuthorizer` type. Four epoch-1001 keys became zero at initialization; four later commits populated four epoch-1002 keys, then the ninth total event populated a fifth. Old/current copied/wrong-epoch/duplicate receipts were rejected. Separate controls confirmed the existing duplicate rejection and 24-key per-epoch capacity. History does not reauthorize an old event.

## 14. Current-state semantics

Primary transition:

| Property | Before | After initialization |
|---|---:|---:|
| External current state | 3 | 0 |
| Authorized Map current state | 3 | 0 |
| Map epoch | 1001 | 1002 |
| Map version | 4 | 0 |
| Last historical next_state | 3 | 3 |
| Memory / pairs / packages | 4 each | 4 each |
| Source event / world execution count | 4 | 4 |
| Next transaction ID | 5 | 1 |
| Current epoch step count | 4 | 0 |
| Authorization keys | 4 | 0 |

Current state is explicit trusted initialization state, not inferred from the last event. No corrective/recovery event was triggered by this difference.

## 15. UNKNOWN across reset

At fresh state 0, retained HOLD and ADVANCE evidence stayed visible; untouched state-0 RETREAT remained UNTRIED / []. Episode initialization did not erase known evidence. The existing rule remains zero currently retained matching authorized observations → absence projection only. No absence marker became a receipt, package or Memory fact. After ordinary eviction, visibility continues to depend on the retained set, not an unbounded claim of never having experienced an action.

## 16. Map epoch-visible history

The separate projection contains exactly `epoch`, `transaction_id`, `surface_action`, `next_state`, `consequence` per matching historical record, sorted by `(epoch, transaction_id)`. It exposes no source capability, receipt object, package ID or authorizer information. Epoch identifies history; it is not a regime or outcome label. Removing only epoch reproduces the unchanged historical Map projection exactly in the mixed-epoch checks. No old prompt, parser or adapter was retrofitted.

## 17. Explorer retained history

Explorer retains the existing consequence-list schema and chronological ordering; epoch was not added merely for symmetry. Immediately after initialization at 0: ADVANCE has **[1]**, HOLD **[0]**, RETREAT **UNTRIED**. After the next four events: ADVANCE **[1,1]**, HOLD **[0,0,0]**, RETREAT still UNTRIED. Explorer reads current state 0, while history still includes the old final transition to 3. No Explorer model call occurred.

## 18. Mandatory nonzero-state reset test

Four authenticated old events deliberately ended at state **3**. The registered initializer then set external and authorized current state to **0**. This is not a natural return to 0 and is not test code manually assigning state. The trusted operation owns staging and synchronization. The next proposal/prediction and authenticated receipt used pre-state 0 and epoch 1002.

## 19. Complete two-episode fixture

Completed **4 old + 4 new authenticated commits** across the explicit boundary, followed separately by a ninth ordinary commit. Prior history survived a genuine nonzero-to-zero initialization. Existing deterministic framework sources and external receipt admission were used throughout; zero inference. Detailed before/after snapshots, receipt bindings, projections, boundary metadata and negative controls remain in private deterministic evidence.

## 20. Episode-1 history

Epoch 1001, initial state 0:

| Transaction / event | Action | Pre → next | Consequence |
|---|---|---|---:|
| 1 / 1 | HOLD | 0 → 0 | 0 |
| 2 / 2 | ADVANCE | 0 → 1 | 1 |
| 3 / 3 | ADVANCE | 1 → 2 | -1 |
| 4 / 4 | ADVANCE | 2 → 3 | 1 |

The final prior record remains next_state 3 after initialization.

## 21. Boundary delta

Called `start_episode(1002,0)`. World/current state 3→0; Map version 4→0; epoch 1001→1002; counters restart as registered. Historical rings, source event count, execution count and last actual event remain unchanged. No protected transition event represents initialization. Boundary observer counts: external_execute 0, package_admission 0, measure 0, recovery 0.

## 22. Episode-2 history

Epoch 1002:

| Transaction / event | Action | Pre → next | Consequence |
|---|---|---|---:|
| 1 / 5 | HOLD | 0 → 0 | 0 |
| 2 / 6 | ADVANCE | 0 → 1 | 1 |
| 3 / 7 | RETREAT | 1 → 0 | 0 |
| 4 / 8 | HOLD | 0 → 0 | 0 |

All four append through ordinary authenticated publication. The older four remain unchanged. Event 5 proves the fresh current-state binding against the continuing external source.

## 23. Cross-epoch chronology

State-0 HOLD projects **(1001,1), (1002,1), (1002,4)** before the ninth commit. Repeated transaction ID 1 is distinguishable through the new epoch field. Reversing the input Memory iteration produced identical serialized output for every action. No averaging, pseudo-summary, historical replacement or inserted absence marker.

## 24. Contradiction representation

A **separate authenticated representation control** reuses the existing Map established-prior v1 `HoldWorld` and its already-registered switch-after-event-2 rule. It reconstructs old outcomes **[1,1,-1] before initialization** at state 1, then initializes epoch 1002 at registered state 1 and commits a further -1. The projection preserves **(1001,1,+1), (1001,2,+1), (1001,3,-1), (1002,1,-1)** with full receipt provenance. No epoch or receipt was relabeled, and initialization neither causes nor adjudicates the earlier switch.

This control deliberately reuses an available historical nonstationary fixture solely to test representation. The **primary fixture remains stationary** across initialization. No new regime law, model response or nonstationary-transfer claim is introduced.

## 25. Bounds

Unchanged bounds: Memory/pairs/packages 8, pending authentic receipt 1, trace 24, epochs per instance 2, core decisions per epoch 12, authorizations per epoch 24, external executions per source lifetime 24. Primary rings reached eight and remained eight after event nine. Third-epoch initialization failed atomically. Source event IDs continue rather than receiving a fresh lifetime budget.

## 26. Ninth-event eviction

Epoch 1002 / transaction 5 / source event 9 was HOLD at 0. Existing FIFO removed exactly **epoch 1001 / transaction 1 / pair 4299262263552**, together with its event-1 package and matching pair. All three rings retained prior entries 2–8 then appended event 9. Eviction count became one; no episode-aware exemption or preference.

## 27. Failure atomicity

**24/24** failure cases rejected with identical published snapshot, unchanged joint publication object and unchanged pending receipt object. Failures after staged world or authorized-state mutation left the old publication intact. Wrong prepared states were also rejected. Four observations during preparation saw only the old joint state.

| Failure case | Observed rejection | Atomic |
|---|---|---|
| pending_receipt | pending external receipt | PASS |
| pending_transaction | in-flight transaction | PASS |
| same_epoch | epoch must change | PASS |
| third_epoch | epoch bound exceeded | PASS |
| bool_state | initial_state must be an exact finite int | PASS |
| float_state | initial_state must be an exact finite int | PASS |
| string_state | initial_state must be an exact finite int | PASS |
| negative_state | initial_state must be an exact finite int | PASS |
| high_state | initial_state must be an exact finite int | PASS |
| unregistered_state | state differs from registered plan | PASS |
| bool_epoch | epoch must be an exact int | PASS |
| float_epoch | epoch must be an exact int | PASS |
| unregistered_epoch | epoch differs from registered plan | PASS |
| detached_pairs | receipt/pair/Memory ring length | PASS |
| detached_packages | receipt/pair/Memory ring length | PASS |
| corrupt_record | retained receipt/Memory binding | PASS |
| illegal_continuation | illegal prior continuation state | PASS |
| source_lifetime_changed | source lifetime changed | PASS |
| external_before | injected external preparation failure | PASS |
| external_after | injected external failure after staged reset | PASS |
| external_wrong | external reset preparation invalid | PASS |
| authorized_before | injected authorized preparation failure | PASS |
| authorized_after | injected authorized failure after staged reset | PASS |
| authorized_wrong | authorized reset preparation invalid | PASS |


## 28. Provenance audit

Every retained Memory/pair/package passed the unchanged framework audit and the diagnostic exact-original-receipt-object check. An independent saved-evidence audit checked all nine primary receipts, record/pair content and full package identities. Corrupt/detached retained history prevented reset. Packages preserve original predictions and measurement status. JSON replay reconstructs and rechecks in-process object identity; serialized data itself is not a receipt capability.

## 29. Identity-collision audit

Nine primary full receipt/package identities and pair IDs were distinct. Transaction IDs may repeat only with different registered epochs; source event IDs never repeat within the tested lifetime. New model-visible `(epoch,transaction_id)` pairs distinguish matching observations under the frozen same-source interpretation. No cross-source import, arbitrary epoch reuse or source-lifetime merging is supported. Driver-provided lifetime identity remains trusted, as before.

## 30. Historical equivalence

All **513 inherited substantive public files** remain byte-identical, including prior boundary-v0 C, ablation SUPPORTED, R1 A, all older results and authority components. Prior archived responses replay exactly. An independent route comparison also reproduced the four primary pre-boundary ordinary transactions through the unchanged historical direct framework/source path: protected publication and receipts matched byte-for-byte. Explorer projection is unchanged; removing epoch from the new Map projection recovers old output. No old API was patched.

## 31. Exact replay

Full deterministic campaign reconstruction passed with **results.json and details.json byte-identical**, including nonzero state, initialization, retained history, later commits, epoch-visible projections, contradictions, ninth-event eviction and every negative control. Both final compact results regenerated identically using the same actual verification evidence. Raw provisional files remain unchanged; only final assurance promotes the eligible classification after replay/regressions.

## 32. Regressions

Actual execution: **6 new tests and 49 inherited tests passed**. Six registered post-campaign commands passed: new replay, new tests, prior v0 C replay, 84-response ablation replay, 164-response R1 replay, and bounded inherited tests covering v0, composition bindings, status/Recovery, realized-event authority, UNKNOWN and both historical Map studies. Networking was denied.

Private checksum preservation: R1 **288** files, ablation **105**, prior v0 **82**. Prior branches, main and tags unchanged. Nothing pushed; no Ollama server or new model inference. [Verification](../experiments/cross_episode_initialization_boundary_v1/verification.json) records commands, counts and log hashes; the independent audit is included separately in that evidence.

## 33. Limitations

Bounded same-source software simulation and trusted controller APIs only. Atomicity covers preparation failures before one in-process publication; it does not provide physical-device synchronization, durable restart, distributed transactions or hostile Python-object isolation. Source authenticity and lifetime uniqueness retain the historical trusted-root assumptions. The copied simulation state is cheap/bounded here; no scalability claim. Epoch plan remains exactly 1001→1002 and the old two-epoch limit is unchanged. The separate historical SHIFT control supports representation, not nonstationary transfer. No model performance, persistent/lifelong learning, autonomous reset, cross-source Memory import, AGI or RSI result.

## 34. Classification

**A — CROSS-EPISODE INITIALIZATION BOUNDARY COMPLETE.** All 18 frozen requirements passed. Zero observed split publication, fake initialization events, rewritten history, provenance detachment, identity collision or anti-replay acceptance in the registered tests. Correctly rejected deliberate faults remain negative controls.

| Frozen requirement | Result |
|---|---|
| authorizer_reset_safe | PASS |
| bounds_unchanged | PASS |
| chronological_append | PASS |
| epoch_visible_Map_identity | PASS |
| exact_replay | PASS |
| explicit_new_epoch | PASS |
| external_authorized_synchronized | PASS |
| failure_atomicity | PASS |
| historical_regressions | PASS |
| history_rings_unchanged | PASS |
| identities_unique | PASS |
| known_pairs_not_UNKNOWN | PASS |
| no_model_reset_capability | PASS |
| nonzero_to_registered_state | PASS |
| ordinary_ninth_eviction | PASS |
| provenance_traceable | PASS |
| untouched_pairs_UNKNOWN | PASS |
| zero_realized_events_at_reset | PASS |


## 35. Narrowest defensible conclusion

The trusted episode-initialization boundary can start a fresh registered current state while preserving bounded authenticated historical evidence, provenance and ordinary authority semantics in the same-source stationary fixture. The present resets; the recorded past does not. **Zero model calls.**

## 36. Recommendation

Stop at this checkpoint. A later separate decision may consider a small stateless-model study beginning a genuinely fresh episode with retained authenticated experience and the new epoch-visible projection. This checkpoint does not authorize or start that campaign. Preserve the old v0 C alongside this new A; no rewrite, merge to main, tag change or push.
