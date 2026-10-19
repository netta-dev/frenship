# Codex dispatch

Run one of `~/.claude/agents/` on OpenAI Codex. The passes below run on Codex every time, without asking; no other dispatch does.

| Pass | Codex model (effort) |
| --- | --- |
| `/optioneer` | Astra (high), alongside the Claude one |
| `design-doc.md` §G4, prose-reviewer | Sol (xhigh), after the Claude one |
| `design-doc.md` §G5, final-pass design-reviewer | Astra (xhigh), alongside the Claude one |
| `build.md` step 4, final-pass reviewer | Sol (xhigh), alongside the Claude one |
| `comment-review.md` step 2, prose-reviewer | Sol (xhigh), after the Claude one |
| `comment-reviewer.md` step 3, rewrites | Sol (high), one batched ad-hoc prompt per round, not an agent file |

## The call

```
codex exec -C <repo-or-worktree> -s <sandbox> --ephemeral \
  -m <model> -c 'model_reasoning_effort="<effort>"' \
  -o /tmp/codex-<agent>-<slug>.md \
  "$(sed '1{/^---$/!q};1,/^---$/d' ~/.claude/agents/<agent>.md)

<the inputs the agent's 'Inputs from caller' section lists — same values the Claude dispatch got>"
```

- `-C` is the same directory the Claude subagent works in. In a worktree project that's the worktree.
- Use `workspace-write` for the code reviewer so checked-in tests can create temporary files and caches, as they can for the Claude reviewer. Use `read-only` for the other roles, except the two prose passes (`design-doc.md` §G4 and `comment-review.md` step 2), which apply their own rewrites. The code reviewer remains a read-only role by instruction: it may run tests but must not edit source files. Check `git diff HEAD` and `git status` again after both runs and resolve any unexpected changes before using either report.
- Run it with Bash `run_in_background`; read the `-o` file when the completion notification arrives. The turn ends while it runs — the ⏳ rule applies.
- Keep reviewed files unchanged until both runs finish. Check Codex's exit status before using its report.
- The prompt is the agent file's body with the frontmatter stripped.
- Tool names in the body (Read, Grep, Agent) are Claude's. Codex maps them to its own shell; a fan-out instruction it can't follow it does inline.
- To stop a run: `pgrep -f '[c]odex exec'` and kill that pid. Never `pkill -f 'codex exec'` — the pattern matches the shell that issued it.

## Models

Use only the models and effort levels listed here, even if the catalog exposes others.

| Model       | Pass as       | Effort levels               | Default |
| ----------- | ------------- | --------------------------- | ------- |
| GPT-6.1 Sol | `gpt-6.1-sol` | low · medium · high · xhigh | medium  |
| GPT-6 Astra | `gpt-6-astra` | low · medium · high · xhigh | low     |

Always the full slug; `sol` alone is rejected. The list is `~/.codex/models_cache.json` — re-read it when a slug fails. Runs bill the ChatGPT subscription, not an API key.
