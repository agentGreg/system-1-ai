#!/bin/bash
# Raw readouts of QUANT_PLAN.md v2 (basal-1.5-mini): every MLX port with run_mlx.py, the fp32 dtype floor and the
# missing bf16 reference runs with run_basal.py. Sequential, one model at a time. Latency is measured separately.
# Ports from convert_mlx.py are read from $MLX_DIR (default ~/models/basal-mlx).
# usage: bash run_quant.sh
set -e
cd "$(dirname "$0")"
PY=../../.venv/bin/python
D=${MLX_DIR:-$HOME/models/basal-mlx}
EXTRA() {  # $1 = runner, $2 = model, $3 = tag
  $PY $1 --model $2 --set rules99 --facts auto --out raw_$3_rules99_facts.jsonl > log_$3_rules99_facts.txt 2>&1
  $PY $1 --model $2 --set rules99 --rule-in-state --out raw_$3_rules99_ris.jsonl > log_$3_rules99_ris.txt 2>&1
  $PY $1 --model $2 --set rc_orig --out raw_$3_rc_orig.jsonl > log_$3_rc_orig.txt 2>&1
  $PY $1 --model $2 --set rc_changed --out raw_$3_rc_changed.jsonl > log_$3_rc_changed.txt 2>&1
}
# reference: the bf16 runs of experiment 06 are reused; rule-change runs only if missing (never overwritten)
for s in rc_orig rc_changed; do
  [ -f raw_basal-1.5-mini_$s.jsonl ] || $PY run_basal.py --model Remek/basal-1.5-mini --set $s \
    --out raw_basal-1.5-mini_$s.jsonl > log_basal-1.5-mini_$s.txt 2>&1
done
echo "done torch-bf16 extras $(date -u +%H:%M:%S)"
# dtype floor
for s in e03 e04; do
  $PY run_basal.py --model Remek/basal-1.5-mini --dtype float32 --set $s --out raw_torch-fp32_mini_$s.jsonl > log_torch-fp32_mini_$s.txt 2>&1
done
echo "done torch-fp32 $(date -u +%H:%M:%S)"
for spec in "bf16 $D/basal-1.5-mini-MLX-bf16" "8bit Remek/basal-1.5-mini-MLX-8bit" "fp4 Remek/basal-1.5-mini-MLX-fp4" \
            "6bit $D/basal-1.5-mini-MLX-6bit" "4bit $D/basal-1.5-mini-MLX-4bit" \
            "4bit-g32 $D/basal-1.5-mini-MLX-4bit-g32" "mixed-4-6 $D/basal-1.5-mini-MLX-mixed-4-6"; do
  set -- $spec
  tag=mlx-$1_mini
  for s in e03 e04; do
    $PY run_mlx.py --model $2 --set $s --out raw_${tag}_$s.jsonl > log_${tag}_$s.txt 2>&1
  done
  EXTRA run_mlx.py $2 $tag
  echo "done $tag $(date -u +%H:%M:%S)"
done
# determinism: one port twice
$PY run_mlx.py --model $D/basal-1.5-mini-MLX-6bit --set e04 --out raw_mlx-6bit_mini_e04_repeat.jsonl > log_mlx-6bit_mini_e04_repeat.txt 2>&1
echo ALLDONE
