# Development runtime requirements

This is a second, isolated runtime plan. The frozen Ollama 0.1.16 server, dolphin-mixtral artifact and historical research remain intact. No runtime or model is installed or downloaded in this milestone, and no new runtime is allowed to inherit behavioral equivalence claims.

## Capacity and service boundary

The 4090 reports 24,564 MiB physical VRAM. The existing server used about 2,260 MiB before loading the model, leaving about 22,304 MiB. A development model should target at most 16 GiB of resident weights, with at least 4–6 GiB of practical headroom for KV cache, CUDA workspaces, context growth and other GPU users. Treat about 18 GiB of weights as a provisional upper bound only after a real fit test; file size alone is not a residency guarantee. Total loaded process occupancy should stay below about 20 GiB at the required context. The historical 26.4 GB artifact cannot meet this on one 4090.

Install and serve the development stack at a separate path and port with pinned engine build, model artifact digest, tokenizer digest, quantization, template and launch options. The two installations can coexist; their GPU runners need not be resident simultaneously. Avoid evicting the historical runner silently. Capture driver/CUDA compatibility and GPU memory at start and after warmup. Never rewrite or remove the historical model.

## Interface and performance acceptance targets

- Support at least 8192 effective input-plus-output tokens for public-safe retrospective inputs and at least 2048 for action calls. Prefer 16384 if exact tokenization shows the preserved 30-decision review input exceeds 8192; prove no silent truncation.
- Expose one strict selected_action JSON object with exactly one action from the supplied allowed set. Support JSON-schema or grammar-constrained output, with raw response and parse status still recorded for audit. The protected authorization and Memory path remains external and unchanged.
- On a warm, single-request 4090 run, target at least 150 prompt tokens/s for a diverse 500-token action shape and at least 100 prompt tokens/s at 2000 tokens, with an eight-token action reply below 5 s total. Target at least 30 generated tokens/s when generation is measured with enough tokens for a stable rate. These are acceptance targets, not measured speedups or model guarantees.
- Record separate load, prompt, generation, client wall and queue times. Keep context and GPU allocation stable between ordinary action calls. Prove no unplanned runner reloads under the intended scheduler.
- Validate model quality on held-out grounded decision cases: strict allowed-action compliance; proper handling of UNSEEN versus ESTABLISHED, unresolved and empirical relations; respect for mechanically excluded actions and +1 ceiling; and evidence-grounded retrospective analysis that does not invent hidden outcomes. A fast model that fails these checks is unsuitable.

A CUDA-enabled llama.cpp server is a plausible low-concurrency local prototype because its official server supports GPU offload, schema-constrained JSON, slots and timing metrics: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md . vLLM is a separate candidate if throughput under multiple clients becomes important; its official server supports structured output and explicit context/memory configuration: https://docs.vllm.ai/en/stable/examples/features/structured_outputs/ and https://docs.vllm.ai/en/stable/cli/serve/ . Engine choice requires a pinned build and a local fit/throughput test; no engine was selected or installed here.

Historical scientific claims remain tied to the old frozen runtime/model. A future active-model or prompt-interface switch requires a separately designed matched behavioral validation, including stochastic outcome handling, before activation. Operational changes that preserve exact request bytes can be tested as engineering optimizations; a new model, changed decoding, context truncation, constrained-output mechanism, or compact prompt is not behaviorally equivalent by assumption.
