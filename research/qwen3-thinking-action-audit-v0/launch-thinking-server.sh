#!/usr/bin/env bash
set -euo pipefail
asset_root="${DEVELOPMENT_RUNTIME_ASSETS:-/tmp/horus-development-runtime-assets}"
engine_dir="$asset_root/engine/llama-b11242"
cuda_dir="$asset_root/engine/cudart-llama-b11242-bin-ubuntu-cuda-12.8-x64"
compat_dir="$asset_root/compat/root/usr/lib/x86_64-linux-gnu"
loader="$compat_dir/ld-linux-x86-64.so.2"
model="$asset_root/model/Qwen3-14B-Q4_K_M.gguf"
cd "$engine_dir"
exec "$loader" --library-path "$compat_dir:$engine_dir:$cuda_dir" "$engine_dir/llama-server" \
  --model "$model" --host 127.0.0.1 --port 18081 --ctx-size 8192 \
  --n-gpu-layers 999 --parallel 1 --jinja --flash-attn on --metrics --log-verbosity 4 \
  --reasoning on --reasoning-format deepseek
