# OpenCode v2 / Fedora 44 validation — 2026-10-25

Implementation branch: `feat/opencode_v2`, starting revision
`13e136ea43514e9124e03d826b5d31e00f091003`. Before repository-wide validation,
the same branch was fast-forwarded to current `main` at
`99cbdd003f97bd94019d47d7d0767f594dcc7421`, preserving the already-merged
Bun 1.4.4 and LLM Wiki 0.6.13 updates. The OpenCode implementation remains 2.1.4.
This report records observed results, not merge or COPR publication authority.

## Selected inputs

Stable desktop and CLI metadata both advertised **2.1.4**. Downloads were checked
against the service's versioned URL, byte size, and SHA-256 metadata:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| opencode-desktop-linux-x86_64.rpm | 205951905 | `6f4fb4c25b26646b60615462ec9810707d185832497699a424e3ce506bbacb03` |
| opencode-linux-x64.tar.gz | 114420630 | `2edaf8cf96e81dec5ee996a3196b03345cf59e5a1673d83a4599bb4afc5c5f6d` |

The actual published Fedora 44 v1 upgrade baseline is
**open-code-1.19.4-1.fc44.x86_64**, newer than the plan's inspection snapshot.
Downloaded binary RPM SHA-256:
`684513b11e3bfa18566f321efebf8573342a185ce6640dadc2986bbad0070a3d`.
It was obtained with DNF from the configured published COPR repository, not the
host's installation.

Read-only COPR API inspection confirmed the OpenCode SCM configuration points to
`https://github.com/Iolaum/copr-repo`, branch `main`, subdirectory
`open-code`, spec `open-code.spec`. The project advertises Fedora 43
and Fedora 44 x86_64 repositories. No settings were changed; webhook delivery
and a future build from this branch have not been proven.

## Release discovery

- Pinned Renovate **44.181.5** passed repository-mode strict config validation.
- All **29/29** fixture/config tests passed via Node's test runner using Renovate's
  installed JSONata dependency, including fractional byte-size rejection added
  after independent review.
- Actual non-writing extraction found **5 files / 5 dependencies**.
- Actual lookup used the aggregate stable endpoint and selected OpenCode 2.1.4.
- A container-only spec copy at 2.1.3 proposed the patch update to 2.1.4.
- A copy at 2.99.0 proposed no OpenCode rollback.
- A nonexistent distribution endpoint returned HTTP 404: lookup failed with
  `no-result`, with no OpenCode update or alternate datasource fallback.
- An HTTP 200 text response (the upstream LICENSE) failed JSON parsing and
  likewise produced no OpenCode update/fallback.
- The unrelated PyPI dependency remained discoverable and lookup worked. Three
  unrelated GitHub dependencies were extracted but skipped lookup as
  `github-token-required`; no credentials were mounted for these tests.

Implementation detail: Renovate uses `https://opencode.ai/update/api/latest`,
the aggregate form of the same stable desktop/CLI records. One native JSONata
transform can require both records and artifacts; separate HTTP documents cannot
be joined by a Renovate transformation. This changes neither the release channel
nor packaging architecture, and introduces no updater service. The other four
managers only migrate the deprecated `fileMatch` key mechanically to
`managerFilePatterns`; their regexes and merge behavior remain unchanged.

Reproduction commands are in [developer notes](developer.md#opencode-release-feed-regression-checks).

## Isolation and remaining gates

Tool installation, builds, and application execution use disposable Fedora 44
containers. Source is mounted read-only and copied into the container. Only a
non-secret temporary evidence directory is shared; concurrent containers use
SELinux shared `:z` labeling. No host home, credentials, desktop sockets,
user bus, package database, privileged mode, or sandbox-disabling option is used.
A nested unprivileged user-namespace preflight succeeded as the container test
user with default Podman security settings; this is a harness prerequisite, not
desktop-ready evidence.

## Fedora 44 candidate

The targeted full RPM build passed dependency resolution, strict spec lint,
source fetching, and version/root-help/service-help checks for both public CLI
names and the private desktop CLI. The final extracted desktop tree matched
upstream across all **96 entries**, including file hashes, entry types, modes,
and symlink targets; no build-ID links were present.
The final public executable and relative compatibility symlink also passed
version/resolution checks.

- Identity: `open-code-2.1.4-1.fc44.x86_64`.
- Binary RPM SHA-256: `268e108b5eec12b47bc792981458bef265b2edca67f63150bdcd2229e8b260e1`.
- Source RPM SHA-256: `d5be2d0adc932f1d2c35c1edd8dbb52a29e00304848685cdefa1546e09c2e3a7`.

CI now selects `fedora:44`; YAML parsing and assertions verified the container
target, unchanged `ubuntu-24.04` runner, and unchanged push/pull-request/manual
triggers. Existing dependency, lint, source-fetch, and full-build gates remain.
README, developer instructions, and repository AGENTS guidance agree on Fedora 44
for local validation.

## Repository-wide Fedora 44 regression

All **5/5** discovered specs passed `dnf builddep`, strict `rpmlint`,
`spectool -Rg`, and complete `rpmbuild -ba` on the refreshed branch:

| Spec | Tested version | Result |
| --- | --- | --- |
| bun | 1.4.4 | PASS |
| llm-wiki | 0.6.13 | PASS |
| open-code | 2.1.4 | PASS |
| python-hf-xet | 1.5.0-2 | PASS |
| python-huggingface-hub | 1.33.0 | PASS |

A separate clean container resolved and installed published
`python3-hf-xet-1.5.0-2.fc44.x86_64` from `iolaum/aitoolkit` and
`python3-mcp-1.26.0-1.fc44.noarch` from Fedora. Both imported successfully.
This proves published dependency availability, not same-change dependency
resolution from locally rebuilt RPMs. No unrelated package versions or
packaging strategies were changed by this implementation.

## Isolated installation, upgrade, and desktop acceptance

- Fresh DNF installation resolved the candidate dependencies. Both public names
  and the private bundled CLI passed installed-package version, root-help, and
  service-help checks; RPM ownership and relative symlink resolution passed.
- DNF upgraded the published `open-code-1.19.4-1.fc44.x86_64` package to
  `open-code-2.1.4-1.fc44.x86_64` normally, with no force/replace-file flags.
  No unexpected package removal occurred. All **18** removed v1 file paths
  were absent afterward; public commands, desktop entries, icons, metainfo,
  LICENSE, and ownership checks passed.
- A synthetic competing RPM owning `/usr/bin/opencode` caused the expected
  normal file-conflict rejection. Its executable content and ownership were
  unchanged; the candidate was not installed in that transaction.
- A synthetic user-local command placed first in PATH shadowed the package
  without an RPM conflict, while `/usr/bin/opencode` still reported v2.1.4.
  The test-local file was removed; no profile files were edited.
- An unprivileged test user launched the installed desktop with a private
  Xvfb display and D-Bus session, with no sandbox-disabling flags. Window
  evidence identified `OpenCode`, class `ai.opencode.desktop`, 1280x800.
  The captured screenshot was visually inspected: the session screen, composer,
  model selector, project selector, and provider-connect control were rendered,
  with no visible crash/error/loading state.
- Bounded desktop logs contain expected minimal-container system-bus, portal,
  Bluetooth, and absent-DRM warnings, plus an upstream missing internal
  `resources/icons/icon.png` warning. The desktop still reached the rendered
  usable screen. The packaged launcher icon and payload preservation checks pass.
- Test containers were removed after each transaction; application/display/bus
  processes stayed in container namespaces. No host home, credentials, display,
  bus, package database, packages, or live profiles were accessed or changed.

Coverage does **not** include physical GPU, native Wayland, GNOME/KDE launcher
integration, model inference, or real-profile/exhaustive session compatibility.

## Synthetic v1 data/configuration migration

The actual published v1.19.4 CLI imported the retained synthetic export fixture
and exported it again successfully. The application-created data/configuration
profile was snapshotted and SHA-256-manifested. Failed harness attempts were
discarded and restarted from a pristine disposable copy, not the source fixture.

After a normal DNF upgrade to the candidate, authenticated supported v2 APIs
proved the following on **two consecutive server startups**:

- `/api/experimental/migration/v1` reported `completed`.
- `/api/session` and `/api/session/ses_coprfixture20261025` returned exactly one
  matching fixture session with title `COPR v1 migration fixture`.
- `/api/session/ses_coprfixture20261025/message?order=asc` returned the original
  user message `msg_000000000001aaaaaaaaaaaaaa` and exact text
  `FEDORA44_COPR_V1_MIGRATION_MARKER_20261025`. There was one message on each
  startup, with identical identity/type; no duplication occurred.
- `/api/config` returned the migrated `copr-fixture` agent description and
  prompt-as-system text. The legacy `bash: deny` rule became a
  `shell` / `*` / `deny` permission, preserving the fixture restriction.
- The complete retained source fixture manifest (**4 files**) was unchanged afterward.

The v2 server requires its normal generated local password. An initial
unauthenticated harness probe could not read the APIs; the corrected harness
authenticates rather than disabling authentication. Generated local test
credentials are redacted from retained server logs. No model request or real
credentials/session data was used.

Focused synthetic fixtures, the API checker, safeguards, and reproduction
sequence are retained under [open-code/tests](../open-code/tests/README.md).
The retained checker passed a fresh container rerun, refuses host/root
execution (host refusal was explicitly tested), and requires the disposable fixture
profile. This proves the tested plain-text session and representative agent
configuration, not every historical session/tool/provider format.

## Review and publication boundary

Independent review found no packaging, strip, command-compatibility, or unrelated
Renovate regressions. Its low-severity fractional byte-size finding was fixed
and covered by two additional regression fixtures (29/29 total passing).

Hosted CI on the pushed implementation revision is a mandatory gate before
PR creation; the PR will link the hosted-run evidence. This request authorizes
a PR, not merge/COPR publication. Subsequent
merge, webhook-to-COPR build verification, installation from the newly published
repository, and hosted Renovate observation remain post-review release gates;
local validation does not prove those future outcomes.
