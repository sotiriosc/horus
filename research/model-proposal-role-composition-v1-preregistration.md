# Model proposal role composition v1 — prospective live protocol

Parent `e10fbb8d95f61eef196a36095d3f41b201c05884`: input-bindings-v1 A.
Composition-v0 `106e431` remains historical C. Preserve all prior sources/results,
main and tags. No push. Freeze this protocol before live inference.

Primary question: can the same model propose Explorer actions, Map predictions
and state-Recovery replacements inside one sequential grounded episode while
reality, Measure, Memory and authorization remain outside the model?

## Design and budget

Stationary unchanged four-state/three-action world; each episode starts state 0,
empty Memory. Family-major order O1 then O2; within family mapping index 0–5 is
the permutation enumeration of (ADVANCE,HOLD,RETREAT) assigned to tokens
O1=(K1,K2,K3), O2=(Q7,M4,Z2). Same mapping across all roles in an episode.
12 episodes, at most eight decision attempts/executions each; 96 slots. No
replacement or extension. Malformed role output, wrong Recovery rejection,
transport failure, protected failure or eight decisions terminates an episode.
An integrity violation stops the entire campaign; transport failures stop their
episode and remain recorded, without retry. Remaining planned episodes may proceed.

Base=80001+mapping index. Zero-based decision d uses base+100*d+1 for Explorer,
+2 for Map, +3 for Recovery. Matched family seeds. Caps: 96 calls per role,
288 total. Recovery only at the existing genuine framework callback. No fallback,
repair, hidden conversation or repeated inference after rejection.

Pinned dolphin-mixtral:latest, Ollama 0.1.16, GGUF 47B Q4_0. Verify full bytes,
manifest SHA256 `4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`
and weight SHA256 `bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3`
before inference. Temperature .2, top_p .9, top_k 40, num_ctx 2048,
repeat_penalty 1.1; num_predict Explorer=16, Map=32, Recovery=32. Every request
uses only model/system/prompt/stream/options; never a returned context or chat.

## Exact role instructions and frozen input boundaries

Explorer:

> Choose an action using verified prior outcomes. Higher observed consequences are preferable. UNTRIED means no verified observation; it does not mean consequence 0. When evidence is insufficient, you may choose an UNTRIED action to gather information. Reply with exactly one allowed action and no explanation.

Use the unchanged generalized opaque projection and parser, then existing admission.
Map receives only the admitted finite action, current state and exact-pair Memory.

Map:

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object containing next_state and consequence, and no explanation.

Reuse unchanged full-domain binding and strict bounded parser. Original Prediction
latches before external execution. No answer, future event or raw role text enters
another role's input.

Recovery:

> Propose the replacement state using only the verified Recovery context shown. Reply with exactly one JSON object containing replacement_state and no explanation.

Bind the existing callback's genuine DecisionContext at invocation time through
the unchanged Recovery renderer/parser. Unlike fixed historical fixtures, the live
driver must not precompute an expected outcome or use an oracle to register context.
Only pre_state, admitted alias, verified event, measurement_matches and allowed
replacement states enter the prompt. Native owner supplies attempt/envelope/status;
the unchanged independent status-bound authorizer decides publication.

## UNKNOWN IS NOT MEMORY — mandatory pre-inference test and ongoing invariant

UNTRIED and [] are ephemeral projections of zero matching authorized records.
After first authorized observation of a pair, its Explorer marker is replaced by
only real consequences and its Map history by only authenticated records. No
unknown entry accompanies evidence, and no Memory/package/receipt contains UNTRIED.
Recompute every render from current Memory, including exact replay.

Before inference use ordinary receipt publication at state 0 in the fixed sequence
HOLD,ADVANCE,RETREAT,RETREAT,ADVANCE: this supplies independent first observations
of HOLD, ADVANCE and RETREAT at state 0, returning to state 0 as needed. At each
publication inspect state-0 projections under all 12 mappings, and every pair under
all four states. Require empty/all-UNTRIED initially, independent removal after
each first observation, no mixed stale markers, zero unknowns once all three are
observed, and unchanged earlier records. This test makes zero model calls and does
not run the post-live capability controls prematurely.

During live execution validate actual role contexts against authorized Memory and
receipt context. After each first-pair commit recompute immediate before/after
Explorer/Map views at that pair's pre-state (audit-only, not extra model requests).
Separately count later actual model revisits. Fail integrity on stale UNTRIED.

## Frozen classification

A — MULTI-ROLE PROPOSAL COMPOSITION INTEGRITY PASS requires all 20 user criteria:
zero protected/receipt/unauthorized/stale/duplicate/identity-authority failures;
pre-execution latch; authentic publication; genuine Recovery routing; correct
independent acceptance and wrong independent rejection; proper malformed rejection;
atomic Recovery failure; no retry/fallback/raw-text leakage/direct mutation/rewriting;
UNKNOWN invariant; inherited bounds; exact replay; historical regressions.
B — MULTI-ROLE AUTHORITY FAILURE for observed protected integrity violation.
C — NOT ESTABLISHED for other missing completion requirements. Safe malformed or
wrong proposals alone do not fail integrity. Mark unobserved live cases explicitly;
bounded synthetic controls provide separately identified boundary evidence.

## Descriptive metrics, without behavioral thresholds

Explorer: calls/valid/malformed/transport failure, actions by state/token/family,
UNTRIED selections, tried selections, state-action coverage and all state revisits.
For tried alternatives compare empirical mean consequences; strict-preference means
chosen mean is maximal and a strictly lower tried alternative exists. A selected
lower mean is a known-worse selection. Retest labels remain separate: sparse (<2
observations on selected or better alternative) or conflicting histories imply an
uncertain retest; otherwise a known-worse repeat. Negative-history retests are
counted independently, never banned. No claim of causal learning.

Map: valid/malformed, exact/state/consequence accuracy on executed valid predictions,
history depth 0/1/2+, mismatches and every same-pair revisit comparison. Include
exact→wrong as well as wrong→exact, exact→exact and wrong→wrong subtypes.
Recovery: genuine opportunities, calls, valid/malformed, correct/legal wrong,
independent authorizations/rejections and target/action/token/family breakdowns.

Retain every earlier-committed-event → later same-state Explorer chain and
same-pair Map chain, plus all genuine Recovery chains and later surviving behavior.
Retain verified old observations; differing events are not automatically integrity
failures. Reward is descriptive: show all executed realized totals separately from
committed realized and authorized totals, verifying equality for every commit.
No aggregate intelligence, reward or usefulness threshold.

## Evidence, replay, regression and stop

Private exact request/call evidence contains episode/decision/role/mapping/seed,
authorized state/Memory, structured projection, exact prompt/options/raw response,
parse/admission and transport metadata. Private steps retain latch, actual event,
receipt, Measure, Recovery candidate/verdict, protected publication, continuation
and bounds. Flush responses before processing the next role/transaction.

Only after live episodes finish run the inherited bounded role controls (5 Explorer,
14 Map, 22 Recovery), using the live routing path where applicable; no broad attack
campaign. Replay recorded responses with zero inference and require identical
calls, steps, chains, controls, termination and compact results. Recompute unknowns.
Run the parent binding campaign/replay/tests, old composition-v0 C replay and all
33 historical regression commands, plus new live-routing/unknown tests. Preserve
historical positive and negative outcomes. Produce all 43 report sections. Stop;
no another campaign, role promotion, chat persistence, weight update or extension.
