# HLD — High-Level Design

Produce a phased design doc from brainstormed requirements.

Authoring craft, diagrams, companion-doc rules, and the shared design-review loop: `~/.claude/playbooks/design-doc.md`.

## Research

Read `~/.claude/conventions.md` and any `.claude/context/*.md` for architecture, conventions, tooling. If the project is an arch-doc milestone: also read the milestone's section, any design-stash sections tagged for it in `docs/designs/design-stash-<arch-project>.md`, and the use-cases entries tagged for it in `docs/designs/use-cases-<arch-project>.md`. Either way, read the workspace's future-improvements doc `docs/designs/future-<workspace>.md` — check whether any deferred idea is now in scope.

## Companions

Engineer-tier paths: stash at `docs/designs/<project-name>/design-stash.md`, beside the HLD; use cases at `docs/designs/use-cases-<project-name>.md`, the arch project's if this is a milestone, or the workspace's existing governing doc for a project inside an existing system. Append the brainstormed behavioral scenarios to that doc now; create `use-cases-<project-name>.md` only for a new standalone system; with no governing doc, keep them in `## Requirements`.

On HLD approval, tag each stash section `[→ phase N]` / `[→ cross-cutting]`.

## Output

Write at `docs/designs/<project-name>/hld-<project-name>.md` (kebab-case). Use template below; delete italicized instructions, replace placeholders. Then alternatives + design review (below), present for approval. On approval: set `**Status**: HLD committed`, then `git add <path> && git commit <path> -m "<project-name>: hld"`. Each phase gets an LLD at `docs/designs/<project-name>/lld-<N>-<slug>.md` via `/engineer`.

## Alternatives, then design review

Run `~/.claude/commands/optioneer.md` — alternatives land under their **Key decisions** entry — then `~/.claude/playbooks/design-doc.md` §G, doc type `hld`. Then present for approval.

## Effort table defaults

Fixed rows: `HLD` 10% (includes brainstorm), `Wrap-up` 5%, `Unexpected` 20%. Phases share the remainder (100 − 10 − 5 − 20 = 65%) split proportionally.

**User-facing phases.** Phases that produce user-visible changes at runtime typically consume more total effort than code-only phases of equivalent implementation scope — human review (visual + functional play-around) catches bugs and edge cases that code review alone misses, and any AI ux-review adds time. Budget roughly **1.5×** the share such a phase would otherwise get based on implementation alone.

**Mid-project new phase.** When a new phase is inserted after the HLD is committed, take its % from the existing planned phases (proportionally). Never touch `Unexpected` — that's slack for the *next* surprise, not for re-planning.

---

## Template

~~~markdown
# <project name>

*Italics = author instruction, delete when filling in. Plain = example/placeholder, replace.*

**Last reviewed**: YYYY-MM-DD
**Status**: HLD (in progress)
**Companions** *(create on first use; for a milestone, use-cases points to the arch project's; future is always the workspace's)*: [design-stash](design-stash.md) · [use cases](../use-cases-`project`.md) · [future](../future-`workspace`.md)

## Overview

1–3 paragraphs: what, why now, shape. Enough to orient reader/future-you.

## Key decisions

*Cross-cutting only.*

- **Decision as statement.** Short support if needed.
  - Why. 1–2 sentences: tradeoff, alternative, non-obvious motivation.

> [!example]- **Alternatives considered** — option A, option B (decision as statement)
> Option A — why it lost. Option B — why it lost. One line each.

- **Another decision.** Statement.
- **Decision with tradeoff.**
  - X over Y because Z. Y better at A, worse at B; B matters more.

## Design

*HLD-altitude structure — include each part only where it earns its keep; per-phase specifics go in the Phase entries below, not here. Skip the whole section for a trivial single-phase change.*

- **Components / topology** — new or changed pieces and how they connect.
- **Data model** — key entities and relationships introduced/changed.
- **Key flows** — the paths worth spelling out.

### Cross-cutting concerns

*Optional — skip if trivial. Concerns spanning phases (auth, observability, migration/back-compat, …) decided once here so a phase's LLD doesn't relitigate them.*

## Requirements

Numbered, one-line, from brainstorm.

1. Deliverable.
2. Another.

## Phases

*Commit-sized; one phase OK for tiny projects.*

### Phase 1 — Short title (N%)

*The title is canonical downstream: LLD filename `lld-<N>-<slug>.md`, phase commit subject `<project>: phase <N> — <title>`.*

1–3 sentences: what ships, what works after, what doesn't.

**Key decisions:**
- **Phase-local decision.** Rationale if needed.

**Key files:**
- `path/file.ext` (new/moved/modified—note)
- `path/other.ext`

**Open questions:**
*Not yet decided. Starting agenda for the LLD. Addressable.*

1. Question?
2. Another?

---

### Phase 2 — Short title (N%)

…same structure…

---

## Effort breakdown

| Stage | % |
|---|---|
| HLD | 10 |
| 1. … | N |
| 2. … | N |
| Wrap-up | 5 |
| Unexpected | 20 |
| **Total** | **100** |
~~~
