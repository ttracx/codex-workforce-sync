# WORKFORCE.md - Codex Team Registry

Last Updated: 2026-02-19
Status: Active

## Architecture
Human -> Orchestrator (Codex main session) -> Team Leads (agents) -> Task outputs -> Validator -> Final response

## Runtime Capacity
- Max concurrent spawned agents: 6
- When at cap, prefer this priority order:
  1. team-recon
  2. team-backend
  3. team-frontend
  4. team-ops
  5. team-security
  6. team-qa
- `team-docs` runs as a virtual role when saturated (assigned to `team-qa` or orchestrator).

## Active Runtime Roster (2026-02-19)
- team-recon: `019c77d1-fcde-7400-87c7-718a35b6509a`
- team-backend: `019c77d1-fcea-7710-b3c9-f973f4696e9d`
- team-docs: `019c77d7-b4ff-7fe3-a88f-136c2bb6b5d8`
- team-qa: `019c77d1-fd06-7961-a7ba-e2da4532b480`
- team-ops: `019c77d2-0d91-7943-be8e-ad20164dcc69`
- team-security: `019c77d6-a464-7eb0-974c-2c5257683c90`

## Persistent Team Definitions

### team-recon
- Agent type: `explorer`
- Mission: repo discovery, dependency mapping, risk surface analysis
- Owns: file discovery, impact analysis, implementation plans
- Output contract: concise map of files, assumptions, and unknowns

### team-backend
- Agent type: `worker`
- Mission: backend features, APIs, services, data flows
- Owns: server code, migrations, backend tests
- Output contract: code diff summary + behavior changes + test notes

### team-frontend
- Agent type: `worker`
- Mission: UI implementation and client-side behavior
- Owns: components, pages, styles, frontend tests
- Output contract: code diff summary + UX implications + test notes

### team-ops
- Agent type: `worker`
- Mission: tooling, scripts, CI/CD, deployment guardrails
- Owns: build scripts, pipeline config, environment setup
- Output contract: operational changes + rollback notes

### team-security
- Agent type: `worker`
- Mission: security review, secrets hygiene, permission boundaries
- Owns: threat checks, auth/authz concerns, dependency risk flags
- Output contract: severity-ranked findings and mitigations

### team-qa
- Agent type: `worker`
- Mission: verification, regression checks, acceptance validation
- Owns: test execution, repro scripts, smoke checks
- Output contract: pass/fail matrix and residual risk list

### team-docs
- Agent type: `worker`
- Mission: documentation, runbooks, changelogs
- Owns: docs updates tied to code behavior changes
- Output contract: updated references and operator guidance

## Delegation Rules
- One owner per deliverable.
- Parallelize only independent tasks.
- Security and QA review all high-risk changes.
- Merge order: recon -> builders -> security -> qa -> docs.
- Operational check: run `scripts/run-workforce-audit.sh` after workforce/session orchestration updates.

## Agent Manager
- Auto-router config: `orchestrator/manager-config.json`
- Routing command: `python3 scripts/agent_manager.py --task "<objective>"`
- Output includes staged team routing (`recon -> build -> security -> qa -> docs`) and whether each team can receive `send_input` now or needs `spawn_required`.
- Use `--format json` for machine-readable dispatch packets.

## Standard Task Packet
When dispatching, include:
- Objective
- Scope (paths/files)
- Constraints
- Done criteria
- Required checks

## Spawn Prompt Templates

Recon template:
"Map files and dependencies for <objective>. Return touched files, assumptions, and risks."

Builder template:
"Implement <objective> in <paths>. You are not alone in the codebase; ignore unrelated edits. Return exact changes and tests."

QA template:
"Validate <objective>. Run targeted tests and smoke checks. Return failures first, then residual risks."
