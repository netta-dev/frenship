# Codex dispatch

Run one of `~/.claude/agents/` on OpenAI Codex, alongside the Claude subagent. Evaluation phase: opt-in (Pick), read-only agents only, single passes only — never inside a review loop's rounds — and the caller reports which agent found what (see Evaluation report).

Callers: `/optioneer`; the final-pass offer and the prose pass in `design-doc.md` §G; the final-pass offer in `build.md` step 4 and `comment-review.md`. The comment-reviewer's rewrites run on Sol (high), one batched ad-hoc prompt per pass, not an agent file; pinned, not offered.

## The call

```
codex exec -C <repo-or-worktree> -s <sandbox> --ephemeral \
  -m <model> -c 'model_reasoning_effort="<effort>"' \
  -o /tmp/codex-<agent>-<slug>.md \
  "$(sed '1{/^---$/!q};1,/^---$/d' ~/.claude/agents/<agent>.md)

<the inputs the agent's 'Inputs from caller' section lists — same values the Claude dispatch got>"
```

- `-C` is the same directory the Claude subagent works in. In a worktree project that's the worktree.
- Use `workspace-write` for the code reviewer so checked-in tests can create temporary files and caches, as they can for the Claude reviewer. Use `read-only` for the other roles. The code reviewer remains a read-only role by instruction: it may run tests but must not edit source files. Check `git diff HEAD` and `git status` again after both runs and resolve any unexpected changes before using either report.
- Run it with Bash `run_in_background` in the same turn as the Claude dispatch; read the `-o` file when the completion notification arrives. The turn ends while both run — the ⏳ rule applies.
- Keep reviewed files unchanged until both runs finish. Check Codex's exit status before using its report.
- The prompt is the agent file's body with the frontmatter stripped.
- Tool names in the body (Read, Grep, Agent) are Claude's. Codex maps them to its own shell; a fan-out instruction it can't follow it does inline.
- To stop a run: `pgrep -f 'codex exec'` and kill that pid. Never `pkill -f 'codex exec'` — the pattern matches the shell that issued it.

## Models

Offer only the models and effort levels listed here, even if the catalog exposes others.

| Model       | Pass as       | Effort levels               | Default |
| ----------- | ------------- | --------------------------- | ------- |
| GPT-6.1 Sol | `gpt-6.1-sol` | low · medium · high · xhigh | low     |
| GPT-6 Astra | `gpt-6-astra` | low · medium · high · xhigh | low     |

Always the full slug; `sol` alone is rejected. The list is `~/.codex/models_cache.json` — re-read it when a slug fails. Runs bill the ChatGPT subscription, not an API key.

## Pick

Follow agent-pick.md’s selection rules, using Codex models; add “no” as option 3. Claude frontmatter pins apply only to Claude. Codex overrides: prose-reviewer and comment-reviewer = Sol (high), ask yes/no; the final-pass design-reviewer = Astra and the final-pass reviewer = Sol, offer two efforts.

## Evaluation report

After both runs return, present the Claude findings as the workflow already does, then one table:

| Finding | Claude | Codex |
|---|---|---|
| `<one-line gist>` | must-fix | — |
| `<one-line gist>` | suggestion | must-fix |

Compare each role's actual outputs: findings, prose violations, or alternatives. Use severity only when the role supplies it. One row per distinct finding, matched by substance, not wording; a finding only one agent raised has a dash in the other column. Triage and fix from the union, per the caller's own rules. This section goes when the evaluation phase ends.
