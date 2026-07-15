# Optimize a Shared-Prefix Agent for Cost and Context

A customer support agent run two ways — baseline (no caching) and optimized
(`cache_control` on system prompt + tools) — with per-call token usage and cost
side by side.

Each of the five user queries is an **independent API call**, not a multi-turn
conversation. What's shared across the calls is the stable prefix (system prompt
+ tool definitions), which is exactly what `cache_control` caches. This mirrors
the common production pattern of a support agent handling many independent user
requests with the same instructions and tool set.

## Layout

```
agent_config.py     System prompt, tool definitions, five user queries
optimize_agent.py   Runs both modes, computes cost from response.usage, prints comparison
```

## Run

```bash
pip install -r requirements.txt
cp .env.example .env       # then edit .env with your real ANTHROPIC_API_KEY
python optimize_agent.py
```

## What to look for

- Baseline: every call pays full input price; `cache_read_input_tokens` is 0.
- Cached: call 1 pays the 1.25x cache write premium; calls 2-5 pay the 0.1x
  cache read price (90% discount). Cache hit rate climbs to ~80% across the run.
- Total cost reduction on a 5-call demo is typically 40-60%. With longer sessions
  or more independent calls sharing the same prefix, savings approach the
  documented Notion case (~90%).

## Notes

- Sonnet 4.6 pricing: $3 input / $15 output / $0.30 cache read / $3.75 cache write
  (5-min) per MTok. Hard-coded in `optimize_agent.py` for transparency.
- `cache_control` goes on the LAST stable block — last tool definition and the
  system prompt block (lecture 6.40).

## References

- docs.claude.com/en/docs/build-with-claude/prompt-caching
- docs.claude.com/en/about-claude/pricing
