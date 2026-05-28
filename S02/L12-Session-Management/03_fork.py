"""
Demo 3 of 3 for L2.12 — fork_session.

Branch off a copy of a prior session. The original stays unchanged.
Run two divergent explorations in parallel without losing the baseline.

USAGE
-----
Three runs:

    python 03_fork.py baseline
    # → writes session_id to .baseline_session_id
    python 03_fork.py fork_a
    python 03_fork.py fork_b

Expected behavior:
  - "baseline" creates the shared analysis (e.g., reads codebase)
  - "fork_a" branches off and asks question A
  - "fork_b" branches off the SAME baseline and asks question B
  - The baseline session is untouched and still resumable separately
"""

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
)

load_dotenv()

BASELINE_FILE = Path(".baseline_session_id")
SYSTEM_PROMPT = "You are a refactoring strategist. Keep answers tight — 3 sentences max."


async def baseline_query() -> None:
    """Establish the shared analysis. Both forks will inherit this context."""
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob", "Grep"],
        system_prompt=SYSTEM_PROMPT,
    )
    captured: str | None = None
    print("--- Baseline query (shared analysis) ---\n")
    async for msg in query(
        prompt=(
            "Look at the auth-related files in this directory. "
            "Briefly note the current authentication approach."
        ),
        options=options,
    ):
        _print(msg)
        if isinstance(msg, ResultMessage):
            captured = msg.session_id
    if captured:
        BASELINE_FILE.write_text(captured)
        print(f"\n[baseline session_id: {captured}]")


async def fork_query(branch_name: str, prompt: str) -> None:
    """Fork the baseline. New session, same prior context, divergent path."""
    if not BASELINE_FILE.exists():
        sys.exit("Run 'python 03_fork.py baseline' first.")
    baseline_id = BASELINE_FILE.read_text().strip()

    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Grep"],
        resume=baseline_id,
        fork_session=True,            # ← the key option
    )
    print(f"--- Fork '{branch_name}' (from baseline {baseline_id}) ---\n")
    async for msg in query(prompt=prompt, options=options):
        _print(msg)


def _print(msg) -> None:
    if isinstance(msg, AssistantMessage):
        for block in msg.content:
            if isinstance(block, TextBlock):
                print(block.text)
    elif isinstance(msg, ResultMessage):
        print(f"\n[done — session_id: {msg.session_id}  turns: {msg.num_turns}]")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "baseline"
    if mode == "baseline":
        asyncio.run(baseline_query())
    elif mode == "fork_a":
        asyncio.run(fork_query(
            branch_name="approach_A_JWT",
            prompt="Sketch a refactor that moves this auth to JWT-based tokens. "
                   "Cover the three biggest changes.",
        ))
    elif mode == "fork_b":
        asyncio.run(fork_query(
            branch_name="approach_B_cookies",
            prompt="Sketch a refactor that moves this auth to server-side session cookies. "
                   "Cover the three biggest changes.",
        ))
    else:
        sys.exit("usage: python 03_fork.py [baseline|fork_a|fork_b]")
