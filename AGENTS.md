# AGENTS.md

## Purpose

This repository maintains Fedora COPR packaging metadata and automation. It is not an upstream source mirror and it is not a local RPM repository.

## Scope

Agents should primarily modify:

- package spec files under package directories such as `bun/` and `open-code/`
- `.github/workflows/`
- `docs/`
- `README.md`
- `renovate.json`

Agents should not:

- commit upstream tarballs, ZIPs, RPMs, binaries, or generated repository metadata
- add whole upstream source trees to this repository
- introduce shared packaging abstractions unless repeated maintenance pain clearly justifies them

## Repository Layout

- `bun/bun.spec`: package Bun from upstream GitHub release binaries
- `open-code/open-code.spec`: repackage the upstream desktop RPM payload
- `.github/workflows/check.yml`: CI installs RPM tooling, installs build deps, runs `rpmlint`, `spectool -Rg`, and `rpmbuild -ba`
- `docs/developer.md`: maintainer notes for Renovate and COPR workflow
- `renovate.json`: version automation for annotated spec files

## General Rules

- Prefer the smallest correct change.
- Keep package-specific changes isolated to the relevant package directory unless docs, CI, or Renovate config also need updates.
- Preserve current package naming. The desktop package is `open-code`.
- Preserve current architecture assumptions unless explicitly asked to expand support. `x86_64` is the active target.
- Preserve existing spec-local conventions rather than normalizing files for style alone.
- Keep Renovate annotations next to `Version:` working when changing version handling.
- If packaging strategy changes, update `README.md`, `docs/developer.md`, CI, and `renovate.json` together when needed.
- Do not edit live COPR or GitHub settings from this repository. Document required manual configuration changes instead.

## Package-Specific Guardrails

### bun

- Package Bun from upstream GitHub release binaries, not from source, unless explicitly requested.
- Keep the optimized Linux `x64` upstream artifact unless the task explicitly changes architecture strategy.
- Preserve `%autochangelog` unless maintainers ask for a different changelog policy.

### open-code

- Preserve the upstream desktop RPM payload as-is for the default packaging flow.
- Do not re-enable RPM strip or related BRP post-processing steps without proving the bundled `opencode-cli` still works.
- Keep the CLI smoke checks meaningful; they are there to catch broken repackaging.
- Preserve the bundled `opencode-cli` binary unless the task explicitly changes packaging strategy.
- Preserve the current changelog style unless asked to change it.

## Validation

Prefer running validation in a temporary Fedora container with Podman rather than installing tooling on the host.

Use a command like:

```bash
podman run --rm -i \
  -v "$PWD":/src:ro,Z \
  --workdir /root \
  fedora:44 \
  bash <<'EOF'
set -euo pipefail

dnf install -y glibc-langpack-en dnf-plugins-core git rpmlint rpmdevtools rpm-build 'dnf-command(builddep)'
dnf copr enable -y iolaum/aitoolkit

mkdir -p /work
cp -a /src/. /work/
cd /work

for file in */*.spec; do
  dnf builddep -y "$file"
  rpmlint "$file" --strict
  spectool -Rg "$file"
  rpmbuild -ba "$file"
done
EOF
```

For a single package, use the same container setup and replace the loop with the target spec path.

Notes:

- Mount the repository read-only and copy it into the container so validation does not dirty the host worktree.
- Keep the Fedora version aligned with CI unless there is a reason to test another target.
- If validation cannot be run, state exactly which command was skipped and why.

## Adding A Package

- Create a dedicated top-level package directory with its own `.spec` file.
- Keep CI compatible with the existing `*/*.spec` discovery pattern.
- Add or update `renovate.json` if the package version should be automated.
- Document packaging strategy and install or verification notes in `README.md`.
- Add maintainer notes to `docs/developer.md` if the package has non-obvious constraints.

## Review Expectations

- Call out packaging risks first: source URL changes, architecture changes, dependency changes, install path changes, `%check` changes, strip behavior changes, or validation gaps.
- Treat changes to source artifact type, architecture support, or `open-code` strip behavior as high-risk.
