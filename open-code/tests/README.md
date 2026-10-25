# OpenCode packaging acceptance fixtures

- `release-feed.test.cjs` tests the actual Renovate JSONata transform and all
  three maintained manager extractions. Run it using the disposable-container
  instructions in [developer notes](../../docs/developer.md#opencode-release-feed-regression-checks).
- `fixtures/v1-session.json` is a synthetic v1.19.4 export: one session and one
  text message, with fixed identifiers and a non-secret marker. Import it with
  the actual published v1 CLI, then export it again to verify the source fixture
  through the application's supported interface. It makes no model request.
- `fixtures/v1-config.json` supplies a synthetic agent prompt/description and
  a legacy `bash: deny` permission. There are no credentials or real sessions.
- `check-v1-migration.py` starts the installed v2 server twice and asserts
  migration completion, the original session/message identity and text,
  configuration conversion, permission preservation, and no message duplication
  through authenticated public API routes. It reads the server's generated
  local password privately and redacts that line from retained logs.

## Isolation requirements

Run only in disposable Fedora 44 Podman containers with an unprivileged
`tester` user and private `/home/tester`, XDG state, networking, and process
namespaces. The checker refuses non-container/root execution and requires the
fixture profile. Do not mount a real home, credentials, desktop sockets, host
package database, user bus, container socket, or use host namespaces/privileged
mode. Bind source read-only and work on a container copy. For concurrent test
containers sharing temporary evidence, use SELinux shared `:z` labels rather
than relabeling a live shared mount with private `:Z` labels.

## Migration sequence inside the container

1. Install the published v1 `open-code` RPM using DNF. The 2026-10-25 test used
   `open-code-1.19.4-1.fc44.x86_64`; pin and verify the baseline artifact rather
   than silently selecting a different release on a rerun.
2. Create `/home/tester/project` and private home/XDG directories. As `tester`,
   copy the config fixture to `$XDG_CONFIG_HOME/opencode/opencode.json` and,
   from the project directory, run:

   `opencode-cli import /path/to/fixtures/v1-session.json`

   `opencode-cli export ses_coprfixture20261025 > /home/tester/v1-export.json`

   Parse that export and assert the session title and text marker match the
   fixture. Do not create a session by submitting a model prompt.
3. With v1 processes stopped, retain a pristine copy of
   `$XDG_CONFIG_HOME/opencode` and `$XDG_DATA_HOME/opencode` outside the
   application user's accessible profile. Record a SHA-256 manifest of every
   source file. Restore a disposable working copy to the tester profile and
   restore its ownership. Never run v2 against the retained source copy.
4. DNF-upgrade to the candidate RPM normally, without force/replace-file flags.
   Check both public commands, the private bundled CLI, and RPM ownership.
5. As `tester`, with no host credentials or service sockets, run:

   `python3 /path/to/tests/check-v1-migration.py`

   It bounds startup/readiness waits and cleans up its server process groups.
   The API response snapshots and sanitized logs remain in the disposable home.
6. Recompute and compare the retained source fixture manifest. It must remain
   unchanged. Remove the container so all remaining private processes/state are
   discarded; retain only sanitized evidence outside tracked source.

For desktop acceptance, launch the installed desktop as the unprivileged user
under private Xvfb and `dbus-run-session` with **normal sandboxing**. Capture a
visible window and inspect the rendered screen; a process or title alone is
not a ready-state pass. No physical GPU or real Wayland acceptance is implied.

The [dated validation report](../../docs/20261025-opencode-v2-fedora44-validation.md)
records the exact tested artifacts, results, and coverage limitations.

## No-system-Bun acceptance

- `fixtures/no-bun-plugin/index.ts` uses the v2 `Plugin.define` setup hook to
  write a fixed marker and the running version. No providers, model calls or
  third-party npm dependencies are needed. The exclusive marker write requires
  a fresh disposable profile for every run.
- `check-no-bun.py` verifies all three installed CLI entry points, ownership and
  compatibility symlink, then starts a bounded server and checks authenticated
  `/api/config` plus the actual plugin setup effect. It checks package/PATH and
  private-profile Bun absence before and after, and redacts the generated local
  server password. Its container/non-root/profile guards must remain enabled.
- `no-bun-runtime.sh` runs only as disposable container root. It installs the
  candidate through ordinary DNF with Bun excluded, checks generated dependencies
  and upstream desktop payload preservation, creates the unprivileged tester,
  and invokes the focused checker and private-display desktop helper.
- `no-bun-desktop.sh` runs only as that tester, under private Xvfb/D-Bus with
  normal sandboxing. A screenshot is captured, not automatically declared ready;
  inspect it for a usable rendered screen. No physical GPU or Wayland proof is
  implied.

Build the candidate in a separate disposable Fedora 44 build container using the
normal packaging gates. Stage only its binary RPM and the matching untouched
upstream desktop RPM in a non-secret temporary input directory. Do not reuse a
build container as the runtime environment. From the repository root:

```bash
# Both paths are temporary directories outside the repository and host home.
inputs=/tmp/copr-no-bun-inputs
outputs=/tmp/copr-no-bun-evidence
mkdir -p "$inputs" "$outputs"
# Copy the built open-code-<version>-<release>.x86_64.rpm into "$inputs".
# Copy its matching upstream desktop RPM as "$inputs/upstream-desktop.rpm".
# There must be exactly one candidate binary RPM in the input directory.
podman run --rm -i --timeout 900 \
  -v "$PWD":/src:ro,z -v "$inputs":/input:ro,z -v "$outputs":/out:z \
  --workdir /root registry.fedoraproject.org/fedora:44 \
  bash < open-code/tests/no-bun-runtime.sh
```

The runner copies source and the desktop helper into container-local `/work`
before dropping privileges. In particular, it does not ask the tester to traverse
a mode-700 host temporary input directory. Keep input mounts read-only; do not
relax host directory permissions or sandboxing to make a test pass.

Record the candidate revision, exact RPM identity/hash and per-gate results.
Inspect `desktop.png`, retain only sanitized evidence, and verify container
cleanup on success and failure. Missing desktop/plugin/runtime coverage is a
blocked gate, not a pass. This tests the local setup fixture and core workflows,
not arbitrary plugins, Bun-dependent projects, inference or real profiles.
