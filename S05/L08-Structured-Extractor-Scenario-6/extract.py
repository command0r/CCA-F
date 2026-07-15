"""Sync extraction with the validation-retry-with-error-feedback loop.

Usage:  python extract.py contracts/contract_004.txt
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv
from pydantic import ValidationError as PydanticValidationError

from schemas import ContractMetadata
from validators import ValidationError, is_recoverable, validate


class MaxRetriesExceeded(Exception):
    """Raised when the retry loop exhausts without converging on a clean extraction."""

    def __init__(self, payload: dict, errors: list[ValidationError]):
        self.payload = payload
        self.errors = errors
        super().__init__("retry loop did not converge")

load_dotenv()

MODEL = "claude-sonnet-4-6"
MAX_RETRIES = 3

client = Anthropic()


def build_tool() -> dict:
    """Schema-as-tool. strict=True turns on grammar-constrained sampling."""
    return {
        "name": "extract_contract_metadata",
        "description": (
            "Extract structured metadata from a contract document. "
            "REQUIRED BEHAVIOR for optional fields:\n"
            "- effective_date: extract the date the agreement takes effect when stated.\n"
            "- termination_clause: extract the verbatim termination language when present.\n"
            "- line_items: if the document contains ANY payment schedule, fee table, "
            "or itemized cost breakdown, extract EVERY line as a separate LineItem entry. "
            "Do NOT summarize. Do NOT skip line items because there are many.\n"
            "- stated_total_usd: extract the document's stated total EXACTLY as written, "
            "even if it doesn't reconcile with line items. The validator depends on this.\n"
            "Only return null/empty for fields that are GENUINELY ABSENT from the source. "
            "Use 'unclear' enum values for categorical fields you cannot confidently determine. "
            "Use 'other' + contract_type_detail string for contract types not in the enum."
        ),
        "input_schema": ContractMetadata.model_json_schema(),
        "strict": True,
    }


USER_INSTRUCTION = (
    "Extract ALL metadata from the contract below using the extract_contract_metadata tool. "
    "Read the entire document carefully. Extract every payment line item, the stated total, "
    "the effective date, and the termination clause when present. Do not skip any of these.\n\n"
    "Contract:\n\n"
)


def extract(document: str) -> ContractMetadata:
    """Extract with retry-on-semantic-error loop. Returns validated payload."""
    tool = build_tool()
    messages: list[dict] = [{"role": "user", "content": USER_INSTRUCTION + document}]
    last_payload: dict | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            tools=[tool],
            tool_choice={"type": "tool", "name": "extract_contract_metadata"},
            messages=messages,
        )

        tool_use_block = next(b for b in response.content if b.type == "tool_use")
        last_payload = tool_use_block.input

        try:
            payload = ContractMetadata.model_validate(last_payload)
        except PydanticValidationError as e:
            print(f"  attempt {attempt}: Pydantic rejected the payload — retrying with feedback")
            if attempt == MAX_RETRIES:
                raise MaxRetriesExceeded(
                    last_payload,
                    [ValidationError(field="schema", message=str(e), recoverable=False)],
                )
            # Feed the Pydantic error back as a tool_result and let the model retry.
            # strict:true guarantees JSON-schema conformance but Pydantic can still
            # reject on enum values, custom validators, or cross-field rules.
            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use_block.id,
                        "content": f"Schema validation failed: {e}\nRe-check field types and constraints, then return a corrected extraction.",
                        "is_error": True,
                    }
                ],
            })
            continue

        errors = validate(payload)
        if not errors:
            print(f"  attempt {attempt}: passed all semantic checks")
            return payload

        if not is_recoverable(errors):
            unrecoverable = [e for e in errors if not e.recoverable]
            raise RuntimeError(f"Unrecoverable semantic errors: {unrecoverable}")

        print(f"  attempt {attempt}: {len(errors)} recoverable error(s) — retrying with feedback")
        # After an assistant tool_use, the next user turn MUST contain a tool_result
        # block referencing that tool_use's id. We pass the validation error as the
        # tool_result content with is_error=True — Claude reads this as a tool failure
        # and re-attempts the extraction.
        messages.append({"role": "assistant", "content": response.content})
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use_block.id,
                    "content": _build_retry_message(errors),
                    "is_error": True,
                }
            ],
        })

    raise MaxRetriesExceeded(last_payload, errors)


def _build_retry_message(errors: list[ValidationError]) -> str:
    lines = ["Re-check the extraction. Specific issues:"]
    lines.extend(f"  - {e.field}: {e.message}" for e in errors)
    lines.append("Return a corrected extraction.")
    return "\n".join(lines)


def main():
    if len(sys.argv) != 2:
        print("Usage: python extract.py <path-to-contract>")
        sys.exit(1)

    document = Path(sys.argv[1]).read_text(encoding="utf-8")
    print(f"Extracting from {sys.argv[1]}...")

    try:
        result = extract(document)
        print("\n" + "=" * 60)
        print(json.dumps(result.model_dump(), indent=2, default=str))
    except MaxRetriesExceeded as e:
        print(f"\n  ✗ Retry loop did not converge after {MAX_RETRIES} attempts.")
        print(f"  The source document appears to have an internal inconsistency:")
        for err in e.errors:
            print(f"    [{err.field}] {err.message}")
        print(f"\n  This is the 'retries don't help' case from lecture 5.36 —")
        print(f"  when the source data itself is inconsistent, no amount of retrying")
        print(f"  will reconcile it. Architectural answer: surface to human review.")
        print(f"\n  Last extracted payload (preserved for the reviewer):")
        print(json.dumps(e.payload, indent=2, default=str))
        sys.exit(2)


if __name__ == "__main__":
    main()
