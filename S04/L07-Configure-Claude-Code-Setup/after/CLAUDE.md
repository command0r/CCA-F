# users-api

Flask user-management API, Postgres in prod, SQLite in dev. Terraform manages
the S3 avatars bucket and IAM. Deployed on AWS ECS Fargate behind an ALB.

Topic-specific conventions live in `.claude/rules/` and load when relevant:

- Python rules load on `*.py` reads.
- Terraform rules load on `*.tf` reads.
- Git rules always apply.

Code review workflow: type `/review` (see `.claude/skills/review/SKILL.md`).
