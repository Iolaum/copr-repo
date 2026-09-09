%global debug_package %{nil}
%global __brp_strip %{nil}
%global __brp_strip_lto %{nil}
%global __brp_strip_comment_note %{nil}
# The bundled upstream Electron/node payload includes musl add-ons that are not used on Fedora.
%global __requires_exclude_from ^/opt/OpenCode/resources/app\.asar\.unpacked/node_modules/(@msgpackr-extract/msgpackr-extract-linux-x64/.*\.musl\.node|@parcel/watcher-linux-x64-musl/.*\.node)$

Name: open-code
# renovate: datasource=github-releases depName=anomalyco/opencode
Version: 1.18.30
Release: 1%{?dist}
Summary: The open source AI coding agent

License: MIT
URL: https://github.com/anomalyco/opencode
Source0: %{url}/releases/download/v%{version}/opencode-desktop-linux-x86_64.rpm
Source1: https://raw.githubusercontent.com/anomalyco/opencode/v%{version}/LICENSE
Source2: %{url}/releases/download/v%{version}/opencode-linux-x64.tar.gz

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
install -Dpm 0755 cli/opencode %{buildroot}%{_bindir}/opencode-cli
install -Dpm 0644 %{SOURCE1} %{buildroot}%{_licensedir}/%{name}/LICENSE

%check
test -x opt/OpenCode/ai.opencode.desktop
test -x cli/opencode
desktop-file-validate usr/share/applications/ai.opencode.desktop.desktop
desktop-file-validate usr/share/applications/opencode-desktop.desktop
test "$(%{buildroot}%{_bindir}/opencode-cli --version)" = "%{version}"
case "$(%{buildroot}%{_bindir}/opencode-cli --help 2>&1)" in \
  *"opencode attach <url>"*) ;; \
  *)
    printf '%s\n' 'packaged opencode-cli no longer exposes the expected OpenCode CLI help output' >&2
    exit 1
    ;;
esac

%files
%license %{_licensedir}/%{name}/LICENSE
%{_bindir}/opencode-cli
%{_datadir}/applications/ai.opencode.desktop.desktop
%{_datadir}/applications/opencode-desktop.desktop
%{_datadir}/icons/hicolor/*/apps/ai.opencode.desktop.png
%{_metainfodir}/ai.opencode.desktop.metainfo.xml
/opt/OpenCode

%changelog
* Mon Mar 16 2026 Nikos <14947634+Iolaum@users.noreply.github.com> - 1.2.27-2
- disable RPM strip/post-processing steps that truncate the bundled OpenCode CLI payload
- add CLI smoke checks so builds fail if the packaged binary falls back to Bun behavior
