#!/bin/bash
# Claude Code statusline.
# Reads the status-line JSON (see Claude Code docs) from stdin and prints:
#   os user | cwd | session name (truncated) | model | reasoning effort | context used
# Managed by the statusline-setup agent -- ask Claude to change it further
# rather than hand-editing, so ~/.claude/settings.json stays in sync.

input=$(cat)

osuser=$(whoami 2>/dev/null || id -un 2>/dev/null || printf '%s' "$USER")
cwd=$(printf '%s' "$input" | jq -r '.workspace.current_dir // empty')
session=$(printf '%s' "$input" | jq -r '.session_name // empty')
[ ${#session} -gt 30 ] && session="${session:0:29}…"
model=$(printf '%s' "$input" | jq -r '.model.display_name // empty')
effort=$(printf '%s' "$input" | jq -r '.effort.level // empty')
used_pct=$(printf '%s' "$input" | jq -r '.context_window.used_percentage // empty')

# Shorten cwd: "~" for $HOME itself, basename otherwise.
if [ -n "$cwd" ]; then
  dir="${cwd/#$HOME/\~}"
  [ "$dir" != "~" ] && dir=$(basename "$dir")
else
  dir="?"
fi

# Colors -- picked to stay legible when the terminal dims the statusline.
DIM=$'\033[2m'
BLUE=$'\033[34m'
CYAN=$'\033[36m'
LILAC=$'\033[38;5;183m'
GREEN=$'\033[32m'
YELLOW=$'\033[33m'
RESET=$'\033[0m'
SEP="${DIM} · ${RESET}"

parts=()
[ -n "$osuser" ] && parts+=("${BLUE}${osuser}${RESET}")
parts+=("${CYAN}${dir}${RESET}")
[ -n "$session" ] && parts+=("${LILAC}${session}${RESET}")
[ -n "$model" ] && parts+=("${GREEN}${model}${RESET}")
[ -n "$effort" ] && [ "$effort" != "null" ] && parts+=("${YELLOW}${effort} effort${RESET}")

usage=""
if [ -n "$used_pct" ] && [ "$used_pct" != "null" ]; then
  usage=$(printf '%.0f%% ctx' "$used_pct")
fi
[ -n "$usage" ] && parts+=("${DIM}${usage}${RESET}")

out="${parts[0]}"
for part in "${parts[@]:1}"; do
  out="${out}${SEP}${part}"
done

printf '%s\n' "$out"
