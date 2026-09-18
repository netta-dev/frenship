# Coding conventions (universal)

Write as a senior SWE: idiomatic, well-factored, tested.

## Preferences

- In artifacts a project *produces* (shipped playbooks/code/docs, not its own design docs), describe mechanisms generically — never bake in the producing project's phase numbers (`Phase 3 does X`).
- Prefer more, smaller single-responsibility files over one dense file (e.g. a `fakes/` package over one `fakes.py`).
- Never promote your own private to public just to test it — test through the public caller. When the code delegates into a framework default, stub the *external* collaborator and assert the public behavior.
- Early return when nested code is 3× longer than guard logic.
- Public methods (static methods, public getters/setters) at top of class; private at bottom.
- Don't duplicate logic — copies drift; bug fixes miss the copy. Extract at 2–3 sites — at 2 when the duplication carries a non-trivial shared invariant, drift risk is high, or a 3rd site is imminent. This overrides the built-in *three similar lines is better than a premature abstraction*, which sets the bar too high for a shared invariant.

## Comments

A comment must save a competent engineer, working here under time pressure, from digging elsewhere or breaking something. Default is no comment.

- First try to make the comment unnecessary (rename, extract). Comment: constraints, rationale, traps.
- Split a file or a method rather than using section dividers.
- Public method docstring: what a caller needs — contract, plus precision the signature lacks (units, bounds, ownership).
- Class/file comment: role in the system, cross-method invariants, lifecycle.
- A comment lives once, next to the code that would invalidate it.
- A reviewer's question resolves to the LLD, restructuring, or a comment if the answer is needed at the code.
- Comments obey `~/.claude/prose.md`.
- No tombstone comments — a comment describes present code, not what was removed or how it used to work. Same for dead deps: delete them; removal narration belongs in the design doc.
- In over-commented code, bring the area you're working in to this bar. Delete unnecessary comments.
- A file's existing comment density is not a precedent — match this bar, not the file.

Workspaces may add their own at `.claude/context/conventions.md`; those layer on top and override where conflicting.
