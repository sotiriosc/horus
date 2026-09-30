# Horus Real Task v0 — Local Inference Runtime Optimization

Prospective method. No scientific execution precedes Method Freeze. This is operational inference work, not another model-comparator or epistemic study. Prior results and all promoted source bytes remain immutable.

## Lineage and authority

Base: `26cdae9de75811dd492d32de8f3337e0b67d09b7`. Exact promoted architecture: `69947aa243a69e7ae26db534727a7122922d978d` (the supplied attachment contains a transcription error). `lineage.json` verifies 757 source/configuration files against both heads, including S, E, grounded derivation, receipt source, protected preparation/execution/Measure/authorization, SessionStore and ModernMemory. No historical merge or reconstruction occurs.

Arm A calls exact `grounded_agent.empirical_policy.integrated_decide`; B calls exact `grounded_agent.policy.promoted_decide`. The ordinary route retains its authorized `dolphin-mixtral:latest` model, original prompts, sampling, seed rule and bounded transport-repair rule. Qwen is the target workload model only, with no model promotion. Model choices are restricted to the three permitted actions; model text cannot write latency, consequence, receipts, authorizations or Memory.

The new task supplies one domain metadata registry: all twelve profile/action relations are EMPIRICAL, because noisy runtime measurements cannot honestly establish deterministic outcomes. The existing `relation_type` function and all policy functions remain byte-identical; its application registry is bound in the isolated study worker only. S and grounded mechanical authority keep their exact eligibility rules, and may consequently never activate. Zero activations are reported, not engineered around. Four persistent context sessions per Horus arm retain the original four-state interface without fabricating context-transition outcomes. Every actual execution is a self-loop in its profile. Context sessions are never reset and never see another context's or arm's evidence.

## Fixed task and execution

Target: Qwen3-14B Q4_K_M, SHA256 `500a8806e85ee9c83f3ae08420295592451379b4f8cf2d0f41c15dffeb6b81f0`; llama.cpp b11242 commit `526c43b8f7dfea9032e9f35e7a1be9183ca7cc20`, executable SHA256 `778f1b3fbbb76e921af1d7f25a5b61d82859962dcd18c71ce86ab84d7f4884e5`. Exact libraries, hardware identity and commands are pinned in runtime-manifest.json.

| Action | Batch | Micro-batch | Threads | Batch threads |
| --- | --- | --- | --- | --- |
| HOLD | 512 | 128 | 8 | 8 |
| ADVANCE | 2048 | 512 | 16 | 16 |
| RETREAT | 128 | 64 | 4 | 4 |

These three candidates were chosen before qualification, independently of candidate speed. Engineering qualification used only synthetic parcel fixtures at three lengths and seven repeated HOLD variance calls. All three completed, with 41/41 layers and all model tensors on CUDA0. A preliminary desktop-idle threshold failed before target calls; this is documented in engineering-plan.json. The final idle admission permits <=25% display/background GPU utilization, <5,000 MiB occupied memory and no competing CUDA compute process. Measured total VRAM ceiling is 22,000 MiB. WSL process visibility does not establish absence of unreported Windows display activity; static controls and noise gates limit the resulting claim.

All candidates use context 8192, f16 K/V on GPU, flash attention, no context shift, one slot, prompt/RAM/idle-slot caches disabled, auto-fit disabled, explicit CUDA0 tensor placement, and offline operation. Target requests use temperature 0, top_p 1, top_k 1, min_p 0, seed 917223 and thinking disabled; per-workload output cap/schema is fixed in the request bytes. No decoding or semantic knob varies with action.

For every target execution: verify the model/executable hashes; check GPU admission; launch the exact action command in a fresh process; confirm full GPU residency; run two identical non-scientific warmup calls; erase and inspect the slot; wait one second; measure one frozen request; retain response/timing data; terminate the server. No action execution is repeated. Wall time is HTTP request-to-complete-response time, excluding launch, hashing, warmup and policy inference; those overheads are retained separately. This objective is warm inference latency, not an assertion that total autonomous-system overhead beats static serving.

The historical Ollama server lacks keep_alive support. After each ordinary decision, an empty system/prompt/template request with num_gpu=0 parks that model CPU-only without generating a decision or outcome. GPU idle admission is then rechecked. Original decision requests and options are unchanged. This is isolated execution management, not a policy change.

## Workloads, references and schedule

Twelve distinct public-safe requests come from the preserved operational Horus decision/review interface and its historical authenticated trajectory projections. No diagnostic benchmark questions or gold are used. Historical consequences inside review inputs are legitimate task material; no prior review answer is included. P0 contains three short structured decisions; P1 three five-decision reviews; P2 three eleven-decision reviews; P3 three longer reviews with 26, 28 and 30 decisions. Exact input provenance and immutable bytes are in workload-manifest.json and workloads/. Returned content is evaluated for execution integrity, never intelligence or diagnostic correctness.

Seed 29092026 fixes schedule.json: 24 encounters per arm, six per profile, each of three prompts repeated exactly once in the second half. Profile and prompt order repeat across halves. Within each matched encounter the A/B/static-C execution order is seeded and fixed. C always executes HOLD and has no Horus decision model, receipts or Memory. It runs the target inference workload, as every arm does. Arm C is an engineering drift control.

Policy input is the existing current-profile integer, admissible actions, authenticated grounded assessments, local decision count and bounded local history. It receives no prompt identity, reference output, reference latency, future profile/schedule position, static control data, other-arm evidence, or unexecuted action outcome.

After Method Freeze, execute three independent HOLD reference runs for each workload, with the same fresh-process/warmup procedure. Every reference must stop normally, satisfy its structural requirement, remain within resources and produce exactly identical final UTF-8 hashes across its three runs. Use their median request wall time. Any reference failure or disagreement stops the campaign before autonomous execution; do not change the workload, budget or validator to rescue it. Reference prompts are never exposed to the policy. Freeze reference outputs, medians, executable implementation and all environment configuration in Environment/Implementation Freeze before the campaign.

## Consequence and failure rules

Synthetic HOLD variance had maximum relative deviation 0.0235513 from its median across seven repetitions. The prospectively chosen rule sets margin=max(0.10, ceiling of three times this deviation to a whole percentage point), stopping if >0.30. Thus margin=0.10: +1 for valid execution at <=0.90 times its prompt's reference; 0 for valid execution >0.90 and <=1.10; -1 for slower, structurally invalid, nonmatching, truncated, OOM or resource/runtime failure. References use identical deterministic outputs, not author-assigned correct actions. Never infer an unexecuted action's consequence.

Integrity means normal stop, frozen structural check, exact final-output SHA256 equality to its HOLD reference, and resource ceiling respected. Review structure requires the three prescribed headings exactly once and in order; the exact reference hash further constrains all content. No manual semantic rescue. Prompt cap exhaustion is a negative execution, not an infrastructure excuse. Failed candidate launch/requests remain real failures if their attempted process/request is recorded.

A competing compute process, unavailable monitoring, artifact mismatch, lost provenance or external service interruption before protected execution is infrastructure-invalid. Stop the whole campaign, preserve every attempted/completed record and do not retry the measurement or restart a failed campaign. No favorable-result retries or omitted episodes. The inherited ordinary-model transport alone retains its documented maximum two identical-byte attempts for listed transport errors, before any execution; invalid model selections stop without a substituted action.

## Authenticated experience and restart

Protected RuntimeWorld executes the chosen configuration before returning an actual event. The unchanged ExternalExecutionBoundary emits the original receipt, and unchanged Measure/authorization admits that same object. The signed SessionStore event binds the original receipt and raw continuous measurement/digest. Only that authorized event enters ModernMemory. Predicted neutral forecasts exist only to prepare the preserved framework, never as executed evidence. Model output has no executor, signing-key or Memory-write capability.

After encounter 12 (12 decisions per Horus arm, three per profile), stop the worker. Persist all eight contexts, close databases/stores and exit. A fresh process must reconstruct exact checkpoints, authenticated stream/file hashes, Memory database/content hashes, current states, grounded assessments, S suffixes and E recommendations before any next decision. No state reset or synthetic receipt is allowed. Finish the remaining fixed encounters.

## Raw first, metrics and claims

During execution only progress counts and elapsed/estimated time are printed. The protected policy necessarily consumes realized consequences; no analyst correctness/performance inspection or aggregate scoring occurs. After completion, freeze original private signed streams, authorization, databases, server outputs/logs and model envelopes with hashes and read-only files. Commit safe raw decision/event/measurement projections plus private-file hashes before any scientific outcome analysis. Raw private streams, keys, databases and reasoning never enter public ancestry. Replay authenticated provenance and recompute scores without model inference; require byte-identical scoring.

Report each arm's cumulative consequence; +/0/- counts; mean/median and per-prompt normalized latency; absolute measured times and throughput; invalid/truncated/OOM/resource failures; unique learned relations; prior-negative repetitions (same profile/action had any prior -1); exact E/S/mechanical/model route counts; every action in order; prompt-matched early/later differences and each profile's means; every profile return; Memory admissions; restart result; target launch/decision overheads. Prior-negative does not mean deterministic knowledge; report the operational definition literally.

Registered experience-conditioned gate for A requires: complete authenticated/replayable campaign, exact restart, all 24 A outputs valid; late cumulative consequence at least four above early; at least three of four profiles improve mean normalized latency by >=10%; no profile regresses by >10%; aggregate mean normalized latency improves >=10%; and static HOLD's late/early mean normalized latency ratio lies within [0.90,1.10]. All comparisons pair the same frozen prompts and balance profiles. Additionally at least one later changed action must follow an authenticated observation for that profile. These are bounded repeated-context outcomes, not weight learning or proof that model internals improved.

The E-benefit gate additionally requires at least one verified E acquisition, A cumulative consequence >=B+4, A mean normalized latency <=0.90*B, A no more invalid executions than B, and A mean normalized latency <=B in at least three profiles. This gate establishes matched policy-level benefit in this campaign, not a randomized population-level causal effect. If E never triggers, no E-benefit claim. Ordinary-model decisions also vary seed by local index under the preserved route; without a memory-ablation arm, model-driven action changes alone do not isolate Memory causally. Exact E overrides, when present, have deterministic receipt-backed ownership.

Classification: E_ADDS_REAL_TASK_BENEFIT if both gates pass; otherwise EXPERIENCE_CONDITIONED_IMPROVEMENT_SUPPORTED if the A experience gate passes; otherwise REAL_TASK_INTEGRITY_ONLY if the full integrity/replay/restart campaign succeeds; otherwise INCOMPLETE_OR_INFRASTRUCTURE_INVALID (report actual boundary without upgrading an incomplete run). Negative output-integrity outcomes do not erase executed receipts but prevent the improvement gate.

No held-out prompts, transfer claim or post-campaign oracle grid is planned. Distinguish target-model output, ordinary-model choices, deterministic mechanisms, Memory-conditioned system behavior and measured engineering latency. Exact-context adaptation is not generalization. No training, self-modification, RSI, intelligence increase, model/policy promotion, merge, automatic follow-on study or Horus change follows. Publish only the audited new research branch and stop after the requested ten-question handoff.
