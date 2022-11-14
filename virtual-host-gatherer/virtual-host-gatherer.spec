#
# spec file for package virtual-host-gatherer
#
# Copyright (c) 2022 SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#


%global with_susecloud 0
%define skip_python2 1
%global __python /usr/bin/python3

%{?!python_module:%define python_module() python3-%{**}}
%{?!python_build:%define python_build %{expand:%py3_build}}
%{?!python_install:%define python_install %{expand:%py3_install}}

Name:           virtual-host-gatherer
Version:        1.0.23
Release:        0
Summary:        Gather virtualization information
License:        Apache-2.0
Group:          Development/Languages/Python
URL:            https://github.com/uyuni-project/virtual-host-gatherer
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  asciidoc
BuildRequires:  python-rpm-macros
%if 0%{?rhel}
BuildRequires:  libxslt-devel
%else
BuildRequires:  libxslt-tools
%endif
BuildRequires:  %{python_module devel}
BuildRequires:  %{python_module pycurl}
BuildRequires:  %{python_module six}
Requires:       %{python_module pycurl}
Requires:       %{python_module six}
BuildArch:      noarch

%description
This package contains a script to gather information about virtual system
running on different kind of hypervisors.

%package VMware
Summary:        VMware connection module
Group:          Development/Languages
Requires:       %{name} = %{version}
Requires:       %{python_module pyvmomi}

%description VMware
VMware connection module for gatherer

%if 0%{with_susecloud}
%package SUSECloud
Summary:        SUSE Cloud connection module
Group:          Development/Languages
Requires:       %{name} = %{version}
Requires:       %{python_module novaclient}

%description SUSECloud
SUSE Cloud connection module for gatherer
%endif

%package Kubernetes
Summary:        Kubernetes connection module
Group:          Development/Languages
Requires:       %{name} = %{version}
Requires:       %{python_module kubernetes}

%description Kubernetes
Kubernetes connection module for gatherer

%package libcloud
Summary:        Azure, Amazon AWS EC2 and Google Compute connection module
Group:          Development/Languages
Requires:       %{name} = %{version}
Requires:       %{python_module apache-libcloud}

%description libcloud
Azure, Amazon AWS EC2 and Google Compute Engine connection module

%package Nutanix
Summary:        Nutanix AHV connection module
Group:          Development/Languages
Requires:       %{name} = %{version}

%description Nutanix
Nutanix AHV connection module for gatherer

%package Libvirt
Summary:        Libvirt connection module
Group:          Development/Languages
Requires:       %{name} = %{version}
Requires:       %{python_module libvirt-python}

%description Libvirt
Libvirt connection module for gatherer

%prep
%setup -q

%build
%python_build

%install
%python_install
%if ! 0%{with_susecloud}
rm -f $RPM_BUILD_ROOT%{python_sitelib}/gatherer/modules/SUSECloud.py*
rm -f $RPM_BUILD_ROOT%{python_sitelib}/gatherer/modules/__pycache__/SUSECloud.*
%endif

a2x -v -d manpage -f manpage doc/%{name}.1.asciidoc
mkdir -p %{buildroot}%{_mandir}/man1
install -m 0644 doc/%{name}.1 $RPM_BUILD_ROOT%{_mandir}/man1/

%check
export PYTHONPATH=%{buildroot}%{python_sitelib}
%{buildroot}%{_bindir}/%{name} -h
%{buildroot}%{_bindir}/%{name} -l

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%license LICENSE
%doc README.md
%doc %{_mandir}/man1/%{name}.1*
%dir %{python_sitelib}/gatherer
%dir %{python_sitelib}/gatherer/modules
%{_bindir}/%{name}
%{python_sitelib}/gatherer/*.py*
%{python_sitelib}/gatherer/modules/__init__.py*
%{python_sitelib}/virtual_host_gatherer-*.egg-info
%{python_sitelib}/gatherer/modules/File.py*
%dir %{python_sitelib}/gatherer/__pycache__
%dir %{python_sitelib}/gatherer/modules/__pycache__
%{python_sitelib}/gatherer/__pycache__/*
%{python_sitelib}/gatherer/modules/__pycache__/File.*
%{python_sitelib}/gatherer/modules/__pycache__/__init__.*

%files VMware
%defattr(-,root,root,-)
%{python_sitelib}/gatherer/modules/VMware.py*
%{python_sitelib}/gatherer/modules/__pycache__/VMware.*

%if 0%{with_susecloud}
%files SUSECloud
%defattr(-,root,root,-)
%{python_sitelib}/gatherer/modules/SUSECloud.py*
%{python_sitelib}/gatherer/modules/__pycache__/SUSECloud.*
%endif

%files Kubernetes
%defattr(-,root,root,-)
%{python_sitelib}/gatherer/modules/Kubernetes.py*
%{python_sitelib}/gatherer/modules/__pycache__/Kubernetes.*

%files libcloud
%defattr(-,root,root,-)
%{python_sitelib}/gatherer/modules/Azure.py*
%{python_sitelib}/gatherer/modules/GoogleCE.py*
%{python_sitelib}/gatherer/modules/AmazonEC2.py*
%{python_sitelib}/gatherer/modules/__pycache__/Azure.*
%{python_sitelib}/gatherer/modules/__pycache__/GoogleCE.*
%{python_sitelib}/gatherer/modules/__pycache__/AmazonEC2.*

%files Nutanix
%defattr(-,root,root,-)
%{python_sitelib}/gatherer/modules/NutanixAHV.py*
%{python_sitelib}/gatherer/modules/__pycache__/NutanixAHV.*

%files Libvirt
%defattr(-,root,root,-)
%{python_sitelib}/gatherer/modules/Libvirt.py*
%{python_sitelib}/gatherer/modules/__pycache__/Libvirt.*

%changelog
