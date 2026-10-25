# COPR Packaging Repository

This repository contains the packaging metadata and automation needed to publish selected upstream software through Fedora COPR.

## Current status

The COPR project that publishes the available packages is [iolaum/aitoolkit](https://copr.fedorainfracloud.org/coprs/iolaum/aitoolkit/).

Current published package status:

| Package | Status |
| --- | --- |
| `open-code` | [![Copr build status](https://copr.fedorainfracloud.org/coprs/iolaum/aitoolkit/package/open-code/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/iolaum/aitoolkit/package/open-code/) |
| `python-hf-xet` | [![Copr build status](https://copr.fedorainfracloud.org/coprs/iolaum/aitoolkit/package/python-hf-xet/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/iolaum/aitoolkit/package/python-hf-xet/) |
| `python-huggingface-hub` | [![Copr build status](https://copr.fedorainfracloud.org/coprs/iolaum/aitoolkit/package/python-huggingface-hub/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/iolaum/aitoolkit/package/python-huggingface-hub/) |

## Scope

The repository is intentionally focused on packaging and publication, not on mirroring upstream source trees or storing a hand-managed RPM repository.

It is used to:

- keep RPM spec files under version control
- let COPR fetch upstream release artifacts during builds
- build RPMs in Fedora infrastructure via COPR
- publish installable Fedora repositories for supported packages
- document packaging constraints, architecture choices, and maintenance workflow

It is not used to:

- maintain a local `createrepo_c` repository
- commit upstream release tarballs or binaries into git
- rebuild large upstream projects from source unless that becomes necessary later


## Packaging strategy

### [OpenCode](https://github.com/anomalyco/opencode)


- package name in this repository and in RPM metadata should be `open-code`
- approach: repackage stable **v2** desktop `.rpm` releases and install the matching standalone CLI artifact from `https://opencode.ai/files/bin/<version>/`
- primary architecture: `x86_64`
- secondary architecture: `aarch64` is planned but not yet enabled
- preserve the upstream desktop application payload as-is
- expose the standalone CLI as `opencode`, with an RPM-owned `opencode-cli -> opencode` compatibility symlink
- preserve the desktop’s private bundled `opencode-cli`; the desktop executable is `/opt/OpenCode/ai.opencode`, not either public CLI command

This approach is chosen because it matches the current local workflow of consuming upstream release artifacts and publishing them as installable packages, while moving repository generation and hosting into COPR.

Packaging note:

- `open-code` disables Fedora RPM strip-related BRP post-processing during rebuilds
- this protects upstream-provided binary payloads from being modified during repackaging
- the spec checks the version, root help, and service help of both public CLI names and the desktop’s bundled CLI
- Renovate follows the stable desktop update API, not the v1 GitHub Releases stream; the matching CLI must fetch and pass the build checks before an update is accepted

Install on Fedora:

```bash
sudo dnf copr enable iolaum/aitoolkit
sudo dnf install open-code
opencode --version
opencode-cli --version  # compatibility name
```

The v2 package upgrades the existing `open-code` package; it is not a side-by-side desktop. Another RPM owning `/usr/bin/opencode` must be resolved explicitly before installation. A user-local `opencode` earlier in `PATH` can shadow this package without an RPM conflict; check `type -a opencode` and choose which installation to use. The package does not remove other installations or edit profiles.

The tested v2 CLI, desktop and local-plugin setup workflow does not require a
separately installed system Bun package. See the
[no-Bun validation report](docs/20261025-retire-bun-llm-wiki-validation.md) for
exact versions, evidence and coverage limits.

Desktop verification after install:

- confirm `OpenCode` appears in the desktop launcher
- launch `OpenCode` once to verify the desktop entry, icons, and bundled runtime work as expected

### [hf-xet](https://github.com/huggingface/xet-core)

- COPR package name: `python-hf-xet`
- installable RPM name: `python3-hf-xet`
- primary architecture: `x86_64`
- package the upstream Linux `cp37-abi3` wheel for the standard Fedora CPython build
- do not switch to the upstream `cp313t` or `cp314t` wheels for normal Fedora builds; those target free-threaded Python variants

This approach keeps the repository aligned with its current binary-repackaging strategy while still selecting a Python-compatible upstream artifact across supported Fedora releases.

Packaging note:

- `hf-xet` is built upstream from Rust sources using maturin/PyO3
- the published `cp37-abi3` wheel works across supported Fedora Python versions with the default interpreter
- rebuilding from source would require a much heavier Rust workspace toolchain and is intentionally avoided here

Install on Fedora:

```bash
sudo dnf copr enable iolaum/aitoolkit
sudo dnf install python3-hf-xet
python3 -c "import hf_xet"
```

### [huggingface_hub](https://github.com/huggingface/huggingface_hub)

- COPR package name: `python-huggingface-hub`
- installable RPM name: `python3-huggingface-hub`
- initial target architecture: `x86_64`
- package the upstream PyPI source release
- preserve the upstream `hf` and `tiny-agents` CLI entry points

This approach keeps the repository aligned with its Python source-packaging workflow while relying on separately packaged Fedora or COPR dependencies for the components that upstream expects at runtime.

Packaging note:

- `huggingface_hub` depends on `hf-xet` on supported Linux architectures, so this package currently follows the repository's active `x86_64` target
- `tiny-agents` is installed upstream unconditionally, so the package adds an explicit runtime dependency on `python3-mcp` to keep that CLI functional
- the PyPI source release currently includes upstream tests, but this repository keeps `%check` to import and CLI smoke checks rather than running the full upstream test suite

Install on Fedora:

```bash
sudo dnf copr enable iolaum/aitoolkit
sudo dnf install python3-huggingface-hub
python3 -c "import huggingface_hub"
hf --help
```

## Retired repository maintenance

`bun` and `llm-wiki` are no longer maintained by this repository. Existing
installed copies and published COPR artifacts are not removed by this change.
Retiring their live COPR rebuild paths is a separate operator task; see the
[maintainer handoff](docs/developer.md#retired-package-copr-handoff).

## Intended repository layout

Each package now lives in its own directory so COPR package subdirectories, build separation, and any future package-specific metadata stay isolated.

The repository is expected to grow into a small packaging repo with files such as:

- `open-code/open-code.spec`
- `python-hf-xet/python-hf-xet.spec`
- `python-huggingface-hub/python-huggingface-hub.spec`
- `docs/developer.md`
- `.github/workflows/check.yml`
- `renovate.json`

## COPR workflow

The intended workflow is:

1. update spec files in this repository
2. let Renovate propose `Version:` bumps for annotated spec files when supported upstream releases change
3. validate changes in CI with `rpmlint`, source fetching, and RPM builds
4. review and merge the resulting pull request
5. configure COPR packages to build from this repository with source type `SCM`, clone URL set to this GitHub repository, and `Committish` set to `main`
6. set each package `subdirectory` to its package folder, such as `open-code/`, `python-hf-xet/`, or `python-huggingface-hub/`, and set the matching spec path inside that folder
7. enable `Webhook rebuild` for each COPR SCM package
8. add the COPR webhook URL to the GitHub repository webhook settings with content type `application/json`
9. let COPR rebuild from new commits on `main`, generate and host repository metadata for Fedora users, and publish the updated package
10. verify the published package in COPR and test installation from a Fedora system

This repository uses the Renovate GitHub App from Mend (`https://github.com/apps/renovate`) to automate supported package version updates.
Maintainer-facing notes for Renovate and related workflow details are documented in `docs/developer.md`.

This replaces the local workflow of downloading release files, renaming them manually, and running `createrepo_c` by hand.

For routine package updates:

1. wait for Renovate to open a pull request for supported upstream releases, or update the spec manually when needed
2. run local validation or open a pull request and let CI validate the change
3. review whether the change is a straightforward `Version:` bump or also needs packaging adjustments
4. merge the change to `main` so GitHub sends the webhook event to COPR
5. confirm that COPR starts a new SCM build from `main` for the updated package
6. confirm the new build appears in the expected Fedora chroot
7. install or upgrade from the COPR repository and verify the packaged application behavior

For automatic COPR rebuilds from GitHub:

1. open the package configuration in the COPR project
2. set `Source Type` to `SCM`
3. set `Clone URL` to the GitHub repository URL
4. set `Committish` to `main`
5. set the package subdirectory to the package folder, such as `open-code/`, `python-hf-xet/`, or `python-huggingface-hub/`, and set the matching spec path inside that folder
6. enable `Webhook rebuild`
7. copy the webhook URL shown by COPR
8. add that URL in GitHub under repository `Settings` -> `Webhooks`
9. set the GitHub webhook content type to `application/json`
10. save the webhook and verify that a new commit to `main` triggers a COPR rebuild

## Local validation

The repository uses GitHub Actions to validate spec changes in a Fedora 44 container on the Ubuntu 24.04 runner. This CI target does not retire any configured COPR chroot.

Prefer running the same checks in a temporary Fedora container with Podman so the host worktree stays clean and the toolchain stays close to CI.

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

For a single package, use the same container setup and replace the loop with the spec path you want to validate.
