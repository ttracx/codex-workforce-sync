"""Audit helpers for workspace governance files."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re
from typing import Dict, List

REQUIRED_FILES = [
    "AGENTS.md",
    "WORKFORCE.md",
    "TEAM-ORCHESTRATION.md",
    "SOUL.md",
    "USER.md",
    "MEMORY.md",
    "HEARTBEAT.md",
    "TOOLS.md",
    "memory/heartbeat-state.json",
]

ROSTER_LINE_RE = re.compile(r"^-\s+([a-z0-9-]+):\s+`([^`]+)`\s*$")
UUID_LIKE_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
MAX_WORKFORCE_BYTES = 1_048_576


@dataclass
class AuditResult:
    ok: bool
    checked_root: str
    required_files: List[str]
    missing_files: List[str]
    roster_entries: List[Dict[str, str]]
    invalid_agent_ids: List[Dict[str, str]]
    duplicate_agent_ids: List[str]
    errors: List[str]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)



def _find_active_roster_lines(workforce_text: str) -> List[str]:
    in_roster = False
    lines: List[str] = []

    for raw_line in workforce_text.splitlines():
        line = raw_line.rstrip("\n")

        stripped = line.lstrip()
        if stripped.startswith("## "):
            if stripped.lower().startswith("## active runtime roster"):
                in_roster = True
                continue
            if in_roster:
                break

        if in_roster and stripped.startswith("- "):
            lines.append(stripped)

    return lines


def _is_safe_file_under_root(root: Path, rel_path: str) -> bool:
    candidate = root / rel_path

    try:
        # Reject symlinks and only accept regular files located under root.
        if candidate.is_symlink() or not candidate.is_file():
            return False
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except (FileNotFoundError, OSError, ValueError, RuntimeError):
        return False

    return True


def _safe_line_preview(raw_line: str, max_len: int = 160) -> str:
    # Keep diagnostics readable and prevent terminal control sequences leakage.
    escaped = raw_line.encode("unicode_escape").decode("ascii")
    return escaped if len(escaped) <= max_len else escaped[: max_len - 3] + "..."



def run_audit(root: Path) -> AuditResult:
    errors: List[str] = []
    try:
        root = root.resolve(strict=True)
    except (FileNotFoundError, OSError, RuntimeError):
        return AuditResult(
            ok=False,
            checked_root=str(root),
            required_files=REQUIRED_FILES,
            missing_files=REQUIRED_FILES,
            roster_entries=[],
            invalid_agent_ids=[],
            duplicate_agent_ids=[],
            errors=["Audit root does not exist or is not accessible"],
        )

    if not root.is_dir():
        return AuditResult(
            ok=False,
            checked_root=str(root),
            required_files=REQUIRED_FILES,
            missing_files=REQUIRED_FILES,
            roster_entries=[],
            invalid_agent_ids=[],
            duplicate_agent_ids=[],
            errors=["Audit root is not a directory"],
        )

    missing_files = [path for path in REQUIRED_FILES if not _is_safe_file_under_root(root, path)]

    roster_entries: List[Dict[str, str]] = []
    invalid_agent_ids: List[Dict[str, str]] = []
    duplicate_agent_ids: List[str] = []

    workforce_path = root / "WORKFORCE.md"
    if _is_safe_file_under_root(root, "WORKFORCE.md"):
        try:
            if workforce_path.stat().st_size > MAX_WORKFORCE_BYTES:
                errors.append("WORKFORCE.md is too large to parse safely")
                workforce_text = ""
            else:
                workforce_text = workforce_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            errors.append("WORKFORCE.md is unreadable or not valid UTF-8")
            workforce_text = ""

        roster_lines = _find_active_roster_lines(workforce_text) if workforce_text else []

        if not roster_lines:
            errors.append("No active roster entries found in WORKFORCE.md")
        else:
            seen: Dict[str, int] = {}
            for line in roster_lines:
                match = ROSTER_LINE_RE.match(line)
                if not match:
                    errors.append(f"Unparseable roster line: {_safe_line_preview(line)}")
                    continue

                team_name, agent_id = match.group(1), match.group(2)
                roster_entries.append({"team": team_name, "agent_id": agent_id})

                if not UUID_LIKE_RE.match(agent_id):
                    invalid_agent_ids.append({"team": team_name, "agent_id": agent_id})

                seen[agent_id] = seen.get(agent_id, 0) + 1

            duplicate_agent_ids = sorted([agent_id for agent_id, count in seen.items() if count > 1])
    else:
        errors.append("WORKFORCE.md missing; roster checks skipped")

    ok = not missing_files and not invalid_agent_ids and not duplicate_agent_ids and not errors

    return AuditResult(
        ok=ok,
        checked_root=str(root),
        required_files=REQUIRED_FILES,
        missing_files=missing_files,
        roster_entries=roster_entries,
        invalid_agent_ids=invalid_agent_ids,
        duplicate_agent_ids=duplicate_agent_ids,
        errors=errors,
    )



def format_text(result: AuditResult) -> str:
    if result.ok:
        return f"OK workforce audit passed ({len(result.roster_entries)} roster entries)"

    lines = ["FAIL workforce audit"]

    if result.missing_files:
        lines.append("missing files: " + ", ".join(result.missing_files))

    if result.invalid_agent_ids:
        formatted = ", ".join(
            f"{item['team']}={item['agent_id']}" for item in result.invalid_agent_ids
        )
        lines.append("invalid agent ids: " + formatted)

    if result.duplicate_agent_ids:
        lines.append("duplicate agent ids: " + ", ".join(result.duplicate_agent_ids))

    for err in result.errors:
        lines.append("error: " + err)

    return "\n".join(lines)
