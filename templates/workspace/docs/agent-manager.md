# Agent Manager Runbook

## Purpose
Automatically route a task to the right workforce teams and produce stage-ordered dispatch packets.
Now includes requirements-first pipeline creation from `codex_agents` team libraries before route assignment.
All tasks are normalized to feature-first mode and include demo-ready app planning in pipeline phases.

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
- `requirement_analysis`: task-domain understanding that drives routing.
- `codex_agents.selected_teams`: teams selected from `codex_agents/teams` catalog based on requirements.
- `pipeline_automation.phases`: automation pipeline created after requirements analysis and assignment mapping.

## Config
- `orchestrator/manager-config.json`
- Update `team_registry` agent IDs when roster changes.
- Tune `intent_keywords` and `workflows` to change routing behavior.
- `codex_agents.teams_root_candidates` controls where team catalogs are loaded from.

## Post-Change Check
- Run: `scripts/run-workforce-audit.sh`
