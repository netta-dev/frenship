---
description: Dispatch an implementation plan — main-thread vs subagent, pick model.
---

# /implement

Execute an approved implementation plan. Decide dispatch; run.

## Decide

Compare work cost to subagent handoff tax (~20k tokens).

- **Main thread** (no subagent): diff is clearly smaller than the handoff tax. Proxy: ~≤3 files, simple edits, no deep per-file reasoning.
- **Subagent**: everything else. Choose model + effort per `~/.claude/playbooks/agent-pick.md` — two candidates, she picks.

## Execute

- **Main thread**: act as implementer per `@~/.claude/agents/implementer.md` — reference conventions/capabilities/docs as needed (usually already in context), `git add -A`, run lint/test if declared, surface unrelated observations separately. Ad-hoc dispatch general-purpose subagents for chunks when it pays (e.g., Haiku for a bulk rename sweep while main thread handles the reasoning-heavy edits).
- **Subagent**: `Agent` tool, `subagent_type: "implementer"`, with the chosen `model` + `effort`. Pass the approved design (LLD, DD, or inline plan) + mode (`implement` or `fix`).

Surface unrelated bugs/suggestions as non-blocking observations to caller.
