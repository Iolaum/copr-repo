"""Run only in an isolated Fedora Podman container as the disposable tester."""
import base64
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time
import urllib.error
import urllib.request

HOME = Path('/home/tester')
if not Path('/run/.containerenv').is_file() or os.geteuid() == 0 or Path.home() != HOME:
    raise SystemExit('Requires an unprivileged disposable /home/tester Podman profile')
if os.environ.get('COPR_NO_BUN_ACCEPTANCE') != 'disposable-fixture':
    raise SystemExit('Requires the explicit disposable-fixture guard')
os.environ.update(HOME=str(HOME), XDG_CONFIG_HOME=str(HOME/'.config'),
                  XDG_DATA_HOME=str(HOME/'.local/share'), XDG_CACHE_HOME=str(HOME/'.cache'),
                  XDG_STATE_HOME=str(HOME/'.local/state'))
project = HOME/'project'
fixture = project/'.opencode/plugins/copr-no-bun/index.ts'
if not fixture.is_file():
    raise SystemExit('Expected the local no-Bun fixture, not a real project')
version = subprocess.check_output(['/usr/bin/rpm', '-q', '--qf', '%{VERSION}', 'open-code'], text=True)

def no_bun(label):
    assert subprocess.run(['rpm', '-q', 'bun'], stdout=subprocess.DEVNULL).returncode != 0
    assert not shutil.which('bun') and not shutil.which('bunx')
    # The disposable profile must not acquire a downloaded standalone runtime.
    assert not list(HOME.rglob('bun')) and not list(HOME.rglob('bunx'))
    print('BUN_ABSENT', label, flush=True)

no_bun('before')
assert Path('/usr/bin/opencode-cli').is_symlink()
assert os.readlink('/usr/bin/opencode-cli') == 'opencode'
for command in ['/usr/bin/opencode', '/usr/bin/opencode-cli', '/opt/OpenCode/resources/opencode-cli']:
    assert subprocess.check_output(['rpm', '-qf', command], text=True).startswith('open-code-')
    assert subprocess.check_output([command, '--version'], text=True, timeout=30).strip() == 'opencode v'+version
    assert 'service' in subprocess.check_output([command, '--help'], text=True, stderr=subprocess.STDOUT, timeout=30)
    help_text = subprocess.check_output([command, 'service', '--help'], text=True, stderr=subprocess.STDOUT, timeout=30)
    assert all(word in help_text for word in ['start', 'status', 'stop'])
    print('INSTALLED_ENTRY_POINT_PASS', command, flush=True)

marker = HOME/'no-bun-plugin.json'
assert not marker.exists()
os.environ['COPR_NO_BUN_MARKER'] = str(marker)
logpath = HOME/'no-bun-service.log'
password = None

def get(path):
    assert password, 'Expected the generated local server password'
    headers = {'Authorization': 'Basic '+base64.b64encode(('opencode:'+password).encode()).decode()}
    request = urllib.request.Request('http://127.0.0.1:4180'+path, headers=headers)
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.load(response)

with logpath.open('w') as log:
    process = subprocess.Popen(['/usr/bin/opencode', 'serve', '--hostname', '127.0.0.1', '--port', '4180'],
                               cwd=project, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    try:
        deadline = time.monotonic()+90
        response = None
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError('OpenCode server exited: '+str(process.returncode))
            for line in logpath.read_text().splitlines():
                if line.startswith('server password '):
                    password = line.removeprefix('server password ').strip()
            if not password:
                time.sleep(1)
                continue
            try:
                response = get('/api/config')
                if marker.is_file():
                    break
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                pass
            time.sleep(1)
        assert password, 'Server did not provide a nonempty local password'
        assert isinstance(response, list), response
        assert marker.is_file(), 'Plugin setup did not produce its marker'
        observed = json.loads(marker.read_text())
        assert observed == {'marker': 'COPR_NO_BUN_PLUGIN_SETUP_20261025', 'version': version}, observed
        (HOME/'no-bun-config.json').write_text(json.dumps(response, indent=2)+'\n')
        print('AUTHENTICATED_NON_MODEL_API_PASS /api/config', flush=True)
        print('LOCAL_PLUGIN_SETUP_PASS', observed, flush=True)
    finally:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=5)
        logpath.write_text(re.sub(r'(?m)^server password .+$', 'server password [redacted local test credential]', logpath.read_text()))
no_bun('after-service-and-plugin')
print('NO_BUN_SERVICE_PLUGIN_PASS', flush=True)
