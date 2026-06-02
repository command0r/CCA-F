# users-api — project instructions

## Overview

This is a Flask-based user management API backed by Postgres in production and SQLite in development. Terraform manages the S3 bucket and IAM policy for user-uploaded avatars. Deployment runs on AWS ECS Fargate behind an ALB.

## Python style

- Python 3.11+. Use type hints on every function signature.
- Format with `black --line-length 100`. Lint with `ruff check`. No exceptions.
- Prefer dataclasses over plain dicts for structured data. Use `frozen=True` when the data shouldn't mutate.
- Imports grouped: stdlib, third-party, local — separated by blank lines.
- Docstrings: Google style, two-line minimum. Document every public function.
- Use `pathlib.Path` over `os.path` for filesystem operations.
- No bare `except:` clauses. Always catch a specific exception type.
- Use `logging` over `print`. Configure logger in `app/logging_config.py`.

## Flask conventions

- Blueprints for grouping routes by domain. One blueprint per resource.
- Request validation with Pydantic models — never trust raw JSON.
- Error responses follow RFC 7807 problem-detail format.
- All endpoints return JSON. No HTML rendering.
- Use Flask's `before_request` for auth checks, not decorators on every route.
- Pagination via cursor-based, not offset. Limit defaults to 50, max 200.
- Health check at `/healthz`, returns 200 if DB connection works.

## Terraform conventions

- Resource naming: `<env>_<service>_<resource_type>`. Example: `prod_usersapi_bucket`.
- All modules pinned to a version tag — never `main` or `latest`.
- State backend is S3 + DynamoDB lock. Never local state, even for testing.
- Outputs typed and documented. Use the `description` field on every output.
- Variables declared with `type` and `description`. Mark sensitive variables.
- Use `terraform fmt` before commits. CI rejects unformatted code.
- Tag every resource with `Environment`, `Service`, `ManagedBy: terraform`.

## Git workflow

- Conventional commits: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`.
- Branch naming: `feature/<ticket>-<slug>`, `fix/<ticket>-<slug>`.
- PRs require one approval, all CI green, no merge conflicts.
- Squash-merge to main. No merge commits, no rebase-merge.
- Tag releases with `v<major>.<minor>.<patch>`. Semantic versioning.
- Never force-push to main or release branches. Force-push to feature branches OK.
- Sign all commits with GPG. Unsigned commits rejected at the branch protection layer.

## Testing patterns

- Unit tests in `tests/unit/`, integration tests in `tests/integration/`.
- Use pytest fixtures over `setUp`/`tearDown`.
- Test naming: `test_<function>_<scenario>_<expected>`. Be specific.
- Mock external services with `pytest-mock`. Never hit real APIs in tests.
- Integration tests use real Postgres in Docker, not SQLite-in-memory.
- Coverage threshold: 80% line, 70% branch. CI enforces.
- Slow tests marked `@pytest.mark.slow`, excluded from default runs.

## Security rules

- Never commit secrets. Use AWS Secrets Manager for production, `.env` for local.
- All dependencies pinned with hashes in `requirements.txt`. Use `pip-compile`.
- Run `safety check` and `bandit` in CI. Block merges on high-severity findings.
- Input validation on every endpoint. Never trust client data.
- SQL via parameterized queries only. No string concatenation.
- Avatars uploaded to S3 — validate file type by magic bytes, not extension.
- Rate-limit API endpoints with Flask-Limiter. Default 100 req/min per IP.

## Deployment notes

- ECS Fargate task definition in `infra/ecs.tf`. Memory 1GB, CPU 0.5 vCPU.
- Health check path `/healthz`, threshold 3 consecutive failures.
- Blue/green deployment via CodeDeploy. 10-minute soak before full shift.
- Logs to CloudWatch. Structured JSON via `python-json-logger`.
- Metrics to CloudWatch custom namespace `users-api`. Track p50/p95/p99 latency.
- Dead-letter queue on SQS for failed events. Alert if DLQ depth > 0.
- Rollback automatic on health check failure during deploy. Manual rollback via `aws deploy stop-deployment`.
