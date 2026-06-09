"""Semantic validators — the layer constrained decoding can't see.

Each validator returns None on pass, or a (message, recoverable) tuple on fail.
"""

from __future__ import annotations

from dataclasses import dataclass

from schemas import ContractMetadata, ContractType


@dataclass
class ValidationError:
    field: str
    message: str
    recoverable: bool


def validate(payload: ContractMetadata) -> list[ValidationError]:
    """Run all semantic checks against the extracted payload."""
    errors: list[ValidationError] = []

    if not payload.parties:
        errors.append(ValidationError(
            field="parties",
            message="parties is empty — every contract must name at least one party.",
            recoverable=False,
        ))

    if payload.contract_type == ContractType.OTHER and not payload.contract_type_detail:
        errors.append(ValidationError(
            field="contract_type_detail",
            message="contract_type='other' requires contract_type_detail to be non-null.",
            recoverable=True,
        ))

    if payload.line_items and payload.stated_total_usd is not None:
        calculated = sum(item.amount_usd for item in payload.line_items)
        if abs(calculated - payload.stated_total_usd) > 0.01:
            errors.append(ValidationError(
                field="stated_total_usd",
                message=(
                    f"stated_total_usd = {payload.stated_total_usd}, "
                    f"but sum(line_items) = {calculated:.2f}. "
                    "Re-check the totals — either the stated total is wrong, "
                    "a line item is missing, or a line item amount is wrong."
                ),
                recoverable=True,
            ))

    return errors


def is_recoverable(errors: list[ValidationError]) -> bool:
    """A retry helps only if every error is marked recoverable."""
    return bool(errors) and all(e.recoverable for e in errors)
