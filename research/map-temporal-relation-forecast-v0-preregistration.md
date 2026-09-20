# Map temporal-relation forecast v0: preregistration

Parent: research/map-guided-explorer-interface-v0, commit 24beb32ada2c1661ae31f067aebbe9b7b1939697.
This is a new real-model Map-only forecasting study. Prior results and all authority code remain unchanged.

Question: can Map forecast the next realized consequence from chronological authenticated exact-pair history when pure recency and unordered counts cannot distinguish the registered outcomes?

Each independent context starts state 1, epoch 1001, empty Memory. Six ordinary HOLD events execute through the external source, authentic receipt, Measure, authorization and publication. Each HOLD self-loops to 1. Map then predicts event seven. The strict historical parser and existing MapProposalAdapter latch the original prediction through begin_step before execution. The seventh authentic receipt, never a policy target, scores exact, state and consequence accuracy. Incorrect finite output executes unchanged. Invalid output has no legal Prediction: count invalid and incorrect, do not execute a substitute seventh event, and proceed to the next independent context without retry. Transport ambiguity or integrity failure stops the campaign without reissue.

| Arm | First six realized consequences | Registered seventh |
|---|---|---|
| S stable | +1,+1,+1,+1,+1,+1 | +1 |
| F persistent flip | +1,+1,+1,-1,-1,-1 | -1 |
| T transient deviation | +1,+1,+1,+1,+1,-1 | +1 |
| P periodic/order discriminator | +1,-1,+1,-1,+1,-1 | +1 |

F/P have identical counts, mean 0, latest -1, length, state/action and transaction-ID shape. Their chronological order and next realized consequences differ. This does not identify an internal model mechanism or uniquely identify any process from finite history.

The world stores its seven-event sequence privately and reads an index only during execution. Event seven is guarded until the model response is durably recorded, strict-parsed, and latched. No forecast filtering, replacement, hidden-world pre-execution lookup, model Recovery, or Explorer call. Six-record history is reconstructed from protected authorized Memory using the unchanged epoch-visible Map projection. Memory/pairs/packages have six records before inference and seven after a valid forecast; existing bounds remain eight, no eviction. State stays 1, epoch 1001, transaction IDs 1..7. Setup uses ordinary deterministic framework predictions; measured event uses the model prediction.

Map payload has exactly state, target_action, VERIFIED_CHRONOLOGICAL_HISTORY. Rows contain epoch, transaction_id, surface_action, next_state, consequence. No arm/process labels, targets, summaries, aggregation or instructions about temporal patterns enter it. Full source identities remain in private audits, outside model input.

System instruction (exact established text):

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object with exactly two fields: next_state must be an integer in {0,1,2,3}, and consequence must be an integer in {-1,0,1}. Do not include any other fields or explanation.

The unchanged parser accepts exactly those two finite integer fields; rejects bool, float, strings, duplicate/extra fields, prose and extraction/coercion. One response only.

Model: dolphin-mixtral:latest, Ollama 0.1.16, GGUF 47B Q4_0. Verify complete manifest and all blob bytes before inference. Sampler: temperature .2, top_p .9, top_k 40, num_ctx 2048, repeat_penalty 1.1, num_predict 32. Stateless requests; no returned context/chat history/weight changes.

O1 K1/K2/K3 and O2 Q7/M4/Z2: all six complete mappings, twice per family, mapping index j mod 6 for j=0..11. Underlying target always HOLD, opaque alias varies. Seed 95001+j matched across four arms and both families. Exactly 96 Map calls, zero Explorer/model Recovery, no retry/replacement/extension. Order: j ascending; family order O1,O2 when even, O2,O1 when odd; rotate S,F,T,P left by j mod 4; reverse this rotated order for the second family position. schedule.json freezes all 96 descriptors and exact serialized request hashes before inference.

Zero-call preflight must establish all six authentic events, state/epoch/lengths, all mappings, no seventh read/execution, exact projections and hashes, F/P matched counts/latest but distinct order and registered seventh value, T latest -1/seventh +1. Any failure stops before inference. Additional deterministic controls cover all 12 finite predictions, malformed output, premature execution rejection and a changed seventh value that cannot alter a prompt but must alter receipt-based scoring.

Per-family support requires ALL:

1. All 48 registered family calls complete.
2. Every arm valid >=11/12.
3. S exact >=10/12.
4. F exact >=9/12.
5. T exact >=9/12.
6. P exact >=9/12.
7. Matched F/P BOTH CORRECT >=8/12 (consequence correctness; state exactness separately gated above).
8. P forecasts latest-value -1 <=2/12.
9. T forecasts latest-value -1 <=2/12.
10. All scored events use authentic seventh receipts.
11. Zero hidden future leakage before inference.
12. Provenance/framework integrity passes.
13. Exact replay passes.

Classify each matched F/P pair BOTH CORRECT, F ONLY, P ONLY, BOTH WRONG by valid consequence correctness, with invalid classified incorrect; retain exact/state scores. Report per mapping/seed histories, original predictions and receipt outcomes, same-consequence and latest-for-both flags. Report T +1/-1/0/invalid counts. No pooling, threshold changes or rescue by other arms. Overall REPLICATED requires independent full support in both O1 and O2; otherwise NOT ESTABLISHED.

Descriptive baselines only: latest observed consequence; unordered +1/-1 histogram (signature only, no arbitrary prediction for a tie); exact arithmetic mean and its sign when nonzero. Mean zero has undefined sign comparator. Baselines never score or repair the model. Latest predicts -1 for F,T,P, while authentic seventh outcomes differ. Report setup and measured mismatch/native state Recovery/native measurement Recovery separately, authorization failures, and original prediction/receipt/history preservation.

Before every request fsync descriptor, authenticated snapshot, exact prompt/body/hash. Fsync raw before parse, parsed result before latch, latched Prediction before event seven; then fsync event/receipt/Measure/Recovery/authorization/score. Exclusive one-campaign reservation and no ambiguous automatic reissue. Private evidence must use durable storage outside public tree. Replay all 96 raw responses without network, reconstructing exact history, requests, parser, latch, execution, receipt and result; require seven deterministic files and 96 snapshots byte-identical. Final replay/preservation status is derived separately without overwriting live evidence.

Run historical zero-inference regressions including interface, explicit-mean, Explorer revision, Map revision, feasibility, depth, transfer, initialization, ablation, R1 and grounding; verify inherited substantive files and prior refs/archive checksums unchanged. Preserve negative results and all main/tags; push nothing.

Claims are bounded temporal forecast discrimination, not generative-law identification, causal inference, Bayesian inference, general noise detection, general world models, persistent/weight learning, RL, AGI or RSI. The temporal worlds and authentic source remain trusted single-process simulation components, not cryptographic or hostile-code isolation. Finite histories cannot uniquely determine event seven. Descriptive baselines are not trained competing models.

Stop after 96 calls, replay and preservation. No live Map-to-Explorer pipeline. If replicated, a future separately authorized study could compare Explorer given oracle forecasts versus model forecasts, with Map accuracy separately measured. Otherwise retain the exact failed gates for the next research decision.
