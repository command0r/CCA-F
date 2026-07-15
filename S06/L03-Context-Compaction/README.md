# S06-L03 — Context Compaction (Claude Code's /compact under the hood)

Long conversations eat context. When you approach the model's context window
limit, you have three options:

1. **Start a fresh conversation** — loses everything (goals, decisions, open questions).
2. **Manually curate history** — tedious, error-prone.
3. **Summarize old turns, keep recent ones verbatim** — the compaction pattern.

Claude Code's `/compact` command implements option 3 as a one-command action.
This demo shows the mechanism directly, using the Anthropic API, so you can
observe real token counts before and after.

## Layout

```
compact_demo.py    Simulates a 10-turn support conversation, summarizes turns 1..8,
                   preserves turns 9..10 verbatim, and reports token counts before
                   and after. Includes a --mock mode that runs without an API key.
requirements.txt   anthropic, python-dotenv
```

## Run

```bash
pip install -r requirements.txt
cp .env.example .env       # then edit .env with your real ANTHROPIC_API_KEY
python compact_demo.py           # real API — shows actual token counts
python compact_demo.py --mock    # deterministic, no API calls needed
```

## What to look for

- Before/after token count difference. On the sample 10-turn conversation, real
  API mode typically shows a 60-70% token reduction.
- **What was preserved**: the summary retains user goals, all decisions
  (refund amount, reference number, account flag), open questions, and root
  cause identified. The last two turns stay verbatim so continued conversation
  has full recent context.
- **What was lost**: exact wording, pleasantries, tone. If you needed the
  verbatim customer language for QA review, compact was the wrong move.

## Reproducing this in Claude Code interactively

The Python demo shows the mechanism. Here's how to see it directly in Claude Code:

1. Start a Claude Code session and have a long conversation (~10+ turns of
   substantive back-and-forth on a real task).
2. Type `/context` to see your current context-window usage.
3. Type `/compact` to compress older turns into a summary.
4. Type `/context` again — you'll see the token count drop, usually by 50-80%.

`/compact` is safe to use mid-task. Recent turns stay verbatim, so Claude's
continuity on your active work is preserved.

## When to use /compact

- **Long collaborative sessions.** Anything past ~50k tokens of context on
  Sonnet, or ~30k on Haiku.
- **Approaching the context limit.** Claude Code warns you when you cross
  ~80% of the window. `/compact` is the fast fix.
- **After a phase transition.** Finished planning, now executing? Compact
  the planning turns before writing code — the plan lives in your files
  and CLAUDE.md, not just in chat.

## When NOT to use /compact

- **When you need verbatim recall.** Extraction tasks, compliance reviews,
  legal contexts where the exact prior wording matters — do not compact.
  Start a fresh session with the transcript loaded as a file instead.
- **When the "old" turns aren't old yet.** If a decision from turn 3 is
  about to become relevant on turn 15, compacting turn 3 out to a summary
  strips detail you'll need.

## Why this matters for the exam

The CCA-F exam (Domain 5, Context Management & Reliability) tests
context-window awareness. A common distractor is "increase the context
window size" for a long-session token-pressure problem — which is wrong
because Sonnet's window is already 200k. The right answer is context
management: compaction, `/context` monitoring, offloading to files.

Root Cause Bias applied to context pressure:

- **Wrong answer**: "increase the context window" (Anthropic already gave
  you 200k on Sonnet; window size isn't the constraint).
- **Right answer**: manage what you keep in context — compact old turns,
  offload state to files, use CLAUDE.md for stable rules, invoke skills
  for one-shot procedures.

## References

- docs.claude.com/en/docs/claude-code/context — /context, /compact, /clear
- docs.claude.com/en/api/messages-count-tokens — token counting endpoint
- docs.claude.com/en/docs/build-with-claude/context-windows — window sizes per model
