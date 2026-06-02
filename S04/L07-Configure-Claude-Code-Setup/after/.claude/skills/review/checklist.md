# Code review checklist

## Blockers (must fix before merge)

- [ ] Secrets in code (API keys, passwords, tokens) — anywhere, any form.
- [ ] SQL string concatenation instead of parameterized queries.
- [ ] Missing input validation on a public endpoint.
- [ ] Bare `except:` clauses or broad `except Exception:` without re-raise.
- [ ] Terraform resource without required tags (`Environment`, `Service`, `ManagedBy`).
- [ ] Terraform module pinned to `main` or `latest` instead of a version tag.
- [ ] New dependency added without a pinned version + hash.

## Warnings (fix unless there's a documented reason)

- [ ] Public function without a docstring.
- [ ] Public function without type hints on parameters or return.
- [ ] New endpoint without a pytest test covering happy path AND failure path.
- [ ] Logging statement using `print` instead of the configured logger.
- [ ] Use of `os.path` instead of `pathlib.Path`.
- [ ] Pagination by offset instead of cursor.
- [ ] Terraform output without `description`.

## Notes (worth surfacing, not blocking)

- [ ] Functions over 30 lines — consider extracting.
- [ ] Files over 300 lines — consider splitting.
- [ ] TODO/FIXME comments without a ticket reference.
- [ ] Test naming that doesn't match `test_<function>_<scenario>_<expected>`.
