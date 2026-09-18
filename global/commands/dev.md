---
description: Worktree-backed fix or small feature — brainstorm, one plan, build, wrap-up. No HLD, no phases.
---

# /dev

After every commit and every conversation compaction, re-read this `/dev` skill before deciding next steps.

A fix or small feature too small for an HLD: one worktree, one brainstorm, one plan (inline or a single design doc), one build, one wrap-up. Read each playbook only when entering that step — don't preload.

Out of scope: a change whose plan splits into phases or needs an architecture-level decision.

## Resume

1. Run `grep -L "^\*\*Status\*\*: Project complete" docs/designs/*/dd-*.md` to list mid-flight design docs (paths only).
2. **None**: a new project — run **New project** (below), then Pipeline A1 (Brainstorm).
3. **One**: read it, confirm "Resuming `<project>`: `<Status>`. Go?", then enter its worktree per `~/.claude/playbooks/worktree.md` (Resume entry — it reconciles a main-vs-branch `Status` lag and no-ops for a main-checkout project) and jump to the step matching `Status:` — `DD committed` → B; `Complete` → C. (`DD (in progress)` is never committed, so the grep can't see it.)
4. **Multiple**: list projects, ask the human to pick, then proceed as in (3).

Only a committed DD is a breakpoint; an inline-plan project is single-session by design. If a session dies mid-way, `/resume` in Claude Code restores the conversation.

## New project

Settle the slug, create + enter the worktree and run the toolchain check, all per `~/.claude/playbooks/worktree.md` (Create + enter). The pipeline runs inside `.claude/worktrees/<project>/` on `eng/<project>`; a git-less workspace runs in place.

## Pipeline

A. **Plan**
   1. **Brainstorm** — `~/.claude/playbooks/brainstorm.md`. Output: crystallized requirements. If abandoned, discard the worktree per `~/.claude/playbooks/worktree.md` (Discard).
   2. **Design** — first do `~/.claude/playbooks/lld.md` Process steps 3–7 as far as the change warrants (read context and code, verify every external API relied on, grep the readers of any field whose semantics change, screenshot the current UI state). Append the brainstormed behavioral scenarios to the workspace's existing governing use-cases doc; with no such doc, they stay in the requirements. Then:
      1. **Inline plan.** Present the plan as a numbered list of steps — files to touch, tests, the shape of the change — with its decisions called out. Fold in the design-stash items and any `docs/designs/future-<workspace>.md` item now in scope.
      2. **Doc or go.** Recommend one, with a one-line reason. Doc when the change spans subsystems, changes behavior someone else must review later, or the plan should outlive this chat. The human answers `go` or `dd`.
      3. **On `go`** — present the plan for approval; a clear yes → B.
      4. **On `dd`** — expand the plan into `docs/designs/<project>/dd-<project>.md` per `~/.claude/playbooks/lld.md` (the Write-the-plan rules and the Template's DD variant), `**Status**: DD (in progress)`. Then `lld.md`'s Alternatives-then-design-review section with doc type `dd`, and its Present-for-approval section. On approval: `**Status**: DD committed`; commit `docs/designs` alone — `git add docs/designs && git commit docs/designs -m "design doc for <desc>"`, the whole dir so the companions land and the tree is clean for the breakpoint — and integrate to main per `~/.claude/playbooks/worktree.md` (Integrate — doc-only). Then recommend continue vs. `/exit` + `/dev` resume, judged by context budget — the injected `Token usage: X/Y; Z remaining` signal if present, else files read and conversation length.
   3. **Setup** (one-off, if workspace lacks `.claude/context/`) — `~/.claude/playbooks/setup.md`; then re-run the toolchain check (`worktree.md` Create + enter, step 4), since Setup declares it.
B. **Build** — `~/.claude/playbooks/build.md` with the design (inline plan or DD) and status `Complete`. It ends with the change committed and integrated.
C. **Wrap-up** — `~/.claude/playbooks/wrap-up.md`. Its steps say which apply to a `/dev` project.

## Workflow-lessons list

Append *generalizable* workflow improvements to `docs/designs/<project>/workflow-lessons.md` (create on first entry), per `~/.claude/playbooks/workflow-lessons.md`. Nothing generalizable → no file.
