"""Runs Claude with the project_stats MCP server. Pass any owner/repo as an argument."""

import asyncio
import json
import sys

from dotenv import load_dotenv
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    UserMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock,
)

from server import project_stats_server

load_dotenv()

DEFAULT_REPO = "microsoft/typescript"  # change this to analyze a different repo by default


def print_message(msg):
    if isinstance(msg, AssistantMessage):
        for block in msg.content:
            if isinstance(block, TextBlock) and block.text.strip():
                print(f"\n[CLAUDE] {block.text.strip()}")
            elif isinstance(block, ToolUseBlock):
                print(f"\n[TOOL CALL] {block.name}({json.dumps(block.input)})")
    elif isinstance(msg, UserMessage) and isinstance(msg.content, list):
        for block in msg.content:
            if isinstance(block, ToolResultBlock):
                raw = block.content
                if isinstance(raw, list):
                    text = "".join(b.get("text", "") for b in raw if isinstance(b, dict))
                else:
                    text = str(raw)
                print(f"\n[TOOL RESULT] {text[:600]}")
    elif isinstance(msg, ResultMessage):
        bits = []
        if msg.num_turns is not None:
            bits.append(f"turns={msg.num_turns}")
        if msg.total_cost_usd is not None:
            bits.append(f"cost=${msg.total_cost_usd:.4f}")
        print(f"\n[DONE] {'  '.join(bits)}")


async def main(repo_arg):
    owner, _, repo = repo_arg.partition("/")
    if not owner or not repo:
        sys.exit("usage: python agent.py <owner>/<repo>")

    print(f"--- Analyzing {owner}/{repo} ---\n")

    options = ClaudeAgentOptions(
        system_prompt=(
            "You analyze GitHub repositories using the single tool available to you. "
            "Do NOT ask for clarification — call the tool with the provided repo."
        ),
        model="sonnet",
        mcp_servers={"project_stats": project_stats_server},
        # tools=[] strips ALL built-in tools. Claude can only use the MCP tool.
        tools=[],
        allowed_tools=["mcp__project_stats__count_files_by_extension"],
        permission_mode="bypassPermissions",
        max_turns=4,
    )

    prompt = (
        f"Analyze the GitHub repo {owner}/{repo}. "
        f"From the file composition, what kind of project is it?"
    )

    async for msg in query(prompt=prompt, options=options):
        print_message(msg)


if __name__ == "__main__":
    repo_arg = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_REPO
    asyncio.run(main(repo_arg))
