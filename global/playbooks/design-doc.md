# Design docs

Authoring craft and the shared review loop behind every design doc a human reads — architecture docs (`~/.claude/commands/architect.md`), HLDs (`~/.claude/playbooks/hld.md`), LLDs (`~/.claude/playbooks/lld.md`), `/dev` design docs (the DD variant in `lld.md`), and any one-off design write-up.

CLAUDE.md's writing rules apply to a design doc's prose too; this playbook adds what only a written doc needs.

## A. Audience model

1. Three readers, three channels: the main text serves the skimmer, footnotes serve the implementer, collapsible blocks serve the reviewer.

   | | main text | footnotes | blocks |
   |---|---|---|---|
   | skimmer | ✓ | — | — |
   | implementer | ✓ | ✓ | on demand |
   | reviewer | ✓ | some | ✓ |

2. **The main text is the contract.** Read it alone and you have every commitment the doc makes — requirement, constraint, decision, scope line. The other channels hold what a reader can skip and still be right: sourcing, elaboration, the *why*. Default is a plain sentence; a device earns its place by saving a detour.

## B. The three devices

Short rule: **parens for facts, footnotes for sources, blocks for reasoning.**

1. **Parentheses** — narrow, factual, and short enough to read faster than deciding whether to read it:
   - units, ranges, precision: "the retry budget (three attempts, exponential backoff)"
   - naming the thing just described: "the coordinator (`sync-worker` in the codebase)"
   - short qualifications: "all writes go through the primary (except the migration backfill)"
   - brief examples: "idempotency keys (e.g. the request UUID)"

   Misfiled if any of:
    1. Longer than the clause containing it.
    2. Contains a "because" — that's a rationale block squeezed into punctuation.
    3. Carries a binding caveat — parens signal "optional" to a skimmer, so promote it to a sentence.
2. **Footnotes** — material one audience wants that would stall the skimmer:
   - sourcing: the p99 figure, the incident this references, the benchmark, the RFC/spec section
   - definitions and term disambiguation: "we use 'session' in the auth sense here, not the analytics sense"
   - pointers: the API doc, the dashboard, the prior design doc
   - scope disclaimers: "this excludes the batch path, which is out of scope"
   - asides — trivia that would derail the sentence but that you can't bring yourself to cut

   Anchor a definition footnote at the term's first mention.
3. **Collapsible blocks** — reasoning. The heading is a typed prefix + the specific subject ("**Rationale** — why not shard by tenant ID"), never a bare "Details". The prefixes, with their callout types:
   - **Rationale** (`[!info]`) — why this decision, given the constraints
   - **Alternatives considered** (`[!example]`) — what else was on the table and why it lost
   - **Anticipated questions** (`[!question]`) — a reviewer's likely misreading, named and answered
   - **Context** (`[!note]`) — history, prior incidents, external forces that explain why the doc is shaped this way
   - **Evidence** (`[!abstract]`) — the itemized backing of a countable claim: grep results, tallies, member lists

   Syntax and placement:
    1. Obsidian-rendered repos: `> [!info]- **Rationale** — subject`, body lines prefixed `> `; the trailing `-` on the type folds it by default.
    2. `<details>` only in GitHub-first repos — several renderers close the HTML block at the first blank line, so a multi-paragraph body falls *outside* the fold.
    3. Don't nest a callout inside a list item; live-preview rendering breaks. Place it at top level directly after the item it backs, with the subject line naming that item.
    4. In an ordered list, keep writing each item's real number: the callout ends the list, so the next item starts a new one at whatever number you write.
4. A whole section can be one collapsible block when none of it binds the implementer (pure history, pure justification). If any part binds, that part stays in main text and only the reasoning folds.
5. **Place a block where the question arises, not where the answering fact lives.** A cross-reference like "the caller census counts these as SM call sites" defends the census — it belongs in an **Anticipated questions** block under the census, not appended to the far-away fact that backs it.

## C. Sentence-level rules

Every doc obeys `~/.claude/prose.md` (cite `P<n>`). Doc-specific rules, each with the ✗ shape it replaces and the ✓ rewrite:

1. **Content before provenance.** State the fact first; file its origin in a footnote or block.
   - ✗ "Carried over from the Q3 incident review: retries must be idempotent."
   - ✓ "Retries must be idempotent.[^1]" — footnote: "From the Q3 incident review."
2. **Symbols in prose, coordinates in footnotes.** The symbol (`Class.method`) rides in the sentence; the file/line coordinate goes to a footnote, one per claim carrying all its coordinates rather than one per coordinate. Coordinates stay inline in exactly two places: **edit instructions** (Files/Tests — the coordinate is the operand) and **evidence blocks** (grep results — the coordinates are the content). Docs only — in chat, `file.py:42` is clickable, so coordinates ride inline there.
   - ✗ "the abort resolves it (`executor.py:595`)"
   - ✓ "`Executor.on_abort_entry` resolves it[^abort-loc]" — footnote: "`executor.py:595`"
3. **Doc-process clauses fold, whatever their size.** Sentences about the document itself — approval scope, review conventions, playbook precedents — go to a **Context** block even at one clause; main text keeps what the *system* does. Diagnostic: process words in main text ("approval", "precedent", "recorded here", "per the playbook") mark a misfiled clause.
   - ✗ "The approved scope also includes, named here so approval covers all of it: …"
   - ✓ "The approved scope also includes: …" + a **Context** block: "none of these is named by a requirement; listing them here makes approval cover them."
4. **Three or more enumerated items become a numbered or lettered list.** Never bulleted (the house Lists rule); nest with ordered markers, indented 4 spaces per level so multi-digit parents render.
   - ✗ "the reader (updated in place), the writer — with its retry path — and the janitor (unchanged)" → ✓ one numbered item per component
   - ✓ "the four states: `FLAT`, `PENDING_ENTRY`, `LONG`, `PENDING_EXIT`" — a bare name-set with no per-item content stays inline
5. **Context before items.** One or two sentences before any list, naming the subject and why it matters. A list item is never the first place a concept appears.
   - ✗ "1. The handoff must be atomic. 2. The lease must not expire mid-handoff." (what handoff?)
   - ✓ "Two workers exchange the queue lease at rollover: 1. The handoff must be atomic. 2. …"
6. **References carry their gist.** Attach a two-to-five-word gloss to any reference the reader would otherwise have to dereference: requirement numbers, decision numbers, doc-section pointers, issue IDs. A pointer's wording must also exist at its target: "the two force-drop sites (Background)" fails if Background never uses that term — align the target's terminology, or carry the gist in a footnote instead of the bare pointer.
   - ✗ "as decision 4 requires"
   - ✓ "as decision 4 (startup reconcile owns belief) requires"
7. **No attribution.** Don't attribute a decision to anyone.

## D. Diagrams

Mermaid fenced blocks where they earn their keep; skip when prose covers it just as clearly. The three that usually earn it:

1. **Components / topology** — flowchart, in architecture *Key components* and HLD *Design*. Worth it when the change introduces or rewires components; put external actors and systems on the diagram's edges.
2. **Data model** — ERD, when entities and relationships are non-trivial. Skip when the data shape absorbs into the components section; per-stage schema deltas belong to that stage's doc, not the tier above.
3. **Key flows** — one sequence diagram per hot path, 1–3 max. Skip when the components diagram already makes the flow obvious.

A diagram and the prose beside it tell the same story; when they drift, one of them is wrong.

Prefer `flowchart TD`. Quote any node label containing `/`, `(`, `[`, `{` or `>` — unquoted they read as shape delimiters and the diagram fails to render: `Z["/engineer: settle the slug"]`.

## E. Templates and recurring blocks

Each playbook carries its own template; these conventions and block shapes are shared.

1. **Template conventions** — italics = instruction to the author, delete when filling in; plain text = example content or placeholder, replace with real content; drop any section that doesn't apply; compress semantically. A section still carrying italics or an unreplaced placeholder isn't written yet.
2. **Header block** (architecture, HLD, DD) — `**Last reviewed**: YYYY-MM-DD`, `**Status**: <pipeline step>`, `**Companions**: <links>`. Resume reads `Status`, so it advances in the same commit as the work it describes.
3. **Decisions block** — same shape at every tier (architecture *Key architectural decisions*, HLD *Key decisions*, LLD and DD *Resolved decisions*):
    1. Top level: the decision as a statement.
    2. Indented under it: the rationale, one or two sentences on the tradeoff or non-obvious motivation, included only when it isn't self-explanatory.
    3. Then an **Alternatives considered** callout (§B3) at top level directly after the decision — its summary line names the rejected options so nobody re-proposes one without opening the fold, and one line per option inside carries the reason it lost.

    Each tier holds only the decisions at its own altitude: the architecture doc project-level, the HLD cross-phase, the LLD its one phase. A decision that binds a single lower stage belongs to that stage's entry or its own doc.
4. **Stage entry** — an architecture milestone and an HLD phase share a shape:
    1. `### <Stage> N — Short title (N%)`.
    2. 1–3 sentences on what ships, what works after, and what still doesn't.
    3. The tier's specifics — milestone: components in scope, stack pieces introduced; phase: key decisions, key files.
    4. **Open questions**, addressable, as the starting agenda for the next tier's doc.

    The title is canonical downstream: its kebab-case slug names the next artifact (milestone → the `<project-name>` of its `/engineer` run; phase → `lld-<N>-<slug>.md`) and the title itself is the commit subject.
5. **Effort table** — one row per stage plus the tier's fixed rows, summing to 100.

## F. Companion docs

Four companions live beside a design doc, created on first use and linked from its `Companions` header line. The paths differ per tier; the rules don't.

1. **design-stash** — *destined* content awaiting its home: detail too low-altitude for the doc being written (worked examples, sample prompts, algorithm/schema specifics, cost math). Sections by topic, addressable, self-contained items, each tagged with its destination — `[→ §<section>]` (a later section of the same architecture doc), `[→ <milestone>]` / `[→ cross-cutting]` (picked up by that milestone's `/engineer` run), `[→ phase N]` (picked up by that phase's LLD). A `/dev` project's items are untagged; its Plan step consumes them all. Delete an item once it's integrated; git keeps the history. Two tiers, same rules: `design-stash-<project>.md` beside the architecture doc, `<project-name>/design-stash.md` beside the HLD or DD.
2. **use-cases** — detailed behavioral scenarios: the exact system response to a specific situation. Permanent spec, so it accretes rather than drains — architecture, HLDs, LLDs and DDs all append. `use-cases-<project>.md` for an architecture project (its milestone HLDs append to it, and entries may be tagged by milestone); `use-cases-<project-name>.md` for a new standalone system (the HLD decides). A fix or small project inside an existing system, and every `/dev` project, appends to the existing governing doc; with no such doc, the scenarios stay in the requirements (the DD's Goal).
3. **future** — *speculative* out-of-scope improvements, the inverse of design-stash: destined for nothing, so nothing deletes them on use — pruned only once shipped. One addressable section each. `docs/designs/future-<workspace>.md`, one per workspace — never per project, milestone, or phase. Living doc: `/architect`, `/engineer` and `/dev` write to it. `/engineer` reads it at HLD and LLD time, `/dev` at Plan time, to check whether a deferred idea has come into scope.
4. **workflow-lessons** — workflow improvements, triage overrides, review findings. Two tiers like design-stash, swept at architecture send-off and at wrap-up (`/engineer` and `/dev`); paths, doc shape and the resolution rule in `~/.claude/playbooks/workflow-lessons.md`.

Routing rule while brainstorming or writing: too-low-altitude detail → design-stash; behavioral scenario → use-cases; out-of-scope idea → future; process friction → workflow-lessons.

## G. Design review

1. Invoke the design-reviewer subagent (Task, `subagent_type: design-reviewer`). Pass: doc path, doc type, project name. It returns categorized findings (must-fix / suggestion / nit) with section refs.
2. Apply the findings yourself — every must-fix, and suggestions and nits at your judgment. No triage with the human mid-loop.
3. Re-invoke a **fresh** design-reviewer at the first one's model + effort; loop until a review returns nothing new beyond what you already skipped.
4. Once the loop converges, run the prose-reviewer subagent (Task, `subagent_type: prose-reviewer`), passing the doc path — it pins its own model + effort — and a Codex one if she opts in (`~/.claude/playbooks/codex.md` Pick). One pass, never in the same turn as a review round. Unconditional, because it catches the fix accretion the loop itself caused (§H). Apply its findings the same way.
5. Then *offer* one final design-reviewer pass on Fable, effort per `~/.claude/playbooks/agent-pick.md`, and a Codex one per `~/.claude/playbooks/codex.md` (Pick). Never auto-run.
6. Report to the human: the non-nit findings you skipped, one line each with why, plus anything you fixed in a way that isn't the straightforward one, plus the evaluation report (`codex.md`) for any Codex pass. Fixed findings aren't listed — they're in the diff she reviews.

## H. Fix accretion

1. The failure mode of the review loop: each round's clarification lands as an appended clause, negation, or parenthetical, and after N rounds the paragraph is a transcript of the argument rather than a statement of the result.
2. After applying a round's fixes, reread each touched paragraph as a fresh reader; if a fix added a second negation or a second parenthetical to one sentence, rewrite the sentence.
3. A fix that exists only to preempt a reviewer's misreading goes to an **Anticipated questions** block, not the main flow (P10).
4. Worked signature, from a real doc: "Items 1 and 2 make one anti-confusion tripwire, from the two sides: `executor.py:367` and `:595` are **not** callers of…" — provenance first (§C1), a one-off coinage (P3), bare coordinates (§C2), and a rebuttal (P10), all in one sentence. Each clause was a correct review fix; the sentence is unreadable.
5. Before handing the doc to review, self-pass the prose against `~/.claude/prose.md`.
