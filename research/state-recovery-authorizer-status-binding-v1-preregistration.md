# State Recovery authorizer status binding v1 — frozen zero-call protocol

Parent `ed8b8f3f6fdae83bf0a9c8a5aff51c25ce35ed9b`; previous interface classification **C — NOT ESTABLISHED** remains unchanged. No model calls, historical source edits, main/tag changes or push. This protocol precedes implementation and status-matrix execution.

## Contract preflight and minimum scope

Source inspection found that v0 Recovery constructs its own older candidate with RECOVERING; v1 `Recovery.state_candidate` always creates `CrossAuthorityState.RECOVERING`, including its wrong-value fault path. V2 and realized-event grounding reuse the v1 core. Interface-v1 consumes that native candidate and replaces only value. No legitimate state-Recovery producer requiring another status was found. Historical tests/campaigns exercise native recovery, failed recovery, incumbent retention, ordinary replacement and epoch changes.

The shared authorizer also legitimately handles **non-Recovery PROPOSED** candidates: retained incumbent and ordinary measured replacement. A global RECOVERING-only predicate would regress those paths. Freeze a Recovery-scoped contract: forward the coordinator's already existing local `recovery_authorized` branch flag as a trusted keyword to the same repaired authorizer instance. The flag is true when a state-Recovery candidate was selected, before authorization; it is not an authorization verdict and is never supplied by the value-only source. Ordinary branches pass false. Do not derive this scope from candidate-controlled status. Default direct calls to the repaired authorizer use state-Recovery scope.

Add exactly one semantic rejection requirement in that scope: `candidate.status != CrossAuthorityState.RECOVERING` returns false. Delegate every remaining identity/value/duplicate/capacity check to the inherited authorizer. No second authorizer instance, new verifier, normalization, proposer fields, budget changes, retries or fallback. Implement in a separate package; copy the prior `_complete_pair` with only the authorization-call keyword addition, and inherit the proposal helper/wrapper. Ensure epoch reset reinstalls the same repaired authorizer type after the inherited reset, without changing counters or semantics.

If executable preflight finds a genuine successful state-Recovery producer with another status, STOP BEFORE REPAIR and report C. Ordinary non-Recovery PROPOSED candidates are explicitly a separate existing branch, not such a contradiction.

## Frozen status matrix

Enumerate every member of both existing status enums, keeping enum type/name in evidence:

- `CrossAuthorityState`: PROPOSED, OBSERVED_PARTIAL, OBSERVED_PAIRED, DISAGREEMENT, REOBSERVING, MEASURED, QUARANTINED, RECOVERING, AUTHORIZED, REJECTED.
- v0 `AuthorityState`: PROPOSED, OBSERVED, MEASURED, QUARANTINED, RECOVERING, AUTHORIZED, REJECTED.

The typed dataclass does not enforce enum class at runtime. Both are string enums; the requested equality predicate admits the semantic RECOVERING value from either enum. Do not add a separate enum-class/type requirement. All 15 other typed entries reject in Recovery scope. No invented strings. Use each of the eight authentic genuine Recovery decisions: **136 direct comparisons**, fresh authorizer instances. Historical acceptance remains visible separately. No duplicate/capacity state is reused between independent matrix cells.

## Bounded tests

1. Executable source/creation-site preflight plus the unchanged interface campaign demonstrates that all observed native/injected Recovery envelopes are RECOVERING; ordinary PROPOSED paths are distinguished. Compare inherited interface campaign bytes to its retained evidence.
2. Run the entire prior interface campaign through the repaired path: 32 default cases, 52 injected-path transactions, eight budget cases and 32 identity/status controls. Do not alter its historical code or its old C classification. In the new harness require protected outcomes byte-identical for all valid and safe-rejected ordinary transactions; only the eight low-level wrong-status acceptances change to rejection. Observe repaired status rejection separately from delegation to the inherited authorizer.
3. Run the full 136-cell status matrix. RECOVERING candidates must have exactly historical outcomes; all other statuses reject in Recovery scope. Preserve the original REJECTED before/after witness for every genuine fixture.
4. Eight decisions × five RECOVERING/combined-invalid cases: wrong epoch, transaction, pair, value, and wrong value + REJECTED status. All 40 comparisons reject historically and after repair.
5. Transaction-capable **test-only** core subclasses change only status after the normal native attempt and correct value callback. Eight genuine fixtures × REJECTED/PROPOSED/AUTHORIZED = **24 transactions**, all rejected by the repaired authorizer in trusted Recovery scope. The normal proposer API remains unchanged. Add a two-step HOLD-history → wrong-status ADVANCE sequence to test retained Memory. Before-submit continuation is already false after begin; wrong-status rejection must keep it false, commit_delta 0 and Map/quarantines/Memory/pairs/packages unchanged. Preserve receipt and latched prediction; no second callback/begin execution.
6. Test duplicate and authorization-capacity behavior using RECOVERING candidates against historical and repaired authorizers; rejected wrong statuses must not consume authorization identities. Test epoch reset and a clean ordinary measured replacement to detect scope/reset regressions.
7. Read-only instrumentation requires uninstrumented duplicates with identical protected outputs. Campaign and compact results replay byte-for-byte. Detailed logs stay private.

## Frozen completion and stop

A — STATE RECOVERY STATUS BINDING COMPLETE only if all 16 requested criteria pass: unambiguous Recovery contract; valid RECOVERING behavior preserved; wrong statuses reject; identity/value rejection; value-only proposer; correct injected acceptance; wrong injected rejection; malformed rejection; unchanged no-Recovery controls; native budget; atomic wrong-status transaction rejection; receipt/prediction/history preservation; zero repaired protected false accepts; exact replay; historical regressions; preserved old-authorizer negative witness.

B — CORE / AUTHORITY REGRESSION takes precedence for a new protected false accept, bypass, legitimate Recovery rejection, retry leak or publication error. C — NOT ESTABLISHED for another unmet criterion. A requires completed replay/regressions, not only an initially passing campaign.

Run the new campaign/replay/tests plus all 28 inherited interface-v1 regression commands. Historical C/blocked/expected-failure outcomes must remain unchanged. Preserve all inherited source/result bytes except root README append and manifest refresh. Create the 30-section report and stop even on A. No model Recovery campaign, prompt/parser or inference transport.
