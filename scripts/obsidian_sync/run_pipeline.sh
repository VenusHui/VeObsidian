#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$SCRIPT_DIR/../.." && pwd)"
MAPPING="$SCRIPT_DIR/channels.json"
LOGDIR="$SCRIPT_DIR/logs"
mkdir -p "$LOGDIR"

DAY="${1:-}"

cd "$REPO"

run_with_retry() {
  local cmd="$1"
  if eval "$cmd" >> "$LOGDIR/pipeline.log" 2>&1; then
    return 0
  fi
  echo "[retry] $cmd" >> "$LOGDIR/pipeline.log"
  sleep 2
  eval "$cmd" >> "$LOGDIR/pipeline.log" 2>&1
}

run_with_retry "python3 '$SCRIPT_DIR/collect_from_sessions.py' --repo '$REPO' --mapping '$MAPPING'"

if [[ -n "$DAY" ]]; then
  run_with_retry "python3 '$SCRIPT_DIR/summarize_daily.py' --repo '$REPO' --day '$DAY'"
  TARGET_DAY="$DAY"
else
  run_with_retry "python3 '$SCRIPT_DIR/summarize_daily.py' --repo '$REPO'"
  TARGET_DAY=$(TZ=Asia/Shanghai date -d 'yesterday' +%F)
fi

run_with_retry "python3 '$SCRIPT_DIR/memory_compact.py' --repo '$REPO' --day '$TARGET_DAY' --max-tokens 3000"

cd "$REPO"
if [[ -n "$(git status --porcelain)" ]]; then
  git add .
  git commit -m "daily-kb: ${TARGET_DAY}"
  git push
fi

echo "pipeline done for ${TARGET_DAY}" >> "$LOGDIR/pipeline.log"
