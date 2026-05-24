"""
Agent loop for the L2.4 demo.
Identical for both broken and fixed runs — only the tool module changes.
"""
import sys
import json
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

USER_MESSAGE = "Look up order 99999 and tell me its status."
MODEL = "claude-sonnet-4-5"

# Safety belt — capped low so the recording doesn't burn the host's wallet.
# In production this would be 25+ and exist purely as a circuit breaker.
MAX_ITERATIONS = 5


def load_tools(mode: str):
    if mode == "broken":
        from tools_broken import TOOL_SCHEMA, execute_tool
    elif mode == "fixed":
        from tools_fixed import TOOL_SCHEMA, execute_tool
    else:
        sys.exit("usage: python agent.py [broken|fixed]")
    return TOOL_SCHEMA, execute_tool


def run(mode: str) -> None:
    tools, execute_tool = load_tools(mode)
    messages = [{"role": "user", "content": USER_MESSAGE}]

    for i in range(1, MAX_ITERATIONS + 1):
        print(f"\n[iter {i}] calling Claude...")
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=tools,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            text_parts = [b.text for b in response.content if hasattr(b, "text")]
            print(f"\n[DONE at iter {i}] {' '.join(text_parts).strip()}")
            return

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"[iter {i}] tool_use: {block.name}({json.dumps(block.input)})")
                    result = execute_tool(block.name, block.input)
                    display = result if isinstance(result, str) else json.dumps(result)
                    print(f"[iter {i}] tool_result: {display!r}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": display,
                    })
            messages.append({"role": "user", "content": tool_results})

    print(f"\n[CAPPED at iter {MAX_ITERATIONS}] safety belt fired — no convergence")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "broken"
    run(mode)