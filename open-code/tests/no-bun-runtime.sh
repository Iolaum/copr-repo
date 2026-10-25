#!/bin/bash
set -euo pipefail
if [ ! -f /run/.containerenv ] || [ "$(id -u)" -ne 0 ] || [ ! -d /src/open-code/tests ] || [ ! -d /input ] || [ ! -d /out ]; then
  echo "Run only as container root with disposable /src, /input and /out mounts" >&2
  exit 1
fi
collect() { for file in /home/tester/no-bun-service.log /home/tester/desktop.log /home/tester/xvfb.log; do if [ -f "$file" ]; then sed -E 's/(server password ).*/\1[redacted local test credential]/' "$file" > "/out/$(basename "$file")"; fi; done; }
trap collect EXIT
dnf install -y --exclude=bun --exclude=bunx python3 shadow-utils util-linux procps-ng findutils cpio xorg-x11-server-Xvfb xdotool ImageMagick dbus-x11
if rpm -q bun; then echo "Unexpected installed Bun" >&2; exit 1; fi
if command -v bun; then echo "Unexpected Bun executable" >&2; exit 1; fi
rpm -qpR /input/open-code-*.x86_64.rpm | tee /out/generated-requires.txt
if grep -E '(^|[/[:space:]])bun(x)?($|[[:space:](])' /out/generated-requires.txt; then exit 1; fi
dnf install -y --exclude=bun --exclude=bunx /input/open-code-*.x86_64.rpm
rpm -qa | sort > /out/installed-packages.txt
if rpm -q bun; then echo "Unexpected installed Bun" >&2; exit 1; fi
if command -v bun; then echo "Unexpected Bun executable" >&2; exit 1; fi
mkdir /upstream
(cd /upstream; rpm2cpio /input/upstream-desktop.rpm | cpio -idm --quiet)
python3 - <<'PY'
import hashlib, os, pathlib, stat
source=pathlib.Path('/upstream/opt/OpenCode')
target=pathlib.Path('/opt/OpenCode')
def manifest(root):
    result={}
    for path in sorted(root.rglob('*')):
        mode=path.lstat().st_mode
        value=os.readlink(path) if stat.S_ISLNK(mode) else hashlib.sha256(path.read_bytes()).hexdigest() if stat.S_ISREG(mode) else None
        result[str(path.relative_to(root))]=(mode,value)
    return result
s,t=manifest(source),manifest(target)
assert s == t, 'Upstream desktop payload changed'
import subprocess
assert '/usr/lib/.build-id' not in subprocess.check_output(['rpm','-ql','open-code'],text=True)
print('DESKTOP_PAYLOAD_IDENTICAL',len(s),'entries')
PY
useradd -m tester
mkdir -p /work
cp -a /src/open-code/tests /work/tests
install -d -o tester -g tester /home/tester/project/.opencode/plugins/copr-no-bun /home/tester/.config /home/tester/.local/share /home/tester/.cache /home/tester/.local/state /home/tester/runtime
chmod 700 /home/tester/runtime
cp /work/tests/fixtures/no-bun-plugin/index.ts /home/tester/project/.opencode/plugins/copr-no-bun/index.ts
chown -R tester:tester /home/tester
runuser -u tester -- unshare -Ur true
runuser -u tester -- env HOME=/home/tester COPR_NO_BUN_ACCEPTANCE=disposable-fixture python3 /work/tests/check-no-bun.py
# The desktop uses a fresh project, without re-running the exclusive marker fixture.
install -d -o tester -g tester /home/tester/desktop-project
install -m 0644 /work/tests/no-bun-desktop.sh /work/desktop.sh
runuser -u tester -- env HOME=/home/tester XDG_CONFIG_HOME=/home/tester/.config XDG_DATA_HOME=/home/tester/.local/share XDG_CACHE_HOME=/home/tester/.cache XDG_STATE_HOME=/home/tester/.local/state XDG_RUNTIME_DIR=/home/tester/runtime dbus-run-session -- bash /work/desktop.sh
if rpm -q bun; then echo "Unexpected installed Bun" >&2; exit 1; fi
if command -v bun; then echo "Unexpected Bun executable" >&2; exit 1; fi
if find /home/tester \( -name bun -o -name bunx \) -print -quit | grep .; then echo "Unexpected downloaded Bun" >&2; exit 1; fi
cp /home/tester/no-bun-service.log /home/tester/no-bun-config.json /home/tester/no-bun-plugin.json /home/tester/desktop.png /home/tester/desktop-window.txt /out/
# Desktop logs may contain a generated local server password. Retain only redacted logs.
sed -E 's/(server password ).*/\1[redacted local test credential]/' /home/tester/desktop.log > /out/desktop.log
printf 'NO_BUN_RUNTIME_DESKTOP_PASS\n'
