---
description: Worktree-backed bug fix — diagnose, prove the cause with a failing test, build, wrap-up.
argument-hint: <bug>
---

# /fix

After every commit and every conversation compaction, re-read this `/fix` skill before deciding next steps.

A bug fix: `/dev`'s pipeline with a diagnosis in place of its Plan. Read each playbook in full, and only when entering its step. If a session dies mid-way, `/resume` in Claude Code restores the conversation.

1. **Start** — settle the slug, create + enter the worktree and run the toolchain check, all per `~/.claude/playbooks/worktree.md` (Create + enter). The pipeline runs inside `.claude/worktrees/<project>/` on `eng/<project>`.
2. **Diagnose**
   1. Investigate until you can name the cause.
   2. Prove it with a test that fails because of it.
   3. Report in one message: the cause, the evidence, and the fix plan in the shape of `/dev`'s inline plan (files to touch, tests, the shape of the change). Without a failing test, say so, call the cause a hypothesis, and ask whether to (a) fix it and keep logging that would catch a recurrence, or (b) ship the logging alone and wait for the next occurrence.
   4. On her go → 3. If she drops the fix, discard the worktree per `worktree.md` (Discard).
3. **Build** — `~/.claude/playbooks/build.md` with the plan and the failing test.
4. **Wrap-up** — `~/.claude/playbooks/wrap-up.md`, with a `/dev` project's steps.

## Workflow-lessons list

Append *generalizable* workflow improvements to `docs/designs/<project>/workflow-lessons.md` (create on first entry), per `~/.claude/playbooks/workflow-lessons.md`. Nothing generalizable → no file.
