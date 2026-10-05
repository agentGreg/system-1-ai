#!/bin/bash
# Runs with basal-serve v1.5.0 on this Mac: starts a server, runs run_serve.py tasks against it, stops it.
# Needs a separate environment with the engine:  uv venv --python 3.12 basal-env &&
#   uv pip install --python basal-env/bin/python "basal[mlx] @ https://github.com/rkinas/basal/archive/refs/tags/v1.5.0.tar.gz"
# usage: BASAL_ENV=/path/to/basal-env bash run_serve.sh <hf repo> <mode> <tag> <task> [<task> ...]
#        tasks: lat_e03 lat_e04 soam evidence
set -e
cd "$(dirname "$0")"
REPO=$1; MODE=$2; TAG=$3; shift 3
export PORT=${PORT:-8000}
PY=$BASAL_ENV/bin/python
# refuse to run against a server someone else already started on the port
if curl -sf http://127.0.0.1:$PORT/health > /dev/null; then echo "port $PORT already in use"; exit 1; fi
$BASAL_ENV/bin/basal-serve --model "$REPO" --mode "$MODE" --port $PORT --host 127.0.0.1 > log_serve_${MODE}_${TAG}.txt 2>&1 &
SRV=$!
trap "kill $SRV 2>/dev/null; wait $SRV 2>/dev/null || true" EXIT
for i in $(seq 1 600); do
  curl -sf http://127.0.0.1:$PORT/health > /dev/null && break
  kill -0 $SRV 2>/dev/null || { echo "server died"; tail -20 log_serve_${MODE}_${TAG}.txt; exit 1; }
  sleep 1
done
LABEL="$TAG ($REPO, basal-serve --mode $MODE)"
for t in "$@"; do
  case $t in
    lat_e03) $PY run_serve.py latency --set e03 --label "$LABEL" --out raw_serve_${MODE}_${TAG}_e03.jsonl > log_serve_${MODE}_${TAG}_e03.txt 2>&1 ;;
    lat_e04) $PY run_serve.py latency --set e04 --label "$LABEL" --out raw_serve_${MODE}_${TAG}_e04.jsonl > log_serve_${MODE}_${TAG}_e04.txt 2>&1 ;;
    soam) $PY run_serve.py soam --label "$LABEL" --out raw_soam_${MODE}_${TAG}.json > log_soam_${MODE}_${TAG}.txt 2>&1 ;;
    evidence) $PY run_serve.py evidence --label "$LABEL" --out raw_evidence_${MODE}_${TAG}.jsonl > log_evidence_${MODE}_${TAG}.txt 2>&1 ;;
  esac
  echo "done $TAG $MODE $t $(date -u +%H:%M:%S)"
done
