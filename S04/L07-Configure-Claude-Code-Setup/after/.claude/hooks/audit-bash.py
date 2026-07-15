#!/usr/bin/env python3
"""PreToolUse hook for Bash calls — audit + deny complex patterns.

Two jobs:
  1) Audit — log every Bash command Claude Code proposes to run.
  2) Deny — reject destructive patterns the static permissions list
     CAN'T easily express: piped downloads, permissive chmod, dd/mkfs,
     raw disk redirects, sudo. Simple globs like `Bash(rm -rf *)` stay
     in settings.json permissions.deny where they belong.

Root Cause Bias, Pattern 4: critical business rules go in hooks
(deterministic), not in prompts (probabilistic). This is that pattern
in code — a rule Claude cannot talk itself out of, because the decision
is made by Python before the tool call reaches the shell.

Log format is JSON lines at .claude/logs/bash-audit.log. Each line has:
  ts:       ISO-8601 UTC timestamp
  decision: "deny" (hook blocked) or "pass" (hook has no opinion —
            settings.json permissions still gets its say)
  reason:   human-readable block reason, empty when pass
  command:  the Bash command Claude tried to run
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path(__file__).parent.parent / "logs" / "bash-audit.log"

# Patterns that must be blocked. Each entry: (regex, reason shown to Claude).
# These are all patterns the static permissions.deny glob syntax handles
# poorly — substring matches, pipes, alternatives, numeric constraints.
BLOCKED_PATTERNS: list[tuple[str, str]] = [
    (r"\bsudo\b",                       "sudo is not permitted in this project"),
    (r"\bcurl\b.+\|\s*(bash|sh)\b",     "download-and-execute pipeline is not permitted"),
    (r"\bwget\b.+\|\s*(bash|sh)\b",     "download-and-execute pipeline is not permitted"),
    (r"\bchmod\b\s+[0-7]?[67][67]\b",   "world-writable chmod is not permitted"),
    (r"\bdd\b\s+if=",                   "raw disk write via dd is not permitted"),
    (r"\bmkfs(\.[a-z0-9]+)?\b",         "filesystem creation is not permitted"),
    (r">\s*/dev/(sd|nvme|hd)",          "raw disk redirect is not permitted"),
]


def load_event() -> dict:
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}


def log_call(payload: dict, decision: str, reason: str = "") -> None:
    """Append one JSON-lines record per Bash call to the audit log."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    command = payload.get("tool_input", {}).get("command", "")
    record = json.dumps({
        "ts": ts,
        "decision": decision,
        "reason": reason,
        "command": command,
    })
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(record + "\n")


def check(command: str) -> tuple[str, str]:
    """Return ('deny', reason) if any blocked pattern matches, else ('pass', '')."""
    for pattern, reason in BLOCKED_PATTERNS:
        if re.search(pattern, command):
            return "deny", reason
    return "pass", ""


def main() -> int:
    payload = load_event()
    command = payload.get("tool_input", {}).get("command", "")

    # No command payload — defer to normal permission flow.
    if not command:
        return 0

    decision, reason = check(command)
    log_call(payload, decision, reason)

    if decision == "deny":
        json.dump({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Hook rejected: {reason}",
            }
        }, sys.stdout)
        return 0

    # No hook decision — the static permissions list (settings.json) still
    # gets its say. Exit 0 with no stdout means "hook has no opinion".
    return 0


if __name__ == "__main__":
    sys.exit(main())
