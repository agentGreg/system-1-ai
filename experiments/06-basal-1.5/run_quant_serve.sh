#!/bin/bash
# Served path and latency of QUANT_PLAN.md v2: basal-serve --mode mlx for the ports that pass the raw decision rule,
# e03 + e04, two passes (latency = minimum of the per-pass medians). A watcher logs any other model process on the
# machine every 2 s to log_gpu_watch_quant.txt, so overlaps can be checked afterwards.
# usage: BASAL_ENV=/path/to/basal-env PORT=8017 bash run_quant_serve.sh
set -e
cd "$(dirname "$0")"
D=${MLX_DIR:-$HOME/models/basal-mlx}
export PORT=${PORT:-8017}
: > log_gpu_watch_quant.txt
(
  while true; do
    ps axo pid,command | grep -E "basal-serve|run_basal|run_mlx|mlx_lm|convert_mlx|llama|ollama" \
      | grep -v -E "grep|run_quant_serve" | grep -v -e "--port $PORT" | sed "s/^/$(date -u +%H:%M:%S) /" \
      >> log_gpu_watch_quant.txt || true
    sleep 2
  done
) &
WATCH=$!
trap "kill $WATCH 2>/dev/null || true" EXIT
for pass in 1 2; do
  for spec in "$D/basal-1.5-mini-MLX-bf16 mlx-bf16" "Remek/basal-1.5-mini-MLX-8bit mlx-8bit" \
              "$D/basal-1.5-mini-MLX-6bit mlx-6bit"; do
    set -- $spec
    bash run_serve.sh $1 mlx quant-$2-p$pass lat_e03 lat_e04
  done
done
echo ALLDONE
