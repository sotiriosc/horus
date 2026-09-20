# Map positive-evidence depth v0 results

**B — NO DEPTH RESCUE OBSERVED.** Exactly eight real-model Map calls completed and all eight were valid. One-observation D1 was exact in **0/4** calls; two-observation D2 was exact in **1/4**. There was **one improving pair**, three unchanged-wrong pairs and zero regressions. Integrity and exact zero-inference replay passed.

The B label follows the frozen D2 ≤1/4 rule; it does not mean that no individual forecast changed. Repeated identical positive evidence did not rescue the registered task. The one O1/98002 change is retained without promoting it into a general depth-effect claim.

## Identity and frozen protocol

Branch: `research/map-positive-evidence-depth-v0`. Parent forensic checkpoint: `bf26f6a65ac844676e6c35da2a4ed782b71de8f7`. Grounded root: `79921b1da735e1495dffb695c00d7e7a21a234a6`. Mechanical reference: `004ec5a6952d6b1c2c793eabe7200215611ea7b0`.

The [preregistration](map-positive-evidence-depth-v0-preregistration.md), eight-call schedule, code and request hashes were committed **before inference** as `3304d49d089bc7538e24b45e970ca110b8f932ab`. [Frozen inputs](../experiments/map_positive_evidence_depth_v0/frozen-inputs.json) bind 702 files; [schedule](../experiments/map_positive_evidence_depth_v0/schedule.json) binds the exact eight request hashes. No threshold, prompt, sampler, alias, seed or decision rule changed after registration.

D1/D2 here mean history depths one/two, not the earlier changed-world D1 fixture. Each trial starts with a separate grounded system at state 1, epoch 1001 and empty Memory. Target HOLD self-loops to state 1 with consequence +1. O1 mapping 0 uses K2; O2 mapping 0 uses M4. Seeds 98001 and 98002 are paired across depths within each block; ordering is balanced as registered.

The local model is `dolphin-mixtral:latest`, Ollama 0.1.16, 47B Q4_0. All manifest blobs were hashed before the run. Manifest: `4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`; weights: `bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3`. Sampler remains temperature 0.2, top_p 0.9, top_k 40, num_predict 32, num_ctx 2048, repeat_penalty 1.1, with the registered seed. Requests are stateless and use the unchanged established Map instruction/template and strict parser.

## All eight real responses and receipt scores

Prediction/actual notation is `(next_state, consequence)`. Every actual scored receipt is **(1,+1)**. Original raw output text and parsed objects are retained in [results.json](../experiments/map_positive_evidence_depth_v0/results.json); complete write-ahead request/response and runtime evidence is in the private durable archive.

| Index | Block | Seed | Depth | History identities | History consequences | Model prediction | New receipt tx/event | State correct | Consequence correct | Exact |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | O1 | 98001 | D1 | 1001/1 | [1] | (1, 0) | 2/2 | True | False | False |
| 1 | O1 | 98001 | D2 | 1001/1, 1001/2 | [1, 1] | (1, 0) | 3/3 | True | False | False |
| 2 | O2 | 98001 | D2 | 1001/1, 1001/2 | [1, 1] | (1, 0) | 3/3 | True | False | False |
| 3 | O2 | 98001 | D1 | 1001/1 | [1] | (1, 0) | 2/2 | True | False | False |
| 4 | O2 | 98002 | D1 | 1001/1 | [1] | (1, 0) | 2/2 | True | False | False |
| 5 | O2 | 98002 | D2 | 1001/1, 1001/2 | [1, 1] | (1, 0) | 3/3 | True | False | False |
| 6 | O1 | 98002 | D2 | 1001/1, 1001/2 | [1, 1] | (1, +1) | 3/3 | True | True | True |
| 7 | O1 | 98002 | D1 | 1001/1 | [1] | (1, 0) | 2/2 | True | False | False |

| Condition | Valid | next_state correct | Consequence correct | Exact |
| --- | --- | --- | --- | --- |
| D1 | 4/4 | 4/4 | 0/4 | 0/4 |
| D2 | 4/4 | 4/4 | 1/4 | 1/4 |

## Four paired outcomes

| Block | Seed | D1 → D2 full prediction | Consequence category | Improvement | Regression |
| --- | --- | --- | --- | --- | --- |
| O1 | 98001 | (1, 0) → (1, 0) | 0 → 0 | False | False |
| O1 | 98002 | (1, 0) → (1, +1) | 0 → +1 | True | False |
| O2 | 98001 | (1, 0) → (1, 0) | 0 → 0 | False | False |
| O2 | 98002 | (1, 0) → (1, 0) | 0 → 0 | False | False |

Consequence categories: **0→+1: 1/4; +1→+1: 0/4; 0→0: 3/4; +1→0: 0/4; other/invalid: 0/4.** The improvement was O1/K2 seed 98002, whose D2 request occurred before its D1 request in the balanced schedule. Both outputs were separately generated in independent fresh systems; it was not a continuation with hidden model conversation state.

## Genuine history acquisition and post-prediction scoring

The live campaign performed **12 setup executions and eight scored executions: 20 executions, 20 distinct original receipts and 20 ordinary authorized Memory publications**. Each D1 history contains event/transaction 1; each D2 history contains separate events/transactions 1 and 2 from that trial’s own source. All are epoch 1001, state 1, action HOLD, next_state 1, consequence +1. No receipt, Memory row or observation was duplicated. Source identities are distinct across all eight trials, and each source preserves its event identities.

The normal authenticated epoch-visible exact-pair projection produces each prompt. Within each alias/seed pair the exact request differs only by its additional genuine history row; model, system text, sampler, seed, state, target alias and latest outcome agree. Neither the D1/D2 label nor the hidden future outcome is supplied to the model. No Explorer or model Recovery was invoked; HOLD is the externally fixed study target.

Each durable sequence was checked: **request intent → real response → strict parse → framework prediction latch → execution intent → actual HOLD execution → original receipt → Measure → ordinary authorization → Memory publication**. The score event had not executed at request formation or at latch. Its transaction/event is 2 for D1 and 3 for D2. Exact predictions and the latched prediction agree and remain unchanged after execution.

The unchanged `MapProposalAdapter` supplied the retained finite prediction through the normal Map prediction hook. The unchanged `StatusBoundFramework` used the real `ExternalExecutionBoundary.reader()` and ordinary package/Measure/authorization path. All eight score receipts had object identity and fields verified against the external source and actual execution. Memory published the actual +1 in all eight trials, including all seven erroneous consequence predictions; Measure correctly recorded those seven mismatches. No model output obtained authority to rewrite the event, authorize itself or rewrite old Memory. No native state Recovery or model Recovery was needed for these self-loops.

## Leak control, durability and exact replay

Before inference, eight throwaway canaries acquired the registered authentic positive histories, then changed only the hidden next HOLD consequence to −1. Exact request bytes remained unchanged in all eight. After a synthetic +1 prediction was latched, the canary’s actual scored execution, original receipt and authorized Memory record carried −1; old histories remained unchanged. Canary responses were synthetic software controls, never counted as model behavior.

Zero-model preflight passed: eight future-answer canaries, 11 strict-parser rejection cases, seven classification boundary controls, an invalid-proposal/no-execution control, two interrupted-journal controls, and a complete synthetic campaign/replay. Invalid responses cannot trigger repair, retry, constrained decoding or replacement. There were no invalid responses, transport failures, ambiguous intents or interruptions in the real campaign.

The real archive has 72 valid hash-chained journal records and exactly eight intent/response/parse sequences. The model server independently logged exactly eight `/api/generate` requests. It was stopped after completion. The eight real responses were replayed with network blocked, reconstructing fresh grounded histories, request bytes, prediction latches, actual scored executions, original receipts, Measure and authorization. **Seven deterministic data files and eight snapshots were byte-identical**; the complete 16-file live/replay comparison also includes the empty writer lock. Replay used **zero inference**.

Execution accounting is separate from model-call accounting: registration request construction used 12 setup executions; zero-model preflight used 61 simulator executions (20 canary, 20 synthetic campaign, 20 synthetic replay, one invalid-fixture setup); live used 20; real-response replay used 20. Total simulator executions for preparation, live and replay were 113. Only the eight live responses are model observations. No extra behavioral arm, seed, alias, model call or extension was added.

The raw campaign metrics remain their original provisional `AWAITING_EXACT_REPLAY` record. The final B classification is in results.json after successful byte comparison and independent audit; the live archive was not rewritten to change its provisional classification.

## Frozen decision and narrow conclusion

| Requirement | Observed |
| --- | --- |
| All calls complete / valid | 8/8 complete; 8/8 valid |
| D2 exact ≥3/4 for A | 1/4 — not met |
| At least two improving pairs for A | 1/4 — not met |
| Zero regressions | 0/4 — met |
| Authentic post-prediction score receipts | 8/8 — passed |
| Provenance / integrity / replay | Passed |
| D2 exact ≤1/4 for B | 1/4 — met |

**Repeated identical positive evidence did not rescue the registered task.** A second authentic +1 observation coincided with a correct +1 forecast in one of four pairs, while three remained at 0. All four fresh depth-one calls repeated the historical W1 underprediction pattern; strong D1 performance did not occur in this sample.

This eight-call contrast does not establish that depth has no effect, that repetition is the sole cause of previous failures, that two observations are generally sufficient or insufficient, or that Map estimates probability/confidence. It does not identify an internal mechanism or test general world modeling, exploration, mechanical exploitation, broader aliases or closed-loop adaptation. The result is restricted to this stationary simulated HOLD relation, two alias blocks, two paired seeds, one model and the frozen sampler. No statistical generalization is claimed.

## Grounded claim boundary, preservation and stop

This new study’s scores come from actual post-prediction simulated execution receipts. The parent decomposition remains a detached-evaluator study under its original claim firewall; no historical declared-law or detached score was upgraded. Original receipt identity is a trusted in-process capability, not cryptographic attestation or protection against a hostile host. Replay rechecks object identity in its own execution; serialized records alone cannot recreate historical object identity.

All **694** parent tracked files retained exact bytes and executable modes. The grounded baseline A, mechanical baseline A, full Map forensic report, temporal Map negative, all Explorer negatives, stale-Memory Map result and historical authority results remain unchanged. The grounded clean-root manifest and claim firewall retained their hashes. No architecture or prompt file was edited. [Verification](../experiments/map_positive_evidence_depth_v0/verification.json) records the controls, source hashes and preservation checks.

No expansion, additional calls, Explorer work, confidence field, prompt tuning or further experiment was performed. Main and tags are unchanged; nothing was pushed. **Stopped after the registered eight calls, exact replay and report.**
