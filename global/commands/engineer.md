---
description: Orchestrate the engineering pipeline — brainstorm, HLD, phases, wrap-up.
---

# /engineer

After every commit and every conversation compaction, re-read this `/engineer` skill before deciding next steps.

Orchestrate the engineering pipeline. Single-session; walk the pipeline and let conversation hold state. Read each playbook only when entering that step — don't preload.

## Resume

Find a mid-flight project and resume:

1. Run `grep -L "^\*\*Status\*\*: Project complete" docs/designs/*/hld-*.md` to list mid-flight HLDs (paths only, no content loaded).
2. **None**: a new project — run **New project** (below), then Pipeline A1 (Brainstorm).
3. **One**: read that HLD, confirm "Resuming `<project>`: `<Status>`. Go?", then enter its worktree per `~/.claude/playbooks/worktree.md` (Resume entry) and jump to the step matching `Status:` (e.g., `HLD committed` → B1, the phase-1 LLD; `Phase 2 complete` → Phase 3 LLD; `Phase 3 LLD committed` → B2, the build playbook; `HLD (in progress)` → continue HLD). Resume entry reconciles a main-vs-branch `Status` lag and no-ops for a main-checkout project.
4. **Multiple**: list project names, ask the human to pick, then proceed as in (3).

## Milestone start

When invoked with an arch-doc milestone (e.g. `/engineer m2`, "engineer the referral milestone"): resolve it in `docs/designs/architecture-<project>.md` (ask which doc if multiple match), then run **New project** (below) before Brainstorm. Seed the brainstorm with the milestone's section (components in scope, open questions) plus any design-stash sections tagged `[→ <milestone>]` in `docs/designs/design-stash-<project>.md`.

## New project

For a new project (Resume found none) or a milestone start — **before Brainstorm** — settle the slug, create + enter the worktree and run the toolchain check, all per `~/.claude/playbooks/worktree.md` (Create + enter). The pipeline runs inside `.claude/worktrees/<project>/` on `eng/<project>`. Resume skips this — an in-flight project already has its worktree.

## Pipeline

A. **Plan**
   1. **Brainstorm** — `~/.claude/playbooks/brainstorm.md`. Output: crystallized requirements. If abandoned same-session before any HLD, discard the worktree per `~/.claude/playbooks/worktree.md` (Discard).
   2. **HLD** — `~/.claude/playbooks/hld.md`. Output: design doc at `docs/designs/<project-name>/hld-<project-name>.md`. On approval (after the playbook commits it), integrate the HLD to main per `~/.claude/playbooks/worktree.md` (Integrate) — doc-only, guarded (a no-op for a main-checkout project).
   3. **Setup** (one-off, if workspace lacks `.claude/context/`) — `~/.claude/playbooks/setup.md`; then re-run the toolchain check (`worktree.md` Create + enter, step 4), since Setup declares it.
B. **Build**, per phase in HLD order
   1. **LLD** — `~/.claude/playbooks/lld.md`. On approval the playbook commits + integrates it.
   2. **Build** — `~/.claude/playbooks/build.md` with the LLD and status `Phase N complete`. Ends with the phase committed and integrated.
   3. **Running stats** — Re-paste the HLD's `## Effort breakdown` table plus a progress line — **`Phases 1–N complete — X% complete`**, X = the HLD row's % + the sum of completed phases' %. Worked: HLD 10 + phases 1–4 summing 25 → "35% complete"; after the last phase, 10 + 65 = 75%.
   4. **Continue vs. fresh-session** — recommend whether to start the next phase in this context or `/exit` and resume fresh (Resume picks up from the `Status:` line). Lean toward a fresh session when context is getting tight — judge from the injected budget signal if present (`Token usage: X/Y; Z remaining`), else heuristics (files read, conversation length, phases done). Phase boundaries are clean cut-points.
C. **Wrap-up** (after the last phase) — `~/.claude/playbooks/wrap-up.md`.

## Workflow-lessons list

During the run, append *generalizable* candidate workflow improvements — triage overrides, skipped-finding patterns, deferred implementer observations, things the human catches in review — to `docs/designs/<project-name>/workflow-lessons.md` (create if missing), each with an empty `- [ ] Resolution:` line. Not every fixed finding: a fix with no process lesson stays in the code, not here. Wrap-up §3 promotes it. Doc shape, what-qualifies, and the resolution rule (a generalizable process change or `SKIP`, never a bare one-off fix): `~/.claude/playbooks/workflow-lessons.md`.
