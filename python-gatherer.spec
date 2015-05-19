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
Version:        1.0.1
Release:        1
Summary:        gather virtualization information
Group:          Development/Languages
License:        Apache-2.0
Url:            http://www.suse.com
Source0:        gatherer-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  python-devel
%{py_requires}

%description
This package contains a script to gather information about virtual system
running on different kind of hypervisors.

%prep
%setup -q -n gatherer-%{version}

%build
python setup.py build

%install
python setup.py install --prefix=%{_prefix} --root=$RPM_BUILD_ROOT --record-rpm=INSTALLED_FILES

%clean
rm -rf %{buildroot}

%files -f INSTALLED_FILES
%defattr(-,root,root,-)
%doc LICENSE README.md

%changelog