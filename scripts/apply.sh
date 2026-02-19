#!/usr/bin/env bash
set -euo pipefail

TARGET_HOME="${1:-$HOME}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKSPACE_TPL="$REPO_ROOT/templates/workspace"
CODEX_TPL="$REPO_ROOT/templates/codex"
STAMP="$(date +%Y%m%d_%H%M%S)"

backup_file() {
  local file="$1"
  if [[ -f "$file" ]]; then
    cp "$file" "$file.bak.$STAMP"
  fi
}

mkdir -p "$TARGET_HOME/.codex" "$TARGET_HOME/orchestrator" "$TARGET_HOME/scripts" "$TARGET_HOME/docs" "$TARGET_HOME/memory"

# Apply .codex template (backup existing)
backup_file "$TARGET_HOME/.codex/config.toml"
cp "$CODEX_TPL/config.toml" "$TARGET_HOME/.codex/config.toml"

# Apply workspace core docs
for f in AGENTS.md WORKFORCE.md TEAM-ORCHESTRATION.md SOUL.md USER.md MEMORY.md HEARTBEAT.md TOOLS.md; do
  backup_file "$TARGET_HOME/$f"
  cp "$WORKSPACE_TPL/$f" "$TARGET_HOME/$f"
done

# Apply orchestrator + scripts + docs
cp "$WORKSPACE_TPL/orchestrator/manager-config.json" "$TARGET_HOME/orchestrator/manager-config.json"
cp "$WORKSPACE_TPL/scripts/agent_manager.py" "$TARGET_HOME/scripts/agent_manager.py"
cp "$WORKSPACE_TPL/scripts/workforce_audit.py" "$TARGET_HOME/scripts/workforce_audit.py"
cp "$WORKSPACE_TPL/scripts/workforce_audit_lib.py" "$TARGET_HOME/scripts/workforce_audit_lib.py"
cp "$WORKSPACE_TPL/scripts/run-workforce-audit.sh" "$TARGET_HOME/scripts/run-workforce-audit.sh"
cp "$WORKSPACE_TPL/scripts/sync_agent_ids.py" "$TARGET_HOME/scripts/sync_agent_ids.py"
cp "$WORKSPACE_TPL/docs/workforce-audit.md" "$TARGET_HOME/docs/workforce-audit.md"
cp "$WORKSPACE_TPL/docs/agent-manager.md" "$TARGET_HOME/docs/agent-manager.md"
cp "$WORKSPACE_TPL/memory/heartbeat-state.json" "$TARGET_HOME/memory/heartbeat-state.json"

chmod +x "$TARGET_HOME/scripts/agent_manager.py" "$TARGET_HOME/scripts/run-workforce-audit.sh" "$TARGET_HOME/scripts/sync_agent_ids.py"

cat <<MSG
Applied Codex workforce sync to: $TARGET_HOME

Next steps:
1) cd "$TARGET_HOME"
2) python3 scripts/sync_agent_ids.py
3) scripts/run-workforce-audit.sh
4) python3 scripts/agent_manager.py --task "Test routing" --format text
MSG
