# Structured Extractor — Scenario 6

End-to-end structured extraction from contract documents using tool_use,
validation-retry, and the Message Batches API.

## Layout

```
contracts/           Five sample contract texts — varied formats and edge cases
schemas.py           Pydantic models for the extraction schema
validators.py        Semantic validation (the layer grammar enforcement can't see)
extract.py           Sync extraction with the retry-with-error-feedback loop
batch_extract.py     Bulk extraction via the Message Batches API
```

## Run

```bash
pip install -r requirements.txt
cp .env.example .env       # then edit .env with your real ANTHROPIC_API_KEY

# Sync — one contract, with the retry loop
python extract.py contracts/contract_004.txt

# Batch — all five contracts in one submission
python batch_extract.py contracts/
```

## What to look for

- `extract.py` on `contract_004.txt` — the line items don't sum to the stated total.
  Watch the retry trigger on the first attempt and Claude reconcile on retry.
- `batch_extract.py` — results are mapped by `custom_id`, never indexed.
  Per-request errors don't fail the batch.

## Notes

- `tool_use` with `strict: true` and forced `tool_choice` is the Scenario 6 canon.
- For pure extraction with no retries, `output_config.format` is the modern alternative
  (lecture 5.35).

## References

- docs.claude.com/en/docs/agents-and-tools/tool-use/strict-tool-use
- docs.claude.com/en/docs/build-with-claude/batch-processing
