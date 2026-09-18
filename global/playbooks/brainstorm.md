# Brainstorm

Explore a project idea before planning. No design doc, code, or file edits — except the design-stash and use-cases captures below.

## Research

Read `.claude/context/` if present: `conventions.md` (principles), `capabilities.md` (declared tooling; for UI with visual testing, check if running or launch it + screenshot). Read user-facing guides for current behavior. Web-search analogues when useful.

## Discussion

Present options with tradeoffs. Ask clarifying questions. Keep it conversational—the human is thinking aloud. For UI/UX, critique honestly as a senior designer: design principles, accessibility, edge cases.

## Capture low-level details

Low-level details (implementation, paths, phrasing) come up — follow the human's lead and discuss them if she wants, but don't drive the brainstorm down there yourself. When that thread wraps, offer to stash it so it's not lost: "Want me to note that for the relevant HLD section?" — for `/dev`, "Want me to note that for the plan?" On approval, add to the project's design-stash file (`docs/designs/<project-name>/design-stash.md`, create if missing). At HLD time, surface it so questions land as open questions under the right phase; at `/dev` plan time, fold it into the plan.

Behavioral scenarios discussed (exact system response to a specific situation) → carry them into the requirements list below; the design-doc step appends them to the governing use-cases doc.

## Output

When the human's ready to move forward, crystallize agreed requirements as a concise numbered list. Input to the HLD stage, or to `/dev`'s plan.
