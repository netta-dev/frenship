# Comment review

The pass over a change's comments and docstrings. `build.md` step 6 runs it after the fix loop converges, never in the same turn as a review round.

## Dispatch

Stage the change (`git add -A`) before each pass, so the pass's edits are the unstaged diff.

1. Run the prose-reviewer on Codex, Sol (high), per `~/.claude/playbooks/codex.md` The call with `-s workspace-write`, in diff mode on the diff, scoped to code comments and docstrings, excluding `docs/designs/**`. Tell it to apply each finding's rewrite, editing comments and docstrings only.
2. Then run the comment-reviewer (Task, `subagent_type: comment-reviewer`) on the working tree, so it judges the comments with the prose pass's fixes in. It applies its own rewrites.

After each pass, read `git diff` and keep every edit unless it introduces a factual error or drops a fact the original comment carried; fix those hunks, then stage. A comment either pass deleted stays deleted; similar comments elsewhere in the file are never grounds to restore it.

Re-run the pass after any later change to the code.

## Unsupported files

The comment-reviewer's report opens with a "not reviewed (no extractor)" line when the diff changed a file its tool has no scanner for. Ask the human per file type:

1. Add the extension to `SILENT` in `~/.claude/tools/comment-lint/comment_lint/extract.py` — the file carries no code comments.
2. Add a scanner there — a hash-comment or C-style type is one entry in `SUPPORTED`; anything else is a new block function.
3. Leave it.

Apply 1 or 2 through the symlink, and say it's an uncommitted change to the global config.

## Report

`build.md` step 8 carries the skipped findings as usual, plus the comment-reviewer's **Still flagged after 5 attempts** list verbatim when it has one. A low per-rule figure in the comment-reviewer's flags is never a weak flag; the figures sum to 1 (`comment-reviewer.md` step 1).
