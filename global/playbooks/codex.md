# Codex dispatch

Run one of `~/.claude/agents/` on OpenAI Codex, alongside the Claude subagent. Evaluation phase: opt-in (Pick), read-only agents only, single passes only — never inside a review loop's rounds — and the caller reports which agent found what (see Evaluation report).

Callers: `/optioneer`; the final-pass offer and the prose pass in `design-doc.md` §G; the final-pass offer in `build.md` step 4 and `comment-review.md`.

## The call

```
codex exec -C <repo-or-worktree> -s read-only --ephemeral \
  -m <model> -c 'model_reasoning_effort="<effort>"' \
  -o /tmp/codex-<agent>-<slug>.md \
  "$(sed '1{/^---$/!q};1,/^---$/d' ~/.claude/agents/<agent>.md)

<the inputs the agent's 'Inputs from caller' section lists — same values the Claude dispatch got>"
```

- `-C` is the same directory the Claude subagent works in. In a worktree project that's the worktree.
- Run it with Bash `run_in_background` in the same turn as the Claude dispatch; read the `-o` file when the completion notification arrives. The turn ends while both run — the ⏳ rule applies.
- Keep reviewed files unchanged until both runs finish. Check Codex's exit status before using its report.
- The prompt is the agent file's body with the frontmatter stripped.
- Tool names in the body (Read, Grep, Agent) are Claude's. Codex maps them to its own shell; a fan-out instruction it can't follow it does inline.
- To stop a run: `pgrep -f 'codex exec'` and kill that pid. Never `pkill -f 'codex exec'` — the pattern matches the shell that issued it.

## Models

Offer only the models and effort levels listed here, even if the catalog exposes others.

| Model | Pass as | Effort levels | Default |
|---|---|---|---|
| GPT-5.6 Sol | `gpt-5.6-sol` | low · medium · high · xhigh | low |
| GPT-6 Astra | `gpt-6-astra` | low · medium · high · xhigh | low |

Always the full slug; `sol` alone is rejected. The list is `~/.codex/models_cache.json` — re-read it when a slug fails. Runs bill the ChatGPT subscription, not an API key.

## Pick

Follow agent-pick.md’s selection rules, using Codex models; add “no” as option 3. Claude frontmatter pins apply only to Claude. Codex override: prose-reviewer and comment-reviewer = Sol (medium); ask yes/no.

## Evaluation report

After both runs return, present the Claude findings as the workflow already does, then one table:

| Finding | Claude | Codex |
|---|---|---|
| `<one-line gist>` | must-fix | — |
| `<one-line gist>` | suggestion | must-fix |

Compare each role's actual outputs: findings, prose violations, or alternatives. Use severity only when the role supplies it. One row per distinct finding, matched by substance, not wording; a finding only one agent raised has a dash in the other column. Triage and fix from the union, per the caller's own rules. This section goes when the evaluation phase ends.
