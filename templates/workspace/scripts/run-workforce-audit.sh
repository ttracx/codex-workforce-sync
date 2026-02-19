#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ "$#" -eq 0 ]; then
  exec python3 "$SCRIPT_DIR/workforce_audit.py" --format text
fi

exec python3 "$SCRIPT_DIR/workforce_audit.py" "$@"
