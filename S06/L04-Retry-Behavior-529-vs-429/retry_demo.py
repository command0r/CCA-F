"""Distinguish 429 (your org's rate limit) from 529 (Anthropic overloaded).

Two errors with the same "please back off" surface behavior, but two very
different causes and two different mitigation strategies. This demo trips
each one deterministically using httpx.MockTransport so the SDK's retry
behavior and the surfaced exception type can be observed without spending
tokens or racing against real capacity.

Usage:
    python retry_demo.py            # runs both scenarios end-to-end
    python retry_demo.py 429        # 429-only scenario
    python retry_demo.py 529        # 529-only scenario
"""
from __future__ import annotations

import random
import sys
import time
from typing import Callable

import httpx
from anthropic import Anthropic, APIStatusError, InternalServerError, RateLimitError

MODEL = "claude-sonnet-4-6"


# ---------------------------------------------------------------------------
# Mock transport — deterministically returns 429 or 529 for every request.
# ---------------------------------------------------------------------------

def make_mock_client(status: int) -> Anthropic:
    """Return an Anthropic client whose HTTP layer always returns `status`.

    We DO NOT set a Retry-After header even for 429. In production the API
    sends one and the SDK respects it (typically 20-60 seconds); for a
    teaching demo we let the SDK fall back to its exponential-backoff
    default so the whole run completes in under two seconds.

    max_retries is set to 1 for the same reason — the pedagogical point
    is the surfaced exception type and its correct handling, not the SDK's
    retry cadence. In production keep the default (max_retries=2) or tune
    it based on your reliability requirements.
    """
    body = {
        429: {"type": "error", "error": {"type": "rate_limit_error", "message": "rate limit exceeded"}},
        529: {"type": "error", "error": {"type": "overloaded_error", "message": "platform overloaded"}},
    }[status]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json=body)

    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport)
    return Anthropic(api_key="sk-mock-key", http_client=http_client, max_retries=1)


# ---------------------------------------------------------------------------
# Scenario 1 — 429: YOUR org's per-minute / per-day quota is exhausted.
# ---------------------------------------------------------------------------

def scenario_429() -> None:
    print("=" * 72)
    print("SCENARIO 1 — 429 rate_limit_error")
    print("=" * 72)
    print(
        "Meaning:  YOUR organization has hit its per-minute or per-day quota.\n"
        "Scope:    Your org only. Other orgs on Anthropic are unaffected.\n"
        "Retry:    SDK auto-retries max_retries times with exponential backoff.\n"
        "          If a Retry-After header is present, the SDK respects it.\n"
        "Fix:      Slow your call rate. Buy more quota. Queue/throttle upstream.\n"
        "          Retrying harder does not solve the underlying quota problem.\n"
    )

    client = make_mock_client(429)

    print("→ Calling messages.create() against a 429-mocked API...")
    print("  (SDK will retry once with exponential backoff, then surface the error)")
    started = time.monotonic()
    try:
        client.messages.create(
            model=MODEL,
            max_tokens=64,
            messages=[{"role": "user", "content": "hello"}],
        )
    except RateLimitError as exc:
        elapsed = time.monotonic() - started
        print(f"  Caught RateLimitError after {elapsed:.1f}s wall time (SDK exhausted its retries).")
        print(f"  status_code = {exc.status_code}")
        print(f"  response body error type = {exc.body['error']['type'] if exc.body else 'n/a'}")
        print()
        print("Recommended app-level handling for 429:")
        print("  1. Check response.headers['retry-after'] and wait that long before your")
        print("     next call (the SDK already respects this, but application code that")
        print("     hits the exhaustion boundary needs its own back-off).")
        print("  2. Drop or queue non-critical work. 429 means you're pushing more work")
        print("     than your quota allows — retrying without fixing that just wastes time.")
        print("  3. If persistent, request a rate-limit increase in the Anthropic console.")


# ---------------------------------------------------------------------------
# Scenario 2 — 529: Anthropic's platform is under global load.
# ---------------------------------------------------------------------------

def scenario_529() -> None:
    print("=" * 72)
    print("SCENARIO 2 — 529 overloaded_error")
    print("=" * 72)
    print(
        "Meaning:  ANTHROPIC's platform is over capacity right now (global).\n"
        "Scope:    Every org on the platform sees this. Not your quota.\n"
        "Retry:    SDK auto-retries; typically no Retry-After header. Longer,\n"
        "          jittered exponential backoff is the right pattern.\n"
        "Fix:      Wait it out. There's nothing to change on your side. If it\n"
        "          persists, consider Batches API (unaffected during typical\n"
        "          Messages-API pressure) or a fallback model.\n"
    )

    client = make_mock_client(529)

    print("→ Calling messages.create() against a 529-mocked API...")
    print("  (SDK will retry with exponential backoff — 529 has no Retry-After)")
    started = time.monotonic()
    try:
        client.messages.create(
            model=MODEL,
            max_tokens=64,
            messages=[{"role": "user", "content": "hello"}],
        )
    except APIStatusError as exc:
        elapsed = time.monotonic() - started
        print(f"  Caught {type(exc).__name__} after {elapsed:.1f}s wall time (SDK exhausted its retries).")
        print(f"  status_code = {exc.status_code}")
        print(f"  response body error type = {exc.body['error']['type'] if exc.body else 'n/a'}")
        print()
        print("Recommended app-level handling for 529:")
        print("  1. Longer, jittered backoff — start with ~4s and double up to a cap")
        print("     (e.g., 60s). 529 outages usually clear in minutes; make sure your")
        print("     retry cadence isn't dogpiling the platform.")
        print("  2. If your workload is not latency-sensitive, switch to the Batches")
        print("     API (50% cheaper AND typically unaffected by 529 episodes).")
        print("  3. If your workload IS latency-sensitive, consider a fallback model")
        print("     tier that's less contended (e.g., Haiku).")
        print("  4. Do NOT ask for a rate-limit increase — that's for 429, not 529.")

    # Demonstrate the recommended app-level backoff pattern.
    print()
    print("App-level backoff loop that plays well with 529 (jittered exponential):")
    for attempt in range(1, 4):
        base = min(60, 2 ** attempt)
        wait = base + random.uniform(0, base * 0.25)  # jitter up to 25%
        print(f"  attempt {attempt}: back off ~{wait:.1f}s before next call")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "both"

    scenarios: dict[str, Callable[[], None]] = {
        "429": scenario_429,
        "529": scenario_529,
    }

    if mode == "both":
        scenario_429()
        print()
        scenario_529()
    elif mode in scenarios:
        scenarios[mode]()
    else:
        print("Usage: python retry_demo.py [429|529|both]")
        return 1

    print()
    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)
    print("  429 = YOUR org's rate limit. Slow down or buy more quota.")
    print("  529 = ANTHROPIC's platform overload. Wait it out; consider Batches.")
    print("  Both are retryable, but the RIGHT retry strategy differs — and the")
    print("  RIGHT organisational response differs even more.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
