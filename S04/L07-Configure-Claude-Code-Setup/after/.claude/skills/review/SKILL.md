---
name: review
description: |
  ALWAYS use this skill when the user asks for a code review, PR review,
  or "look at this change." Runs the team's standard checklist from
  checklist.md. Do not perform code reviews directly without invoking
  this skill.
allowed-tools: Read, Grep, Glob
argument-hint: "[file-or-directory]"
context: fork
paths:
  - "**/*.py"
  - "**/*.tf"
---

# Code review workflow

Run through the checklist in `checklist.md` against the target file or
directory. Report findings grouped by severity (blocker, warning, note).

## Steps

1. Read the target — use `Read` or `Glob` to identify files in scope.
2. Walk the checklist top to bottom, one item at a time.
3. For each finding, cite the file + line and explain WHY it matters.
4. Summarize at the end — blocker count, warning count, note count.

Do not propose edits in this skill. Surface findings only — the user
decides what to act on.
