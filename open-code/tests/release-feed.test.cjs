// Run with Node's test runner and Renovate's installed jsonata dependency (see docs/developer.md).
const assert = require('node:assert/strict');
const { readFileSync, readdirSync } = require('node:fs');
const { resolve } = require('node:path');
const { test } = require('node:test');
const jsonata = require('jsonata');
const root = resolve(__dirname, '../..');
const config = JSON.parse(readFileSync(resolve(root, 'renovate.json')));
const expression = jsonata(config.customDatasources['opencode-desktop'].transformTemplates[0]);
// Compare serialized API data, not JSONata's intentionally null-prototype objects.
async function evaluate(value) {
  return JSON.parse(JSON.stringify(await expression.evaluate(value)));
}
const rpm = 'opencode-desktop-linux-x86_64.rpm';
const cli = 'opencode-linux-x64.tar.gz';
function artifact(name, filename) {
  return { channel: 'latest', name, distribution: 'opencode', version: '2.1.4', metadata: { files: {
    [filename]: { url: 'https://opencode.ai/files/bin/2.1.4/' + filename, sha256: 'a'.repeat(64), size: 100 },
  } } };
}
function fixture() {
  return { channel: 'latest', artifacts: [artifact('desktop', rpm), artifact('cli', cli)] };
}
const expected = { releases: [{ version: '2.1.4', isStable: true }] };
test('matching stable desktop and CLI are eligible', async () => {
  assert.deepEqual(await evaluate(fixture()), expected);
});
const rejected = {
  'empty response': () => ({}),
  'wrong aggregate channel': f => { f.channel = 'beta'; },
  'wrong desktop channel': f => { f.artifacts[0].channel = 'beta'; },
  'wrong CLI channel': f => { f.artifacts[1].channel = 'dev'; },
  'wrong distribution': f => { f.artifacts[0].distribution = 'github'; },
  'missing desktop': f => { f.artifacts.shift(); },
  'missing CLI': f => { f.artifacts.pop(); },
  'missing RPM': f => { delete f.artifacts[0].metadata.files[rpm]; },
  'missing CLI archive': f => { delete f.artifacts[1].metadata.files[cli]; },
  'CLI version mismatch': f => { f.artifacts[1].version = '2.1.3'; },
  'v1': f => { f.artifacts.forEach(a => { a.version = '1.18.33'; }); },
  'v3': f => { f.artifacts.forEach(a => { a.version = '3.0.0'; }); },
  'prerelease': f => { f.artifacts.forEach(a => { a.version = '2.2.0-beta.1'; }); },
  'leading zero': f => { f.artifacts.forEach(a => { a.version = '2.01.4'; }); },
  'malformed version': f => { f.artifacts.forEach(a => { a.version = '2.1'; }); },
  'wrong RPM URL version': f => { f.artifacts[0].metadata.files[rpm].url = 'https://opencode.ai/files/bin/2.1.3/' + rpm; },
  'wrong CLI URL host': f => { f.artifacts[1].metadata.files[cli].url = 'https://example.com/' + cli; },
  'bad RPM hash': f => { f.artifacts[0].metadata.files[rpm].sha256 = 'bad'; },
  'missing CLI hash': f => { delete f.artifacts[1].metadata.files[cli].sha256; },
  'zero RPM size': f => { f.artifacts[0].metadata.files[rpm].size = 0; },
  'fractional RPM size': f => { f.artifacts[0].metadata.files[rpm].size = 0.5; },
  'fractional CLI size': f => { f.artifacts[1].metadata.files[cli].size = 100.5; },
  'string CLI size': f => { f.artifacts[1].metadata.files[cli].size = '100'; },
  'duplicate desktop': f => { f.artifacts.push(structuredClone(f.artifacts[0])); },
  'duplicate CLI': f => { f.artifacts.push(structuredClone(f.artifacts[1])); },
};
for (const [name, mutate] of Object.entries(rejected)) {
  test('rejects ' + name, async () => {
    const f = fixture();
    assert.deepEqual(await evaluate(mutate(f) || f), { releases: [] });
  });
}
test('inactive rollout fallbacks remain eligible', async () => {
  const f = fixture();
  f.artifacts.forEach(a => { a.active = false; });
  assert.deepEqual(await evaluate(f), expected);
});
test('all three maintained spec dependencies remain discoverable', () => {
  const found = [];
  for (const manager of config.customManagers) {
    for (const pattern of manager.managerFilePatterns) {
      const filePattern = new RegExp(pattern.slice(1, -1));
      for (const dir of readdirSync(root, { withFileTypes: true }).filter(d => d.isDirectory())) {
        const path = dir.name + '/' + dir.name + '.spec';
        if (!filePattern.test(path)) continue;
        const match = new RegExp(manager.matchStrings[0]).exec(readFileSync(resolve(root, path), 'utf8'));
        assert.ok(match, path);
        found.push([path, match.groups.depName]);
      }
    }
  }
  assert.deepEqual(found.sort(), [
    ['open-code/open-code.spec', 'opencode-desktop'],
    ['python-hf-xet/python-hf-xet.spec', 'huggingface/xet-core'],
    ['python-huggingface-hub/python-huggingface-hub.spec', 'huggingface_hub'],
  ]);
});
test('OpenCode is semver v2-only with rollback proposals disabled', () => {
  const manager = config.customManagers.find(m => m.managerFilePatterns.some(p => p.includes('open-code/')));
  const rule = config.packageRules.find(r => r.matchDatasources?.includes('custom.opencode-desktop'));
  assert.equal(manager.versioningTemplate, 'semver');
  assert.equal(rule.allowedVersions, '>=2.0.0 <3.0.0');
  assert.equal(rule.ignoreUnstable, true);
  assert.equal(rule.rollbackPrs, false);
  assert.deepEqual(config.packageRules[0], { matchUpdateTypes: ['minor', 'patch', 'pin', 'digest'], automerge: true });
});
