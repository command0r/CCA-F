# Configure a Project's Claude Code Setup — End-to-End

A small Flask + Terraform project shown in two states.

## Layout

```
before/    The project as you'd inherit it — bloated CLAUDE.md,
           no other Claude Code config.

after/     Same project, properly configured:
             CLAUDE.md       lean, cross-cutting only
             .claude/
               settings.json defaultMode: plan + permissions
               rules/
                 python.md      paths-scoped to *.py
                 terraform.md   paths-scoped to *.tf
                 git.md         unconditional
               skills/
                 review/
                   SKILL.md     code review workflow
                   checklist.md supporting file
```

## Walkthrough order

1. `before/CLAUDE.md` — read it. Notice the bloat. Eight topics in one file.
2. `after/CLAUDE.md` — read it. Five lines. Cross-cutting only.
3. `after/.claude/rules/*.md` — each topic in its own file, path-scoped.
4. `after/.claude/skills/review/SKILL.md` — the code-review workflow as a skill.
5. `after/.claude/settings.json` — `defaultMode: plan` plus an explicit allow-list.

## Verify it works

In the `after/` directory:

```bash
claude /memory
```

Confirms which memory files load at session start versus on file read.

## References

- docs.claude.com/en/docs/claude-code/memory
- docs.claude.com/en/docs/claude-code/skills
- docs.claude.com/en/docs/claude-code/permission-modes
