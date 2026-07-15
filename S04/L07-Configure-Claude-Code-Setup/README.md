# Configure a Project's Claude Code Setup — End-to-End

A small Flask + Terraform project shown in two states.

## Layout

```
before/    The project as you'd inherit it — bloated CLAUDE.md,
           no other Claude Code config.

after/     Same project, properly configured:
             CLAUDE.md       lean, cross-cutting only
             .claude/
               settings.json defaultMode: plan + permissions + hook wiring
               rules/
                 python.md      paths-scoped to *.py
                 terraform.md   paths-scoped to *.tf
                 git.md         unconditional
               skills/
                 review/
                   SKILL.md     code review workflow
                   checklist.md supporting file
               hooks/
                 audit-bash.py  PreToolUse hook — audits every Bash call,
                                denies patterns permissions.deny can't easily
                                express (piped downloads, chmod 777, dd, etc.)
               logs/
                 bash-audit.log JSON-lines audit trail (created on first run,
                                gitignored)
```

## Walkthrough order

1. `before/CLAUDE.md` — read it. Notice the bloat. Eight topics in one file.
2. `after/CLAUDE.md` — read it. Five lines. Cross-cutting only.
3. `after/.claude/rules/*.md` — each topic in its own file, path-scoped.
4. `after/.claude/skills/review/SKILL.md` — the code-review workflow as a skill.
5. `after/.claude/settings.json` — `defaultMode: plan`, an explicit allow-list,
   AND a `hooks.PreToolUse` entry wiring in `audit-bash.py`.
6. `after/.claude/hooks/audit-bash.py` — the PreToolUse hook. Read the
   docstring. This is the Root Cause Bias in code — patterns like piped
   downloads and permissive chmod that a static glob list can't express
   go here, deterministic, before the tool call reaches the shell.

## Verify it works

In the `after/` directory:

```bash
claude /memory
```

Confirms which memory files load at session start versus on file read.

To exercise the hook end-to-end, ask Claude to run a `sudo` command or a
`curl … | bash` pipeline in the after/ project. The hook will block it and
Claude will see the reason string. Every Bash call — allowed or denied —
lands in `.claude/logs/bash-audit.log` for later review.

## References

- docs.claude.com/en/docs/claude-code/memory
- docs.claude.com/en/docs/claude-code/skills
- docs.claude.com/en/docs/claude-code/permission-modes
- docs.claude.com/en/docs/claude-code/hooks
