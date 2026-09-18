# Workflow-lessons

Shared rules for capturing and promoting **workflow lessons** — things that should improve the *workflow itself*: conventions, playbook/command edits, Claude settings. Used by `/architect` (lessons sweep before send-off), `/engineer` and `/dev` (lessons list during the run, promoted at wrap-up).

Not for one-off code fixes or project-specific notes — those live in the code and the design doc. A lesson earns a place here only if it generalizes.

## The doc

One per design run, addressable format, same naming convention as the other companions:
- Architect level: `docs/designs/workflow-lessons-<project>.md`
- Engineer/dev level: `docs/designs/<project-name>/workflow-lessons.md` (pre-rename projects: `lessons.md` / `scratch.md`)

Create on first entry; delete unused sections, add new ones as needed. Wrap-up / send-off reads it.

## What goes in

Candidate workflow improvements surfaced during the run:
- Human triage overrides (the human disagreed with a fix/skip decision).
- Approved-skipped review findings (intentionally unfixed — is there a class to stop flagging?).
- Deferred implementer observations.
- Anything the human catches in review that a process change could have caught first.

Add an item **only** when it's a candidate *generalizable* process change, with an empty `- [ ] Resolution:` line from the start. A finding just fixed in code, or a per-step "nothing to report," doesn't go here — this is a promotion queue, not a progress log.

## The resolution rule

Every resolution is a **concrete, generalizable workflow change** — or an explicit `SKIP`. Record the *process* change, not the one-off fix (the fix already happened in the code; the lesson is how to stop the whole class recurring).

- A resolution answers "how do we stop this class of issue recurring," as a concrete action: a new bullet in `.claude/context/conventions.md`, a playbook/command/agent edit, a Claude setting — or `HANDOFF` for a global (`~/.claude/...`) edit.
- For a finding the *human* caught in her review: the resolution must name the process/convention change that would have caught it first — not just "fixed it."
- No generalizable lesson? `SKIP — <why>`. Don't record a bare one-off fix as a resolution.
- A fix status is **not** a resolution: `Fixed` / `Done` / `Refactored` records the code change, not a lesson. Name the process change that stops the class recurring, or `SKIP` — if neither fits, the item doesn't belong here.
- **Never tick a box yourself** — both `[x]` and `[-]` are the human's, even after you've applied or promoted the resolution. Fill the `- [ ]` line and leave the box unchecked.

Status keywords + review loop: `~/.claude/playbooks/iterative-review.md` (universal `SKIP`/`DEFER`/`FOLD`). Promotion-specific keywords (`HANDOFF`, local-apply) are defined where the doc is swept (`wrap-up.md` §3, `/architect` lessons sweep).

## Template

~~~markdown
# <project-name> — workflow-lessons

## A. Human triage overrides

1. Atomic item.
   - [ ] Resolution:

2. Item with sub-points sharing one resolution.
   a. First sub-point.
   b. Second sub-point.
   - [ ] Resolution:

3. Resolved item (human-ticked).
   - [x] Resolution: the generalizing action — e.g. "add to `.claude/context/conventions.md`: 'Always X when Y'" — or `DEFER`/`SKIP`/`HANDOFF`/`FOLD` — <reason>. See `~/.claude/playbooks/iterative-review.md`.

4. Dropped item (the human ticked `[-]`).
   - [-] Resolution: SKIP — the proposal stays as written; the box retires the item with no action.

## B. Deferred implementer observations

## C. Human-review findings
~~~
