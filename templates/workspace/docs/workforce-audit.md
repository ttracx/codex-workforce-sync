# Workforce Audit Runbook

## Purpose
Run a fast integrity check on workspace governance files and runtime roster formatting before or after orchestration changes.

## Commands
- Default text output:
  - `scripts/run-workforce-audit.sh`
- JSON output:
  - `scripts/run-workforce-audit.sh --format json`
- Explicit root (if not running from workspace root):
  - `python3 scripts/workforce_audit.py --root /home/ttracx --format text`

## Exit Codes
- `0`: Audit passed (all required files present, roster parsed, IDs valid, no duplicate IDs).
- `1`: Audit failed (one or more missing files, roster/ID issues, or parse/read errors).
- `2`: CLI usage error (invalid arguments from `argparse`).

## Failure Interpretation
- `missing files:` Required governance files are missing, unreadable, symlinked, or not regular files.
- `invalid agent ids:` One or more roster IDs are not UUID-like values.
- `duplicate agent ids:` Same agent ID appears more than once in active roster.
- `error: No active roster entries found in WORKFORCE.md`: Active roster section missing, empty, or malformed.
- `error: Unparseable roster line: ...`: A roster line does not match expected `- team-name: \`uuid\`` format.
- `error: WORKFORCE.md is unreadable or not valid UTF-8` or too large: File integrity/readability issue blocked parsing.

## Quick Remediation
1. Restore missing governance files listed in failure output.
2. Fix `WORKFORCE.md` active roster lines to `- team-name: \`uuid\``.
3. Ensure each team has a unique UUID-like ID and no duplicates.
4. Re-run `scripts/run-workforce-audit.sh` until exit code is `0`.
5. If failures persist after file fixes, escalate to `team-ops` (tooling/readability issues) or `team-security` (unexpected file integrity concerns).
