# State Recovery proposal interface v1 — frozen zero-call protocol

Parent: `0ccc3889a4c7efcfa413e476f4994df647f206d5` (`research/model-recovery-proposal-v0`). This protocol is committed before implementation or campaign execution. **ZERO model calls**, no prompt/parser, no automatic Recovery model campaign. Historical sources, evidence, main and tags remain unchanged.

## Question and permitted change

Expose only a replacement-state value at the existing post-Measure, post-quarantine native state-Recovery call site. Use a separate package and a subclass with a mechanically checked copy of `_complete_pair`; its sole semantic edit replaces the inline native proposal expression with an explicit helper. Inherit the ordinary state authorizer and realized-event staged wrapper unchanged. Do not change the trigger, branches, counters, publication or fault paths.

The helper owns one native `Recovery` object for an opportunity. It consumes its native `state_candidate` attempt first. Without a source it returns the native candidate unchanged. With a source it calls `propose(context)` once, admits only `type(value) is int` in `range(4)`, and replaces only `value` in the native immutable candidate. The trusted native envelope owns epoch, transaction, pair identity and RECOVERING status. No coercion, retry, fallback, callback authorization or direct publication. Ordinary proposer exceptions become safe rejection through the existing atomic wrapper.

Context is a frozen scalar-only dataclass with exactly: `epoch`, `transaction_id`, `pair_decision_id`, `pre_state`, `action`, `next_state`, `consequence`, `measurement_matches`. No receipt object, authorizer, verdict, Map, Memory, package, continuation or executor capability. The native input is an audited PairDecision; the helper does not introduce a new verifier.

## Fixed diagnostic matrix

1. Run all previous 32 diagnostic cases through historical and new default paths with the same fixtures, names, fault flags, evidence and read-only observer. Require byte-identical serialized case records and native proposal/authorization semantics. Compare the historical run to the retained canonical diagnostic. Do not change the old checkpoint's blocked result.
2. All eight genuine ADVANCE/RETREAT fixtures, one S failure each: correct external value and cyclic wrong external value (16 transactions; all four realized targets).
3. Admission/failure controls on state 1 ADVANCE: values −1, 4, True, 1.0, None, string, list, tuple, arbitrary object; mappings for each of AUTHORIZED, verified, approved, receipt_id, package_id, grant, continuation; a full StateCandidate object; ordinary callback exception; implicit no-return; an int subclass. These 20 controls must reject before state authorization without fallback.
4. Registered no-Recovery cases with a source that raises if called: eight HOLD S/SC cases plus four HOLD consequence-only cases. Zero callbacks and native state attempts.
5. One default `failed_recovery=True` rejection already included in the exact 32-case comparison. An external wrong value must not be silently repaired.
6. For each genuine fixture, invoke a trusted opportunity twice with a counting deterministic source. First invokes once; native second attempt raises before callback (historical counter increments to 2 on denial). The source receives no attempt owner or retry API. Rejected full transactions deny a subsequent begin request without a second invocation.
7. Low-level candidate controls on each of the eight receipt-grounded decisions: wrong epoch, transaction, pair ID and status, using a fresh unchanged authorizer each time. Compare the historical authorizer with the new path's actual authorizer. These controls are outside the value-only API; no authority monkey-patching.
8. Two-step retained-Memory checks: successful HOLD history followed by correct and wrong state Recovery (two matched sequences). Verify old history and prediction preservation and full atomic rejection. These are additional minimal preservation controls, not a new world or fault campaign.

All transactions execute the unchanged world through the authentic external boundary. Deterministic Explorer and Map only. Wrong Map next state is `(registered_actual_next_state+1)%4`; S/SC follow the prior diagnostic. Invalid incumbent is required; HOLD never manufactures Recovery.

## Required observations

Correct: one native attempt, one callback, trusted envelope, existing authorizer accepts, receipt-consistent Map/Memory commit. Wrong: one callback, existing authorizer rejects, zero commit delta, unchanged published Map/quarantines/Memory/pairs/packages and denial of continuation. Malformed/failing: one consumed native attempt, at most one callback, no state authorization, identical rejection guarantees. Every case preserves exact receipt and original latched prediction. Observe verified Measure → quarantine → native attempt → callback → ordinary authorization → publication; compare uninstrumented duplicates for identical protected outcomes and counts. Check all inherited bounds.

Detailed local evidence stays outside public source. Public artifacts include compact results, source/evidence hashes, reproduction instructions and actual regression statuses. Exact campaign replay must match deterministic evidence and compact results byte-for-byte without inference.

## Frozen completion rules and known specification conflict

**A — STATE RECOVERY PROPOSAL INTERFACE READY** requires all 16 requested completion criteria: default equivalence; correct accept; wrong reject; malformed safe rejection; value-only source; trusted identity/status/budget; one invocation per opportunity; no invocation without Recovery; failure closed; atomic rejection; unchanged receipt/prediction; unchanged independent authorizer; unchanged bounds; zero protected false accepts; exact replay; historical regressions. All mandatory controls must also meet their requested expectations.

**B — AUTHORITY / CORE SEMANTIC REGRESSION** takes precedence if the new interface causes a protected false accept, bypass, receipt rewrite, identity forgery acceptance, extra attempt, unexpected invocation or partial protected publication compared with the historical implementation.

**C — NOT ESTABLISHED** applies to another unmet mandatory requirement. Source inspection before implementation found that the unchanged authorizer checks epoch/transaction/pair/value but does not check status. Therefore the requested wrong-status rejection may be incompatible with keeping its logic unchanged. Test and disclose actual acceptance; do not silently add a verifier, redefine status as validated, omit the control or classify A despite its failure. If the same status acceptance is reproduced in both old and new low-level paths and normal API status cannot be supplied, classify C with a pre-existing requirement conflict, not a new B regression. If the new path adds an acceptance absent historically, classify B. Report normal-interface false accepts separately from low-level status-control acceptances.

## Regression and stop

Run campaign + exact replay, new boundary/budget/atomicity unit tests and the prior checkpoint's actual 25-command regression set (including its expected exit-2 blocked gate). This includes Map v1/v0, Explorer v1/feasibility/factorial/semantic/adaptive/Memory/original, realized-event campaign/replay, minimum repair 1, base v0/v1/v2 and old contradiction-v0 expected failure. Preserve results and source bytes. No live inference, source optimization, main/tag change or push. Report 33 requested sections and stop regardless of classification.
