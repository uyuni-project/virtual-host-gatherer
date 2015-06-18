#
# spec file for package python-gatherer (Version 1.0.0)
#
# Copyright (c) 2015 SUSE LLC, Nuernberg, Germany.
# This file and all modifications and additions to the pristine
# package are under the same license as the package itself.
#
# Please submit bugfixes or comments via http://bugs.opensuse.org/
#


Name:           python-gatherer
Version:        1.0.3
Release:        1
Summary:        gather virtualization information
Group:          Development/Languages
License:        Apache-2.0
Url:            http://www.suse.com
Source0:        gatherer-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  python-devel
%{py_requires}
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

%package SUSECloud
Summary:        SUSE Cloud connection module
Group:          Development/Languages
Requires:       %{name} = %{version}
Requires:       python-novaclient

%description SUSECloud
SUSE Cloud connection module for gatherer


%prep
%setup -q

%build
python setup.py build

%install
python setup.py install --prefix=%{_prefix} --root=$RPM_BUILD_ROOT

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

%files VMware
%defattr(-,root,root,-)
%{python_sitelib}/gatherer/modules/VMware.py*

%files SUSECloud
%defattr(-,root,root,-)
%{python_sitelib}/gatherer/modules/SUSECloud.py*

%changelog
