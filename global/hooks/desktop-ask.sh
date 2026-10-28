#!/usr/bin/env bash
# PreToolUse (Bash) hook: ask before a command that drives or captures the human's
# desktop. A segment asks when its first word, after any sudo or VAR=value prefix, is
# xdotool, wmctrl, gnome-screenshot, or xwd, or is ImageMagick's import followed by a
# flag or an image file. A hook rather than an ask rule, for the reason in
# git-rewrite-ask.sh. Like env-dump-deny.sh, it matches the raw command string, split
# at shell separators and quotes, so `ssh host 'xdotool …'` asks too.
CMD=$(jq -r '.tool_input.command // empty')
[ -n "$CMD" ] || exit 0
source "$(dirname "$0")/lib/strip-data-heredocs.sh"
CMD=$(strip_data_heredocs "$CMD")

image='\.(png|jpe?g|gif|bmp|tiff?|webp|xwd|p[bgpn]m)$'
while IFS= read -r seg; do
  read -ra words <<< "$seg"
  i=0
  while ((i < ${#words[@]})) && [[ ${words[i]} == sudo || ${words[i]} =~ ^[A-Za-z_][A-Za-z0-9_]*= ]]; do ((i++)); done
  ((i < ${#words[@]})) || continue
  cmd=${words[i]##*/}
  next=${words[i+1]:-}
  if [[ $cmd =~ ^(xdotool|wmctrl|gnome-screenshot|xwd)$ ]] || { [ "$cmd" = import ] && [[ $next == -* || $next =~ $image ]]; }; then
    jq -cn '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "ask", permissionDecisionReason: "Drives or captures the human'"'"'s desktop; needs her approval each time."}}'
    exit 0
  fi
done < <(printf '%s\n' "$CMD" | sed -E 's/&&|\|\||[;|&()`]/\n/g' | tr "'\"" '\n\n')
exit 0
