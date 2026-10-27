%global debug_package %{nil}
%global __brp_strip %{nil}
%global __brp_strip_lto %{nil}
%global __brp_strip_comment_note %{nil}
# The bundled upstream Electron/node payload includes musl add-ons that are not used on Fedora.
%global __requires_exclude_from ^/opt/OpenCode/resources/app\.asar\.unpacked/node_modules/(@msgpackr-extract/msgpackr-extract-linux-x64/.*\.musl\.node|@parcel/watcher-linux-x64-musl/.*\.node)$

Name: open-code
# renovate: datasource=custom.opencode-desktop depName=opencode-desktop
Version: 2.2.0
Release: 1%{?dist}
Summary: The open source AI coding agent

License: MIT
URL: https://github.com/anomalyco/opencode
Source0: https://opencode.ai/files/bin/%{version}/opencode-desktop-linux-x86_64.rpm
Source1: https://raw.githubusercontent.com/anomalyco/opencode/v%{version}/LICENSE
Source2: https://opencode.ai/files/bin/%{version}/opencode-linux-x64.tar.gz

ExclusiveArch: x86_64

BuildRequires: cpio
BuildRequires: desktop-file-utils
BuildRequires: rpm-build
BuildRequires: tar

%description
OpenCode is an open source AI coding agent desktop application.

This package republishes the upstream x86_64 desktop RPM payload through COPR
and installs the matching upstream x86_64 CLI release artifact.

%prep
%setup -q -c -T
rpm2cpio %{SOURCE0} | cpio -idm --quiet
mkdir cli
tar -xzf %{SOURCE2} -C cli

%build

%install
cp -a opt usr %{buildroot}/
rm -rf %{buildroot}%{_prefix}/lib/.build-id
install -Dpm 0755 cli/opencode %{buildroot}%{_bindir}/opencode
ln -s opencode %{buildroot}%{_bindir}/opencode-cli
install -Dpm 0644 %{SOURCE1} %{buildroot}%{_licensedir}/%{name}/LICENSE

%check
test -x opt/OpenCode/ai.opencode
test -x cli/opencode
desktop-file-validate usr/share/applications/ai.opencode.desktop.desktop
desktop-file-validate usr/share/applications/opencode-desktop.desktop
# Test both public names and the private CLI used by the unmodified desktop.
for command in %{buildroot}%{_bindir}/opencode %{buildroot}%{_bindir}/opencode-cli opt/OpenCode/resources/opencode-cli; do
  test "$("$command" --version)" = "opencode v%{version}"
  help=$("$command" --help 2>&1)
  case "$help" in \
    *"opencode <subcommand>"*"service"*) ;; \
    *)
      printf '%s\n' "$command no longer exposes the expected OpenCode root help" >&2
      exit 1
      ;;
  esac
  help=$("$command" service --help 2>&1)
  case "$help" in \
    *"opencode service <subcommand>"*"start"*"status"*"stop"*) ;; \
    *)
      printf '%s\n' "$command no longer exposes the expected OpenCode service help" >&2
      exit 1
      ;;
  esac
done

%files
%license %{_licensedir}/%{name}/LICENSE
%{_bindir}/opencode
%{_bindir}/opencode-cli
%{_datadir}/applications/ai.opencode.desktop.desktop
%{_datadir}/applications/opencode-desktop.desktop
%{_datadir}/icons/hicolor/*/apps/ai.opencode.png
%{_metainfodir}/ai.opencode.desktop.metainfo.xml
/opt/OpenCode

%changelog
* Sun Oct 25 2026 Nikos <14947634+Iolaum@users.noreply.github.com> - 2.1.4-1
- follow stable v2 desktop and matching CLI artifacts from the upstream files service
- expose opencode with an opencode-cli compatibility symlink
- preserve the v2 desktop payload and verify all packaged CLI entry points

* Mon Mar 16 2026 Nikos <14947634+Iolaum@users.noreply.github.com> - 1.2.27-2
- disable RPM strip/post-processing steps that truncate the bundled OpenCode CLI payload
- add CLI smoke checks so builds fail if the packaged binary falls back to Bun behavior
