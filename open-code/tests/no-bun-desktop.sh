#!/bin/bash
set -euo pipefail
if [ ! -f /run/.containerenv ] || [ "$(id -u)" -eq 0 ] || [ "$HOME" != /home/tester ]; then
  echo "Run only as the disposable unprivileged container tester" >&2
  exit 1
fi
cd /home/tester/desktop-project
Xvfb :99 -screen 0 1280x800x24 -nolisten tcp > /home/tester/xvfb.log 2>&1 &
xvfb=$!
app=''
cleanup() { if [ -n "$app" ]; then kill "$app" 2>/dev/null || true; fi; kill "$xvfb" 2>/dev/null || true; wait 2>/dev/null || true; }
trap cleanup EXIT
export DISPLAY=:99
for i in $(seq 1 20); do if xdotool getdisplaygeometry >/dev/null 2>&1; then break; fi; sleep 1; done
/opt/OpenCode/ai.opencode > /home/tester/desktop.log 2>&1 &
app=$!
window=''
for i in $(seq 1 60); do
  kill -0 "$app"
  window=$(xdotool search --onlyvisible --class 'ai.opencode.desktop' 2>/dev/null | head -1 || true)
  if [ -n "$window" ]; then break; fi
  sleep 1
done
test -n "$window"
sleep 12
xdotool getwindowname "$window" > /home/tester/desktop-window.txt
xdotool getwindowgeometry "$window" >> /home/tester/desktop-window.txt
import -window root /home/tester/desktop.png
cat /home/tester/desktop-window.txt
printf 'DESKTOP_SCREENSHOT_CAPTURED_REQUIRES_INSPECTION\n'
