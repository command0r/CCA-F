"""Pydantic schemas for contract metadata extraction.

Demonstrates the four documented schema design patterns from lecture 5.36:
"other" + detail string, "unclear" enum, nullable for optional, self-correction fields.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ContractType(str, Enum):
    SERVICES = "services"
    SAAS = "saas"
    NDA = "nda"
    CONSULTING = "consulting"
    OTHER = "other"
    UNCLEAR = "unclear"


class LineItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str = Field(description="What the line item is for.")
    amount_usd: float = Field(description="Amount in USD, numeric only.")


class ContractMetadata(BaseModel):
    """Structured representation of contract metadata."""

    model_config = ConfigDict(extra="forbid")

    parties: list[str] = Field(
        description="All named parties to the agreement. Always required.",
    )
    contract_type: ContractType = Field(
        description=(
            "Category of agreement. Use 'other' for types not listed and provide "
            "contract_type_detail. Use 'unclear' if the document doesn't make it determinable."
        ),
    )
    contract_type_detail: Optional[str] = Field(
        description="Required when contract_type is 'other'. Free-text description. Null otherwise.",
    )
    effective_date: Optional[str] = Field(
        description="ISO 8601 date the agreement takes effect. Null if not stated.",
    )
    termination_clause: Optional[str] = Field(
        description="Verbatim termination language from the document. Null if absent.",
    )
    line_items: list[LineItem] = Field(
        description=(
            "EVERY itemized payment line in the document. Required field — must be present "
            "in output. Use empty list ONLY if the document has no payment schedule at all "
            "(e.g., an NDA). Otherwise extract every line, do not summarize."
        ),
    )
    stated_total_usd: Optional[float] = Field(
        description=(
            "The total amount STATED in the document — extract EXACTLY as written, even if "
            "it doesn't reconcile with line items. Null only if no total is stated."
        ),
    )
    indemnification: bool = Field(
        description="True if the contract contains an indemnification clause.",
    )
