# Composition input bindings v1 — prospective zero-call protocol

Parent `106e43134e786820aff4d7228fe58f7a73a29630`; composition-v0 remains C — NOT
ESTABLISHED. Implement only new Explorer/Map input bindings alongside historical
sources. Zero model calls. No authority changes, live runner, push, or automatic
follow-up. Freeze this document before implementation and campaign execution.

Question: can fixture-specific input adapters support the existing finite domain
and empty experience while preserving parsers, authority and historical behavior?

## Frozen projections and binding

Explorer JSON: `state`, `actions`; each action entry contains opaque `action` and
`verified_outcomes`, either the string `UNTRIED` or a chronological list of observed
integer consequences. Sort records by (epoch, transaction_id), filter authorized
records for the current state and offered action. All three actions remain offered,
including negative, unobserved and conflicting histories. No invented observation.
This new shape is needed because historical opaque renderers require complete
experience. Compare complete-history evidence/order with the old shape explicitly;
old Explorer bytes and code remain unchanged.

Map JSON remains exactly `state`, `target_action`, `VERIFIED_CHRONOLOGICAL_HISTORY`.
Rows retain the historical fields transaction_id, surface_action, next_state,
consequence, filtered to the current state and admitted action, sorted by
(epoch,transaction_id). At state 1/HOLD require exact historical serialized bytes.
Empty pair history is []. No default prior or copied other-pair observation.
Serialize with sorted keys and compact separators; no canonical action names.

One validated mapping per episode: O1=(K1,K2,K3) or O2=(Q7,M4,Z2), bijectively paired
with all six permutations of (ADVANCE,HOLD,RETREAT), in that enumeration order.
Reuse the historical opaque Explorer parser, Map finite JSON parser, and unchanged
Recovery v1 parser/proposer. Preserve generate(prompt, seed) transport semantics.
Transport sees strings/scalars only, never stores, receipts or authority objects.

Explorer receives the existing coordinator's audited records. Map references the
same staged Memory store, after existing Memory audit and ordinary action admission;
its predict method uses the framework-supplied finite action and current Map state.
Deepcopy must preserve the Map-to-staged-Memory reference, never a separate prompt
history store. Existing wrapper audits, Prediction latch and publication remain
unchanged. This trusted binding is not a new verifier or sandbox for arbitrary
Python callbacks. No role may supply identities, status, scope or verdicts.

## Frozen deterministic campaign

- 48 empty Explorer contexts: 4 states × 2 families × 6 mappings. Require three
  opaque UNTRIED entries, deterministic bytes, no record mutation or canonical text.
- Mixed histories in each state: ordinary published HOLD,HOLD,ADVANCE,RETREAT
  returns to the starting state with HOLD twice, ADVANCE once, RETREAT untried there.
  Project under all 12 mappings; preserve chronology/records and observed signs.
- Map: every 12 finite pair × 0/1/2 authentic prior observations × all 12 mappings.
  Construct histories through ordinary stationary-world receipt publication, using
  reverse action to return after ADVANCE/RETREAT; HOLD requires no return.
- Historical Map v0 and established-prior v1: reconstruct each registered context
  through original fixture functions and require exact new/old prompt bytes.
- Required first transactions: all three actions × all 12 mappings from state 0,
  empty Memory; use exact synthetic prediction and a raising no-Recovery sentinel.
- Genuine Recovery: from state 0, ADVANCE, wrong Map next_state=0/consequence=0;
  correct Recovery=1 versus legal wrong=2, for all 12 mappings. Reuse the unchanged
  one-call Recovery v1 proposer and repaired status-bound independent authorizer.
- No-Recovery controls: HOLD at every state with wrong prediction next_state and
  consequence; raising source must never be called despite Measure mismatch.
- One eight-decision episode, O1 mapping 0: HOLD,HOLD,ADVANCE,HOLD,RETREAT,HOLD,
  ADVANCE,HOLD. Exact synthetic predictions except decision index 2, where (0,0)
  induces genuine Recovery to 1 under the unchanged world. No world corruption.
  Capture every input, empty→experienced revisits, latch, authentic event, Measure,
  candidate/envelope, authorization, Memory, continuation and bounds. Only new
  authorized Memory supplies cross-decision evidence; no transcript carryover.
- Bounded malformed/capability controls at each role: reject cross-role schemas,
  extra identity/status/receipt/action/retry fields, invalid finite values and
  existing malformed examples. Check rejected Explorer never reaches Map; rejected
  Map never executes; rejected Recovery never publishes/continues/retries.
- Repeat a genuine Recovery opportunity on its same native owner and require no
  second proposer callback. Instrument native attempts, Measure, authorizer and
  receipt checks read-only; compare instrumented/uninstrumented protected traces.

All A–O composition properties require executed evidence: finite role control;
no cross-role action/prediction/receipt capability; immutable receipt/latch during
Recovery; genuine routing; one attempt; correct independent acceptance; atomic
wrong rejection; authentic Memory; staged coexistence; no post-rejection requests;
and inherited bounds. Static assertions alone cannot mark any property PASS.

## Frozen classification and completion

A — COMPOSITION INPUT BINDINGS READY only if all 17 user completion criteria pass:
empty-Memory UNTRIED; full Map domain/empty history; admitted action binding; coherent
aliases; actual state-0 execution; every A–O property reached; authentic sequential
experience and empty→observed transition; both Recovery paths; no raw-text leakage;
unchanged parsers/authority/core; zero protected false accepts; unchanged bounds;
exact replay; historical regressions. B — AUTHORITY / CORE REGRESSION for protected
failure or historical semantic regression; C — NOT ESTABLISHED for another unmet
requirement. No behavioral score or model-learning claim.

Privately retain full synthetic prompts/responses/transactions; publicly retain
compact results and verification. Replay all recorded synthetic responses with
zero inference and require identical evidence and summary. Run composition-v0
blocked replay and all 33 preceding historical regression commands, preserving
expected exit-2 negative checkpoints, plus meaningful new binding/routing tests.
Report all 37 requested sections. Even if A, stop without the 288-call campaign.
