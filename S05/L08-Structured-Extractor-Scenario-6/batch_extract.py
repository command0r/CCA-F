"""Bulk extraction via Message Batches API.

Usage:  python batch_extract.py contracts/
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

from schemas import ContractMetadata

load_dotenv()

MODEL = "claude-sonnet-4-6"
POLL_INTERVAL_SECONDS = 30

client = Anthropic()


def build_tool() -> dict:
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
            "even if it doesn't reconcile with line items.\n"
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


def submit_batch(documents: dict[str, str]) -> str:
    """Create a batch. documents keys become custom_ids."""
    tool = build_tool()
    requests = [
        {
            "custom_id": custom_id,
            "params": {
                "model": MODEL,
                "max_tokens": 4096,
                "tools": [tool],
                "tool_choice": {"type": "tool", "name": "extract_contract_metadata"},
                "messages": [{"role": "user", "content": USER_INSTRUCTION + text}],
            },
        }
        for custom_id, text in documents.items()
    ]
    batch = client.messages.batches.create(requests=requests)
    return batch.id


def wait_for_batch(batch_id: str) -> None:
    """Poll until processing_status is 'ended'."""
    while True:
        batch = client.messages.batches.retrieve(batch_id)
        counts = batch.request_counts
        print(
            f"  status={batch.processing_status} "
            f"succeeded={counts.succeeded} errored={counts.errored} "
            f"processing={counts.processing}"
        )
        if batch.processing_status == "ended":
            return
        time.sleep(POLL_INTERVAL_SECONDS)


def collect_results(batch_id: str) -> dict:
    """Stream JSONL results and map by custom_id. Never index into an array."""
    results_by_id: dict = {}
    for result in client.messages.batches.results(batch_id):
        results_by_id[result.custom_id] = result
    return results_by_id


def main():
    if len(sys.argv) != 2:
        print("Usage: python batch_extract.py <contracts-dir>")
        sys.exit(1)

    contracts_dir = Path(sys.argv[1])
    documents = {p.stem: p.read_text() for p in sorted(contracts_dir.glob("*.txt"))}
    print(f"Submitting batch of {len(documents)} contracts...")
    batch_id = submit_batch(documents)
    print(f"  batch_id={batch_id}")

    print("Polling for completion (most batches finish in under an hour)...")
    wait_for_batch(batch_id)

    print("\nCollecting results...")
    results = collect_results(batch_id)

    succeeded = []
    failed = []
    for custom_id, result in results.items():
        if result.result.type == "succeeded":
            msg = result.result.message
            tool_use = next(b for b in msg.content if b.type == "tool_use")
            succeeded.append((custom_id, tool_use.input))
        else:
            failed.append((custom_id, result.result.type, result.result))

    print(f"\nSUCCESS: {len(succeeded)} / {len(results)}")
    for custom_id, payload in succeeded:
        print(f"\n--- {custom_id} ---")
        print(json.dumps(payload, indent=2, default=str))

    if failed:
        print(f"\nFAILED: {len(failed)}")
        for custom_id, type_, _ in failed:
            print(f"  {custom_id}: {type_}")
        print("\nRetry pattern: rebuild a new batch from these custom_ids only.")


if __name__ == "__main__":
    main()
