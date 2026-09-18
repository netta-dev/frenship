---
description: Commit changes via git, gated by lint and tests from capabilities.md.
---

# /commit

1. `git status`.
2. If diff touches code: run declared **lint** / **test** in `capabilities.md`; refuse on failure.
3. `git add -A` for untracked/missing files (ignore stray build artifacts, caches, secrets via `.gitignore`). Don't use `-X` or partial path lists to skip tracked-modified files — if one genuinely doesn't belong, ask.
4. If user-facing: propose `changelog` entry (under `## Unreleased`) and `user_guide` edits if declared.
   - `Fix:` lines describe behavior present in a previous release that's now corrected. Bugs introduced and fixed *during* a feature build don't belong. Audit: "would a user upgrading from the previous release notice this difference?"
5. `git commit` with a meaningful message. Subject is one line; multi-line body OK after a blank line.
   - **In an active mid-`/engineer` project** (the current branch is `eng/<project>` and `docs/designs/<project>/hld-*.md` has an incomplete `Status:`; on a main checkout, the incomplete HLD of the project being worked, if any): subject is `` `<project>: <stage> — <desc>` `` where stage ∈ `{hld, phase N, unexpected, wrap-up}`; for `phase N`, `<desc>` is the title verbatim from the HLD phase heading. Pick the stage by what the commit *contains*, not the current phase — a fix to phase 6's script made during phase 8 is `phase 6`. If a change spans stages, keep one commit labeled by the current phase and mention the other stages' content in the body. Unexpected = catch-all for work outside any labeled phase.
   - **No active project** (including any `/dev` project): plain subject — just `` `<desc>` ``. No project or workspace prefix.
