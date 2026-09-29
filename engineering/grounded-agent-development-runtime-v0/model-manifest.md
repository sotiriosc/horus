# Candidate model manifest

- Publisher/repository: [Qwen/Qwen3-14B-GGUF](https://huggingface.co/Qwen/Qwen3-14B-GGUF), repository revision `530227a7d994db8eca5ab5ced2fb692b614357fd`.
- Exact artifact: `Qwen3-14B-Q4_K_M.gguf`; size **9,001,752,960 bytes** (8.38 GiB); SHA-256 **`500a8806e85ee9c83f3ae08420295592451379b4f8cf2d0f41c15dffeb6b81f0`**, matching the publisher's LFS SHA-256 object identity. No model substitution was made.
- License: Apache 2.0 as identified on the publisher's model card.
- Loaded metadata: GGUF V3, architecture `qwen3`, `Q4_K - Medium`, quantization version 2, 40 blocks, 5120 embedding width, 40 attention heads/8 KV heads, and embedded `qwen3.context_length=40960`. The card states 32,768 native tokens; only 2048, 8192, and 16384 were tested here, below both figures.
- Embedded tokenizer: GGUF `tokenizer.ggml.model=gpt2`, pretokenizer `qwen2`, 151,936 tokens, 151,387 merges, BOS insertion disabled, EOS token ID 151645. The full artifact digest authenticates the embedded tokenizer and template bytes.
- Chat template: embedded Qwen3 Jinja template from the GGUF, supporting `enable_thinking=false` through `chat_template_kwargs`. No replacement template file or prompt compression was used. New-runtime tokenizer counts differ from the historical Dolphin Mixtral counts and are reported separately.

The model is a development candidate only. Historical scientific results remain tied to the frozen Dolphin Mixtral digest `4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`.
