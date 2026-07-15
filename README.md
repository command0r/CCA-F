# CCA-F — Demo Code

Working code demos for the Udemy course **[Claude Certified Architect — Foundations (CCA-F): The Teaching Course](https://www.udemy.com/course/claude-certified-architect-foundations-cca-f/)**.

Each folder maps one-to-one to a specific lecture in the course. Every demo runs end-to-end against real Anthropic APIs, with a small mock fallback where API cost or determinism matters.

---

## Repository layout

```
CCA-F/
├── S02/  # Domain 1 — Agentic Architecture & Orchestration
│   ├── L04-Watch-The-Loop-Break/            # Broken agent loop → structured error fix
│   ├── L07-Coordinator-Subagent-Demo/       # Multi-agent coordinator + subagents
│   └── L12-Session-Management/              # Agent SDK continue / resume / fork
├── S03/  # Domain 2 — Tool Design & MCP Integration
│   └── L07-MCP-Server-Demo/                 # MCP server + agent that consumes it
├── S04/  # Domain 3 — Claude Code Configuration & Workflows
│   └── L07-Configure-Claude-Code-Setup/     # Before/after Claude Code project setup
├── S05/  # Domain 4 — Prompt Engineering & Structured Output
│   └── L08-Structured-Extractor-Scenario-6/ # tool_use + strict mode + validation-retry + Batches
└── S06/  # Domain 5 — Context Management & Reliability
    └── L06-Optimize-Multi-Turn-Agent/       # Prompt caching cost comparison
```

Each demo folder contains:

- `README.md` — what the demo teaches, how to run it, what to look for
- `requirements.txt` — pinned Python dependencies for the demo
- `.env.example` — required environment variables
- `*.py` — the runnable Python source
- Any supporting data files (contracts, benchmarks, etc.)

---

## Quick start

**Prerequisites**

- Python 3.10 or newer
- An [Anthropic API key](https://console.anthropic.com/settings/keys)
- For the Claude Code demo (S04/L07) and MCP demo (S03/L07): the [Claude Code CLI](https://docs.claude.com/en/docs/claude-code/setup) installed via `npm install -g @anthropic-ai/claude-code`

**Setup for any demo**

```bash
cd S0X/L0X-Demo-Name/
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
python <demo-file>.py
```

Each demo's `README.md` has the specific run command and what to look for in the output.

---

## Demos at a glance

| Section | Demo | Teaches | Key concept |
|---|---|---|---|
| Domain 1 | `S02/L04` — Watch the Loop Break | Structured tool errors vs iteration caps | Root Cause Bias Pattern 2 |
| Domain 1 | `S02/L07` — Coordinator + Subagents | Multi-agent orchestration, task decomposition | Root Cause Bias Pattern 3 |
| Domain 1 | `S02/L12` — Session Management | Agent SDK continue/resume/fork primitives | Stateful vs stateless agents |
| Domain 2 | `S03/L07` — MCP Server + Agent | Author an MCP server, consume its tools from an agent | Tool integration architecture |
| Domain 3 | `S04/L07` — Claude Code Setup | `.claude/settings.json`, CLAUDE.md hierarchy, hooks, allowed_tools scoping | Deterministic capability control |
| Domain 4 | `S05/L08` — Structured Extractor | `tool_use` with `strict: true`, forced `tool_choice`, validation-retry loop, Batches API | Guaranteed-schema output |
| Domain 5 | `S06/L06` — Prompt Caching | Cache breakpoints, TTL choice, cache-hit-rate measurement, cost comparison | Cost audit — first lever |

---

## The course's central meta-skill

Every CCA-F exam question is essentially "something is broken — what do you do?" The right answer fixes the **cause**, not the symptom. Four canonical patterns run through both the exam and these demos:

| Symptom | Wrong fix (the exam distractor) | Right fix (root cause) |
|---|---|---|
| Tool routing unreliable | Add a classifier layer | Fix tool descriptions |
| Agent loops forever | Cap iterations at N | Fix structured error responses |
| Subagent output wrong | Add shared memory between subagents | Fix coordinator decomposition |
| Critical business rule not enforced | Add it to the system prompt | Use a hook |

Every demo in this repo teaches one of these patterns.

---

## Helpful resources

**Official Anthropic documentation** (start here for any technical claim)

- [Anthropic documentation home](https://docs.claude.com/en/home) — canonical reference for API, models, and pricing
- [Claude API — Messages endpoint](https://docs.claude.com/en/api/messages) — the core API surface these demos exercise
- [Tool use guide](https://docs.claude.com/en/docs/agents-and-tools/tool-use/overview) — schemas, strict mode, forced tool_choice
- [Prompt caching](https://docs.claude.com/en/docs/build-with-claude/prompt-caching) — breakpoints, TTL, cost math
- [Extended thinking](https://docs.claude.com/en/docs/build-with-claude/extended-thinking) — budget, multi-turn preservation on newer models
- [Message Batches API](https://docs.claude.com/en/docs/build-with-claude/batch-processing) — 50% discount async workload
- [Model overview + pricing](https://docs.claude.com/en/docs/about-claude/pricing) — check before you trust any hardcoded price in demo code

**Claude Code**

- [Claude Code setup and configuration](https://docs.claude.com/en/docs/claude-code/setup)
- [Slash commands](https://docs.claude.com/en/docs/claude-code/slash-commands) — custom `.claude/commands/`
- [Hooks](https://docs.claude.com/en/docs/claude-code/hooks) — the deterministic enforcement primitive
- [CLAUDE.md hierarchy](https://docs.claude.com/en/docs/claude-code/memory) — user/project/subdirectory scoping

**Claude Agent SDK**

- [Agent SDK overview](https://docs.claude.com/en/api/agent-sdk/overview)
- [Session management](https://docs.claude.com/en/api/agent-sdk/session-management) — continue/resume/fork
- [Custom tools](https://docs.claude.com/en/api/agent-sdk/custom-tools)
- [MCP integration](https://docs.claude.com/en/api/agent-sdk/mcp)

**Model Context Protocol (MCP)**

- [MCP specification](https://modelcontextprotocol.io/introduction)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Reference server implementations](https://github.com/modelcontextprotocol/servers) — read real MCP server code

**Community study references**

- [paullarionov/claude-certified-architect](https://github.com/paullarionov/claude-certified-architect) — the highest-quality open-source CCA-F study guide. Deep technical detail across all five domains with worked exam questions. Recommended as a companion to this course.

**Certification**

- [Register for the CCA-F exam](https://anthropic.skilljar.com/claude-certified-architect-foundations-access-request) — $99 USD (free for the first 5,000 Anthropic Partner Network employees)
- [Official CCA-F exam guide v0.1 (PDF)](https://www.anthropic.com/) — request via the registration page above; this PDF is the authoritative reference for domains, task statements, sample questions, in-scope and out-of-scope topics

**Books and long-form reference**

- [Anthropic's engineering blog](https://www.anthropic.com/engineering) — architectural deep-dives on Claude systems
- [Building effective agents (Anthropic)](https://www.anthropic.com/research/building-effective-agents) — the paper that shaped modern agentic design patterns

---

## Model IDs used in these demos

All demos default to:

- `claude-sonnet-4-6` for standard workloads
- `claude-opus-4-6` where reasoning depth matters
- `claude-haiku-4-5-20251001` for cost-sensitive high-volume paths

If Anthropic ships new model IDs, update the `MODEL` constant near the top of each demo file (or set `ANTHROPIC_MODEL` in your `.env`).

---

## Contributing / reporting issues

If you find a bug, an outdated pattern, or a demo that no longer runs against the current Anthropic API:

1. Open an issue on this repo describing the demo, the command you ran, and the observed vs expected output
2. Or DM in the Udemy Q&A — the course author reads every question

Pull requests welcome for fixes and clarifications; behavioral changes to demos should go through issue discussion first so we don't drift from what the course lectures teach.

---

## License

Course material and demo code © Alex Kaziuka, released under the MIT License for educational use. Feel free to adapt in your own production work.

---

*Companion to the Udemy course [Claude Certified Architect — Foundations: The Teaching Course](https://www.udemy.com/course/claude-certified-architect-foundations-cca-f/).*
