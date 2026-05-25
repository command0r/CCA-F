"""
Deterministic stand-in for the Anthropic client.

Why this exists:
  Modern Claude models reason past ambiguous tool output within 1-2 turns,
  which makes the 'forever loop' failure mode hard to demonstrate live on
  camera. This mock client mimics how Claude WOULD respond if it strictly
  followed tool guidance, so the demo's failure-and-fix behavior is
  reproducible across recordings.

Decision rule:
  - First call: tool_use with order_id="99999"
  - Subsequent calls: inspect the last tool result
      * If result parses as JSON with status='not_found' or status='ok',
        emit end_turn (the structured-error case — the fix terminates)
      * Otherwise (prose, empty string, ambiguous text),
        emit tool_use with the next ID variation (the broken case loops)

The SDK call signature is identical to anthropic.Anthropic().messages.create,
so agent.py treats both clients the same way.
"""
import json
from types import SimpleNamespace


class _MockMessages:
    def __init__(self):
        self.variations = ["099999", "ORD-99999", "00099999", "ORD-099999", "99999-A"]
        self.call_count = 0

    def create(self, *, model, max_tokens, tools, messages):
        self.call_count += 1
        last_msg = messages[-1]

        # First turn: only the user prompt is in messages
        if last_msg["role"] == "user" and isinstance(last_msg["content"], str):
            return self._tool_use("99999")

        # Subsequent turns: pull the most recent tool_result block
        if last_msg["role"] == "user" and isinstance(last_msg["content"], list):
            tool_results = [
                b for b in last_msg["content"]
                if isinstance(b, dict) and b.get("type") == "tool_result"
            ]
            if not tool_results:
                return self._end_turn("No tool result to evaluate.")

            raw = tool_results[-1]["content"]

            # Try to parse as structured JSON
            try:
                parsed = json.loads(raw) if isinstance(raw, str) else raw
                if isinstance(parsed, dict):
                    status = parsed.get("status")
                    if status == "not_found":
                        return self._end_turn(
                            f"I couldn't find an order with ID 99999. "
                            f"{parsed.get('error', '')} "
                            f"Could you double-check the order number?"
                        )
                    if status == "ok":
                        return self._end_turn(
                            f"Found the order: {parsed.get('data')}"
                        )
            except (json.JSONDecodeError, TypeError):
                pass

            # Unstructured / ambiguous — keep trying variations
            next_var = self.variations[(self.call_count - 2) % len(self.variations)]
            return self._tool_use(next_var)

        return self._end_turn("Done.")

    def _tool_use(self, order_id: str):
        block = SimpleNamespace(
            type="tool_use",
            id=f"toolu_mock_{self.call_count:02d}",
            name="lookup_order",
            input={"order_id": order_id},
        )
        return SimpleNamespace(stop_reason="tool_use", content=[block])

    def _end_turn(self, text: str):
        block = SimpleNamespace(type="text", text=text)
        return SimpleNamespace(stop_reason="end_turn", content=[block])


class MockClient:
    def __init__(self):
        self.messages = _MockMessages()
