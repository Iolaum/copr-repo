%global pypi_name huggingface_hub

Name:           python-huggingface-hub
# renovate: datasource=pypi depName=huggingface_hub
Version:        1.32.0
Release:        1%{?dist}
Summary:        Client library to handle repos on the Hugging Face Hub

License:        Apache-2.0
URL:            https://github.com/huggingface/huggingface_hub
Source0:        %{pypi_source %{pypi_name}}

BuildArch:      noarch

BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-devel
BuildRequires:  python3dist(packaging)
BuildRequires:  python3dist(pip) >= 19
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(wheel)

%global _description %{expand:
The huggingface_hub library allows Python applications to download, publish,
and manage models, datasets, and other repositories hosted on the Hugging Face
Hub.

It also installs the upstream hf CLI and the tiny-agents helper command.
}

%description %_description


%package -n python3-huggingface-hub
Summary:        %{summary}
Requires:       python3dist(mcp) >= 1.8.0

%description -n python3-huggingface-hub %_description


%prep
%autosetup -n %{pypi_name}-%{version}


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files huggingface_hub


%check
PYTHONPATH=%{buildroot}%{python3_sitelib} python3 -c 'import huggingface_hub'
test -x %{buildroot}%{_bindir}/hf
test -x %{buildroot}%{_bindir}/tiny-agents


%files -n python3-huggingface-hub -f %{pyproject_files}
%license LICENSE
%doc README.md
%{_bindir}/hf
%{_bindir}/huggingface-cli
%{_bindir}/tiny-agents


%changelog
%autochangelog
