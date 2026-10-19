---
description: Explore out-of-the-box alternatives to a design doc's key decisions.
---

# /optioneer

Run the optioneer agent against a design doc and record what it finds. The HLD and LLD playbooks run this after the draft, before design review; it also works ad-hoc on any design doc.

1. Resolve the doc — the path in the arguments, else the mid-flight design doc in `docs/designs/`; ask if several match.
2. Invoke `Agent`, `subagent_type: "optioneer"`, with `model: "fable"` and `effort: "high"`, and the Codex run per `~/.claude/playbooks/codex.md` in the same turn. Pass both runs the doc path, doc type, project name, and the do-nothing posture: what already covers the scenario today, without the design. With it, the optioneer can weigh not building it instead of only naming it.
3. Present the alternatives from both runs and triage each with the human — adopt / reject.
4. **Write every alternative into the doc**, adopted or rejected, in an **Alternatives considered** callout directly after the decision it bears on — summary line naming the options and the decision, one line per option inside with the reason it lost.
