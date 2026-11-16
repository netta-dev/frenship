---
description: Start a session — resume the project in flight, or recommend a pipeline for a brief.
argument-hint: "[<brief>]"
---

# /gm

Open your first reply with `gm` after an emoji you pick, also when a repo's file takes over.

1. If the repo has `.claude/playbooks/gm.md`, follow it instead of these steps.
2. List the projects in flight with the Resume greps of `/architect`, `/engineer`, and `/dev`.
3. Without `$ARGUMENTS`: if no project is in flight, ask for a brief. If one project is in flight, invoke its command; that command's Resume step picks it up. If several are, list each project with its command and ask which to resume.
4. With a brief: recommend `/fix` (a bug), `/dev` (a small feature or change with one plan), `/engineer` (a plan that splits into phases or needs an HLD), `/architect` (a new system's architecture), or no pipeline (a question or a small edit), and ask, recommendation first. Name any project in flight in the same question. On her pick, invoke that command with the brief.
