#!/usr/bin/env bash
# Feeds each command to env-dump-deny.sh as a PreToolUse event and checks whether it denies.
HOOK="$(dirname "$0")/../env-dump-deny.sh"
fail=0

check() {
  local want=$1 cmd=$2 got=pass
  [[ $(jq -cn --arg c "$cmd" '{tool_input: {command: $c}}' | bash "$HOOK") == *'"deny"'* ]] && got=deny
  if [ "$got" != "$want" ]; then
    printf 'FAIL: want %s, got %s:\n%s\n\n' "$want" "$got" "$cmd"
    fail=1
  fi
}

check deny 'printenv'
check deny 'env'
check deny "ssh host 'printenv'"
check deny 'sh -c "env"'
check deny 'cat .env'
check deny $'ssh host <<\'EOF\'\nenv\nEOF'
check deny $'bash <<EOF\nprintenv\nEOF'
check deny $'python3 - <<\'EOF\'\nprint(1)\nEOF\nprintenv'

check pass 'env FOO=1 make'
check pass 'printenv HOME'
check pass $'python3 - <<\'EOF\'\nassert "env" not in s\ns["env"] = {}\nEOF'
check pass $'cat > notes.txt <<EOF\nenv\nEOF'

[ "$fail" = 0 ] && echo "all passed"
exit "$fail"
