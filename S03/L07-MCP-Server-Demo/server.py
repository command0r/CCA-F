"""MCP server exposing count_files_by_extension — counts files in any public GitHub repo."""

import json
import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from claude_agent_sdk import tool, create_sdk_mcp_server


@tool(
    name="count_files_by_extension",
    description=(
        "Count files in a public GitHub repository, grouped by file extension. "
        "Returns the total file count and the top 10 extensions by count "
        "(e.g., {'.cs': 423, '.cshtml': 187}). Use this for a quick sense of "
        "what languages and file types make up a project."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "owner": {"type": "string", "description": "GitHub username or org (e.g., 'command0r')"},
            "repo": {"type": "string", "description": "Repository name (e.g., 'eShop')"},
            "branch": {"type": "string", "description": "Branch name. Default: 'main'."},
        },
        "required": ["owner", "repo"],
    },
)
async def count_files_by_extension(args):
    owner = args["owner"]
    repo = args["repo"]
    branch = args.get("branch") or "main"

    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    headers = {"User-Agent": "ccaf-mcp-demo", "Accept": "application/vnd.github+json"}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"

    try:
        with urlopen(Request(url, headers=headers), timeout=15) as resp:
            data = json.loads(resp.read())
    except HTTPError as e:
        return _text({
            "isError": True,
            "errorCategory": "transient" if e.code >= 500 else "validation",
            "isRetryable": e.code >= 500,
            "description": f"GitHub API returned {e.code}: {e.reason}. Tried {owner}/{repo}@{branch}.",
        })
    except URLError as e:
        return _text({
            "isError": True,
            "errorCategory": "transient",
            "isRetryable": True,
            "description": f"Network error reaching GitHub: {e.reason}",
        })

    counts = {}
    for entry in data.get("tree", []):
        if entry.get("type") != "blob":
            continue
        name = os.path.basename(entry.get("path", ""))
        ext = "." + name.rsplit(".", 1)[-1] if "." in name else "(no extension)"
        counts[ext] = counts.get(ext, 0) + 1

    top = dict(sorted(counts.items(), key=lambda kv: -kv[1])[:10])
    return _text({
        "isError": False,
        "owner": owner,
        "repo": repo,
        "branch": branch,
        "total_files": sum(counts.values()),
        "top_10_extensions": top,
        "truncated": data.get("truncated", False),
    })


def _text(payload):
    return {"content": [{"type": "text", "text": json.dumps(payload)}]}


project_stats_server = create_sdk_mcp_server(
    name="project_stats",
    version="1.0.0",
    tools=[count_files_by_extension],
)
