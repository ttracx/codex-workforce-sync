#!/usr/bin/env python3
"""Sync active runtime agent IDs from WORKFORCE.md into manager-config.json."""

from __future__ import annotations

import json
from pathlib import Path
import re

ROSTER_HEADER = "## Active Runtime Roster"
ROSTER_LINE = re.compile(r"^-\s+([a-z0-9-]+):\s+`([^`]+)`\s*$")


def parse_roster(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    in_roster = False
    entries: dict[str, str] = {}

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if line.startswith("## "):
            if line.startswith(ROSTER_HEADER):
                in_roster = True
                continue
            if in_roster:
                break

        if in_roster and line.startswith("-"):
            m = ROSTER_LINE.match(line)
            if m:
                team, agent_id = m.group(1), m.group(2)
                entries[team] = agent_id

    return entries


def main() -> int:
    root = Path(".").resolve()
    workforce = root / "WORKFORCE.md"
    config = root / "orchestrator" / "manager-config.json"

    if not workforce.is_file() or not config.is_file():
        raise SystemExit("WORKFORCE.md or orchestrator/manager-config.json not found")

    roster = parse_roster(workforce)
    cfg = json.loads(config.read_text(encoding="utf-8"))

    registry = cfg.get("team_registry", {})
    changed = 0
    for team, values in registry.items():
        new_id = roster.get(team)
        old_id = values.get("agent_id")
        if old_id != new_id:
            values["agent_id"] = new_id
            changed += 1

    config.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    print(f"Synced agent IDs. Updated entries: {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
