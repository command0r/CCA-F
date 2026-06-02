# Git conventions

(No `paths:` frontmatter — these rules load at every session start.)

- Conventional commits: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`.
- Branch naming: `feature/<ticket>-<slug>`, `fix/<ticket>-<slug>`.
- PRs require one approval, all CI green, no merge conflicts.
- Squash-merge to `main`. No merge commits, no rebase-merge.
- Tag releases with `v<major>.<minor>.<patch>`. Semantic versioning.
- Never force-push to `main` or release branches. Force-push to feature branches OK.
- Sign all commits with GPG. Unsigned commits rejected at branch protection.
