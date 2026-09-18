#!/usr/bin/env bash
# PreToolUse (Bash) hook: force an approval prompt for git commits AND history
# rewrites (rebase, reset, force-push) — even when wrapped in a compound like
# `cd <dir> && git commit ...`. `git commit --amend` is covered by the `commit`
# branch.
#
# Why a hook and not an ask-rule: in Claude Code (>=2.1.52) ask/deny permission
# rules don't match the split subcommands of a compound under bypassPermissions,
# so `cd x && git commit` runs silently. See anthropics/claude-code#28240, #13009.
# A PreToolUse hook sees the RAW command string and matches anywhere in it.
#
# Matches (also behind `cd ... &&` etc.):
#   git [..] commit | rebase | reset        (incl. `git -C <path>`, `git -c k=v`)
#   git [..] push [..] -f | --force         (space-delimited so branch names like
#                                            `my-feature` don't false-trigger)
# The [^&|;] class stops a match from spanning a shell separator, so
# `git status && echo commit` does NOT trigger.
CMD=$(jq -r '.tool_input.command // empty')
if printf '%s' "$CMD" | grep -qE 'git +[^&|;]*(commit|rebase|reset)|git +[^&|;]*push[^&|;]*( -f| --force)'; then
  printf '%s' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"git history-rewrite detected (commit/rebase/reset/force-push) — confirm (compound-safe hook)"}}'
fi
exit 0
