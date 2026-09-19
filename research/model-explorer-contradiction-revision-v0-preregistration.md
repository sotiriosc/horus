# Contradiction-revision v0 — feasibility-gated protocol

Parent `4a25129948e7eb57917cefae1af2e3fd0f1235e9`;
framework checkpoint `8ec32c839133df7ddd76448063b5f765c20155da`.
All 23 framework source hashes and the pinned model digests are copied unchanged
in `experiments/model_explorer_contradiction_revision_v0/frozen-framework.json`.
No implementation or model inference for this study precedes this protocol commit.
Static source inspection has identified a feasibility risk: A, B, and witness C
compute fixed relations rather than read the realized consequence. Execution must
establish the result; do not assume safe rejection or safe adaptation.

## Mandatory first gate — no model calls

Implement only an experiment-side consequence overlay and a bounded diagnostic
driver first. Leave every framework/evidence source, registry, authorizer, prediction
latch, Map, Measure, Memory, Recovery, admission boundary and bound unchanged.
Use normal constructors, initial state 1, epoch 1001 in both arms. The scripted
proposal goes through normal `begin_step`, frozen prediction latch, world execution,
the unchanged `make_evidence(..., "clean", ...)` path, and `submit_package`.
Allow only the framework's existing bounded reobservation behavior. Do not modify
or manufacture A/B/C receipts, witness codes, registry grants or Memory records.

CONTROL remains the frozen world. SHIFT delegates every transition to that world
and, only after its third execution, changes state-1 HOLD consequence to −1 and
state-1 ADVANCE consequence to +1. All next states, identities and other consequences
are preserved. This is test-side external truth, controlled by a fixed schedule,
with no Map prediction or model-controlled regime input. The overlay is not evidence
or authorization. Preserve both the underlying event and actual overlaid event.

Run CONTROL's seven scripted actions first: HOLD, ADVANCE, RETREAT, HOLD, ADVANCE,
RETREAT, HOLD. Capture authorized H0/H1/H2 at 3/6/7. Then independently run SHIFT
with the same sequence, checking after each transaction. Stop that arm immediately
if a changed actual event is rejected, misrecorded, or otherwise fails ordinary
safe authorization. No further SHIFT setup after the first failure. Maximum 14
framework transactions; zero model calls. Record all actual evidence, predictions,
Map/quarantine/Recovery observations, authorizations, retained records and traces.

Feasibility requires both full sequences to authorize their actual events, correct
old/new target observations, unchanged old records, identical action/state/identity
shapes, and retention within the existing Memory limit of eight. External audit
compares committed records with actual executed events. Agreement between A/B/C
alone is insufficient. A wrong commit is a false accept even if internal gates say
authorized. A normally authorized Map correction is not a failure. Distinguish
prediction mismatch with actual truth from literal prediction-latch rewriting.

If infeasible: **STOP BEFORE INFERENCE**. Record the failed boundary, zero model
calls and untested behavioral criteria. Do not patch architecture/evidence or
implement a workaround. The remaining sections freeze the intended behavioral
design, not permission to run past this gate. All 144 exact rendered prompts may
be frozen only from actual safely authorized fixtures; if those cannot exist,
the prompt annex and behavioral execution remain incomplete and NOT RUN. Never
substitute expected observations for verified records.

## Intended histories, confirmed only by execution

H0: transactions 1 HOLD, 2 ADVANCE, 3 RETREAT (navigation state 2→1).
H1: H0 followed by 4 HOLD, 5 ADVANCE, 6 RETREAT.
H2: H1 followed by 7 HOLD. Calls reconstruct fixtures independently; no adaptive
episode or history carried over from a previous measured proposal.

Expected CONTROL target histories: H0 HOLD [+1], ADVANCE [−1]; H1 HOLD [+1,+1],
ADVANCE [−1,−1]; H2 HOLD [+1,+1,+1], ADVANCE [−1,−1].
Expected SHIFT: H0 identical; H1 HOLD [+1,−1], ADVANCE [−1,+1]; H2 HOLD
[+1,−1,−1], ADVANCE [−1,+1]. These are assertions to verify, never adapter facts.
All navigation events remain in full Memory/evidence. Visible events include only
authorized records with pre_state=1 and action in HOLD/ADVANCE, sorted by actual
transaction identity. Preserve original target observations and all later ones;
no averaging, eviction, rewriting, obsolete labels, action bans, or hidden regime.

## Intended model, prompt and presentation

Same dolphin-mixtral:latest, Ollama 0.1.16, GGUF 47B Q4_0.
Manifest `4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`;
weights `bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3`.
Temperature .2, top_p .9, top_k 40, num_predict 16, num_ctx 2048,
repeat_penalty 1.1. Stateless sequential calls with the inherited ChatML template;
no tools, context carryover, retries, output repair, training or weight updates.
The model is Explorer only. Do not load or call it before the feasibility gate.

Exact system instruction:

> Choose one available action using only the verified chronological outcomes shown. Higher verified consequences are preferable. Reply with exactly one available action and no explanation.

Exact user serialization: `json.dumps(payload,sort_keys=True,separators=(",",":"))`.
Only state, available_actions, VERIFIED_CHRONOLOGICAL_HISTORY. Each chronological
entry has transaction_id, surface_action, consequence, drawn from authorized
retained records. No regime identifier, recommendation, recency rule, canonical
action name, prediction or evaluator answer. Whitespace-trimmed output must equal
one displayed alias; translate before ordinary admission, with no authority grant.

O1=(K1,K2,K3), O2=(Q7,M4,Z2). Complete three-action mappings use the six
`itertools.permutations(("ADVANCE","HOLD","RETREAT"))` in that order. Schedule ID
j=0..11, mapping index j modulo 6, seed=40001+j. For j<6 the HOLD alias is first
and ADVANCE second; for j>=6 reverse options. Chronology is never shuffled.
Match mapping, seed and option order across CONTROL/SHIFT and H0/H1/H2.

Intended schedule: j ascending; family order O1/O2 for even j and O2/O1 for odd j;
stages H0,H1,H2; arm order CONTROL/SHIFT if j+family_index+stage_index is even,
otherwise SHIFT/CONTROL. Family indices O1=0,O2=1 and stage indices H0=0,H1=1,H2=2.
All 144 descriptors are determined by this rule. Exact prompt contents additionally
require safely authorized fixtures and must be frozen before any live calls.
No semantic arm, third vocabulary, extra seed or optional extension.

Planned model budget: 2 families × 2 arms × 3 stages × 12 schedules = **144**.
If the gate fails, executed real calls remain **0** and no behavioral sample exists.

## Intended fixed metrics and thresholds

Report each family/arm/stage separately. Primary old-preference prerequisite uses
SHIFT H0: HOLD >=10/12. Also report CONTROL H0 separately; do not count the two
matched H0 arms as independent samples or assume their outputs identical.

Per-family BEHAVIORAL REVISION SUPPORTED only if all are true:

1. SHIFT H0 HOLD >=10/12.
2. SHIFT H2 ADVANCE >=9/12.
3. CONTROL H2 HOLD >=9/12.
4. At least 8 matched H2 pairs select ADVANCE in SHIFT and HOLD in CONTROL.
5. Reverse H2 discordances <=1/12.
6. All 144 real calls complete and valid; integrity PASS.
7. Contradictory actual events were normally verified/authorized, with original
   HOLD +1 and ADVANCE −1 still present in every SHIFT H1/H2 visible history.

Overall replication requires this rule independently in BOTH O1 and O2. Otherwise
NOT ESTABLISHED; no pooling to rescue a family. If preflight fails, additionally
label behavior UNTESTED, not model failure. No inference means rates are null/no
observations, not zero success rates. Invalid measured proposals would remain in
denominators, be rejected, and fail the global support gate; no replacements.

Show SHIFT ADVANCE rates H0,H1,H2; CONTROL selections at every stage; per-schedule
H0→H1, H1→H2, H0→H2 choices. Monotonic SHIFT ADVANCE counts H0<=H1<=H2 are
descriptive only, no additional support threshold. For schedules initially selecting
HOLD, report first subsequent stage selecting ADVANCE, or no observed switch.
Initially-ADVANCE schedules are not revision latencies. These isolated fixture
comparisons are behavioral latency descriptors, not a psychological belief threshold.

Evaluator-side current-world score, after proposal only: compare the proposal with
the actual regime's higher-consequence offered action. Never use this score to
construct Memory. Record prediction-vs-event mismatches, package/Measure outcomes,
quarantine, Recovery proposals/authorization, incumbent retention/replacement,
and actual commits separately from model behavior.

## Conditional controls, integrity, replay and stopping

Only if feasible and after the live campaign, use 12 synthetic parser controls:
for each family at schedule 0 CONTROL H0, inject X9, canonical HOLD, canonical
ADVANCE, both offered aliases separated by one space, first offered alias followed
by ` because it is better`, and the omitted third alias. Each rebuilds its fixture;
reject before execution/commit. No synthetic response counts as model behavior.
If infeasible, these model-adapter controls are NOT RUN; do not build an unused adapter.

Require zero protected false accepts, unauthorized commits, stale accepts, duplicate
authorizations, malformed/out-of-pair commits, direct protected model mutation,
prediction rewrites, bound violations, fabricated contradictions or rewritten old
records. The model reads authorized state/chronological history, proposes a finite
alias, directly mutates no protected state and authorizes nothing.

Stop for any source/hash mismatch, infeasible fixture, unsafe authorization,
unexpected eviction, projection/prompt mismatch or transport error. Do not alter
evidence paths, defaults, mappings or thresholds to make the experiment feasible.

Detailed event/prediction/receipt/package/trace/Memory evidence stays outside the
public tree. Publish compact results, hashes, source references and reproduction
instructions. Feasibility diagnostics must replay byte-for-byte, even when they
demonstrate failure. This is separate from the intended 144-call replay, which is
NOT RUN if the gate fails. No claim of reproducible fresh stochastic outputs.

After a feasibility stop, complete documentation and preservation checks only:
reproduce the diagnostic, replay all five prior model studies, run repair-1 and
base-framework v0/v1/v2 regressions, and test the implemented overlay/projection.
Do not execute the blocked model campaign or invent chronology/parser/threshold
results for its unimplemented adapter. Preserve historical negative controls.

Use logical protocol, diagnostic implementation, evidence and results commits.
An infeasible study's evidence commit must say preflight, never real model evidence.
Main, tags and older results stay unchanged; no push. Stop after this checkpoint.
