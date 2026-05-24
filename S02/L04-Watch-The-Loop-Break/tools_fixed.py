"""
Structured-error tool. Returns {status, error, next_action} on not_found.
"""

TOOL_SCHEMA = [{
    "name": "lookup_order",
    "description": (
        "Look up an order by its ID. "
        "Returns status='ok' with data on success, or status='not_found' "
        "with an error message and next_action if the order does not exist."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "order_id": {"type": "string"}
        },
        "required": ["order_id"]
    }
}]

ORDERS = {
    "12345": {"status": "shipped", "total": 49.99},
}


def execute_tool(name: str, args: dict):
    if name == "lookup_order":
        order = ORDERS.get(args["order_id"])
        if not order:
            return {
                "status": "not_found",
                "error": f"No order with id {args['order_id']}",
                "next_action": "ask the user to verify the order ID",
            }
        return {"status": "ok", "data": order}
    return {"status": "error", "error": "unknown tool"}