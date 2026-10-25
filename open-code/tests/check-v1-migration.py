import base64, json, os, pathlib, re, signal, subprocess, time, urllib.request, urllib.error
# This fixture harness must never run against a workstation profile.
if not pathlib.Path('/run/.containerenv').is_file() or os.geteuid() == 0:
    raise SystemExit('Run only as the unprivileged tester inside an isolated Podman container')
home=pathlib.Path.home()
if home != pathlib.Path('/home/tester'):
    raise SystemExit('Expected the disposable /home/tester profile')
os.environ.update(HOME=str(home), XDG_CONFIG_HOME=str(home/'.config'), XDG_DATA_HOME=str(home/'.local/share'), XDG_CACHE_HOME=str(home/'.cache'), XDG_STATE_HOME=str(home/'.local/state'))
fixture_config=json.loads((home/'.config/opencode/opencode.json').read_text())
if fixture_config.get('agent',{}).get('copr-fixture',{}).get('description') != 'COPR_MIGRATION_CONFIG_MARKER_20261025':
    raise SystemExit('Expected the non-secret v1 fixture configuration')
sid='ses_coprfixture20261025'
mid='msg_000000000001aaaaaaaaaaaaaa'
marker='FEDORA44_COPR_V1_MIGRATION_MARKER_20261025'
base='http://127.0.0.1:4180'
password=None
def get(path):
    headers={} if password is None else {'Authorization':'Basic '+base64.b64encode(('opencode:'+password).encode()).decode()}
    request=urllib.request.Request(base+path,headers=headers)
    with urllib.request.urlopen(request,timeout=5) as response: return json.load(response)
def save(name,value): (home/name).write_text(json.dumps(value,indent=2)+'\n')
previous=None
for round in (1,2):
    password=None
    log=(home/f'v2-round-{round}.log').open('w')
    process=subprocess.Popen(['/usr/bin/opencode','serve','--hostname','127.0.0.1','--port','4180'],cwd=home/'project',stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    try:
        deadline=time.monotonic()+90
        status=None
        while time.monotonic()<deadline:
            if process.poll() is not None: raise RuntimeError(f'v2 server exited {process.returncode}')
            try:
                for line in (home/f'v2-round-{round}.log').read_text().splitlines():
                    if line.startswith('server password '): password=line.removeprefix('server password ')
                status=get('/api/experimental/migration/v1')
                if status.get('status')=='error': raise RuntimeError(status)
                if status.get('status')=='completed': break
            except (urllib.error.URLError,TimeoutError,ConnectionError): pass
            time.sleep(1)
        assert status and status.get('status')=='completed', status
        sessions=get('/api/session')
        matched=[s for s in sessions['data'] if s['id']==sid]
        assert len(matched)==1, sessions
        assert matched[0]['title']=='COPR v1 migration fixture', matched
        session=get('/api/session/'+sid)
        messages=get('/api/session/'+sid+'/message?order=asc')
        matching=[m for m in messages['data'] if m['id']==mid]
        assert len(matching)==1, messages
        assert matching[0]['text']==marker, matching
        config=get('/api/config')
        agents=[e['info']['agents']['copr-fixture'] for e in config if e.get('type')=='document' and 'copr-fixture' in e.get('info',{}).get('agents',{})]
        assert agents, config
        agent=agents[-1]
        assert agent['description']=='COPR_MIGRATION_CONFIG_MARKER_20261025', agent
        assert agent['system']=='Keep the non-secret Fedora 44 migration marker.', agent
        assert any(p['action']=='shell' and p['resource']=='*' and p['effect']=='deny' for p in agent['permissions']), agent
        current=sorted((m['id'],m['type']) for m in messages['data'])
        if previous is not None: assert current==previous, (previous,current)
        previous=current
        for name,value in [('status',status),('sessions',sessions),('session',session),('messages',messages),('config',config)]: save(f'v2-round-{round}-{name}.json',value)
        print('V2_SUPPORTED_API_MIGRATION_PASS',round,sid,mid,'message_count',len(current),'config_prompt_and_shell_deny_preserved',flush=True)
    finally:
        if process.poll() is None:
            os.killpg(process.pid,signal.SIGTERM)
            try: process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid,signal.SIGKILL); process.wait(timeout=5)
        log.close()
        path=home/f'v2-round-{round}.log'
        path.write_text(re.sub(r'(?m)^server password .+$','server password [redacted local test credential]',path.read_text()))
print('REPEATED_STARTUP_NO_DUPLICATION_PASS',flush=True)
