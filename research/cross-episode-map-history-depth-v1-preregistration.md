# Cross-episode Map history depth v1 — preregistration

Parent: `research/cross-episode-model-transfer-v0`, `148b760d7c97583142c7e7f6093aa0835f0d4a71`. Preserve its overall NOT ESTABLISHED, Explorer SUPPORTED and Map NOT ESTABLISHED decisions. In particular, its CARRY exact 3/12 versus FRESH 0/12 and three favorable pairs against four required remain unchanged.

This is a separately registered Map-only 36-call experiment. No Explorer/Recovery inference, architecture changes, changed prompt/parser, output-driven world execution, weight/chat updates, retries, repair, replacement, extension, extra seeds or push.

## Question and motivation

Does the amount of authenticated exact-pair experience retained from an earlier episode affect first-decision Map prediction after genuine fresh-state initialization? Primary comparison is two observations versus genuinely empty history. One observation is a fully reported secondary condition, with no requirement to reproduce the old 3/12 result.

Earlier Map v0 showed weak exact old-relation prediction with one row; the prospectively registered established-prior Map v1 obtained exact old predictions with two observations. That earlier between-study comparison also changed navigation, transaction identities and seeds. It motivates this test without isolating a universal depth mechanism or revising any earlier finding.

## Three ordinary systems per context

- D0: ordinary new stationary world/source/StatusBoundFramework at state 0, epoch 1002, empty Memory, pairs and packages. No earlier episode exists in D0.
- D1: new EpisodeController starts at state 0, epoch 1001; execute ADVANCE once through ordinary receipt-grounded publication. Transaction 1: state 0→1, consequence +1. Episode 1 ends at nonzero state 1. Trusted `start_episode(1002,0)` resets current external/authorized state to 0 without a new realized event; retain the original record, receipt, package and source lifetime.
- D2: independently construct ADVANCE (transaction 1, 0→1,+1), RETREAT (transaction 2, 1→0,0), ADVANCE (transaction 3, 0→1,+1), all through authentic execution/Measure/authorized publication. Episode 1 ends at state 1. The same trusted initialization retains all three observations while resetting present state to 0 in epoch 1002.

No navigation beyond the one necessary D2 return is used. No injected Memory or fabricated row. D1/D2 use the same-source-lifetime semantics within each system; their separate sources are never imported across systems. Before and after every probe audit all systems, original receipt object identities, source identity/counter, full package binding, protected snapshots, current epoch/state, original epoch/transaction chronology and zero-event reset. Probes cannot execute choices, latch predictions, create receipts or commit Memory.

Map always targets state 0/ADVANCE. Score all depths against the authentic D1 transaction-1 receipt; independently require both D2 target receipts to agree on (next_state 1, consequence 1). No evaluator designation or future answer is supplied to the model. There are four ordinary setup events per context, 48 total, separate from the 36 model calls. There are 24 trusted resets, all with zero realized events.

## Truthful projections and matching

Use the unchanged epoch-visible initialization-v1 Map projection and strict existing Map parser. All requests have exactly state, target_action, VERIFIED_CHRONOLOGICAL_HISTORY. D0 has a truthful empty list; D1 has one authentic epoch-1001 transaction-1 row; D2 has two chronological authentic epoch-1001 rows, transactions 1 and 3. Each row contains only epoch, transaction_id, surface_action, next_state and consequence. The D2 transaction-2 RETREAT observation remains in protected Memory but does not match the projected pair.

Only authenticated history differs within a matched triple. State, target alias, instruction, options and seed match. No condition labels, summaries, averages, confidence, explanations or recency instructions. Epoch is preserved. UNTRIED or [] is never stored as an observation, and retained target observations are never labeled unknown. Negative history never removes an allowed action. No nonstationarity or contradictory-history experiment here.

## Exact prompt, model and schedule

Unchanged explicit R1 Map instruction:

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object with exactly two fields: next_state must be an integer in {0,1,2,3}, and consequence must be an integer in {-1,0,1}. Do not include any other fields or explanation.

Strict parser rejects malformed JSON, duplicate/extra/missing fields, booleans, floats and out-of-domain values. Invalid output counts wrong for next_state, consequence and exact pair. No alternate parser or repair.

Pinned dolphin-mixtral:latest; Ollama 0.1.16; GGUF 47B Q4_0. Manifest SHA256 `4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`, weights SHA256 `bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3`. Verify all five complete manifest blobs before inference. Temperature .2, top_p .9, top_k 40, num_predict 32, num_ctx 2048, repeat_penalty 1.1. Stateless requests, no returned context or persistent chat; no warm-up generations.

Reuse O1 K1/K2/K3 and O2 Q7/M4/Z2, all six permutations of ADVANCE/HOLD/RETREAT once per family in historical order. Context 0–5 is O1, 6–11 O2. Seed = 91001+mapping_index (0–5), identical across depths and corresponding O1/O2 mappings. Only the ADVANCE alias appears as target_action.

Exactly 12 contexts × 3 depths = 36 Map calls. Context index modulo three determines order: 0 D0→D1→D2; 1 D1→D2→D0; 2 D2→D0→D1. Freeze the complete schedule in `experiments/cross_episode_map_history_depth_v1/schedule.json` before inference. No adaptation to outputs.

## Frozen primary decision — D2 versus D0

TWO-OBSERVATION CROSS-EPISODE MAP EFFECT SUPPORTED iff all twelve hold:

1. All 36 calls complete.
2. D0 valid ≥11/12.
3. D1 valid ≥11/12.
4. D2 valid ≥11/12.
5. D2 exact ≥9/12.
6. D2 exact > D0 exact.
7. D2-vs-D0 favorable exact discordances ≥5.
8. D2-vs-D0 reverse exact discordances ≤1.
9. Favorable > reverse in O1.
10. Favorable > reverse in O2.
11. System/provenance integrity passes.
12. Exact replay passes.

Otherwise TWO-OBSERVATION CROSS-EPISODE MAP EFFECT NOT ESTABLISHED. Thresholds are never changed. Live metrics leave replay pending and the final decision provisional until actual verification. Historical preservation must pass before releasing a final supported claim.

For each depth report valid, exact, next_state correct, consequence correct /12. For each of D1-vs-D0, D2-vs-D0 and D2-vs-D1 report favorable (higher depth exact/lower wrong), reverse, both exact, both wrong overall and by family. Report every context trajectory and trajectory frequencies. Report D0≤D1≤D2 aggregate exact accuracy as descriptive only; monotonicity is not a gate. A state-only prediction cannot satisfy exact-pair correctness. D1 is secondary, without a retrospectively fitted support threshold.

## Durable evidence and verification

Use inherited R1 write-ahead primitives with a fixed campaign-wide reservation and exclusive fresh output. Fsync exact intent plus full system snapshot before send, raw response before parse, parsed/scored row before the next request. Durable evidence lives outside the public tree on persistent storage. Stop on interruption or uncertain transport; no automatic reissue or replacement.

Freeze all inherited substantive public files, new scientific code, schedule, reproduction notes and this preregistration before calls. Root README and manifest may be updated to link final results; no old result/code changes. Replay all 36 saved responses with network forbidden, reconstructing actual D0/D1/D2 systems, authentic setup, trusted resets, projections, requests, strict parsing, scores and all pairwise classifications. Require eight registered output files and twelve full system snapshots to match byte for byte; finalized live/replay results must also match.

Execute zero-inference preservation replays for transfer-v0, initialization-v1, Map ablation, R1 and established-prior Map v1. Verify all other inherited substantive files, prior result decisions, prior archive checksums, branch references, main and tags unchanged. No unrelated live campaign. Publish compact evidence and the required 32-section report, keeping raw requests/output archives private.

## Claim limits and stop

A supported result concerns two authenticated old observations versus a genuinely fresh system in this fixture. It does not automatically establish D2 superiority to D1 or isolate row count from the authentic identity/length/content of added history. This is stateless input-conditioned proposal behavior, not persistent/lifelong/weight learning, RL, causal world-model learning, AGI or RSI. The old transfer-v0 overall result remains NOT ESTABLISHED.

Stop after 36 calls, replay, preservation and report. No Explorer rerun, extension for a close D2 result, new world regime, epoch-presentation change or full composed campaign.
