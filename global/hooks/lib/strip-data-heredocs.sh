# Sourced by the PreToolUse Bash hooks. strip_data_heredocs prints a command with each
# heredoc body removed, except a body fed to a shell, ssh, eval, or a container exec,
# which runs as commands; any other body is that program's data.
heredoc_re="(^|[^<])<<-?[[:space:]]*['\"]?([A-Za-z_][A-Za-z0-9_]*)"
shell_like='bash|sh|zsh|dash|ksh|ssh|eval|docker|docker-compose|podman|kubectl'
strip_data_heredocs() {
  local line delim="" keep="" out="" word
  local -a words
  while IFS= read -r line; do
    if [ -n "$delim" ]; then
      [ -n "$keep" ] && out+="$line"$'\n'
      [ "${line#"${line%%[!$'\t']*}"}" = "$delim" ] && delim=""
      continue
    fi
    out+="$line"$'\n'
    [[ $line =~ $heredoc_re ]] || continue
    delim=${BASH_REMATCH[2]}
    read -ra words <<< "$(printf '%s\n' "${line%%<<*}" | sed -E 's/.*(&&|\|\||[;|&()`])//')"
    word=""
    for word in "${words[@]}"; do
      [[ $word == sudo || $word =~ ^[A-Za-z_][A-Za-z0-9_]*= ]] || break
    done
    [[ ${word##*/} =~ ^($shell_like)$ ]] && keep=1 || keep=""
  done <<< "$1"
  printf '%s' "$out"
}
