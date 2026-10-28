#!/usr/bin/env bash
# Feeds each command to desktop-ask.sh as a PreToolUse event and checks whether it asks.
HOOK="$(dirname "$0")/../desktop-ask.sh"
fail=0

check() {
  local want=$1 cmd=$2 got=pass
  [[ $(jq -cn --arg c "$cmd" '{tool_input: {command: $c}}' | bash "$HOOK") == *'"ask"'* ]] && got=ask
  if [ "$got" != "$want" ]; then
    printf 'FAIL: want %s, got %s:\n%s\n\n' "$want" "$got" "$cmd"
    fail=1
  fi
}

check ask 'xdotool key ctrl+s'
check ask 'cd /tmp && import -window root s.png'
check ask 'DISPLAY=:0 xwd -root -out s.xwd'
check ask 'x=$(gnome-screenshot -f s.png)'
check ask 'wmctrl -a Firefox'
check ask 'sudo /usr/bin/xdotool mousemove 10 10'
check ask 'import shot.png'
check ask "ssh host 'xdotool key a'"
check ask $'bash <<EOF\nwmctrl -c Firefox\nEOF'

check pass 'grep xdotool scripts/meld-titled'
check pass 'scripts/meld-titled a b'
check pass 'echo import'
check pass $'python3 - <<\'EOF\'\nimport os\nEOF'
check pass $'cat > notes.txt <<EOF\nxdotool key a\nEOF'

[ "$fail" = 0 ] && echo "all passed"
exit "$fail"
