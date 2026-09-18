# Wrap-up

Runs after the last phase commits, as `/engineer`'s final step — and after the change commits, as `/dev`'s. Steps that apply only to an HLD project say so.

## 1. Context sweep

Walk project changes since start: `git log <hld-commit>..HEAD --stat`. A `/dev` project has no HLD commit, so anchor on the branch instead. In a worktree: `git log "$(git reflog show --format=%H eng/<project> | tail -1)"..HEAD --stat`; if the reflog is empty or the worktree was recreated from a remote, anchor on the DD's add commit (`git log --diff-filter=A -- <dd-path>`); with no DD, ask the human for the range. In a main checkout, the project began at Setup's root commit, so walk the whole history: `git log --stat`. Edit if warranted (create files if needed):

- `CLAUDE.md` — new critical rules, stack changes, ops quick-ref?
- `.claude/context/architecture.md` — new subsystems, moved boundaries, new top-level components? Keep it high-level: a component/boundary map, not a per-feature/widget/impl changelog.
- `.claude/context/conventions.md` — new conventions surfaced during review/implementation?
- `.claude/context/docs.md` — new guides added? Obsolete pointers to drop?
- `.claude/context/capabilities.md` — new tooling (lint/test/visual-testing/etc.)?
- `docs/designs/architecture-<arch-project>.md` (milestone projects only) — mark this milestone delivered and reconcile drift (components, boundaries, decisions) against what shipped. The arch doc is the living system reference (§6).

**Don't document the self-evident.** If a behavior is plain from a glance at the code, don't write it down. These files are for the non-obvious — gotchas, conventions, ops paths, things future-you would not reconstruct from reading the source. Especially `CLAUDE.md`: it loads on every prompt; feature/architecture descriptions don't belong there even when non-obvious — those go in `architecture.md`.

## 2. Open questions + design-stash + future leftovers

For an HLD project, walk unresolved open questions in each phase; move resolved ones into the phase's key decisions (Overview if cross-cutting); drop anything no longer relevant. Then, in every project, walk unconsumed items in `docs/designs/<project-name>/design-stash.md` — integrate, re-home, or drop each; the file should end empty or deleted. Finally, walk the workspace's future-improvements doc `docs/designs/future-<workspace>.md` — prune items this project shipped (no longer "future"); leave the rest. Don't delete the file; it's a living doc.

## 3. Workflow-lessons promotion

The doc is a **promotion queue**, not a project retro (`docs/designs/<project-name>/workflow-lessons.md`; pre-rename projects: `lessons.md` / `scratch.md`). No file → nothing to sweep, skip to §4. Otherwise sweep it in two passes.

**Pass 1 — prune to generalizable candidates.** Delete anything that isn't a candidate workflow change: per-step "None"/narrative recaps, and findings already fixed in code that surface no *process* lesson (those live in the code + design doc). Drop now-empty sections.

**Pass 2 — resolve every survivor.** Each is one addressable item with exactly one `- [ ] Resolution:` line — add one to any item missing it (items with *no* resolution line count, not just empty ones). Propose resolutions per `~/.claude/playbooks/workflow-lessons.md`: a concrete generalizable change or `SKIP`, never a fix status (`Fixed`/`Done`/`Refactored` is not a resolution). Leave every box unticked (the human ticks). Review loop per `~/.claude/playbooks/iterative-review.md`.

Wrap-up-specific status keywords (additional to the playbook's set):
- *(no prefix)* — apply locally (workspace `CLAUDE.md`, `.claude/context/*`, etc.).
- `HANDOFF — <reason>` — global edit (`~/.claude/...`). On approval, append to your global config's inbox under a new section for this project — follow the **TEMPLATE** at the top of that file.

The sweep isn't done until every approved `HANDOFF` is appended to the inbox and every item is `[x]` or `[-]`.

For skipped review findings specifically, also look for generalizable patterns — categories of things the reviewer shouldn't have flagged in the first place. Propose `HANDOFF` "don't flag" rules for `~/.claude/agents/reviewer.md` when a pattern covers multiple skipped findings or reflects a stable preference.

## 4. Anything else?

Ask: "Anything else to address before we wrap up?" Handle whatever comes up. Changes get picked up in the next commit.

## 5. HLD sync + final progress

HLD projects only — a `/dev` project has no phases, skip to §6. Append each phase's commit hash to its heading — `### Phase N — Title (X%) · <shorthash>`. Use the `phase N:` commit; ignore straggler/workspace commits.

Show a final progress line — **`All phases + wrap-up complete`**

## 6. Status update + archive

If a design doc exists (HLD or DD), edit its `Status` line to `Project complete`. Then, if `docs/designs/<project-name>/` exists (an inline-plan `/dev` project may have none), `git mv docs/designs/<project-name> docs/designs/done/<project-name>` (step 7's commit picks it up) — `docs/designs/` root keeps only arch docs and in-flight projects. Arch docs never move; they're the living system reference.

## 7. Commit

If steps 1–6 produced changes, follow `~/.claude/commands/commit.md`. Message: `<project>: wrap-up — project complete`; a `/dev` project keeps a plain subject, e.g. `wrap up <what shipped>`.

## 8. Teardown (worktree projects)

If the project ran in a worktree, retire it per `~/.claude/playbooks/worktree.md` (Teardown): final merge of the wrap-up commit to main, then remove the worktree + branch + remote ref. Guarded — a no-op for a main-checkout project. Runs here, after the commit, so the worktree's transient state is drained before removal.

## 9. Release

Check for `.claude/commands/release.md` in the workspace. If found, ask the human whether to invoke. Otherwise skip.

## 10. Celebrate

For an HLD project, paste the HLD's `## Effort breakdown` estimate table into a text response so the human sees it inline. Then, in every project, send a short silly/fun/motivational message with emojis loosely related to what shipped, celebrating project-complete and telling the human to `/exit`. Programming humor, fun facts, puns, motivational quotes — whatever lightens the mood. Under 50 words for the celebratory bit.
