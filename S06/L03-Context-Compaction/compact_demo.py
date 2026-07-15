"""Simulate what Claude Code's /compact command does under the hood.

Long conversations eat context. Claude Code's `/compact` command replaces
the old turns with an LLM-generated summary and keeps only the most
recent turns verbatim — freeing tokens for continued work.

This demo:
  1. Builds a plausible 10-turn support-agent conversation.
  2. Counts input tokens for the full history (Messages Token Count API).
  3. Summarizes turns 1..N-2 using Claude (mimicking /compact).
  4. Reconstructs a compacted history: system + summary as one assistant
     turn + the last 2 turns verbatim.
  5. Counts tokens for the compacted history.
  6. Reports the reduction and what was preserved vs summarized.

Usage:
    python compact_demo.py           # real API — requires ANTHROPIC_API_KEY
    python compact_demo.py --mock    # deterministic mock, no API calls
"""
from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-4-6"
SUMMARIZER_SYSTEM = (
    "You are compressing a conversation history for context-window reuse. "
    "Produce a compact summary that preserves: (1) the user's goals and "
    "constraints, (2) all decisions and commitments made, (3) any open "
    "questions or unfinished actions, (4) key facts and references cited. "
    "Do NOT include pleasantries, restatements, or exploratory reasoning "
    "the model performed. Aim for ~150 tokens of dense, factual summary."
)

# A plausible customer-support conversation. 10 turns, mostly filler prose.
CONVERSATION = [
    ("user",      "Hi, I need help with order 12345. It was supposed to arrive last Thursday but tracking says it's still in transit and I'm going on vacation tomorrow. Can you check what's going on and see if you can either expedite it or arrange a hold at a nearby pickup point?"),
    ("assistant", "I've pulled up order 12345. The carrier's last scan was three days ago in the Louisville sorting facility. That's unusual for a package with a Thursday commitment. Let me check whether we can escalate to the carrier or set up a hold-at-location for you. Which pickup location is nearest — the Main Street FedEx or the Cedar Avenue drop point?"),
    ("user",      "Main Street is closer, that would work. But actually — could you just refund it and I'll reorder when I'm back? I don't want to risk it sitting somewhere for a week if I miss the pickup window."),
    ("assistant", "That's reasonable. I can process the refund now, and you'll see the credit back on your original payment method within 3-5 business days. The order was $187.42 including shipping. Would you like me to issue the full refund, or refund only the item cost and keep the shipping charge for tracking research?"),
    ("user",      "Full refund please. And can you flag the account so I don't get charged for the return if the package eventually shows up?"),
    ("assistant", "Full refund of $187.42 processed. Reference number RF-889412. I've also added an account note flagging this as a carrier-loss case — if the package eventually surfaces, you won't be charged for a return; we'll ask you to donate or dispose of it. Is there anything else I can help you with today?"),
    ("user",      "One more thing — I've had this happen twice in six months. Is there something wrong with my address on file? I keep getting deliveries that go dark at Louisville."),
    ("assistant", "Good catch. Let me look at your delivery history. I see three prior orders that either delayed or lost at Louisville — that's a routing pattern, not an address issue. Your address is clean. This looks like a carrier hub problem specific to Louisville for shipments to your ZIP. I'd recommend selecting the alternative carrier option (UPS Ground) at checkout for future orders — that routes through Cincinnati instead."),
    ("user",      "That's really helpful, thank you. Where do I select the alternative carrier? I don't remember seeing that option."),
    ("assistant", "At checkout, on the shipping method dropdown, expand the 'Standard shipping' option and there's a 'Show alternative carriers' link below the default. You'll see UPS Ground and USPS Priority as options — either avoids Louisville. If you'd like, I can also default your account to prefer UPS Ground going forward so you don't have to select it each time."),
]


def as_messages(turns: list[tuple[str, str]]) -> list[dict]:
    """Convert (role, content) tuples to the Messages API shape."""
    return [{"role": role, "content": content} for role, content in turns]


def count_tokens(client, messages: list[dict]) -> int:
    """Use the Anthropic token count endpoint. Free — doesn't consume tokens."""
    r = client.messages.count_tokens(model=MODEL, messages=messages)
    return r.input_tokens


def summarize(client, messages: list[dict]) -> str:
    """One-shot summary of the conversation. This IS what /compact does."""
    r = client.messages.create(
        model=MODEL,
        max_tokens=400,
        system=SUMMARIZER_SYSTEM,
        messages=[{
            "role": "user",
            "content": (
                "Summarize this conversation history preserving all decisions, "
                "open questions, and key facts:\n\n"
                + format_transcript(messages)
            ),
        }],
    )
    # Concatenate any text blocks in the response.
    return "".join(b.text for b in r.content if hasattr(b, "text")).strip()


def format_transcript(messages: list[dict]) -> str:
    return "\n\n".join(f"[{m['role'].upper()}] {m['content']}" for m in messages)


def run_real() -> None:
    from anthropic import Anthropic
    client = Anthropic()

    print("=" * 72)
    print("STEP 1 — Full 10-turn conversation")
    print("=" * 72)
    full_messages = as_messages(CONVERSATION)
    full_tokens = count_tokens(client, full_messages)
    print(f"  Turns:  {len(full_messages)}")
    print(f"  Tokens: {full_tokens}\n")

    print("=" * 72)
    print("STEP 2 — Summarize turns 1..8 (all but the last 2)")
    print("=" * 72)
    older = full_messages[:-2]
    recent = full_messages[-2:]
    print(f"  Compressing {len(older)} old turns; preserving {len(recent)} recent turns verbatim.")
    print()
    print("  Sending old turns to Claude for summarization...")
    summary = summarize(client, older)
    print()
    print("  Summary produced:")
    print("  " + "\n  ".join(summary.splitlines()))
    print()

    print("=" * 72)
    print("STEP 3 — Reconstruct compacted history")
    print("=" * 72)
    compacted_messages = [
        {"role": "user", "content": "[prior conversation summary]"},
        {"role": "assistant", "content": summary},
        *recent,
    ]
    compacted_tokens = count_tokens(client, compacted_messages)
    print(f"  Turns:  {len(compacted_messages)}  (1 summary pair + 2 recent = 4)")
    print(f"  Tokens: {compacted_tokens}")
    print()

    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)
    reduction = full_tokens - compacted_tokens
    reduction_pct = 100 * reduction / full_tokens if full_tokens else 0
    print(f"  Before /compact:  {full_tokens} input tokens")
    print(f"  After  /compact:  {compacted_tokens} input tokens")
    print(f"  Reduction:        {reduction} tokens ({reduction_pct:.1f}%)")
    print()
    print("  This is what Claude Code's `/compact` command does under the hood:")
    print("  summarize the old turns, keep the recent ones verbatim, and you get")
    print("  the context-window space back to continue working.")
    print()
    print("  Tradeoff: fine-grained details from the summarized turns are lost.")
    print("  Design principle: /compact when the recent context matters more than")
    print("  the historical detail. If you need the detail later, revisit the")
    print("  transcript from your session log.")


def run_mock() -> None:
    """Deterministic mock — no API calls. Uses rough word-count-based token
    estimates to demonstrate the pattern without requiring a key."""
    full_messages = as_messages(CONVERSATION)
    full_words = sum(len(m["content"].split()) for m in full_messages)
    full_tokens = int(full_words * 1.35)  # rough English words → tokens

    mock_summary = (
        "Customer requested help with order 12345 (delayed at Louisville "
        "carrier hub). Options offered: hold-at-Main-Street pickup or refund. "
        "Customer chose full refund ($187.42, ref RF-889412) and an account "
        "flag preventing return charge if package surfaces. Root cause "
        "identified: recurring Louisville routing issue for their ZIP — not "
        "an address problem. Remediation offered: switch default carrier to "
        "UPS Ground (routes via Cincinnati). Instructions for finding the "
        "alternative-carrier option at checkout provided. Open: set UPS "
        "Ground as account default?"
    )

    recent = full_messages[-2:]
    recent_words = sum(len(m["content"].split()) for m in recent)
    summary_words = len(mock_summary.split())
    compacted_tokens = int((summary_words + recent_words) * 1.35)

    print("MOCK MODE — no API calls, token counts are approximate.\n")
    print("=" * 72)
    print("STEP 1 — Full 10-turn conversation")
    print("=" * 72)
    print(f"  Turns:  {len(full_messages)}")
    print(f"  Tokens: ~{full_tokens} (estimated)\n")

    print("=" * 72)
    print("STEP 2 — Simulated summary")
    print("=" * 72)
    print("  " + "\n  ".join(mock_summary[i:i+68] for i in range(0, len(mock_summary), 68)))
    print()

    print("=" * 72)
    print("STEP 3 — Compacted history")
    print("=" * 72)
    print(f"  Turns:  4  (1 summary pair + 2 recent)")
    print(f"  Tokens: ~{compacted_tokens} (estimated)\n")

    reduction = full_tokens - compacted_tokens
    reduction_pct = 100 * reduction / full_tokens if full_tokens else 0
    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)
    print(f"  Before /compact:  ~{full_tokens} tokens")
    print(f"  After  /compact:  ~{compacted_tokens} tokens")
    print(f"  Reduction:        ~{reduction} tokens ({reduction_pct:.1f}%)")
    print()
    print("  Run without --mock to see real token counts from the Anthropic API.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mock", action="store_true", help="Deterministic mock, no API calls")
    args = parser.parse_args()

    if args.mock:
        run_mock()
        return 0

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY not set. Either export it or run with --mock.", file=sys.stderr)
        return 1

    run_real()
    return 0


if __name__ == "__main__":
    sys.exit(main())
