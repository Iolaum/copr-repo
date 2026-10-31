# Plan: OpenCode v2 desktop releases and Fedora 44 CI

> Type: Migration
> Source Type: Mixed
> Source: Nikolaos's 2026-10-25 discussion, supplied upstream release report, packaging investigation, and repository inspection.
> Confidence: High; implementation, isolated acceptance, initial COPR build, and hosted Renovate discovery are evidenced below. Exact COPR source-SHA linkage and published-artifact DNF verification remain unconfirmed.
> Status: Implemented; outcome snapshot updated 2026-10-31. This dated plan is not ongoing execution authority.
> Phase Review: Four-phase structure approved by Nikolaos on 2026-10-25 at 07:52 Europe/Athens.

## Goal

Make subsequent OpenCode releases from this COPR packaging repository stable **v2 desktop** packages, retaining the RPM name **open-code**, exposing the CLI as **opencode** with **opencode-cli** compatibility, and moving repository CI and isolated acceptance testing to **Fedora 44**.

## Context

The existing package republishes an upstream desktop RPM and a matching standalone CLI. Its GitHub Releases datasource still follows upstream v1. Stable v2 desktop and CLI downloads instead use OpenCode's files service and update API. Both desktop generations share application identity; this is an upgrade, not side-by-side v1/v2 packaging.

The approved sequencing was: one v2 candidate, Fedora 44 CI migration, isolated installation/upgrade acceptance, then publication verification. At creation, this plan did not authorize operational actions; the work below was subsequently implemented and separately verified/authorized. Recheck dated facts before any new action.

## Outcome update (2026-10-31)

- Phases 1–3 completed for the initial stable v2.1.4 candidate. The [validation report](../20261025-opencode-v2-fedora44-validation.md) records artifact hashes, Fedora 44 builds (5/5 specs), isolated install/upgrade and migration tests, conflict checks, desktop startup, and coverage limits.
- Implementation PR [#185](https://github.com/Iolaum/copr-repo/pull/185) merged as 0f26cabbc84ccff083cc263679ca9602d7480b42; its hosted CI passed ([run](https://github.com/Iolaum/copr-repo/actions/runs/40172844825)).
- COPR [build 11204521](https://copr.fedorainfracloud.org/coprs/iolaum/aitoolkit/build/11204521/) succeeded for Fedora 43 and 44 x86_64 and produced open-code-2.1.4-1. It was submitted seconds after the merge; the inspected SCM configuration targeted main, but the public build API does not expose a source commit SHA, so exact revision linkage is timing/configuration evidence rather than a reported build field.
- Nikolaos reported on 2026-10-25 that v2 worked well in his test; the tested artifact/source was not recorded. This is useful user feedback, but does not by itself prove the specific published-COPR DNF install/upgrade criterion below.
- Hosted Renovate discovery is now proven: Renovate PR [#192](https://github.com/Iolaum/copr-repo/pull/192) proposed opencode-desktop 2.2.4 → 2.2.5 from the stable-v2 feed, merged 2026-10-31 as 6d16dcb7776418b16087279a53d5fd59ff66d67d, and its GitHub Actions check passed ([run](https://github.com/Iolaum/copr-repo/actions/runs/41169182963)). The current repository spec is 2.2.5.
- **Remaining unverified:** Exact COPR source-SHA linkage, and DNF install/upgrade plus desktop/CLI checks specifically against the published COPR artifact, are not documented. The isolated candidate acceptance in Phase 3 is not a substitute for this Phase 4 gate.

## Semantic Core

- **Claim:** The selected stable v2 desktop payload can be repackaged without mutation, installed or upgraded using Fedora 44 DNF, and maintained through the existing repository-to-COPR release flow.
- **Evidence:** Source metadata and hashes; spec lint and RPM build logs; extracted-payload comparisons; final RPM CLI checks; DNF transaction and ownership evidence; fixture migration assertions; bounded virtual-display desktop startup; CI and COPR records tied to the same reviewed revision.
- **Population:** One selected stable v2 x86_64 release for targeted acceptance; every spec discovered by CI for the Fedora 44 regression gate (five at planning time).
- **Interpretation:** A successful build is not installation or desktop acceptance. A virtual-display startup is not proof of physical GPU, Wayland, GNOME/KDE launcher, or unrestricted real-profile compatibility. A version string alone is not a meaningful CLI or migration test.

## Planning Brief

- **Outcomes:** Stable v2 release discovery; correct desktop payload packaging; canonical and compatibility CLI commands; Fedora 44 CI; container-only acceptance; verified publication after authorization.
- **Scope:** open-code/open-code.spec, renovate.json, .github/workflows/check.yml, README.md, docs/developer.md, and Fedora-version guidance in repository AGENTS.md. Add only focused test fixtures or helpers if existing tooling cannot adequately express acceptance; do not introduce a generic packaging framework.
- **Non-goals:** Source-building OpenCode; aarch64 enablement; package renaming; side-by-side v1/v2 packages; custom repository hosting; live workstation installation, profile migration, or desktop-session access; live COPR/GitHub settings changes; unrelated package modernization.
- **Constraints:** Preserve the upstream /opt/OpenCode payload, bundled CLI, strip protections, package-local conventions, changelog style, and other packages' behavior. Never commit downloaded RPMs, archives, binaries, generated metadata, or upstream trees.
- **Isolation:** Use disposable Fedora 44 containers with private home/XDG state, test users, displays, and session buses. Mount source read-only and work on a container copy. Do not mount the real home, credentials, host desktop sockets, user service bus, or system package database. Do not silently introduce privileged containers, host namespace access, or sandbox disabling.
- **Assumptions and validation conditions:** Existing COPR SCM/webhook configuration and Fedora 44 dependency availability must be checked, not inferred. A newer stable v2 may replace the initially observed 2.1.4 after repeating artifact/layout checks.
- **Acceptance signals:** All required gates below pass or are explicitly blocked; no host packages or live profiles changed; published Fedora 44 packages match the reviewed implementation.

## Grounding

### Verified system facts

Inspection baseline: repository revision **13e136ea43514e9124e03d826b5d31e00f091003**, on the existing **feat/opencode_v2** branch with a clean worktree before this plan. Do not switch or reset user branches merely because this snapshot names one.

- [Current spec](../../open-code/open-code.spec) declares 1.18.33, GitHub Releases discovery, separate desktop and CLI sources, x86_64, strip exclusions, and the public opencode-cli command.
- [CI](../../.github/workflows/check.yml) uses ubuntu-24.04 as runner and fedora:43 as job container; it discovers */*.spec and runs build-dependency resolution, strict spec lint, source fetching, and RPM builds.
- [Renovate configuration](../../renovate.json) has package-specific regex managers and automerges minor/patch/pin/digest updates. Avoid changing unrelated managers or global merge behavior.
- [Repository instructions](../../AGENTS.md), [README](../../README.md), and [developer notes](../developer.md) establish packaging invariants, container validation, and the documented SCM-to-COPR workflow. Live settings are not established by these documents.
- The desktop and CLI stable APIs both advertised 2.1.4 during planning, with the expected x86_64 RPM and Linux x64 CLI archive.
- The preceding disposable Fedora 43 investigation built a 2.1.4 RPM and verified CLI behavior and unmodified desktop payload. This is feasibility evidence only, not Fedora 44 or installation/upgrade acceptance.

### Durable upstream references

- [Stable desktop metadata](https://opencode.ai/update/api/latest/desktop/opencode)
- [Stable CLI metadata](https://opencode.ai/update/api/latest/cli/opencode)
- [v2 desktop packaging configuration](https://github.com/anomalyco/opencode/blob/0b7f4c416104387deaa6c1184718d9eb7da35d93/packages/desktop/electron-builder.config.ts)
- [v2 artifact upload contract](https://github.com/anomalyco/opencode/blob/0b7f4c416104387deaa6c1184718d9eb7da35d93/script/update-artifact.ts)
- [Update service contract and rollout semantics](https://github.com/anomalyco/opencode/blob/0b7f4c416104387deaa6c1184718d9eb7da35d93/services/update/README.md)
- [Renovate custom datasources](https://docs.renovatebot.com/modules/datasource/custom/)

The v2 source pattern is `https://opencode.ai/files/bin/<version>/<filename>`, without a v prefix in the path. The LICENSE remains obtainable from the corresponding v-prefixed Git tag. GitHub tags alone are not desktop publication readiness evidence.

## Decisions

1. **Stable v2 desktop, existing RPM identity and architecture**
   - Status: Confirmed baseline.
   - Authority: User-approved goal and repository constraints.
   - Why: Upgrade existing open-code users without expanding architecture or packaging strategy.

2. **Fedora 44 container acceptance and a dedicated CI migration phase**
   - Status: Confirmed baseline.
   - Authority: Nikolaos's explicit container-only and CI requirements; approved four-phase structure.
   - Why: Avoid installing or migrating the live workstation, and align automated validation with the desired Fedora release.
   - Boundary: Changing CI does not authorize modifying COPR chroots or retiring any existing published target.

3. **Provide opencode while retaining opencode-cli compatibility**
   - Status: Confirmed baseline for both command names; proposed exact file layout.
   - Authority: Approved CLI-naming direction; planner-proposed implementation detail.
   - Proposed layout: /usr/bin/opencode is the existing standalone CLI payload; /usr/bin/opencode-cli is an RPM-owned relative symlink to opencode. The desktop continues using /opt/OpenCode/ai.opencode and its private bundled opencode-cli.
   - Why: Match upstream CLI naming without breaking existing scripts or changing the desktop's internal paths. Do not add Provides: opencode or package-wide Conflicts/Obsoletes merely because a command is named opencode.

4. **Keep the separate CLI source for the initial migration**
   - Status: Proposed; preserves the existing packaging strategy.
   - Authority: Planner-proposed reversible detail.
   - Why: Minimize the initial migration. Reusing the bundled CLI may remove duplication, but is deferred rather than silently added to this plan.

5. **Discover stable desktop releases through Renovate's existing custom-datasource capability**
   - Status: Proposed.
   - Authority: Planner-proposed use of a maintained existing mechanism.
   - Contract: Read the stable desktop API's version with explicit semver versioning and a >=2.0.0 <3.0.0 range. Require the expected x86_64 RPM entry. Validate the matching CLI artifact before accepting an update. Keep versioned source URLs in the spec, not mutable latest redirects.
   - Why: Follow published desktop v2 artifacts rather than the v1 GitHub Releases stream or ordinary dev/beta builds. No custom updater service is needed.
   - Failure behavior: Missing files, invalid responses, unavailable matching CLI, or mismatched metadata must not silently select v1, prereleases, or another artifact type. Prevent downgrades. Preserve unrelated Renovate behavior.

## Plan

Phases are sequencing and verification units, not automatic tickets, commits, or pull-request boundaries. All future implementation is subject to applicable authorization; phase-structure approval is not permission to merge or publish.

### Phase 1: Build the OpenCode v2 candidate

**Outcomes covered:** One narrow end-to-end stable-release path: discovery, pinned sources, packaging, both CLI names, documentation, and a Fedora 44 candidate artifact.

**Entry dependencies / preconditions:** Implementation authorization; fresh worktree/instruction review; stable v2 metadata and matching artifacts available. No host software installation is required.

#### What to build or change

Update the spec's version, versioned desktop/CLI sources, canonical command and compatibility symlink, payload expectations, checks, and changelog. Adapt the existing OpenCode Renovate manager to the proposed stable-desktop contract and align package documentation. Build on Fedora 44 locally while leaving the repository-wide CI switch for Phase 2.

For the observed 2.1.4 layout, the executable is /opt/OpenCode/ai.opencode, icons are ai.opencode.png, and the CLI reports opencode v2.1.4. Desktop entries remain ai.opencode.desktop.desktop and opencode-desktop.desktop. Revalidate these against the actual selected version instead of assuming permanence. Retain the app's private bundled CLI and meaningful version/help checks for it as well as the public commands.

#### Acceptance criteria

- [x] Selected release is stable v2; desktop and CLI versions agree; downloaded artifacts match the upstream metadata hashes.
- [x] Renovate config validation and a non-writing extraction/lookup dry-run select the intended OpenCode dependency/version; exercise wrong channel/major, missing RPM, and invalid metadata cases. Confirm unrelated dependencies remain discoverable.
- [x] Fedora 44 build-dependency resolution, strict spec lint, source fetching, and complete RPM build succeed.
- [x] The final RPM retains name open-code and architecture x86_64. Its CLI executable and compatibility symlink are both correctly owned and resolve inside the installed container.
- [x] Final-package version, root help, and service help assertions exercise v2 CLI behavior; do not just replace the old attach-help assertion with an unchecked invocation.
- [x] Extracted /opt/OpenCode contents and symlink targets match upstream; no strip mutation or unwanted build-ID links are introduced.
- [x] LICENSE, icons, desktop entries, metainfo, and expected paths are packaged correctly. Documents distinguish CLI commands from the desktop executable.

#### Completion evidence

- Selected version/source URLs/hashes, reviewed diff, Renovate validation/dry-run results, Fedora 44 build logs and RPM identity, ownership/symlink checks, smoke results, and payload comparison.

#### Stop or escalation conditions

- Artifact type/architecture or strip strategy must change; sources disagree; payload behavior differs materially; required tools would need host installation or access. Report evidence and ask Nikolaos before expanding scope.
- An API/datasource limitation requires a materially different automation architecture. Do not substitute a custom hosted updater or a different release channel without approval.

### Phase 2: Migrate CI to Fedora 44

**Outcomes covered:** Repository-wide validation uses Fedora 44 without weakening existing checks or breaking unrelated packages.

**Entry dependencies / preconditions:** Phase 1 candidate passes targeted Fedora 44 validation. Review the actual spec inventory and available published dependencies.

#### What to build or change

Change the GitHub Actions job container from fedora:43 to fedora:44 while retaining ubuntu-24.04 as runner. Preserve workflow triggers, locale settings, package discovery, COPR dependency setup, and validation gates. Align Fedora-version instructions in README.md, docs/developer.md where applicable, and repository AGENTS.md. Do not add an unrequested Fedora matrix or silently change action versions.

#### Acceptance criteria

- [x] Workflow configuration is valid and the existing checks execute inside Fedora 44.
- [x] Every discovered spec passes dependency resolution, strict spec lint, source fetching, and full RPM build: bun, llm-wiki, open-code, python-hf-xet, and python-huggingface-hub at the planning baseline.
- [x] Results record completed/total specs and per-spec outcomes; one passing OpenCode build cannot stand in for a green repository.
- [x] Published COPR dependencies required by the Python packages resolve on Fedora 44. Do not infer same-change dependency support from the existing published-dependency setup.
- [x] Local validation instructions and CI agree on Fedora 44; no changes weaken tests or alter unrelated package strategy.

#### Completion evidence

- Workflow/docs diff; discovered-spec inventory; Fedora 44 per-spec validation results and dependency blockers, if any. Actual hosted CI success must be verified in Phase 4 rather than inferred from local reproduction.

#### Stop or escalation conditions

- Any unrelated package or dependency fails on Fedora 44: isolate and report the failure. Do not broadly upgrade packages, disable gates, or edit COPR settings to manufacture a green run. Ask Nikolaos if the fix materially expands this migration.

### Phase 3: Validate installation and upgrades in isolated Fedora 44 containers

**Outcomes covered:** Fresh installation, v1-to-v2 upgrade, command compatibility/conflicts, fixture migration, and bounded desktop startup without live-system changes.

**Entry dependencies / preconditions:** Phases 1 and 2 gates pass; obtain the existing published Fedora 44 v1 RPM through the repository/artifact service, not the host installation. Use retained candidate artifacts and clean container instances.

#### What to build or change

Exercise DNF installation and upgrade transactions in disposable containers. Use synthetic v1 fixtures created by the v1 application or a representative non-secret test fixture; run v2 against a disposable copy. Use a private virtual display and session bus for desktop startup under an unprivileged test user. Keep any spawned service processes and data within the container and terminate them after tests.

#### Acceptance criteria

- [x] Fresh DNF installation resolves declared dependencies and installs the expected candidate. Run the public and bundled CLI checks from the installed package, not only a buildroot.
- [x] DNF upgrades the published open-code v1 package to the candidate v2 under the same package identity without force/replace-file flags, unexpected package removal, or obsolete unowned files. Record old/new NEVRA and transaction outcome.
- [x] Both public command names work after upgrade; their ownership and compatibility symlink are correct. Desktop entries reference the new executable and icon paths; removed v1 paths do not remain stale.
- [x] A deliberate competing RPM owning /usr/bin/opencode is rejected normally without overwriting it. A user-local command earlier in PATH is demonstrated and documented as shadowing, not an RPM dependency/file conflict. Do not modify user profiles or auto-remove another installation.
- [x] Known non-secret v1 sessions/configuration fixture data is available through v2's supported interfaces after migration, not merely present on disk; record stable fixture identifiers/content and relevant logs. Source fixtures remain unchanged, and repeated startup does not corrupt or duplicate the fixture's data.
- [x] Desktop startup reaches a usable window/ready state under the isolated virtual display, with no missing-library or launcher failures. Capture bounded logs/window evidence; a live process alone is not a pass.
- [x] No real home, credentials, display/service sockets, or host package database were exposed, and no host packages or live profiles changed.

#### Completion evidence

- Fresh-install and upgrade logs; package identities/ownership; both-command and conflict-test results; fixture assertions and source-integrity checks; desktop-ready screenshot or equivalent observable evidence; isolation settings and process cleanup results.
- Explicit coverage limitation: this is not physical GPU, real Wayland, GNOME/KDE launcher integration, exhaustive session-format compatibility, or real-profile acceptance. Live-system testing is not required by this plan.

#### Stop or escalation conditions

- Required v1 artifacts/representative fixtures cannot be obtained, or migration/desktop behavior fails: report the concrete gap and keep the affected gate open.
- Tests require privileged/host-connected containers, disabling the Electron sandbox, real credentials, live data access, or host installation: do not proceed silently. Propose an isolated alternative and ask Nikolaos if the safety boundary must change.

### Phase 4: Publish and verify

**Outcomes covered:** Reviewed changes pass hosted Fedora 44 CI, produce the intended COPR package, and can be installed/upgraded from the published repository in Fedora 44 containers.

**Entry dependencies / preconditions:** Phases 1-3 pass; applicable authorization for repository publication/merge and package release; reviewed current revision; read-only verification of actual SCM branch/subdirectory/webhook and supported chroots. If Fedora 44 is not an available target, request operator action rather than changing live settings.

#### What to build or change

Use the repository's approved review/merge process, verify hosted CI on the exact implementation revision, and observe the existing main-branch SCM/webhook-to-COPR build path. Inspect Renovate's real hosted lookup behavior when available. Verify both installation and upgrade from the resulting COPR repository using clean Fedora 44 containers.

#### Acceptance criteria

- [x] Hosted CI is green on the reviewed revision and runs in Fedora 44; required review gates are preserved.
- [x] Authorized merge is verified; COPR build 11204521 succeeded for Fedora 44 x86_64 (and Fedora 43).
- [ ] Exact COPR source-commit linkage is not directly evidenced: build 11204521 was submitted two seconds after the merge and the inspected SCM target was main, but the public build API does not return a source SHA.
- [ ] Published-artifact DNF installation and upgrade, both public CLI names, and desktop startup from the expected COPR repository remain undocumented. Nikolaos reported a successful v2 test, but did not identify the artifact source.
- [x] Hosted Renovate discovered stable v2 through the new datasource: PR #192 proposed 2.2.4 → 2.2.5 and merged; its check passed.
- [x] Implementation revision, hosted CI run, COPR build/package, selected version, validation report, and remaining limitation are linked or identified above. The user separately tested v2; no claim is made here that this plan authorized live-system changes.

#### Completion evidence

- Review/merge reference and revision, hosted CI run, COPR build and repository package identity, published-artifact container test results, and hosted Renovate observation or a named external blocker.

#### Stop or escalation conditions

- CI/COPR fails, webhook does not run, published revision/artifact differs, dependencies fail, or live settings need changes: preserve evidence, report the blocker and operator action, and do not bypass gates or claim completion.
- User-data migration failure or a security-relevant regression must stop rollout. A package downgrade is not proof that migrated user data can be rolled back; use untouched test fixtures/snapshots for recovery tests and seek explicit release-recovery authority if publication already occurred.

## Delivery

- **Required delivery split:** None. Phases are not mandatory PR or commit boundaries. One coherent change or reviewed chained changes is acceptable provided publication does not bypass acceptance gates.
- **Authority at plan creation (2026-10-25):** Plan creation only; the saved draft did not itself authorize implementation, builds, commits/pushes, merges, settings changes, or publication. Subsequent work was separately authorized and is evidenced in the outcome update above.
- **Evidence placement:** Keep downloaded sources, built RPMs, displays, and temporary state outside tracked source. Retain concise sanitized validation reports in docs when implementing; link external CI/COPR evidence. Preserve unrelated user changes.
- **Recovery:** Before publication, retain the original repository revision and reproducible previous v1 artifact reference. Discard failed test containers and restart from pristine fixtures. Do not apply an unapproved public revert, version downgrade, or data migration to a live system.

## Testing and Validation

- [x] Phase 1 proves one complete release-discovery-to-candidate path, including meaningful final-package behavior.
- [x] Phase 2 covers every spec in the planning baseline without weakening existing gates.
- [x] Phase 3 covers normal and conflict/upgrade cases with isolated data, plus observable virtual-display desktop readiness.
- [x] Phase 4 distinguishes local validation from hosted CI, COPR build evidence, and hosted updater verification; published-artifact installation/upgrade remains explicitly open.
- [x] Completion evidence identifies versions/revisions, target Fedora release/architecture, test inputs, observed results, and limitations; the missing published-artifact test is named.
- [x] Scope, authority, stop/escalation boundaries, and approved phase structure remain intact.

## Risks and Open Questions

- **Fedora 44 dependencies and all-spec compatibility:** Resolved for the planning baseline by 5/5 Fedora 44 builds; see the validation report. Later package versions are outside that all-spec result.
- **Fedora 44 desktop harness and fixture fidelity:** The bounded virtual-display and representative fixture gates passed. Physical GPU, native Wayland, desktop-environment integration, and exhaustive real-profile compatibility remain outside tested coverage.
- **Command collisions/shadowing:** Synthetic RPM-conflict rejection and PATH shadowing tests passed; no broad package Conflicts/Obsoletes was introduced.
- **Release-feed evolution and partial publication:** Recheck actual metadata/layout at execution and enforce version/artifact consistency. Explicit semver/range, file-availability checks, and no-fallback tests must prevent wrong-channel updates.
- **Hosted Renovate/COPR behavior:** Hosted Renovate discovery is proven by merged PR #192. Build 11204521 succeeded in Fedora 44; exact source SHA and DNF install/upgrade from the published artifact remain unverified in retained evidence.
- **Planner-proposed implementation details:** The exact command symlink layout, initial separate CLI retention, and custom datasource design are visible proposals within the approved outcomes. They are not additional safety blockers for writing this plan; any material departure during execution requires Nikolaos's approval.
