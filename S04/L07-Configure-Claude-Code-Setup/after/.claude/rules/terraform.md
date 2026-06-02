---
paths:
  - "**/*.tf"
  - "**/*.tfvars"
---

# Terraform conventions

- Resource naming: `<env>_<service>_<resource_type>` — example, `prod_usersapi_bucket`.
- All modules pinned to a version tag. Never `main` or `latest`.
- State backend is S3 + DynamoDB lock. No local state, even for testing.
- Outputs typed AND documented — `description` field on every output.
- Variables declared with `type` and `description`. Mark sensitive variables.
- Run `terraform fmt` before commits. CI rejects unformatted code.
- Tag every resource with `Environment`, `Service`, `ManagedBy: terraform`.

## Safety rules

- Never put credentials in `.tf` files. Use variables or remote secret stores.
- `terraform apply` is gated by approval — never auto-apply.
- `terraform destroy` requires explicit confirmation and a recent state backup.
