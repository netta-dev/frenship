# LLD — Low-Level Design

Detailed plan for one phase — or, as the DD variant (see Template), `/dev`'s single design doc, which runs this playbook from Write the plan onward. Written to file, reviewed via diff, committed on approval. Approval hands off to the build playbook.

Authoring craft, diagrams, companion-doc rules, and the shared design-review loop: `~/.claude/playbooks/design-doc.md`.

## Input

Current phase from the HLD's `Status` line. Confirm with the human if ambiguous.

## Process

1. **Read HLD** — locate phase section. Also read the companions: `docs/designs/<project-name>/design-stash.md` for sections tagged `[→ phase N]`, the use-cases entries relevant to the phase, and `docs/designs/future-<workspace>.md` for any deferred idea now in scope.
2. **Work open questions** — open with a short overview of the project; then the open questions, batched with proposed resolutions. The human confirms/pushes back; integrate. Behavioral scenarios or edge cases surfaced here (e.g. "resume window = 5 min") → append to the governing use-cases doc.
3. **Read context:** `@~/.claude/conventions.md`, workspace `.claude/context/{conventions,architecture,docs}.md` as relevant, user guides if the change affects user behavior.
4. **Read relevant code** for change surface.
5. **Verify external APIs** — check every vendor/library API the plan relies on against the installed package / vendor docs: exists, not deprecated, right *mode*, valid params, and *every* relied-on path. Non-derivable endpoints and per-provider telemetry are explicit fail-loud inputs or independently measured.
6. **Field-semantics changes** — when the plan changes an existing field's *semantics*, grep every reader of that field and mark each affected/unaffected in the plan.
7. **UI changes**: screenshot current state via declared visual-testing MCP.

## Write the plan

Write at `docs/designs/<project-name>/lld-<N>-<slug>.md` — `<N>` and `<slug>` per HLD phase heading. Use template below.

- A keep-as-reference / might-need-it skip must name a live consumer or documented future use; re-check after any same-change decision that could have removed the last consumer.
- External-infra phases: fix the orchestrator-vs-human split up front — Claude drives everything reachable from shell + creds (provisioning, resource CRUD, headless validation); the human does only hardware (mic/voice) or browser (dashboard/account) steps.

## Alternatives, then design review

Run `~/.claude/commands/optioneer.md` — alternatives land under their **Resolved decisions** entry — then `~/.claude/playbooks/design-doc.md` §G, doc type `lld` (or `dd` for a `/dev` design doc).

## Present for approval

Ask: **"❓ Ready to commit?"** Iterate via Edit on human pushback until clear approval. Answering a scoped sub-question resolves that item only — re-ask and wait for a clear yes.

## On approval

1. **Commit**: bump the HLD's `Status` to `Phase <N> LLD committed`, then `git add <lld-path> <hld-path> && git commit <lld-path> <hld-path> -m "<project-name>: phase <N> lld — <title>"`. One commit, so no window exists where the plan is committed but `Status` still points at the previous phase.
2. **Integrate to main** per `~/.claude/playbooks/worktree.md` (Integrate) — doc-only like HLD approval, guarded (a no-op for a main-checkout project). Main's `Status` then reads `Phase <N> LLD committed` for every reader.
3. **Continue vs. fresh session** — recommend starting the build here or `/exit`ing and re-running `/engineer` (Resume picks the committed LLD up at Pipeline B2). Judge by context budget, as `/engineer` does at a phase boundary. A clean cut-point: the plan is on disk and committed, so nothing is held in conversation.
4. **Build** — `~/.claude/playbooks/build.md` with the approved LLD, in whichever session runs it. Don't edit files yourself; the build playbook dispatches the implementer.

---

## Template

**DD variant** — `/dev`'s single design doc at `docs/designs/<project-name>/dd-<project-name>.md`: the same template, with the heading `# <title> (DD)`, the header block per `design-doc.md` §E2 under it, and Goal tying back to the brainstormed requirements. Without an HLD phase, "this phase" reads "this change", and "the HLD open-Q being closed" reads "the requirement or brainstorm decision being closed". Brainstormed behavioral scenarios were appended to the governing use-cases doc at `/dev`'s Design step, or stay in Goal when there is none. Everything else applies unchanged.

~~~markdown
# Phase `N` — `title` (LLD)

*Italics = author instruction, delete when filling in. Plain = example/placeholder, replace.*

## Goal

1–3 sentences: what this phase delivers end-to-end, what's true after, what still doesn't work. Ties back to the HLD phase entry.

## Resolved decisions

*Numbered list. Each: the HLD open-Q being closed, or a new decision surfaced during the LLD.*

1. **Decision.** Resolution + rationale.

> [!example]- **Alternatives considered** — option A, option B (decision 1)
> Option A — why it lost. Option B — why it lost. One line each.

2. **Decision.** …

## Design

*1–3 paragraphs. The narrative that bridges decisions to the concrete API/Files. Structural shape of the change, the pattern (e.g. "dual ownership: BLoC owns canonical state, widget owns local copy"), data flow. Skip only when the change adds no structure. A decision with structural consequences appears here and/or in API/Schema; `Resolved decisions` is rationale and reference, never the sole carrier of the design.*

## API / Schema

*Interface signatures, proto/DB schema deltas, type/contract changes. Omit the section entirely if no API surface changes.*

```dart
class FooScope extends StatefulWidget {
  final Map<String, bool> initialValue;
  // ...
}
```

## Files

### Modified

- `path/file.ext` — one-line note describing the change.

### New

- `path/new.ext` — what it owns.

### Deleted

- `path/old.ext` — why dropped; what absorbed it.

## Tests

- **New**: `path/foo_test.dart` — what it covers.
- **Modified**: `path/bar_test.dart` — why.
- **Deleted**: `path/baz_test.dart` — replaced by/folded into X.

## Test plan

*Concrete run commands; manual smoke notes if applicable.*

```
./claude/run-tests.sh test/path/foo_test.dart
flutter analyze
```

Manual: open X, do Y, verify Z.

## Risks / notes

*Non-obvious gotchas, sequencing constraints, things future readers would miss from the code alone.*

- **Risk / note.** One sentence.
~~~
