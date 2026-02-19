# codex-workforce-sync

Portable Codex workforce bootstrap for multi-node setups (Linux/macOS).

## One-liner install

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/ttracx/codex-workforce-sync/main/install.sh)"
```

## What it syncs
- `~/.codex/config.toml`
- Workspace governance files (`AGENTS.md`, `WORKFORCE.md`, etc.)
- Orchestrator config (`orchestrator/manager-config.json`)
- Routing and audit scripts (`scripts/agent_manager.py`, `scripts/run-workforce-audit.sh`, etc.)
- Runbooks under `docs/`

## Notes
- Existing files are backed up as `*.bak.YYYYmmdd_HHMMSS` before overwrite.
- Runtime agent IDs in `WORKFORCE.md` and `orchestrator/manager-config.json` are session-specific; update them as needed on each node/session.
- After each session starts, run `python3 scripts/sync_agent_ids.py` to sync live IDs from `WORKFORCE.md`.
