# Plan: Retire Bun and LLM Wiki repository maintenance

> Type: Migration
> Source Type: Grill-me
> Source: Nikolaos’s confirmed 2026-10-25 decision handoff and subsequent sequencing correction: retire both, prove OpenCode independence, then validate the repository.
> Confidence: High for scope and acceptance contract; OpenCode independence requires fresh execution evidence.
> Status: Implementation plan for review; this document does not authorize implementation, merge, or operational retirement.
> Phase Review: Nikolaos approved the execution order on 2026-10-25; the phases below group that order into focused acceptance followed by repository-wide acceptance.

## Goal

Stop maintaining `bun` and `llm-wiki` in this repository while preserving users’ ability to install and use the packaged OpenCode desktop and CLI without a separately installed system Bun. Document COPR retirement as a separate follow-up rather than changing live infrastructure here.

## Context

Both retiring packages have dedicated specs and Renovate managers. Current documentation advertises their installation, and the OpenCode release-feed regression suite explicitly expects all five package dependencies. Deleting specs alone would leave stale maintenance instructions and failing regression expectations.

The current OpenCode package installs the matching upstream native CLI as `/usr/bin/opencode`, provides the relative `opencode-cli -> opencode` compatibility symlink, and preserves the desktop’s private bundled CLI. Its spec has no explicit Bun dependency. This supports investigating independence; it does not prove generated RPM dependencies or runtime/plugin behavior without system Bun.

## Semantic Core

- **Claim:** The repository can cease packaging both retired applications while the selected packaged OpenCode release remains installable and usable for the tested core and plugin workflows without system Bun.
- **Population:** The selected stable OpenCode v2 x86_64 candidate on Fedora 44; all three remaining specs for repository regression. Record exact versions and revisions at execution time.
- **Evidence:** Generated RPM dependency inspection, ordinary DNF installation, package/PATH absence checks for Bun before and after runtime tests, installed CLI/service checks, a visibly rendered desktop under a private virtual display, and an observable deterministic plugin result.
- **Success:** Every required gate passes against the reviewed removal revision, with no host application/profile/package changes. Missing or skipped coverage is not a pass.
- **Failure:** Installation requires external Bun, runtime/plugin behavior invokes or installs system Bun, required behavior fails, or isolation cannot be preserved. Stop and return the finding to Nikolaos; do not silently add a replacement runtime.
- **Interpretation limits:** Embedded upstream runtime components are not the separately maintained Bun package and must remain intact. Version/help output alone is not runtime acceptance. No claim is made about arbitrary Bun-dependent projects, all third-party plugins, model inference, physical GPUs, native Wayland, or real user profiles.

## Planning Brief

- **Outcomes:** Both packages disappear from active packaging and update discovery; current guidance describes only maintained packages; OpenCode independence is demonstrated; remaining packaging passes regression; COPR follow-up is explicit.
- **Scope:** `bun/`, `llm-wiki/`, `renovate.json`, `README.md`, `docs/developer.md`, repository `AGENTS.md`, `open-code/tests/release-feed.test.cjs`, and `open-code/tests/README.md`. Add only focused no-Bun acceptance fixtures/checks and sanitized evidence documentation if needed.
- **Conditional scope:** `.github/workflows/check.yml` only if evidence shows a necessary integration change. Its existing `*/*.spec` discovery should already handle the reduced set; preserve its gates, Fedora 44 target, and triggers.
- **Non-goals:** Live COPR or GitHub settings changes; deleting published RPMs; host installation/uninstallation or profile migration; replacement Bun packaging or a custom updater; unrelated package/version/architecture changes; rewriting historical reports and changelogs.
- **Constraints:** Preserve remaining specs and OpenCode payload, command ownership, CLI compatibility, desktop launchers, and strip protections. Do not commit downloaded artifacts, binaries, generated repository metadata, credentials, or upstream source trees.
- **Isolation:** All test tooling, builds, and application execution use disposable Podman containers. Bind source read-only and work on a container copy. Use private test home/XDG state, unprivileged application users, and private display/D-Bus sessions. Never mount host home, credentials, desktop sockets, user bus, package database, or container socket; never use privileged mode, host namespaces, or sandbox-disabling flags. Repository editing and Git publication remain authorized host-side work.
- **Acceptance signals:** Focused no-Bun acceptance passes, the remaining three packages pass their normal packaging checks, Renovate extracts exactly their expected dependencies, and the implementation diff contains no unrelated changes.

## Grounding

Inspection baseline: **0f26cabbc84ccff083cc263679ca9602d7480b42**, on `plan/retire-bun-llm-wiki`. Five specs exist at this baseline. An unrelated untracked OpenCode plan already exists under `docs/plans/`; preserve it and exclude it from this delivery.

### Verified repository facts

- [OpenCode baseline spec](https://github.com/Iolaum/copr-repo/blob/0f26cabbc84ccff083cc263679ca9602d7480b42/open-code/open-code.spec) selects 2.1.4 and matching desktop/standalone CLI artifacts, with version/root-help/service-help checks for both public names and the private CLI.
- [Renovate baseline](https://github.com/Iolaum/copr-repo/blob/0f26cabbc84ccff083cc263679ca9602d7480b42/renovate.json) has separate managers for the two retiring packages and the three remaining ones. Preserve the remaining managers, OpenCode datasource, and unrelated merge policy.
- [Release-feed tests](../../open-code/tests/release-feed.test.cjs) explicitly assert five dependencies; [test instructions](../../open-code/tests/README.md) also describe five-manager extraction and define existing isolation safeguards.
- [CI](../../.github/workflows/check.yml) discovers `*/*.spec`, enables published COPR dependencies, and runs build-dependency resolution, strict spec lint, source fetching, and full RPM builds on Fedora 44.
- [Repository instructions](../../AGENTS.md), [README](../../README.md), and [developer notes](../developer.md) contain active Bun/LLM Wiki maintenance references requiring cleanup. The remaining specs declare no direct dependency on either retiring package.

### Documented evidence and assumptions

- The [dated OpenCode validation report](../20261025-opencode-v2-fedora44-validation.md) records earlier builds, installation, migration, and virtual-display checks. Preserve it as historical evidence; it does not establish the new no-system-Bun acceptance contract.
- [Upstream v2 installation documentation](https://opencode.ai/v2/docs/) describes native CLI binaries; [v2 plugin documentation](https://opencode.ai/v2/docs/plugins/) describes plugin loading. Do not apply the different v1 plugin/runtime documentation to v2.
- Generated dependencies, a deterministic version-compatible plugin fixture, and fresh no-Bun runtime behavior remain execution-time validation obligations. No live COPR configuration or retirement state is established by this plan.

## Decisions

All six decisions below are the user-confirmed Grill Me baseline (2026-10-25).

1. **Repository-only retirement.** Remove both specs and active maintenance references, including Renovate configuration and test expectations. COPR retirement remains a documented follow-up.
   - Status: Confirmed baseline. Authority: User-approved.
   - Why: Stop repository maintenance without expanding this work into operational retirement.
   - Rejected: Changing live COPR settings in this work.
2. **Preserve historical evidence.** Keep dated reports and changelogs; Git history retains the removed specs. No separate packaging archive to maintain.
   - Status: Confirmed baseline. Authority: User-approved.
   - Why: Preserve useful evidence without creating another maintenance surface.
   - Rejected: Rewriting history or maintaining archived spec copies.
3. **Preserve OpenCode’s packaging.** Keep its public commands and bundled desktop runtime unchanged unless testing exposes a blocker.
   - Status: Confirmed baseline. Authority: User-approved.
   - Why: Protect existing installation and usability while removing standalone Bun maintenance.
   - Rejected: Preemptively changing OpenCode’s runtime architecture.
4. **Require no-system-Bun acceptance.** In clean Fedora 44 containers, verify installation, CLI/service operation, desktop startup, and representative plugin loading; validate the remaining packages too.
   - Status: Confirmed baseline. Authority: User-approved.
   - Why: Test the user-visible concern rather than infer independence from metadata.
   - Rejected: Treating dependency declarations or help output alone as sufficient proof.
5. **Keep isolation strict.** Read-only repository input, disposable working copies and profiles, private display/session bus—no host credentials, desktop sockets, package database, or privileged containers.
   - Status: Confirmed baseline. Authority: User-approved.
   - Why: Keep test effects away from the host environment.
   - Rejected: Testing against the host installation or live profiles.
6. **Stop on a real dependency.** If OpenCode needs external Bun, bring that finding back rather than silently introducing replacement maintenance.
   - Status: Confirmed baseline. Authority: User-approved.
   - Why: A newly discovered runtime dependency changes the approved design and requires a user decision.
   - Rejected: Silently packaging or installing another system Bun provider to make acceptance pass.

## Plan

The execution order is **retire both → prove OpenCode independence → validate the repository**. Phase 1 includes the first two steps as one focused end-to-end slice; Phase 2 widens acceptance. These are sequencing and verification units, not separate commits or PRs.

### Phase 1: Retire both packages and prove OpenCode independence

**Outcomes covered:** Remove both maintenance surfaces together and demonstrate the primary protected user workflow on the resulting candidate.

**Entry dependencies / preconditions:** Obtain implementation authorization; recheck repository state and preserve unrelated work. Confirm disposable Fedora 44 Podman isolation is available without relaxing safeguards.

#### What to build or change

Remove both package directories and their dedicated Renovate managers. Clean their current package listings, install instructions, SCM examples, and package-specific maintenance instructions from the scoped documentation and AGENTS file. Update dependency-extraction expectations to the three remaining packages without weakening OpenCode’s release-feed safeguards. Keep historical reports, historical changelog entries, and legitimate references explaining Bun independence.

From this candidate, build the selected OpenCode RPM in a disposable build container. Test that RPM using a separate clean Fedora 44 runtime container that does not inherit the build environment. Ensure ordinary DNF cannot silently satisfy a dependency with the still-published Bun package. Inspect generated RPM dependencies and installed packages, and verify that no external Bun executable is available before and after runtime acceptance.

Exercise both public CLI names and the private desktop CLI; verify version/root/service help, ownership, and compatibility symlink. Demonstrate actual service readiness and a supported non-model API response, followed by bounded shutdown. Launch the desktop under private Xvfb/D-Bus with normal sandboxing and inspect a screenshot for a usable rendered screen. Load a minimal deterministic v2-compatible plugin and assert its observable effect rather than merely checking that the process starts. Use synthetic state and no provider credentials or model requests.

#### Acceptance criteria

- [ ] Both specs and their dedicated update managers are absent; no active installation/maintenance instructions still advertise them as maintained.
- [ ] The modified extraction test passes and finds exactly `open-code`, `python-hf-xet`, and `python-huggingface-hub` with their intended datasources/dependency names.
- [ ] The candidate installs through normal DNF dependency resolution with system Bun absent; no force flags, hidden external runtime, or host state is used.
- [ ] Installed CLI names, private CLI, service operation, rendered desktop, and deterministic plugin effect pass against the same candidate.
- [ ] Bun absence is rechecked after plugin/runtime execution; desktop payload and strip protections remain unchanged.
- [ ] All disposable processes and containers are cleaned up, including on failure.

#### Completion evidence

- Candidate revision, selected version, RPM identity/hash, generated dependencies, DNF transaction result, and before/after Bun absence checks.
- Focused extraction/CLI/service/plugin assertions, sanitized logs, inspected desktop screenshot, and confirmation of container-only execution and cleanup.

#### Stop or escalation conditions

- External Bun is required, fetched, or invoked; a protected OpenCode entry point fails; or packaging changes would exceed the approved removal scope. Return evidence and alternatives to Nikolaos.
- Isolation, ordinary sandboxing, or required runtime/plugin evidence cannot be achieved. Record the exact blocked gate; never substitute host execution or a help-only pass.

### Phase 2: Validate the remaining repository and document the COPR handoff

**Outcomes covered:** Full regression of maintained packages, coherent current documentation, and a bounded operational follow-up.

**Entry dependencies / preconditions:** Phase 1 passes on the candidate. Use the same reviewed revision or repeat affected gates after changes.

#### What to build or change

Run the normal repository packaging checks for all three remaining specs in disposable Fedora 44 containers. Validate Renovate configuration using the documented pinned toolchain, run the complete release-feed fixture suite, and inspect actual extraction rather than relying only on a hard-coded test list. Preserve OpenCode’s stable-v2 selection, fail-closed behavior, rollback protection, and unrelated package policies.

Review all active references and count-based documentation, including test instructions. Leave generic CI discovery unchanged unless a demonstrated integration issue requires a scoped fix. Document the separate manual COPR follow-up and review the implementation diff for unrelated changes.

#### Acceptance criteria

- [ ] All **3/3** remaining specs pass `dnf builddep`, strict `rpmlint`, `spectool -Rg`, and `rpmbuild -ba`.
- [ ] Strict Renovate configuration validation and the complete release-feed fixture suite pass; actual extraction finds exactly three intended dependencies and none for the retired packages.
- [ ] Current README, developer notes, AGENTS instructions, and test documentation agree on the maintained package set. Historical evidence remains unchanged.
- [ ] CI retains its normal build gates and supported target; any necessary workflow change is justified and verified. Hosted implementation CI is green before merge is proposed.
- [ ] Review confirms no remaining spec/runtime/architecture changes beyond approved scope, no committed artifacts or secrets, and no live COPR/GitHub settings changes.
- [ ] The COPR follow-up below is explicitly handed off; repository removal is not reported as completed infrastructure retirement.

#### Completion evidence

- Per-spec results tied to the candidate revision, Renovate validation/extraction and fixture results, hosted implementation CI link, reviewed diff, and follow-up checklist.
- Report every skipped/blocked gate with its exact command or check and reason; never convert unavailable evidence into success.

#### Stop or escalation conditions

- Any remaining package or release-discovery regression blocks acceptance. Distinguish infrastructure/upstream unavailability from an actual candidate regression, but do not waive the gate silently.
- A proposed fix changes scope, runtime architecture, risk, or host-isolation requirements: pause for Nikolaos’s decision.

## Separate COPR Follow-up

Owner: Nikolaos or a separately authorized operator. Execution is outside this repository change.

- Inspect current package SCM/webhook/rebuild configuration for `bun` and `llm-wiki`, plus outstanding updates/builds. Disable or retire their rebuild paths without disturbing the remaining packages or shared automation. Do not blindly delete a project-wide GitHub webhook.
- Decide separately whether published RPMs/build history remain available or are removed, whether a retirement notice or migration guidance is needed, and how outstanding package-update PRs are handled. No deletion or uninstall policy is implied here.
- Verify the resulting automation state and continued publication of maintained packages; retain a separate operational report.
- **Known sequencing risk:** Until that follow-up occurs, live SCM/webhook jobs may still target the removed directories and fail after merge. Repository cleanup does not disable those jobs or remove existing user installations. Call out this risk in implementation review and coordinate follow-up timing separately; do not conceal it or silently change live settings.

## Delivery

- **Immediate delivery:** This plan only, committed on `plan/retire-bun-llm-wiki` and submitted as a plan-only PR. Preserve the unrelated untracked OpenCode plan.
- **Implementation delivery:** After separate authorization, one coherent removal change can contain both phases. Phase boundaries do not require separate PRs. Implementation, merge, publication, and COPR retirement are not authorized by accepting or merging this plan alone.
- **Recovery:** Git history retains the removed packaging. Any restoration or runtime redesign after a failed gate is a reviewed follow-up, not an automatic operational rollback.

## Testing and Validation

- [ ] Phase 1 spans removal, update discovery, artifact build/install, protected runtime behavior, and observable acceptance on one OpenCode candidate.
- [ ] Phase 2 covers all three maintained packages and all touched maintenance integrations.
- [ ] Test environments demonstrably lack external/system Bun, including after plugin execution; original upstream embedded components remain intact.
- [ ] All application/test-tool execution remains disposable-container-only; no real profiles, secrets, model requests, host package changes, or unsafe sandbox workarounds.
- [ ] Evidence distinguishes fresh runtime proof, metadata checks, historical reports, and untested functionality.

## Risks and Open Questions

- **External-runtime risk:** Plugin or service paths may reveal a dependency not represented in the spec. Resolve through Phase 1 execution; an external Bun requirement blocks acceptance and goes to Nikolaos.
- **Fixture mechanics:** Choose the smallest deterministic plugin supported by the selected v2 release, preferably a local synthetic fixture. Define its observable effect before execution. This is an executor-owned reversible detail, not an unresolved scope decision; inability to demonstrate actual plugin loading blocks that gate.
- **Published dependency availability:** CI uses existing COPR packages for build dependencies, not same-change repo-local outputs. Preserve remaining packaging and report unavailable upstream/dependency infrastructure rather than changing strategy.
- **Deferred operational retirement:** Live rebuild failures can continue until the separately authorized COPR follow-up is completed. Existing published packages and installed copies are not removed by Git changes.
- **Current planning blockers:** None. Runtime success is deliberately unproven until implementation acceptance; the plan-only PR must not claim those tests have run.
