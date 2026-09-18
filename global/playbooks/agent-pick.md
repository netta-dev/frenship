# Agent pick

For any workflow point that dispatches a subagent: offer two model + effort combinations; she picks.

Callers: `/implement`, `/optioneer`, `hld.md` / `lld.md` (Design review), `build.md` (Reviewer).

## When to run it

At a dispatch decision — an implementer for a phase, a review pass, an optioneer run. Once per loop: ask at the loop's first dispatch; every later iteration of the same loop — a fresh reviewer, a fix pass — reuses that pair unchanged.

## The ask

Two candidates, numbered, with a recommendation and the reason for it:

> ❓ (1 - rec) `<model>` (`<effort>`) or (2) `<model>` (`<effort>`) to implement this?
> `<reason for the recommendation>`

The pair can vary along either axis, or both — `opus (high)` vs `opus (xhigh)` (same model, more thinking), `opus (medium)` vs `sonnet (high)` (cheaper model, harder thinking), `fable (medium)` vs `opus (xhigh)` (top tier vs. the workhorse). Pick the two that actually bracket this task; don't reach for a habitual pair.

Rules:

- **Exactly two**.
- **Ground the reason in what you know about this task** — its size, how much is mechanical, whether the plan leaves anything open, what it touches.
- **Check the agent's frontmatter first.** It can pin `model`, `effort`, or both. Offer only the axis it leaves open, and skip the ask entirely when it pins both.
- **Pass `effort` as a parameter on the Agent call** — it works even though the tool schema you see doesn't list it. Frontmatter `effort:` pins it instead.

## Models

| Model | Pass as | $/MTok in/out | Reach for it when |
|---|---|---|---|
| Haiku 4.5 | `haiku` | 1 / 5 | Bulk mechanical work — rename sweeps, reformats, delete sweeps, wide greps. Near-zero reasoning per file. |
| Sonnet 5 | `sonnet` | 3 / 15 | Standard feature work; near-Opus quality on coding and agentic tasks. The default working model. |
| Opus 5 | `opus` | 5 / 25 | Multi-file features, larger refactors, end-to-end feature work. The margin over Sonnet shows on hard tasks, not on easy edits. |
| Fable 5 | `fable` | 10 / 50 | Hardest long-horizon work — overnight autonomous runs, first-shot builds of a well-specified system, large migrations. Turns can run many minutes. |

**Haiku takes no effort level** — `effort` errors on Haiku 4.5; offer it bare.

## Effort

`low` · `medium` · `high` · `xhigh`; default `high`.

| Level | Use for |
|---|---|
| `low` | Short scoped tasks, latency-sensitive work, mechanical subagents. |
| `medium` | Cost-sensitive work that still needs judgment. Often the sweet spot. |
| `high` | The floor for intelligence-sensitive work. |
| `xhigh` | Coding and agentic work — repeated tool calls, wide exploration. The start point for an implementer. |

Lower effort buys fewer and more consolidated tool calls, less preamble, terser output; higher buys exploration and tokens. A cheaper model at higher effort often matches a stronger model at lower effort.
