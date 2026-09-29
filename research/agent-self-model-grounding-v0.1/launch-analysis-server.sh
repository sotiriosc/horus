#!/usr/bin/env bash
set -euo pipefail
asset_root=/tmp/horus-development-runtime-assets
engine_dir="$asset_root/engine/llama-b11242"
cuda_dir="$asset_root/engine/cudart-llama-b11242-bin-ubuntu-cuda-12.8-x64"
compat_dir="$asset_root/compat/root/usr/lib/x86_64-linux-gnu"
cd "$engine_dir"
exec "$compat_dir/ld-linux-x86-64.so.2" --library-path "$compat_dir:$engine_dir:$cuda_dir" "$engine_dir/llama-server" \
 --model "$asset_root/model/Qwen3-14B-Q4_K_M.gguf" --host 127.0.0.1 --port 18083 --ctx-size 16384 \
 --n-gpu-layers 999 --parallel 1 --jinja --flash-attn on --metrics --log-verbosity 4 \
 --reasoning on --reasoning-format deepseek --reasoning-budget 512
