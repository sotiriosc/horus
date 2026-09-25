# Contradiction revision v1 — frozen behavioral protocol

Parent/feasibility `56432a68db4ca5960caa4edc5580a427ed7a8267`; repair `ca131869b97dd5c96dd60eb7329f65b1a293246f`; historical framework `8ec32c839133df7ddd76448063b5f765c20155da`. This protocol and `experiments/model_explorer_contradiction_revision_v1/frozen-inputs.json` precede implementation/inference. The latter freezes exact framework, repair, feasibility and reused adapter/fixture source hashes plus model digests. Preserve all historical files/results, main and tags. No push.

## Question and authority

Can authenticated contradictory experience revise an earlier evidence-favored proposal preference while old true observations remain? Explorer is the only model role. The unchanged receipt-bound framework decides admission, execution, provenance and publication. No model weights, world structure, receipt semantics, authenticity, Map, Measure, Memory, Recovery, atomicity, bounds, trust roots or verifiers change. Confirmation verifies authentic arrival/binding, not agreement with old expectation. A/B remain shared-root descendants. The model cannot read hidden regime or write/authorize protected state.

## World and independent histories

Reuse the unchanged feasibility external world and scripted execution logic. Both arms start state 1, epoch 1001; sequence HOLD, ADVANCE, RETREAT, HOLD, ADVANCE, RETREAT, HOLD. CONTROL never changes. SHIFT changes only state-1 HOLD +1→−1 and ADVANCE −1→+1 after external execution 3, preserving their next states 1/2. All other events remain unchanged. Regime is external evaluator truth, never model/Map/authorization input.

Rebuild each measured call independently through real authorized receipts. H0 follows 3 scripted events, H1 6, H2 7. Required target histories:

| Stage | CONTROL HOLD / ADVANCE | SHIFT HOLD / ADVANCE |
|---|---|---|
| H0 | [+1] / [−1] | [+1] / [−1] |
| H1 | [+1,+1] / [−1,−1] | [+1,−1] / [−1,+1] |
| H2 | [+1,+1,+1] / [−1,−1] | [+1,−1,−1] / [−1,+1] |

These are assertions, not injected Memory or prompt constants. Navigation stays in full Memory. Original tx1 HOLD +1 and tx2 ADVANCE −1 must remain in every SHIFT H1/H2 projection. Measured probes execute in the actual current arm after setup; consequently **SHIFT H0's probe is already execution 4 in the changed world**, although its visible history is old. Each probe remains local to that reconstructed fixture.

## Pinned model and inference

`dolphin-mixtral:latest`, Ollama 0.1.16, GGUF 47B Q4_0. Manifest SHA-256 `4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`; weights SHA-256 `bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3`. Hash actual bytes before inference and verify server model/version/template. Sampler: temperature 0.2, top_p 0.9, top_k 40, num_predict 16, num_ctx 2048, repeat_penalty 1.1; seed below. Reuse inherited ChatML template. Sequential stateless requests, no context carryover, tools, retries, fallback, voting, repair, training or weight updates. One request is one observed proposal. Stop on transport failure; never replace it.

Exact system prompt (without surrounding quote marks):

> Choose one available action using only the verified chronological outcomes shown. Higher verified consequences are preferable. Reply with exactly one available action and no explanation.

Exact user serialization: `json.dumps(payload,sort_keys=True,separators=(",",":"))`. Payload has exactly `state`, `available_actions`, `VERIFIED_CHRONOLOGICAL_HISTORY`. Each history entry has exactly `transaction_id`, `surface_action`, `consequence`. Mechanically select authorized pre_state=1 HOLD/ADVANCE Memory records, preserving chronological transaction order. No source/event/epoch IDs, canonical names, regime, prediction, measurement, Recovery, scores, recommendation, averages or recency rule in the prompt. H1 SHIFT has conflicting evidence for both actions; no prescribed correct choice or invented H1 threshold.

## Complete prospective schedule and prompt annex

O1=(K1,K2,K3); O2=(Q7,M4,Z2). Use all six `itertools.permutations(("ADVANCE","HOLD","RETREAT"))` in that exact order, zipped to the family's aliases. j=0..11; seed=40001+j; mapping index=j%6. Offer only HOLD/ADVANCE aliases; HOLD first for j<6, ADVANCE first for j>=6. RETREAT remains framework-valid and is merely omitted from the experimental pair.

Execution order is unchanged from the original frozen design: j ascending; family order O1/O2 for even j, O2/O1 for odd j; stages H0,H1,H2; arm order CONTROL/SHIFT if j+family_index+stage_index is even, otherwise SHIFT/CONTROL. Family indices O1=0,O2=1, stage indices H0=0,H1=1,H2=2. Exactly **144 real calls**, no extensions, extra seeds, semantic arm or replacement calls.

Before any real call, construct all 144 exact prompts from safely authorized reconstructed fixtures and freeze their SHA-256 annex publicly as digests, retaining exact prompt archives privately. Verify matched H0 prompts byte-identical; H1/H2 paired prompts differ only in authentic chronological consequence values. Same mapping/option/seed across arms/stages. Abort before inference on mismatch. No prompt, schedule, threshold or interpretation changes after the first real call.

## Admission, execution and integrity

The string-only adapter reads authorized state/Memory, renders the registered prompt, calls once, strips outer whitespace, and accepts exactly one offered alias. Translate mechanically to HOLD/ADVANCE and use ordinary Explorer admission. Reject explanations, two labels, canonical names, unknown/omitted aliases or extra text before execution. Invalid real outputs remain in all denominators, receive no retry, and fail the global behavioral support gate. Continue the registered schedule after a safe malformed rejection; stop immediately on a protected failure.

Latch prediction before actual execution. Mint authentic receipt only afterward, authorize through the unchanged repair, audit exact original receipt object and full provenance plus actual event, and preserve the old Memory prefix. Record original prediction, measurement, Map/quarantine, actual Recovery returns, package/Memory/commit, bounds and integrity. Reuse the feasibility read-only observer; no function replacement. Model adapter gets no source, framework, regime or authorization capability. Assert no protected mutation across transport; rejected proposal has commit_delta=0 and no continuation grant. Valid contradictory events must authorize despite old expectations. Every probe is independent; no measured response/outcome feeds another sample.

Require zero protected false accepts, receipt mismatches, unauthorized/stale/duplicate commits, malformed commits, direct model protected mutation, prediction/history rewrites, fabricated contradictory records or bound violations. Keep Memory/pair/package ≤8, pending authentic receipt ≤1 and trace ≤24; a valid H2 probe reaches exactly eight records without eviction. Stop on any source mismatch, unsafe fixture/probe, failed origin/binding, history disappearance, projection mismatch, unexpected eviction, bound failure or transport error. Do not patch architecture or resume with replacements.

## Frozen metrics and criteria

All proportions use 12 registered schedules per family/arm/stage, including malformed proposals. SHIFT H0 HOLD ≥10/12 establishes old preference for that family; report CONTROL H0 too but do not treat identical-prompt H0 arms as independent populations. Report CONTROL HOLD and SHIFT ADVANCE counts/rates at H0/H1/H2 separately, H1 descriptive only. Show every matched H0→H1, H1→H2, H0→H2 proposal transition. Among SHIFT schedules initially selecting HOLD, report first ADVANCE at H1, H2, no observed switch; invalid later responses are explicitly visible and cannot count as switching successes. Initially-ADVANCE schedules are excluded from latency successes. Monotonicity of SHIFT counts is descriptive, not a criterion.

For each family independently, **BEHAVIORAL REVISION SUPPORTED** iff all are true:

1. SHIFT H0 HOLD ≥10/12.
2. SHIFT H2 ADVANCE ≥9/12.
3. CONTROL H2 HOLD ≥9/12.
4. Matched H2 SHIFT=ADVANCE, CONTROL=HOLD in ≥8/12 pairs.
5. Reverse SHIFT=HOLD, CONTROL=ADVANCE in ≤1/12 pairs.
6. All 144 registered calls complete and valid.
7. Framework integrity PASS.
8. All SHIFT H1/H2 contradictory observations authenticated through the receipt path.
9. Original HOLD +1 and ADVANCE −1 preserved in every required history.

Overall **CONTRADICTION-DRIVEN BEHAVIORAL REVISION REPLICATED** requires support independently in both O1 and O2. Otherwise **CONTRADICTION-DRIVEN BEHAVIORAL REVISION NOT ESTABLISHED**; no pooling or weakened thresholds. On incomplete execution explicitly report unfinished denominators and stop reason, never impute outputs. Current-world accuracy is secondary evaluator-only: CONTROL favors HOLD, every measured SHIFT probe occurs after execution 3 and favors ADVANCE. This truth never enters prompts. Do not infer internal causal understanding, belief change, recency weighting or averaging from action changes.

## Post-campaign controls, replay and preservation

Only after all 144 real calls complete, run exactly 12 synthetic controls, six per family at schedule 0 CONTROL H0: X9; canonical HOLD; canonical ADVANCE; both offered aliases separated by one space; first offered alias followed by ` because it is better`; omitted third alias. Each rebuilds its fixture and must reject before execution/commit. Controls are not model behavior. Bounded adapter/history/matching tests use deterministic fixtures and parser logic, not extra model calls.

Privately retain every exact call/response/configuration/prompt, descriptor, setup, full fixture/visible history, probe receipt/package/Memory and integrity evidence. Exact recorded-response replay must reproduce all evidence files and compact results byte-for-byte (metadata reused from the original request); no claim that fresh stochastic inference would reproduce outputs. Run feasibility replay; repair campaign/replay; unchanged old failing diagnostic (expected exit 2); five prior model-study replays; minimum repair 1; base frameworks v0/v1/v2; new adapter/parser/history/matching tests. Preserve historical negatives. Publish a 38-item report, compact counts/hashes and reproduction instructions, with private archives/local paths outside public source.

Stop after reporting. No architecture expansion, model promotion, longer-horizon study, weight learning, RL, training, RSI, AGI, general drift adaptation, physical truth or universal grounding claims. A supported result would establish only prompt-conditioned proposal revision under this bounded controlled history intervention.
