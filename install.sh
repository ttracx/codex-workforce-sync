#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${CODEX_SYNC_REPO_URL:-}"
TARGET_HOME="${1:-$HOME}"
INSTALL_DIR="${CODEX_SYNC_INSTALL_DIR:-$HOME/.codex-workforce-sync}"

if [[ -z "$REPO_URL" ]]; then
  echo "Set CODEX_SYNC_REPO_URL first, e.g.:"
  echo "  export CODEX_SYNC_REPO_URL=https://github.com/<you>/codex-workforce-sync.git"
  exit 1
fi

if [[ -d "$INSTALL_DIR/.git" ]]; then
  git -C "$INSTALL_DIR" pull --ff-only
else
  git clone "$REPO_URL" "$INSTALL_DIR"
fi

bash "$INSTALL_DIR/scripts/apply.sh" "$TARGET_HOME"
