Name:	  tsm-exporter
Version:  0.0.4
%global gittag 0.0.4
Release:  1%{?dist}
Summary:  Prometheus exporter for IBM Spectrum Protect

License:  Apache License 2.0
URL:      https://github.com/guilbaults/tsm-exporter
Source0:  https://github.com/guilbaults/%{name}/archive/v%{gittag}/%{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:	systemd
Requires:       python36
Requires:       python3-prometheus_client

%description
Prometheus exporter for IBM Spectrum Protect

%prep
%autosetup -n %{name}-%{gittag}
%setup -q

%build

%install
mkdir -p %{buildroot}/%{_bindir}
mkdir -p %{buildroot}/%{_unitdir}

sed -i -e '1i#!/usr/bin/python3.6' tsm-exporter.py
install -m 0755 %{name}.py %{buildroot}/%{_bindir}/%{name}
install -m 0644 tsm-exporter.service %{buildroot}/%{_unitdir}/tsm-exporter.service

%clean
rm -rf $RPM_BUILD_ROOT

%files
%{_bindir}/%{name}
%{_unitdir}/tsm-exporter.service

%changelog
* Tue Nov 4 2021 Simon Guilbault <simon.guilbault@calculquebec.ca> 0.0.4-1
- Releasing for EL8
- Using python3.6
- Adding a "insecure" option to quiet down some logs from ssl cert
* Tue Sep 1 2020 Simon Guilbault <simon.guilbault@calculquebec.ca> 0.0.3-1
- Adding storage pools stats
* Tue Sep 1 2020 Simon Guilbault <simon.guilbault@calculquebec.ca> 0.0.2-1
- Using config file from ENV vars
* Tue Sep 1 2020 Simon Guilbault <simon.guilbault@calculquebec.ca> 0.0.1-1
- Initial release
