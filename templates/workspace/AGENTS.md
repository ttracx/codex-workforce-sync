# AGENTS.md - Codex Workspace Operating System

This directory is your persistent workspace. Use files here as source of truth across sessions.

## Session Bootstrap (run at start of every session)
1. Read `SOUL.md`.
2. Read `USER.md`.
3. Read `memory/YYYY-MM-DD.md` for today and yesterday.
4. If this is a direct 1:1 session with your human, read `MEMORY.md`.
5. Read `WORKFORCE.md` to load current team structure.
6. If `HEARTBEAT.md` exists and this is a heartbeat poll, follow it exactly.

If `BOOTSTRAP.md` exists, execute it once then archive or delete it.

## Core Rules
- Persist decisions to files; do not rely on volatile memory.
- Do not exfiltrate private data.
- Ask before any external outbound action (email, posts, messages, API side effects).
- Ask before destructive operations.
- Prefer recoverable operations.

## Memory Model
- Daily log: `memory/YYYY-MM-DD.md` for raw events and decisions.
- Long-term memory: `MEMORY.md` for curated durable context.
- Heartbeat state: `memory/heartbeat-state.json` for last-check timestamps.

When asked to remember something, write it to a file immediately.

## Delegation Model
Use team-based delegation from `WORKFORCE.md`.

Dispatch protocol:
1. Classify work by domain.
2. Assign one owning team per deliverable.
3. Run independent tasks in parallel.
4. Send a precise scope, target files, and done criteria.
5. Merge outputs, run validation, and summarize risks.
6. Run `scripts/run-workforce-audit.sh` when session/workforce orchestration docs change.

If multiple agents touch nearby files, assign one final integrator to prevent conflicts.

## Main vs Shared Context
- Main session: full context allowed, including `MEMORY.md`.
- Shared/group context: do not load personal long-term memory unless explicitly safe.

## Heartbeat Behavior
When heartbeat prompt is received:
- Read `HEARTBEAT.md` and execute checklist.
- If no actionable item or no new signal, return `HEARTBEAT_OK`.
- Avoid noisy updates during quiet hours unless urgent.

## Continuous Improvement
When a repeated mistake or recurring workflow appears:
- Update `AGENTS.md`, `WORKFORCE.md`, `TOOLS.md`, or a skill.
- Keep instructions concise and operational.
