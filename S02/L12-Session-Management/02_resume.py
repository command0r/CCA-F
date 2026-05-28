"""
Demo 2 of 3 for L2.12 — resume by session_id.

Capture the session_id from a ResultMessage, then explicitly pass it back
to ClaudeAgentOptions(resume=...) later. This is the targeted form — pick
up THIS specific session, not whichever was most recent.

USAGE
-----
Run twice, back-to-back. The second run uses the session_id printed by
the first run:

    python 02_resume.py first
    # → look for "captured session_id: SOMETHING" in the output, then:
    python 02_resume.py resume SOMETHING

Expected behavior:
  - "first" creates a fresh session, writes the session_id to a file
    (.last_session_id) for convenience
  - "resume SOMETHING" picks up that specific session and asks a follow-up
  - If you omit the ID on the resume call, it auto-reads from the file
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

SESSION_FILE = Path(".last_session_id")
SYSTEM_PROMPT = "You are a codebase analyst. Keep answers under 4 sentences."


async def first_query() -> str | None:
    """Fresh session — capture the ID for the follow-up call."""
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob"],
        system_prompt=SYSTEM_PROMPT,
    )
    captured: str | None = None
    print("--- First query (fresh session) ---\n")
    async for msg in query(
        prompt="Identify the entry-point file in this directory.",
        options=options,
    ):
        _print(msg)
        if isinstance(msg, ResultMessage):
            captured = msg.session_id
    if captured:
        SESSION_FILE.write_text(captured)
        print(f"\n[captured session_id: {captured}]")
        print(f"[written to: {SESSION_FILE.resolve()}]")
    return captured


async def resume_query(session_id: str) -> None:
    """Pick up a specific prior session by ID."""
    options = ClaudeAgentOptions(
        allowed_tools=["Read"],
        resume=session_id,            # ← the key option
    )
    print(f"--- Resume query (session_id={session_id}) ---\n")
    async for msg in query(
        prompt="What did we conclude about the entry point — and what's the next thing worth investigating?",
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
    elif mode == "resume":
        if len(sys.argv) > 2:
            sid = sys.argv[2]
        elif SESSION_FILE.exists():
            sid = SESSION_FILE.read_text().strip()
            print(f"[reading session_id from {SESSION_FILE}]")
        else:
            sys.exit("usage: python 02_resume.py resume <session_id>")
        asyncio.run(resume_query(sid))
    else:
        sys.exit("usage: python 02_resume.py [first|resume <session_id>]")
