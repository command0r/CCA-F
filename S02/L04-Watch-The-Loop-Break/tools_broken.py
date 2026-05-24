"""
Silent-failure tool. The bug: on not_found, returns '' instead of structured error.
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
            return ""        # <-- the bug: silent failure
        return order
    return ""