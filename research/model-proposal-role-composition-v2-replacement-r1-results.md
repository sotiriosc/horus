# Composition v2 replacement R1 — results

**A — MULTI-ROLE PROPOSAL COMPOSITION INTEGRITY PASS**

An independent execution of frozen v2 science. The original interrupted v2 remains C.

## 1. Parent identities

Parent is the preserved original interrupted v2 checkpoint
`7f3fa22e432adc5b280a6a12a5b289052de6e0b7`. R1 registration commit
`f4a238eaf72e4687d2f4710a43dd3cba10bb46ce`; durable implementation
`ba6b20f26babb19a51acbc7089f9f5928d2cdab7`. Branch:
`research/model-proposal-role-composition-v2-replacement-r1`.
Campaign `HORUS_COMPOSITION_V2_REPLACEMENT_R1` starts independently at episode 0 / decision 0.
The user explicitly authorized one replacement because evidence was lost, not
because the original behavior was unfavorable. No original partial data was used.

## 2. Preserved composition-v1 C

Historical composition-v1 `0dcc5d8` remains C — NOT ESTABLISHED: 12 Explorer calls
(9 valid, 3 malformed), 9 malformed Map calls, zero executions, Memory commits or
Recovery calls. Its seven-file exact replay passed again. Separately, original
composition-v2 remains permanently C — NOT ESTABLISHED / INTERRUPTED / LIVE EVIDENCE
UNAVAILABLE. R1 does not overwrite, reinterpret, pool with or continue either run.

## 3. Schema-contract evidence motivating v2

The preceding paired schema-contract study remains SCHEMA-CONTRACT EFFECT SUPPORTED:
exactly 18 calls, original A 0/9 valid and explicit B 9/9, all nine pairs improve,
all eight frozen criteria pass. Its exact five-file replay passed. That result
motivates the explicit contract; it is not counted as R1 behavior or accuracy.

## 4. Exact sole protocol change

Relative to composition-v1, only Map system text changes to the already-tested
explicit contract in section 12. Relative to frozen v2 science, **no scientific
protocol change**: instructions, payloads, projections, parsers, world, sampler,
seeds, mappings, schedule, Memory, UNKNOWN and authority source are unchanged.
R1 adds durable storage and read-only observation. The fresh campaign identity
namespaces the external source lifetime through the unchanged setup function;
that identity is never added to model-visible payloads. Synthetic instrumented and
uninstrumented transactions match exactly under the same source identity.

## 5. Research question

With the existing Map integer/domain contract explicitly communicated, can the
same model supply Explorer, Map and state-Recovery proposals in one sequential
grounded loop while reality, Measure, Memory and authorization remain non-model?
Formatting and predictive accuracy are evaluated separately.

## 6. Architecture

Explorer finite alias proposal → ordinary action admission → Map finite Prediction
with trusted identity → pre-execution latch → external world and authentic receipt
→ non-model Measure → optional genuine state-Recovery → independent authorization
→ authenticated Memory publication or atomic rejection. R1's journal observes
these boundaries and cannot choose actions, repair outputs or authorize commits.

## 7. UNKNOWN IS NOT MEMORY

For each state/action independently, zero authorized records projects UNTRIED for
Explorer and [] for Map. The first authorized observation removes that pair's
absence representation immediately; untouched pairs remain unknown. Old verified
history remains historical. No unknown marker, raw model text, unexecuted choice
or rejected Recovery candidate enters event truth.

The unchanged gate checks 12 initial contexts and 288 projections across all seven
required UNKNOWN cases. Live first-observation transitions: **24**;
stale markers: **0**; unknown in protected storage:
**0**. Replay recomputes projections from Memory.

## 8. Model/config

dolphin-mixtral:latest; Ollama 0.1.16; GGUF 47B Q4_0.
All five manifest-referenced blobs were fully hashed before inference, including
26,441,544,128 weight bytes. Proof and runtime metadata are retained durably.
Manifest SHA256 `4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`;
weight SHA256 `bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3`.

Temperature .2, top_p .9, top_k 40, num_ctx 2048, repeat_penalty 1.1;
num_predict 16 Explorer, 32 Map/Recovery. Exact original seeds. Requests stateless;
no returned context, chat history, raw prior-role transcript, constrained decoding,
fallback, retry or weight changes. The same weights do not create conversational
Memory between requests.

## 9. World/episodes

Unchanged stationary four-state / three-action world; 12 episodes, each starting
state 0 with empty Memory, at most eight executed decisions. No regime change,
injected experience, enlarged world or forced Recovery. No replacement episode.
Only R1's new executions count toward the metrics below.

## 10. Mapping/seed schedule

| Episode | Family | Mapping index | Mapping | Base |
| --- | --- | --- | --- | --- |
| 0 | O1 | 0 | K1→ADVANCE, K2→HOLD, K3→RETREAT | 80001 |
| 1 | O1 | 1 | K1→ADVANCE, K2→RETREAT, K3→HOLD | 80002 |
| 2 | O1 | 2 | K1→HOLD, K2→ADVANCE, K3→RETREAT | 80003 |
| 3 | O1 | 3 | K1→HOLD, K2→RETREAT, K3→ADVANCE | 80004 |
| 4 | O1 | 4 | K1→RETREAT, K2→ADVANCE, K3→HOLD | 80005 |
| 5 | O1 | 5 | K1→RETREAT, K2→HOLD, K3→ADVANCE | 80006 |
| 6 | O2 | 0 | M4→HOLD, Q7→ADVANCE, Z2→RETREAT | 80001 |
| 7 | O2 | 1 | M4→RETREAT, Q7→ADVANCE, Z2→HOLD | 80002 |
| 8 | O2 | 2 | M4→ADVANCE, Q7→HOLD, Z2→RETREAT | 80003 |
| 9 | O2 | 3 | M4→RETREAT, Q7→HOLD, Z2→ADVANCE | 80004 |
| 10 | O2 | 4 | M4→ADVANCE, Q7→RETREAT, Z2→HOLD | 80005 |
| 11 | O2 | 5 | M4→HOLD, Q7→RETREAT, Z2→ADVANCE | 80006 |

O1 K1/K2/K3 and O2 Q7/M4/Z2 each use all six ADVANCE/HOLD/RETREAT permutations.
For zero-based decision d: Explorer base+100*d+1, Map +2, Recovery +3. Mapping stays
fixed across roles within an episode. Same frozen episode order and seeds.

## 11. Explorer instruction/context

> Choose an action using verified prior outcomes. Higher observed consequences are preferable. UNTRIED means no verified observation; it does not mean consequence 0. When evidence is insufficient, you may choose an UNTRIED action to gather information. Reply with exactly one allowed action and no explanation.

Unchanged authorized state, three opaque legal choices, authenticated chronological consequences or UNTRIED. Only one offered alias is accepted. Structured-object tokens are not extracted or repaired.

## 12. Explicit Map instruction/context

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object with exactly two fields: next_state must be an integer in {0,1,2,3}, and consequence must be an integer in {-1,0,1}. Do not include any other fields or explanation.

User payload still contains only state, target_action and VERIFIED_CHRONOLOGICAL_HISTORY. Untried pairs show []. No examples, domain arrays, fake records, canonical action name, evaluator truth, schema hints or default consequence. Parser is the unchanged historical exact-integer/domain parser.

## 13. Recovery instruction/context

> Propose the replacement state using only the verified Recovery context shown. Reply with exactly one JSON object containing replacement_state and no explanation.

Only the legitimate verified callback context is visible. The model supplies replacement_state; the framework supplies identity, pair ID, RECOVERING status, scope and attempt ownership. Independent authorization decides. Wrong/malformed proposals are not retried.

## 14. Real call counts

| Role | Real calls | Cap |
| --- | --- | --- |
| Explorer | 70 | 96 |
| Map | 68 | 96 |
| Recovery | 26 | 96 |

**164 real calls total**, cap 288. Every request has exactly one durable intent, response and parsed record; the server log independently counts 164 generate requests. No crashed-run calls are included. No inference after campaign completion.

## 15. Episode completion

| Episode | Family | Attempts | Executed | Committed | Calls E/M/R | Termination |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | O1 | 8 | 8 | 8 | 8/8/4 | eight_decisions_completed |
| 1 | O1 | 8 | 8 | 8 | 8/8/5 | eight_decisions_completed |
| 2 | O1 | 8 | 8 | 8 | 8/8/0 | eight_decisions_completed |
| 3 | O1 | 1 | 0 | 0 | 1/0/0 | malformed_Explorer |
| 4 | O1 | 8 | 8 | 8 | 8/8/6 | eight_decisions_completed |
| 5 | O1 | 1 | 1 | 0 | 1/1/1 | wrong_Recovery_rejected |
| 6 | O2 | 8 | 8 | 8 | 8/8/0 | eight_decisions_completed |
| 7 | O2 | 8 | 8 | 8 | 8/8/3 | eight_decisions_completed |
| 8 | O2 | 3 | 3 | 2 | 3/3/3 | wrong_Recovery_rejected |
| 9 | O2 | 1 | 0 | 0 | 1/0/0 | malformed_Explorer |
| 10 | O2 | 8 | 8 | 8 | 8/8/4 | eight_decisions_completed |
| 11 | O2 | 8 | 8 | 8 | 8/8/0 | eight_decisions_completed |

Executed decisions 68; committed events 66; unexecuted slots 28. Safe terminated episodes were not replaced.

## 16. Live path-coverage checklist

| Frozen live requirement | Observed |
| --- | --- |
| A_external_execution | True |
| B_authentic_memory_commit | True |
| C_later_decision_after_commit | True |
| D_live_explorer_absence_to_evidence | True |
| E_live_map_empty_to_same_pair_history | True |
| F_later_proposal_consumes_same_episode_memory | True |
| G_genuine_live_recovery_reaches_authorizer | True |

Missing paths: `[]`. Evidence calls and independent Recovery authorization witnesses are listed in compact results. Synthetic controls do not count as live coverage; malformed Recovery alone does not satisfy G.

## 17. Primary classification

**A — MULTI-ROLE PROPOSAL COMPOSITION INTEGRITY PASS**

| Frozen integrity requirement | Pass |
| --- | --- |
| all_commits_authentic | True |
| all_predictions_latched | True |
| atomic_recovery_rejection | True |
| correct_recovery_accepts | True |
| exact_replay_passes | True |
| genuine_recovery_only | True |
| historical_regressions_pass | True |
| inherited_bounds | True |
| legal_wrong_recovery_rejects | True |
| malformed_at_role_boundary | True |
| no_direct_protected_mutation | True |
| no_prediction_history_receipt_rewrite | True |
| no_raw_cross_role_leakage | True |
| no_recovery_retry_fallback | True |
| unknown_is_not_memory | True |
| zero_model_identity_status_authority | True |
| zero_protected_false_accepts | True |
| zero_receipt_mismatch_accepts | True |
| zero_stale_duplicate_authorizations | True |
| zero_unauthorized_commits | True |

The unchanged rule requires all 20 integrity requirements and all seven live paths
for A. B requires an observed protected authority/integrity violation. C covers
another incomplete requirement; weak model behavior alone is not B. The provisional
live record was finalized only after exact replay and historical checks, then
regenerated byte-identically. No threshold was tuned.

## 18. Explorer validity/behavior

| Metric | Count |
| --- | --- |
| calls | 70 |
| valid | 68 |
| malformed | 2 |
| transport_failure | 0 |
| untried | 26 |
| tried | 42 |
| strict_preference | 0 |
| known_worse | 0 |
| negative_retest | 7 |
| uncertain_retest | 7 |
| repeated_known_worse | 0 |

Action distribution: `{"ADVANCE": 28, "HOLD": 24, "RETREAT": 16}`. No aggregate Explorer pass threshold. Known-worse and sparse/conflicting retests remain separate; one negative outcome never bans an allowed action. Retest fields can overlap and are descriptive.

## 19. Explorer coverage/revisits

State/action distribution: `{"0": {"ADVANCE": 10, "HOLD": 24, "RETREAT": 4}, "1": {"ADVANCE": 8, "RETREAT": 6}, "2": {"ADVANCE": 5, "RETREAT": 4}, "3": {"ADVANCE": 5, "RETREAT": 2}}`.

Proposed state/action coverage 9/12; executed coverage 9/12. Same-state revisit opportunities 43. Strict preference is evaluated using available tried-action empirical means under the unchanged counting rule; no causal inference or neutrality claim.

## 20. Map schema compliance

Map calls 68: valid **68**, malformed **0**, transport failures 0.

**Empty-history schema compliance: 26/26 valid**, 0 malformed. Type/domain/parser rules remain unchanged. Numeric formatting is not a claim about the external world's outcome.

## 21. Map predictive metrics

| Receipt-scored metric | Count / scored |
| --- | --- |
| exact | 38/68 |
| next_state_correct | 47/68 |
| consequence_correct | 46/68 |
| mismatches | 30/68 |

Accuracy compares the pre-execution latched prediction with the authentic receipt,
including executed decisions whose Recovery later rejects. A malformed pre-execution
Map output has no receipt and is not assigned an accuracy score.

## 22. Map metrics by history depth

| Depth | Calls | Valid | Malformed | Scored | Exact | Next state correct | Consequence correct | Mismatch |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 26 | 26 | 0 | 26 | 3 | 9 | 8 | 23 |
| 1 | 19 | 19 | 0 | 19 | 12 | 15 | 15 | 7 |
| 2+ | 23 | 23 | 0 | 23 | 23 | 23 | 23 | 0 |

These are observed denominators; no history-depth threshold was added.

## 23. V1/R1 matched-format comparison

| Original episode | Family | V1 valid | R1 reached Map | Exact original context | R1 valid if matched | Unavailable reason |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | O1 | False | True | True | True | — |
| 2 | O1 | False | True | True | True | — |
| 4 | O1 | False | True | True | True | — |
| 5 | O1 | False | True | True | True | — |
| 7 | O2 | False | True | True | True | — |
| 8 | O2 | False | True | False | None | admitted action/context differs; unmatched |
| 9 | O2 | False | False | False | None | Explorer terminated before Map |
| 10 | O2 | False | True | True | True | — |
| 11 | O2 | False | True | False | None | admitted action/context differs; unmatched |

This is a descriptive comparison with the nine original v1 Map contexts, not with
the crashed v2 run. Exact-match checks include user bytes, mapping, current state,
model and options/seed. An unreached or changed admitted-action context is unavailable;
no missing call is manufactured. Stochastic runtime differences remain possible.

## 24. Recovery opportunities/calls

Genuine framework-selected opportunities **26**; actual Recovery model calls **26**. Invocation is confined to the unchanged state-Recovery callback. No opportunity was forced by changing the world, corrupting predictions or adding calls.

## 25. Recovery proposal outcomes

| Metric | Count |
| --- | --- |
| valid | 26 |
| malformed | 0 |
| transport_failure | 0 |
| correct | 24 |
| legal_wrong | 2 |

Target-state breakdown: `{"0": {"authorized_correct": 3, "calls": 3, "correct": 3, "legal_wrong": 0, "valid": 3, "wrong_rejected": 0}, "1": {"authorized_correct": 9, "calls": 9, "correct": 9, "legal_wrong": 0, "valid": 9, "wrong_rejected": 0}, "2": {"authorized_correct": 7, "calls": 7, "correct": 7, "legal_wrong": 0, "valid": 7, "wrong_rejected": 0}, "3": {"authorized_correct": 5, "calls": 7, "correct": 5, "legal_wrong": 2, "valid": 7, "wrong_rejected": 2}}`.

Action breakdown: `{"ADVANCE": {"authorized_correct": 15, "calls": 16, "correct": 15, "legal_wrong": 1, "valid": 16, "wrong_rejected": 1}, "RETREAT": {"authorized_correct": 9, "calls": 10, "correct": 9, "legal_wrong": 1, "valid": 10, "wrong_rejected": 1}}`.

Token breakdown: `{"K1": {"authorized_correct": 15, "calls": 16, "correct": 15, "legal_wrong": 1, "valid": 16, "wrong_rejected": 1}, "M4": {"authorized_correct": 5, "calls": 6, "correct": 5, "legal_wrong": 1, "valid": 6, "wrong_rejected": 1}, "Q7": {"authorized_correct": 4, "calls": 4, "correct": 4, "legal_wrong": 0, "valid": 4, "wrong_rejected": 0}}`. No new Recovery usefulness threshold.

## 26. Independent Recovery authorization

Correct independent authorization **24**; legal wrong independent rejection **2**. Each legal candidate is checked against the authentic receipt with framework-owned identity, status, scope and attempt ownership. Malformed outputs stop before authorization; their failure is distinct from legal wrong rejection. Rejection is atomic and no retry/fallback occurs.

## 27. UNKNOWN→known transitions

**24** first committed state/action observations. Every one retains before and immediate-next Explorer and Map projections in the private chains and transaction trace. UNKNOWN disappears for the newly known exact pair; other untouched pairs remain unknown. Counts concern first observations, not all commits.

## 28. Stale-UNTRIED audit

Stale UNKNOWN markers **0**; unknown in protected storage **0**. All live prompts are independently reconstructed from current authorized Memory. No prompt keeps UNTRIED alongside observations for the same pair; no Memory/package/receipt stores UNTRIED as an event. Empty snapshot arrays in the evidence journal describe an empty store and are not inserted as Memory observations.

## 29. []→history transitions

Immediate post-commit exact-pair []→authenticated-history transitions: **24**. Actual later live Map calls with same-pair history: **42**; call indices `[12, 14, 17, 19, 32, 34, 37, 40, 44, 46, 48, 50, 52, 54, 56, 71, 73, 75, 78, 86, 88, 90, 92, 94, 96, 98, 106, 109, 111, 113, 115, 117, 143, 145, 147, 151, 153, 155, 157, 159, 161, 163]`. Immediate projections and actually consumed model inputs are counted separately. Replay recomputes both from authenticated state.

## 30. Experience-use chains

Retained observational chain counts: `{"Explorer": 113, "Map": 112, "Recovery": 26}`. The private archive links role calls, pre-execution predictions, external receipts, commits and later decisions within each episode. Later same-episode Memory-consuming calls: 85. These are evidence-availability/use observations, not weight learning or proof of inferred causality.

## 31. Explorer revisit chains

113 retained earlier-commit → later same-state Explorer chains, spanning 43 later decision opportunities. All earlier commits are authenticated R1 events. Multiple earlier observations can link to one later proposal; chain counts are not independent samples or causal attributions.

## 32. Map revisit chains

112 earlier-commit → later same-pair Map chains; 42 later opportunities. Changes: `{"becomes_exact": 41, "different_wrong": 5, "remains_exact": 64, "same_wrong": 2}`.

The inherited labels becomes_exact / remains_exact / exact_to_wrong / different_wrong correspond to wrong→exact / exact→exact / exact→wrong / wrong→different-wrong. same_wrong and malformed_or_transport remain separate. Counts compare every retained earlier commit with matching later proposals, not only adjacent visits.

| Revisit change | Chain count |
|---|---|
| wrong → exact | 41 |
| exact → exact | 64 |
| exact → wrong | 0 |
| wrong → different wrong | 5 |
| same wrong | 2 |
| malformed/transport | 0 |

## 33. End-to-end Recovery chains

26 retained genuine Recovery chains; 18 have a wrong next-state Prediction. The others, if present, arise through the unchanged framework's mismatch routing and are not mislabeled wrong-state predictions. Each chain retains receipt, Measure, callback, independent decision and subsequent decisions if the episode survives.

## 34. Realized/authorized consequence

| Quantity | Sum |
| --- | --- |
| All executed realized consequences | 4 |
| Committed realized consequences | 4 |
| Authorized Memory consequences | 4 |

Committed realized and authorized sums match. Executed-but-rejected events, if any,
are not published as Memory. These descriptive consequence sums are not a new
behavioral success threshold.

## 35. Memory growth

| Episode | Committed events | Final Memory records |
| --- | --- | --- |
| 0 | 8 | 8 |
| 1 | 8 | 8 |
| 2 | 8 | 8 |
| 3 | 0 | 0 |
| 4 | 8 | 8 |
| 5 | 0 | 0 |
| 6 | 8 | 8 |
| 7 | 8 | 8 |
| 8 | 2 | 2 |
| 9 | 0 | 0 |
| 10 | 8 | 8 |
| 11 | 8 | 8 |

Observed bounds maxima: `{"map_quarantine": 0, "memory": 8, "memory_quarantine": 0, "packages": 8, "pairs": 8, "pending_authentic": 1, "trace": 24}`. Old verified observations are preserved under the original bounded policy; only absence representations disappear. No unexecuted choice, raw role output or rejected replacement is event truth.

## 36. Representation breakdown

| Role | Family | Calls | Valid |
| --- | --- | --- | --- |
| Explorer | O1 | 34 | 33 |
| Explorer | O2 | 36 | 35 |
| Map | O1 | 33 | 33 |
| Map | O2 | 35 | 35 |
| Recovery | O1 | 16 | 16 |
| Recovery | O2 | 10 | 10 |

Map predictive breakdown by family: `{"O1": {"calls": 33, "consequence_correct": 20, "exact": 15, "next_state_correct": 20, "valid": 33}, "O2": {"calls": 35, "consequence_correct": 26, "exact": 23, "next_state_correct": 27, "valid": 35}}`.

Recovery authorization breakdown by family: `{"O1": {"authorized_correct": 15, "calls": 16, "correct": 15, "legal_wrong": 1, "valid": 16, "wrong_rejected": 1}, "O2": {"authorized_correct": 9, "calls": 10, "correct": 9, "legal_wrong": 1, "valid": 10, "wrong_rejected": 1}}`. O1/O2 are the original families; no representation-neutrality claim or new family threshold.

## 37. Cross-role leak audit

164 request projections independently reconstructed; raw cross-role leaks **0**. Explorer text passes as a parsed finite action only; Map text as a finite Prediction only; Recovery text as a parsed replacement integer only. Returned model context is never reused. The durable journal is external evidence and is never fed back into prompts.

## 38. Role-boundary controls

After the live episodes, exactly the inherited bounded synthetic controls ran:
**5 Explorer, 14 Map, 22 Recovery**. All passed at their proper pre/post-execution
boundaries. They use zero real inference and are regenerated by exact replay.
No expanded adversarial campaign or proposal repair was added.

## 39. Model authority audit

Explorer remains action proposer; Map remains finite Prediction proposer;
Recovery remains replacement-state proposer. External execution defines reality;
Measure, authenticated Memory and authorizers are non-model. Model-originated
identity/status authority: 0; stale/duplicate
authorizations: 0; protected false accepts:
0; receipt-mismatch accepts: 0;
unauthorized commits: 0. The journal only records outcomes.
No model role certifies itself or another role.

## 40. Exact R1 replay

R1 replay used zero new inference and regenerated **all ten registered files**:
metadata, schedule, calls, steps, chains, bounded controls, provisional results,
durable journal, atomic campaign state and durability audit. All Memory snapshot
files also match byte-for-byte. Reconstructed paths include model routing, UNKNOWN,
exact prompts, parsers, trusted latches, events/receipts, Measure, Recovery,
authorizers, Memory and stops. The final summary was separately regenerated
byte-identically after verification. This replays R1 only, not the interrupted run.

Journal records: 1092. Unique call IDs: 164.
Ambiguous calls: 0. Duplicate call IDs: 0.
The independent audit confirms intent→response→parsed ordering and each finalized
transaction against the canonical call/step records.

The first zero-inference replay stopped because runtime Memory contains a Python
source_pair tuple, while its JSON archive necessarily stores an array. A separate
replay-only compatibility module compares canonical serialized structured metadata,
with JSON types/values preserved. The ten-file byte-identity requirement is unchanged.
All frozen scientific/live-recording sources and raw data remain unchanged. An
independent request recount also corrected its reconstruction of HTTP option key
order using the frozen OPTIONS order. Both initial failed checks are retained;
no model request was repeated and no scientific output was repaired.

## 41. Regressions

**41 final post-campaign regression/replay commands passed**. One earlier replay attempt failed on the serialization comparison described above and is retained separately (42 recorded validation attempts total).
They include R1 exact replay and durability tests, schema-contract and forensic
replays, composition-v1 C, bindings A, composition-v0 C, v2 routing/schema/UNKNOWN
tests, and the inherited 33-command Recovery/status/interface, Map, Explorer,
realized-event, minimum-repair, base v0/v1/v2 and expected-negative diagnostics.
Original v2 has no live archive to replay; its interrupted source/results remain
byte-identical, with no substituted R1 data. `verification.json` lists actual
commands, timestamps, exits and file/log digests. No historical result was changed.
All 473 substantive parent files remain identical; only root README and manifest
index the new checkpoint. Main, tags and other branches are unchanged.

## 42. Limitations

A small stationary four-state/three-action world, one pinned model/runtime, fixed
seed schedule, 12 episodes and bounded history. Calls and revisit chains within
episodes are dependent. This is neither broad agent intelligence nor a claim of
representation neutrality, causal learning, persistent learning, reinforcement
learning, weight updates, self-improvement or self-authorization. Software object
identity and the external receipt source remain inherited trusted boundaries;
malicious same-process code and a lying trusted root are outside this live model.
Fsync/atomic rename provide the operating-system durability contract tested here,
not a guarantee against every hardware/storage failure. Journal I/O may change
timing; fixed seeds do not make different stochastic executions identical.

## 43. Narrowest defensible conclusion

**A — MULTI-ROLE PROPOSAL COMPOSITION INTEGRITY PASS** for this independently recorded execution of the unchanged v2 protocol. R1 made 164 calls, executed 68 decisions and committed 66 authentic events. Its own live paths and verification—not the original crashed run or historical synthetic evidence—determine this classification. Formatting and predictive usefulness remain separate descriptive results.

## 44. Recommendation

Preserve R1's complete durable archive and the original interrupted checkpoint as
separate research history. Stop after this registered execution, bounded controls,
replay and regressions. Do not tune prompts/parsers, change the world/weights,
extend episodes, spend unused call capacity or launch R2 automatically. Any further
scientific question requires a separate decision. Nothing was pushed.

## 45. Durable evidence and crash inspection

Persistent storage was established before inference. Every intent is flushed and
fsynced before send; raw response and metadata before parsing; parsed result before
further role processing. Read-only boundary events are synchronously fsynced.
TRANSACTION_FINALIZED and atomic campaign-state updates precede the next decision.
Memory snapshots are content-addressed; the journal is hash-chained. Atomic writes
use a same-directory temporary file, file fsync, rename and parent-directory fsync.
Final journal counts: `{"AUTHENTIC_RECEIPT": 68, "AUTHORIZER_DECISION": 68, "CANDIDATE_ENVELOPE": 68, "COMMIT_OR_REJECTION": 68, "EXTERNAL_EVENT": 68, "MEASURE_RESULT": 68, "PARSED": 164, "PREDICTION_LATCHED": 68, "PREEXECUTION_REJECTION": 2, "RECOVERY_CANDIDATE_ENVELOPE": 26, "RECOVERY_OPPORTUNITY": 26, "REQUEST_INTENT_RECORDED": 164, "RESPONSE_RECEIVED": 164, "TRANSACTION_FINALIZED": 70}`.

Six zero-call tests covered all five restart phases, torn records, duplicate IDs,
fsync failure, ephemeral-path rejection and exact transaction equivalence. The
initial test exposed an unwrapped directory-fsync exception; it was corrected and
all tests passed **before any R1 inference**, with failed and passed evidence kept.
Inspection never automatically resends/resumes. An intent without a response is
ambiguous/possibly issued and requires stopping. Existing live directories are
refused. Final state contains role counts, terminations, digests and file sizes/hashes;
all agree with retained evidence. No second crash or ambiguous call is hidden.

## 46. Separate campaign identity

ORIGINAL V2: C — NOT ESTABLISHED / INTERRUPTED / LIVE EVIDENCE UNAVAILABLE,
permanently preserved at `7f3fa22`. No original known/suspected calls, partial console
counts or reported commits appear in R1 metrics.

REPLACEMENT R1: the classification and complete durable evidence in this report.
It starts independently at episode 0 / decision 0 with campaign ID
HORUS_COMPOSITION_V2_REPLACEMENT_R1. Deterministic call identity is campaign +
episode + decision + role. The authorizing reason was irrecoverably incomplete
scientific evidence, not dissatisfaction with observed performance. No pooling,
repair of the old result, stochastic-run equivalence claim or R2.
