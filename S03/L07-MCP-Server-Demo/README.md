# MCP server demo

An in-process MCP server with one tool. The tool counts files in any public GitHub repository by extension. The agent has access to ONLY this tool — it cannot read your local files.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env                # paste your ANTHROPIC_API_KEY
```

Optional: add `GITHUB_TOKEN=ghp_...` to `.env` to raise GitHub's rate limit from 60/hr to 5000/hr.

## Run

```bash
python agent.py                       # default: command0r/eShop
python agent.py microsoft/typescript  # any public repo
python agent.py facebook/react        # any public repo
```

## What to look for

```
[TOOL CALL] mcp__project_stats__count_files_by_extension({"owner": "command0r", "repo": "eShop"})

[TOOL RESULT] {"total_files": 1234, "top_10_extensions": {".cs": 423, ".cshtml": 187, ...}}

[CLAUDE] eShop is primarily a C# project — 423 .cs files dominate...
```

## References

- [Custom tools — Agent SDK](https://docs.claude.com/en/api/agent-sdk/custom-tools)
- [Agent SDK MCP](https://docs.claude.com/en/api/agent-sdk/mcp)
- [modelcontextprotocol.io](https://modelcontextprotocol.io)
