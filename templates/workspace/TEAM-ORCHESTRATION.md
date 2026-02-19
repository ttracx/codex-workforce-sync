# TEAM-ORCHESTRATION.md

## Quick Start
1. Run requirements understanding first (`agent_manager.py` requirement analysis + `codex_agents` team selection).
2. Treat every task as a feature workflow (`feature_first_demo_ready` mode).
3. Run mandatory `demo_ready_app_planning` phase before assignment execution.
4. Create route assignments from requirements (`route_assignments` in plan output).
5. Execute automation pipeline phases (`requirements_understanding -> demo_ready_app_planning -> route_and_assignment_creation -> automation_pipeline_execution`).
6. Run `team-security` in parallel with late-stage implementation if scope is stable.
7. Run `team-qa` after merges.
8. Update docs via `team-docs` when behavior changes.

## Parallelism Policy
Safe to run in parallel:
- Recon + environment checks
- Backend + frontend when file boundaries are clear
- Security review on stable patches

Do not run in parallel:
- Two builders editing same files
- Final refactor and final validation on moving targets

## Escalation Thresholds
Require explicit user confirmation for:
- Destructive file/system commands
- External outbound actions
- Irreversible operations

## Definition of Done
- Implementation complete and scoped
- Validation run (or blocked reason documented)
- Risks documented
- Relevant docs/memory updated
