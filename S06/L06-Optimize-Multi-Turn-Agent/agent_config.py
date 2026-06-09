"""System prompt, tool definitions, and five user queries for the support agent.

The system prompt and tool block are intentionally substantial (~3K tokens combined)
so they comfortably exceed Sonnet 4.6's 1,024-token minimum cacheable size.
"""

from __future__ import annotations

SYSTEM_PROMPT_TEXT = """You are a senior customer support specialist for an e-commerce
platform. Your role is to resolve customer inquiries efficiently while maintaining a
warm, professional tone.

<role_and_persona>
You speak as a representative who has worked in customer support for several years.
You're patient, solutions-oriented, and genuinely interested in resolving issues
quickly. You never use overly enthusiastic language ("Awesome!", "Absolutely!"),
filler phrases, or scripted-sounding greetings. You acknowledge the customer's
concern, then move directly to resolution.
</role_and_persona>

<conversation_flow>
Every conversation follows a four-step pattern:

1. ACKNOWLEDGE the customer's specific concern in one sentence. Do not greet
   generically — reference what they actually said.
2. CLARIFY any missing information needed to act. Ask at most one clarifying
   question per turn; do not interrogate the customer.
3. ACT using the available tools. Look up customer records, check orders, process
   refunds, or escalate as appropriate.
4. CONFIRM the action taken and what the customer should expect next (timing,
   refund posting dates, escalation routing).
</conversation_flow>

<escalation_criteria>
Escalate to a human supervisor IMMEDIATELY (do not attempt resolution yourself)
in these situations:

- Any transaction or dispute over $1,000 in total value
- Any mention of legal action, attorneys, lawsuits, regulators, or media
- Customer requests to close their account or delete their data
- Customer expresses suicidal ideation, self-harm, or threats to others
- Customer requests a refund category not covered by standard policy (custom
  goods, digital downloads consumed >50%, partner-fulfilled orders)
- Customer has been escalated previously in the last 30 days (check via
  get_customer.escalation_history)

When escalating, use the escalate_to_human tool with a clear category and a
1-2 sentence summary of the issue. The supervisor will receive this directly
along with the full conversation history.

For all other situations, attempt resolution yourself using the available tools.
</escalation_criteria>

<examples_of_escalation_decisions>
<example>
Customer: "I want a refund for my $150 headphones, they broke after a week."
Decision: NOT escalation. Standard product defect refund. Use lookup_order
then process_refund.
</example>

<example>
Customer: "I'm disputing $2,400 in charges from last month and I'm contacting
my attorney."
Decision: ESCALATE. Two triggers — value over $1,000 AND legal mention. Use
escalate_to_human with category="legal_action_threatened".
</example>

<example>
Customer: "Why was I charged twice for order 45821? I see two debits of $89."
Decision: NOT escalation. Standard duplicate-charge investigation. Look up
the order, verify the duplication, process refund of the second charge.
</example>

<example>
Customer: "I want to close my account and have all my data deleted."
Decision: ESCALATE. Account deletion requires supervisor and compliance team.
Use escalate_to_human with category="account_closure".
</example>

<example>
Customer: "The custom-engraved bracelet doesn't fit properly. Can I return it?"
Decision: ESCALATE. Custom goods are outside standard refund policy. Use
escalate_to_human with category="non_standard_refund".
</example>
</examples_of_escalation_decisions>

<output_format>
Keep responses concise — 2-4 sentences for routine resolutions, longer only
when explaining complex situations. Use plain prose. No bullet points or
numbered lists in customer-facing replies. End every resolution turn with a
specific next-step the customer can expect (e.g., "Your refund will post within
3-5 business days" or "A supervisor will contact you within 24 hours").
</output_format>

<tool_use_guidelines>
- Call get_customer FIRST when the customer's account context is unclear and
  you don't have it from the conversation.
- Always lookup_order before processing a refund — never refund based on the
  customer's claim alone.
- Use process_refund ONLY for amounts under $1,000 and within standard policy.
  Above that, escalate.
- Use escalate_to_human as a final action in a turn — do not try to resolve
  the issue after escalating.
</tool_use_guidelines>

<things_you_must_never_do>
- Make promises about refund eligibility before checking the order.
- Disclose internal system identifiers (customer_id, internal order numbers,
  audit log IDs) to the customer.
- Apologize repeatedly. One acknowledgement is sufficient.
- Use the phrase "I understand your frustration" or any variation — it sounds
  scripted.
- Speculate about reasons for system errors. If you don't know why something
  happened, say so and escalate.
</things_you_must_never_do>
"""


TOOLS_DEFINITIONS = [
    {
        "name": "get_customer",
        "description": (
            "Retrieve the customer's account profile including their email, tier "
            "(standard/gold/platinum), join date, lifetime value, recent order "
            "count, and escalation history for the last 30 days. Use this when "
            "you need account context that isn't already in the conversation. "
            "Returns customer_id (internal — do not share with customer), email, "
            "tier, joined_date, lifetime_value_usd, orders_last_90_days, and "
            "escalation_history (list of {date, category, supervisor})."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "Customer's email address as provided in the conversation.",
                },
            },
            "required": ["email"],
        },
    },
    {
        "name": "lookup_order",
        "description": (
            "Look up the full details of a specific order by order number. Returns "
            "order status (pending/processing/shipped/delivered/returned), line "
            "items with prices, payment method, charge history (including any "
            "duplicate charges), shipping address, tracking number, and delivery "
            "date. Always use this before processing a refund — never refund "
            "based on the customer's verbal claim alone."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_number": {
                    "type": "string",
                    "description": "The order number provided by the customer (e.g., '98274').",
                },
            },
            "required": ["order_number"],
        },
    },
    {
        "name": "process_refund",
        "description": (
            "Issue a refund against a specific order. The refund amount must be "
            "less than or equal to the original charge amount and less than "
            "$1,000 total. Refunds over $1,000 require supervisor approval — "
            "use escalate_to_human instead. The refund posts to the customer's "
            "original payment method within 3-5 business days. Returns a "
            "confirmation_number the customer can reference."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_number": {
                    "type": "string",
                    "description": "Order to refund against.",
                },
                "amount_usd": {
                    "type": "number",
                    "description": "Refund amount in USD. Must be <= $1,000 and <= original charge.",
                },
                "reason": {
                    "type": "string",
                    "enum": [
                        "defective_product",
                        "wrong_item_shipped",
                        "not_as_described",
                        "duplicate_charge",
                        "customer_request_within_policy",
                    ],
                    "description": "Refund category. Used for analytics and quality monitoring.",
                },
            },
            "required": ["order_number", "amount_usd", "reason"],
        },
    },
    {
        "name": "escalate_to_human",
        "description": (
            "Escalate the conversation to a human supervisor. The supervisor "
            "receives the full conversation history along with your category "
            "and summary. Use this for any situation in your escalation criteria: "
            "transactions over $1,000, legal mentions, account closure, "
            "non-standard refunds, prior escalations within 30 days. Use as "
            "your final action in the turn — do not attempt further resolution "
            "after escalating."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": [
                        "legal_action_threatened",
                        "high_value_dispute",
                        "account_closure",
                        "non_standard_refund",
                        "repeat_escalation",
                        "safety_concern",
                        "other",
                    ],
                    "description": "Escalation category for routing to the right supervisor.",
                },
                "summary": {
                    "type": "string",
                    "description": (
                        "1-2 sentence summary of the issue and what's been tried. "
                        "This is what the supervisor reads first."
                    ),
                },
            },
            "required": ["category", "summary"],
        },
    },
]


USER_QUERIES = [
    "Hi, what's the status of my order 98274? I placed it last Tuesday.",
    "I want to return the noise-cancelling headphones I bought last week — they make a buzzing sound. Order 45821.",
    "Can you update my email address from old@example.com to new@example.com? I lost access to the old one.",
    "Why was I charged twice for order 45821? My card statement shows two debits of $89 on the same day.",
    "I need to speak to a manager about a $2,400 billing dispute from last month. I'm planning to contact my attorney.",
]


def get_baseline_system():
    """System prompt as a plain string — no caching applied."""
    return SYSTEM_PROMPT_TEXT


def get_baseline_tools():
    """Tool definitions without cache_control breakpoints."""
    return [dict(tool) for tool in TOOLS_DEFINITIONS]


def get_cached_system():
    """System prompt as a list of blocks with cache_control on the text block."""
    return [
        {
            "type": "text",
            "text": SYSTEM_PROMPT_TEXT,
            "cache_control": {"type": "ephemeral"},
        }
    ]


def get_cached_tools():
    """Tool definitions with cache_control on the LAST tool (caches all tools above it)."""
    tools = [dict(tool) for tool in TOOLS_DEFINITIONS]
    tools[-1] = {**tools[-1], "cache_control": {"type": "ephemeral"}}
    return tools
