# Agent Manager Runbook

## Purpose
Automatically route a task to the right workforce teams and produce stage-ordered dispatch packets.

## Command
- Text plan:
  - `python3 scripts/agent_manager.py --task "Implement workforce heartbeat scheduler"`
- JSON plan:
  - `python3 scripts/agent_manager.py --task "Fix auth regression in API" --format json`
- Persist plan:
  - `python3 scripts/agent_manager.py --task "Add deployment guardrails" --write-plan /tmp/dispatch-plan.json`

## Stages
- `recon`
- `build` (parallel where possible)
- `security`
- `qa`
- `docs`

## Output Semantics
- `action=send_input`: team has an active agent ID and can be dispatched immediately.
- `action=spawn_required`: no active agent ID exists; spawn that team first.

## Config
- `orchestrator/manager-config.json`
- Update `team_registry` agent IDs when roster changes.
- Tune `intent_keywords` and `workflows` to change routing behavior.

## Post-Change Check
- Run: `scripts/run-workforce-audit.sh`
