# Established-prior Map revision v1 — frozen protocol

Parent `f7b16c4997625e902b59800ec1110806342a1069`. Map-v0 remains **CONTRADICTION-DRIVEN MAP REVISION NOT ESTABLISHED**: both families had 0/12 exact SHIFT-H0 old predictions, despite 12/12 favorable H2 pairs; two invalid responses also failed the global gate. Its one-observation H0 produced 46/48 valid next_state=2 predictions, although actual next_state stayed 1. All 96 H1/H2 responses predicted next_state=1 correctly. This motivates testing two consistent old observations prospectively, not a general sufficiency claim or a reinterpretation of v0. Apply the unchanged [representation checkpoint](representation-priors-and-neutrality-checkpoint.md).

## Frozen authority and sole model role

Only the experiment-side history/world schedule changes. Reuse, byte-for-byte, the realized-event framework/root, original Map proposal adapter and boundary, strict parser, deterministic Explorer, Measure, Memory, Recovery, normal prediction latch, atomic publication and all bounds. No new role, verifier, vocabulary, Memory capacity, training, RL, repair or retry. Model can read authorized state and authenticated target-action history; propose one bounded prediction; directly mutate no protected state; authorize nothing. It cannot choose the action, switch the world, mint a receipt, rewrite reality, approve itself or alter Recovery.

Target is state=1 and underlying HOLD only. Actual next state remains 1; old consequence +1, changed consequence −1. Each sample independently reconstructs a fresh authenticated HOLD-only history. No ADVANCE/RETREAT setup, injected records, or carryover from measured probes. CONTROL executes old HOLD throughout. SHIFT performs exactly two old HOLD executions; the external driver then switches its world consequence law. Executions 3 onward are changed HOLD. This intervention is external to the proposer, framework and receipt-authority code. Receipt authority itself is unchanged.

## Histories and zero-call preflight

P0 follows two setup events: both arms [(1,+1),(1,+1)]. SHIFT switches after event 2, before the model probe, so P0 is measured in the changed world with only old experience visible. P1 follows three events: CONTROL [+1,+1,+1], SHIFT [+1,+1,−1]. P2 follows four: CONTROL [+1,+1,+1,+1], SHIFT [+1,+1,−1,−1]. All next states are 1; chronological transaction IDs are 1…2/3/4. Every old record remains alongside later contradictions. Maximum Memory with a valid probe is five, within the existing eight-record bound.

Before inference, construct all six histories through ordinary external execution/receipt authorization, verify exact authentic object/full event provenance and old-history preservation, and construct the exact 144-prompt annex. In each stage/arm, test two synthetic predictions through the unchanged Map latch: (1,+1) and (0,0). Verify same actual world/receipt outcome despite differing predictions, pre-execution latch, receipt-based Measure and Memory, and unchanged bounds. This is twelve synthetic probe cases plus their setup, no model inference and no expanded attack campaign. Exact preflight replay must match. If any required construction, independence, provenance, bound, or prompt-matching check fails: STOP with zero model calls, no architecture patch.

## Exact representation, prompt, parser and runtime

Import the Map-v0 rendering, compact sorted-key JSON serialization, system instruction, strict parser, transport and sampler without edits. Payload keys: state=1, target_action=<HOLD alias>, VERIFIED_CHRONOLOGICAL_HISTORY. Each row: transaction_id, surface_action, next_state, consequence, projected only from authorized pre_state=1 HOLD records. No canonical action name, regime, evaluator truth, previous prediction, Measure, Recovery, average, recency instruction or recommendation.

Exact system instruction:

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object containing next_state and consequence, and no explanation.

Exactly one JSON object with next_state and consequence; exact integers, next_state∈{0,1,2,3}, consequence∈{−1,0,1}. Reject bool/float, duplicate/missing/extra fields, malformed JSON, explanation and multiple objects. No correction, retry or schema relaxation. The coordinator, never model output, supplies epoch/transaction/state/action identity for the original prediction latch.

Same dolphin-mixtral:latest, Ollama 0.1.16, GGUF 47B Q4_0. Verify complete model bytes before inference: manifest SHA256 `4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`; weights `bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3`, 26,441,544,128 bytes. Verify server metadata/template. Unchanged sampler: temperature .2, top_p .9, top_k 40, num_predict **32**, num_ctx 2048, repeat_penalty 1.1. Stateless sequential calls, no context carryover, voting, training or weight updates.

## Exactly 144 calls, prospectively ordered

2 families × 2 arms × 3 stages × 12 schedules = **144 real calls**, conditional on preflight PASS. O1=(K1,K2,K3); O2=(Q7,M4,Z2). Six mappings in `itertools.permutations(("ADVANCE","HOLD","RETREAT"))` order, zipped to family tokens; mapping index j mod 6. Fresh seed **60001+j**, j=0…11. Each mapping occurs twice per family/arm/stage; only the HOLD alias appears in the prompt, with no action-choice list.

Reuse Map-v0 ordering with renamed stages: j ascending; O1/O2 on even j, reversed on odd j; P0/P1/P2; CONTROL/SHIFT when j+family_index+stage_index is even, otherwise reversed. Family indices O1=0/O2=1, stage indices 0/1/2. Match mapping, seed, sampler, schema and action across stages/arms. P0 CONTROL/SHIFT prompts must be byte-identical. P1/P2 differ only in authenticated consequences, never chronology or identity. Freeze full private annex and public prompt digests before inference. No extension, replacement call, prompt adjustment or schedule adaptation.

## Frozen decisions and component analysis

For each family independently, MAP REVISION SUPPORTED iff all nine hold:

1. SHIFT P0 exact old (1,+1) ≥10/12. Report CONTROL P0 separately. If absent: OLD MAP NOT ESTABLISHED; no family revision claim.
2. SHIFT P2 exact new (1,−1) ≥9/12.
3. CONTROL P2 exact old (1,+1) ≥9/12.
4. At least 8/12 matched P2 pairs are CONTROL=(1,+1), SHIFT=(1,−1).
5. Reverse CONTROL=(1,−1), SHIFT=(1,+1) ≤1/12.
6. All 144 responses complete and valid.
7. Framework integrity PASS.
8. All admitted predictions latched before execution.
9. Every commit equals its authentic realized receipt.

Overall **ESTABLISHED-PRIOR MAP REVISION REPLICATED** requires both independently; otherwise **ESTABLISHED-PRIOR MAP REVISION NOT ESTABLISHED**. No pooling or weakened thresholds. An invalid response remains in the denominator, rejects safely before execution, and fails global behavioral support; continue the fixed schedule without replacement unless transport or protected integrity fails.

P1 is descriptive only. Report (1,+1), (1,0), (1,−1), other valid, invalid; no mandatory switch, averaging/recency interpretation or post-hoc threshold. For every family/arm/stage, report exact-pair, next-state and consequence distributions/accuracy, invalids and prediction/receipt mismatches, denominator 12. Invalid pairs earn no primary or admitted-component accuracy; retain their raw component values for inspection. Secondary component performance cannot replace the exact-pair criterion. P0 SHIFT can rationally predict the old consequence from its visible history while the hidden world has changed.

Prospective secondary question: does two-observation P0 remove the v0 one-observation next-state error? Report new P0 next_state=1 rate descriptively against unchanged v0 H0 (46/48 valid responses predicted next_state=2; two responses invalid). Do not pool studies statistically or claim two observations generally suffice. This follow-up also uses direct HOLD-only construction, consecutive transaction IDs, fresh seeds and a later change point relative to target observations; these limit a pure causal attribution to history depth alone.

## Integrity, controls, replay, regressions and stop

Require zero protected false accepts, accepted receipt mismatches, unauthorized/stale/duplicate/malformed commits, direct model mutation, post-execution prediction rewrite, history rewrite and bound violations. Wrong prediction is not framework failure; invalid output is behavioral failure when safely rejected. Preserve proposal, latch, actual execution, receipt, Measure, transient/published Map quarantine, actual Recovery returns/authorization, final Map and Memory. HOLD's valid incumbent need not invoke state Recovery merely because a prediction is wrong. Stop for transport failure, unsafe publication, lost history, ungrounded evidence, latch/root mutation or bounds failure; no automatic core patch.

After exactly 144 calls, reuse the same nine Map-v0 admission outputs in each family at schedule 0 CONTROL P0 (18 synthetic controls): malformed JSON, explanation, invalid next state, invalid consequence, bool, float, missing key, extra key, multiple objects. No expanded controls; no synthetic response counted as model behavior.

Retain private exact setup, authenticated history, prompt/mapping/seed, raw/parsed response, latch, receipt, Measure/Recovery, commits and Memory. Exact recorded-response replay must reproduce all evidence and summary with zero inference. Run this study replay; Map-v0 replay; contradiction-v1 and feasibility replays; realized-event replay; old contradiction-v0 expected-failure diagnostic; factorial, semantic, adaptive, Memory and original Explorer replays; minimum repair 1; base v0/v1/v2; new stage/history tests. Preserve every positive and negative result.

Publish compact results, verification, reproduction instructions and the required 35-section report. Preserve historical sources/results, representation checkpoint, main and tags; no push or public raw private archives. Then STOP. No third Map study to strengthen numbers, role combination, Recovery promotion, new vocabulary or architecture work. At most this tests bounded prompt-conditioned prediction revision with authenticated software evidence, not persistent/weight learning, RL, causal understanding, general world-model learning/concept drift, AGI or RSI.
