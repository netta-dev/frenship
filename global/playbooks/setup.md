# Setup

Bootstrap a fresh workspace with the standard `.claude/context/` convention when `.claude/context/` is missing (inline, no subagent/review; `/engineer` runs it after the HLD, `/dev` after the plan).

## Detect

- A git repo: `git rev-parse --git-dir` succeeds (in a worktree `.git` is a file, not a directory)
- Project type: `pubspec.yaml` (Flutter), `package.json` (Node/web), `pyproject.toml` (Python), etc.
- Existing config: `CLAUDE.md`, `.claude/settings.local.json`

## Propose

Show the human a short list of what you'll create, tailored to detected markers.

    Detected: Flutter workspace, no git repo, no .claude/context/.
    Proposing:
      - git init (via wsinit skill if remote not yet chosen)
      - .gitignore (Flutter build artifacts)
      - .claude/context/capabilities.md (YAML):
          lint: flutter analyze
          test: flutter test
          visual_testing:
            mcp: mobile-device

## Execute

Create approved files. Skip empty context files (`conventions.md`, `architecture.md`, `docs.md` added later when needed); only `capabilities.md` gets initial contents from detection. `capabilities.md` holds only tooling a workflow skill invokes; phase-specific / one-shot commands live in that phase's runbook or LLD. Seed `toolchain_check` as well — the command that says whether the project's tools and packages are behind, without changing anything: `npm outdated`, `flutter upgrade --verify-only`. Leave it out where the ecosystem has nothing like that.

`CLAUDE.md`: identity + stack + critical rules + ops quick-ref (run/deploy/SSH/env commands main thread uses). Reference material goes in `.claude/context/*`.

`docs.md` (when created): per-topic sections with bulleted file lists + notes. High-signal only — feature-area pointers. Drop project-level HLDs without feature-area value.

## Worktree manifest

After Execute (the manifest authoring routine's cwd-grep reads `capabilities.md`, which Execute just created):

- Run `~/.claude/playbooks/worktree.md`'s manifest authoring routine and write `.claude/context/worktree.md` (copy-list of untracked local state, setup command, runtime notes — "None" where nothing applies).
- Add `.claude/worktrees/` and `.eng-provisioned` to `.gitignore` (so future worktrees don't dirty main checkout; sentinel self-clears on recreate).

## Commit

`git add -A && git commit` the scaffold.

## Hand off

Complete. The caller continues: `/engineer` proceeds to phase 1, `/dev` to Build.
