# TEAM-ORCHESTRATION.md

## Quick Start
1. Route discovery to `team-recon`.
2. Split implementation by domain (`team-backend`, `team-frontend`, `team-ops`).
3. Run `team-security` in parallel with late-stage implementation if scope is stable.
4. Run `team-qa` after merges.
5. Update docs via `team-docs` when behavior changes.

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
