# Frenship

Ship software with your AI frens. An AI-native SDLC: resumable pipelines, agents, playbooks, and conventions.

## What's in it

Three pipelines, each a slash command. Each writes its design doc as it goes and picks up from that doc in a fresh session.

- `/architect` — a new product: architecture doc, milestones. Each milestone later becomes an `/engineer` run.
- `/engineer` — a milestone or big feature: brainstorm, HLD, phased LLDs, build, wrap-up.
- `/dev` — a fix or small feature: brainstorm, one plan, build, wrap-up.

Around them:

- `global/agents/` — subagents: implementer, reviewer, design-reviewer, optioneer, prose-reviewer, comment-reviewer.
- `global/playbooks/` — the step-by-step instructions a pipeline loads on demand.
- `global/commands/` — the pipelines plus `/commit`, `/debug`, `/implement`, `/optioneer`, `/time-travel`.
- `global/CLAUDE.md`, `conventions.md`, `prose.md` — how the main thread behaves, how code is written, how prose is written.
- `global/output-styles/`, `hooks/`, `scripts/`, `tools/` — the output style, a commit-confirmation hook, and helper tools. The comment-lint tool reads its API key from `TYPESAFE_API_KEY`, or from `~/.env.d/typesafe` if that exists.

Written for Claude Code. The playbooks pick models per step and can hand review or rewrite passes to other vendors' agents.

## Install

Clone, then symlink each entry of `global/` into `~/.claude/`:

```
git clone https://github.com/netta-dev/frenship ~/workspaces/frenship
cd ~/.claude
for f in CLAUDE.md conventions.md prose.md commands agents playbooks scripts output-styles tools; do
  ln -s ~/workspaces/frenship/global/$f $f
done
```

Then read `global/CLAUDE.md` and edit the parts that are personal: the pronouns line, the aliases. An installer that asks for these is planned.

## Status

Early. This is a direct copy of one person's working config, made public so others can try it. Templates, an installer, and generation are next.

This repo is a read-only mirror. Fork freely; pull requests aren't accepted.

## License

0BSD. See `LICENSE`.
