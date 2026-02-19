# TOOLS.md

Local tool notes and operational references.

## Conventions
- Prefer `rg` for search.
- Prefer recoverable deletes where available.

## Workforce Commands
- Route a task: `python3 scripts/agent_manager.py --task "Implement X"`
- Route as JSON: `python3 scripts/agent_manager.py --task "Implement X" --format json`
- Save dispatch plan: `python3 scripts/agent_manager.py --task "Implement X" --write-plan /tmp/dispatch.json`
- Validate workspace/roster: `scripts/run-workforce-audit.sh`

## Add Here
- SSH hosts
- Device aliases
- API endpoint references
- Environment-specific runbooks

## Commands
- Workforce audit: `./scripts/run-workforce-audit.sh [--root PATH] [--format text|json]`
