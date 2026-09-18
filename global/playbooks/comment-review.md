# Comment review

The pass over a change's comments and docstrings. `build.md` step 6 runs it after the fix loop converges, never in the same turn as a review round.

## Dispatch

1. Run the prose-reviewer (Task, `subagent_type: prose-reviewer`) in diff mode on the diff, scoped to code comments and docstrings, excluding `docs/designs/**` — design docs get their own pass at `design-doc.md` §G4.
2. Ask whether to run a Codex one alongside (`~/.claude/playbooks/codex.md` Pick).
3. Ask whether to run the comment-reviewer alongside (Task, `subagent_type: comment-reviewer`, same input; it pins its own model + effort). It skips `docs/designs/**` itself.

2 and 3 are evaluation phase: opt-in per pass, alongside the prose-reviewer, never instead of it, until the evaluation ends.

Apply the findings and rewrites you judge right. Re-run the pass after any later change to the code.

## Unsupported files

The comment-reviewer's report opens with a "not reviewed (no extractor)" line when the diff changed a file its tool has no scanner for. Ask the human per file type:

1. Add the extension to `SILENT` in `~/.claude/tools/comment-lint/comment_lint/extract.py` — the file carries no code comments.
2. Add a scanner there — a hash-comment or C-style type is one entry in `SUPPORTED`; anything else is a new block function.
3. Leave it.

Apply 1 or 2 through the symlink, and say it's an uncommitted change to the global config.

## Report

`build.md` step 8 carries the skipped findings as usual. When the comment-reviewer ran, add the evaluation table from `codex.md` with columns prose-reviewer / comment-reviewer; when Codex ran, its own.
