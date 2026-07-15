"""Run the support agent in baseline and cached modes, print cost comparison.

Usage:  python optimize_agent.py
"""

from __future__ import annotations

from anthropic import Anthropic
from dotenv import load_dotenv

from agent_config import (
    USER_QUERIES,
    get_baseline_system,
    get_baseline_tools,
    get_cached_system,
    get_cached_tools,
)

load_dotenv()

MODEL = "claude-sonnet-4-6"
MAX_OUTPUT_TOKENS = 1024

# Sonnet 4.6 pricing per million tokens (verified June 2026, docs.claude.com/about-claude/pricing)
INPUT_PRICE_PER_TOKEN = 3.00 / 1_000_000           # $3 / MTok
OUTPUT_PRICE_PER_TOKEN = 15.00 / 1_000_000         # $15 / MTok
CACHE_READ_PRICE_PER_TOKEN = 0.30 / 1_000_000      # 0.1x base input
CACHE_WRITE_5MIN_PRICE_PER_TOKEN = 3.75 / 1_000_000  # 1.25x base input

client = Anthropic()


def compute_cost(usage) -> float:
    """Compute total USD cost from a Messages API usage object."""
    cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
    cache_write = getattr(usage, "cache_creation_input_tokens", 0) or 0
    return (
        usage.input_tokens * INPUT_PRICE_PER_TOKEN
        + usage.output_tokens * OUTPUT_PRICE_PER_TOKEN
        + cache_read * CACHE_READ_PRICE_PER_TOKEN
        + cache_write * CACHE_WRITE_5MIN_PRICE_PER_TOKEN
    )


def run(mode: str) -> list[dict]:
    """Execute the five user queries in the specified mode. Returns per-call metrics.

    Each query is an INDEPENDENT API call sharing only the system prompt + tools
    as a cacheable prefix. Not a multi-turn conversation. This mirrors the common
    production pattern where a support agent processes many independent user
    requests, all reusing the same stable instructions and tool set.
    """
    tools = get_cached_tools() if mode == "cached" else get_baseline_tools()
    system = get_cached_system() if mode == "cached" else get_baseline_system()

    results = []
    for i, query in enumerate(USER_QUERIES, 1):
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_OUTPUT_TOKENS,
            tools=tools,
            system=system,
            messages=[{"role": "user", "content": query}],
        )
        usage = response.usage
        results.append({
            "turn": i,
            "input": usage.input_tokens,
            "cache_write": getattr(usage, "cache_creation_input_tokens", 0) or 0,
            "cache_read": getattr(usage, "cache_read_input_tokens", 0) or 0,
            "output": usage.output_tokens,
            "cost": compute_cost(usage),
        })
    return results


def print_results(mode: str, results: list[dict]) -> float:
    """Pretty-print per-call metrics. Returns total cost."""
    print(f"\n=== {mode.upper()} ===\n")
    print(f"  {'Call':<6}{'Input':>8}{'CacheWr':>10}{'CacheRd':>10}{'Output':>8}{'Cost':>12}")
    print(f"  {'-'*6}{'-'*8:>8}{'-'*10:>10}{'-'*10:>10}{'-'*8:>8}{'-'*12:>12}")
    total = 0.0
    total_cache_read = 0
    total_uncached_input = 0
    for r in results:
        print(
            f"  {r['turn']:<6}{r['input']:>8}{r['cache_write']:>10}"
            f"{r['cache_read']:>10}{r['output']:>8}{'$'+format(r['cost'], '.4f'):>12}"
        )
        total += r["cost"]
        total_cache_read += r["cache_read"]
        total_uncached_input += r["input"]

    denom = total_cache_read + total_uncached_input
    hit_rate_pct = (total_cache_read / denom * 100) if denom > 0 else 0.0

    print(f"\n  Total cost:     ${total:.4f}")
    print(f"  Cache hit rate: {hit_rate_pct:.1f}%")
    return total


def main():
    print(f"Running 5-query support agent on {MODEL}")
    print("Pricing: $3 input / $15 output / $0.30 cache read / $3.75 cache write (5-min) per MTok\n")

    print("Phase 1: BASELINE (no cache_control)...")
    baseline = run("baseline")
    baseline_total = print_results("baseline", baseline)

    print("\nPhase 2: CACHED (cache_control on system + tools)...")
    cached = run("cached")
    cached_total = print_results("cached", cached)

    print("\n" + "=" * 60)
    print("\nSUMMARY")
    print(f"  Baseline:   ${baseline_total:.4f}")
    print(f"  Cached:     ${cached_total:.4f}")
    if baseline_total > 0:
        reduction = (baseline_total - cached_total) / baseline_total * 100
        print(f"  Reduction:  {reduction:.1f}%")
    print()


if __name__ == "__main__":
    main()
