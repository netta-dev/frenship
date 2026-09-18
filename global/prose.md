# Prose rules

Rules for all prose — chat, code comments, docs, commit messages.

P1. **Actor first** — subject–verb–object, no clefts or fronting:
   - ✗ "what the guard refuses is a call from any other state" → ✓ "the guard refuses a call from any other state"
   - ✓ "the clips are committed as audio" — passive is fine when the agent is uninteresting or unknown
P2. **Full sentences, no telegraphese**:
   - ✗ "ff-only merge, else abort" → ✓ "Merge fast-forward only; otherwise abort."
P3. **Plain words, no one-off coinages**:
   - ✗ "this part records the kept negatives" → ✓ "this part restates facts earlier write-ups got wrong"
P4. **No personification of abstractions**:
   - ✗ "the function wants to be a class" → ✓ "the function should be a class"
   - ✗ "the alias earns its place" → ✓ cut, or "the alias saves typing"
P5. **No "worth x"**:
   - ✗ "worth not confusing" → ✓ "don't confuse"
   - ✗ "it's worth noting that X" → ✓ "X"
P6. **No no-negation**:
   - ✗ "A swipe fires no onTap" → ✓ "A swipe doesn't fire onTap"
   - ✗ "The icon carries no text" → ✓ "The icon is unlabelled"
P7. **No empty intensifiers** — actually, really, genuinely, simply, just, clearly, obviously, very, fundamentally; emphatic reflexives; importantly, notably:
   - ✗ "criteria that lawyers themselves define" → ✓ "criteria that lawyers define"
P8. **No overstated absolutes**:
   - ✗ "it never re-asks" → ✓ "it won't re-ask"
P9. **No negation-for-emphasis** — don't reject an alternative nobody assumed:
   - ✗ "configuration, not re-architecture" → ✓ "configuration"
P10. **Assertions, not rebuttals** — don't correct a mistake the reader hasn't made:
   - ✗ "`on_force_flat` is *not* the silent-return site — it raises" → ✓ "`force_flat` returns silently; `on_force_flat` raises"
P11. **Distinguish pairs symmetrically** — one sentence per difference, both sides named:
   - ✗ "the flush path is not where batching happens — ingest batches" → ✓ "Ingest batches; flush writes one record at a time."
P12. **No rule-of-three padding** — list only the items that carry information:
   - ✗ "simpler, cleaner, and more maintainable" → ✓ "simpler"
P13. **No emphasis jargon** — well-defined seam, the key insight, a real X:
   - ✗ "the well-defined seam between the two" → ✓ "the boundary between the two"
P14. **Omit what the reader can infer** — justifications, restatements, illustrative examples when the why is plain; keep *when-to-apply* heuristics:
   - ✗ "Use `git -C` (so the command runs against the right repo even when cwd is a worktree)" → ✓ "Use `git -C`"
