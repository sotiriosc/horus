# Cross-episode model transfer v0 — preregistration

Parent: `research/cross-episode-initialization-boundary-v1`, `9e2e70bcde58f8cfe5a76f0dd2d2a08c2ba617f8`.

Question: can a stateless model start a fresh present informed by a verified past that lives outside the model? Explorer and Map are tested independently. This is a single prospective 48-call study. All thresholds below are frozen before inference. No additional calls, retries, repair, replacement, extension, Recovery role, world enlargement, weights or chat updates are authorized.

## Construction and truth

For each of twelve contexts CARRY starts at state 0, epoch 1001 and executes HOLD (0→0,0), ADVANCE (0→1,+1), RETREAT (1→0,0), RETREAT (0→3,−1) through ordinary authentic receipt-grounded publication. Trusted `start_episode(1002,0)` resets external and authorized state with zero realized events. Four original records, packages, receipt objects and the source lifetime survive. The existing bounded architecture is unchanged.

FRESH is an independent new ordinary world/source/StatusBoundFramework at state 0, epoch 1002, with empty Memory. It is never made by clearing or withholding CARRY history. All three actions remain allowed. CARRY state-0 evidence is ADVANCE [1], HOLD [0], RETREAT [−1]; FRESH has truthful UNTRIED for all three. UNKNOWN is not an event. A negative observation does not ban an action.

Each role/condition call is preceded by actual system/provenance audit. CARRY must remain at epoch 1002/state 0 with four epoch-1001 records, original receipts and source, zero-event reset, and Map epoch identity. Exact protected and external snapshots must be unchanged after every probe. No model choice is executed, no prediction is latched, and no new receipt or Memory record is created by probing.

Map always targets state-0 ADVANCE, independently of Explorer. CARRY exposes the epoch-1001 transaction-2 row (next_state 1, consequence 1, ADVANCE alias). FRESH exposes `VERIFIED_CHRONOLOGICAL_HISTORY: []`. Both are scored against the authentic retained CARRY ADVANCE receipt, never a newly fabricated event. The evaluator designation is absent from the prompt.

## Representations, prompts and sampler

O1 aliases K1/K2/K3 and O2 aliases Q7/M4/Z2 each use all six permutations of ADVANCE/HOLD/RETREAT in the unchanged historical schedule order. Contexts 0–5 are O1, 6–11 O2. Mapping index 0–5 gives base seed 90001–90006. Explorer seed = base; Map seed = base+100, identical within each CARRY/FRESH pair and reused across families. Within each context run the Explorer pair followed by the Map pair. Even context: CARRY then FRESH; odd: FRESH then CARRY. The complete 48-call order is frozen in `experiments/cross_episode_model_transfer_v0/schedule.json`.

Explorer system, unchanged:

> Choose an action using verified prior outcomes. Higher observed consequences are preferable. UNTRIED means no verified observation; it does not mean consequence 0. When evidence is insufficient, you may choose an UNTRIED action to gather information. Reply with exactly one allowed action and no explanation.

Map system, unchanged R1 explicit contract:

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object with exactly two fields: next_state must be an integer in {0,1,2,3}, and consequence must be an integer in {-1,0,1}. Do not include any other fields or explanation.

Use the existing Explorer projection and new epoch-visible initialization-v1 Map projection. No model-visible group labels, transfer narrative or evaluator answer. Exact structured inputs and serialized requests are saved privately before sending. Strict existing parsers; malformed outputs remain invalid, with no repair or alternate parsing.

Pinned dolphin-mixtral:latest, Ollama 0.1.16, GGUF 47B Q4_0. Manifest SHA256 `4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`; weights SHA256 `bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3`. Verify all five complete manifest blobs before inference. Temperature .2, top_p .9, top_k 40, num_ctx 2048, repeat_penalty 1.1; num_predict 16 Explorer, 32 Map. Stateless requests; no returned context supplied on later requests, no constrained decoding, retries or warm-up generations.

## Frozen decisions

Explorer SUPPORTED iff all eight hold:

1. All 24 Explorer calls complete.
2. CARRY valid ≥11/12.
3. FRESH valid ≥11/12.
4. CARRY ADVANCE ≥9/12.
5. CARRY ADVANCE / FRESH non-ADVANCE ≥5 pairs.
6. CARRY non-ADVANCE / FRESH ADVANCE ≤1 pair.
7. CARRY ADVANCE ≥4/6 in O1.
8. CARRY ADVANCE ≥4/6 in O2.

Otherwise CROSS-EPISODE EXPLORER MEMORY EFFECT NOT ESTABLISHED. Report underlying action counts, valid identical choices, favorable/reverse/both-ADVANCE/both-non-ADVANCE pairs overall and by family. Invalid output counts as non-ADVANCE for binary scoring and is reported separately; two invalid outputs are not identical valid choices. FRESH choices are not labeled irrational because FRESH lacks evidence.

Map SUPPORTED iff all eight hold:

1. All 24 Map calls complete.
2. CARRY valid ≥11/12.
3. FRESH valid ≥11/12.
4. CARRY exact > FRESH exact.
5. CARRY exact / FRESH wrong ≥4 pairs.
6. CARRY wrong / FRESH exact ≤1 pair.
7. Favorable > reverse in O1.
8. Favorable > reverse in O2.

Otherwise CROSS-EPISODE MAP MEMORY EFFECT NOT ESTABLISHED. Score exact, next_state and consequence separately. Invalid is wrong on all three. Report both-exact and both-wrong and all family directions. No pooled rescue of a family failure.

CROSS-EPISODE AUTHENTICATED-MEMORY BEHAVIORAL TRANSFER SUPPORTED only if both roles pass their own unchanged rules AND exact replay/preservation checks pass. Otherwise NOT ESTABLISHED. Raw threshold decisions are recorded before verification and are never altered to rescue a result.

## Evidence, replay and preservation

Exactly 24 Explorer + 24 Map = 48 real model calls; zero Recovery calls and zero model-induced world execution. Twelve deterministic setups execute four events each, distinct from inference. Use the inherited R1 fsync journal, a fixed campaign-wide reservation, exclusive fresh output directory, deterministic unique call IDs, content-addressed full system snapshots, durable intent before send, durable raw response before parse and durable parsed/scored record before the next call. Save raw evidence on persistent storage outside the public tree. Any interruption or ambiguous request stops; never automatically reissue it.

Freeze all inherited public files except root README and manifest, plus new scientific code, this preregistration and schedule before inference. Replay all 48 saved responses with network forbidden, reconstructing actual systems, receipts, boundary, truthful UNKNOWN, projections, requests, parser, scores and decisions. Require eight registered output files and twelve system snapshots to match byte for byte.

Run focused zero-inference tests plus preservation replays for initialization-v1 A, boundary-v0 C, Map ablation SUPPORTED, R1 A and schema contract SUPPORTED. Verify earlier public results and branch/tag/main references unchanged. Preserve original interrupted-v2 C and all authority architecture. Public output contains code, preregistration, compact results, verification, reproduction and the 35-part report; private prompts/raw archives/local paths stay outside the public tree except the explicit public experimental prompt contract above.

A positive result concerns authenticated external information availability in fresh stateless requests. It does not establish persistent model learning, weight learning, lifelong learning, RL, self-improvement, AGI, RSI or causal inference by the model. Tiny stationary fixture, one model, paired seeds and bounded history limit generalization. Stop after the 48-call study, replay and preservation. A changed-world correction study may be recommended but is not authorized here.
