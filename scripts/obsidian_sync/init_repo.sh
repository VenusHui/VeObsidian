#!/usr/bin/env bash
set -euo pipefail

REPO_DIR=${1:-"/home/ubuntu/.openclaw/workspace/obsidian-kb-server"}

mkdir -p "$REPO_DIR"/{finance/inbox,ai/inbox,quant/inbox,shared/templates,.obsidian}

if [ ! -d "$REPO_DIR/.git" ]; then
  git -C "$REPO_DIR" init -b main
fi

cat > "$REPO_DIR/README.md" <<'EOF'
# Obsidian Knowledge Base

Server-ingested Feishu content organized by board:
- finance/
- ai/

Use local machine to `git pull` and open this folder in Obsidian.
EOF

cat > "$REPO_DIR/.gitignore" <<'EOF'
.DS_Store
Thumbs.db
EOF

git -C "$REPO_DIR" add .
git -C "$REPO_DIR" commit -m "chore: initialize obsidian kb structure" || true

echo "Initialized: $REPO_DIR"
