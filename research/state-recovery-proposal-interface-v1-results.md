# State Recovery proposal interface v1 — zero-call result

**C — NOT ESTABLISHED. Zero model calls.** The bounded value-only interface passed its operational checks, including exact default equivalence, correct/wrong proposal handling, admission, attempt ownership and atomic rejection. One mandatory control fails: the unchanged authorizer accepts a wrong **status** when epoch, transaction, pair identity and value are otherwise correct. This occurs in both historical and new paths. It is a pre-existing requirement conflict, not a new acceptance caused by this refactor. It prevents claiming overall readiness.

[Preregistration](state-recovery-proposal-interface-v1-preregistration.md), [compact evidence](../experiments/state_recovery_proposal_interface_v1/results.json), [verification](../experiments/state_recovery_proposal_interface_v1/verification.json) and [reproduction](../experiments/state_recovery_proposal_interface_v1/README.md).

## 1. Historical missing interface

Recovery v0 correctly stopped before inference: the coordinator constructed `Recovery().state_candidate(decision, wrong=failed_recovery)` inline, with no configured proposal source. Its original sources, blocked result, exact diagnostic and zero-call finding remain unchanged. This study implements a separate path.

## 2. Frozen parent identities

Parent `0ccc3889a4c7efcfa413e476f4994df647f206d5`. Protocol commit `0d21641`; interface implementation `5b87181`; campaign/tests `abc13a6`. The parent includes established-prior Map v1 `b576b3a`, Map v0 `f7b16c4` and earlier preserved checkpoints. Frozen hashes cover all 367 inherited files except the root README and public inventory. Those two receive only the new checkpoint append/inventory refresh. Main and all tags remain unchanged; nothing pushed.

## 3. Minimal refactor

The separate [framework layer](../experiments/state_recovery_proposal_interface_v1/framework.py) subclasses the historical core. Its copied `_complete_pair` body differs by exactly one expression: the inline native call becomes `self._state_recovery_candidate(...)`. A source-text equivalence check enforces that restriction. All other coordinator methods, the authorizer class and realized-event staging/publication methods are inherited. No runtime method/global monkey-patching or new verifier is used. The static method copy is a maintenance cost; historical edits must not silently drift into this layer.

## 4. New proposal interface

`StateRecoveryProposalSource.propose(context) -> int` returns only a replacement state. Admission requires **exact built-in int**, value 0–3; bool, int subclasses, floats, strings, containers and objects reject without coercion. Context is a frozen dataclass of eight scalar fields: epoch, transaction ID, pair ID, pre-state, action, realized next state, realized consequence and audited measurement_matches. No receipt, Map, Memory, authorizer, verdict, executor or continuation capability is passed.

## 5. Trusted/native candidate envelope

The helper consumes a native StateCandidate first. Without a source it returns that object unchanged. With a source it replaces only `value`; epoch, transaction, pair identity and RECOVERING status come from native Recovery. The source cannot express those fields in the normal API. Observed candidates at the actual authorizer retained every envelope field for all correct and wrong injected cases. Passing a complete StateCandidate object was rejected at value admission.

## 6. Native attempt ownership

A framework-owned `RecoveryOpportunity` creates one native Recovery object. Native `state_candidate` consumes its attempt before any callback. The owner is not passed to the source. No callback counter is used to grant an attempt; the unchanged native limit enforces it. Measurement/Memory Recovery are inherited and do not use this state-only hook.

## 7. Unchanged independent authorizer

The actual state authorizer remains `CrossSourceStateAuthorizer`, with the same method object and frozen source bytes. It checks epoch, transaction, pair identity and value, and enforces duplicate/capacity bounds. **It does not validate candidate status.** The interface supplies trusted RECOVERING status, but that cannot establish the stronger requested low-level status-rejection property. No status check was added to hide this conflict.

## 8. Exact call ordering

Read-only observations on genuine injected opportunities recorded authentic receipt validation → audited Measure → incumbent quarantine → native attempt → source invocation → ordinary state authorization → Map commit → staged publication. Malformed values/source failures stopped before authorization; legal wrong values reached and failed authorization. The hook is located only at the historical state-Recovery branch, with its trigger unchanged.

## 9. Default/native equivalence

All **32** previous diagnostic cases ran through both the historical wrapper and new default wrapper. Complete deterministic case records were byte-identical, including protected snapshots, predictions, receipts, StepResult, metrics, native proposal/authorization observations and fault reasons. The complete historical diagnostic also matched the privately retained Recovery-v0 canonical file exactly. Unsupported callback keywords and the ignored ordinary-candidate/unused-slot probes retained their old behavior.

## 10. Genuine Recovery fixture matrix

All eight unchanged ADVANCE/RETREAT transitions under the frozen wrong-Map rule were tested, covering all four realized target states. Each received one correct and one legal wrong external value: **16 primary injected transactions**. HOLD remains a valid-incumbent path and was not reclassified as a Recovery opportunity. Deterministic Explorer and Map produced every fixture; the world table was unchanged.

## 11. Correct injected proposals

**8/8** primary correct values invoked the source once, consumed one native attempt, reached the existing authorizer and committed the receipt-consistent Map state and authentic Memory event. Receipt and original prediction were unchanged. A separate retained-history sequence added one successful injected correction without changing old records. These are synthetic proposals, not model outputs.

## 12. Wrong injected proposals

**8/8** primary cyclic wrong values reached the ordinary authorizer and were rejected. No correct receipt state was substituted. Every rejection had commit_delta=0, unchanged protected snapshots, denied continuation and no second callback after another begin request. The retained-history sequence added one matching wrong-value rejection with a prior Memory record preserved.

## 13. Malformed-value admission

The campaign tested −1, 4, bool, float, None, string, list, tuple, arbitrary object, int subclass, full StateCandidate, seven self-certifying mappings, ordinary callback exception and implicit no-return: **20/20** rejected before state authorization. The native opportunity had already been consumed; failure did not fall back to the native correct value. No model text parser was introduced.

## 14. Self-certification structure

The normal return type has no authorization or identity fields. Mappings containing a value plus each of `AUTHORIZED`, `verified`, `approved`, `receipt_id`, `package_id`, `grant` or `continuation` all rejected as non-integers. A StateCandidate carrying AUTHORIZED status also rejected at this boundary. This is a typed value interface, not a sandbox against arbitrary Python code in the trusted process.

## 15. Low-level identity forgery controls

Each of the eight genuine receipt-grounded decisions was paired with a candidate forging exactly one field. Fresh historical and new-path authorizers were tested independently, without publishing a transaction.

| Forged field | Historical rejects | New-path rejects | Required rejection |
|---|---:|---:|---|
| epoch | 8/8 | 8/8 | PASS |
| transaction_id | 8/8 | 8/8 | PASS |
| pair_decision_id | 8/8 | 8/8 | PASS |
| status = REJECTED | **0/8** | **0/8** | **FAIL** |

Thus **8/8 wrong-status candidates were accepted in each path**. These are direct authorizer acceptances below the normal interface, with zero protected publications in the controls. They must not be merged into the normal-interface false-accept count or omitted. Source inspection identified this possibility before implementation, and the frozen protocol explicitly bars an A classification if it occurs.

## 16. Historical wrong-Recovery control

The default `failed_recovery=True` case remained byte-identical: the native wrong value failed authorization and rejected atomically. This flag still affects the native candidate when no external source is configured. The new external source controls only replacement value; its independent correct/wrong cases are evaluated separately.

## 17. No-Recovery controls

All **12** registered controls passed with a source that would raise if called: eight HOLD S/SC cases and four consequence-only HOLD mismatches. Callback count and native state-Recovery attempt count were both zero. The valid incumbent remained, authentic consequences committed and measurement_matches remained false. Two additional HOLD steps seeded the retained-history controls, also without Recovery.

## 18. Invocation counts

The new injected-path campaign contains **52 transactions**: 16 correct/wrong, 20 admission/failure, 12 no-Recovery and four retained-history steps. It recorded **38 callbacks**, **23 commits** and **29 atomic rejections**. Every genuine opportunity called once; all 14 valid-incumbent steps called zero times. The default equivalence cases and low-level controls are separate denominators. Instrumented and uninstrumented duplicates are validation repeats, not additional model samples.

## 19. Recovery budget

Eight direct opportunity controls each allowed one callback and rejected a second candidate request **before a second callback**. Native attempts increments before its check, so its counter is 2 after the denied second request; only one candidate was returned. Additional unit controls verified this after correct, wrong, exception and None responses. This remains one attempt **per native object**, not a newly claimed global Recovery budget across state, Measure and Memory repair.

## 20. Proposer exceptions/failure

A LookupError callback, implicit no-return and malformed responses all failed closed. The helper converts ordinary callback exceptions to ValueError, which the unchanged staged wrapper rejects. It does not retry, repair the response or use native Recovery as fallback. BaseException/process termination and hostile trusted-process Python are outside these tests; this is not process isolation.

## 21. Atomicity

For all **29** injected rejections, before/after published Map, Map quarantine, Memory, Memory quarantine, pair store, package store and commit count matched exactly. Continuation was denied. Staged quarantine did not leak. A subsequent begin request could not execute or invoke the proposer again. The already executed external action is not rolled back; after rejection, stored Map is not asserted to track the moved world, and continuation is withheld.

## 22. Receipt authority

Every committed Memory event remained bound to the authentic receipt emitted after external execution. The proposal supplied only a Map correction value; it did not supply realized next-state/consequence evidence. Every correct, wrong and malformed transaction preserved receipt content and the exact current receipt object. The shared-root A/B compatibility adapters remain shared-root, not independent truth measurements.

## 23. Measure ordering

The unchanged auditor establishes the prediction comparison before the Recovery branch. All genuine fixtures had a verified mismatch and invalid incumbent. The proposer neither diagnoses failure nor requests its own invocation. Valid-incumbent mismatch controls never dispatched it. Failed predictions remained latched through success and rejection.

## 24. Memory preservation

The two matched retained-history sequences first committed an authentic HOLD event, then tested a successful or rejected ADVANCE correction. Both preserved the old verified record. Successful publication appended the authentic new event; rejection appended nothing. Memory schema and historical records were not rewritten. Existing package structures retain predictions; no new Recovery-history field was invented.

## 25. Bounds

Native limits and their enforcing methods are inherited unchanged. Every transaction passed existing Map/Memory quarantine, pair, package, trace, episode, authorization and epoch checks. Maximum Memory in the new campaign was two. The campaign does not newly establish saturation behavior for every bound; historical regressions retain their prior coverage.

## 26. Protected false accepts

**Zero protected false accepts**, receipt rewrites, prediction rewrites, protected partial publications or bound violations occurred in the normal injected campaign. Separately, the direct wrong-status controls had eight acceptances historically and eight on the new path. The latter are the disclosed mandatory-control failure, not normal proposer outputs and not protected transaction publications in this test.

## 27. Observer noninterference

An uninstrumented duplicate matched all protected results, summary, callback contexts, denial behavior, budget and identity-control evidence exactly. Only read-only profile observations were excluded from that comparison. The observer neither changes a method binding nor grants authorization. Default equivalence also compared the original native observations exactly.

## 28. Exact replay

The final campaign's detailed `campaign.json` and compact `results.json` replayed byte-for-byte with zero inference. Both runs also compared the historical 32-case diagnostic against its retained canonical evidence. Source/evidence hashes bind the replay. The expected exit code is **2**, reporting classification C; it is not disguised as full interface readiness.

## 29. Historical regressions

**28 actual commands returned their expected statuses**: the new campaign, exact replay, nine new unit tests, and all 25 commands retained from Recovery v0. They cover its still-blocked diagnostic; established-prior Map v1; Map v0; contradiction Explorer v1 and feasibility; realized-event campaign/replay; prior factorial; semantic, adaptive, Memory and original Explorer; minimum repair 1; base v0/v1/v2; old contradiction-v0 expected failure; and prior boundary/study tests. Verification records commands, actual/expected exit codes, timestamps and log hashes. No model inference ran during replay. Prior positive and negative results are preserved.

## 30. Limitations

The wrong-status requirement is unmet by the unchanged authorizer. This study does not authorize changing that logic or relaxing the requirement. The scalar-only API prevents a normal source from supplying status, but cannot prove rejection of candidates forged below it. The software receipt root, coordinator and Python process remain trusted. Synthetic proposal success says nothing about model usefulness. The fixed world and bounded fixtures do not establish general Recovery reasoning. The copied method requires explicit drift checks.

## 31. Classification

**C — NOT ESTABLISHED**, as frozen. The 16 operational completion criteria pass with the recorded regressions/replay, but the separately mandatory wrong-status rejection fails. No A readiness claim is made. B does not apply to this observed gap because historical and new acceptances are identical, with no new protected bypass or publication introduced. The negative result is retained rather than repaired outside scope.

## 32. Narrowest defensible conclusion

A separate value-only state-Recovery hook was implemented and passed the tested operational boundary checks while preserving default behavior and native authority. **Overall requested readiness is not established** because unchanged authorization does not reject the tested forged status. There were **zero model calls**; model Recovery usefulness, autonomous repair, model self-correction/self-authorization and general Recovery reasoning were not established.

## 33. Recommendation

Stop here. A separate research decision must resolve whether status is required to be validated by the low-level authorizer, or instead is a trusted coordinator-owned field outside that authorizer's contract. No requirement was silently relaxed and no verifier change was made. Do not run the Recovery model campaign or combine roles. Main and tags remain untouched; nothing pushed.
