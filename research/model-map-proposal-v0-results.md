# Model Map proposal v0 — results

**CONTRADICTION-DRIVEN MAP REVISION NOT ESTABLISHED.** Framework integrity: **PASS**. The frozen exact-outcome criteria govern this result; consequence-only scores do not replace them. No extension, pooling, output repair or retry.

Both families achieved 12/12 exact SHIFT-H2 predictions and 12/12 favorable matched H2 pairs. Nevertheless, both had 0/12 exact old predictions at SHIFT H0: valid H0 responses predicted next_state=2 rather than 1. Two additional O1 H0 responses proposed consequence=2 and were safely rejected. Thus both the old-Map prerequisite and all-valid gate failed. Strong H2 separation does not satisfy the registered revision claim.

## 1. Representation-prior checkpoint

[Permanent interpretation checkpoint](representation-priors-and-neutrality-checkpoint.md), committed at `c4fcbfc` before Part B. It preserves the semantic/factorial/contradiction findings, the descriptive M4/Z2 pattern, O1-only prior contradiction support, and overall **NOT ESTABLISHED** for that earlier study. No additional Explorer token campaign ran. Representation is an experimental variable; opaque symbols do not establish neutrality.

## 2. Parent, framework and repair identities

Parent `492d257e2c999ab167050353cba43a3fbeb7f9a5`; minimum repair `8ec32c839133df7ddd76448063b5f765c20155da`; realized-event repair `ca131869b97dd5c96dd60eb7329f65b1a293246f`; complete-fixture feasibility `56432a68db4ca5960caa4edc5580a427ed7a8267`. Map preregistration `2091199`; zero-call boundary gate `80643ad`; implementation and prompt annex `a131b38`, all preceding inference. [Frozen inherited hashes](../experiments/model_map_proposal_v0/frozen-inputs.json) and [verification](../experiments/model_map_proposal_v0/verification.json) bind the preserved sources/results. Main and tags remain unchanged; nothing was pushed.

## 3. Mandatory zero-call Map-role gate

**PASS: 16 synthetic cases, zero model calls.** Four ordinary valid proposals included correct changed/stationary outcomes, the wrong old consequence, and wrong next state plus consequence. All latched before execution and committed the authentic result. One injected Measure fault recovered and committed; an additionally corrupted measurement recovery rejected atomically. Nine malformed schema cases and a raised proposal failure rejected before execution. Five total synthetic commits, eleven rejections; no gate errors. Exact gate evidence replay was byte-identical.

The existing `MapModel.predict` component method returns through the original `CrossSourceFramework.begin_step` latch. The experiment-side adapter delegates current state, quarantine and commit to the original Map; staging deep-copies that protected state. No core method, receipt root, latch, verifier or authority was patched. [Gate digest and summary](../experiments/model_map_proposal_v0/gate-results.json).

## 4. Exact model authority boundary

MODEL CAN READ: authorized state and authenticated chronological target-action history, serialized as text. MODEL CAN PROPOSE: one bounded next-state/consequence pair. MODEL CAN MUTATE: no protected state directly. MODEL CAN AUTHORIZE: nothing. It cannot choose the action, mint a receipt, alter the world regime, rewrite an event, approve its prediction, or modify Measure/Recovery authority.

Only prompt text and an integer seed enter the transport. The controller supplies transaction/epoch/action identity; the response cannot provide identity or callbacks. This is a capability-limited model-text interface inside a trusted Python process, not process isolation for arbitrary hostile Python.

## 5. Deterministic Explorer

A separate experiment-side `DeterministicExplorer` selects HOLD at state 1. No model action choice or forced model output enters Explorer. The model occupies Map proposal only; the existing admission rules remain in force.

## 6. Target state/action

Every primary probe targets state 1, underlying HOLD. Old outcome is (next_state=1, consequence=+1); changed outcome is (1,−1). No ADVANCE primary probes were added. Historical ADVANCE/RETREAT setup events remain part of the unchanged authenticated fixture but are omitted from model-visible history.

## 7. CONTROL and SHIFT worlds

The inherited CONTROL world stays stationary. SHIFT changes the registered state-1 consequences only after setup execution 3. All measured SHIFT probes therefore execute the changed HOLD outcome, including H0; this truth is not supplied to the proposer. The world, external receipt source, root authorization and fixture overlay are unchanged.

## 8. Authenticated histories

CONTROL H0/H1/H2 show HOLD consequences [+1], [+1,+1], [+1,+1,+1]; SHIFT shows [+1], [+1,−1], [+1,−1,−1]. Every displayed next state is 1. Each call independently reconstructs the full 3/6/7-event prefix, then projects authorized pre_state=1 HOLD records with transaction IDs [1], [1,4], [1,4,7]. Exact receipt-object identity and full provenance are checked. Old +1 and new −1 coexist; old observations are never relabeled or overwritten. Probe outcomes never enter another sample.

## 9. Opaque families and mappings

O1 uses K1/K2/K3; O2 uses Q7/M4/Z2. Six complete mappings from permutations of ADVANCE/HOLD/RETREAT occur twice in each family/arm/stage. The model sees only that schedule’s HOLD alias, with no offered action list. Schedule j uses mapping j mod 6 and seed 50001+j, j=0…11. Family and arm order are prospectively counterbalanced; chronological evidence order remains fixed.

## 10. Exact prompt and schema

System instruction, frozen before inference:

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object containing next_state and consequence, and no explanation.

User JSON contains exactly `state`, `target_action`, `VERIFIED_CHRONOLOGICAL_HISTORY`; rows contain `transaction_id`, `surface_action`, `next_state`, `consequence`. Serialization sorts keys with compact separators. No regime, canonical action name, previous prediction, evaluator answer, Measure, Recovery, mean or recency recommendation appears. Matched H0 prompts are byte-identical; H1/H2 differ only in authentic consequences.

Strict output: `{"next_state":<integer>,"consequence":<integer>}` with next_state∈{0,1,2,3}, consequence∈{−1,0,1}. Bool, float, duplicate/missing/extra fields, explanation, multiple objects and malformed text reject without repair. [Prospective prompt digests](../experiments/model_map_proposal_v0/registration-digests.json).

## 11. Exact budget and pinned configuration

Registered and completed **144/144 real calls**: 2 families × 2 arms × 3 stages × 12 schedules. Server generation-request count independently matched 144. No replacement or extra inference. Pinned dolphin-mixtral:latest, Ollama 0.1.16, GGUF 47B Q4_0; complete manifest and all 26,441,544,128 weight bytes hashed before inference and matched frozen digests. Temperature .2, top_p .9, top_k 40, num_predict **32**, num_ctx 2048, repeat_penalty 1.1. Stateless requests, fixed seeds, no chat carryover, voting, training or weight updates. 768 authenticated setup transactions were separate from measured probes.

## 12. Proposal validity

Valid: **142/144**. Invalid: **2**. Both were O1 H0 responses proposing consequence=2 outside the finite domain; exact schedules and raw outputs are in verification. They were complete model responses, not truncations. Rejection recorded control/audit status but published no protected Map/Memory event. Each valid response passed the strict schema before entering the normal latch. Malformed responses, if present, remain in the registered denominator and fail the global all-valid criterion; none are repaired or replaced. All recorded-response and step evidence is privately retained, with public evidence hashes in [compact results](../experiments/model_map_proposal_v0/results.json).

## 13. H0 old-Map prerequisite — O1

SHIFT H0 exact (1,+1): **0/12**, required ≥10/12. Old Map prediction NOT ESTABLISHED under the frozen rule. CONTROL H0 exact (1,+1): **0/12**, reported separately. Consequence +1 alone cannot satisfy this prerequisite.

## 14. H0 old-Map prerequisite — O2

SHIFT H0 exact (1,+1): **0/12**, required ≥10/12. Old Map prediction NOT ESTABLISHED under the frozen rule. CONTROL H0 exact (1,+1): **0/12**, reported separately. Consequence +1 alone cannot satisfy this prerequisite.

## 15. CONTROL H0/H1/H2 — O1

| Stage | (1,+1) | (1,−1) | Consequence +1 / 0 / −1 | Invalid | Next-state correct | Exact current outcome | Prediction/receipt mismatch |
|---|---:|---:|---|---:|---:|---:|---:|
| H0 | 0/12 | 0/12 | 11 / 0 / 0 | 1 | 0/12 | 0/12 | 11 |
| H1 | 12/12 | 0/12 | 12 / 0 / 0 | 0 | 12/12 | 12/12 | 0 |
| H2 | 12/12 | 0/12 | 12 / 0 / 0 | 0 | 12/12 | 12/12 | 0 |

## 16. CONTROL H0/H1/H2 — O2

| Stage | (1,+1) | (1,−1) | Consequence +1 / 0 / −1 | Invalid | Next-state correct | Exact current outcome | Prediction/receipt mismatch |
|---|---:|---:|---|---:|---:|---:|---:|
| H0 | 0/12 | 0/12 | 12 / 0 / 0 | 0 | 0/12 | 0/12 | 12 |
| H1 | 12/12 | 0/12 | 12 / 0 / 0 | 0 | 12/12 | 12/12 | 0 |
| H2 | 12/12 | 0/12 | 12 / 0 / 0 | 0 | 12/12 | 12/12 | 0 |

## 17. SHIFT H0/H1/H2 — O1

| Stage | (1,+1) | (1,−1) | Consequence +1 / 0 / −1 | Invalid | Next-state correct | Exact current outcome | Prediction/receipt mismatch |
|---|---:|---:|---|---:|---:|---:|---:|
| H0 | 0/12 | 0/12 | 11 / 0 / 0 | 1 | 0/12 | 0/12 | 11 |
| H1 | 0/12 | 12/12 | 0 / 0 / 12 | 0 | 12/12 | 12/12 | 0 |
| H2 | 0/12 | 12/12 | 0 / 0 / 12 | 0 | 12/12 | 12/12 | 0 |

SHIFT H1 has no required consequence or retrospective success threshold. H0’s old-consequence prediction is compatible with its only visible observation even though the hidden current world changed.

## 18. SHIFT H0/H1/H2 — O2

| Stage | (1,+1) | (1,−1) | Consequence +1 / 0 / −1 | Invalid | Next-state correct | Exact current outcome | Prediction/receipt mismatch |
|---|---:|---:|---|---:|---:|---:|---:|
| H0 | 0/12 | 0/12 | 12 / 0 / 0 | 0 | 0/12 | 0/12 | 12 |
| H1 | 0/12 | 12/12 | 0 / 0 / 12 | 0 | 12/12 | 12/12 | 0 |
| H2 | 0/12 | 12/12 | 0 / 0 / 12 | 0 | 12/12 | 12/12 | 0 |

SHIFT H1 has no required consequence or retrospective success threshold. H0’s old-consequence prediction is compatible with its only visible observation even though the hidden current world changed.

## 19. Matched H2 result — O1

Favorable CONTROL=(1,+1), SHIFT=(1,−1): **12/12**, required ≥8. Reverse: **0/12**, allowed ≤1. SHIFT H2 exact new: **12/12**, required ≥9; CONTROL H2 exact old: **12/12**, required ≥9.

All nine criteria:

- shift_h0_old: **FAIL**
- shift_h2_new: **PASS**
- control_h2_old: **PASS**
- favorable_pairs: **PASS**
- reverse_pairs: **PASS**
- all_144_complete_valid: **FAIL**
- framework_integrity: **PASS**
- latched_before_execution: **PASS**
- actual_commits_equal_receipts: **PASS**

Family verdict: **NOT ESTABLISHED**. Schedule-level matched outcomes are in compact results.

## 20. Matched H2 result — O2

Favorable CONTROL=(1,+1), SHIFT=(1,−1): **12/12**, required ≥8. Reverse: **0/12**, allowed ≤1. SHIFT H2 exact new: **12/12**, required ≥9; CONTROL H2 exact old: **12/12**, required ≥9.

All nine criteria:

- shift_h0_old: **FAIL**
- shift_h2_new: **PASS**
- control_h2_old: **PASS**
- favorable_pairs: **PASS**
- reverse_pairs: **PASS**
- all_144_complete_valid: **FAIL**
- framework_integrity: **PASS**
- latched_before_execution: **PASS**
- actual_commits_equal_receipts: **PASS**

Family verdict: **NOT ESTABLISHED**. Schedule-level matched outcomes are in compact results.

## 21. Consequence-only secondary analysis

The trajectory tables separately give predicted +1/0/−1 counts. Consequence accuracy against current receipts is tabulated in compact results for every family/arm/stage. At H0, O1 proposed +1 in 11/12 calls per arm (one invalid each) and O2 in 12/12 per arm. At H1 and H2, both families proposed +1 in CONTROL 12/12 and −1 in SHIFT 12/12. This clean consequence-only separation coexists with the failed exact H0 prerequisite. It is descriptive and cannot replace the exact (next_state,consequence) criterion or rescue a failed H0 prerequisite. A consequence revision accompanied by an incorrect next state is not an exact-outcome success.

## 22. Next-state stability

Every authentic probe receipt has next_state=1. Across H0, 46/48 responses were valid but predicted next_state=2; two rejected responses predicted next_state=1 with out-of-domain consequence=2. At H1/H2, all 96 responses correctly predicted next_state=1. This is a descriptive history-depth pattern, not a new success criterion or an identified causal mechanism. The tables report exact next-state accuracy per cell; incorrect next-state predictions remained visible as model errors and did not change the realized receipt or final committed state. The target structure is stable, so these errors are separable from consequence revision.

## 23. Prediction error curve

The four trajectory tables are the per-family/arm/stage error curve, with denominators 12. Exact outcome, state and consequence accuracy are independently recorded in compact results; invalid proposals do not earn accuracy. Prediction/receipt mismatches are observed disagreements, not automatically framework failures. SHIFT H0 mismatch is not labeled irrational: only old +1 was visible before executing the changed world. H1 remains descriptive.

## 24. Measure behavior

Measure compared the original latched prediction with receipt-derived evidence. **46** valid predictions disagreed with their authentic receipt. Stored `measurement_matches` agreed with the independently computed next-state/consequence comparison for every committed probe. Measure did not grant prediction truth or alter reality.

## 25. Recovery and Map quarantine

Measured probes: **0 Map quarantines**, **0 state Recovery authorizations**; observed Recovery-return counts: `{}`. HOLD’s incumbent state remains 1, so wrong prediction alone does not require state Recovery in this frozen framework. Do not infer recovery execution merely from prediction mismatch. The separate synthetic gate exercised successful and rejected Measure recovery; neither rewrote the receipt. Setup recovery belongs to the inherited fixture and is not model-probe behavior.

## 26. Memory preservation

**144/144** probe histories retained all prior records unchanged. In every SHIFT H1/H2 input, the authenticated old HOLD +1 coexisted with later HOLD −1. **142** probe commits recorded actual receipt consequences regardless of prediction. Full before/after Memory, protected pairs, receipt packages and provenance are retained; no rewritten past, action prohibition or model-authorized evidence was introduced.

## 27. Representation dependence

Registered family verdicts: O1=NOT ESTABLISHED, O2=NOT ESTABLISHED. Both independently must pass for overall replication. Both families showed the same exact-outcome failure at H0 and 12/12 H2 separation; only O1 had invalid outputs. This experiment did not reproduce the earlier O1-supported/O2-unsupported pattern, nor establish representation neutrality. No vocabulary pooling or automatic alias follow-up occurred. Any observed O1/O2 differences are descriptive here unless covered by the frozen replication criterion; this design does not isolate an intrinsic token cause or prove neutrality. The Part A standing rule remains in force.

## 28. Framework integrity

**MODEL MAP PROPOSAL BOUNDARY INTEGRITY PASS.**

- protected false accepts: **0**
- receipt mismatch accepts: **0**
- unauthorized commits: **0**
- stale duplicate authorizations: **0**
- malformed prediction commits: **0**
- direct protected mutations: **0**
- post execution prediction rewrites: **0**
- historical receipt rewrites: **0**
- bound violations: **0**

Predictions latched before execution: **142**. Protected maxima: `{"map_quarantine": 0, "memory": 8, "memory_quarantine": 0, "packages": 8, "pairs": 8, "pending_authentic": 1, "trace": 24}`. Every committed event passed authentic receipt provenance. These are results within the trusted-process/external-source threat model; trusted root compromise remains out of model.

## 29. Post-run synthetic parser/admission controls

After all real calls: **18** controls, nine per family; **0** commits. Malformed JSON, explanation, invalid next state, invalid consequence, bool, float, missing key, extra key and multiple objects all rejected before external execution. These controls are distinct from the zero-call gate and unit tests; they are not model behavior or extra model calls.

## 30. Exact recorded-response replay

Executed with **zero new inference**. All seven files—registered prompts, model calls, steps, setup, controls, metadata and compact results—were **byte-identical**. This includes all protected outcomes and metrics, not just matching the final verdict. Raw archives remain private; public hashes and [reproduction instructions](../experiments/model_map_proposal_v0/README.md) identify their required role. An independent recount from recorded responses checked the frozen family criteria without using the analysis module.

## 31. Actually executed historical regressions

**20 commands returned their expected exit statuses.** These were executed after this study; they are not historical summaries.

| Check | Actual result |
|---|---|
| Map v0 replay | All evidence and compact results byte-identical |
| Contradiction revision v1 replay | 144 recorded responses; original O1-pass/O2-fail result unchanged |
| Complete contradiction feasibility replay | 14 primary transactions and original evidence byte-identical |
| Realized-event grounding tests + campaign/replay | 6 tests; original campaign and negative boundary unchanged |
| Old contradiction v0 tests + diagnostic | 3 tests; diagnostic exit **2 as expected**, old failure evidence byte-identical |
| Factorial / semantic / adaptive / Memory / original Explorer replays | 216 / 288 / 288 / 224 / 69 recorded real responses; no new inference; historical summaries preserved |
| Minimum framework repair 1 | 177 runs; original expected ablations and boundary failures preserved |
| Base framework v0 / v1 / v2 | 12 / 10 / 13 tests and 42 / 69 / 57 scenarios |
| New Map adapter/parser/authority tests | 5 tests passed |
| Zero-call Map gate replay | 16 cases, byte-identical |

Exact commands, exit codes, timestamps and log hashes are in verification. v1 common-mode false accepts, v2 A+B+C common-mode and trusted-registry false accepts, and realized-event root compromise remain documented historical negatives. No inherited experimental result was changed.

## 32. Limitations

One pinned model/runtime, one state/action, two alias families, 12 fixed seeds, and bounded deterministic synthetic worlds. Authenticated software receipts establish authority inside the declared software boundary, not independent physical truth. Repeated independent reconstructions are prompt-conditioned samples, not a persistent learned Map or weight update. H0 evidence is sparse; H1 is conflicting. Representation/seed/schedule structure limits mechanistic interpretation. The root, harness, parser and framework process remain trusted; arbitrary hostile Python is outside this interface contract. Recovery authority was not model-driven. Raw private archives are needed for exact replay; compact public results alone are insufficient.

## 33. Narrowest defensible conclusion

**CONTRADICTION-DRIVEN MAP REVISION NOT ESTABLISHED.** The existing Map proposal boundary safely accepted bounded model predictions, latched them before execution, and allowed authentic reality to disagree while preserving prior observations. Family-specific behavioral support is exactly as reported above; no broader success follows from valid output or consequence-only performance. This is not weight learning, RL, training, causal understanding, general concept-drift adaptation, general world-model learning, general grounding, AGI or recursive self-improvement.

## 34. Recommendation

Stop at this checkpoint. Review the family-specific exact outcomes and separate next-state/consequence errors before choosing any follow-up. Do not automatically combine Explorer+Map, promote the model into Recovery, modify the receipt architecture, add vocabularies or extend inference. Any new research question requires a separate bounded decision and preregistration. Reality remains authoritative throughout.
