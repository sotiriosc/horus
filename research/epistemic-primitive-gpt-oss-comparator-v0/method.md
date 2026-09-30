# Frozen Epistemic Primitive gpt-oss Comparator v0 — Method Freeze

This is the final planned model comparator. It resolves a bounded architectural question and does not start another comparator, a new benchmark, model promotion, Horus engineering, training, policy/Memory changes or an intervention.

## Immutable sources

Base branch: `research/epistemic-primitive-cross-model-comparator-v0`, verified publication `2ab9eb50f9f8842b46936ef35b1d98ff31965384`. Semantic source: `research/qwen-epistemic-primitive-factorization-v0/materialized/neutral/` at `2cfcf8097c99d13df2156dde47409af0f65cb42a`. Reuse all 112 neutral tasks, 56 aligned states, 28 pairs, seven families and exact source schedule. No scientific case creation or edits to facts, questions, labels, definitions, gold or pairs. `neutral-task-hashes.json` commits every neutral file hash; `interface-equivalence.json` checks exact message content through native template rendering without scientific inference.

Qwen published `scores.json` SHA256: `5dd018b316230b8126c0e6eefe86363d6983f3dc179b934f4b4735119edfd99b`. Ministral published `scores.json` SHA256: `ac6fb003b9bc46d08d8ab558fc98f231392f4542b0697818626ba32d329c20e1`. Reuse those score bytes; do not rerun or rescore either prior model.

## Fixed model and engineering selection

The only model is `openai/gpt-oss-20b`. Use the trusted `bartowski/openai_gpt-oss-20b-GGUF` representation, revision `e39ba3aa000c47c83dacdc9e1ca2c9dd0808c205`, file `openai_gpt-oss-20b-bf16.gguf`, expected SHA256 `5cf32dc225be2115513bcb6480d2f4eff95c6f58355639a679fe93454bbce8bc`. This preserves native released MXFP4 experts with BF16 non-expert matrices and F32 auxiliary tensors; it does not mean every tensor is BF16. The initial ggml-org candidate was loaded with zero model calls; its Q8_0 non-expert tensors motivated selecting this higher-precision candidate based on available VRAM alone. See quantization-selection.json. It preserves native expert precision; expanding quantized experts to nominally larger formats does not recover higher precision. Do not confuse optional Eagle3 draft files with this model. No draft/speculative model is used. Freeze the actual non-expert tensor types and full identity in `model-runtime.json`.

Engineering criteria are full GPU residency, stability, context headroom, schema transport and active native reasoning under task-shaped synthetic inputs. Scientific accuracy cannot affect artifact selection. No silent model substitution. If the configuration cannot qualify, stop before scientific inference and report the incompatibility, without fabricating data.

Runtime: llama.cpp b11242, commit `526c43b8f7dfea9032e9f35e7a1be9183ca7cc20`. Pin the server executable and runtime dependencies by SHA256. RTX 4090; all layers and tensors assigned to CUDA0, auto-fit disabled; no CPU weight/layer offload. Context 16384, f16 K/V, flash attention on, context shift disabled, one isolated slot, no prompt/RAM/idle cache. Host control/staging buffers are not CPU model execution. `original-launch.json` and `launch-plan.json` contain the exact command.

Reasoning: high effort through native Harmony template metadata, extraction enabled, no artificial reasoning-token cutoff (`--reasoning-budget -1`). Final+analysis allowance is 8192 tokens. Sampling is temperature 1.0, top_p 1.0, top_k 0, min_p 0.0, seed 413708629. These values are chosen before synthetic/scientific inference, not from task performance. GPU sampling reproducibility is not assumed merely from a fixed seed. Context/output settings differ from the prior models; conclusions are bounded model/interface comparisons, not equal-compute or isolated causal model comparisons.

## Harmony interface and reasoning qualification

OpenAI documents Harmony analysis/final channels and system-to-developer mapping for semantic instructions: [Harmony format](https://developers.openai.com/cookbook/articles/openai-harmony). [Implementation guidance](https://developers.openai.com/cookbook/articles/gpt-oss/verifying-implementations) documents native MXFP4 weights and separated reasoning. The pinned local llama.cpp `common/parsers/gpt-oss.cpp` supplies the native parser: analysis is extracted privately; JSON schema constrains the final channel. No post-hoc JSON repair or reasoning-to-answer conversion is performed.

Use the GGUF's native template with one prospectively recorded transport edit: freeze its dynamic current-date expression to `2026-09-29`. `template-provenance.json` records native and runtime hashes and the exact substitution. The pinned runtime additionally disables a native-template assistant channel-tag validation guard; this built-in compatibility normalization is recorded in runtime-template-normalization.json and cannot affect the absent assistant history. Do not edit any semantic message. The native template maps the original system instruction to Harmony developer content and adds protocol identity/channel/reasoning/date metadata. No scientific hints, examples, extra reasoning instructions, prefills, tools, reference answers, gold or pair/family labels are added. Original system and user content must appear verbatim in the rendered prompt.

Before either freeze, run 22 non-scientific fixtures: 21 task-shaped parcel-routing arithmetic fixtures spanning all eight schemas and every permitted output label, plus one long context fixture. They use the same primitive/reduction system instruction strings, similarly sized tabular factual inputs, the same schema burden, binary choices or five opaque class codes, and no explanation request. They contain no benchmark states or gold. Qualification requires schema-valid output, nonempty separated native analysis on every fixture, normal stop, total completion below half of the 8192 allowance, sufficient context for prompt plus full allowance, and complete GPU residency. Synthetic answer accuracy is descriptive only and cannot select a model/quantization or affect qualification. Freeze every fixture and qualification artifact, preserving only safe metadata/hashes publicly and full envelopes/logs privately. Run zero-model orchestration/scoring tests separately. Scientific template rendering/tokenization is allowed for equivalence/capacity checks; scientific completions are prohibited during qualification.

## Execution and failure policy

After committing Method Freeze, commit implementation, scorer, tests, all request bytes/hashes and the exact source schedule. Execute 56 primitive and 56 reduction calls exactly once. Erase and inspect the sole slot before each request. No conversation history or previous output enters any request. No adaptive ordering or outcome inspection while running.

Readiness timeout 180 seconds; per-completion timeout 600 seconds. HTTP/control/runtime failures, malformed transport envelopes or missing final string invalidate and stop the campaign. Never retry a dispatched scientific completion or resume a partial run. An empty, truncated, incorrect or schema-invalid final string is preserved as data and does not trigger another attempt. Native reasoning presence and finish reasons are recorded; no setting or budget changes are permitted in response to scientific observations. Unexpected reasoning absence is reported as an interface limitation without silently enabling it later. Zero repairs, critics or manual semantic rescue.

## Raw-first scoring

Do not inspect answer correctness during execution. Preserve exact final bytes and safe request/response/final/reasoning hashes. Full envelopes, logs and reasoning stay outside Git. After execution, verify hashes, exact order, slot controls and preservation; make raw files read-only; commit raw pre-scoring evidence. Only then call the frozen scorer. Require a second zero-inference scoring run to be byte-identical. Neither scoring nor reporting can launch models.

Use the exact unchanged source `grade` and `summarize` functions, gold and pair definitions. Reject duplicate keys, nonfinite JSON, prose and schema violations. No partial schema credit. Identity reports same_referent, equal_value and joint exact. Each primitive requires >=7/8 endpoints AND >=3/4 matched pairs. Report endpoint/schema counts, confusion counts, every endpoint selection and every matched transition separately for all seven families; no pooled intelligence score.

Reduction requires >=48/56 plus all source floors: SUPPORTED_CURRENT_DEFECT >=9/12; NO_SUPPORTED_DIAGNOSIS >=9/12; INSUFFICIENT_EVIDENCE >=9/11; HISTORICAL_DEFECT_NOT_CURRENT >=9/11; INVALID_OR_CONTRADICTORY_EVIDENCE >=8/10. Use that class order for confusion matrices, with invalid-output column. Report endpoints, schema validity, per-class counts, exact pairs /28, diagnostic flips /19, stable retention /9 and family subsets. Never substitute a new threshold after inference.

## Three-model matched analysis

Join all 112 tasks by render ID and assert identical state, family, arm and gold. Use published Qwen/Ministral scores without modifying them. Report primitive endpoint/pair/gate tables and reduction endpoint/pair/flip/stable/class/confusion tables for all three models. Preserve exact per-task selections/correctness, every pair transition and pairwise disagreement IDs. All comparisons are descriptive; scientific units are correlated states/pairs, not 112 independent observations. No overall ranking or causal percentages.

Enumerate exact state sets: all three P correct; Qwen P correct/both comparator P wrong; Qwen and gpt-oss P correct; all three P correct but selected reductions differ; Qwen and gpt-oss P correct but their selected reductions differ; Qwen R wrong/gpt-oss R correct; Qwen R correct/gpt-oss R wrong; all three R wrong; all three R correct. Sets overlap. Here P means the isolated family primitive tested on that aligned state, not an assertion that all seven primitives were evaluated inside its reduction invocation.

Separately report the eight EVIDENCE_SUFFICIENCY endpoints and four pairs, with exact selected primitive and reduction objects for every model. Fixed references: Qwen P 8/8, pairs 4/4, R 3/8, R pairs 0/4; Ministral P 4/8, pairs 0/4, R 2/8, R pairs 0/4. No special prompting or treatment for that subset.

## Registered interpretation

A: all seven gpt-oss primitive gates AND reduction gate pass -> `QWEN_REDUCTION_LIMITATION_SUPPORTED_AGAINST_CAPABLE_COMPARATOR`. Another model/interface can meet the frozen tasks; Qwen's reduction limitation is supported relative to this comparator under these conditions. This does not authorize replacing Qwen.

B: all seven primitive gates pass but reduction fails -> `SHARED_REDUCTION_LIMITATION_SUPPORTED`. This supports shared reduction difficulty and makes the ontology/reduction interface an architectural concern; it does not identify a causal mechanism or test an intervention. No error-overlap threshold from the previous study is inherited.

C: one or more primitive gates fail -> `SECOND_COMPARATOR_PRIMITIVE_LIMITATIONS`. Follow this explicit rule even if reduction passes; report that mixed observation literally using a separate flag. Qwen is the only tested model to establish every frozen primitive gate; this is not an overall model-quality ranking. The clean reduction-specific question remains unresolved. Stop comparator work.

A/B/C exhaust the ordinary scored gate outcomes. D is reserved for an unanticipated protocol/result condition that prevents applying those rules, described literally without forcing a capability conclusion. Transport-invalid or unqualified runs are reported as invalid/unqualified, not as scientific gate failures.

## Preservation, publication and real-system boundary

Preserve every file inherited from the verified base and all 22 protected local/remote heads in `preservation-baseline.json`. No prior branch changes, merge, architecture/policy/Memory changes, compiler-assisted diagnoses, model promotion or training. Audit all reachable commit paths and unique blobs plus private artifact separation; never publish private archives, credentials, envelopes or reasoning. Publish only `research/epistemic-primitive-gpt-oss-comparator-v0`, verify exact remote head and protected heads, and stop.

Report model capability, deterministic verification/scoring, and combined-system capability separately. Combined-system capability and real interventions are NOT TESTED. Primitive calls do not prove internal primitive computation during reduction. Quantization, reasoning, sampling and native interfaces remain confounded across models.

This study provides evidence for architectural responsibility only. Real progress later means useful behavior that survives prospective testing, an honestly identified source of improvement, and persistence in later operation. Benchmark scores, deterministic rules that provide answers, prompt tuning, and unmeasured model replacement do not establish learning or self-improvement. A real consequence-grounded system requires separately authorized engineering; this study neither designs nor builds it. Final handoff answers the eight requested architectural questions, then ends comparator work.
