# S02-L12 — Session Management Demos

Three small scripts that demonstrate the SDK primitives covered in
Lecture 2.12: **continue**, **resume**, and **fork**. Real Anthropic
Claude Agent SDK. All field names and option shapes verified against
the official docs at `https://docs.claude.com/en/api/agent-sdk/sessions`.

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
$EDITOR .env
```

If you don't already have the Claude Code CLI: `npm install -g @anthropic-ai/claude-code`.

## The three demos

### 1. `01_continue.py` — pick up the most recent session

The simplest pattern. No ID tracking. `continue_conversation=True` finds
the latest session in the current directory and resumes it.

```bash
python 01_continue.py first
python 01_continue.py followup
```

You should see the second call's response reference whatever the first
call discovered — same session, no manual ID handling.

### 2. `02_resume.py` — pick up a specific session by ID

Capture `msg.session_id` from a `ResultMessage`, write it down, pass it
back as `resume=session_id` later. Targeted form — pick up THIS session,
not whichever was most recent.

```bash
python 02_resume.py first
# The script writes the session_id to .last_session_id
python 02_resume.py resume
# (or pass the ID explicitly: python 02_resume.py resume sess_xyz123)
```

### 3. `03_fork.py` — branch off without losing the baseline

Combine `resume=baseline_id` with `fork_session=True` to create a NEW
session that starts with a copy of the baseline's history. The baseline
is untouched. Run two divergent explorations in parallel.

```bash
python 03_fork.py baseline
python 03_fork.py fork_a       # JWT refactor
python 03_fork.py fork_b       # session-cookie refactor
```

The baseline session is still resumable separately — fork_a and fork_b
don't disturb it.

## What's REAL vs what's PERSISTED

| Thing                                     | Where it lives                          |
|-------------------------------------------|-----------------------------------------|
| Conversation history (sessions)           | Disk, written by the SDK automatically  |
| Session IDs                               | In `ResultMessage.session_id`           |
| Helper files for these demos              | `.last_session_id`, `.baseline_session_id` (gitignored) |
| File changes the agent made               | Your filesystem — NOT in the session    |

Sessions persist the *conversation*, not the filesystem. To snapshot and
revert file changes, see the [file checkpointing docs](https://docs.claude.com/en/api/agent-sdk/checkpointing).

## When to resume vs start fresh

This is the exam-tested decision rule (Task Statement 1.7):

| Resume when…                                 | Start fresh (with injected summary) when… |
|----------------------------------------------|-------------------------------------------|
| Files the agent read haven't changed         | Files have been modified since            |
| Minutes / hours have passed, same context    | Days have passed, codebase has moved      |
| Prior tool results still describe reality    | Prior tool results would now be stale     |

Stale tool results in a resumed session are worse than no context at all
— the agent reasons from outdated data and confidently misleads you.

## Reference docs

- **Sessions overview:** https://docs.claude.com/en/api/agent-sdk/sessions
- **Persist sessions to external storage (production):** https://docs.claude.com/en/api/agent-sdk/session-store
- **File checkpointing:** https://docs.claude.com/en/api/agent-sdk/checkpointing
