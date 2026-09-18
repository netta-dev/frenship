---
description: Explore out-of-the-box alternatives to a design doc's key decisions.
---

# /optioneer

Run the optioneer agent against a design doc and record what it finds. The HLD and LLD playbooks run this after the draft, before design review; it also works ad-hoc on any design doc.

1. Resolve the doc — the path in the arguments, else the mid-flight design doc in `docs/designs/`; ask if several match.
2. Choose the model per `~/.claude/playbooks/agent-pick.md`, and ask about a Codex run per `~/.claude/playbooks/codex.md` (Pick).
3. Invoke `Agent`, `subagent_type: "optioneer"`, with the chosen `model` + `effort`, and, if she opted in, the Codex run per `codex.md` in the same turn. Pass both the doc path, doc type, project name.
4. Present the alternatives with the evaluation report (`codex.md`), and triage each with the human — adopt / reject.
5. **Write every alternative into the doc**, adopted or rejected, in an **Alternatives considered** callout directly after the decision it bears on — summary line naming the options and the decision, one line per option inside with the reason it lost.
