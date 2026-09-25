%global debug_package %{nil}
%global wheel_name hf_xet-%{version}-cp37-abi3-manylinux2014_x86_64.manylinux_2_17_x86_64.whl

Name: python-hf-xet
# renovate: datasource=github-releases depName=huggingface/xet-core
Version: v1.6.0
Release: 2%{?dist}
Summary: Python bindings for Hugging Face Xet storage

License: Apache-2.0
URL: https://github.com/huggingface/xet-core
Source0: %{url}/releases/download/%{version}/%{wheel_name}

ExclusiveArch: x86_64

BuildRequires: python3
BuildRequires: python3-rpm-macros

%description
hf-xet provides the native Python bindings used by huggingface_hub to
upload and download files through Hugging Face Xet storage.

This package republishes the upstream x86_64 abi3 wheel through COPR.

%package -n python3-hf-xet
Summary: %{summary}
Requires: python3 >= 3.8
Provides: python%{python3_version}dist(hf-xet) = %{version}
Provides: python3dist(hf-xet) = %{version}

%description -n python3-hf-xet
hf-xet provides the native Python bindings used by huggingface_hub to
upload and download files through Hugging Face Xet storage.

%prep
%setup -q -c -T
python3 -m zipfile -e %{SOURCE0} .

%build

%install
install -d %{buildroot}%{python3_sitearch}
cp -a hf_xet %{buildroot}%{python3_sitearch}/
cp -a hf_xet-%{version}.dist-info %{buildroot}%{python3_sitearch}/

%check
PYTHONPATH=%{buildroot}%{python3_sitearch} python3 -c 'import hf_xet'

%files -n python3-hf-xet
%dir %{python3_sitearch}/hf_xet
%pycached %{python3_sitearch}/hf_xet/__init__.py
%{python3_sitearch}/hf_xet/hf_xet.abi3.so
%dir %{python3_sitearch}/hf_xet-%{version}.dist-info
%{python3_sitearch}/hf_xet-%{version}.dist-info/METADATA
%{python3_sitearch}/hf_xet-%{version}.dist-info/RECORD
%{python3_sitearch}/hf_xet-%{version}.dist-info/WHEEL
%dir %{python3_sitearch}/hf_xet-%{version}.dist-info/licenses
%license %{python3_sitearch}/hf_xet-%{version}.dist-info/licenses/LICENSE
%dir %{python3_sitearch}/hf_xet-%{version}.dist-info/sboms
%{python3_sitearch}/hf_xet-%{version}.dist-info/sboms/hf_xet.cyclonedx.json

%changelog
%autochangelog
