# S06-L04 — Retry Behavior: 429 vs 529

Two HTTP error codes the Anthropic SDK will surface at you, with the same
"please back off" behavior on the wire, but with completely different
causes and completely different correct responses:

| Code | Meaning | Scope | Your response |
|------|---------|-------|---------------|
| **429** — `rate_limit_error` | YOUR org's per-minute or per-day quota is exhausted. | Your org only. | Slow the call rate. Queue upstream. Buy more quota if this is persistent. |
| **529** — `overloaded_error` | Anthropic's platform is over capacity right now. | Everyone on the platform. | Wait it out with jittered backoff. Consider Batches API or a fallback model. |

Both are retryable. The SDK auto-retries both up to `max_retries` (default 2)
with exponential backoff. What's different is **what you do when the SDK
gives up.**

## Layout

```
retry_demo.py     Trips both codes deterministically via httpx.MockTransport.
                  No real API calls are made — no tokens spent.
requirements.txt  anthropic, httpx, python-dotenv
```

## Run

```bash
pip install -r requirements.txt
python retry_demo.py           # runs both scenarios
python retry_demo.py 429       # 429-only scenario
python retry_demo.py 529       # 529-only scenario
```

## What to look for

- **Both scenarios take several seconds of wall time** — that's the SDK's built-in
  exponential backoff between retries. Default is 2 retries, backoff starts
  at ~500ms and doubles.
- **The exception type differs**: `RateLimitError` for 429,
  `APIStatusError` (with `status_code == 529`) for 529.
- **The recommended app-level backoff differs**: 429 respects any `Retry-After`
  header the server sends (the SDK already does this); 529 usually has no
  `Retry-After` and calls for longer, jittered exponential backoff to avoid
  dogpiling the platform once it recovers.
- **The organizational response differs even more**: 429 is a "your side" problem
  (quota, throttling, queueing); 529 is an "Anthropic's side" problem (wait,
  switch to Batches, fall back to a less contended tier).

## Why this matters for the exam

The CCA-F exam explicitly distinguishes these two codes (Domain 5, Task
Statement 5.3 — Reliability Patterns). A common distractor is "retry with a
larger `max_retries`" for a 429 — which is wrong because the underlying
problem is quota, not transient failure. Another common distractor is
"request a rate-limit increase" for a 529 — which is wrong because 529
is platform-side, not your-org-side.

Root Cause Bias, applied to retries:

- **429**: the wrong answer is "retry harder." The right answer is "stop pushing
  more work than your quota allows."
- **529**: the wrong answer is "request more quota." The right answer is "back
  off longer, or route the work to a channel that isn't currently degraded."

## References

- docs.claude.com/en/api/errors — error codes reference
- docs.claude.com/en/docs/build-with-claude/rate-limits — 429 handling
- docs.claude.com/en/api/overloaded-error — 529 handling
