"""
S02-L07 demo: Coordinator + 3 research subagents, parallel spawn.

What this proves on screen:
  - A real Claude Agent SDK coordinator decomposes a research task
  - It emits three Agent tool calls in ONE assistant turn (parallel spawn)
  - Three subagent instances run concurrently, each with isolated context
  - Each subagent uses the real built-in Read tool to load one benchmark file
  - The coordinator aggregates the three JSON outputs into one comparison

Usage:
    python coordinator_demo.py
"""

import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AgentDefinition,
    AssistantMessage,
    UserMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock,
)

load_dotenv()

PROJECT_DIR = Path(__file__).parent

# ──────────────────────────────────────────────────────────────────────
# Subagent definition: one "researcher" type, three instances at runtime
# ──────────────────────────────────────────────────────────────────────

RESEARCHER_PROMPT = """You are a vector-database benchmark research subagent.

CONTEXT:
You will be given the name of a vector database (one of: pgvector,
qdrant, weaviate). A benchmark report for it lives at:

    benchmarks/<database>_benchmark.md

(All lowercase. The path is relative to the current working directory.)

GOAL:
1. Use the Read tool to load that benchmark file.
2. Extract these fields if present: source URL, p50 latency,
   p99 latency, recall@10, storage cost, test scale.
3. Return ONLY a single-line JSON object — no prose, no markdown.

OUTPUT FORMAT (one line):
{"database": "<name>", "p50_ms": <number>, "p99_ms": <number>,
 "recall_at_10": <number>, "storage_cost": "<string>",
 "scale": "<string>", "source": "<url>"}
"""

researcher = AgentDefinition(
    description=(
        "Reads ONE vector-database benchmark file from the local "
        "benchmarks/ folder and returns extracted metrics as JSON. "
        "Use this once per database you need to research."
    ),
    prompt=RESEARCHER_PROMPT,
    tools=["Read"],                     # least privilege: just Read
    model="sonnet",
)

# ──────────────────────────────────────────────────────────────────────
# Coordinator config
# ──────────────────────────────────────────────────────────────────────

COORDINATOR_SYSTEM_PROMPT = """You coordinate vector-database research.

You will receive a request to compare three databases. Your job:

1. Spawn ONE researcher subagent per database, ALL IN PARALLEL —
   meaning all three Agent tool calls must appear in the SAME
   assistant turn. Do NOT spawn them sequentially across turns.

2. When all three subagents return their JSON, aggregate the
   outputs into a single side-by-side comparison table for the user
   covering: p50 latency, p99 latency, recall@10, storage cost, source.

3. End with one short recommendation sentence noting which database
   looks strongest for latency-sensitive RAG at the tested scale.
"""

options = ClaudeAgentOptions(
    system_prompt=COORDINATOR_SYSTEM_PROMPT,
    allowed_tools=["Agent", "Read"],    # "Agent" is the spawning primitive
    agents={"researcher": researcher},
    max_turns=10,
    model="sonnet",
    cwd=str(PROJECT_DIR),
)

USER_PROMPT = (
    "Compare the RAG benchmark numbers for pgvector, qdrant, and "
    "weaviate at 10M-vector scale. Spawn one researcher subagent per "
    "database — all three in parallel — then give me a side-by-side "
    "comparison and a one-sentence recommendation."
)

# ──────────────────────────────────────────────────────────────────────
# Pretty-printer: highlights the parallel spawn moment specifically
# ──────────────────────────────────────────────────────────────────────

def print_message(msg) -> None:
    if isinstance(msg, AssistantMessage):
        agent_calls = [
            b for b in msg.content
            if isinstance(b, ToolUseBlock) and b.name == "Agent"
        ]
        if len(agent_calls) > 1:
            print(f"\n[PARALLEL SPAWN] coordinator emitted "
                  f"{len(agent_calls)} Agent calls in ONE turn")
        for block in msg.content:
            if isinstance(block, TextBlock):
                text = block.text.strip()
                if text:
                    print(f"\n[COORDINATOR] {text}")
            elif isinstance(block, ToolUseBlock):
                if block.name == "Agent":
                    sub = block.input.get("subagent_type", "?")
                    prm = (block.input.get("prompt") or "").strip().replace("\n", " ")
                    print(f"  -> Agent(subagent_type='{sub}'): {prm[:90]}...")
                else:
                    args = json.dumps(block.input)[:80]
                    print(f"  -> {block.name}({args})")
    elif isinstance(msg, UserMessage):
        content = msg.content
        if isinstance(content, list):
            for block in content:
                if isinstance(block, ToolResultBlock):
                    raw = block.content
                    if isinstance(raw, list):
                        text = "".join(
                            b.get("text", "") for b in raw if isinstance(b, dict)
                        )
                    else:
                        text = str(raw)
                    print(f"\n[SUBAGENT RESULT] {text.strip()[:400]}")
    elif isinstance(msg, ResultMessage):
        cost = getattr(msg, "total_cost_usd", None)
        turns = getattr(msg, "num_turns", None)
        bits = []
        if turns is not None:
            bits.append(f"turns={turns}")
        if cost is not None:
            bits.append(f"cost=${cost:.4f}")
        print(f"\n[DONE] {'  '.join(bits)}")


async def main() -> None:
    print(f"[STARTING] cwd={PROJECT_DIR}\n")
    async for message in query(prompt=USER_PROMPT, options=options):
        print_message(message)


if __name__ == "__main__":
    asyncio.run(main())
