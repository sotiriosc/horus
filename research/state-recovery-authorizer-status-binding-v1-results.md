# State Recovery authorizer status binding v1 — zero-call result

**A — STATE RECOVERY STATUS BINDING COMPLETE**, within the frozen software boundary and trusted state-Recovery scope. **Zero model calls.** All 120 wrong-status matrix candidates rejected; all 16 RECOVERING candidates preserved historical acceptance. Twenty-five wrong-status transactions rejected atomically. Exact replay and all 31 regression commands returned their expected outcomes. The old interface checkpoint remains **C — NOT ESTABLISHED**.

[Preregistration](state-recovery-authorizer-status-binding-v1-preregistration.md), [compact campaign evidence](../experiments/state_recovery_authorizer_status_binding_v1/results.json), [final classification/verification](../experiments/state_recovery_authorizer_status_binding_v1/verification.json) and [reproduction](../experiments/state_recovery_authorizer_status_binding_v1/README.md).

## 1. Demonstrated wrong-status failure

The previous study constructed otherwise correct candidates with status REJECTED. Its old and interface-v1 authorizers both accepted all eight. The normal value-only proposer could not supply status, but the required low-level negative control failed. That is the sole demonstrated authority-contract gap addressed here.

## 2. Preserved previous C classification

Parent `ed8b8f3f6fdae83bf0a9c8a5aff51c25ce35ed9b`; protocol `99a43aa`; executable preflight `2f93db6`; repair `099fce1`; tests/campaign `3490a05`. All 379 inherited files outside the root README/inventory remain byte-identical. Interface-v1 retains C, Recovery-v0 retains its blocked result, and prior Map/Explorer/framework evidence is unchanged. Main and tags are unchanged; nothing pushed.

## 3. Historical authorizer contract

`CrossSourceStateAuthorizer` historically checked epoch, transaction, pair ID, replacement value and duplicate/capacity rules. It did not check status. It also serves ordinary incumbent-retention and measured-replacement branches, whose legitimate candidates carry PROPOSED. A global RECOVERING-only rule would wrongly reject those transactions. This repair binds status only in **trusted state-Recovery scope**, while preserving the shared ordinary authorization contract.

## 4. Legitimate-status preflight

Before implementation, source inspection covered v0 and v1 native Recovery producers, the inherited v2/realized-event routes, historical campaigns/tests and interface-v1's value replacement. Native state-Recovery producers explicitly construct RECOVERING. The executable preflight checked **57 native Recovery envelopes**, all RECOVERING, and separately identified **14 ordinary PROPOSED acceptances**. No legitimate state-Recovery producer requiring another status was found. The prior full campaign matched its retained canonical evidence exactly; its old wrong-status acceptances remained reproducible. The preflight and complete matrix were committed before repair execution.

## 5. Exact repaired predicate

The separate [repaired authorizer](../experiments/state_recovery_authorizer_status_binding_v1/framework.py) adds:

```python
if state_recovery and candidate.status != CrossAuthorityState.RECOVERING:
    return False
return super().authorize(candidate, decision)
```

All remaining predicates are inherited. The coordinator forwards its **existing** `recovery_authorized` local branch flag as `state_recovery`; despite its historical name, this flag identifies the selected Recovery branch before authorization. The proposer cannot supply it, and candidate status does not determine it. Direct repaired-authorizer calls default to Recovery scope. The copied coordinator method has only that keyword addition. Epoch reset reinstalls the repaired authorizer with the same empty identity state. There is one active state authorizer, no second verifier, no normalization and no new proposal fields.

## 6. Status matrix

The frozen matrix contains all ten `CrossAuthorityState` members and all seven v0 `AuthorityState` members, for each of eight genuine receipt-grounded decisions: **136 cells**.

| Typed status entries per decision | Cells | Historical accepts | Repaired accepts | Repaired rejects |
|---|---:|---:|---:|---:|
| RECOVERING from each of the two string enums | 16 | 16 | 16 | 0 |
| Other nine CrossAuthorityState members | 72 | 72 | 0 | 72 |
| Other six AuthorityState members | 48 | 48 | 0 | 48 |
| Total | 136 | 136 | 16 | 120 |

Both enum classes compare RECOVERING equal under the requested predicate. This is semantic status equality, not a new enum-class admission rule. No invented status strings were tested. Detailed evidence retains enum class/name so shared spellings are not counted as independent semantic states.

## 7. Valid RECOVERING behavior

All **16/16** correct RECOVERING matrix candidates behaved as before. Eight primary correct injected corrections and the retained-history success still authorized. Native attempt ownership, selected value and candidate envelope remained unchanged. Valid duplicate and capacity cases preserved the historical exceptions and authorization-set bounds.

## 8. Wrong-status rejection

All **120/120** other enum candidates rejected in Recovery scope, including PROPOSED, AUTHORIZED and REJECTED. Rejection neither rewrote status nor inserted an authorization identity. The status gate runs before inherited authorization checks; no claim is made that a malformed candidate must reach the historical checker first. Ordinary non-Recovery calls deliberately retain their historical status semantics.

## 9. Identity/value controls

On each genuine decision, RECOVERING candidates with wrong epoch, transaction ID, pair ID or value still rejected: **32/32** in both historical and repaired checks. No identity/value validation was duplicated, removed or relaxed.

## 10. Combined-invalid controls

Wrong value plus REJECTED status rejected for all **8/8** decisions in both paths. Together with the identity/value cases, **40/40** invalid controls rejected. The test requires rejection without attributing success to which invalid field is checked first.

## 11. Historical-versus-repaired direct comparison

The exact original CrossAuthorityState.REJECTED witness remained **8/8 accepted historically** and became **8/8 rejected after repair**. Across the whole matrix, the intended difference was 120 wrong-status acceptances becoming rejections in Recovery scope; RECOVERING behavior was unchanged. The prior interface campaign's 32 identity/status controls differed only in its eight wrong-status results. Old source files were not edited to manufacture this contrast.

## 12. Normal proposal-interface compatibility

All **32 default diagnostic case records** and all **52 prior injected-path transaction records** were byte-identical through the repaired path, including the same native proposal/authorization observations. The eight budget cases were identical. The normal proposal helper, finite-value admission, deterministic fixture construction, Measure and staged publication are inherited unchanged. Only the explicitly invalid low-level status controls changed outcomes.

## 13. Correct injected proposals

All **8/8** primary correct replacement values still authorized with one callback and one native attempt. Published Map state and Memory event matched the authentic receipt. Additional retained-history and post-epoch successful corrections also preserved behavior. These were deterministic synthetic sources, not model outputs.

## 14. Wrong injected proposals

All **8/8** primary legal wrong values still reached the inherited value checker and rejected. The existing retained-history wrong-value rejection remained identical. No receipt-consistent fallback, retry, coercion or status normalization was introduced.

## 15. Malformed-value admission

All **20/20** prior malformed/failing controls retained their original safe rejections before state authorization. They include non-integer values, out-of-domain values, containers, self-certifying mappings, a complete StateCandidate, callback exception and no-return. The proposer still returns only an exact built-in int 0–3. No model text parser exists in this study.

## 16. No-Recovery controls

All **12** registered HOLD mismatch controls retained zero state-Recovery attempts and zero callbacks. Authentic outcomes committed normally, with mismatch visible. Ordinary PROPOSED candidates remained eligible through the same active authorizer in non-Recovery scope. A separate accurate-prediction measured-replacement check also matched the historical outcome.

## 17. Budget

The unchanged native object permits one candidate. Its counter increments to 2 on the denied second request, without a second callback. The eight inherited budget cases matched exactly. Every wrong-status transaction consumed one normal attempt/callback, then rejected; a subsequent begin request neither executed nor invoked the source. There is no fallback or extra opportunity. This remains a per-object state-Recovery limit, not a new global multi-component budget.

## 18. Proposal/envelope ownership

External source: replacement-state int only. Trusted native Recovery: epoch, transaction, pair ID and RECOVERING envelope. Trusted coordinator: Recovery/non-Recovery scope. Repaired authorizer: status predicate plus inherited value/identity/duplicate/capacity checks. Tests corrupting status use a **test-only core subclass below the normal interface**, after its native attempt and correct value proposal. This test mechanism is not exposed through the production proposal API.

## 19. Atomicity

Twenty-four transaction controls covered eight genuine fixtures × REJECTED/PROPOSED/AUTHORIZED; a further retained-history case brought the total to **25/25 atomic wrong-status rejections**. Every case had commit_delta=0 and identical published Map, Map quarantine, Memory, Memory quarantine, pairs, packages and commit count. Continuation was already false after begin and remained false across submission. Receipt and latched prediction were preserved. Transient quarantine stayed staged. Direct matrix controls have no publication by construction and are reported separately from these transaction tests.

## 20. Receipt authority

The realized-event wrapper and authentic external executor are unchanged. Authorized event content continues to come from the receipt, never from the proposal or status. Wrong-status tests checked both exact current receipt-object identity and unchanged receipt content. The existing shared-root compatibility adapters remain shared-root; the repair adds no independent truth measurement.

## 21. Prediction preservation

Historical/default/injected records matched exactly, including original latched predictions. All 25 wrong-status transaction controls separately verified the prediction after rejection. Recovery did not rewrite the failure that led to its opportunity.

## 22. Memory preservation

Both prior retained-history sequences were unchanged. The new two-step control first committed authentic HOLD history, then rejected a forged-status ADVANCE correction. Its existing Memory and package records remained identical; no rejected event was appended. This preserves historical observations rather than editing them retrospectively.

## 23. Bounds

Existing bound checks passed throughout. Maximum Memory in these transaction fixtures was two. Direct capacity controls filled exactly 24 authorization identities and rejected the next candidate with the same historical exception; duplicate behavior also matched. Wrong status consumed no authorization identity. Epoch reset retained the repaired authorizer type and empty authorization state, and subsequent Recovery remained protected. No historical numeric limit changed.

## 24. Protected false accepts

The repaired protected transaction path recorded **zero false accepts**, receipt rewrites, prediction rewrites, retry leaks or protected publication errors. All tested wrong-status transactions rejected. Historical wrong-status acceptance is retained explicitly as the before-repair negative evidence; it is not relabeled as repaired success or omitted from the matrix.

## 25. Exact replay

The final detailed campaign and compact campaign result replayed **byte-for-byte**, with zero inference. An uninstrumented duplicate matched all protected outputs and counts. Compact campaign results deliberately point to `verification.json` for the final classification: the standalone campaign cannot certify that later regression commands have run. The final verification establishes A after those checks. Raw evidence and logs remain private; public artifacts retain source and evidence hashes.

## 26. Historical regressions

**31 actual commands returned their expected statuses**: new campaign, exact replay, nine new tests and all 28 inherited interface-v1 commands. These preserve interface-v1's C and Recovery-v0's blocked diagnostic, Map v1/v0, Explorer contradiction/feasibility/factorial/semantic/adaptive/Memory/original studies, realized-event campaign/replay, minimum repair 1, base v0/v1/v2 and the old contradiction expected-failure diagnostic. Expected exit-2 checkpoints remained exit 2. Exact commands, timestamps and log digests are recorded in verification. No inference occurred.

## 27. Limitations

The Recovery/non-Recovery scope is trusted coordinator input, not a fact inferred from untrusted candidate status. Arbitrary trusted-process Python could call the authorizer with another scope; hostile-process security is not claimed. Status equality does not impose runtime enum-class identity. Ordinary authorization retains its prior semantics outside Recovery scope. The receipt root remains trusted. Fixture coverage is bounded; this is not a general fault or reasoning campaign. Static copied coordinator code is guarded by an exact single-call-change comparison and must not silently drift.

## 28. Classification

**A — STATE RECOVERY STATUS BINDING COMPLETE.** All 16 frozen completion requirements are supported by the campaign, replay, actual regressions and preservation checks. The prior C classification remains unchanged. No new legitimate Recovery rejection, authorization bypass, retry leak or protected publication error was observed.

## 29. Narrowest defensible conclusion

The repaired state-Recovery authorizer binds the replacement value and trusted candidate status **in coordinator-owned Recovery scope**, closing the demonstrated wrong-status acceptance while preserving tested legitimate native, injected and ordinary transaction behavior. There were **zero model calls**. This does not establish model usefulness, autonomous recovery, general Recovery reasoning or self-improvement.

## 30. Recommendation

Stop at the completed status-contract repair. The next separate research decision is whether to run the previously planned bounded model study through this repaired value-only interface. No model campaign, prompt/parser, combined proposal roles or additional repair was launched. Main and tags remain unchanged; nothing pushed.
