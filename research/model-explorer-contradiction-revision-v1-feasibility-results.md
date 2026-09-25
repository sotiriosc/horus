# Contradiction revision v1 — full fixture feasibility

**A — CONTRADICTION REVISION FIXTURE FEASIBLE.**

Both complete seven-step fixtures constructed all six H0/H1/H2 snapshots safely. **14/14 primary commits; 3/3 authenticated contradictions accepted; zero protected false accepts, receipt mismatches, prediction rewrites or history rewrites.** Old and new observations coexist. Exact replay and every required historical regression passed. **Actual model calls: 0. Parser controls: 0. Behavioral revision: UNTESTED.** The repair implementation was not changed.

[Preregistration](model-explorer-contradiction-revision-v1-feasibility-preregistration.md) · [compact results](../experiments/model_explorer_contradiction_revision_v1_feasibility/results.json) · [final classification and execution verification](../experiments/model_explorer_contradiction_revision_v1_feasibility/verification.json) · [reproduction](../experiments/model_explorer_contradiction_revision_v1_feasibility/README.md).

## 1. Parent, framework and repair identities

Parent/repair checkpoint: `ca131869b97dd5c96dd60eb7329f65b1a293246f`. Historical framework: `8ec32c839133df7ddd76448063b5f765c20155da`. Preserved failed contradiction checkpoint: `f21c62532590c35b7c459b647ec09ecfbcb5bb0c`. New protocol `90b521f`, fixture implementation `5a93936`, evidence/verification `557bd89`. All 23 frozen framework sources and 14 additional repair/fixture inputs were hash-checked before/after execution. Of 304 inherited files, 302 remain byte-identical; root README is appended and PUBLIC_MANIFEST refreshed. Main and all historical tags remain unchanged; nothing was pushed.

## 2. Why feasibility only

This establishes whether the required contradictory authorized histories can exist. The 14 primary transactions are scripted, not model proposals. A second 14-transaction uninstrumented execution checks observer noninterference; exact replay repeats both. No model server was started, model prompts constructed, parser controls run, stochastic inference invoked or 144-call budget consumed. The implementation has no model transport.

## 3. Exact CONTROL regime

The external world never changes. At state 1, HOLD realizes next state 1/consequence +1; ADVANCE realizes next state 2/consequence −1. Other cases use the unchanged historical transition law.

## 4. Exact SHIFT regime

Executions 1–3 use the same old world. After execution 3, only state-1 HOLD consequence becomes −1 and state-1 ADVANCE consequence becomes +1. Their next states remain 1 and 2. All other transitions/consequences remain unchanged. The existing repair `TestWorld` and historical change overlay are reused without edits.

## 5. External regime boundary

The switch is a property of the external fixture. The framework receives the authentic receipt after completed execution, not the regime flag. Neither Map nor authorization receives CONTROL/SHIFT as input. Separate audit evidence identifies arms; model-visible data previews contain no arm, regime or source-lifetime label. Receipt origin/integrity retain the repair's declared software trust assumptions.

## 6. Action sequence

Both arms start state 1, epoch 1001, transaction 1 and execute HOLD, ADVANCE, RETREAT, HOLD, ADVANCE, RETREAT, HOLD. Pre-states are `[1,1,2,1,1,2,1]`; next states `[1,2,1,1,2,1,1]`. H0/H1/H2 are captured after transactions 3/6/7 at state 1. Expected histories are assertions against actual authorized records, never injected fixtures or fabricated Memory.

## 7. H0 CONTROL

HOLD `[+1]`; ADVANCE `[−1]`. Three authorized Memory records include the navigation RETREAT. Target observations have transaction/event IDs 1 and 2.

## 8. H0 SHIFT

HOLD `[+1]`; ADVANCE `[−1]`. O1 and O2 chronological previews are exactly identical to CONTROL H0. Full provenance correctly uses a separate external source lifetime rather than falsely claiming the same physical execution.

## 9. H1 CONTROL

HOLD `[+1,+1]`; ADVANCE `[−1,−1]`. Six authorized records; target transaction/event IDs 1,2,4,5 in chronological order.

## 10. H1 SHIFT

HOLD `[+1,−1]`; ADVANCE `[−1,+1]`. The original records remain unchanged alongside their newly authenticated contradictory consequences. Six authorized records; the same target transaction/event ID shape as CONTROL.

## 11. H2 CONTROL

HOLD `[+1,+1,+1]`; ADVANCE `[−1,−1]`. Seven authorized records; target transaction/event IDs 1,2,4,5,7.

## 12. H2 SHIFT

HOLD `[+1,−1,−1]`; ADVANCE `[−1,+1]`. Seven authorized records; no Memory eviction or rewritten history. All five visible target observations trace to their exact authentic receipt objects and external execution identities.

## 13. Changed HOLD: actual, predicted and authorized

| SHIFT transaction | Latched prediction | Actual / authentic receipt | Authorized Memory |
|---|---:|---:|---:|
| 4, HOLD | +1 | −1 | −1 |
| 7, HOLD | +1 | −1 | −1 |

Both committed with `measurement_matches=false`. Both retained the valid state-1 incumbent. The original HOLD +1 record survived unchanged at H1 and H2; no prediction was rewritten.

## 14. Changed ADVANCE: actual, predicted and authorized

SHIFT transaction 5: prediction −1; actual/authentic receipt +1; authorized Memory +1; next state 2. Measurement correctly recorded disagreement. Ordinary bounded Recovery proposed state 2 and its authorization succeeded. The earlier ADVANCE −1 record remained unchanged.

## 15. Old-history preservation

Every step compared all earlier authorized records with their retained values. All remained unchanged; no event was relabeled false, superseded, averaged or banned. At SHIFT H1/H2, transaction 1 still records HOLD +1 and transaction 2 ADVANCE −1. New records carry distinct event identities. This concerns bounded retained history; indefinite archival retention is not claimed.

## 16. Receipt/provenance audit

For every retained record, the audit follows Memory pair ID → pair → authorized package → the exact original receipt object captured from the external pending slot → execution. It checks epoch, transaction, event ID, source identity, pre-state, action, next state and realized consequence. This includes 32 record checks across six stage snapshots, of which 22 are visible target observations; observations recur across stages, so these are not 32 unique events. Object-origin identity was checked in addition to content equality. A/B remain shared-root descendants, not independent truth observations.

## 17. Contradiction-only acceptance test

All three opportunities—SHIFT transactions 4, 5 and 7—contradicted the latched prediction and at least one earlier same-state/action observation. All three were accepted with their authentic realized consequences. No conformity-based rejection or substitution occurred. The explicit fixture assertion would fail on rejection of these clean, authentic contradictory events. Confirmation verifies origin and binding; it does not require agreement with earlier expectation.

## 18. Map behavior

Both arms' published Map states follow the same next-state sequence. Versions advance identically from 0 to 7. The static prediction remains contrary at all three changed events; no prediction rewrite or learned transition update is claimed. SHIFT transaction 5 transiently quarantines state 1/version 4 and publishes recovered state 2/version 5. That transient event is separately recorded, not concealed by the empty final quarantine.

## 19. Measure behavior

CONTROL measurements match on all seven transactions. SHIFT matches on transactions 1,2,3,6 and disagrees on 4,5,7. Those three mismatches do not invalidate authentic evidence. The authorized package preserves the original prediction separately from the realized receipt, and Memory retains the correct `measurement_matches` value.

## 20. Recovery behavior

Exactly one state-Recovery proposal/authorization occurred: SHIFT transaction 5, value 2, bound to epoch 1001, transaction 5 and pair ID 4299262264576. A read-only profiling hook captured the actual original function return, plus the transient quarantine record. No Recovery function or implementation was replaced. The uninstrumented duplicate matched all other evidence exactly. Recovery did not alter the receipt; CONTROL required no Recovery.

## 21. Atomicity

The complete fixture has zero rejected steps, so it provides no new rejection opportunities; all 14 commits have commit_delta=1. The unchanged repair campaign was separately rerun and replayed: **20/20 attacks rejected atomically**, with commit_delta=0, no partial protected publication and no continuation grant. Its evidence matched the preserved repair checkpoint byte-for-byte. The new harness checks this same conditional invariant on any failure and stops; it does not weaken or replace the repair's atomic coordinator.

## 22. Bounds

Observed per-arm maxima: Memory 7, pairs 7, packages 7, pending authentic receipt 1, trace 21. Limits remain 8/8/8/1/24. No eviction or bound enlargement. Published Map/Memory quarantine maxima were zero; the read-only observer recorded one transient Map quarantine at SHIFT tx5, within the existing bound of one. The finite external audit holds at most seven original receipt references per arm and never feeds that archive to the framework or Explorer.

## 23. Chronological projection preview

Current state is 1; offered actions are HOLD/ADVANCE. Only authorized pre_state=1 records for those actions appear, preserving chronology. RETREAT records remain in full Memory but are excluded from the preview. Every row below has epoch 1001; event IDs are scoped to the separately audited source lifetime.

| Transaction / event ID | O1 surface | O2 surface | SHIFT H2 consequence |
|---|---|---|---:|
| 1 / 1 | K2 | M4 | +1 |
| 2 / 2 | K1 | Q7 | −1 |
| 4 / 4 | K2 | M4 | −1 |
| 5 / 5 | K1 | Q7 | +1 |
| 7 / 7 | K2 | M4 | −1 |

O1 maps K1=ADVANCE, K2=HOLD; O2 maps Q7=ADVANCE, M4=HOLD. The actual preview contains epoch, transaction ID, event ID, surface action and consequence only. Full source identity/provenance is audited separately. No hidden regime label, summary/average or model prompt is included. These are deterministic previews, not observations of model behavior.

## 24. CONTROL/SHIFT matching

Starting protected states match exactly. All seven epoch/transaction/action/pre-state/next-state/event-counter shapes and package shapes match. Map versions also match. Source-lifetime identities deliberately differ at every step, so full receipts/packages are not claimed byte-identical across arms. Realized consequences differ only at transactions 4,5,7; measurement metadata differs there. Recovery/quarantine metadata differs at transaction 5. O1/O2 H0 projections match exactly.

## 25. Protected false accepts

Primary fixture: **0 protected false accepts, 0 receipt-mismatch accepts, 0 receipt substitutions, 0 prediction rewrites, 0 old-history rewrites**. All 14 committed outcomes match both their authentic receipt and the external event audit. The separate unchanged repair control still has its disclosed one out-of-model wrong acceptance when the trusted root lies; that limitation has not disappeared.

## 26. Exact replay

The final `fixture.json` and compact `results.json` replay byte-for-byte, including both arms, all receipts/predictions/packages/authorizations/Memory, stage snapshots, projections, metadata, bounds and provisional campaign gate. Each invocation includes the additional uninstrumented 14-transaction noninterference validation. Final classification follows replay and regressions and is recorded in `verification.json`; the campaign gate alone is explicitly provisional. Detailed evidence and logs remain private. Initial passing evidence is retained too; a final failure-counter cleanup prevents double-counting a stopped step and leaves detailed fixture evidence byte-identical.

## 27. Historical regressions actually executed

Exact commands, UTC times, expected/actual exits and private-log hashes are in verification. All required runs completed with their expected outcomes.

| Regression | Actual result |
|---|---|
| Realized-event grounding v0 campaign + replay | Both passed; evidence byte-identical to preserved checkpoint; 105 protected clean authorizations, 20 atomic rejections, one disclosed out-of-model root false accept |
| Repair boundary tests | 6/6 passed |
| Old contradiction-v0 diagnostic | Expected exit 2; original false accept still reproduced; detailed and compact evidence byte-identical |
| Old contradiction-v0 unit tests | 3/3 passed |
| Minimum framework repair 1 | 177 runs; 126/126 protected passes; historical 15 ablation and six boundary violation runs retained |
| Base framework v0 | 12 tests / 42 scenarios passed |
| Base framework v1 | 10 tests / 69 scenarios passed; three common-mode false accepts retained |
| Base framework v2 | 13 tests / 57 scenarios passed; 12 A+B blocks, three A+B+C and three registry false accepts retained |
| Original Explorer integration replay | Passed; 69 recorded model responses plus historical synthetic controls |
| Memory v1 replay | Passed; 224 recorded responses |
| Adaptive v0 replay | Passed; 288 recorded responses |
| Semantic-prior v0 replay | Passed; 288 recorded responses |
| Prior-factorial v1 replay | Passed; 216 recorded responses |

All five model transcripts and summaries matched their earlier evidence. Replaying 1,085 recorded responses performs zero new model calls. Historical parser/control checks belong to those unchanged replay regressions; no parser control was implemented or run for the new feasibility study.

## 28. Limitations

The root remains trusted for external source authenticity and receipt integrity within the declared single-threaded software prototype. This does not prove physical truth, sensor independence, arbitrary grounding, hostile-process security or physical common-mode protection. The changed world is a narrow scripted fixture. The audit establishes authentic software event binding and preserved history, not causality, model understanding, model adaptation, concept-drift detection, RL, weight learning, general nonstationarity adaptation, AGI or RSI.

## 29. Frozen classification

**A — CONTRADICTION REVISION FIXTURE FEASIBLE.** All 16 preregistered completion criteria passed, including complete histories, changed HOLD/ADVANCE authorization, old-record preservation, zero protected mismatches/rewrites, contradiction acceptance, preserved atomicity, bounds, projection, exact replay and unchanged historical regressions. The final per-criterion checklist is in verification. No core failure required a repair; the realized-event implementation and evidence stayed unchanged.

## 30. Narrowest defensible conclusion

Within the declared software trust root, the framework now safely retains both “this was true then” and “this different thing is true now,” without requiring the new authentic consequence to conform to the old prediction or history. The complete verified CONTROL/SHIFT fixture exists. No conclusion about model revision follows from zero model calls.

## 31. Next-step recommendation

Stop at this feasibility checkpoint. The next research decision is whether to run the already designed contradiction-revision behavioral study through the receipt-bound path. No 144-call campaign was implemented, run or scheduled. Main, tags, historical implementations and historical evidence remain unchanged; nothing was pushed.
