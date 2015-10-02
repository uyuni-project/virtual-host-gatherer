#
# spec file for package python-gatherer
#
# Copyright (c) 2015 SUSE LINUX GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

%global with_susecloud 0

Name:           python-gatherer
Version:        1.0.5
Release:        1
Summary:        gather virtualization information
License:        Apache-2.0
Group:          Development/Languages
Url:            http://www.suse.com
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  python-devel
%{py_requires}
Requires:       python-urlgrabber
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
Requires:       python-pyvmomi

%description VMware
VMware connection module for gatherer

%if 0%{with_susecloud}
%package SUSECloud
Summary:        SUSE Cloud connection module
Group:          Development/Languages
Requires:       %{name} = %{version}
Requires:       python-novaclient

%description SUSECloud
SUSE Cloud connection module for gatherer
%endif

%prep
%setup -q

%build
python setup.py build

%install
python setup.py install --prefix=%{_prefix} --root=$RPM_BUILD_ROOT

%if ! 0%{with_susecloud}
rm -f $RPM_BUILD_ROOT%{python_sitelib}/gatherer/modules/SUSECloud.py*
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc LICENSE README.md
%dir %{python_sitelib}/gatherer
%dir %{python_sitelib}/gatherer/modules
%{python_sitelib}/gatherer/*.py*
%{python_sitelib}/gatherer/modules/__init__.py*
%{_bindir}/gatherer
%{python_sitelib}/gatherer-*.egg-info
%{python_sitelib}/gatherer/modules/File.py*

%files VMware
%defattr(-,root,root,-)
%{python_sitelib}/gatherer/modules/VMware.py*

%if 0%{with_susecloud}
%files SUSECloud
%defattr(-,root,root,-)
%{python_sitelib}/gatherer/modules/SUSECloud.py*
%endif

%changelog
