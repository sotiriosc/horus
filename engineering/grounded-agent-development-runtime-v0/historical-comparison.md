# Frozen historical comparison

The historical result is the unchanged [`runtime-performance-v0 benchmark`](../grounded-agent-runtime-performance-v0/benchmark-results.json) on Ollama 0.1.16 and `dolphin-mixtral:latest` (digest `4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`). Its 26.44 GB Q4_0 artifact used only 20–21/33 GPU layers. No old-runtime inference was repeated.

| Public-safe shape | Frozen Dolphin Mixtral | Isolated Qwen3 Q4_K_M |
|---|---:|---:|
| P1 tiny | Frozen B1 warm: 55 rendered tokens, 3.52 s prefill, 4.48 s wall; a separate minimal tokenizer-only probe was 30 tokens | 46 input tokens including Qwen template; 0.39 s warm, 19 generated tokens |
| P2 compact | 107 input tokens, 6.45 s prefill | 78 input tokens, 0.055 s prefill, 0.42 s wall |
| P3 representative action | 559 tokens, 31.82 s prefill, 17.57 tok/s; 32.80 s wall | Same public-safe semantic shape, 438 Qwen tokens, 0.098 s prefill, 4,450 tok/s; eight-token action in 0.239 s wall |
| P4 five-decision retrospective | 1,554 tokens, 88.82 s prefill, 17.50 tok/s | Same public-safe content, 1,159 Qwen tokens, 0.257 s prefill, 4,518 tok/s |
| P5 30-decision retrospective | 6,321 rendered historical tokens; no response within 900 s (censored) | Same sanitized input, 4,943 Qwen tokens; complete 192-token response in 4.40 s at 8192 context |

The measured P3 prefill rate is **253×** the historical rate, and its prefill duration is **323×** shorter. These are descriptive ratios across **different models, tokenizers, constrained-output interfaces, and runtimes**; they do not isolate an engine effect or establish behavioral equivalence. The old P5 has no completed phase timing, so no speed ratio is computed. The new P4 wall time includes 104 output tokens versus the historical eight-token cap and is not a matched generation comparison.

The frozen action-model audit found no queue bottleneck. The new run used one client and one slot, with no other development request queued. llama.cpp reported prompt and generation phase durations; client wall minus those phases remains HTTP/scheduling overhead rather than an independently measured queue duration. GPU utilization in [`benchmark-results.json`](benchmark-results.json) is a before/after `nvidia-smi` snapshot per call, not a sampled phase average.
