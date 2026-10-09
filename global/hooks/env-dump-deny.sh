#!/usr/bin/env bash
# PreToolUse (Bash) hook: deny a command that prints a whole environment or env file,
# since every secret in the output lands in the session transcript. Denied forms:
#   printenv, env                  with no variable name, also via docker exec,
#                                  docker compose exec, or ssh
#   docker inspect                 without -f/--format, or with a format that reads
#                                  .Config.Env, all of .Config, or {{json .}}
#   docker compose config          without --no-env-resolution, -q/--quiet, or a
#                                  listing flag (--services, --volumes, --profiles,
#                                  --images)
#   cat, head, tail, less          on an env file: .env, *.env, or .env.* other than
#                                  .env.example and .env.sample
#   grep                           on an env file, with -v or with a pattern that
#                                  names no key
# `env FOO=1 cmd` runs a command and passes. Like git-rewrite-ask.sh, it matches the
# raw command string, split at shell separators.
CMD=$(jq -r '.tool_input.command // empty')
[ -n "$CMD" ] || exit 0

deny() {
  jq -cn --arg r "$1 would print secrets into the transcript. Read one setting by key, e.g. \`docker compose exec -T <service> printenv <KEY>\`." \
    '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $r}}'
  exit 0
}

S='[[:space:]]'
N='[^[:space:]]'
segs=$(printf '%s\n' "$CMD" | sed -E 's/&&|\|\||[;|&()`]/\n/g')

# Quotes also end a command here, so `ssh host 'printenv'` and `sh -c "env"` match.
dump="(printenv($S+-$N*)*|env($S+(-$N*|[A-Za-z_][A-Za-z0-9_]*=$N*))*)$S*$"
local_dump="^$S*(sudo$S+)?$dump"
remote_dump="(^|$S)(docker$S+exec|docker(-|$S+)compose$S(.*$S)?exec|ssh)$S.*$S$dump"
while IFS= read -r seg; do
  [[ $seg =~ $local_dump || $seg =~ $remote_dump ]] && deny "Printing the whole environment"
done < <(printf '%s\n' "$segs" | tr "'\"" '\n\n')

inspect="docker$S+((container|image)$S+)?inspect($S|$)"
format="(^|$S)(-f|--format)"
env_format='\.Config\.Env|\.Config[[:space:]]*\}\}|\{\{[[:space:]]*json[[:space:]]+\.[[:space:]]*\}\}'
compose_config="docker(-|$S+)compose($S.*)?$S+config($S|$)"
compose_safe="(^|$S)(--no-env-resolution|-q|--quiet|--services|--volumes|--profiles|--images)($S|$)"

is_env_file() {
  local base=${1##*/}
  case $base in
    .env.example|.env.sample) return 1 ;;
    *.env|.env.*) return 0 ;;
  esac
  return 1
}

# Reader commands and an env file among their arguments.
check_reader() {
  local -a t=("$@")
  local i cmd tok pattern="" invert="" files=() skip_next=""
  for ((i = 0; i < ${#t[@]}; i++)); do
    cmd=${t[i]##*/}
    case $cmd in cat|head|tail|less|grep) break ;; esac
  done
  ((i < ${#t[@]})) || return 0
  for ((i++; i < ${#t[@]}; i++)); do
    tok=${t[i]//[\'\"]/}
    if [ -n "$skip_next" ]; then skip_next=""; continue; fi
    case $tok in
      '>'|'>>'|[0-9]'>'|[0-9]'>>') skip_next=1; continue ;;
      '>'*|[0-9]'>'*) continue ;;
      '<') continue ;;
      '<'*) tok=${tok#<} ;;
    esac
    if [ "$cmd" = grep ]; then
      case $tok in
        -e|--regexp) ((i++)); pattern=${t[i]//[\'\"]/}; continue ;;
        --regexp=*) pattern=${tok#*=}; continue ;;
        -e*) pattern=${tok#-e}; continue ;;
        -f|-m|-A|-B|-C|-d|-D|--file|--max-count|--after-context|--before-context|--context) ((i++)); continue ;;
        --invert-match) invert=1; continue ;;
        --*) continue ;;
        -*v*) invert=1; continue ;;
        -*) continue ;;
      esac
      if [ -z "$pattern" ]; then pattern=$tok; continue; fi
    else
      case $tok in -*) continue ;; esac
    fi
    files+=("$tok")
  done
  local f
  for f in "${files[@]}"; do
    is_env_file "$f" || continue
    [ "$cmd" != grep ] && deny "Reading an env file with $cmd"
    [ -n "$invert" ] && deny "grep -v on an env file"
    [[ $pattern =~ [A-Za-z_]{2,} ]] || deny "grep on an env file without a key name"
  done
}

while IFS= read -r seg; do
  if [[ $seg =~ $inspect ]] && { ! [[ $seg =~ $format ]] || [[ $seg =~ $env_format ]]; }; then
    deny "docker inspect without a narrow --format"
  fi
  if [[ $seg =~ $compose_config ]] && ! [[ $seg =~ $compose_safe ]]; then
    deny "docker compose config without --no-env-resolution"
  fi
  read -ra toks <<< "$seg"
  check_reader "${toks[@]}"
done <<< "$segs"
exit 0
