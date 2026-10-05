#!/bin/bash
# Final latency pass of experiment 06: every latency-bearing run, one after another, with nothing else on the GPU.
# A watcher logs (every 2 s) any other model process on the machine to log_gpu_watch.txt, so overlaps can be checked.
# PyTorch MPS runs repeat the accuracy runs (deterministic; analyze.py checks the predictions are identical).
# usage: BASAL_ENV=/path/to/basal-env bash run_latency_pass.sh
set -e
cd "$(dirname "$0")"
PY=../../.venv/bin/python
ME=$$
(
  while true; do
    ps axo pid,command | grep -E "basal-serve|run_basal|mlx_lm|convert_mlx|run_serve.py|llama|ollama" \
      | grep -v -E "grep|run_latency_pass" | grep -v -e "--port 8000" -e "--out lat_basal-1.5-" \
      -e "--label basal-1.5-" | sed "s/^/$(date -u +%H:%M:%S) /" >> log_gpu_watch.txt || true
    sleep 2
  done
) &
WATCH=$!
trap "kill $WATCH 2>/dev/null || true" EXIT
: > log_gpu_watch.txt
wait_port() { until ! curl -sf http://127.0.0.1:8000/health > /dev/null; do sleep 1; done; sleep 2; }
step() { echo "start $* $(date -u +%H:%M:%S)" >> log_latency_pass.txt; "$@"; echo "end $* $(date -u +%H:%M:%S)" >> log_latency_pass.txt; }
: > log_latency_pass.txt
for m in mini 4.5B max; do
  case $m in mini) id=Remek/basal-1.5-mini ;; 4.5B) id=Remek/basal-1.5-4.5B ;; max) id=Remek/basal-1.5-max ;; esac
  for s in e03 e04; do
    step $PY run_basal.py --model $id --set $s --out lat_basal-1.5-${m}_${s}.jsonl > log_lat_basal-1.5-${m}_${s}.txt 2>&1
  done
done
export PORT=8000
for spec in "Remek/basal-1.5-mini-MLX-8bit mlx basal-1.5-mini lat_e03 lat_e04 soam" \
            "Remek/basal-1.5-4.5B-MLX-8bit mlx basal-1.5-4.5B lat_e03 lat_e04 soam" \
            "Remek/basal-1.5-max-MLX-8bit mlx basal-1.5-max lat_e03 lat_e04" \
            "Remek/basal-1.5-mini mps basal-1.5-mini lat_e03 lat_e04 soam" \
            "Remek/basal-1.5-4.5B mps basal-1.5-4.5B lat_e03 lat_e04 soam evidence"; do
  wait_port
  step bash run_serve.sh $spec
done
echo ALLDONE >> log_latency_pass.txt
