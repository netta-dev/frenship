# Personal CLAUDE.md

## Human

- When you need to refer to me in 3rd person (e.g. in a doc) use "the human" not "the user", and she/her not they/them (otherwise use "you" normally when talking to me)

## Code

- Bug fix: failing test first (red → fix → green); if a test isn't practical, say so.

## Aliases

Shortcuts I type; when I do, apply the expansion:
- `ctr` — present the options with pros, cons, and tradeoffs + a recommendation (with refs, per Lists).
- `cxp` — explain more simply and in plainer language; provide more context; add a worked example if it aids understanding; if there's a decision for me, ctr.
- `crd` — redo your last message with refs where missing, per Lists.
- `cws` — do a web search.
- `qq <question>` — answer the question only; no edits or other actions.
- `cai` — I track work in an external issue tracker; write the action item as an issue: one-line title + a short description I can paste in.
- `crc <reply>` — I accept all your recommendations except what's in the reply (a bare `crc` accepts all).
- `lg` — looks good; proceed.

## Docs

- All prose — chat, comments, docs, commits — follows `~/.claude/prose.md`.
- CLAUDE.md prose extra-tight — loaded every prompt.
- Wrap `<placeholders>` in backticks in markdown — bare `<...>` renders as broken HTML in Obsidian.
- Reflow `.md` prose to one line per paragraph — never hard-wrap to a column width.
- Don't reference transient (e.g. `design-stash`) or untracked files from committed docs or code comments.

## Git

- `git add -N <file>` immediately after creating any file you'll commit — so `git diff` shows it.

## Lists

**Addressable lists**: Anything I might reply to (questions, options, findings, scratch items) gets a ref I can use **unambiguously**: `3`, `B11`, `A22a`. Don't use the letter O in a ref.
