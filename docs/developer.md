# Developer Notes

This document collects maintainer-facing notes for the COPR packaging repository.

## Renovate

The Renovate app from Mend is installed for this repository.

- Renovate app: `https://github.com/apps/renovate`
- Mend settings: `https://developer.mend.io/github/Iolaum`

This repository uses Renovate to propose version bumps for annotated RPM spec files.
The current spec annotations live next to the `Version:` field and identify the upstream release source for each package.

Each package owns its own directory so COPR subdirectory configuration, CI, and any future package-specific files stay isolated.

- `open-code/` with `open-code/open-code.spec`
- `python-hf-xet/` with `python-hf-xet/python-hf-xet.spec`
- `python-huggingface-hub/` with `python-huggingface-hub/python-huggingface-hub.spec`

Renovate configuration lives in `renovate.json`.

### OpenCode release-feed regression checks

Use a disposable Node container, with no credentials or host home mounted. The
pinned Renovate version provides its actual JSONata dependency for the fixture
suite. Tools and caches live only in the container; no host install is needed.

```bash
podman run --rm -i -v "$PWD":/src:ro,Z docker.io/library/node:24 bash <<'EOF'
set -euo pipefail
mkdir -p /work /tools
cp -a /src/. /work/
cd /tools
npm install --no-audit --no-fund renovate@44.181.5
export PATH="/tools/node_modules/.bin:$PATH"
export NODE_PATH=/tools/node_modules
export RENOVATE_CACHE_DIR=/tmp/renovate-cache
cd /work
renovate-config-validator --no-global --strict renovate.json
node --test open-code/tests/release-feed.test.cjs
LOG_LEVEL=debug renovate --platform=local --dry-run=extract --enabled-managers=custom.regex
LOG_LEVEL=debug renovate --platform=local --dry-run=lookup --enabled-managers=custom.regex
EOF
```

Extraction must still find every spec. Unauthenticated GitHub lookups may be
reported as `github-token-required`; this is not an OpenCode lookup failure.
For update-selection testing, change only the container copy's OpenCode version
to an older v2 release and repeat lookup. Test a version ahead of the feed too;
it must not propose a rollback. The fixture suite covers missing/duplicate
records, wrong channel/major, prereleases, invalid versions, missing files,
wrong versioned URLs, malformed hash/size metadata, and rollout fallbacks.

## Maintainer expectations

- review Renovate pull requests before merge, especially for major upstream releases
- keep CI green on Renovate pull requests before merging
- verify that updated spec files still fetch sources and build cleanly
- treat `Release:` as a maintainer-managed field when packaging changes require more than a plain upstream version bump

## COPR rebuild automation

COPR packages in this repository should be configured as SCM packages that build from the `main` branch of the GitHub repository.

- set `Source Type` to `SCM`
- set `Clone URL` to the repository URL
- set `Committish` to `main`
- set the package `subdirectory` to its package folder, such as `open-code/`, `python-hf-xet/`, or `python-huggingface-hub/`
- set the spec path inside that folder, such as `open-code/open-code.spec`, `python-hf-xet/python-hf-xet.spec`, or `python-huggingface-hub/python-huggingface-hub.spec`
- enable `Webhook rebuild` in the COPR package configuration
- add the COPR webhook URL to the GitHub repository webhook settings with content type `application/json`

The expected result is that each new commit to `main` triggers a COPR rebuild for the affected package configuration.

## CI and local validation

The CI workflow discovers package specs from the package directories rather than a shared `specs/` directory.

- CI and local acceptance use Fedora 44 (`fedora:44`); the GitHub Actions runner remains Ubuntu 24.04
- prefer running local validation in a temporary Fedora 44 container with Podman rather than installing RPM tooling on the host
- changing the CI target does not modify COPR chroots or retire Fedora 43
- start the container in an existing workdir such as `/root`, copy the repository into `/work`, and run validation from `/work`
- enable the published `iolaum/aitoolkit` COPR repository before resolving build dependencies
- full validation iterates over `*/*.spec`
- targeted validation can replace the loop with a single spec path when working on one package
- run `dnf builddep`, `rpmlint`, `spectool -Rg`, and `rpmbuild -ba` for each validated spec file

## Package-specific notes

### open-code

- track stable v2 desktop publication, not the v1 GitHub Releases stream; Renovate reads `https://opencode.ai/update/api/latest`, the aggregate form of the same stable desktop and CLI records
- the aggregate endpoint lets one native JSONata transform require exactly one matching stable desktop/CLI pair, both expected files, versioned URLs, SHA-256 metadata, and positive integer byte sizes; no hosted updater, custom script datasource, or channel change is involved
- constrain updates to semver `>=2.0.0 <3.0.0`, ignore unstable releases, and disable rollback proposals; unavailable/malformed metadata must fail closed
- metadata readiness is not executable or byte-integrity proof: source fetching and all three packaged CLI checks remain acceptance gates; recheck downloaded SHA-256 hashes for migration acceptance
- repackage the version-pinned `https://opencode.ai/files/bin/<version>/opencode-desktop-linux-x86_64.rpm` and matching `opencode-linux-x64.tar.gz`; LICENSE comes from the corresponding `v<version>` Git tag
- install the standalone CLI as `/usr/bin/opencode` and own the relative `/usr/bin/opencode-cli -> opencode` compatibility symlink; do not add package-wide Provides/Conflicts/Obsoletes merely for the command name
- preserve `/opt/OpenCode/ai.opencode` and its private `resources/opencode-cli`; desktop entries use the desktop executable, not the public CLI
- keep the package scoped to `x86_64` unless upstream release artifacts and repository architecture policy change together
- preserve the upstream desktop payload under `/opt/OpenCode` as-is
- check version, root help, and `service --help` for both public CLI names and the bundled CLI; v2 reports `opencode v<version>`
- compare the extracted candidate `/opt/OpenCode` tree with the upstream RPM, including symlink targets; do not introduce build-ID links
- test installation and v1 upgrades only in disposable Fedora containers with private home/XDG state; never mount the maintainer’s home, credentials, package database, desktop sockets, or user bus
- a virtual-display startup does not prove physical GPU, Wayland, GNOME/KDE launcher integration, or real-profile migration compatibility
- keep strip-related BRP post-processing disabled unless the rebuilt package is proven to preserve the upstream binary payloads correctly

### python-hf-xet

- keep the package naming Fedora-style: source package `python-hf-xet`, installable package `python3-hf-xet`
- use the upstream Linux `cp37-abi3` wheel for standard Fedora builds on `x86_64`
- do not switch to the upstream `cp313t` or `cp314t` wheels unless the packaging target explicitly changes to free-threaded Python
- avoid switching this package to a source build unless the repository intentionally adopts a Rust-native packaging workflow for it

### python-huggingface-hub

- keep the package naming Fedora-style: source package `python-huggingface-hub`, installable package `python3-huggingface-hub`
- package the upstream PyPI source release rather than vendoring the upstream git tree
- keep the package scoped to the repository's active `x86_64` target while `hf-xet` remains provided here as an `x86_64` package
- keep the upstream `hf` and `tiny-agents` entry points, and keep `python3-mcp` available so `tiny-agents` does not ship as a half-working CLI
- keep static `BuildRequires` for now instead of `%generate_buildrequires`
- reason: dynamic build requirements would pull `python3dist(hf-xet)` into `dnf builddep` resolution for CI, and GitHub Actions can only resolve that when the dependency has already been published in the COPR repo
- current CI enables the published `iolaum/aitoolkit` COPR repository before `dnf builddep`, which is enough for already-published dependencies but does not validate same-PR changes to both a dependency package and a dependent package
- revisit `%generate_buildrequires` only after CI can also resolve repo-local package outputs during the build-dependency phase

## Retired-package COPR handoff

Repository maintenance for `bun` and `llm-wiki` has ended. Their specs and
Renovate managers are removed; historical reports and Git history remain.
This does not uninstall existing copies or remove published RPMs/build history.

Owner: Nikolaos or a separately authorized operator. Outside this repository PR:

- Inspect each retired package’s SCM, webhook/rebuild settings and outstanding
  builds/updates. Disable or retire only its rebuild paths; preserve maintained
  packages and shared automation. Do not blindly delete the project-wide webhook.
- Decide separately whether to retain published artifacts/history, provide a
  retirement notice or migration guidance, and close outstanding update PRs.
- Verify the resulting automation state and continued publication of maintained
  packages; retain a separate operational report.

Until that follow-up is completed, live jobs may still target the removed
directories and fail after merge. Coordinate timing before merge; this change
does not alter live COPR or GitHub settings.
