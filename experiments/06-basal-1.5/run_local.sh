#!/bin/bash
# Local plain-PyTorch MPS runs of experiment 06 (one model at a time, sequential, nothing else on the GPU).
# usage: bash run_local.sh mini 4.5B max 1.0-4.5B
set -e
cd "$(dirname "$0")"
PY=../../.venv/bin/python
for m in "$@"; do
  case $m in
    mini) id=Remek/basal-1.5-mini; tag=basal-1.5-mini ;;
    4.5B) id=Remek/basal-1.5-4.5B; tag=basal-1.5-4.5B ;;
    max) id=Remek/basal-1.5-max; tag=basal-1.5-max ;;
    1.0-4.5B) id=Remek/basal-1.0-4.5B; tag=basal-1.0-4.5B ;;
  esac
  if [ "$m" != "1.0-4.5B" ]; then
    $PY run_basal.py --model $id --set e03 --out raw_${tag}_e03.jsonl > log_${tag}_e03.txt 2>&1
    $PY run_basal.py --model $id --set e04 --out raw_${tag}_e04.jsonl > log_${tag}_e04.txt 2>&1
  fi
  $PY run_basal.py --model $id --set rules99 --facts auto --out raw_${tag}_rules99_facts.jsonl > log_${tag}_rules99_facts.txt 2>&1
  $PY run_basal.py --model $id --set rules99 --rule-in-state --out raw_${tag}_rules99_ris.jsonl > log_${tag}_rules99_ris.txt 2>&1
  $PY run_basal.py --model $id --set rules99 --rule-in-state --facts auto --out raw_${tag}_rules99_ris_facts.jsonl > log_${tag}_rules99_ris_facts.txt 2>&1
  echo "done $m $(date -u +%H:%M:%S)"
done
