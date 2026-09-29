# HISTORICAL_REPRO_RUNTIME

Frozen scientific runtime for the promoted grounded-authority plus BOUNDED_STAGNATION_ESCAPE agent. This record describes the existing local service; it does not update it. Historical claims remain tied to their original archived calls, not to this engineering benchmark.

| Item | Observed value |
| --- | --- |
| Binary | /usr/local/bin/ollama, SHA-256 96f082b45229387e3839682a49a80129cdf0c95cb223d8e74089677478f67e15 |
| CLI/server | Ollama 0.1.16, server PID 918574 when inspected |
| Server launch | /usr/local/bin/ollama serve; listening on 127.0.0.1:11434 |
| Model | dolphin-mixtral:latest, digest 4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a |
| Artifact | GGUF V3, 47B, Q4_0, 26,441,544,856 bytes |
| Model blob identity | sha256:bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3, as shown in runner command |
| Template SHA-256 | a47b02e00552cd7022ea700b1abf8c572bb26c9bc8c1a37e01b566f2344df5dc |
| Stored parameters SHA-256 | 05af43222e4c4cab1829682f6d59d2acba7d5ebe4cc8d78716ac37c0b384b91b |
| Stored parameters | num_ctx 4096; stop tokens <|im_end|>, <|im_start|>, <|im_end|> |
| Action request | stream=false, format=json; temperature 0.2, top_p 0.9, top_k 40, repeat_penalty 1.1, num_ctx 2048, num_predict 48; frozen run/decision seed; no request-level stop or keep_alive override |
| Retrospective self-diagnosis request | num_ctx 8192, num_predict 1024, same temperature/top-p/top-k/repetition settings; different historical role and prompt |
| GPU | NVIDIA GeForce RTX 4090, 24,564 MiB reported total, driver 616.92 under WSL |
| GPU offload | Prior logs: 21/33 layers. Benchmark start: 20/33 layers, context 2048, batch 512; runner model/context VRAM 15,995.91 MiB and total GPU use about 19.6 GiB |
| Service environment | No OLLAMA_, CUDA_, GGML_, OMP_, OPENBLAS_, or MKL_ variables observed in /proc/918574/environ |
| Server log | /tmp/horus-v018-ollama.log (local; not published). Startup line on 2026-09-26 records version and listen address. Later lines record runner loads, offload counts, context sizes and request wall times. |

The installed model file is larger than the physical GPU memory, so full residency of this exact artifact on one 4090 is impossible. The current 20/33 offload differs from the earlier frozen 21/33 observation because available VRAM at load differed; neither setting was changed deliberately for this milestone. The 8192-token review probe temporarily requested its historical context at 20/33 GPU layers and then restored the 2048-token action context. The restored runner was PID 2925004 at 21/33 GPU layers, verified by its command line and server log. The Ollama binary, model files, server command, research scripts and historical settings were not replaced.

Provenance: research/action-model-reproducibility-audit-v0/source-manifest.json and verification.json preserve the same model/version/template/parameter identities and earlier 21-layer observation. The promoted source commit is 8bc396b96662ff7fa04b87a7a3300008e12228b9. The benchmark record contains only request hashes and timing/device metadata, not raw model outputs or private historical calls.

The historical grounded-self-diagnosis-v0 study remains INVALID: its three logical review calls each exhausted two 600-second transport attempts without text. The engineering 30-decision probe similarly timed out at 900 seconds with an eight-token cap and no response. Neither result is valid behavioral evidence; both are runtime observations.
