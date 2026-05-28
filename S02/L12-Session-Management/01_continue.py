"""
Demo 1 of 3 for L2.12 — continue_conversation.

Pick up the most recent session in this directory. No session-ID tracking
needed — the SDK finds the latest session on disk automatically.

USAGE
-----
Run twice, back-to-back:

    python 01_continue.py first
    python 01_continue.py followup

Expected behavior:
  - "first" creates a fresh session, prints a session_id at the end
  - "followup" picks up that same session via continue_conversation=True
    and asks a question that depends on prior context
"""

import asyncio
import sys

from dotenv import load_dotenv
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
)

load_dotenv()

SYSTEM_PROMPT = (
    "You are a codebase analyst. Be concise — one short paragraph per response."
)


async def first_query() -> None:
    """Fresh session. SDK persists it to disk automatically."""
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob"],
        system_prompt=SYSTEM_PROMPT,
    )
    print("--- First query (fresh session) ---\n")
    async for msg in query(
        prompt=(
            "List the Python files in the current directory and summarize "
            "what each one is for in one line."
        ),
        options=options,
    ):
        _print(msg)


async def followup_query() -> None:
    """Pick up the most recent session in this directory."""
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob"],
        continue_conversation=True,   # ← the key option
    )
    print("--- Follow-up query (continuing the most recent session) ---\n")
    async for msg in query(
        prompt="Of those files, which one looks most important and why?",
        options=options,
    ):
        _print(msg)


def _print(msg) -> None:
    if isinstance(msg, AssistantMessage):
        for block in msg.content:
            if isinstance(block, TextBlock):
                print(block.text)
    elif isinstance(msg, ResultMessage):
        print(f"\n[done — session_id: {msg.session_id}  turns: {msg.num_turns}]")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "first"
    if mode == "first":
        asyncio.run(first_query())
    elif mode == "followup":
        asyncio.run(followup_query())
    else:
        sys.exit("usage: python 01_continue.py [first|followup]")
