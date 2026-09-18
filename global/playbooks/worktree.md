# Worktree

Machinery for running an `/engineer` or `/dev` project in its own git worktree on `eng/<project>` at `.claude/worktrees/<project>/`, so a dirty implementation tree never touches the main checkout. Loaded on demand by the command at each lifecycle step. "Design doc" below means the HLD (`/engineer`) or the DD (`/dev`).

Session isolation refuses an action: `ExitWorktree(keep)`, run it from the main checkout, `EnterWorktree(path=…)` back. Try that before escalating manual work to the human. It also refuses a Bash command whose text mentions `git` even when it only edits files (a heredoc, a Python script): use Edit, or keep `git` out of the command text.

## Create + enter

For a new project (Resume found none) or a milestone start. **Slug rule**: a milestone start uses the milestone's kebab-case slug as `<project>` — it's canonical, the arch doc's stash tags point at it; a free-form task gets a short kebab-case slug derived from it. State the slug and proceed in the same turn; the human objects in her first reply if it's wrong, while a rename is still cheap. To rename: Discard (below), then re-run this block. When the command was invoked bare, ask. Steps 1–3 below run **on the main checkout, on main** — the session hasn't branched yet; step 4 runs on the branch:

```
# steps 1–3 on the main checkout, on main
1. ensure `.claude/worktrees/` and `.eng-provisioned` are both in .gitignore
   (commit to main if missing; idempotent once seeded)
2. git worktree add -b eng/<project> .claude/worktrees/<project> HEAD   # base = local HEAD
3. EnterWorktree(path=".claude/worktrees/<project>")                    # session moves onto the branch
4. toolchain check: if `.claude/context/capabilities.md` declares a `toolchain_check`, provision
   first (Provision, below), run the check, and offer a toolchain upgrade as the project's first
   commit iff it reports something behind, naming what; run the full declared suite before
   committing the upgrade (see below)
# the rest of the command's pipeline now runs here, on eng/<project>
```

- **Step 4's suite run** verifies the upgrade commit at creation. It can then ride a doc/tooling-only integrate (caller 2 of Integrate) without a second verification; otherwise it rides the change commit's integrate, which re-verifies. A workspace that Setup hasn't scaffolded yet doesn't declare a check; both commands re-check after Setup.
- **Assumes an existing git repo.** A git-less greenfield workspace has nothing to worktree from — skip create/enter and run the project in the workspace dir (today's main-checkout behavior); the Setup playbook `git init`s it, and worktree adoption begins with the next project.
- **Base is local `HEAD`, not origin.** Don't use `EnterWorktree`'s native create — it bases off `origin/<default>`, which can be stale or absent. Local `HEAD` is the correct base.
- **`EnterWorktree(path)` takes no `name`**, so it enters the worktree by path without tripping the "already in a worktree" guard.
- **Both `.gitignore` entries must land on main before creation.** Without `.claude/worktrees/`, the nested worktree dir shows untracked in the main checkout's `git status`, dirtying it — and main must stay clean so the branch can fast-forward back into it later. `.eng-provisioned` rides along for the provisioning sentinel (see Provision). Git still lets `git worktree add` write into the ignored path.
- **The step-1 fallback commit touches shared main.** If it actually has to commit (an un-seeded repo — one not yet given these entries), and the repo is shared with another checkout, keep this commit single-owner.

## Manifest

Per-repo provisioning inputs at `.claude/context/worktree.md`, read once at first build/run (see Provision). Prose sections, not YAML — orchestrator reads without parsing; Runtime notes must be prose. All three sections optional; write "None" for what doesn't apply. A tracked-only repo — no build, no app — has all three "None".

### Template

```markdown
# Worktree manifest — <repo>

*Replace the `<…>` header line and the example entries; the Authoring routine (below) explains each section. All sections optional — write "None" for what doesn't apply.*
<one line: what the repo needs at cold-start — or "tracked-only / no build / no app — nothing to provision">

## Copy-list
- .env
- .env.local

## Setup

    npm install && npm run codegen

## Runtime notes
Worktree serves PORT=3001 (main uses 3000). `npm run dev` is cwd-relative — safe.
```

### Authoring routine

Invoked by two deliberate callers — Setup (fresh workspaces) and the eager per-repo seed (existing repos) — never lazily mid-provision. Author it working *in* the repo, with full attention on the cwd-grep. Steps:

1. **Copy-list** — enumerate the git-ignored local state a fresh checkout lacks: `.env*`, `settings.local.json`, dev-DB seeds, credential files. Repo-root-relative, one per line. Everything tracked is already on the branch — don't list it.
2. **Setup** — the cold-start command (deps install, codegen, migrations) run once in the worktree cwd. "None" if the repo has no build.
3. **Runtime notes** — the cwd-relative check. Grep the repo's `capabilities.md` run/test commands for **absolute paths or `cd`-into-main** — either would serve *main's* code from a worktree session (a silent bug). Fix the offending command to be cwd-relative, or record a per-worktree port/DB override here so the worktree app doesn't collide with a running main-checkout one. No `capabilities.md` (no declared run/test tooling) → nothing to serve → "None".

## Provision

Lazily, once, before the first step that builds or runs. Skip if the sentinel exists:

1. **Sentinel check** — if `.eng-provisioned` exists at the worktree root, provisioning already ran; skip.
2. **Read the manifest** — `.claude/context/worktree.md`. Missing → fail-loud (below).
3. **Resolve the main-checkout root** — `realpath "$(git rev-parse --git-common-dir)"` gives the main `.git` as an absolute path (a linked worktree can emit it relative); its parent is the main checkout root. Copy each Copy-list file from there into the worktree at the same repo-root-relative path.
4. **Run Setup** in the worktree cwd.
5. **Write the sentinel** — create `.eng-provisioned` at the worktree root.

**Fail-loud on any provisioning gap** — a missing manifest, a copy-list source file absent, or a Setup failure: abort and report to the human (for a missing manifest, point at the authoring routine — eager-seed + Setup are supposed to have authored it; a gap is real, not a cue to improvise). Never half-provision — partial setup throws confusing downstream failures; human is already in-loop.

The sentinel is `.eng-provisioned` at the worktree root: *inside* the tree but git-ignored (the `.eng-provisioned` `.gitignore` entry), so it never dirties status, survives a normal resume, and — being ignored, never checked out — is absent from a freshly re-created worktree. So deleting and re-creating a worktree (`rm -rf`→recreate) re-provisions automatically, with no separate sentinel cleanup.

## Integrate to main

Merges a completed phase — or an approved design doc — back to main. Guarded: runs only when the `eng/<project>` branch exists (`git show-ref --verify --quiet refs/heads/eng/<project>`); a main-checkout project no-ops, its commit already on main. Callers, and whether a back-merge re-verifies:

1. Each phase commit, and `/dev`'s change commit — re-verifies if main moved.
2. Each approved HLD, LLD or DD, and Discard's carry-over of an abandon, setup or toolchain commit — doc/tooling-only, no re-verify (the toolchain commit was suite-verified at step 4 of Create + enter).
3. The wrap-up commit at teardown — re-verifies if main moved; no doc-only skip, since it rides the full project branch.

Main only ever *fast-forwards* to a tip the full suite already passed, so it never takes an unverified merge.

Resolve the main-checkout root once: `MAIN="$(dirname "$(realpath "$(git rev-parse --git-common-dir)")")"`.

1. **Main clean and on `main`?** Pause and ask — never stash — if `git -C "$MAIN" status --porcelain` is non-empty or `git -C "$MAIN" symbolic-ref --short HEAD` isn't `main`. The ff below writes to the main checkout's HEAD, so a dirty or wrong-branch checkout would corrupt the target or loop on retry. (`--porcelain` also flags stray untracked files; pausing on those is fine — the main checkout is clean by design.)
2. **Did main move?** `git -C "$MAIN" merge-base --is-ancestor main eng/<project>`: exit 0 → main is contained in the branch, fast-forward directly (step 4); exit 1 → main gained an independent commit (a hotfix, or another checkout), so back-merge first (step 3).
3. **Back-merge main → branch** (in the worktree, on `eng/<project>`): `git merge main`. On conflict, stop and hand the conflicted files to the human — never auto-resolve (`-X ours/theirs` picks a side blind and could ship an unverified combination). After they resolve and commit, re-run the full declared suite (`capabilities.md`), not just the touched tests — the fused state is untested. Red → fix on the branch with new commits (never amend; the branch is synced history), re-verify, continue only once green. (A doc-only or tooling-only merge — caller 2 above — skips the re-verify.)
4. **Fast-forward main:** `git -C "$MAIN" merge --ff-only eng/<project>`. Rejected → main advanced again or went dirty; re-run from step 1, which re-checks and either pauses or back-merges. `--ff-only` leaves main untouched on rejection, so retrying is safe.

`git -C "$MAIN"` reaches the parent checkout from the worktree's permission scope — no scope switch needed.

## Resume entry

Re-enters a project's worktree when resuming across sessions. The session starts in the main checkout on main; the resume grep has found the design doc and the human confirmed. Derive `<project>` from the doc path — `branch = eng/<project>`, `path = .claude/worktrees/<project>`.

1. **A worktree project?** Yes iff the branch exists locally or on origin: `git show-ref --verify --quiet refs/heads/eng/<project> || git ls-remote --exit-code origin eng/<project> >/dev/null 2>&1`. Neither → a main-checkout project (pre-worktree, or a git-less workspace); resume in place, don't enter.
2. **Enter, if cleanly enterable** — the local branch exists and the dir is present (`[ -d .claude/worktrees/<project> ]`; use the filesystem, not `git worktree list`, which keeps showing a `rm -rf`'d worktree until `git worktree prune`). `EnterWorktree(path=".claude/worktrees/<project>")`, then check the tree is at a clean boundary — `git status --porcelain` empty and no in-progress merge (`git rev-parse -q --verify MERGE_HEAD` empty). Dirty or mid-merge → stop and surface (an interrupted back-merge, hotfix or implementation left it mid-flight); don't build on an unfinished tree. Clean → read the current step from the branch's design-doc `Status` line — authoritative in the worktree, since the branch is at or ahead of main. Every branch commit integrates to main as soon as it lands (LLD or DD approval, phase commit; a setup or toolchain commit rides the next integrate), so a branch ahead of main at a clean boundary is an interrupted integrate: run Integrate to catch main up, as whichever caller the stranded commit belongs to, then continue at the pipeline step matching the branch's `Status`.
3. **Otherwise fail loud** — the dir is missing, or the branch is only on origin (no local head — e.g. another checkout). Report the state — branch local? on origin? dir present? — and the recovery: `git worktree prune`, then `git worktree add .claude/worktrees/<project> eng/<project>` (or `git worktree add -b eng/<project> .claude/worktrees/<project> origin/eng/<project>` if the local head is gone too); re-provision then runs on its own, since `.eng-provisioned` is git-ignored and absent from the fresh dir. Let the human decide — don't silently recreate or resume on main.

## Teardown

Retires a completed project's worktree, at wrap-up, after the final commit. Guarded — only when the `eng/<project>` branch exists (`git show-ref --verify --quiet refs/heads/eng/<project>`); a main-checkout project no-ops (its commit is already on main). Runs after that final commit, so step 1 carries it to main before step 3 deletes the dir; the worktree's remaining non-committed files are all git-ignored (deps, sentinel, scratch) and drop with it.

1. **Final merge** — integrate the wrap-up commit to main per **Integrate to main** (above, caller 3): main fast-forwards to the branch tip, back-merging + re-verifying first if main moved. This is what makes the `git branch -d` below safe.
2. **Return scope** — `ExitWorktree(keep)`: moves the session back to the main checkout (the harness scope, not just cwd) — you can't `git worktree remove` your own cwd, and in a resumed session `ExitWorktree(remove)` can't remove a path-entered worktree.
3. **Remove** from the main checkout — worktree before branch (git refuses to delete a branch still checked out in a worktree):

```
git worktree remove .claude/worktrees/<project>    # no --force: committed tree; ignored files don't block. Refusal = a stray untracked non-ignored file (unconsumed state) → stop + check, don't --force
git branch -d eng/<project>                         # safe: the final merge left it an ancestor of main. Refusal = integrate didn't fully land (unmerged) → stop + surface; never -D (strands unmerged work)
git ls-remote --exit-code origin eng/<project> >/dev/null 2>&1 && git push origin --delete eng/<project>   # branch is on main; drop the remote ref (else cruft + name-reuse trap). Surface a failure — a lingering ref is that trap
```

## Discard

The human drops the project. With her OK, drop the uncommitted work (`git checkout -- . && git clean -fd`). If a design doc already reached main, retire it before removing anything: set its `Status` to `Project complete (abandoned)` (the Resume grep treats the prefix as done), `git mv docs/designs/<project> docs/designs/done/<project>`, commit `docs/designs` alone with subject `abandon <project>`, and integrate (doc-only). If a setup or toolchain commit is on the branch, it was approved on its own — integrate it too (doc/tooling-only) so the `branch -D` below doesn't lose it. Guarded like Teardown — a main-checkout project has no worktree or branch to remove, so it stops here. Manual teardown — **never `ExitWorktree(remove)`** (it only removes worktrees it created via `name`; it can't remove a path-entered one):

```
1. ExitWorktree(keep)                                  # return scope to the main checkout
2. git worktree remove --force .claude/worktrees/<project>
3. git branch -D eng/<project>                         # -D: the abandoned branch is unmerged
4. git ls-remote --exit-code origin eng/<project> >/dev/null 2>&1 && git push origin --delete eng/<project>
```

Step 4's `ls-remote` gate handles the timing: the orchestrator can't see whether a background push already ran during the brainstorm, so it *checks* origin for the ref rather than guessing. Present → delete it (else a later project reusing the name hits a stale remote ref); absent → the `&&` short-circuits to a no-op.
