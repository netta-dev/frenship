# Iterative review

Convention for the propose → human-reviews → revise loop on a shared markdown working file (inbox, wrap-up scratch list, design review, anywhere a list of items needs collaborative resolution).

## Item shape

Each addressable item:

1. Brief description (or body).
2. Optional blockquote with the proposer's wording verbatim.
3. One or more resolution checkboxes:

`- [ ] Resolution: [STATUS — ]<details / wording>`

Multi-resolution items allowed — each its own `- [ ]` line. The human ticks independently; Claude applies each on its own.

Checkboxes belong to the human — Claude never ticks (or unticks) `[x]`, even after applying a resolution.

Two ticked states: `[x]` applies the resolution as written; `[-]` skips it and the item retires with no action. Both count as resolved.

## Status keywords

Universal:
- *(no prefix)* — apply as proposed (default).
- `SKIP — <reason>` — won't apply. `[-]` in the box is the tickable form, no reason needed.
- `DEFER — <reason>` — too big for inline; needs its own follow-up. Include an issue-ready **title + one-line description** so the human can paste it into her issue tracker.
- `FOLD — <reason>` — merged into another item.

Contexts may add their own status keywords on top.

## Resolution formatting

- Short resolutions: one line after `- [ ] Resolution: ...`.
- Long ones: sub-lettered points (`a.`, `b.`, ...) under the checkbox.

## Review loop

1. **Claude proposes** resolutions on items without a resolution line (or with an empty one).
2. **Human reviews** — ticks `[x]` on what she agrees with, `[-]` on what she's dropping, edits text she doesn't, adds inline `==†==[^N]` markers + footnote bodies at the bottom of the file for per-spot questions, may add wholly new items. The human removes her own `==†==[^N]` markers AND their footnote bodies together when she's satisfied; Claude doesn't touch either. **When revising a span of text that had a `==†==[^N]` marker, Claude keeps the marker visible — either inline on the revised text, or as a short placeholder like `==†==[^N] (addressed: <one-liner>)` if the original span was deleted.**
3. **Claude re-reads** the entire file (not just diff for new ticks — human edits and new items can appear anywhere), addresses footnotes in revised resolutions (referencing each by `[^N]`), revises unticked resolutions. Loop 2–3 until every item is `[x]` or `[-]`.
