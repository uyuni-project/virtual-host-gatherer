#
# spec file for package virtual-host-gatherer
#
# Copyright (c) 2019 SUSE LINUX GmbH, Nuernberg, Germany.
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

%if 0%{?suse_version} > 1320 || 0%{?rhel}
# SLE15 builds on Python 3
%global build_py3   1
%endif
%define pythonX %{?build_py3:python3}%{!?build_py3:python2}
%define python_sitelib %(%{pythonX} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")

Name:           virtual-host-gatherer
Version:        1.0.22
Release:        1
Summary:        Gather virtualization information
License:        Apache-2.0
Group:          Development/Languages/Python
Url:            http://www.suse.com
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  asciidoc
%if 0%{?rhel}
BuildRequires:  libxslt-devel
%else
BuildRequires:  libxslt-tools
%endif
%if 0%{?build_py3}
BuildRequires:  python3-devel
BuildRequires:  python3-pycurl
BuildRequires:  python3-six
Requires:       python3-pycurl
Requires:       python3-six
%else
BuildRequires:  python-devel
BuildRequires:  python-pycurl
BuildRequires:  python-six
Requires:       python-pycurl
Requires:       python-six
%{py_requires}
%endif
%if 0%{?suse_version} && 0%{?suse_version} <= 1110
%{!?python_sitelib: %global python_sitelib %(python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%else
BuildArch:      noarch
%endif

%description
This package contains a script to gather information about virtual system
running on different kind of hypervisors.

%package VMware
Summary:        VMware connection module
Group:          Development/Languages
Requires:       %{name} = %{version}
%if 0%{?build_py3}
Requires:       python3-pyvmomi
%else
Requires:       python-pyvmomi
%endif

%description VMware
VMware connection module for gatherer

%if 0%{with_susecloud}
%package SUSECloud
Summary:        SUSE Cloud connection module
Group:          Development/Languages
Requires:       %{name} = %{version}
%if 0%{?build_py3}
Requires:       python3-novaclient
%else
Requires:       python-novaclient
%endif

%description SUSECloud
SUSE Cloud connection module for gatherer
%endif

%package Kubernetes
Summary:        Kubernetes connection module
Group:          Development/Languages
Requires:       %{name} = %{version}
%if 0%{?build_py3}
Requires:       python3-kubernetes
%else
Requires:       python-kubernetes
%endif

%description Kubernetes
Kubernetes connection module for gatherer

%package libcloud
Summary:        Azure, Amazon AWS EC2 and Google Compute connection module
Group:          Development/Languages
Requires:       %{name} = %{version}
%if 0%{?build_py3}
Requires:       python3-apache-libcloud
%else
Requires:       python-apache-libcloud
%endif

%description libcloud
Azure, Amazon AWS EC2 and Google Compute Engine connection module

%package Nutanix
Summary:        Nutanix AHV connection module
Group:          Development/Languages
Requires:       %{name} = %{version}

%description Nutanix
Nutanix AHV connection module for gatherer

%prep
%setup -q

%build
# Fixing shebang for Python 3
%if 0%{?build_py3}
for i in `find . -type f`;
do
    sed -i '1s=^#!/usr/bin/\(python\|env python\)[0-9.]*=#!/usr/bin/python3=' $i;
done
%endif
%{pythonX} setup.py build

%install
%{pythonX} setup.py install --prefix=%{_prefix} --root=$RPM_BUILD_ROOT

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
%doc LICENSE README.md
%doc %{_mandir}/man1/%{name}.1*
%dir %{python_sitelib}/gatherer
%dir %{python_sitelib}/gatherer/modules
%{python_sitelib}/gatherer/*.py*
%{python_sitelib}/gatherer/modules/__init__.py*
%{_bindir}/%{name}
%{python_sitelib}/virtual_host_gatherer-*.egg-info
%{python_sitelib}/gatherer/modules/File.py*
%if 0%{?build_py3}
%dir %{python_sitelib}/gatherer/__pycache__
%dir %{python_sitelib}/gatherer/modules/__pycache__
%{python_sitelib}/gatherer/__pycache__/*
%{python_sitelib}/gatherer/modules/__pycache__/File.*
%{python_sitelib}/gatherer/modules/__pycache__/__init__.*
%endif

%files VMware
%defattr(-,root,root,-)
%{python_sitelib}/gatherer/modules/VMware.py*
%if 0%{?build_py3}
%{python_sitelib}/gatherer/modules/__pycache__/VMware.*
%endif

%if 0%{with_susecloud}
%files SUSECloud
%defattr(-,root,root,-)
%{python_sitelib}/gatherer/modules/SUSECloud.py*
%if 0%{?build_py3}
%{python_sitelib}/gatherer/modules/__pycache__/SUSECloud.*
%endif
%endif

%files Kubernetes
%defattr(-,root,root,-)
%{python_sitelib}/gatherer/modules/Kubernetes.py*
%if 0%{?build_py3}
%{python_sitelib}/gatherer/modules/__pycache__/Kubernetes.*
%endif

%files libcloud
%defattr(-,root,root,-)
%{python_sitelib}/gatherer/modules/Azure.py*
%{python_sitelib}/gatherer/modules/GoogleCE.py*
%{python_sitelib}/gatherer/modules/AmazonEC2.py*
%if 0%{?build_py3}
%{python_sitelib}/gatherer/modules/__pycache__/Azure.*
%{python_sitelib}/gatherer/modules/__pycache__/GoogleCE.*
%{python_sitelib}/gatherer/modules/__pycache__/AmazonEC2.*
%endif

%files Nutanix
%defattr(-,root,root,-)
%{python_sitelib}/gatherer/modules/NutanixAHV.py*
%if 0%{?build_py3}
%{python_sitelib}/gatherer/modules/__pycache__/NutanixAHV.*
%endif

%changelog
