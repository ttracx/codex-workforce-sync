#!/usr/bin/env python3
"""CLI audit for workspace governance files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from workforce_audit_lib import format_text, run_audit


def _dir_path(value: str) -> Path:
    candidate = Path(value).expanduser()
    if not candidate.exists():
        raise argparse.ArgumentTypeError(f"--root does not exist: {value}")
    if not candidate.is_dir():
        raise argparse.ArgumentTypeError(f"--root is not a directory: {value}")
    return candidate


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit workspace governance files")
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--root",
        type=_dir_path,
        default=_dir_path("."),
        help="Workspace root to audit (default: current directory)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_audit(args.root)

    if args.format == "json":
        print(json.dumps(result.to_dict(), separators=(",", ":"), sort_keys=True))
    else:
        print(format_text(result))

    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
