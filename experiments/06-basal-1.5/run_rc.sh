#!/bin/bash
# Rule-change test, local plain-PyTorch MPS runs (gold committed in 7d6ef19 before these runs).
# usage: bash run_rc.sh 1.0-4.5B mini 4.5B max
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
  for v in orig changed; do
    $PY run_basal.py --model $id --set rc_$v --out raw_${tag}_rc_$v.jsonl > log_${tag}_rc_$v.txt 2>&1
    if [ "$m" != "1.0-4.5B" ]; then
      $PY run_basal.py --model $id --set rc_$v --rule-in-state --out raw_${tag}_rc_${v}_ris.jsonl > log_${tag}_rc_${v}_ris.txt 2>&1
    fi
  done
  echo "done rc $m $(date -u +%H:%M:%S)"
done
