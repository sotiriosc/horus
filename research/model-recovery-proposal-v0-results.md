# Recovery proposal v0 — zero-call interface checkpoint

**STOPPED WITH ZERO MODEL CALLS: MISSING PROPOSAL INTERFACE.** Model Recovery usefulness is **UNTESTED / NOT ESTABLISHED**. This is an integration-gate result, not poor model performance. Native Recovery authorization passed the bounded diagnostic; model-adapter authorization remains untested. No inference implementation, live schema/prompt, 96-call campaign or architecture repair was introduced.

## 1. Parent/checkpoint identities

Parent `b576b3a55beade14f4e578d9ec367c52e881f8a6`. Gate protocol `5d12e86`; diagnostic implementation/tests `51ee2b2`. Established-prior Map v1 remains replicated; Map-v0 remains NOT ESTABLISHED. The representation checkpoint, Explorer studies, realized-event repair and framework history remain unchanged. [Frozen sources](../experiments/model_recovery_proposal_v0/frozen-inputs.json), [compact results](../experiments/model_recovery_proposal_v0/results.json) and [verification](../experiments/model_recovery_proposal_v0/verification.json) bind the evidence. Main and tags unchanged; nothing pushed.

## 2. Why Map work stops here

Established-prior Map v1 satisfied both families' registered criteria. No third Map study or combined model roles were run. This checkpoint inspects only whether Recovery can accept an externally supplied proposal through its existing path.

## 3. Exact Recovery implementation inspected

Actual code, not design prose:

- [StateCandidate and PairDecision](../experiments/base_framework_v1/framework.py#L49): immutable proposal fields `epoch`, `transaction_id`, `pair_decision_id`, `value`, `status`. State Recovery returns status RECOVERING.
- [Recovery](../experiments/base_framework_v1/framework.py#L274): `state_candidate(decision, wrong=False)` consumes one object-local attempt and returns the decision's next state, or its cyclic successor under the built-in fault flag. Input is `PairDecision`, including audited `measurement_matches`, plus that fault flag. It does not receive the latched Prediction.
- [Core constructor](../experiments/base_framework_v1/framework.py#L326): stores Explorer, Map, Memory and authorizers, but no Recovery component or factory.
- [Actual state Recovery call](../experiments/base_framework_v1/framework.py#L609): quarantine, then `Recovery().state_candidate(decision, wrong=failed_recovery)` inline.
- [State authorizer](../experiments/base_framework_v1/framework.py#L194): independently checks epoch/transaction/pair identity and candidate value against the receipt-grounded decision, then rejects duplicate/bounded authorization identities.
- [Atomic wrapper](../experiments/realized_event_grounding_v0/framework.py#L131): validates authentic root, runs the coordinator on a deep copy, audits receipt/pair/Memory and prediction preservation, and publishes only after success.

## 4. Proposal/authorization separation

The native proposal and authorizer are separate functions. Correct native candidates pass; the native wrong-candidate fault is rejected. However, the coordinator does not expose a configurable state-Recovery proposer/component/factory between quarantine and the unchanged authorizer.

An attached `inner.recovery` sentinel received **zero calls**; the native candidate was authorized instead. Supplying `candidate_value=0` during a genuine state-1 ADVANCE failure also committed state 2: that ordinary candidate was discarded and native Recovery supplied 2. Thus `candidate_value` cannot honestly be labeled a model Recovery proposal interface. An unsupported `recovery_proposer` keyword safely rejected with TypeError, not a dispatched callback.

Python method/global replacement could intercept an inline call technically, but that would change the frozen class/module behavior rather than use an exposed composed-component entry point. It was not used to manufacture a passing gate. No authorization function, Recovery method, module binding or coordinator was monkey-patched/copied.

## 5. Zero-call interface gate

**BLOCKED: exact missing interface is a configurable proposal source at the existing post-Measure, post-quarantine state-Recovery call site, retaining the native attempt owner and ordinary independent authorizer.** It was documented, not implemented.

| Required property | Evidence/status |
|---|---|
| A: correct proposal independently authorized | Native path demonstrated; external/model adapter untested |
| B: incorrect proposal rejected | Native `failed_recovery=True` candidate rejected |
| C: malformed/out-of-domain model candidate rejected | **UNTESTED: no model admission interface** |
| D/E: receipt and original prediction unchanged | All 32 synthetic transactions passed |
| F/G: rejected Recovery has zero commit delta and no continuation | Native wrong candidate passed; another begin request denied |
| H: existing staged publication | Correct native transactions passed; failed staging published no protected event |
| I: budget unchanged | Native one-attempt-per-object limit confirmed; adapter budget untested |
| J: proposer has no authorization capability | No model source was dispatched; no adapter capability claim established |
| No-Recovery-needed control | Four consequence-only HOLD cases committed authentic consequences without state Recovery |

A passing native characterization does not satisfy the model adapter gate. The user's zero-call stop rule therefore applies.

## 6. Sole model role

No model occupied any role: **zero inference**. Diagnostics used deterministic Explorer, deterministic Map and native non-model Recovery. Intended future role would be Recovery proposal only; no Explorer/Map/Recovery combination occurred.

## 7. Fixture matrix

The unchanged world was enumerated with 12 authentic external executions, then tested in a 24-case S/SC matrix. Eight underlying ADVANCE/RETREAT transitions produce genuine state Recovery; four HOLD self-loops retain the valid incumbent. Across both classes: **16 native Recovery commits and eight incumbent-retention commits**. Genuine corrections cover all four realized target states. The preferred full 12-case live Recovery matrix is therefore not semantically valid as stated; no HOLD opportunities were manufactured.

## 8. Failure classes

S predicts `(actual_next_state+1) mod 4` and the observed historical consequence. SC also rotates consequence −1→0→+1→−1. Both deliberately mismatch the authentic event. For the same state/action, their native `PairDecision` Recovery inputs are identical, including `measurement_matches=False`; the differing failed Prediction is not passed to `state_candidate`. Recovery repairs only the replacement state. These were diagnostic classes, not a frozen live two-class behavioral design.

## 9. Deterministic Explorer

An experiment-side selector returns the registered canonical action through the original `begin_step` action-admission path. No model chooses the action and no framework allowed-action list is changed.

## 10. Deterministic wrong Map construction

A fixture-only Map subclass overrides prediction and inherits the original protected state, commit and quarantine methods. Frozen wrong values come from the preceding ordinary world/receipt enumeration. Runtime execution has its own unchanged external world; it receives action and identity, not the Map prediction. No incumbent corruption was used to force Recovery.

## 11. Authenticated realized events

The unchanged `ExternalExecutionBoundary` emitted receipts only after execution. The wrapper required the exact current receipt object, full identity/content binding and the normal shared-root compatibility adapters. Every accepted event matched actual execution and its receipt. The external world transition table was not changed.

## 12. Model-visible Recovery context

**No model prompt was constructed.** Native state Recovery receives `PairDecision`: identity, pre-state/action, realized next state/consequence, source/provenance fields and the audited measurement flag. It does not receive the original latched prediction or a world/root capability as a parameter. A future interface would need to settle exactly which legitimate fields to serialize; the recommended richer failure payload was not assumed available.

## 13. Representation families

O1/O2 remain the requested prospective choices if an action-visible model interface is later authorized. Neither family was sampled here; no mappings, semantic arm, new vocabulary or neutrality campaign was executed. The representation-prior checkpoint remains unchanged.

## 14. Exact output schema

Existing native output is `StateCandidate(epoch, transaction_id, pair_decision_id, value, status=RECOVERING)`, with a bounded world-state value generated internally. **No live model JSON schema/parser was frozen or implemented**, because no supported admission point was found. Type annotations alone are not asserted to validate arbitrary model text. Native synthetic tests are not evidence that a nonexistent model parser rejects malformed candidates.

## 15. Exact real-call count

**0 real calls.** No server started, weights loaded, model request, retry, vote or replacement call. The 96-call maximum was not consumed or repurposed. Evidence contains synthetic diagnostic executions, not a model transcript.

## 16. Validity

Model valid/malformed/correct/wrong counts: **UNTESTED, denominator 0**. They are not scored 0/48 or treated as behavioral failures. Thirty of 32 diagnostic transactions committed correctly; the native wrong Recovery and unsupported-keyword probes rejected without protected publication. These counts describe the native diagnostic only.

## 17. O1 proposal usefulness

**UNTESTED / NOT ESTABLISHED.** No O1 calls, validity rate, correct-candidate rate, live threshold or family decision was estimated.

## 18. O2 proposal usefulness

**UNTESTED / NOT ESTABLISHED.** No O2 calls. No family pooling or invented denominator.

## 19. Correct proposal authorization

Native Recovery produced receipt-consistent corrections through the unchanged independent authorizer. The primary matrix had 16 such authorizations; the ignored ordinary-candidate and unused-component-slot probes added two. These **18 native Recovery authorizations** are not model-generated corrections. Correct model-candidate authorization remains untested.

## 20. Incorrect proposal rejection

In the focused native wrong-Recovery test, the returned replacement state was wrong, the ordinary authorizer returned false, commit_delta was 0, and continuation was denied. A subsequent begin request did not execute. The unsupported callback keyword also rejected atomically before any Recovery callback. These checks do not establish malformed model-output admission or self-certification rejection.

## 21. Final Map correctness

All 30 diagnostic commits published the receipt-consistent next state. Both rejected transactions retained the pre-transaction protected Map/Memory/pairs/packages unchanged. The external action had already happened in these rejections; the unchanged stored Map is not claimed to equal the now-moved world after rejection. Continuation was denied instead of publishing a false correction.

## 22. Measure boundary

The original auditor verified the prediction/receipt comparison before the Recovery branch. All registered wrong predictions produced mismatches, but state Recovery additionally required an invalid incumbent. The read-only observer recorded Measure verification, quarantine, native proposal, then independent authorization in that order on genuine Recovery paths. A model did not diagnose failure.

## 23. Recovery budget

`RECOVERY_LIMIT=1` applies **per Recovery object**. A second proposal call on that object raised `recovery attempt bound exceeded`; the counter reached 2 because `_take()` increments before checking, not because a second candidate was allowed. The state branch normally constructs one fresh object and calls it once. Measurement and Memory recovery independently instantiate objects elsewhere, so this is not a demonstrated single global attempt budget across all Recovery functions. Native transaction rejection prevented continuation. Model-call/adapter retry behavior is untested because no adapter ran.

## 24. No-Recovery control

Four HOLD cases, one per state, used a correct next-state prediction with a deliberately wrong consequence. All committed authentic consequences with `measurement_matches=False`, no state Recovery invocation and unchanged receipt authority. The 24-case matrix also produced eight HOLD non-Recovery cases despite wrong next-state predictions. Surprise alone did not manufacture a Recovery opportunity.

## 25. Memory preservation

Successful Memory stores receipt-grounded event fields, measurement_matches and AUTHORIZED status under its existing structure. It does **not** contain a new free-form Recovery plan or explicit Recovery-proposal history field. Accepted packages preserve the original Prediction; control traces/StepResult and private diagnostic evidence record Recovery/rejection details. Rejected transactions append no authorized Memory event. Fixtures began empty, so this checkpoint does not independently claim a new long-history preservation result; historical replay checks cover the existing retained-history studies.

## 26. Self-certification controls

**NOT RUN: interface blocked before model campaign.** AUTHORIZED strings, extra verifier/receipt/package fields, multiple model candidates and malformed model outputs were not routed through a fabricated parser. Native independent authorization separation was inspected and tested as above; model-like self-certification behavior remains untested.

## 27. Framework integrity

**NATIVE RECOVERY AUTHORIZATION INTEGRITY PASS** for this bounded diagnostic: zero protected false accepts, receipt rewrites, prediction rewrites or bound violations; both diagnostic rejections had zero commit delta and no continuation. Correct paths preserved staged publication; transient Map quarantine on failed staging did not leak into protected publication. Maximum Memory was one. **Model-adapter authorization integrity is UNTESTED**, not promoted to PASS. Trusted emitter compromise and hostile Python in the trusted process remain outside the protected model.

## 28. Exact replay

The zero-call diagnostic and compact results replayed **byte-for-byte**, with no inference. An additional uninstrumented run produced identical protected outcomes and summary, checking observer noninterference. A recorded-model-response Recovery replay is **not applicable: no model responses exist**. Private detailed evidence hashes are in compact results; [reproduction instructions](../experiments/model_recovery_proposal_v0/README.md) explain the expected blocked-gate exit code 2.

## 29. Actually executed historical regressions

**25 commands returned their expected exit statuses**, including this diagnostic's expected exit 2 and the old contradiction-v0 diagnostic's separate expected exit 2. Established-prior Map v1, Map v0, contradiction Explorer v1, feasibility, realized-event repair, factorial, semantic, adaptive Explorer, Memory and original Explorer recorded evidence all replayed without new inference. Minimum repair 1 and base v0/v1/v2 reran; new interface/budget/authority tests passed **4/4**. Existing study/gate tests also passed. Exact commands, timestamps and log hashes are in verification. Historical positive findings and common-mode/registry/root/old-contradiction negative outcomes remain intact.

## 30. Limitations

No model usefulness, model parser, injected-candidate authority boundary, model retry budget or self-certification resistance was tested. Native synthetic success is not a substitute. The missing boundary is specific to this frozen implementation and the allowed composed-component integration pattern; it does not establish that Recovery could never support such a role. The software receipt root and process are trusted; native fault flags are limited and not a general adversarial-language campaign. S/SC converge at the actual Recovery input, and HOLD is not a genuine state-Recovery fixture.

## 31. Narrowest defensible conclusion

**MODEL RECOVERY PROPOSAL USEFULNESS NOT ESTABLISHED — UNTESTED, ZERO CALLS.** The unchanged implementation separates native Recovery proposals from independent authorization and safely rejects the tested wrong native correction. It does not expose the proposal-only injection point required to test a real model under this task's constraints. No model-generated corrections were independently authorized, and no model authorization-integrity PASS is claimed. This is not autonomous self-repair, recursive self-improvement, weight learning, RL, general Recovery reasoning/world-model repair, AGI or RSI.

## 32. Recommendation

Stop at this interface checkpoint. A separately scoped change would be needed to expose a state-Recovery proposal source while retaining the native budget owner, verified-failure/quarantine ordering, ordinary authorizer and atomic publication. Such a change and a fresh synthetic gate would require a separate decision; neither was implemented here. Do not run the 96-call campaign, combine model roles, alter receipt authority, promote the model into Measure/Memory, add retries or launch another Recovery campaign under this checkpoint.
