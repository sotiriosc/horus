# Cross-episode authenticated Memory boundary v0 — results

**C — NOT ESTABLISHED. ZERO MODEL CALLS.**

The existing epoch operation preserves authenticated history but does not reset the world/current authorized state to a registered fresh start. This is a missing boundary capability, not evidence that history must be erased.

## 1. Parent identity

Parent `46d01e1e6d09a24191aea1ddf9e413f04711b14b`, branch `research/composition-map-memory-ablation-v0`. This separate zero-call checkpoint is `research/cross-episode-authenticated-memory-boundary-v0`; preregistration commit `6d94504`. No prior result or core implementation was changed. Main and tags unchanged; nothing pushed.

## 2. Causal Map-memory result motivating the study

The preceding paired ablation remains **AUTHENTIC-HISTORY MAP EFFECT SUPPORTED**: visible history 33/42 exact, withheld history 11/42 exact, 22 favorable and zero reverse exact discordances. That result concerns information visibility in matched inputs. It does not establish safe history retention across an episode boundary or persistent model learning.

## 3. Exact question

Can experience remain history after an episode ends, without confusing past evidence with current state, and without losing the provenance that made it authentic? Specifically: can a new episode initialize at registered state 0 while earlier authorized events remain available with valid provenance, chronology, identity, bounds and UNKNOWN semantics?

## 4. Current episode/reset implementation

The [composition setup](../experiments/model_proposal_role_composition_v2/runtime.py#L128) constructs a fresh `TestWorld(0, False)`, external source lifetime and `StatusBoundFramework(..., 0, 1001)` for each episode. Episode identity is driver metadata included in the source-lifetime name; the core has an epoch and episode-step counter, not a general episode-reset API. Fresh construction starts empty Memory/pairs/packages and fresh counters/authorizers.

The existing alternative is [start_epoch](../experiments/realized_event_grounding_v0/framework.py#L102), which audits retained provenance, rejects a pending external receipt, then delegates to the core. These two operations have different semantics.

| Component | Fresh construction | Existing start_epoch(E+1) |
|---|---|---|
| External world/source | New objects, world initialized by constructor | Same world/source, current state unchanged |
| Authorized Map | Registered initial state, version 0 | Prior current state, new epoch, version 0 |
| Memory, pairs, packages | Empty | Retained |
| Transaction / step counters | 1 / 0 | 1 / 0 |
| Source event counter | Starts at 0 | Continues |
| State-authorizer identities | Empty | Cleared; repaired authorizer type retained |
| Continuation | True | True after successful epoch transition |
| Memory quarantine, trace, metrics | Fresh | Retained |
| Map quarantine | Empty | Replaced with empty Map quarantine |

The core retains Explorer and any configured Recovery proposal source; it replaces Map. `_prediction_at_begin` remains until the next begin_step overwrites it. R1 normally rebuilds all role transports/bindings on every decision; no model binding was used here. This checkpoint does not establish a live cross-episode role-routing lifecycle.

## 5. World and current-state semantics

World state is the external oracle state; current authorized state is `inner.map.current.state`; historical event pre/next states live in immutable evidence records. They are separate concepts. In the nonzero probe, HOLD then ADVANCE ended at state **1**. start_epoch(1002) left both external and authorized state at **1**. A fresh constructor produced state **0** but empty history. Neither is the requested combination of independent fresh-state initialization plus retained authenticated evidence. No last event was rewritten.

## 6. Epoch semantics

[CrossSourceFramework.start_epoch](../experiments/base_framework_v1/framework.py#L368) requires a different epoch, fewer than two started epochs, and no pending transaction. It resets transaction ID to 1, episode_steps to 0, Map version to 0 and authorization identity state, and enables continuation. It retains current state and history. The implementation checks inequality, not monotonic increase; this study specifically freezes **1001 → 1002**. Same-epoch and third-epoch requests were rejected unchanged. Epochs alone are not a general episode initialization primitive. No epoch semantics changed.

## 7. Transaction and event identity semantics

Transaction IDs restart at 1 in epoch 1002. Source event IDs continue 1…9 across the same lifetime. Full receipt/package identity is `(source_identity, event_id, epoch, transaction_id)`. Pair ID is `(epoch << 32) | (transaction_id << 8) | channel_sequence`; adapter observation IDs use `(epoch << 24) | (transaction_id << 8) | port_offset`. Retained Memory identifies its pair by `(epoch, transaction_id, pair_decision_id)`, with both observation IDs and generic SOURCE_A/SOURCE_B names. Nine executed carryover events had distinct full event/package/pair identities in the registered bounded ranges.

## 8. Memory reset and retention behavior

Fresh construction initializes empty Memory. Existing start_epoch preserves records and their prior epochs, values, authorization, observation IDs and pair IDs. All four epoch-1001 records remained content-identical through the boundary and the next four commits. Only the ordinary ninth-event FIFO eviction removed an old record. Memory never stored an episode label, UNTRIED, [], reset event or averaged pseudo-observation.

## 9. Pair/package provenance requirements

A retained value alone is insufficient. The [receipt audit](../experiments/realized_event_grounding_v0/framework.py#L71) requires equal package/pair/Memory ring lengths, package identity matching the receipt, pair identity/content matching that receipt, measurement binding to the original prediction, and Memory matching its pair. Both rings survive the actual epoch transition. Throwaway controls that discarded only pairs or only packages were rejected by begin validation without protected partial publication. Such detached states were never used as a carryover design.

## 10. Receipt lifetime

During current admission, candidate receipt must be the exact object in the source’s single pending slot. Once committed, the authorized package retains that original receipt object as historical evidence. Ordinary release clears the pending slot, not the package. The four old receipt objects survived start_epoch by identity; later provenance audits still found those same objects. Pending count was one during execution/admission and zero after release. Historical audit relies on the trusted previously published package ring; it does not require old receipts to remain pending, and it is not a cryptographic persistence proof.

## 11. Source lifetime

Frozen interpretation: **one existing external source lifetime across E=1001 → E+1=1002**. It has no reset/import API; its pending slot is released normally and its event counter continues. The bound remains 24 executions per lifetime. Source identity is a trusted driver-supplied nonempty string; the constructor does not enforce global uniqueness. A separate new-lifetime diagnostic found distinct full receipt/package IDs but identical partial Memory/pair keys when epochs and transaction IDs restart identically. Those histories were not combined. New-lifetime carryover is not established.

## 12. Authorizer reset behavior

At the epoch boundary, four old authorization keys were replaced by an empty set in a new `StatusBoundAuthorizer`; its repaired RECOVERING status check remained intact. The subsequent four commits populated four epoch-1002 keys; the ninth total commit populated a fifth. Capacity is 24 per epoch, not an accumulated cross-epoch set. This reset is compatible with the registered new-epoch path because current admission still checks pending proposal, exact current receipt, epoch and transaction identity. Replaying an old receipt after the transition was rejected. This does not authorize bypassing the receipt wrapper or resetting IDs in an unchanged epoch.

## 13. UNKNOWN IS NOT MEMORY across the boundary

At state 0, earlier HOLD and ADVANCE observations remained visible after the epoch changed. RETREAT at state 0 remained UNTRIED / [] because no matching record existed; the RETREAT observation at state 1 did not contaminate that projection. No stale UNKNOWN coexisted with retained evidence. No marker entered protected state. Under bounded semantics, UNKNOWN refers to zero currently retained matching authorized observations; ordinary eviction can eventually remove all matching observations, but an episode label alone does not erase them.

## 14. Explorer cross-episode projection

Direct use of the unchanged Explorer projection after the boundary produced K1/ADVANCE verified outcomes **[1]**, K2/HOLD **[0,0]**, and K3/RETREAT **UNTRIED**, all at state 0. After four more events the observed outcomes became ADVANCE **[1,1]** and HOLD **[0,0,0,0]**, with RETREAT still UNTRIED. No Explorer model or chat was invoked.

## 15. Map cross-episode projection

The unchanged Map projection for state-0 HOLD preserved the two old records after the boundary; state-0 RETREAT had []. After episode-group 2, HOLD projected old then new observations. **Limitation:** sorting uses `(epoch, transaction_id)`, but the displayed Map record includes transaction_id, surface_action, next_state and consequence, omitting epoch/source/event identity. The visible IDs can therefore repeat. Protected provenance remains unambiguous in this registered mode, but the abbreviated payload cannot itself identify a historical event globally. No schema change was made.

## 16. Two-episode fixture

A limited same-source two-epoch continuity fixture completed **4 + 4 authenticated commits**, followed separately by a ninth commit. It starts both groups at 0 only because the first group naturally returns to 0 through authenticated actions. **The requested complete fresh-state-reset fixture was not established.** No manually assigned world state, imported rings, fabricated initialization record or direct Map.commit reset was used.

## 17. Episode-1 evidence

Epoch 1001, start 0:

| Transaction | Action | Pre → next | Consequence |
|---:|---|---|---:|
| 1 | HOLD | 0 → 0 | 0 |
| 2 | ADVANCE | 0 → 1 | 1 |
| 3 | RETREAT | 1 → 0 | 0 |
| 4 | HOLD | 0 → 0 | 0 |

All committed through ordinary proposal, external execution, receipt-bound admission and paired publication. The natural return to 0 is an actual event, not a boundary reset.

## 18. Boundary operation

Called the existing `system.start_epoch(1002)` after the fourth receipt had been released. No external execution occurred: execution count stayed 4, Memory/pairs/packages stayed length 4, source pending count stayed 0. Transaction counter changed 5→1; episode_steps 4→0; Map epoch 1001→1002 and version 4→0; four authorization keys became zero. World/current state stayed 0. The nonzero control demonstrates that this same operation would preserve 1 rather than initialize 0. Unsupported `initial_state=0` keyword was rejected; no replacement mechanism was implemented.

## 19. Episode-2 evidence

Epoch 1002 used HOLD, ADVANCE, RETREAT, HOLD with transaction IDs 1–4 and source event IDs 5–8. Those four authenticated events appended beside the four unchanged older records. World/current state followed 0→0→1→0→0. No episode-1 record was replaced, averaged, relabeled or declared false. This is epoch continuity, not an independently reset world.

## 20. Mixed chronology

State-0 HOLD order was **(1001,1), (1001,4), (1002,1), (1002,4)**. Reversing the supplied record list produced the identical serialized projection because the binding sorts by epoch then transaction ID. Sorting only by restarted transaction ID would mix the two groups; the existing binding did not do that. Protected full identities remained distinct even though displayed transaction IDs were [1,4,1,4].

## 21. Contradiction representation

Read an already-authenticated historical Map established-prior SHIFT setup: call index 2, step 3, same state/action HOLD at 1, consequences **[1,1,-1]**. Saved receipts/provenance and original identities were checked; the unchanged projection preserved both old and differing later outcomes. Earlier/later grouping was diagnostic metadata outside the records. No epoch, event or historical field was rewritten. **This is only a read-only representation control, not a newly authenticated cross-epoch contradiction or a demonstrated reset boundary.** No new nonstationary world was introduced.

## 22. Bounds

Unchanged limits: Memory 8, pairs 8, packages 8, trace 24, core decisions per epoch 12, epochs per instance 2, authorizations per epoch 24, pending authentic receipt 1, external source executions per lifetime 24. Memory/pair/package lengths reached 8 and remained 8 after the ninth commit. No old-episode exemption or expanded capacity. R1’s separate model campaign cap of eight decisions was not repurposed as the core limit; this study made zero model calls.

## 23. Ninth-event eviction

The ninth total commit was epoch 1002 / transaction 5 / source event 9, HOLD at state 0. Ordinary FIFO removed exactly epoch **1001 / transaction 1 / pair 4299262263552**, the oldest HOLD record (0→0, consequence 0), together with its matching pair and package/source event 1. Each ring retained its previous entries 2–8 and appended event 9. Eviction counter became 1. Selection was by ordinary insertion order, not by episode preference.

## 24. Provenance audit

All retained primary records passed unchanged Memory/pair/package binding checks and the diagnostic exact-original-receipt-object check. Original package predictions remained bound to measurement status; world reset was never substituted for an observed event. Discarding supporting rings failed closed in throwaway controls. Serialized diagnostic evidence preserves identities/content, while replay re-creates and rechecks live Python object identity within each run; serialized JSON alone does not carry an object-identity capability.

## 25. Identity collision audit

No full identity collision occurred in the registered same-lifetime 1001→1002 fixture: transaction IDs repeat with a different epoch; source event IDs continue. The separate fresh-instance diagnostic deliberately showed a **potential partial-key collision if histories from different lifetimes at the same epoch were naively merged**. Full package identities differ by source lifetime, but Memory/pair lookup keys omit that lifetime. No merge was performed, so this is a reason to reject that unimplemented interpretation, not a protected false authorization in the supported epoch path. Broader lifetime imports require a separate design.

## 26. Authority preservation

No core module changed. Existing receipt wrapper, Measure, Recovery and status authorizer were imported unchanged. Four negative controls rejected: old receipt after epoch, equal-field copy of current receipt, missing pairs and missing packages. All retained protected state remained unchanged during these rejections. Four epoch guards also rejected without state mutation. Pending-slot release and current-source origin requirements remained ordinary. No model proposal, prompt, hidden chat or stochastic inference occurred.

## 27. Exact replay

Re-executed the deterministic diagnostic from frozen code and the same hash-pinned historical contradiction archive, with network creation denied. Both registered files, **details.json and results.json**, reproduced byte-for-byte. Final compact results were regenerated from each copy with the same actual verification and were identical. The original raw provisional diagnostic was retained unchanged. This is deterministic fixture reconstruction, not a model replay or a claim of durable receipt-object capabilities across processes.

## 28. Historical regressions

Actual execution: five new boundary tests and **25 inherited tests** passed. Inherited tests cover v2 UNKNOWN, realized-event receipt authority, repaired status authorization and composition bindings. The prior 84-response ablation and 164-response R1 archives replayed exactly with zero inference. Five post-study commands returned their expected zero status.

**503 inherited substantive public files** remain byte-identical. All **288 R1** and **105 ablation** saved private archive checksums still match. Earlier classifications, main, tags and prior branches remain unchanged. No unrelated live campaign was rerun and no Ollama server was started. Detailed commands and log hashes are in [verification.json](../experiments/cross_episode_authenticated_memory_boundary_v0/verification.json).

## 29. Limitations

One stationary bounded world, two registered epochs, same source lifetime, deterministic fixture sources, no model performance experiment. A natural return to zero cannot substitute for independent state initialization. No reset-capable full two-episode fixture or genuinely new cross-epoch differing-outcome fixture was demonstrated. Map projection abbreviates event identity. Source lifetime uniqueness and previously committed package authority remain trusted software assumptions; no cryptographic or hostile same-process persistence claim. No indefinite retention, arbitrary epoch reuse, cross-source import, nonstationarity or general transfer was established.

## 30. Classification

**C — NOT ESTABLISHED.** Sixteen required checks pass within the tested scope; fresh-zero current-state initialization with retained authenticated history is missing. The complete required fixture therefore cannot be claimed. No supported carryover semantic failure requiring B was observed. The deliberately invalid controls were rejected.

| Required invariant | Outcome |
|---|---|
| Measure_unchanged | PASS (within tested scope) |
| Recovery_unchanged | PASS (within tested scope) |
| exact_replay | PASS (within tested scope) |
| fresh_zero_current_state_without_history_rewrite | MISSING / unsupported |
| historical_regressions | PASS (within tested scope) |
| known_retained_pairs_not_UNKNOWN | PASS (within tested scope) |
| memory_bound_8 | PASS (within tested scope) |
| new_observations_append_chronologically | PASS (within tested scope) |
| no_boundary_fake_event | PASS (within tested scope) |
| no_identity_collision_in_registered_same_lifetime_epochs | PASS (within tested scope) |
| no_model_chat_persistence | PASS (within tested scope) |
| ordinary_eviction_unchanged | PASS (within tested scope) |
| pending_authentic_receipt_at_most_1 | PASS (within tested scope) |
| prior_authenticated_records_unchanged | PASS (within tested scope) |
| provenance_traceable | PASS (within tested scope) |
| receipt_authority_unchanged | PASS (within tested scope) |
| untouched_pairs_remain_UNKNOWN | PASS (within tested scope) |


## 31. Narrowest defensible conclusion

Authenticated event history can remain available through the existing bounded **same-source epoch transition**, retaining provenance, chronology and ordinary eviction. **That transition preserves current state; it is not a fresh-episode reset.** The requested fresh-state cross-episode authenticated Memory boundary is not established by current APIs. Zero model calls; no model-learning claim.

## 32. Recommendation

Stop at this checkpoint. Before any cross-episode model campaign, make a separate research decision about an explicit trusted episode-initialization boundary that synchronizes external/current state while preserving audited historical rings and appropriate identity/anti-replay semantics. Specify whether the source lifetime continues, and whether abbreviated model-visible IDs need an epoch field. Do not implement that repair or launch inference automatically. Do not reset protected state by manual assignment or invent a RESET event to bypass the missing operation.
