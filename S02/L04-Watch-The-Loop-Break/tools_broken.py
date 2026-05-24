"""
Ambiguous-output tool. The bug: on not_found, returns a prose instruction
Claude reads as 'try again with a variation' — so it does, forever.

This is failure-mode #2 from Lecture 2.3 (ambiguous output). We picked
this over failure-mode #1 (silent failure / empty string) because newer
Claude snapshots are smart enough to recover from a bare empty string;
they treat it as 'not found' and respond gracefully. Real production
bugs more often look like the line below — a tool returning prose that
the model interprets as a directive.
"""

TOOL_SCHEMA = [{
    "name": "lookup_order",
    "description": "Look up an order by its ID.",
    "input_schema": {
        "type": "object",
        "properties": {
            "order_id": {"type": "string"}
        },
        "required": ["order_id"]
    }
}]

# Tiny fake DB. Order 99999 (the one the demo asks for) does NOT exist.
ORDERS = {
    "12345": {"status": "shipped", "total": 49.99},
}


def execute_tool(name: str, args: dict):
    if name == "lookup_order":
        order = ORDERS.get(args["order_id"])
        if not order:
            # <-- the bug: prose output that Claude reads as 'retry with a variation'
            return (
                f"No exact match for '{args['order_id']}'. "
                "Try variations (with or without leading zeros, hyphens, or 'ORD-' prefix)."
            )
        return order
    return ""
