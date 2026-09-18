# Build

From an approved plan to a landed commit. `/engineer` runs it once per phase after the LLD; `/dev` runs it once after the plan. Loaded on demand at that point.

## Inputs from the caller

- The approved design: the LLD, or `/dev`'s DD or inline plan. It carries its own context; nothing else is passed down.
- The status to write at step 11 — `/engineer`: `Phase N complete`; `/dev`: `Complete`.

## Steps

1. **Provision** (worktree projects, first build/run only) — provision per `~/.claude/playbooks/worktree.md` (Provision). Sentinel-gated: a no-op on later runs and build-less repos; a main-checkout project has no worktree to provision.
2. **Implement** — `~/.claude/commands/implement.md`. Dispatches main-thread or subagent (with model) based on plan shape. Pass the design + mode `implement`.
3. **Reviewer** — Task, `subagent_type: "reviewer"`, model + effort per `~/.claude/playbooks/agent-pick.md`. Pass the design.
4. **Fix loop** — triage findings (must-fix, suggestion, nit). Fix by value/effort; no triage with the human mid-loop. For subagent fix passes, invoke `/implement` with mode `fix`. Re-run the reviewer — a **fresh** reviewer subagent each time (new Task invocation, not a SendMessage continuation), at the first reviewer's model + effort, passing it a short log of prior findings and their disposition (fixed / rejected, with the reason); fix passes reuse the implementer's pick — until a review returns no findings beyond your skips. Then run the **full** declared test suite (`capabilities.md`), not just the directly-touched suites — the change isn't done until full-suite green. Once the loop converges, *offer* one final pass by a fresh reviewer on Fable, effort per `~/.claude/playbooks/agent-pick.md`, and a Codex one per `~/.claude/playbooks/codex.md` (Pick); always ask, never auto-run.
5. **Orchestrator review** — review the full diff yourself against `~/.claude/agents/reviewer.md`'s axes before presenting; fix findings via `/implement`.
6. **Comment review** — `~/.claude/playbooks/comment-review.md`. Never dispatched alongside a review round; re-run after any later change.
7. **Visual review prep** — if the change is user-visible at runtime: (a) offer to restart/reload the apps listed in `.claude/context/capabilities.md`; (b) if `.claude/playbooks/ux-review.md` exists in the project, invoke `/ux-review` against the affected screens with target/scope/goal pre-filled from the change. Skip silently if not user-visible.
8. **Report** — present the **skipped** findings (intentionally unfixed) + relevant implementer observations + the evaluation report (`codex.md`) for any Codex pass, and `comment-review.md`'s when the comment-reviewer ran. Fixed findings aren't re-listed — they're in the diff she reviews at step 9. Nits are triaged/fixed by the orchestrator without surfacing them. Explicitly ask the human to approve the skips. Triage disagreements → the workflow-lessons list (`~/.claude/playbooks/workflow-lessons.md`). On approval, skipped findings → that list too.
9. **Human reviews code** — ask the human to review. For user-visible changes, also visually review the running app and play with the feature to find edge cases. Findings: fix if warranted *and* add to the workflow-lessons list.
10. **Human approval** — clear yes → proceed.
11. **Status update** — if a design doc exists, edit its `Status` to the caller's value.
12. **Commit** — `~/.claude/commands/commit.md`; the subject rule lives there.
13. **Integrate to main** — per `~/.claude/playbooks/worktree.md` (Integrate); guarded (a no-op for a main-checkout project).
