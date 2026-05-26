# S02-L07 — Coordinator + 3 Subagents (Parallel Spawn)

Demo accompanying Lecture 2.7 of the CCA-F course. Real Anthropic Claude
Agent SDK, real Agent tool, real parallel subagent spawning. The three
benchmark files in `benchmarks/` are local test fixtures the subagents
read with the built-in `Read` tool — nothing is mocked, just stubbed
with deterministic local data so the demo is reproducible.

## Prerequisites

- Python 3.10+
- Node.js 18+ (the Agent SDK wraps the Claude Code CLI under the hood)
- Anthropic API key

## Setup

```powershell
# Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
notepad .env    # paste your ANTHROPIC_API_KEY=sk-ant-...
```

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
$EDITOR .env    # paste your ANTHROPIC_API_KEY=sk-ant-...
```

If you don't already have the Claude Code CLI installed locally, install it once with `npm install -g @anthropic-ai/claude-code`.

## Run

```powershell
python coordinator_demo.py
```

## What you should see

```
[STARTING] cwd=...

[COORDINATOR] I'll spawn three research subagents in parallel to look up
              each database's benchmark.

[PARALLEL SPAWN] coordinator emitted 3 Agent calls in ONE turn
  -> Agent(subagent_type='researcher'): Research pgvector...
  -> Agent(subagent_type='researcher'): Research qdrant...
  -> Agent(subagent_type='researcher'): Research weaviate...

[SUBAGENT RESULT] {"database": "pgvector", "p50_ms": 14, ...}
[SUBAGENT RESULT] {"database": "qdrant", "p50_ms": 8, ...}
[SUBAGENT RESULT] {"database": "weaviate", "p50_ms": 11, ...}

[COORDINATOR] Comparison:
  | DB         | p50 | p99 | Recall@10 | Storage   | Source            |
  | pgvector   | 14  | 52  | 0.94      | $0.020/GB | supabase.com/...  |
  | qdrant     | 8   | 29  | 0.96      | $0.014/GB | qdrant.tech/...   |
  | weaviate   | 11  | 38  | 0.95      | $0.022/GB | weaviate.io/...   |

  Recommendation: Qdrant looks strongest for latency-sensitive RAG...

[DONE] turns=3  cost=$0.0XX
```

The `[PARALLEL SPAWN]` line is the architectural moment — three Agent
calls in one assistant turn means the subagents run concurrently. That's
the demo's payoff.

## What's REAL vs what's STUBBED

| Component                        | Real or stubbed?                               |
|----------------------------------|------------------------------------------------|
| Anthropic Claude Agent SDK       | Real (claude-agent-sdk 0.2.87+)                |
| Claude model (coordinator + subs)| Real (sonnet, live API call)                   |
| Agent tool / subagent spawning   | Real                                           |
| Subagent isolation               | Real (each gets a fresh context)               |
| Built-in `Read` tool             | Real                                           |
| `benchmarks/*.md` data files     | Local test fixtures (deterministic, not mocks) |

Nothing about the model's behavior is faked. The benchmark files are
just local data — analogous to giving the agent a sandboxed staging
database during dev instead of pointing it at production.
