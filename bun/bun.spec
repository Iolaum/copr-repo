%global debug_package %{nil}

Name: bun
# renovate: datasource=github-releases depName=oven-sh/bun
Version: 1.4.3
Release: 1%{?dist}
Summary: Fast all-in-one JavaScript runtime and toolkit

License: MIT
URL: https://github.com/oven-sh/bun
Source0: %{url}/releases/download/bun-v%{version}/bun-linux-x64.zip
Source1: %{url}/raw/bun-v%{version}/LICENSE.md

ExclusiveArch: x86_64

BuildRequires: unzip

%description
Bun is an all-in-one JavaScript runtime and toolkit designed for speed.
It includes a runtime, package manager, bundler, and test runner.

This package installs the upstream optimized x86_64 Linux release.

%prep
%setup -q -c -T
unzip -q %{SOURCE0}

%build

%install
install -Dpm 0755 bun-linux-x64/bun %{buildroot}%{_bindir}/bun
install -Dpm 0644 %{SOURCE1} %{buildroot}%{_licensedir}/%{name}/LICENSE.md

%check

%files
%license %{_licensedir}/%{name}/LICENSE.md
%{_bindir}/bun

%changelog
%autochangelog
