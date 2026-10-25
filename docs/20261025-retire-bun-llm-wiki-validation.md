# Bun and LLM Wiki retirement validation — 2026-10-25

## Candidate and scope

Branch: `feat/retire-bun-llm-wiki`, based on
`1c739ff23869cd632fea288edca9f812d61ff9f3`. This report accompanies the tested
repository-removal candidate; the implementation PR identifies its exact head.
All three remaining specs and `.github/workflows/check.yml` are unchanged from
that base. Historical reports, changelogs and the unrelated untracked OpenCode
plan were preserved. No live COPR/GitHub settings were changed.

The implementation removes both package specs and their dedicated Renovate
managers, updates current maintenance guidance and three-package extraction
expectations, and retains focused container-only no-Bun acceptance checks.

## Local results

| Gate | Observed result |
| --- | --- |
| OpenCode 2.1.4-1 full Fedora 44 packaging checks | PASS |
| python-hf-xet 1.5.0-2 full Fedora 44 packaging checks | PASS |
| python-huggingface-hub 1.33.0-1 full Fedora 44 packaging checks | PASS |
| Renovate 44.181.5 strict repository config validation | PASS |
| Complete release-feed fixtures | 29/29 PASS, none skipped |
| Actual non-writing Renovate extraction | 3 files / 3 dependencies |
| Normal DNF OpenCode installation without Bun | PASS |
| Installed public/private CLI checks and command ownership | PASS |
| Authenticated non-model API and observable local plugin setup | PASS |
| Rendered desktop under private Xvfb/D-Bus | PASS; screenshot inspected |
| Bun absence after service/plugin and desktop execution | PASS |
| Desktop payload preservation | PASS; 95 descendants plus root unchanged |
| Disposable container/process cleanup | PASS |

Full packaging checks mean `dnf builddep`, strict `rpmlint`, `spectool -Rg` and
`rpmbuild -ba`, including each spec’s normal `%check`. OpenCode was built first
in its own clean Fedora 44 container. After focused runtime acceptance passed,
the two Python specs were validated in a separate disposable Fedora 44 container
with the published COPR repository enabled for existing build dependencies.
This does not prove installation of the Python packages or resolution against
same-change local dependency outputs.

Actual Renovate extraction found only:

- `open-code`: `custom.opencode-desktop` / `opencode-desktop`
- `python-hf-xet`: `github-releases` / `huggingface/xet-core`
- `python-huggingface-hub`: `pypi` / `huggingface_hub`

The documented unauthenticated `github-token-required` limitation applies to
GitHub lookup, not extraction. No credentials were mounted. OpenCode’s native
datasource, v2-only policy, fail-closed fixtures and rollback protection remain
unchanged. This run did not repeat live lookup/update-selection experiments.

## Artifact identity and runtime proof

Selected installed candidate: `open-code-2.1.4-1.fc44.x86_64`.

| Artifact | SHA-256 |
| --- | --- |
| Candidate binary RPM | `da06d036ddd6d356373960fa346678436d0023a21199ec3aa250cd7d39796b7c` |
| Candidate source RPM | `7ad9124880fdd47c9e90c5fc3424aa892c589c79b0e5253b5f41fc0a616807c1` |
| Upstream desktop RPM | `6f4fb4c25b26646b60615462ec9810707d185832497699a424e3ce506bbacb03` |
| Upstream standalone CLI archive | `2edaf8cf96e81dec5ee996a3196b03345cf59e5a1673d83a4599bb4afc5c5f6d` |

Generated RPM requirements were inspected and contained no Bun package or
executable requirement. A separate fresh Fedora 44 runtime container installed
the candidate through ordinary DNF with `--exclude=bun --exclude=bunx` and no
COPR repository or force/replace-file flags. It did not inherit the build
environment. Package/PATH checks and a scan of the disposable profile found no
external Bun before or after runtime testing.

Both `/usr/bin/opencode` and `/usr/bin/opencode-cli`, plus the desktop’s private
`/opt/OpenCode/resources/opencode-cli`, passed installed version, root-help and
service-help checks. RPM ownership and the relative `opencode-cli -> opencode`
symlink passed.

The unprivileged checker started the actual server on container-local loopback,
used its normally generated local password privately, and obtained a supported
`/api/config` response. The local v2 plugin’s actual setup hook wrote exactly
`COPR_NO_BUN_PLUGIN_SETUP_20261025` with runtime version `2.1.4`. There were no
model calls, real profiles, provider credentials or third-party plugin packages.
Shutdown was bounded; retained service logs redact the generated password.

The desktop launched as the unprivileged tester with normal sandboxing under a
private Xvfb display and D-Bus session. The final captured `OpenCode` window was
1279×799 on a 1280×800 display. Visual inspection confirmed the rendered session
screen, composer, model selector, project selector and provider-connect control,
with no visible crash, error or stuck loading screen. Minimal-container portal,
system-bus and absent-device warnings do not establish full desktop integration.

The complete installed `/opt/OpenCode` tree matched the upstream RPM across
file hashes, entry types, modes and symlink targets; the package introduced no
build-ID links. Strip protections and original embedded runtime components were
not modified.

## Harness interruption and recovery

The first runtime attempt passed installation, CLI, API and plugin checks, then
stopped with `Permission denied` reading the desktop helper through a mode-700
temporary input directory. Execution paused and Nikolaos approved correcting
the harness path. This was not treated as desktop acceptance or an OpenCode/Bun
dependency failure.

The corrected harness copies the helper to container-local `/work` before
dropping privileges. No host permissions or sandbox controls were relaxed. The
complete runtime gate then passed, and passed again using the retained guarded
runner and fixture, with the final screenshot separately inspected. Independent
review then identified an assertion gap: a response could have been labelled
authenticated without requiring a captured password. The checker now refuses
empty/missing passwords before opening a request. Both negative cases passed a
focused rejection test, root-refusal guards and shell syntax checks passed, and
the complete retained runtime/desktop gate passed again with a nonempty password
required. That final screenshot was inspected too. Every test container was
removed, including the interrupted one.

## Reproduction and source fingerprints

Use the normal packaging loop in [developer notes](developer.md), the pinned
Renovate commands there, and the retained
[no-system-Bun acceptance sequence](../open-code/tests/README.md#no-system-bun-acceptance).
Builds, test-tool installation and application execution stay in disposable
containers. Source/input mounts are read-only; work, homes, XDG state, display
and session bus are private. No host home, credentials, desktop sockets, bus,
package database, privileged mode or sandbox-disabling flags were used.

Tested source SHA-256 values:

```text
e40aa7c6b7edc0a364e9dd36693be8bfdbbd6af24936bc8cb14325503ed1a98c  open-code/open-code.spec
7192fd07ce56ffbc97a282b594ac2a527fb902f1aae6c432180a3b027b0c53e9  python-hf-xet/python-hf-xet.spec
654e28b05a5b7b81dcf1be49400b31370d7c2e5d321defdb03ff807d7f5c513d  python-huggingface-hub/python-huggingface-hub.spec
777eb743beb89b30ff19333a5683560ac5e81773ce3e9475419ef3eef3fbef0b  open-code/tests/check-no-bun.py
6662027b68001e059075000356c432de438f7d6f398e8b60f308b3af45d1fd8a  open-code/tests/no-bun-runtime.sh
1cb9d870599d95ce4798b1ec98b3c745db75cb67775d717d95c00588bb6145fa  open-code/tests/no-bun-desktop.sh
aede25213d7fc4d3a1abee6285b5e1ff38dbc0e81fc3b3b5cea3dfce2ddabdfa  open-code/tests/fixtures/no-bun-plugin/index.ts
```

## Release boundary and remaining work

Local acceptance does not prove hosted CI, merge, publication, or live COPR
retirement. Consult the implementation PR’s checks for hosted CI on its exact
head; merge/publication are not authorized by this report. No local gate above
was skipped or counted from an interrupted attempt.

The separately authorized operator must follow the
[COPR handoff](developer.md#retired-package-copr-handoff): inspect and retire
only the two packages’ rebuild paths, decide artifact/history and outstanding-PR
policy separately, and verify maintained publication. Until then live jobs may
still target the removed directories and fail after merge. Existing installations
and published artifacts have not been removed.

Coverage is limited to this Fedora 44 x86_64 candidate and the deterministic
local plugin setup workflow. It does not prove arbitrary plugins or Bun-dependent
projects, model inference, physical GPU/native Wayland integration, real-profile
compatibility, or every possible runtime path.
