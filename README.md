# codex-workforce-sync

<!-- THOX-BADGES:START -->
[![Repository](https://img.shields.io/badge/repository-ttracx/codex--workforce--sync-0B1220)](https://github.com/ttracx/codex-workforce-sync)
![THOX.ai LLC](https://img.shields.io/badge/owner-THOX.ai%20LLC-00A676)
![Visibility](https://img.shields.io/badge/visibility-public-00A676)
![Leadership](https://img.shields.io/badge/CTO-Tommy%20Xaypanya-1F6FEB)
![Leadership](https://img.shields.io/badge/CEO-Craig%20Ross-6F42C1)
<!-- THOX-BADGES:END -->


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

<!-- THOX-DOCS-STANDARD:START -->
## Repository Description

THOX.ai LLC repository for codex workforce sync, including project documentation, release readiness, and legal baseline.

## Documentation

- [Repository documentation](docs/README.md)
- [Security policy](SECURITY.md)
- [Contributing guide](CONTRIBUTING.md)
- [Legal notice](NOTICE.md)

## THOX.ai LLC

This repository is maintained by THOX.ai LLC.

- Tommy Xaypanya is CTO.
- Craig Ross is CEO.

## Copyright and Legal

Copyright (c) 2026 THOX.ai LLC. All rights reserved unless this repository includes a separate license file that states otherwise.

THOX-specific documentation, configuration, branding, product definitions, and integration work are owned by THOX.ai LLC unless explicitly noted. Third-party dependencies, forks, vendored components, and upstream source materials remain governed by their original licenses and notices.
<!-- THOX-DOCS-STANDARD:END -->
