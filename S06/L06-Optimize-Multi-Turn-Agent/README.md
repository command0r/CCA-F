# Optimize a Multi-Turn Agent for Cost and Context

A customer support agent run two ways — baseline (no caching) and optimized
(`cache_control` on system prompt + tools) — with per-turn token usage and cost
side by side.

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

- Baseline: every turn pays full input price; `cache_read_input_tokens` is 0.
- Cached: turn 1 pays the 1.25x cache write premium; turns 2-5 pay the 0.1x cache
  read price (90% discount). Cache hit rate climbs to ~80% across the run.
- Total cost reduction on a 5-turn demo is typically 40-60%. With more turns,
  savings approach the documented Notion case (~90%).

## Notes

- Sonnet 4.6 pricing: $3 input / $15 output / $0.30 cache read / $3.75 cache write
  (5-min) per MTok. Hard-coded in `optimize_agent.py` for transparency.
- `cache_control` goes on the LAST stable block — last tool definition and the
  system prompt block (lecture 6.40).

## References

- docs.claude.com/en/docs/build-with-claude/prompt-caching
- docs.claude.com/en/about-claude/pricing
