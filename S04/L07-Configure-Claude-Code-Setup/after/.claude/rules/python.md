---
paths:
  - "**/*.py"
---

# Python conventions

- Python 3.11+. Type hints on every function signature.
- Format with `black --line-length 100`. Lint with `ruff check`.
- Prefer dataclasses over plain dicts. Use `frozen=True` when immutable.
- Imports grouped: stdlib, third-party, local — blank line between groups.
- Docstrings: Google style, two-line minimum on public functions.
- Use `pathlib.Path` over `os.path` for filesystem operations.
- No bare `except:` clauses — catch a specific exception type.
- Use `logging` over `print`. Logger configured in `app/logging_config.py`.

## Flask specifics

- Blueprints for grouping routes by domain — one blueprint per resource.
- Request validation with Pydantic models. Never trust raw JSON.
- Error responses follow RFC 7807 problem-detail format.
- Pagination is cursor-based, not offset. Default limit 50, max 200.
- Health check at `/healthz` returning 200 when DB connection works.

## Testing

- Unit tests in `tests/unit/`, integration in `tests/integration/`.
- Pytest fixtures over `setUp`/`tearDown`.
- Naming: `test_<function>_<scenario>_<expected>`.
- Mock external services with `pytest-mock` — never hit real APIs.
- Coverage threshold: 80% line, 70% branch. Enforced in CI.
